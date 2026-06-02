# UX Use Cases

This document describes the user-facing workflows available in the Share Transfer Instruction platform. Each use case follows a goal-oriented format: who the user is, what they want to achieve, and the steps involved.

---

## UC-1: Standard Instrument Search

**Goal:** Manually search for instruments to verify availability in the EasyEquities ecosystem.

### Preconditions
- User has access to the application URL.

### Flow

1. **Onboarding** -- User enters their full name and EasyEquities User ID on the main page (`app/main.py`). A "Getting Started" card explains the six-step process.
2. **Wallet selection** -- User selects a wallet context (ZAR, USD, TFSA, RA, etc.) or "All Wallets" to search without restriction.
3. **Search** -- User types a query (company name, ticker symbol, or ISIN code) into the search bar and clicks "Smart Search".
4. **Review results** -- Fuzzy-matched results appear ranked by relevance. Each result card shows the instrument name, ticker, exchange, asset group, currency, and wallet availability.
5. **Select instruments** -- User clicks to add instruments to their persistent selection. The sidebar selection panel updates in real-time.
6. **Continue** -- User navigates to the Portfolio page to configure share transfer details, or performs additional searches.

### Alternate Paths
- If the query yields no results, the user can adjust the fuzzy threshold in search options or try a different wallet context.
- From the main page, the user can choose the "AI-Powered Statement Upload" journey card to switch to UC-3 instead.

---

## UC-2: AI-Assisted Discovery

**Goal:** Use the conversational AI assistant to get guidance on search strategies, wallet information, or general platform help.

### Preconditions
- Gemini API key is configured in `.streamlit/secrets.toml`.

### Flow

1. **Navigate** -- User clicks the "AI Assistance" page in the sidebar.
2. **Ask a question** -- User types a question into the chat input (e.g., "Which wallet should I use for JSE shares?").
3. **Receive guidance** -- The assistant responds using the RAG knowledge base (`instrument_finder_knowledge_base.md`) grounded by the system prompt defined in `agent_summarizer_mandate.md`.
4. **Follow recommendations** -- The assistant may suggest specific search terms, wallet contexts, or next steps. The user navigates accordingly.

### Boundaries
- The assistant does not provide financial advice.
- If the question falls outside the knowledge base, the assistant responds with a clear disclaimer.

---

## UC-3: PDF Portfolio Extraction

**Goal:** Upload a broker statement PDF and have AI automatically extract portfolio holdings for import into the platform.

### Preconditions
- User has a PDF broker/portfolio statement.
- Gemini API key is configured.

### Flow

1. **Upload** -- On the AI Assistance page, user uploads a PDF via the file uploader widget.
2. **Analyze** -- User clicks "Analyze Document". The `GeminiPDFProcessor` sends the PDF to Gemini 2.0 Flash for analysis.
3. **Review analysis** -- The assistant provides a conversational summary of the document (type, broker, number of holdings, notable positions).
4. **Extract data** -- User clicks "Extract & Pre-populate Portfolio". The processor runs a multi-tier extraction:
   - **Primary prompt** -- Structured extraction with detailed field mapping.
   - **Table-focused fallback** -- Targets tabular data specifically if primary extraction yields no entries.
   - **Aggressive text search** -- Searches for any financial instrument mentions as a last resort.
5. **Auto-match** -- Extracted instruments are matched against the instrument database using fuzzy search. Successfully matched instruments are auto-selected via `SelectionManager`.
6. **Review import** -- The chat displays a summary showing matched count, newly selected instruments, and any unmatched entries.
7. **Navigate to Portfolio** -- User proceeds to the Portfolio page where extracted data (quantity, cost basis, settlement date) pre-populates the share transfer forms.

### Alternate Paths -- Password-Protected PDFs
1. If encryption is detected, the assistant displays a password input prompt.
2. User enters the document password.
3. The system unlocks the PDF using PyMuPDF and retries extraction.
4. If the password is incorrect, the user is prompted to try again.

---

## UC-4: Portfolio Configuration

**Goal:** Configure share transfer details (quantities, costs, broker IDs) for each selected instrument before submission.

### Preconditions
- At least one instrument is selected (via search or PDF import).
- User has completed onboarding (name, user ID, wallet).

### Flow

1. **Navigate** -- User opens the "My Portfolio" page (`app/pages/2_Portfolio.py`).
2. **Overview** -- A metrics bar shows total selected instruments, configured count, and completion percentage with a progress bar.
3. **PDF data review (if applicable)** -- If instruments were imported from PDF, a summary card shows the source document, broker name, and overall confidence score. Each instrument form shows a confidence indicator:
   - Green (>80%) -- High confidence, likely correct.
   - Yellow (60-80%) -- Medium confidence, verify recommended.
   - Red (<60%) -- Low confidence, manual review required.
4. **Configure forms** -- For each instrument, the user fills in:
   - Trust Account ID
   - Quantity (supports negative values for short positions)
   - Base Cost
   - Settlement Date
   - Last Price
   - Broker From / Broker To (shown by display name)
5. **Remove instruments** -- Individual instruments can be removed via per-card remove buttons, or all instruments can be cleared with a confirmed bulk action.
6. **Proceed** -- Once all entries are configured (100% completion), the "Proceed to Submit" button becomes active.

### Alternate Paths
- User can return to the search page to add more instruments at any time.
- User can navigate to AI Assistance for help with broker IDs or settlement dates.
- Manual entries are preserved when PDF data is merged later (data source tracked as `manual_then_pdf`).

---

## UC-5: Submission and Export

**Goal:** Review the complete portfolio, accept a declaration, and submit for processing with multi-format export.

### Preconditions
- At least one instrument is selected.
- User has completed onboarding.

### Flow

1. **Navigate** -- User opens the "Submit" page (`app/pages/3_Submit.py`).
2. **Portfolio summary** -- Metrics display total instruments, unique exchanges, asset types, and selection period.
3. **Configuration status** -- If the portfolio is fully configured, a share transfer data summary is available. If incomplete, the user is directed back to the Portfolio page.
4. **Review instruments** -- Each selected instrument is displayed in an expandable card showing name, ticker, ISIN, exchange, currency, relevance score, match type, selection timestamp, source query, and wallet availability.
5. **Modify selection** -- User can remove individual instruments or return to search.
6. **Add notes** -- Optional free-text field for submission notes.
7. **Provide feedback** -- Optional feedback component for rating and comments.
8. **Accept declaration** -- User checks a brief confirmation checkbox ("I confirm the information above is accurate to the best of my knowledge").
9. **Submit** -- User clicks "Submit Search Results". The system:
   - If portfolio is complete: calls `handle_portfolio_submission()` which generates a share transfer CSV matching the broker-specific column format, a PDF report, and a standard CSV.
   - If portfolio is incomplete: calls `handle_search_results_submission()` for basic instrument data export.
   - Sends an email with all attachments via SMTP.
   - Clears selections and portfolio data after successful submission.
10. **Confirmation** -- Success message with balloons animation. Next-steps summary is shown directly (email confirmation, team review, downloadable reports). User can start a new search or get more AI help.

### Post-Submission
- User receives an email confirmation with PDF report and CSV data.
- The EasyEquities team reviews the submission and contacts the user with next steps (availability confirmation, account setup assistance, alternative suggestions).
