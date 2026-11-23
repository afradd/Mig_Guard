from app.rules import checks
from app.rules.engine import evaluate_rules, load_patterns


def _field(val, snippet=None):
    return {"value": val, "confidence": 0.95, "source_snippet": snippet or str(val)}


def test_r01_chat_screenshot_flagged():
    data = {"document_type": "chat_screenshot"}
    assert checks.check_r01_no_written_contract(data) is not None


def test_r02_tourist_visa_flagged():
    data = {"visa_type": _field("Tourist Visa", "Visa Type: Tourist Visa (30 days)")}
    res = checks.check_r02_non_work_visa(data)
    assert res == "Visa Type: Tourist Visa (30 days)"


def test_r03_cash_payment_flagged():
    data = {"payment_method": _field("Cash only, no receipt")}
    assert checks.check_r03_cash_or_unspecified_fee(data) is not None


def test_r04_cambodia_crypto_scam_flagged():
    patterns = load_patterns()
    data = {
        "destination": _field("Phnom Penh, Cambodia"),
        "job_title": _field("Crypto Customer Service Agent"),
    }
    res = checks.check_r04_high_risk_scam_pattern(data, patterns)
    assert res is not None and "Cambodia" in res


def test_r06_missing_clauses_flagged():
    data = {"employer": _field("ABC Corp")}  # missing job_title, salary, duration, etc.
    res = checks.check_r06_missing_critical_clauses(data)
    assert res is not None and "Missing:" in res


def test_r07_missing_license_flagged():
    data = {"license_number": _field(None)}
    assert checks.check_r07_missing_agency_license(data) is not None


def test_r08_sign_on_arrival_flagged():
    data = {"raw_red_flag_clauses": ["Worker will sign on arrival at airport."]}
    assert checks.check_r08_sign_on_arrival(data) is not None


def test_r09_passport_retention_flagged():
    data = {"raw_red_flag_clauses": ["Company will hold passport for 2 years."]}
    assert checks.check_r09_passport_retention(data) is not None


def test_r11_pressure_tactics_flagged():
    data = {"raw_red_flag_clauses": ["Pay today, limited seats available!"]}
    assert checks.check_r11_pressure_tactics(data) is not None


def test_r05_unrealistic_salary_flagged():
    data = {"raw_red_flag_clauses": ["Earn big money! High salary up to 3000 USD per month, no experience needed!"]}
    assert checks.check_r05_unrealistic_salary(data) is not None


def test_r05_no_flag_on_normal_salary():
    data = {"raw_red_flag_clauses": ["Monthly salary: 800 USD"]}
    assert checks.check_r05_unrealistic_salary(data) is None


def test_r12_personal_bkash_flagged():
    data = {"payment_method": _field("Send to personal bKash 017XXXXXXXX")}
    assert checks.check_r12_personal_mobile_payment(data) is not None


def test_engine_end_to_end_scam_offer():
    scam_offer = {
        "document_type": "chat_screenshot",
        "destination": _field("Cambodia"),
        "job_title": _field("Online Data Entry"),
        "visa_type": _field("Visit Visa"),
        "payment_method": _field("Personal bKash before visa"),
        "raw_red_flag_clauses": ["Pay today, limited seats!"],
    }
    result = evaluate_rules(scam_offer)
    triggered_ids = {f["rule_id"] for f in result["flags"]}
    assert "R01_NO_WRITTEN_CONTRACT" in triggered_ids
    assert "R02_NON_WORK_VISA" in triggered_ids
    assert "R04_HIGH_RISK_SCAM_PATTERN" in triggered_ids
    assert "R11_PRESSURE_TACTICS" in triggered_ids
    assert "R12_PERSONAL_MOBILE_PAYMENT" in triggered_ids