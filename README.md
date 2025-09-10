# Smart Instrument Finder App

A sophisticated financial instrument search and discovery platform built with Streamlit, featuring advanced fuzzy matching, wallet-aware filtering, and AI-powered assistance.

## Overview

The Smart Instrument Finder App is a modern web application designed to help users discover and select financial instruments across multiple investment platforms and wallets. It provides intelligent search capabilities, personalized recommendations, and seamless result submission workflows.

### Key Features

- **Advanced Fuzzy Search**: Multi-field search across instrument names, ticker symbols, ISIN codes, and contract codes
- **Wallet-Aware Filtering**: Filter instruments based on availability in specific investment wallets/platforms
- **AI-Powered Assistance**: Contextual help and guidance using Google Gemini with RAG architecture
- **Smart Deduplication**: Business-key based deduplication using (Exchange, Ticker, ContractCode)
- **Real-time Results**: Fast, cached search with relevance scoring and ranking
- **Export Capabilities**: Generate PDF reports and CSV exports of selected instruments
- **Session Persistence**: Robust state management across multiple pages
- **Responsive Design**: Modern, gradient-based UI with smooth animations

## Architecture & Core Structure

### Application Structure

```
Instrument Finder App V2/
├── .streamlit/
│   ├── config.toml          # Streamlit configuration
│   └── pages.toml           # Multi-page navigation setup
├── app/                     # Core application directory
│   ├── components/          # Modular UI components
│   │   ├── __init__.py
│   │   ├── feedback.py      # User feedback collection
│   │   ├── result_display.py # Search results presentation
│   │   ├── search_interface.py # Search input & options
│   │   ├── sidebar.py       # Navigation sidebar
│   │   ├── submission.py    # Result submission handling
│   │   └── wallet_selector.py # Wallet context selection
│   ├── data/                # Configuration & specifications
│   │   ├── __init__.py
│   │   ├── search_configurations.json # Search algorithm settings
│   │   └── wallet_specifications.json # Wallet mappings & metadata
│   ├── pages/               # Multi-page application structure
│   │   ├── 1_AI_Assistance.py # RAG-powered AI assistant
│   │   └── 2_Submit.py      # Results review & submission
│   ├── search/              # Core search engine
│   │   ├── __init__.py
│   │   ├── fuzzy_matcher.py # Advanced fuzzy matching algorithm
│   │   └── wallet_filter.py # Wallet-aware filtering engine
│   ├── __init__.py
│   ├── email_sender.py      # SMTP email functionality
│   ├── main.py              # Primary search interface (landing page)
│   ├── pdf_generator.py     # PDF report generation
│   ├── styling.py           # CSS styling & animations
│   └── utils.py             # Session management & utilities
├── assets/
│   └── logos/               # Visual assets & branding
├── data/
│   └── Instrument_Data_Format_Example.csv # Financial instrument dataset
├── documentation/
│   └── persisted_selection_solution_design.md # Technical solution designs
├── agent_summarizer_mandate.md    # AI agent persona & constraints
├── instrument_finder_knowledge_base.md # RAG knowledge base
├── README.md                # Project documentation
└── requirements.txt         # Python dependencies
```

### Core Application Flow

```mermaid
graph TD
    A[User Lands on Main Page] --> B[User Onboarding]
    B --> C[Name & User ID Input]
    C --> D[Wallet Context Selection]
    D --> E[Search Interface]
    E --> F[Fuzzy Search Engine]
    F --> G[Wallet-Filtered Results]
    G --> H[Result Selection]
    H --> I{User Choice}
    I -->|Need Help| J[AI Assistance Page]
    I -->|Ready to Submit| K[Submit Results Page]
    J --> L[RAG-Powered Guidance]
    L --> I
    K --> M[Review & Declaration]
    M --> N[PDF/CSV Generation]
    N --> O[Email Submission]
    O --> P[Success & Downloads]
```

### Technical Stack

- **Frontend**: Streamlit (Python web framework)
- **Search Engine**: FuzzyWuzzy with Python-Levenshtein for fast string matching
- **Data Processing**: Pandas for CSV handling and data manipulation
- **AI Integration**: Google Gemini 1.5 Flash via API
- **PDF Generation**: ReportLab for document creation
- **Email**: SMTP with attachment support
- **Session Management**: Streamlit session state with namespace isolation

### Data Model

The application works with a comprehensive instrument dataset containing:

- **Core Identifiers**: InstrumentID, Ticker, ContractCode, ISINCode
- **Classification**: AssetGroup, AssetSubGroup, Exchange
- **Metadata**: Name, Description, Currency, ActiveData status
- **Wallet Eligibility**: 22 accountFilters columns mapped to wallet codes
- **UI Assets**: Logos, flag codes for visual presentation

#### Wallet Mapping System

The app uses a sophisticated wallet filtering system with 22 wrapper types:

| Wallet | Code | Description |
|--------|------|-------------|
| ZAR | 2 | South African Rand accounts |
| TFSA | 3 | Tax-Free Savings Account |
| USD | 10 | US Dollar accounts |
| GBP | 74 | British Pound accounts |
| EUR | 75 | Euro accounts |
| AUD | 16 | Australian Dollar accounts |
| RA | 9 | Retirement Annuity |
| RISE | 11 | RISE Investment platform |
| EasyCrypto | 99 | Cryptocurrency platform |
| EasyProperties | 66 | Property investment platform |
| ... | ... | (Additional wallets as configured) |

## Installation

### Prerequisites

- Python 3.9+
- pip package manager
- Internet connection for AI features

### Setup Steps

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd "Instrument Finder App V2"
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure secrets** (create `.streamlit/secrets.toml`):
   ```toml
   [app]
   max_upload_mb = 4
   
   [email]
   smtp_server = "smtp.gmail.com"
   smtp_port = 587
   sender_email = "your-email@example.com"
   sender_password = "your-app-password"
   
   [ai]
   gemini_api_key = "your-gemini-api-key"
   ```

4. **Prepare data**:
   - Place your instrument CSV file in the `data/` directory
   - Update the file path in `app/main.py` if needed

5. **Run the application**:
   ```bash
   streamlit run app/main.py
   ```

## Usage

### 1. Smart Search Page

The main landing page where users can:
- Enter their name and user ID for session tracking
- Select their preferred investment wallet
- Search for instruments using natural language queries
- Review and select instruments from ranked results
- Apply advanced search filters (fuzzy threshold, result limits)

### 2. AI Assistance Page

An intelligent assistant that provides:
- Context-aware help based on user's search history
- Explanations of search results and instrument details
- Investment guidance within defined knowledge boundaries
- Wallet-specific recommendations

### 3. Submit Results Page

Final submission workflow featuring:
- Review of selected instruments
- Additional notes and feedback collection
- Declaration acceptance
- Automated PDF and CSV generation
- Email delivery to configured recipients

## Key Business Logic & Algorithms

### Instrument Deduplication Strategy

The application uses a **business key approach** for deduplication as recommended in the CSV analysis:

```python
def get_instrument_key(instrument: Dict) -> str:
    # Primary: Business Key (Exchange, Ticker, ContractCode)
    business_key = (
        (instrument.get('exchange') or '').upper(),
        (instrument.get('ticker') or '').upper(), 
        (instrument.get('contract_code') or '').upper()
    )
    
    if any(business_key):
        return f"BUSINESS_KEY|{business_key[0]}|{business_key[1]}|{business_key[2]}"
    
    # Fallback: Legacy Key (InstrumentID, Name)
    return f"LEGACY_KEY|{instrument.get('instrument_id', '')}|{instrument.get('name', '').upper()}"
```

### Wallet Eligibility Algorithm

```python
def derive_filters_array(row) -> str:
    """Derives accountFiltersArray from 22 wrapper columns"""
    codes = []
    wrapper_cols = [c for c in columns if c.startswith('accountFilters/')]
    
    for column in wrapper_cols:
        try:
            value = int(row.get(column, 0))
            if value != 0:
                codes.append(str(value))
        except (ValueError, TypeError):
            continue
    
    # Deduplicate while preserving order
    return ','.join(dict.fromkeys(codes))
```

### Search Relevance Scoring

```python
# Match Type Priority & Scoring
MATCH_PRIORITIES = {
    'exact_name': (0, 100),      # Highest priority, 100% relevance
    'exact_ticker': (1, 95),     # High priority, 95% relevance  
    'fuzzy_name': (2, 'dynamic'), # Medium priority, fuzzy score
    'ticker': (3, 'dynamic'),    # Lower priority, fuzzy score
    'isin': (4, 'dynamic')       # Lowest priority, fuzzy score
}

def calculate_final_score(match_type: str, fuzzy_score: int) -> int:
    priority, base_score = MATCH_PRIORITIES[match_type]
    return base_score if base_score != 'dynamic' else fuzzy_score
```

## Production Deployment Considerations

### Scalability Architecture

```mermaid
graph TB
    A[Load Balancer] --> B[Streamlit App Instance 1]
    A --> C[Streamlit App Instance 2] 
    A --> D[Streamlit App Instance N]
    
    B --> E[Shared File Storage]
    C --> E
    D --> E
    
    B --> F[Email Service]
    C --> F
    D --> F
    
    B --> G[Gemini API]
    C --> G
    D --> G
    
    E --> H[Instrument Data CSV]
    E --> I[Configuration Files]
    E --> J[Generated Reports]
```

### Environment Configuration

#### Production Secrets (`secrets.toml`)
```toml
[app]
max_upload_mb = 10
environment = "production"

[email]
smtp_server = "smtp.company.com"
smtp_port = 587
sender_email = "noreply@company.com"
sender_password = "secure_app_password"

[llm_api]  
gemini_key = "production_api_key"

[monitoring]
error_reporting_endpoint = "https://monitoring.company.com/errors"
analytics_endpoint = "https://analytics.company.com/events"
```

#### Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health
CMD ["streamlit", "run", "app/main.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Security Considerations

#### Data Protection
- **Input Sanitization**: All user inputs validated and sanitized
- **File Upload Limits**: Configurable file size limits (default 4MB)
- **Session Security**: Secure session state management with UUIDs
- **API Key Protection**: Secrets stored securely, never in code

#### Access Control
- **Rate Limiting**: Implement request rate limiting for API calls
- **User Tracking**: Session-based user identification and audit trails
- **Data Retention**: Configurable data retention policies for user sessions

### Monitoring & Analytics

#### Key Metrics to Track
```python
# User Engagement Metrics
- Session duration and page visits
- Search query patterns and success rates
- Instrument selection patterns
- AI assistant usage frequency

# Performance Metrics  
- Search response times
- CSV loading performance
- Memory usage patterns
- Error rates by component

# Business Metrics
- Most searched instruments
- Wallet preference distributions  
- Submission completion rates
- User feedback sentiment
```

#### Error Monitoring
```python
# Critical Error Categories
1. Data Loading Failures (CSV parsing, missing files)
2. Search Engine Errors (fuzzy matching failures)
3. AI Service Outages (Gemini API failures)
4. Email Delivery Issues (SMTP failures)
5. Session State Corruption
```

## Development

### Key Components

#### Fuzzy Matcher (`app/search/fuzzy_matcher.py`)

The core search engine implements:
- Multi-field fuzzy matching with configurable thresholds
- Relevance scoring and ranking algorithms
- Business-key based deduplication
- Wallet-aware result filtering

#### Wallet Filter (`app/search/wallet_filter.py`)

Handles:
- Wallet eligibility validation
- Account filter parsing from CSV data
- Dynamic wallet list generation

#### Session Management (`app/utils.py`)

Provides:
- Namespace isolation for component state
- Persistent widget helpers
- Session tracking and analytics
- Robust data loading with caching

## Technical Implementation Deep Dive

### Search Engine Architecture

#### Multi-Strategy Fuzzy Matching (`app/search/fuzzy_matcher.py`)

The core search engine implements a sophisticated multi-strategy approach:

```python
# Search Strategy Priority (highest to lowest)
1. Exact Name Matches (100% relevance)
2. Exact Ticker Matches (95% relevance) 
3. Fuzzy Name Matching (configurable threshold)
4. Ticker Fuzzy Matching (lower threshold)
5. ISIN Code Matching (high precision)
```

**Key Features:**
- **Business Key Deduplication**: Uses `(Exchange, Ticker, ContractCode)` as primary key
- **Configurable Thresholds**: Separate thresholds for different field types
- **Relevance Scoring**: Weighted scoring based on match type and quality
- **Performance Optimization**: Pre-built indices for fast lookups

#### Wallet-Aware Filtering (`app/search/wallet_filter.py`)

```python
# Wallet Filter Process
CSV Data → Parse accountFilters/* columns → Build accountFiltersArray → Filter by wallet_id
```

**Implementation Details:**
- Parses 22 `accountFilters/*` columns into unified `accountFiltersArray`
- Supports both existing and derived filter arrays
- Validates wallet eligibility using regex pattern matching
- Provides wallet metadata and display information

### Data Processing Pipeline

#### CSV Data Ingestion (`app/utils.py`)

```mermaid
graph LR
    A[Raw CSV] --> B[Column Normalization]
    B --> C[Data Type Conversion]
    C --> D[accountFiltersArray Derivation]
    D --> E[Active Instrument Filtering]
    E --> F[Cached DataFrame]
```

**Processing Steps:**
1. **Column Validation**: Ensures required columns exist with fallbacks
2. **Type Normalization**: Converts data types and handles missing values
3. **Filter Array Generation**: Derives `accountFiltersArray` from wrapper columns
4. **Active Filtering**: Removes inactive instruments (`ActiveData != 0`)
5. **Caching**: Uses `@st.cache_data` for performance optimization

### Session State Management

#### Namespace Isolation Pattern

```python
# Session State Structure
st.session_state = {
    # User Context
    "user_name": str,
    "user_id": str,
    "selected_wallet": str,
    "selected_wallet_id": str,
    
    # Search State (Temporary)
    "current_results": List[Dict],
    "search_history": List[Dict],
    "search_preferences": Dict,
    
    # Selection State (Persistent)
    "selected_instruments": List[Dict],  # Persists across searches
    "submission_notes": str,
    
    # AI Assistant State
    "messages": List[Dict],  # Chat history
    
    # Session Metadata
    "session_id": str,
    "page_visits": Dict[str, int]
}
```

### AI Architecture (RAG System)

The AI assistance uses a sophisticated Retrieval-Augmented Generation approach:

#### Knowledge Base Architecture
```mermaid
graph TD
    A[User Query] --> B[Context Builder]
    B --> C[System Prompt Construction]
    C --> D[Knowledge Base Injection]
    D --> E[User Context Integration]
    E --> F[Gemini API Call]
    F --> G[Response Generation]
    G --> H[Hallucination Prevention]
    H --> I[Contextual Response]
```

**Components:**
1. **Knowledge Base**: `instrument_finder_knowledge_base.md` - Curated information about the application, search strategies, and wallet details
2. **Agent Mandate**: `agent_summarizer_mandate.md` - Defines AI persona, constraints, and operational guidelines
3. **Dynamic Context**: Real-time user state integration (search history, selections, wallet context)
4. **Hallucination Prevention**: Strict constraints to only use provided knowledge

#### Context-Aware System Prompt

```python
def create_system_prompt():
    return f"""
    AGENT MANDATE: {agent_mandate}
    
    USER CONTEXT:
    - Name: {user_name}
    - Wallet: {selected_wallet}
    - Search History: {recent_searches}
    - Selected Instruments: {selected_count}
    
    KNOWLEDGE BASE: {knowledge_base}
    """
```

### Component Architecture

#### Modular UI Components (`app/components/`)

Each component follows a consistent pattern:

```python
class ComponentName:
    def __init__(self, dependencies):
        self.dependencies = dependencies
    
    def render(self, **kwargs) -> ReturnType:
        # Component-specific rendering logic
        # Returns processed data or user selections
```

**Component Responsibilities:**
- **`search_interface.py`**: Search input, options, and triggers
- **`result_display.py`**: Results presentation and selection management
- **`wallet_selector.py`**: Wallet context selection and user onboarding
- **`submission.py`**: Result processing, PDF/CSV generation, email sending
- **`sidebar.py`**: Navigation and branding
- **`feedback.py`**: User feedback collection and rating system

### Data Flow Architecture

#### Search Flow
```mermaid
sequenceDiagram
    participant U as User
    participant SI as SearchInterface
    participant FM as FuzzyMatcher
    participant WF as WalletFilter
    participant RD as ResultDisplay
    participant SS as SessionState
    
    U->>SI: Enter search query
    SI->>FM: search_instruments(query, wallet_id)
    FM->>WF: filter_by_wallet(wallet_id)
    WF-->>FM: filtered_dataframe
    FM->>FM: multi_strategy_search()
    FM-->>SI: ranked_results
    SI->>SS: store current_results
    SI->>RD: render_results(results)
    RD->>U: display_results_with_selection
    U->>RD: select_instruments
    RD->>SS: update selected_instruments
```

#### Submission Flow
```mermaid
sequenceDiagram
    participant U as User
    participant SP as SubmitPage
    participant SC as SubmissionComponent
    participant PG as PDFGenerator
    participant ES as EmailSender
    participant SS as SessionState
    
    U->>SP: navigate_to_submit
    SP->>SS: get selected_instruments
    SS-->>SP: instruments_list
    SP->>U: display_review_interface
    U->>SP: accept_declaration_and_submit
    SP->>SC: handle_search_results_submission()
    SC->>PG: generate_pdf(submission_data)
    PG-->>SC: pdf_bytes
    SC->>ES: send_email(submission_data, pdf)
    ES-->>SC: email_confirmation
    SC->>U: success_message_and_downloads
```

### Configuration Management

#### Wallet Specifications (`app/data/wallet_specifications.json`)

```json
{
  "wallet_mappings": {
    "wallet_id": {
      "name": "short_name",
      "display_name": "user_friendly_name", 
      "currency": "currency_code",
      "active": boolean,
      "description": "detailed_description"
    }
  },
  "default_wallets": ["priority_wallet_list"],
  "search_settings": {
    "fuzzy_threshold": 80,
    "max_results": 50
  }
}
```

#### Search Configurations (`app/data/search_configurations.json`)

```json
{
  "fuzzy_search": {
    "default_threshold": 80,
    "ticker_threshold": 60,
    "isin_threshold": 85,
    "search_modes": {
      "smart": {"exact_weight": 1.0, "fuzzy_weight": 0.8},
      "exact_only": {"exact_weight": 1.0, "fuzzy_weight": 0.0},
      "fuzzy_only": {"exact_weight": 0.0, "fuzzy_weight": 1.0}
    }
  },
  "display_settings": {
    "results_per_page": 25,
    "show_relevance_scores": true,
    "highlight_exact_matches": true
  }
}
```

### Performance Optimization

#### Caching Strategy

```python
@st.cache_data
def load_instruments_data(csv_path: str) -> pd.DataFrame:
    # Heavy data processing cached at application level
    
@st.cache_data  
def load_application_data():
    # Configuration and data loading cached
```

#### Memory Management

- **Session State Cleanup**: Automatic cleanup of old search history (50 item limit)
- **Result Pagination**: Configurable result limits to prevent memory bloat
- **Lazy Loading**: Components loaded only when needed
- **Data Streaming**: Large datasets processed in chunks

### Error Handling & Resilience

#### Graceful Degradation

```python
try:
    # Primary functionality
    result = primary_operation()
except SpecificException as e:
    # Fallback with user notification
    st.warning(f"Feature unavailable: {e}")
    result = fallback_operation()
except Exception as e:
    # Graceful failure with logging
    st.error("An unexpected error occurred")
    log_error(e)
    result = safe_default()
```

#### Data Validation

- **CSV Schema Validation**: Ensures required columns exist
- **Type Safety**: Robust type conversion with error handling  
- **Input Sanitization**: User input validation and cleaning
- **State Consistency**: Session state validation and recovery

### Adding New Features

To extend the application:

1. **New Search Fields**: Add field handling in `fuzzy_matcher.py`
2. **Additional Wallets**: Update `wallet_specifications.json`
3. **UI Components**: Create new components in `app/components/`
4. **Data Sources**: Extend `load_instruments_data()` in `utils.py`

## Data Requirements

### CSV Format

The instrument data CSV should contain:

**Required Columns**:
- `Name`: Instrument display name
- `Ticker`: Trading symbol
- `Exchange`: Trading venue
- `ContractCode`: Internal contract identifier
- `ActiveData`: Status (1=active, 0=inactive)

**Optional Columns**:
- `InstrumentID`: Internal numeric ID
- `ISINCode`: International Securities ID
- `AssetGroup`: Instrument category
- `accountFilters/*`: 22 wallet eligibility columns
- `accountFiltersArray`: Comma-separated wallet codes

### Data Quality

The application handles:
- Missing or empty fields gracefully
- Automatic derivation of `accountFiltersArray` from wrapper columns
- Deduplication using business keys
- Data type normalization and cleaning

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed and Python path is correct
2. **CSV Loading**: Check file path and column names in your data file
3. **AI Features**: Verify Gemini API key is configured in secrets.toml
4. **Email Sending**: Confirm SMTP settings and app passwords

### Performance Optimization

- Large datasets: Increase caching limits in Streamlit configuration
- Slow searches: Adjust fuzzy thresholds and result limits
- Memory usage: Regular session state cleanup for long-running sessions

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with appropriate tests
4. Submit a pull request with detailed description

## License

This project is proprietary software. All rights reserved.

## Support

For technical support or feature requests, please contact the development team.

---

*Smart Instrument Finder App - Making investment discovery intelligent and accessible.*
