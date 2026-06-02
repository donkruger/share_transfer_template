# Portfolio Management

The Portfolio Management feature provides a form-based interface for configuring share transfer details for each selected instrument. It integrates with the PDF extraction pipeline for data pre-population and tracks data completeness.

## Key Source Files

| File | Role |
|------|------|
| `app/pages/2_Portfolio.py` | Portfolio page UI, instrument forms, progress tracking |
| `app/services/portfolio_service.py` | `PortfolioService` -- CRUD, validation, CSV generation, PDF import |
| `app/components/share_transfer_form.py` | `ShareTransferForm` -- per-instrument form component |

## Architecture

### Session State

Portfolio data lives in `st.session_state` with three keys initialised by `PortfolioService.initialize_portfolio_state()`:

| Key | Type | Purpose |
|-----|------|---------|
| `portfolio_entries` | `Dict[str, Dict]` | Keyed by `instrument_id`, each value holds the share transfer fields |
| `portfolio_metadata` | `Dict` | Defaults (`platform`, `broker_from`, `broker_to`) and timestamps |
| `portfolio_form_data` | `Dict` | Temporary form state for in-progress edits |

### Required Fields per Instrument

| Field | Type | Notes |
|-------|------|-------|
| `trust_account_id` | string | Client trust account identifier |
| `quantity` | int | Supports negative values (short positions) |
| `base_cost` | float | Cost per share/unit |
| `settlement_date` | string (YYYY-MM-DD) | Settlement date for the transfer |
| `last_price` | float | Last known price |
| `broker_from` | string | Originating broker ID |
| `broker_to` | string | Destination broker ID |

### Completeness Check

`PortfolioService.is_portfolio_complete()` iterates all selected instruments and verifies that every required field is present and non-empty (with `quantity` allowed to be zero or negative). The Portfolio page displays a progress bar and metric cards reflecting this status.

## PDF Data Import

When the AI Assistance page extracts data from a PDF, `PortfolioService.import_from_pdf_extraction()` handles the import:

### Instrument Matching Pipeline

1. **Match against selections** -- `_match_with_selected()` checks the extracted entry against already-selected instruments using exact ticker match, ISIN match, and fuzzy name match (threshold 0.8 via `SequenceMatcher`).
2. **Database fuzzy search** -- If not already selected, the system loads the full instrument CSV and runs `InstrumentFuzzyMatcher.search_instruments()` with:
   - Ticker search across all wallets.
   - Name search across all wallets.
   - Cleaned name search (strips "Inc", "Corp", "Corporation").
   - Low-threshold retry (threshold 60) if no results from above.
3. **Auto-selection** -- Successfully matched instruments are automatically added to the user's selection via `SelectionManager`.

### Data Merge Strategy

When a portfolio entry already exists (e.g., from manual input) and PDF data arrives:

- **Metadata fields** (`data_source`, `extraction_confidence`, etc.) are updated. The `data_source` becomes `manual_then_pdf` to preserve provenance.
- **Data fields** (`trust_account_id`, `quantity`, `base_cost`, `last_price`, `settlement_date`, brokers) are only updated if the existing value is empty or still at the default. Manual edits are always preserved.
- A `pdf_merged` flag and `merge_timestamp` are set on the entry.

### Confidence Indicators

The Portfolio page renders confidence badges per instrument:

| Confidence | Indicator | Meaning |
|------------|-----------|---------|
| > 80% | Green | High confidence -- data likely correct |
| 60-80% | Yellow | Medium confidence -- verification recommended |
| < 60% | Red | Low confidence -- manual review required |

Entries with the `manual_then_pdf` data source show a blue "Manual entry enhanced with PDF data" badge.

## Share Transfer CSV Generation

`PortfolioService.generate_share_transfer_data()` produces records matching the broker-specific CSV column format:

| Column | Source |
|--------|--------|
| `SX/EE` | Platform default (session metadata) |
| `User ID ` | User's EasyEquities ID |
| `TrustAccountID` | Portfolio entry field |
| `ShareCode` | Instrument ticker |
| `InstrumentID` | Instrument ID (integer) |
| `Qty` | Quantity (integer, can be negative) |
| `Base Cost (c)` | Base cost (float) |
| `Excel Date` | Settlement date as YYYY/MM/DD |
| `SettlementDate` | Settlement date as YYYY-MM-DD |
| `Last Price` | Last price (float) |
| `BrokerID_From` | Originating broker ID |
| `BrokerID_To` | Destination broker ID |
| `Reference` | Auto-generated reference string |

## Portfolio Actions

The Portfolio page provides five action buttons:

1. **Search More** -- Navigate back to the main search page.
2. **Get AI Help** -- Navigate to the AI Assistance page.
3. **Remove All Instruments** -- Clears all selections and portfolio data (requires double-click confirmation).
4. **Proceed to Submit** -- Active only when portfolio is 100% complete. Navigates to the Submit page.
5. **Clear Portfolio Data** -- Clears portfolio form data without removing instrument selections (requires double-click confirmation).
