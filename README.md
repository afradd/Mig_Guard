# Mig_Guard (Job Offer Checker for Migrant Workers)

> **AI-Powered Pre-Departure Fraud & Scam Checker for Prospective Migrant Workers**  
> *CoU AI Hackathon 2026 | Comilla University | Theme: AI for Humanity*  
> **Declared Domains:** Cybersecurity (Primary: Fraud & Scam Detection) | Accessibility (Secondary: Bangla Audio for Low Literacy)

[![CI](https://github.com/afradd/Mig_Guard/actions/workflows/backend-ci.yml/badge.svg)](https://github.com/afradd/Mig_Guard/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14+-black.svg)](https://nextjs.org/)

---

## 1. Team & Project Information

- **Project Name:** Mig_Guard (Job Offer Checker)
- **Team Name:** CoU Technova Finalist Team
- **Team Members & Roles:**
  - **Member A (Team Leader):** Afrad — AI & Backend Lead (Pipeline orchestrator, vision extraction, scoring, host deployment)
  - **Member B:** Member B — Frontend & UX Lead (Next.js web app, mobile camera capture, Bangla audio player, result screens)
  - **Member C:** Athikul Islam — Data, Rules & Evaluation Lead (15-rule catalog, deterministic checks engine, official data verification, 20-doc evaluation suite, documentation)

---

## 2. Problem Statement & Evidence

Migrant workers from Bangladesh often find overseas opportunities through informal sub-agents with no formal written contract and ambiguous, cash-only fee structures. Unscrupulous brokers lure vulnerable jobseekers into forced labor or Southeast Asian cyber-scam compounds (Cambodia, Myanmar, Laos) under false promises of high-paying online customer service or data-entry jobs.

### Empirical Evidence
- **75% of exploited migrant workers** receive no written employment contract before departure, and **~80% are recruited via unauthorized informal sub-agents** (*TBS News, study on migration justice*).
- Over **583 trafficked Bangladeshi citizens** have been repatriated from cyber-slavery compounds in Cambodia alone, part of an estimated **300,000 victims trapped in scam factories worldwide** (*UNODC / Global Voices, 2026*).
- **The Critical Gap:** Nearly all current interventions happen *post-harm* (rescue, complaint filing, repatriation). Mig_Guard acts *pre-departure*, empowering workers standing before a recruiter with an offer before money changes hands.

---

## 3. The Solution & Key Features

Mig_Guard is a mobile-first, privacy-preserving web app where a worker photographs an offer letter, visa, or chat screenshot (WhatsApp, Facebook, Telegram) and receives an explainable, audio-read risk verdict in everyday Bangla.

- 📷 **Multimodal Document Capture:** Upload photos, camera snapshots, or paste text in Bangla and English.
- 🔍 **Structured Contract Extraction:** Extracts destination, employer, job title, wage, fees, visa category, duration, and agency license with verbatim document snippets.
- 🚩 **15-Rule Deterministic Engine:** Rigorous rule-based verification against official government circulars, BMET licensing lists, statutory fee ceilings, and salary benchmarks.
- 💡 **Evidence Grounding:** Every triggered red flag links directly to verbatim text in the user's document.
- ❓ **Questions to Ask:** Generates actionable, plain-language questions in Bangla and English for the worker to ask the broker before paying.
- 🔊 **Bangla Voice Readout:** High-clarity Bangla text-to-speech ensures critical warnings reach low-literacy workers.
- ☎️ **Official Support Resources:** Instant access to verified government helplines (BMET Probashbandhu 16135, Police 999, National Info 333).
- 🛡️ **Zero Document Storage & PII Masking:** All documents are processed strictly in memory and discarded immediately. Passports and phone numbers are masked.
- ⚖️ **Never-Says-Safe Principle:** The safest verdict is *"Fewer concerns found — still verify with BMET."* Missing terms are cataloged as `unverifiable`, never false reassurance.

---

## 4. System Architecture & How the AI Works

Mig_Guard is **not a thin LLM wrapper**. The language model is used strictly for transcription, schema extraction, and plain-language explanation. The final risk score and verdict are computed by a **deterministic Python rules engine** evaluated against verified statutory databases.

```
Phone Camera / Document Upload / Chat Screenshot
                     |
                     v
1. INGEST & PRE-PROCESS      Mask sensitive PII (passports, phone numbers); resize image
                     |
                     v
2. VISION & OCR              Multimodal LLM vision transcription with Bengali/English OCR fallback
                     |
                     v
3. SCHEMA EXTRACTION         Strict JSON schema (`offer_extraction.json`) with confidence & snippets
                     |
                     v
4. VERIFICATION CHECKS       Deterministic evaluation against official data:
                             - BMET RAIMS recruiting agency license verification
                             - Emigration Act 2013 statutory fee caps
                             - Destination-specific salary benchmarks & wage floors
                             - High-risk destination & scam compound pattern matching
                     |
                     v
5. GROUNDED EXPLANATION      RAG retrieval over 33 curated legal & rights passages
                     |
                     v
6. DETERMINISTIC SCORING     Weighted rule aggregation: Danger, Caution, or Fewer Concerns Found
                     |
                     v
7. MULTIMODAL DELIVERY       Bangla audio synthesis (TTS), highlighted evidence snippets,
                             missing clauses checklist, recruiter questions, and official helplines
```

---

## 5. Red-Flag Rules Catalog (`R01`–`R15`)

| Rule ID | Severity | Weight | Description |
|---|:---:|:---:|---|
| `R01_NO_WRITTEN_CONTRACT` | High | 25 | Offer is only a chat message or social post, not a formal written contract. |
| `R02_NON_WORK_VISA` | High | 30 | Tourist, visit, or business visa offered for overseas employment. |
| `R03_CASH_OR_UNSPECIFIED_FEE` | High | 20 | Cash-only payment demanded, hand-to-hand transaction, or no bank receipt. |
| `R04_HIGH_RISK_SCAM_PATTERN` | High | 35 | Online, crypto, or data-entry jobs in scam-compound border areas (Cambodia, Myanmar, Laos). |
| `R05_UNREALISTIC_SALARY` | High | 20 | Salary far exceeds statutory market rates (scam bait) or falls below legal minimums. |
| `R06_MISSING_CRITICAL_CLAUSES` | Medium | 15 | Missing critical terms: employer name, working hours, salary, accommodation, return ticket. |
| `R07_MISSING_AGENCY_LICENSE` | High | 20 | Recruiting agent has no valid BMET Recruiting License (RL) number. |
| `R08_SIGN_ON_ARRIVAL` | High | 25 | Contract to be signed only after arrival abroad (contract substitution risk). |
| `R09_PASSPORT_RETENTION` | High | 25 | Employer or broker holds the worker's original passport (forced labor indicator). |
| `R10_SALARY_DEDUCTION_DEBT_BOND` | High | 25 | Recruitment or visa expenses deducted from monthly wages (debt bondage risk). |
| `R11_PRESSURE_TACTICS` | Medium | 15 | Urgency tactics used ("pay today", "limited seats") to prevent verification. |
| `R12_PERSONAL_MOBILE_PAYMENT` | High | 25 | Payment demanded to personal bKash/Nagad account or prior to visa issuance. |
| `R13_SOCIAL_MEDIA_ONLY_NO_OFFICE` | Medium | 15 | Broker operates exclusively via WhatsApp, Telegram, or Facebook without an office address. |
| `R14_TOO_GOOD_TO_BE_TRUE_BUNDLE` | High | 25 | Free visa + free airfare + abnormally high pay with no qualifications required. |
| `R15_UNVERIFIABLE_EMPLOYER` | Medium | 15 | Employer name or physical foreign workplace address is missing or generic. |

*Full rule details, rationale, and questions in [docs/rules-catalog.md](docs/rules-catalog.md).*

---

## 6. Official Data Sources & Knowledge Base

Every official threshold, fee ceiling, and contact channel is sourced and dated in [backend/app/data/SOURCES.md](backend/app/data/SOURCES.md):
- **Recruiting Agencies:** BMET RAIMS portal (Over 2,000 public license records checked).
- **Recruitment Fee Caps:** Overseas Employment and Migrants Act 2013, Section 21 & BMET circular ceilings.
- **Salary Benchmarks:** Qatar Law No. 17 of 2020, Malaysia National Minimum Wage 2025, Saudi Musaned Domestic Platform, Singapore MOM employment regulations.
- **Helplines:** Probashbandhu Call Center (16135, from abroad +88 09610 102 030), Bangladesh Police (999), Government Services (333).
- **Curated Knowledge Base:** 33 curated passages in `backend/app/rag/kb/` referencing ILO Fair Recruitment and international labor standards.

---

## 7. Evaluation & Validation Results

We evaluated Mig_Guard's deterministic rules engine against a labeled synthetic benchmark of 20 realistic contracts and chat scenarios (8 legitimate, 12 scam-pattern) across English and Bengali.

```
Total Documents Evaluated: 20 (8 Legit, 12 Scam)
Scam Red-Flag Recall:      117/117 (100.0%)
False Alarms on Legit:     0 (0.0%)
```

- **Zero False Reassurance:** All 12 scam offers were successfully caught with high recall across their respective danger indicators.
- **Zero False Alarms:** All 8 legitimate contracts were assessed cleanly with no erroneous scam flags.
- **Automated Data Validation:** `python scripts/validate_data.py` validates all JSON schemas and catalog consistency with 0 warnings.
- *Detailed metrics and error analysis in [docs/evaluation-report.md](docs/evaluation-report.md).*

---

## 8. Technology Stack

- **Frontend:** Next.js 14, React 18, Tailwind CSS, TypeScript, Mobile Camera Capture API, Web Audio Player.
- **Backend:** Python 3.11+, FastAPI, Uvicorn, Pydantic v2.
- **AI & Multimodal Models:** Gemini 1.5 Pro / Flash & Claude 3.5 Sonnet (multimodal extraction & transcription), Tesseract OCR fallback.
- **TTS Synthesis:** Cloud Bangla TTS with browser SpeechSynthesis fallback.
- **Testing & Tooling:** Pytest, PyYAML, Python-Multipart.
- **Deployment:** Render / Docker (Backend), Vercel (Frontend).

---

## 9. AI Tools & Models Disclosure

As required by Hackathon Rule 9 and Rule 16:
- **Coding Assistants:** Claude 3.5 Sonnet, Claude 3.7 Sonnet, GitHub Copilot (used for route scaffolding, schema design, unit tests, and documentation).
- **Multimodal Models:** Gemini 1.5 Pro / Flash (vision document extraction).
- **Human Governance:** All business logic, legal thresholds, salary ranges, and test assertions were authored, reviewed, and audited by registered team members.
- *Detailed running log available in [AI_USAGE.md](AI_USAGE.md).*

---

## 10. Third-Party Code & Assets

- **Icons & UI:** Lucide React, Tailwind CSS UI components.
- **Standard Libraries:** FastAPI, Pydantic, PyYAML, Pytest.
- **Official Data References:** ILO Fair Recruitment Guidelines, BMET public circulars, IOM Bangladesh reports.

---

## 11. Quick Start & Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- Git

### Backend Setup
```bash
# Clone the repository
git clone https://github.com/afradd/Mig_Guard.git
cd Mig_Guard/backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run unit tests
python -m pytest tests/ -v

# Start backend server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend Setup
```bash
cd ../frontend
npm install
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) to view the application.

### Run Evaluation & Data Validation
```bash
# In repository root
python scripts/validate_data.py
python eval/run_eval.py
```

---

## 12. Links & Deliverables

- **Public GitHub Repo:** [https://github.com/afradd/Mig_Guard](https://github.com/afradd/Mig_Guard)
- **Live Deployment:** [https://mig-guard.vercel.app](https://mig-guard.vercel.app) *(or active host URL)*
- **Demo Script:** [docs/demo-script.md](docs/demo-script.md)
- **Official 150-Word Submission:** [docs/submission-text.md](docs/submission-text.md)
- **Architecture Notes:** [docs/architecture.md](docs/architecture.md)
- **API Contract:** [docs/api-contract.md](docs/api-contract.md)
- **Privacy Policy:** [docs/privacy-and-safety.md](docs/privacy-and-safety.md)

---
*Built with ❤️ for prospective migrant workers worldwide at CoU AI Hackathon 2026.*
