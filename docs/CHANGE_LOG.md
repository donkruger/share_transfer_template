# Change Log

All notable changes to the Share Transfer Instruction platform are documented here.

**Format:** `YYYY-MM-DD HH:MM` | Summary

---

## 2026

### June

`2026-06-02 09:00` | Fix (PROD): AI Assistance failed with `404 models/gemini-1.5-flash is not found for API version v1beta`. Upgraded both the conversational assistant (`app/pages/1_AI_Assistance.py`) and `GeminiPDFProcessor` (`app/services/gemini_pdf_processor.py`) to the latest GA Flash model `gemini-3.5-flash`

### February

`2026-02-27 12:00` | UX cleanup: removed debug output from AI Assistance, simplified Submit page metrics/declaration, removed placeholder AI import section from Portfolio, fixed feedback component branding, cleaned broker dropdowns, improved onboarding help text, consolidated submission email messages

`2026-02-27 00:00` | Documentation baseline established: created CHANGE_LOG.md, UX_USE_CASES.md, and feature documentation in /docs
