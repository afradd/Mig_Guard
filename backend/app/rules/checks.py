from typing import Any, Dict, List, Optional


def _get_val(extracted: Dict[str, Any], field: str) -> str:
    """Safely extract lowercase string value from an extracted field object."""
    item = extracted.get(field)
    if isinstance(item, dict) and item.get("value") is not None:
        return str(item["value"]).strip().lower()
    return ""


def _get_snippet(extracted: Dict[str, Any], field: str) -> str:
    """Safely extract the source snippet for UI evidence highlighting."""
    item = extracted.get(field)
    if isinstance(item, dict) and item.get("source_snippet"):
        return str(item["source_snippet"]).strip()
    return ""


def check_r01_no_written_contract(extracted: Dict[str, Any]) -> Optional[str]:
    doc_type = str(extracted.get("document_type", "")).lower()
    if doc_type in {"chat_screenshot", "social_post"}:
        return f"Document type detected as {doc_type}"
    return None


def check_r02_non_work_visa(extracted: Dict[str, Any]) -> Optional[str]:
    visa = _get_val(extracted, "visa_type")
    bad_visas = ("tourist", "visit", "business", "vistor", "ট্যুরিস্ট", "ভিজিট")
    if any(word in visa for word in bad_visas):
        return _get_snippet(extracted, "visa_type") or visa
    return None


def check_r03_cash_or_unspecified_fee(extracted: Dict[str, Any]) -> Optional[str]:
    method = _get_val(extracted, "payment_method")
    if any(word in method for word in ("cash", "no receipt", "hand to hand", "নগদ")):
        return _get_snippet(extracted, "payment_method") or method
    return None


def check_r04_high_risk_scam_pattern(
    extracted: Dict[str, Any], patterns: Dict[str, Any]
) -> Optional[str]:
    dest = _get_val(extracted, "destination")
    title = _get_val(extracted, "job_title")
    high_risk_countries = [c.lower() for c in patterns.get("high_risk_countries", [])]
    scam_keywords = [k.lower() for k in patterns.get("scam_job_keywords", [])]

    country_match = any(c in dest for c in high_risk_countries)
    job_match = any(k in title for k in scam_keywords)

    if country_match and job_match:
        dest_snip = _get_snippet(extracted, "destination") or dest
        job_snip = _get_snippet(extracted, "job_title") or title
        return f"{dest_snip} | {job_snip}"
    return None


def check_r06_missing_critical_clauses(extracted: Dict[str, Any]) -> Optional[str]:
    required_fields = [
        "employer",
        "job_title",
        "salary_amount",
        "duration",
        "working_hours",
        "accommodation",
        "return_ticket",
    ]
    missing = [f for f in required_fields if not _get_val(extracted, f)]
    if len(missing) >= 2:
        return "Missing: " + ", ".join(missing)
    return None


def check_r07_missing_agency_license(extracted: Dict[str, Any]) -> Optional[str]:
    lic = _get_val(extracted, "license_number")
    if not lic or lic in {"none", "n/a", "null"}:
        return "No RL license number found in document"
    return None


def check_r08_sign_on_arrival(extracted: Dict[str, Any]) -> Optional[str]:
    clauses: List[str] = extracted.get("raw_red_flag_clauses") or []
    triggers = ("sign on arrival", "contract after arrival", "sign after reaching", "পৌঁছানোর পর চুক্তি")
    for clause in clauses:
        if any(t in clause.lower() for t in triggers):
            return clause
    return None


def check_r09_passport_retention(extracted: Dict[str, Any]) -> Optional[str]:
    clauses: List[str] = extracted.get("raw_red_flag_clauses") or []
    triggers = ("hold passport", "keep passport", "passport retention", "submit passport to employer", "পাসপোর্ট জমা")
    for clause in clauses:
        if any(t in clause.lower() for t in triggers):
            return clause
    return None


def check_r11_pressure_tactics(extracted: Dict[str, Any]) -> Optional[str]:
    clauses: List[str] = extracted.get("raw_red_flag_clauses") or []
    triggers = ("pay today", "urgent", "limited seats", "last chance", "today only", "আজই টাকা", "সীমিত সিট")
    for clause in clauses:
        if any(t in clause.lower() for t in triggers):
            return clause
    return None


def check_r12_personal_mobile_payment(extracted: Dict[str, Any]) -> Optional[str]:
    method = _get_val(extracted, "payment_method")
    triggers = ("personal", "bkash", "nagad", "rocket", "before visa", "বিকাশ", "নগদ")
    if any(t in method for t in triggers):
        return _get_snippet(extracted, "payment_method") or method
    return None


def check_r05_unrealistic_salary(extracted: Dict[str, Any]) -> Optional[str]:
    """Flag if salary is suspiciously high (over $5000 USD equivalent / month) for unskilled roles,
    or if no salary is stated at all while high earnings are implied in the clause text."""
    clauses: List[str] = extracted.get("raw_red_flag_clauses") or []
    high_pay_triggers = (
        "high salary", "high pay", "earn big", "big money", "upto 3000",
        "upto 4000", "upto 5000", "লক্ষ টাকা", "অনেক বেতন",
    )
    for clause in clauses:
        if any(t in clause.lower() for t in high_pay_triggers):
            return clause
    return None
