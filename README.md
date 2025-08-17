# Entity Onboarding System

A comprehensive **Streamlit-based entity onboarding application** that supports 17 different entity types with dynamic form generation, reusable components, and intelligent validation. Built using a **semantic specification-driven architecture** for maximum modularity, maintainability, and governance.

## 🚀 **Latest Architecture Enhancements (Semantic Specification Compliance)**

- **📋 Structured Controlled Lists**: Code/label separation with JSON-based specifications for data integrity
- **👥 Role-Based Architecture**: Proper role system for Natural Persons and Entity Fields with validation rules
- **🔧 Field Specifications**: Comprehensive validation rules with cross-field dependencies and business logic
- **📄 Document Requirements**: Structured document upload requirements by entity type and role
- **⚡ Enhanced Validation Engine**: Multi-layer validation with dependency checking and special validations
- **🎯 Dynamic Form Generation**: Forms built from declarative JSON specifications
- **🔄 Data Governance**: Versioned specifications with audit trail and change management
- **🌍 Comprehensive Country Support**: Full integration with 220+ countries from CSV data source
- **👤 Authorised Representative**: Complete individual capture for all entity types
- **🎨 Enhanced UI**: Gradient text styling, Lottie animations, custom avatars
- **📧 Improved Email System**: Context-aware submissions with proper Entity Onboarding branding
- **🔧 Robust Session Management**: Automatic cleanup of legacy data, improved state isolation
- **🖼️ Consistent Branding**: Unified favicon and visual identity across all pages
- **✅ DRY Principle Compliance**: Eliminated address duplication in AuthorisedRepresentativeComponent
- **📊 CSV Data Export**: Machine-readable structured data alongside PDF summaries

## 🚀 **Quick Start**

### Prerequisites
- Python 3.11+
- Streamlit
- Required dependencies (see `requirements.txt`)

### Installation & Setup
```bash
# Clone the repository
git clone <repository-url>
cd EasyETFs_Data_App

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edit secrets.toml with your email credentials

# Run the application
streamlit run app/main.py
```

### Email Configuration
Update `.streamlit/secrets.toml`:
```toml
[email_credentials]
email_address = "your-email@domain.com"
app_password = "your-app-password"
recipient_address = "submissions@domain.com"
```

---

## 🏗️ **Project Architecture**

### **Application Flow**
The system implements a **3-page workflow**:

1. **📋 Introduction** (`app/main.py`) - Entity type selection and dynamic form rendering
2. **🤖 AI Assistance** (`app/pages/1_AI_Assistance.py`) - Context-aware help system
3. **📝 Declaration & Submit** (`app/pages/3_Declaration_and_Submit.py`) - Final validation and submission

### **Core Architecture Principles**

- **🧩 Component Reusability**: Form sections are implemented once and reused across all entity types
- **🔒 Instance Isolation**: Multiple instances of the same component can exist on one page without state collisions
- **📦 Namespace Separation**: Each entity type maintains isolated session state
- **⚙️ Declarative Configuration**: Entity forms are defined declaratively, mixing simple fields with reusable components
- **🎯 Consistent Interface**: All components implement the same interface (render/validate/serialize)

---

## 📁 **Project Structure**

```
EasyETFs_Data_App/
├── .streamlit/                    # Streamlit configuration
│   ├── config.toml               # App configuration
│   ├── pages.toml                # Page navigation setup
│   └── secrets.toml              # Email credentials (not in repo)
│
├── app/                          # Main application code
│   ├── main.py                   # 🏠 Introduction page - Entity selection & form rendering
│   ├── data/                     # 🆕 STRUCTURED DATA & SPECIFICATIONS  
│   │   ├── controlled_lists.json      # Structured controlled lists with codes/labels
│   │   ├── field_specifications.json  # Field validation rules and UI metadata
│   │   ├── role_specifications.json   # Role definitions and field mappings
│   │   ├── entity_role_rules.json     # Entity type to role requirements mapping
│   │   └── document_requirements.json # Document upload requirements
│   ├── controlled_lists_enhanced.py   # 🆕 Enhanced controlled lists manager
│   ├── field_specifications.py        # 🆕 Field specification and validation system
│   ├── document_requirements.py       # 🆕 Document requirements manager
│   ├── controlled_lists.py       # 📋 Legacy controlled lists (for compatibility)
│   ├── utils.py                  # 🔧 Utilities, state management, persistence helpers, session cleanup
│   ├── styling.py                # 🎨 CSS styling definitions (gradient text, animations)
│   ├── email_sender.py           # 📧 Entity Onboarding email submission functionality
│   ├── pdf_generator.py          # 📄 PDF generation utilities
│   ├── csv_generator.py          # 📊 CSV data export and flattening utilities
│   │
│   ├── pages/                    # Application pages
│   │   ├── 1_AI_Assistance.py    # 🤖 AI-powered help system
│   │   ├── 3_Declaration_and_Submit.py  # 📝 Final submission page
│   │   └── _archive/             # 📦 Legacy pages (preserved for reference)
│   │
│   ├── components/               # UI components
│   │   ├── sidebar.py            # 🗂️ Custom navigation sidebar
│   │   └── submission.py         # 📤 Form submission handling
│   │
│   ├── common_form_sections/     # 🧩 Reusable form components
│   │   ├── __init__.py           # Component registry system
│   │   ├── base.py               # SectionComponent interface
│   │   ├── natural_persons.py    # 👥 Person collection with ID validation
│   │   ├── address.py            # 🏠 Address with country-specific validation (220+ countries)
│   │   ├── phone.py              # 📞 Phone with international dialing codes
│   │   ├── authorised_representative.py  # 👤 Individual person details component
│   │   └── CountryList.csv       # 🌍 Comprehensive country database (220+ countries)
│   │
│   └── forms/                    # 📋 Form engine & specifications
│       ├── engine.py             # ⚙️ Form rendering, validation & serialization engine
│       ├── field_helpers.py      # 🛠️ Field generation utilities
│       └── specs/                # 📊 Entity-specific form definitions
│           ├── __init__.py       # SPECS registry
│           ├── company.py        # Company form specification
│           ├── trust.py          # Trust form (with Masters Office field)
│           ├── partnership.py    # Partnership form
│           ├── burial_society.py # Burial Society form
│           ├── charity_organisation.py  # Charity form
│           ├── church.py         # Church form
│           ├── community_group.py # Community Group form
│           ├── cultural_association.py # Cultural Association form
│           ├── environmental_group.py  # Environmental Group form
│           ├── investment_club.py # Investment Club form
│           ├── savings_club.py   # Savings Club form
│           ├── school.py         # School form
│           ├── social_club.py    # Social Club form
│           ├── sports_club.py    # Sports Club form
│           ├── stokvel.py        # Stokvel form
│           ├── closed_corporation.py # Closed Corporation form
│           └── other.py          # Other entity types form
│
├── assets/                       # Static assets
│   └── logos/                    # Logo files, branding, animations
│       ├── favicon.svg           # 🖼️ Application favicon (consistent across pages)
│       ├── profile.svg           # 👤 User avatar for chat interface
│       └── lottie-jsons/         # 🎬 Animation files for AI Assistance page
│
├── docs/                         # 🆕 Documentation
│   └── architecture_diagram.md   # Mermaid diagrams and architecture overview
│
├── knowledge_set.md              # AI assistant knowledge base
├── project_details.md            # Detailed technical architecture documentation
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

---

## 🆕 **Semantic Specification Architecture**

### **📋 Structured Data Management**

The system now implements a **semantic specification-driven architecture** with structured JSON data sources:

#### **1. Controlled Lists with Code/Label Separation**
```json
{
  "source_of_funds": [
    {"code": "BUSINESS_OPERATING_INCOME", "label": "Business Operating Income", "is_active": true, "sort_order": 1},
    {"code": "COMMISSION", "label": "Commission", "is_active": true, "sort_order": 2}
  ]
}
```
- **UI displays labels** (user-friendly)
- **System stores codes** (data integrity)
- **Version control ready** (structured data)

#### **2. Field Specifications with Validation Rules**
```json
{
  "entity_name": {
    "data_type": "string",
    "required_rule": "always",
    "ui_control": "input",
    "min_length": 1,
    "max_length": 200
  },
  "sa_id_number": {
    "data_type": "id_sa",
    "required_rule": "if_id_type_sa_id",
    "validation": "luhn_check",
    "dependencies": {"id_type": "SA ID Number"}
  }
}
```

#### **3. Role-Based System**
- **Natural Person Roles**: AUTHORISED_REPRESENTATIVE, DIRECTOR, TRUSTEE, PARTNER, etc.
- **Role-Specific Fields**: Each role has defined field requirements
- **Entity Role Rules**: Which roles are required/conditional per entity type

#### **4. Document Requirements**
- **Entity-Level Documents**: Certificate of Incorporation, Trust Deed, etc.
- **Role-Level Documents**: ID documents, proof of address per role
- **Upload Validation**: File format, size, and completeness checking

### **🔧 Enhanced Managers**

#### **Controlled List Manager** ✅ **FULLY INTEGRATED**
- Code/label resolution with fallback handling
- Active item filtering for enable/disable functionality
- Custom sort ordering (e.g., South Africa prioritized)
- **Form integration**: Powers all dropdown fields across entity forms

#### **Field Specification Manager**
- Multi-layer validation (type, format, length, range)
- Cross-field dependency validation
- Special validations (Luhn check, phone format, email)
- Business rule enforcement (entity-specific logic)

#### **Document Requirements Manager**
- Role-based document requirements
- Upload schema generation for dynamic UI
- File validation (format, size, completeness)

### **📊 Data Flow Architecture**

The new architecture follows a clear data flow pattern:

1. **📋 JSON Specifications** → **🔧 Enhanced Managers** → **🎯 Dynamic Form Generation** → **⚡ Multi-layer Validation** → **📤 Structured Submission**

**Benefits:**
- **🔄 Maintainable**: JSON-driven configuration
- **📋 Auditable**: Versioned specifications
- **🎯 Scalable**: Role-based architecture
- **🔧 Flexible**: Dynamic form generation
- **🛡️ Robust**: Multi-layer validation

### **🎯 Integration Achievements**

The enhanced controlled lists system is **fully operational** across all form journeys:

| Component | Integration Status | Enhanced Features |
|-----------|-------------------|-------------------|
| **Entity Selection** | ✅ Complete | Dynamic entity types from JSON |
| **Field Helpers** | ✅ Complete | Source of Funds, Industry, Countries |
| **Natural Persons** | ✅ Complete | Member roles, ID countries |
| **Authorised Rep** | ✅ Complete | Titles, genders, marital status, citizenship |
| **Address Forms** | ✅ Complete | 220+ countries with SA prioritization |
| **Session State** | ✅ Complete | Backwards compatibility maintained |

**Key Improvements:**
- 🎯 **Data Consistency**: All dropdowns use standardized code/label pairs
- 🌍 **Global Ready**: 220+ countries with intelligent sorting
- 🔧 **Maintainable**: JSON-driven configuration eliminates hardcoded lists
- 📊 **Scalable**: Easy addition of new options without code changes

---

## 🎯 **Supported Entity Types**

The system supports **17 entity types** (alphabetical order) with **Authorised Representative** capture for all:

| Entity Type | Min. People | Role Label | Special Requirements |
|-------------|-------------|------------|---------------------|
| Burial Society | 1 | Committee Member | + Authorised Representative |
| Charity Organisation | 1 | Board Member | + Authorised Representative |
| Church | 1 | Leader | + Authorised Representative |
| Closed Corporation | 1 | Member | + Authorised Representative |
| Community Group | 1 | Committee Member | + Authorised Representative |
| Company | 1 | Director | Directors + Beneficial Owners (>5%) + Authorised Representative |
| Cultural Association | 1 | Committee Member | + Authorised Representative |
| Environmental Group | 1 | Committee Member | + Authorised Representative |
| Investment Club | 2 | Member | + Authorised Representative |
| Partnership | 2 | Partner | + Authorised Representative |
| Savings Club | 2 | Member | + Authorised Representative |
| School | 1 | Governing Body Member | + Authorised Representative |
| Social Club | 1 | Committee Member | + Authorised Representative |
| Sports Club | 1 | Committee Member | + Authorised Representative |
| Stokvel | 2 | Member | + Authorised Representative |
| Trust | 1 | Trustee | **Masters Office field required** + Authorised Representative |
| Other | 0 | Person | Catch-all for unlisted entities + Authorised Representative |

### **✨ New: Authorised Representative Section**
Every entity type now includes a comprehensive **Authorised Representative** section capturing:
- Personal details (Title, Name, Gender, DOB, Marital Status)
- Identification (SA ID with Luhn validation, Foreign ID, or Foreign Passport)
- Contact information (Email, Phone, Address)
- Citizenship and Country of Residence

---

## 🧩 **Core Components**

### **1. Controlled Lists System** (`app/controlled_lists.py`)

Centralized management of all predefined options with **exact specifications**:

- **📊 Source of Funds** (26 options): Business Operating Income, Commission, Company Profits, etc.
- **🏭 Industry Classification** (75+ options): Accounting Services, Banking, Healthcare, etc.
- **👤 Member Roles** (11 options): Chairperson, Secretary, Treasurer, Director, etc.
- **🌍 Countries** (220+ options): **Comprehensive global coverage** loaded from CSV with South Africa prioritized
- **🏢 Entity Types** (17 types): All supported entity types in alphabetical order ("Other" always last)
- **👤 Personal Details** (NEW): Title options (7), Gender options (3), Marital Status options (3)

### **🆕 Enhanced Country Support**
- **📁 CSV Integration**: Countries loaded from `app/common_form_sections/CountryList.csv`
- **🇿🇦 South Africa Priority**: Always appears first (after empty option) in dropdowns
- **🌍 Global Coverage**: 220+ countries with proper sorting and validation
- **🔧 Centralized Management**: Single source of truth for all country dropdowns

**Key Functions:**
```python
from app.controlled_lists import (
    get_source_of_funds_options,
    get_industry_options,
    get_member_role_options,
    get_countries,              # NEW: 220+ countries from CSV
    get_entity_types,
    get_title_options,          # NEW: Personal titles
    get_gender_options,         # NEW: Gender options
    get_marital_status_options  # NEW: Marital status options
)
```

### **2. Form Engine** (`app/forms/engine.py`)

**Core Data Structures:**
```python
@dataclass
class Field:
    key: str
    label: str
    kind: str                    # "text", "select", "multiselect", "date", etc.
    required: bool = False
    options: Optional[List[str]] = None

@dataclass  
class Section:
    title: str
    fields: List[Field] = []
    component_id: Optional[str] = None    # Reference to reusable component
    component_args: Dict[str, Any] = {}

@dataclass
class FormSpec:
    name: str
    title: str
    sections: List[Section]
```

**Key Functions:**
- `render_form(spec, namespace)` - Renders complete form UI
- `validate(spec, namespace)` - Validates all fields and components
- `serialize_answers(spec, namespace)` - Exports data for submission

### **3. Reusable Components** (`app/common_form_sections/`)

#### **🆕 Authorised Representative Component** ✅ **REFACTORED - DRY COMPLIANT**
**NEW**: Captures individual person details (not collections) for the entity representative:

```python
# Usage in form specs - Personal details only
Section(
    title="Authorised Representative", 
    component_id="authorised_representative",
    component_args={
        "instance_id": "auth_rep",
        "title": "Authorised Representative"
    }
)

# Separate address section using dedicated AddressComponent
Section(
    title="Authorised Representative Address",
    component_id="address",
    component_args={
        "instance_id": "auth_rep_address",
        "title": "Authorised Representative Address"
    }
)
```

**Features:**
- **✅ DRY Principle**: No longer duplicates address fields - uses dedicated AddressComponent
- Personal details with controlled lists (Title, Gender, Marital Status)
- Multiple ID types with validation (SA ID with Luhn, Foreign ID, Foreign Passport)
- **🔧 Single Responsibility**: Focuses solely on personal details, identification, and contact info
- Email validation and citizenship/residence country selection
- Age validation (must be 18+) and comprehensive error handling
- **🏗️ Architectural Consistency**: Maintains clean separation of concerns

#### **Natural Persons Component**
Handles collections of people with comprehensive validation:

```python
# Usage in form specs
Section(
    title="Directors",
    component_id="natural_persons",
    component_args={
        "instance_id": "directors",
        "title": "Directors",
        "role_label": "Director", 
        "min_count": 1,
        "show_uploads": True,
        "show_member_roles": True,  # Enable role selection
        "allowed_id_types": ["SA ID Number", "Foreign Passport Number"]
    }
)
```

**Features:**
- Multiple ID types: SA ID (Luhn validated), Foreign ID, Foreign Passport
- Country-specific validation rules
- Document uploads (ID/Passport, Proof of Address)
- Member role selection from controlled list
- Instance isolation for multiple collections on same page

#### **Address Component** 
Physical address collection with **enhanced international support**:

**Features:**
- Two-column layout (Unit/Street Number + Complex/Street Name)
- **🇿🇦 SA-specific**: 4-digit postal codes, province dropdown (9 provinces)
- **🌍 International**: Flexible postal code format, free-text province/state/region  
- **🆕 220+ Countries**: Full global coverage with South Africa prioritized
- **🔧 Smart Validation**: Dynamic field types based on selected country
- Required fields: Street Number, Street Name, Suburb, City

#### **Phone Component**
Phone number collection with international support:

**Features:**
- Split layout: Dialing code + phone number
- SA validation: 9 digits, no leading zero
- International: 6-15 digits allowed

### **4. State Management System** (`app/utils.py`)

**🆕 Enhanced with Session Cleanup:**
- **🔧 Automatic Legacy Cleanup**: Removes problematic session values (e.g., "Other" in province fields)
- **🛡️ Error Prevention**: Prevents "not in iterable" errors from outdated state
- **🔄 Continuous Protection**: Cleanup runs on every initialization

**Namespace & Instance Scoping:**
```python
# Global keys
"entity_type" → "Company"
"entity_user_id" → "COMP001"

# Namespaced keys (entity isolation)
"company__legal_name" → "Acme Corp Ltd"
"trust__masters_office" → "Cape Town"

# Instance keys (component isolation)
"company__directors__count" → 2
"company__directors__full_0" → "John Smith"
"company__ubos__count" → 1
"company__ubos__full_0" → "Jane Doe"
```

**Key Functions:**
```python
# Namespace management
def current_namespace() -> str
def ns_key(ns: str, key: str) -> str
def inst_key(ns: str, instance_id: str, key: str) -> str

# Persistent widgets
def persist_text_input(label: str, state_key: str, **kwargs)
def persist_selectbox(label: str, state_key: str, **kwargs)
def persist_multiselect(label: str, state_key: str, **kwargs)
```

---

---

## 🎨 **Enhanced User Interface**

### **🆕 Modern Visual Design**
- **🌈 Gradient Text Styling**: Beautiful gradient titles on Introduction, AI Assistance, and Declaration pages
- **🎬 Lottie Animations**: Random animations on AI Assistance page for engaging user experience
- **👤 Custom Avatars**: Profile SVG for user chat messages, favicon SVG for assistant messages
- **🖼️ Consistent Branding**: Unified favicon across all pages (favicon.svg)
- **🎯 Light Theme**: Clean, professional light mode as default theme

### **🤖 AI Assistance Enhancements**
- **📚 Updated Knowledge Base**: Relevant Entity Onboarding information replacing outdated content
- **🎨 Gradient Title**: Matches main page styling with "Entity Onboarding Assistant"
- **🎬 Random Lottie**: Different animation on each page load from `assets/logos/lottie-jsons/`
- **👤 User Avatar**: Custom profile.svg for user messages in chat interface
- **🤖 Assistant Avatar**: Favicon.svg for consistent assistant branding

---

## 🔧 **Development Guide**

### **Adding a New Entity Type**

1. **Update Controlled Lists**
```python
# app/controlled_lists.py
ENTITY_TYPES = [
    # ... existing types ...
    "New Entity Type",  # Add in alphabetical order
    "Other"  # Always last
]
```

2. **Create Form Specification**
```python
# app/forms/specs/new_entity_type.py
from app.forms.engine import FormSpec, Section
from app.forms.field_helpers import create_entity_details_fields

SPEC = FormSpec(
    name="new_entity_type",
    title="New Entity Type",
    sections=[
        Section(
            title="Entity Details",
            fields=create_entity_details_fields()
        ),
        Section(  # NEW: Required for all entity types
            title="Authorised Representative",
            component_id="authorised_representative",
            component_args={
                "instance_id": "auth_rep",
                "title": "Authorised Representative"
            }
        ),
        Section(
            title="Physical Address",
            component_id="address",
            component_args={
                "instance_id": "physical_address",
                "title": "Physical Address"
            }
        ),
        Section(
            title="People",
            component_id="natural_persons",
            component_args={
                "instance_id": "people",
                "title": "Related People",
                "role_label": "Person",
                "min_count": 1,
                "show_uploads": True,
                "show_member_roles": True
            }
        ),
    ]
)
```

3. **Register in Specs Registry**
```python
# app/forms/specs/__init__.py
from . import new_entity_type

SPECS = {
    # ... existing specs ...
    "new_entity_type": new_entity_type.SPEC,
}
```

### **Creating a New Reusable Component**

1. **Implement Component Interface**
```python
# app/common_form_sections/my_component.py
from app.common_form_sections.base import SectionComponent
from app.common_form_sections import register_component

class MyComponent(SectionComponent):
    def render(self, *, ns: str, instance_id: str, **config) -> None:
        # Render UI using Streamlit widgets
        pass
        
    def validate(self, *, ns: str, instance_id: str, **config) -> List[str]:
        # Return list of error messages
        return []
        
    def serialize(self, *, ns: str, instance_id: str, **config) -> Tuple[Dict[str, Any], List[Any]]:
        # Return (data_dict, uploads_list)
        return {}, []

# Register component
register_component("my_component", MyComponent())
```

2. **Use in Form Specifications**
```python
Section(
    title="My Section",
    component_id="my_component",
    component_args={
        "instance_id": "my_instance",
        "custom_config": "value"
    }
)
```

### **Adding Custom Validation Rules**

Extend the validation function in `app/forms/engine.py`:

```python
def _add_conditional_validation_rules(spec: FormSpec, ns: str, errs: List[str]):
    # Add your custom validation logic
    if spec.name == "my_entity":
        field_value = st.session_state.get(ns_key(ns, "my_field"), "")
        if not field_value:
            errs.append("[Section] Custom validation error message.")
```

### **Extending Controlled Lists**

```python
# app/controlled_lists.py

# Add new options to existing lists (maintain alphabetical order)
SOURCE_OF_FUNDS_OPTIONS.extend([
    "New Funding Source",
    "Another Option"
])

# Or create entirely new controlled lists
NEW_CATEGORY_OPTIONS = [
    "",
    "Option 1",
    "Option 2"
]

def get_new_category_options():
    return NEW_CATEGORY_OPTIONS.copy()
```

### **🆕 Adding New Countries**

To add countries to the comprehensive list:

```python
# Update app/common_form_sections/CountryList.csv
# Add new row with Country Name and ISO code:
New Country Name,XX

# The system automatically loads and sorts countries
# South Africa remains prioritized at the top
```

---

## 📊 **Data Flow**

```
User Input → Session State (namespaced) → Component Validation → Form Submission
     ↓              ↓                         ↓                      ↓
UI Widgets    ns_key/inst_key           Error Messages         PDF + Email
```

### **Submission Process**

1. **Validation**: All fields and components validated
2. **Serialization**: Data structured for export
3. **Dual Format Generation**: Both PDF summary and CSV data file created
4. **Email Submission**: PDF + CSV + user attachments sent automatically
5. **User Feedback**: Success confirmation with all attachment details

### **Key Data Structures**

**Field Types:**
- `text` - Text input
- `textarea` - Multi-line text
- `number` - Numeric input
- `select` - Single selection dropdown
- `multiselect` - Multiple selection
- `date` - Date picker
- `checkbox` - Boolean toggle
- `file` - File upload

**Component Arguments:**
- `instance_id` - Unique identifier for component instance
- `title` - Section heading
- `role_label` - Person type label (e.g., "Director", "Member")
- `min_count` - Minimum required entries
- `show_uploads` - Enable/disable file uploads
- `show_member_roles` - Enable/disable role selection
- `allowed_id_types` - Restrict ID type options

---

## 🚦 **Validation Rules**

### **Entity Details**
- **Entity Name**: Required for all entities
- **Registration Number**: 3-50 characters when provided (alphanumeric)
- **Country of Registration**: Required when Registration Number provided (220+ options)
- **Source of Funds**: Required multiselect (26 options from controlled list)
- **Industry**: Required selection (75+ options from controlled list)
- **Trust Masters Office**: Required for Trust entities only, max 200 characters (free text)

### **🆕 Authorised Representative Validation**
- **Required**: Title, First Name, Last Name, Gender, DOB, Marital Status, ID Type, Email, Citizenship, Country of Residence
- **ID Type Validation**: SA ID (13 digits, Luhn check), Foreign ID (required number), Foreign Passport (number + country + future expiry)
- **Age Validation**: Must be 18+ years old at time of submission
- **Email Validation**: Proper email format validation
- **Phone Validation**: Uses PhoneComponent rules (SA: 9 digits no leading 0, International: 6-15 digits)
- **Address Validation**: Uses AddressComponent rules with 220+ country support

### **Address Validation** 
- **Required**: Street Number, Street Name, Suburb, City
- **🇿🇦 South Africa**: Province dropdown required (9 options), 4-digit postal code
- **🌍 International**: Free-text province/state/region, flexible postal code (≤10 characters)
- **🆕 Country Selection**: 220+ countries with South Africa prioritized

### **Phone Validation**
- **Required**: Dialing code and number
- **South Africa (+27)**: 9 digits, no leading zero
- **International**: 6-15 digits

### **Natural Persons**
- **Required**: Full Name, ID Type
- **SA ID**: 13 digits, Luhn algorithm validation
- **Foreign ID**: Number required
- **Foreign Passport**: Number, country, future expiry date required
- **Member Role**: Required when `show_member_roles=True`

---

## 🛠️ **Technical Notes**

### **Session State Management**
- **Namespace Isolation**: Each entity type maintains separate state
- **Instance Scoping**: Multiple component instances don't interfere  
- **Persistence**: State survives page navigation
- **Memory Efficiency**: Only active namespace data loaded
- **🆕 Automatic Cleanup**: Legacy session values automatically removed to prevent errors
- **🛡️ Error Prevention**: Proactive cleanup of problematic values (e.g., "Other" in province fields)

### **Performance Considerations**
- **Lazy Loading**: Components loaded on demand
- **Efficient Validation**: Only validates visible/relevant fields
- **Memory Management**: Old namespaces can be cleared
- **File Handling**: Uploads processed incrementally

### **Security Features**
- **Input Validation**: All inputs validated before processing
- **File Type Restrictions**: Only specific file types allowed for uploads
- **Email Security**: SMTP credentials stored in secrets.toml
- **XSS Prevention**: User inputs properly escaped

### **Accessibility**
- **Screen Reader Support**: Proper ARIA labels
- **Keyboard Navigation**: Full keyboard accessibility
- **Color Contrast**: WCAG compliant color schemes
- **Error Messages**: Clear, descriptive error text

---

## 📧 **Email & PDF Integration**

### **🆕 Enhanced Email System with Dual Format Export**
Configure SMTP settings in `.streamlit/secrets.toml`:
```toml
[email_credentials]
email_address = "your-smtp-email@domain.com"
app_password = "your-smtp-app-password"
recipient_address = "submissions@your-domain.com"
```

**Email Improvements:**
- **📧 Context-Aware Subject**: "New Entity Onboarding Submission: {EntityName} ({EntityType})"
- **📋 Comprehensive Body**: Entity details, submission summary, included documents list
- **📊 Dual Format Attachments**: Both PDF summary and CSV data file automatically included
- **🏢 Professional Signature**: "Entity Onboarding System" and "Satrix Asset Management"
- **🔧 Better Error Handling**: Specific troubleshooting guidance for failures
- **✅ Enhanced Success Messages**: Show recipient, PDF filename, CSV filename, and attachment count

### **Dual Format Output**

#### **PDF Generation**
- **Library**: ReportLab
- **Purpose**: Human-readable formatted summary
- **Content**: Complete form responses + metadata + authorised representative details
- **🆕 File Naming**: `Entity_Onboarding_{EntityName}_{Timestamp}.pdf`

#### **🆕 CSV Data Export**
- **Library**: Python CSV module
- **Purpose**: Machine-readable structured data for processing systems
- **Format**: Long format with Section/Record#/Field/Value columns
- **Content**: All form data flattened into structured rows
- **🆕 File Naming**: `Entity_Onboarding_{EntityName}_{Timestamp}.csv`

**CSV Format Example:**
```csv
Section,Record #,Field,Value
Entity Details,1,Entity Name,Acme Corp Ltd
Entity Details,1,Registration Number,REG123456
Directors,1,Full Name,John Smith
Directors,1,SA ID,1234567890123
Directors,2,Full Name,Jane Doe
Directors,2,Foreign ID,ABC123456
```

**Benefits:**
- **🤖 Automation-Ready**: CSV format perfect for automated processing systems
- **📊 Data Analysis**: Easy import into spreadsheets, databases, and analytics tools
- **🔧 Integration-Friendly**: Standard format for third-party system integration
- **📋 Audit Trail**: Complete structured record of all submitted data
- **🏗️ Low Risk**: Isolated CSV logic doesn't affect existing PDF generation

---

## 🐛 **Troubleshooting**

### **Common Issues**

**Import Errors**
```bash
# Ensure all dependencies are installed
pip install -r requirements.txt

# Check Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

**State Persistence Issues**
```python
# Clear session state if needed
if st.button("Clear Session"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()
```

**Email Sending Failures**
- Verify SMTP credentials in `.streamlit/secrets.toml`
- Check app password settings for Gmail/Outlook
- Ensure recipient email address is valid
- Check firewall/network restrictions

**Validation Errors**
- Review field requirements in form specifications
- Check controlled list options are current (26 Source of Funds, 75+ Industries, etc.)
- Verify component configuration parameters
- Test with minimal valid data first
- **🆕 Country/Province Issues**: Clear session state if "Other is not in iterable" errors occur

**🆕 Session State Issues**
```python
# Clear problematic session state manually if needed
if st.button("Clear Session"):
    for key in list(st.session_state.keys()):
        if "__province" in key and st.session_state[key] == "Other":
            del st.session_state[key]
    st.rerun()
```

### **Debug Mode**
```python
# Enable debug information
import streamlit as st
st.write("Debug Info:", st.session_state)
```

---

## 🚀 **Deployment**

### **Streamlit Cloud**
1. Push code to GitHub repository
2. Connect to Streamlit Cloud
3. Configure secrets via Streamlit Cloud dashboard
4. Deploy with `streamlit run app/main.py`

### **Docker Deployment**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app/main.py"]
```

### **Environment Variables**
```bash
# For production deployment
export STREAMLIT_SERVER_PORT=8501
export STREAMLIT_SERVER_HEADLESS=true
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
```

---

## 📈 **Future Enhancements**

### **Planned Features**
- [ ] **Database Integration**: PostgreSQL/MongoDB support for data persistence
- [ ] **User Authentication**: Login system with role-based access
- [ ] **Audit Trail**: Complete submission history and modifications
- [ ] **Advanced Analytics**: Dashboard for submission statistics
- [ ] **API Endpoints**: REST API for third-party integrations
- [ ] **Multi-language Support**: Internationalization framework
- [ ] **Advanced Validation**: Integration with external validation services
- [ ] **Workflow Management**: Approval processes and status tracking
- [ ] **🆕 Enhanced Document Management**: Document categorization, version control
- [ ] **🆕 Real-time Collaboration**: Multiple users editing same entity
- [ ] **🆕 Advanced Country Support**: Currency, timezone, and regulatory data
- [ ] **🆕 Mobile Optimization**: Enhanced mobile experience for form completion
- [ ] **📊 CSV Data Enhancements**: Custom column mappings, multiple export formats
- [ ] **🔌 API Data Export**: REST endpoints for automated data retrieval

### **Scalability Considerations**
- **Microservices**: Split into smaller, focused services
- **Caching**: Redis for session and form data caching
- **Load Balancing**: Handle multiple concurrent users
- **File Storage**: Cloud storage for uploaded documents
- **Monitoring**: Application performance monitoring

---

## 📝 **Contributing**

### **Development Standards**
- **Code Style**: Follow PEP 8 Python style guide
- **Documentation**: Docstrings for all functions and classes
- **Testing**: Unit tests for components and validation logic
- **Version Control**: Feature branches with descriptive commit messages

### **Pull Request Process**
1. Create feature branch from `main`
2. Implement changes with tests
3. Update documentation as needed
4. Submit pull request with clear description
5. Ensure all checks pass before merging

---

## 📄 **License & Support**

- **License**: [Specify license type]
- **Documentation**: See `project_details.md` for technical architecture details
- **Support**: [Contact information or issue tracker]
- **Updates**: Check repository for latest features and bug fixes

---

**Built with ❤️ using Streamlit and Python**
