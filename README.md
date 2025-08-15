# Entity Onboarding System

A comprehensive **Streamlit-based entity onboarding application** that supports 17 different entity types with dynamic form generation, reusable components, and intelligent validation. Built using a **component-based architecture** for maximum modularity and maintainability.

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
│   ├── controlled_lists.py       # 📋 Centralized predefined options/lists
│   ├── utils.py                  # 🔧 Utilities, state management, persistence helpers
│   ├── styling.py                # 🎨 CSS styling definitions
│   ├── email_sender.py           # 📧 Email submission functionality
│   ├── pdf_generator.py          # 📄 PDF generation utilities
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
│   │   ├── address.py            # 🏠 Address with country-specific validation
│   │   └── phone.py              # 📞 Phone with international dialing codes
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
│   └── logos/                    # Logo files and branding
│
├── knowledge_set.md              # AI assistant knowledge base
├── project_details.md            # Detailed technical architecture documentation
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

---

## 🎯 **Supported Entity Types**

The system supports **17 entity types** (alphabetical order):

| Entity Type | Min. People | Role Label | Special Requirements |
|-------------|-------------|------------|---------------------|
| Burial Society | 1 | Committee Member | - |
| Charity Organisation | 1 | Board Member | - |
| Church | 1 | Leader | - |
| Closed Corporation | 1 | Member | - |
| Community Group | 1 | Committee Member | - |
| Company | 1 | Director | Directors + Beneficial Owners (>5%) |
| Cultural Association | 1 | Committee Member | - |
| Environmental Group | 1 | Committee Member | - |
| Investment Club | 2 | Member | - |
| Partnership | 2 | Partner | - |
| Savings Club | 2 | Member | - |
| School | 1 | Governing Body Member | - |
| Social Club | 1 | Committee Member | - |
| Sports Club | 1 | Committee Member | - |
| Stokvel | 2 | Member | - |
| Trust | 1 | Trustee | **Masters Office field required** |
| Other | 0 | Person | Catch-all for unlisted entities |

---

## 🧩 **Core Components**

### **1. Controlled Lists System** (`app/controlled_lists.py`)

Centralized management of all predefined options:

- **📊 Source of Funds** (28 options): Business Operating Income, Commission, Company Profits, etc.
- **🏭 Industry Classification** (41 options): Accounting Services, Banking, Healthcare, etc.
- **👤 Member Roles** (12 options): Chairperson, Secretary, Treasurer, Director, etc.
- **🌍 Countries** (11 options): South Africa, UK, US, Australia, etc.
- **🏢 Entity Types** (17 types): All supported entity types

**Key Functions:**
```python
from app.controlled_lists import (
    get_source_of_funds_options,
    get_industry_options,
    get_member_role_options,
    get_countries,
    get_entity_types
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
Physical address collection with country-specific validation:

**Features:**
- Two-column layout (Unit/Street Number + Complex/Street Name)
- SA-specific: 4-digit postal codes, province selection
- International: Flexible postal code format
- Required fields: Street Number, Street Name, Suburb, City

#### **Phone Component**
Phone number collection with international support:

**Features:**
- Split layout: Dialing code + phone number
- SA validation: 9 digits, no leading zero
- International: 6-15 digits allowed

### **4. State Management System** (`app/utils.py`)

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

# Add new options to existing lists
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
3. **PDF Generation**: Summary document created
4. **Email Submission**: PDF + attachments sent
5. **User Download**: PDF available for download

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
- **Registration Number**: 3-50 characters when provided
- **Country of Registration**: Required when Registration Number provided
- **Source of Funds**: Required multiselect
- **Industry**: Required selection
- **Trust Masters Office**: Required for Trust entities, max 200 characters

### **Address Validation**
- **Required**: Street Number, Street Name, Suburb, City
- **South Africa**: Province required, 4-digit postal code
- **International**: Flexible postal code (≤10 characters)

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

### **Email Configuration**
Configure SMTP settings in `.streamlit/secrets.toml`:
```toml
[email_credentials]
email_address = "your-smtp-email@domain.com"
app_password = "your-smtp-app-password"
recipient_address = "submissions@your-domain.com"
```

### **PDF Generation**
- **Library**: ReportLab
- **Content**: Complete form responses + metadata
- **File Naming**: `Entity_Onboarding_{EntityName}_{Timestamp}.pdf`
- **Attachments**: All uploaded documents included in email

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
- Check controlled list options are current
- Verify component configuration parameters
- Test with minimal valid data first

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
