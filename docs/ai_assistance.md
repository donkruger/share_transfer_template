# AI Assistance

The AI Assistance feature provides a conversational assistant powered by Google Gemini 3.5 Flash, combined with PDF document processing for automated portfolio data extraction.

## Key Source Files

| File | Role |
|------|------|
| `app/pages/1_AI_Assistance.py` | AI chat page, PDF upload UI, extraction workflow |
| `app/services/gemini_pdf_processor.py` | `GeminiPDFProcessor` -- PDF analysis, extraction, password handling |
| `instrument_finder_knowledge_base.md` | RAG knowledge base for the conversational assistant |
| `agent_summarizer_mandate.md` | Agent persona, operational framework, and behavioural constraints |

## Conversational Assistant

### RAG Architecture

The assistant uses a Retrieval-Augmented Generation pattern:

1. **Knowledge base** -- Loaded from `instrument_finder_knowledge_base.md` at page initialisation. Contains application features, search strategies, wallet information, and common issue resolutions.
2. **System prompt** -- Combines the knowledge base into a structured system prompt that constrains the model to the Instrument Finder domain.
3. **Conversation history** -- Full message history is passed to `model.generate_content()` on each turn, maintaining context across the session.
4. **Session context** -- Current user name, selected wallet, search results, and selected instruments are displayed in an expandable "Current Session Context" panel so the assistant can reference them.

### Behavioural Boundaries

- Answers only questions pertaining to instrument searching and portfolio discovery.
- If information is not in the knowledge base, responds with a clear disclaimer.
- Does not provide financial advice.

### Model Configuration

- **Model:** `gemini-3.5-flash` (latest GA Flash model; the same model string is used by both the conversational assistant and `GeminiPDFProcessor`)
- **API Key:** Loaded from `st.secrets["llm_api"]["gemini_key"]`

## PDF Document Processing

### Upload Flow

1. User uploads a PDF via `st.file_uploader` (accepts `.pdf` only).
2. User clicks "Analyze Document" to trigger `process_uploaded_pdf()`.
3. The processor first checks for encryption, then analyses or extracts data.

### GeminiPDFProcessor

#### Encryption Handling

Password-protected PDFs are handled with a detect-prompt-unlock cycle:

1. **Detection** -- `check_pdf_encryption()` opens the PDF with PyMuPDF (`fitz`) and checks `doc.is_encrypted`.
2. **User prompt** -- If encrypted and no password is available, a password input UI is rendered in-chat.
3. **Unlock** -- `unlock_pdf()` calls `doc.authenticate(password)`. On success, the unlocked bytes are used for subsequent processing.
4. **Retry** -- If the password is incorrect, the user is prompted again. Passwords are stored only in session state for the current session.

#### Document Analysis

`analyze_document()` sends the PDF to Gemini with a conversational analysis prompt. The response summarises:
- Document type (portfolio statement, broker statement, etc.)
- Key information (account details, date range, total value)
- Number of holdings identified
- Notable instruments or largest positions
- Suitability for portfolio configuration

#### Multi-Tier Extraction

`process_pdf()` runs a cascading extraction strategy:

| Tier | Method | Prompt Focus | Confidence |
|------|--------|-------------|------------|
| 1 | `_extract_with_primary_prompt` | Detailed structured extraction with column-by-column guidance | High |
| 2 | `_extract_with_table_focus` | Targets tabular data specifically | Medium |
| 3 | `_extract_with_aggressive_text_search` | Searches for any financial instrument mentions | Low |
| 4 | Demo fallback | Returns sample entries if a demo/test document is detected | N/A |

Each tier produces a JSON response that is:
1. Cleaned of markdown code fences.
2. Parsed from the response text using regex JSON extraction as a fallback.
3. Validated by `_validate_extraction()` which ensures required fields exist, cleans ticker symbols (removes parentheses), and coerces numeric fields.

#### Extraction Output Schema

```json
{
  "document_metadata": {
    "document_type": "Portfolio Statement",
    "broker_name": "string",
    "account_number": "string",
    "statement_date": "YYYY-MM-DD",
    "currency": "USD/ZAR/GBP/EUR"
  },
  "portfolio_entries": [
    {
      "instrument_name": "string",
      "ticker_symbol": "string",
      "isin_code": "string or null",
      "quantity": "number",
      "cost_basis": "number",
      "current_value": "number",
      "purchase_date": "YYYY-MM-DD or null",
      "account_type": "string or null"
    }
  ],
  "confidence_scores": {
    "overall": 0.0-1.0,
    "document_quality": 0.0-1.0,
    "extraction_completeness": 0.0-1.0
  },
  "extraction_notes": ["string"]
}
```

### Post-Extraction Instrument Matching

After extraction, `PortfolioService.import_from_pdf_extraction()` matches each extracted entry against the instrument database:

1. **Selected instrument match** -- First checks against already-selected instruments by ticker, ISIN, or fuzzy name.
2. **Database search** -- Uses `InstrumentFuzzyMatcher` with multiple strategies:
   - Search by ticker across all wallets.
   - Search by name across all wallets.
   - Search by cleaned name (removing common suffixes like "Inc", "Corp").
   - Retry with a lowered threshold (60) if no results.
3. **Auto-selection** -- Matched instruments are automatically added to the user's selections via `SelectionManager.add_instrument()`.
4. **Portfolio pre-population** -- Portfolio entries are created with extracted quantities, cost basis, settlement dates, and metadata indicating the `pdf_extraction` data source.

## UI Elements

- **Lottie animations** -- A random animation is loaded from `assets/logos/lottie-jsons/` on page load.
- **Chat avatars** -- User avatar from `assets/logos/profile.svg`; assistant avatar from `assets/logos/favicon.svg`.
- **Password input** -- Rendered in-chat with help section explaining common password sources and security notes.
- **Extraction button** -- Appears contextually after document analysis, hidden once extraction is completed.
