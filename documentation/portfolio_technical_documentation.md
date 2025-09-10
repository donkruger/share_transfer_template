# Portfolio Feature - Technical Documentation

## Executive Summary

The Portfolio feature is fully implemented in the Smart Instrument Finder application, providing comprehensive share transfer data capture with AI-integration readiness for future PDF processing capabilities.

## Current Implementation State

### Completed Components

| Component | File | Description |
|-----------|------|-------------|
| Portfolio Page | `app/pages/2_Portfolio.py` | Main portfolio configuration interface |
| Share Transfer Form | `app/components/share_transfer_form.py` | Reusable form component with validation |
| Portfolio Service | `app/services/portfolio_service.py` | Business logic and data management |
| Submission Integration | `app/components/submission.py` | Enhanced submission with CSV generation |
| Data Schemas | `app/data/portfolio_schema.json` | JSON schema for AI integration |
| Validators | `app/json_validators.py` | JSON validation utilities |

## Architecture Overview

```
User Interface Layer
├── Portfolio Page (2_Portfolio.py)
│   ├── Instrument Selection Display
│   ├── Progress Tracking
│   └── Share Transfer Forms
│
Service Layer
├── PortfolioService
│   ├── Data Management (CRUD)
│   ├── Validation Logic
│   ├── CSV Generation
│   └── AI Data Import (Ready)
│
Data Layer
├── Session State (Current Storage)
├── JSON Schema (AI Contract)
└── CSV Output (Target Format)
```

## Data Model

### Portfolio Entry Structure

```python
portfolio_entry = {
    # Core Fields (Required)
    'platform': 'EE',              # EE or SX
    'trust_account_id': '8275727', # 6-10 digits
    'quantity': -4,                # Can be negative
    'base_cost': 5574.403385,      # Per unit cost
    'settlement_date': '2025-09-10', # YYYY-MM-DD
    'last_price': 10863.00,        # Current price
    'broker_from': '9',            # Source broker ID
    'broker_to': '26',             # Destination broker ID
    
    # AI Integration Fields (When from PDF)
    'data_source': 'pdf_parser',   # Source type
    'ai_confidence': 0.85,         # Overall confidence
    'source_document': 'statement.pdf',
    'ai_extracted_fields': {       # Per-field confidence
        'trust_account_id': 0.95,
        'quantity': 0.90,
        'base_cost': 0.75
    }
}
```

### CSV Output Format

```csv
SX/EE,User ID ,TrustAccountID,ShareCode,InstrumentID,Qty,Base Cost ©,Excel Date,SettlementDate,Last Price,BrokerID_From,BrokerID_To,Reference,,
EE,1809263,8275727,STXWDM,2827,-4,5574.403385,2025/09/10,2025-09-10,10863.00,9 ,26 ,NT -2025-09-10,NT -,2025/09/10
```

## AI Integration for PDF Processing

### 1. JSON Schema for AI Agents

The system accepts portfolio data from AI agents through `app/data/portfolio_schema.json`:

```json
{
  "metadata": {
    "source": "pdf_parser",
    "confidence_score": 0.85,
    "extraction_timestamp": "2024-01-15T10:30:00Z",
    "source_document": "portfolio_statement.pdf"
  },
  "portfolio_entries": [
    {
      "instrument_identifier": {
        "ticker": "AAPL"  // Can use ticker, ISIN, name, or ID
      },
      "portfolio_data": {
        "trust_account_id": "1234567",
        "quantity": 100,
        "base_cost": 150.50,
        "settlement_date": "2024-01-10",
        "last_price": 160.75,
        "broker_from": "9",
        "broker_to": "26"
      }
    }
  ]
}
```

### 2. PDF Processing Flow

```
PDF Upload → AI Agent → Text Extraction → JSON Structure → Validation → User Review → Save to Portfolio → Generate CSV
```

### 3. AI Agent Integration Points

#### Import Method (Already Implemented)

```python
# app/services/portfolio_service.py
@staticmethod
def import_ai_portfolio_data(json_data: Dict) -> Dict[str, Any]:
    """Import portfolio data from AI agent JSON."""
    # Validates against schema
    # Matches instruments to selected items
    # Stores with AI metadata for review
    # Returns success/error status
```

#### Future PDF Upload Interface

```python
# To be added to app/pages/2_Portfolio.py
uploaded_file = st.file_uploader("Upload Portfolio Statement (PDF)", type=['pdf'])

if uploaded_file:
    # Process with AI agent
    json_data = process_pdf_to_json(uploaded_file)
    
    # Import to portfolio
    result = PortfolioService.import_ai_portfolio_data(json_data)
    
    # Show review interface with confidence scores
    display_ai_review(result)
```

### 4. AI Agent Requirements

When processing PDFs, the AI agent should:

1. **Extract Key Fields**:
   - Account identifiers (Trust Account ID)
   - Instrument identifiers (Name, Ticker, ISIN)
   - Quantities and prices
   - Dates and broker information

2. **Provide Confidence Scores**:
   - Document-level confidence (0-1)
   - Field-level confidence for each value

3. **Handle Multiple Formats**:
   - Different broker statement formats
   - Various date formats
   - Multiple currency representations

## Session State Structure

```python
st.session_state = {
    'portfolio_entries': {
        '12345': {  # Keyed by instrument_id
            'platform': 'EE',
            'trust_account_id': '8275727',
            'quantity': 100,
            'base_cost': 150.50,
            'settlement_date': '2025-09-10',
            'last_price': 160.75,
            'broker_from': '9',
            'broker_to': '26'
        }
    },
    'portfolio_metadata': {
        'default_platform': 'EE',
        'default_broker_from': '9',
        'default_broker_to': '26',
        'last_updated': '2024-01-15T10:30:00'
    }
}
```

## API Design for External Agents

### Portfolio Import Endpoint (Proposed)

```
POST /api/portfolio/import
Content-Type: application/json

Request: {JSON matching portfolio_schema.json}

Response: {
    "success": true,
    "imported_count": 5,
    "errors": [],
    "review_required": true
}
```

## Current Workflow

1. User selects instruments from search results
2. Navigates to Portfolio page via sidebar
3. Configures share transfer data for each instrument
4. System validates and saves to session state
5. Submit page generates CSV in exact target format
6. Email sent with PDF report and CSV attachments

## Key Files

| File | Purpose |
|------|---------|
| `portfolio_service.py` | Core business logic |
| `portfolio_schema.json` | AI data contract |
| `broker_specifications.json` | Broker ID mappings |
| `share_transfer_form.py` | UI component |

## Validation Rules

- Trust Account ID: 6-10 digits
- Quantity: Non-zero integer (can be negative)
- Base Cost: Positive decimal
- Last Price: Positive decimal
- Settlement Date: Valid date in YYYY-MM-DD format
- Broker IDs: Must match configured brokers

## Testing

```python
def test_pdf_import_workflow():
    # Load test PDF
    pdf = load_test_pdf('sample_statement.pdf')
    
    # Simulate AI extraction
    json_data = create_test_json_data()
    
    # Validate against schema
    assert validate_portfolio_json(json_data)[0] == True
    
    # Import to portfolio
    result = PortfolioService.import_ai_portfolio_data(json_data)
    assert result['success'] == True
    
    # Generate CSV
    csv_data = PortfolioService.generate_share_transfer_data()
    assert len(csv_data) > 0
```

## Security Considerations

- PDF files not permanently stored
- Session state cleared on logout
- Input validation at multiple layers
- Schema validation for AI data
- Manual review required for AI imports

## Deployment Status

### Production Ready
- Manual portfolio data entry ✅
- CSV generation ✅
- Email submission ✅
- Full validation ✅

### Future Implementation
- PDF upload interface 🔄
- AI agent integration 🔄
- Bulk import features 🔄
- API endpoints 🔄

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Navigation errors | Check `st.switch_page()` paths relative to app/ |
| Import failures | Validate JSON against schema |
| CSV format issues | Verify exact column names and spacing |
| Session state loss | Ensure `initialize_state()` called |

## Conclusion

The Portfolio feature is fully operational with robust architecture ready for AI integration. The system provides complete manual workflow while being designed for future intelligent automation through PDF processing and AI agents.
