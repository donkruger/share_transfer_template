# Smart Search

The Smart Search feature is the primary instrument discovery mechanism. It combines multi-strategy fuzzy matching with wallet-aware filtering to let users find financial instruments across the EasyEquities ecosystem.

## Key Source Files

| File | Role |
|------|------|
| `app/main.py` | Main search page, onboarding, UI, and search orchestration |
| `app/search/fuzzy_matcher.py` | `InstrumentFuzzyMatcher` -- multi-strategy search engine |
| `app/search/wallet_filter.py` | `WalletFilterEngine` -- wallet eligibility and account filter parsing |
| `app/components/search_interface.py` | Search bar UI component |
| `app/components/result_display.py` | Result cards and selection summary |
| `app/components/wallet_selector.py` | Wallet selection UI and search stats |

## Architecture

### Data Loading

Instrument data is loaded from a CSV file at startup and cached with `@st.cache_data`. The dataset contains columns such as `Name`, `Ticker`, `ISINCode`, `Exchange`, `ContractCode`, `AssetGroup`, `AssetSubGroup`, `ActiveData`, and `accountFiltersArray`.

Wallet configuration is loaded from `app/data/wallet_specifications.json`, mapping wallet IDs to display names and currencies.

### Fuzzy Matching Engine (`InstrumentFuzzyMatcher`)

The matcher initialises three lookup indices on construction:
- **Name index** -- `Name` column to DataFrame row index.
- **Ticker index** -- `Ticker` column to row index.
- **ISIN index** -- `ISINCode` column to row index.

#### Search Strategy (Priority Order)

Each search runs four strategies in sequence. Results are merged, deduplicated, and ranked.

| Priority | Strategy | Scorer | Threshold | Match Types |
|----------|----------|--------|-----------|-------------|
| 1 | Exact matches | String equality | Exact | `exact_name`, `exact_ticker` |
| 2 | Starts-with name | `str.startswith` | 3+ char query | `starts_with_name` |
| 3 | Fuzzy name | `token_sort_ratio` + `WRatio` | Configurable (default 75) | `fuzzy_name` |
| 4 | Fuzzy ticker | `fuzz.ratio` | `max(60, threshold - 20)` | `ticker_exact`, `fuzzy_ticker` |
| 5 | ISIN | `fuzz.ratio` | `max(85, threshold)` | `isin_exact`, `isin_fuzzy` |

Combined scores use the maximum of `token_sort_ratio` and `WRatio` for name matching, providing robustness against word reordering and partial inputs.

#### Deduplication

Results are deduplicated using a business key of `(Exchange, Ticker, ContractCode)` (uppercased). If any part of the business key is missing, a legacy key of `(InstrumentID, Name)` is used as fallback. When duplicates occur, the entry with the lowest priority number (highest priority) wins; ties are broken by relevance score.

### Wallet Filtering (`WalletFilterEngine`)

Before fuzzy matching runs, the instrument dataset is filtered:
1. **Active filter** -- Removes instruments where `ActiveData == 0`.
2. **Wallet filter** -- If a specific wallet ID is selected, instruments are filtered by regex match on the `accountFiltersArray` column. If "All Wallets" is selected, no wallet filtering is applied.

The `WalletFilterEngine` also provides:
- `get_available_wallets(account_filters_str)` -- returns all wallets where an instrument is eligible.
- `is_available_in_wallet(account_filters_str, wallet_name)` -- single-wallet availability check.

### Supported Wallets

| ID | Name | Display Name | Currency |
|----|------|-------------|----------|
| 2 | ZAR | EasyEquities ZAR | ZAR |
| 3 | TFSA | Tax-Free Savings Account | ZAR |
| 9 | RA | Retirement Annuity | ZAR |
| 10 | USD | EasyEquities USD | USD |
| 74 | GBP | EasyEquities GBP | GBP |
| 75 | EUR | EasyEquities EUR | EUR |
| 16 | AUD | EasyEquities AUD | AUD |
| 55 | LA | Living Annuity | ZAR |
| 48 | PENS | Preservation Pension Fund | ZAR |
| 24 | PROV | Preservation Provident Fund | ZAR |

### Currency Determination

The `_determine_currency` method maps exchange codes to currencies (e.g., JSE -> ZAR, NYSE/NASDAQ -> USD, LSE -> GBP). If no exchange mapping exists, it inspects `accountFilters/TradingCurrency*` columns as a secondary heuristic, defaulting to ZAR.

## Result Object Schema

Each search result is a dictionary with the following fields:

```
instrument_id    -- Unique ID from the dataset
name             -- Full instrument name
ticker           -- Ticker symbol
isin             -- ISIN code
contract_code    -- Contract code
asset_group      -- Asset group classification
asset_sub_group  -- Asset sub-group classification
exchange         -- Exchange code
currency         -- Determined trading currency
description      -- Instrument description
relevance_score  -- Integer 0-100
match_type       -- One of the match type strings above
priority         -- Integer (lower = higher priority)
account_filters  -- Raw account filter string for wallet checks
raw_data         -- Full row from the source DataFrame
```
