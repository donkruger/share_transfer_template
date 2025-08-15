# Entity Onboarding System - Technical Architecture Documentation

This document serves as the **comprehensive technical architecture documentation** for the Entity Onboarding System. The system has been fully implemented using a **component-based architecture** that provides maximum modularity, reusability, and maintainability.

## 🏗️ **Architecture Overview**

The Entity Onboarding System implements a **3-page application** with:

* **Dynamic form generation** based on entity type selection
* **Reusable, validated form components** with instance-scoped state management
* **Component interface + registry system** for consistent render → validate → serialize patterns
* **Multiple component instances** on the same page (e.g., "Directors", "Beneficial Owners") with **instance_id** scoping
* **Lightweight form engine** that orchestrates component interactions
* **Preserved session state persistence** using existing `persist_*` helpers

---

## 📁 **System Architecture**

```
EasyETFs_Data_App copy 3/
├── .streamlit/
│   ├── config.toml
│   ├── pages.toml                 # ✅ 3 pages configured
│   └── secrets.toml               # Email/submission configuration
├── app/
│   ├── common_form_sections/      # 🆕 REUSABLE COMPONENTS
│   │   ├── __init__.py            # Component registry system
│   │   ├── base.py                # SectionComponent interface
│   │   ├── natural_persons.py     # Person collection component
│   │   ├── address.py             # Address with country validation
│   │   └── phone.py               # Phone with dialing code validation
│   ├── forms/                     # 🆕 FORM ENGINE & SPECS
│   │   ├── __init__.py
│   │   ├── engine.py              # render_form/serialize/validate
│   │   └── specs/                 # Entity-specific form definitions
│   │       ├── __init__.py        # SPECS registry
│   │       ├── company.py         # Company form specification
│   │       ├── trust.py           # Trust form specification
│   │       ├── partnership.py     # Partnership form specification
│   │       ├── closed_corporation.py # CC form specification
│   │       └── other.py           # Other entity form specification
│   ├── components/                # 🔄 EXISTING COMPONENTS
│   │   ├── sidebar.py             # Updated: 3-page navigation
│   │   └── submission.py          # Submission handling
│   ├── pages/                     # 🔄 PAGE STRUCTURE
│   │   ├── 1_AI_Assistance.py     # AI assistant (unchanged)
│   │   ├── 3_Declaration_and_Submit.py # Final submission page
│   │   └── _archive/              # 📦 ARCHIVED: Original pages 2-7
│   │       ├── 2_Business_Information.py
│   │       ├── 3_Authorised_Persons.py
│   │       ├── 4_Financial_Matters.py
│   │       ├── 5_Director_Information.py
│   │       ├── 6_Beneficial_Owners.py
│   │       └── 7_Strategic_Considerations.py
│   ├── main.py                    # 🔄 Introduction: Dynamic entity forms
│   ├── utils.py                   # 🔄 Enhanced: namespace + instance utilities
│   ├── email_sender.py            # Email submission
│   ├── pdf_generator.py           # PDF generation
│   └── styling.py                 # UI styling
├── assets/                        # Static assets
│   └── logos/
└── requirements.txt               # Dependencies
```

### 🎯 **Key Architectural Principles**

1. **Component Reusability**: Form sections (address, phone, natural persons) are implemented once and reused across all entity types
2. **Instance Isolation**: Multiple instances of the same component can exist on one page without state collisions using `instance_id` scoping
3. **Namespace Separation**: Each entity type maintains isolated session state, allowing users to switch between entity types without data loss
4. **Declarative Configuration**: Entity forms are defined declaratively in specs, mixing simple fields with reusable components
5. **Consistent Interface**: All components implement the same interface (render/validate/serialize) ensuring predictable behavior

---

## 🚀 **Application Flow**

### **3-Page Navigation Structure**

The application implements a streamlined **3-page workflow**:

1. **📋 Introduction (main.py)**: Entity type selection and dynamic form rendering
2. **🤖 AI Assistance**: Context-aware help system
3. **📝 Declaration & Submit**: Final validation and submission

#### **Page Configuration** (`.streamlit/pages.toml`)
```toml
[[pages]]
path = "app/main.py"
name = "Introduction"
icon = "🏠"

[[pages]]
path = "app/pages/1_AI_Assistance.py"
name = "AI Assistance"
icon = "🤖"

[[pages]]
path = "app/pages/3_Declaration_and_Submit.py"
name = "Declaration & Submit"
icon = "📝"
```

#### **Navigation Implementation** (`app/components/sidebar.py`)
```python
st.page_link('main.py', label='Introduction', icon='🏠')
st.page_link('pages/1_AI_Assistance.py', label='AI Assistance', icon='🤖')
st.page_link('pages/3_Declaration_and_Submit.py', label='Declaration & Submit', icon='📝')
```

#### **Legacy Page Archive**
Original pages 2-7 have been preserved in `app/pages/_archive/` for reference and potential future use.

---

## 🔧 **Core Utilities & State Management**

### **Namespace & Instance Key System**

The system implements a sophisticated state management approach with two levels of scoping:

#### **Implementation** (`app/utils.py`)

```python
# Entity Types Configuration
ENTITY_TYPES = ["Company", "Trust", "Partnership", "Closed Corporation", "Other"]

# Namespace Management
def sanitize_ns(label: str) -> str:
    """Convert entity type to valid namespace identifier"""
    return re.sub(r'[^a-z0-9_]', '', label.strip().lower().replace(' ', '_'))

def current_namespace() -> str:
    """Get current entity type namespace from session state"""
    return sanitize_ns(st.session_state.get("entity_type", ENTITY_TYPES[0]))

# Key Generation Functions
def ns_key(ns: str, key: str) -> str:
    """Create entity-namespaced session key: 'company__field_name'"""
    return f"{ns}__{key}"

def inst_key(ns: str, instance_id: str, key: str) -> str:
    """Create instance-scoped session key: 'company__directors__count'"""
    return ns_key(ns, f"{instance_id}__{key}")

# Session State Initialization
def initialize_state():
    """Initialize all required session state variables"""
    if 'state_initialized' not in st.session_state:
        defaults = {
            # Entity Onboarding Core
            "messages": [],
            "accept": False,
            "entity_type": ENTITY_TYPES[0],
            "entity_user_id": "",
            "entity_display_name": "",
            "s1_name": "", "s1_desig": "",
            "s2_name": "", "s2_desig": "",
            # System Configuration
            "favicon_path": str(favicon_path),
            # Legacy DDQ fields (preserved for compatibility)
            # ... additional fields ...
        }
        for key, value in defaults.items():
            st.session_state.setdefault(key, value)
        st.session_state.state_initialized = True
```

#### **State Management Hierarchy**

1. **Global Keys**: `"entity_type"`, `"entity_user_id"`, `"accept"`
2. **Namespace Keys**: `ns_key("company", "legal_name")` → `"company__legal_name"`
3. **Instance Keys**: `inst_key("company", "directors", "count")` → `"company__directors__count"`

#### **Benefits**

- **Entity Isolation**: Users can switch between Company/Trust/etc. without losing data
- **Component Reuse**: Same component (e.g., natural_persons) used multiple times on one page
- **State Persistence**: Session state preserved across page navigation
- **No Collisions**: Unique keys prevent data overwrites

---

## 🧩 **Component System Architecture**

### **Component Interface** (`app/common_form_sections/base.py`)

```python
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple

class SectionComponent(ABC):
    """Abstract base class for reusable form sections."""

    @abstractmethod
    def render(self, *, ns: str, instance_id: str, **config) -> None:
        """
        Render the component UI using Streamlit widgets.
        
        Args:
            ns: Entity namespace (e.g., 'company', 'trust')
            instance_id: Component instance identifier (e.g., 'directors', 'ubos')
            **config: Component-specific configuration options
        """
        raise NotImplementedError

    @abstractmethod
    def validate(self, *, ns: str, instance_id: str, **config) -> List[str]:
        """
        Validate component data and return error messages.
        
        Returns:
            List of human-readable error strings (empty if valid)
        """
        raise NotImplementedError

    @abstractmethod
    def serialize(self, *, ns: str, instance_id: str, **config) -> Tuple[Dict[str, Any], List[Any]]:
        """
        Serialize component data for submission.
        
        Returns:
            Tuple of (payload_dict, uploads_list)
            - payload_dict: JSON-serializable data summary
            - uploads_list: List of UploadedFile objects for email attachment
        """
        raise NotImplementedError
```

### **Component Registry** (`app/common_form_sections/__init__.py`)

```python
from typing import Dict
from app.common_form_sections.base import SectionComponent

# Global component registry
_REGISTRY: Dict[str, SectionComponent] = {}

def register_component(name: str, component: SectionComponent):
    """Register a reusable section under a stable name."""
    _REGISTRY[name] = component

def get_component(name: str) -> SectionComponent | None:
    """Retrieve a registered component by name."""
    return _REGISTRY.get(name)

# Auto-register components on import
from . import natural_persons  # Auto-registers "natural_persons"
from . import address          # Auto-registers "address"  
from . import phone           # Auto-registers "phone"
```

### **Component Registration Pattern**

Each component self-registers during import:

```python
# At end of component file (e.g., natural_persons.py)
register_component("natural_persons", NaturalPersonsComponent())
```

---

## 👥 **Implemented Components**

### **Natural Persons Component** (`app/common_form_sections/natural_persons.py`)

The most complex component, handling collections of people with various identification types and validation rules.

```python
from __future__ import annotations
import datetime, re
from typing import Any, Dict, List, Tuple
import streamlit as st

from app.common_form_sections.base import SectionComponent
from app.common_form_sections import register_component
from app.utils import inst_key
from app.utils import (
    persist_number_input, persist_text_input, persist_selectbox,
    persist_date_input, persist_file_uploader
)

COUNTRIES = ["", "South Africa", "United Kingdom", "United States"]

def _digits_only(s: str) -> str:
    return re.sub(r"\D", "", s or "")

def _luhn_ok(n: str) -> bool:
    n = _digits_only(n)
    total, alt = 0, False
    for d in n[::-1]:
        d = int(d)
        if alt:
            d *= 2
            if d > 9: d -= 9
        total += d
        alt = not alt
    return total % 10 == 0

def _valid_sa_id(n: str) -> bool:
    n = _digits_only(n)
    return len(n) == 13 and _luhn_ok(n)

def _is_future_date(d: datetime.date | None) -> bool:
    return bool(d and d > datetime.date.today())

class NaturalPersonsComponent(SectionComponent):
    """
    Reusable section for capturing a list of natural persons.
    Config (kwargs):
      - title: str = "Related Natural Persons"
      - role_label: str = "Person"    (used in UI headings)
      - min_count: int = 0            (enforce minimum count)
      - show_uploads: bool = True     (toggle ID/PoA uploads)
      - allowed_id_types: list[str] = ["SA ID Number", "Foreign ID Number", "Foreign Passport Number"]
    """

    def render(self, *, ns: str, instance_id: str, **config) -> None:
        title = config.get("title", "Related Natural Persons")
        role_label = config.get("role_label", "Person")
        allowed_id_types = config.get("allowed_id_types",
            ["SA ID Number", "Foreign ID Number", "Foreign Passport Number"])

        st.subheader(title)
        count_key = inst_key(ns, instance_id, "count")
        n = persist_number_input(f"Number of {role_label.lower()}s", count_key, min_value=0, step=1)

        for i in range(st.session_state.get(count_key, 0)):
            with st.expander(f"{role_label} #{i+1}", expanded=False):
                persist_text_input("Full Name & Surname", inst_key(ns, instance_id, f"full_{i}"))

                id_type = persist_selectbox("Identification Type",
                    inst_key(ns, instance_id, f"id_type_{i}"),
                    options=[""] + allowed_id_types)

                if id_type == "SA ID Number":
                    persist_text_input("SA ID Number", inst_key(ns, instance_id, f"sa_id_{i}"),
                                       help="13 digits; Luhn check applies.")
                elif id_type == "Foreign ID Number":
                    persist_text_input("Foreign ID Number", inst_key(ns, instance_id, f"foreign_id_{i}"))
                elif id_type == "Foreign Passport Number":
                    persist_text_input("Passport Number", inst_key(ns, instance_id, f"passport_no_{i}"))
                    persist_selectbox("Passport Issue Country",
                        inst_key(ns, instance_id, f"passport_country_{i}"),
                        options=COUNTRIES)
                    persist_date_input("Passport Expiry (YYYY/MM/DD)",
                        inst_key(ns, instance_id, f"passport_expiry_{i}"),
                        min_value=datetime.date.today() + datetime.timedelta(days=1))

                persist_text_input("Email", inst_key(ns, instance_id, f"email_{i}"))
                persist_text_input("Telephone", inst_key(ns, instance_id, f"tel_{i}"))

                if config.get("show_uploads", True):
                    persist_file_uploader("ID / Passport Document",
                        inst_key(ns, instance_id, f"id_doc_{i}"))
                    persist_file_uploader("Proof of Address",
                        inst_key(ns, instance_id, f"poa_doc_{i}"))

    def validate(self, *, ns: str, instance_id: str, **config) -> List[str]:
        errs: List[str] = []
        role_label = config.get("role_label", "Person")
        min_count = int(config.get("min_count", 0))
        allowed_id_types = config.get("allowed_id_types",
            ["SA ID Number", "Foreign ID Number", "Foreign Passport Number"])

        n = st.session_state.get(inst_key(ns, instance_id, "count"), 0)
        if n < min_count:
            errs.append(f"[{role_label}s] At least {min_count} entr{'y' if min_count==1 else 'ies'} required.")

        for i in range(n):
            prefix = f"[{role_label} #{i+1}]"
            full = (st.session_state.get(inst_key(ns, instance_id, f"full_{i}")) or "").strip()
            if not full:
                errs.append(f"{prefix} Full Name is required.")

            idt = st.session_state.get(inst_key(ns, instance_id, f"id_type_{i}"), "")
            if idt not in [""] + allowed_id_types:
                errs.append(f"{prefix} Invalid ID Type.")
            if not idt:
                errs.append(f"{prefix} Identification Type is required.")
            if idt == "SA ID Number":
                val = st.session_state.get(inst_key(ns, instance_id, f"sa_id_{i}"), "")
                if not _valid_sa_id(val):
                    errs.append(f"{prefix} SA ID Number is invalid.")
            elif idt == "Foreign ID Number":
                if not (st.session_state.get(inst_key(ns, instance_id, f"foreign_id_{i}")) or "").strip():
                    errs.append(f"{prefix} Foreign ID Number is required.")
            elif idt == "Foreign Passport Number":
                if not (st.session_state.get(inst_key(ns, instance_id, f"passport_no_{i}")) or "").strip():
                    errs.append(f"{prefix} Passport Number is required.")
                if not (st.session_state.get(inst_key(ns, instance_id, f"passport_country_{i}")) or "").strip():
                    errs.append(f"{prefix} Passport Issue Country is required.")
                exp = st.session_state.get(inst_key(ns, instance_id, f"passport_expiry_{i}"))
                if not (exp and _is_future_date(exp)):
                    errs.append(f"{prefix} Passport Expiry must be a future date.")

        return errs

    def serialize(self, *, ns: str, instance_id: str, **config) -> Tuple[Dict[str, Any], List[Any]]:
        people: List[Dict[str, Any]] = []
        uploads: List[Any] = []
        n = st.session_state.get(inst_key(ns, instance_id, "count"), 0)

        for i in range(n):
            exp = st.session_state.get(inst_key(ns, instance_id, f"passport_expiry_{i}"))
            people.append({
                "Full Name": st.session_state.get(inst_key(ns, instance_id, f"full_{i}"), ""),
                "ID Type": st.session_state.get(inst_key(ns, instance_id, f"id_type_{i}"), ""),
                "SA ID": st.session_state.get(inst_key(ns, instance_id, f"sa_id_{i}"), ""),
                "Foreign ID": st.session_state.get(inst_key(ns, instance_id, f"foreign_id_{i}"), ""),
                "Passport No": st.session_state.get(inst_key(ns, instance_id, f"passport_no_{i}"), ""),
                "Passport Country": st.session_state.get(inst_key(ns, instance_id, f"passport_country_{i}"), ""),
                "Passport Expiry": exp.strftime("%Y/%m/%d") if exp else "",
                "Email": st.session_state.get(inst_key(ns, instance_id, f"email_{i}"), ""),
                "Telephone": st.session_state.get(inst_key(ns, instance_id, f"tel_{i}"), ""),
                "ID Doc Uploaded": bool(st.session_state.get(inst_key(ns, instance_id, f"id_doc_{i}"))),
                "PoA Uploaded": bool(st.session_state.get(inst_key(ns, instance_id, f"poa_doc_{i}"))),
            })
            if config.get("show_uploads", True):
                uploads.extend([
                    st.session_state.get(inst_key(ns, instance_id, f"id_doc_{i}")),
                    st.session_state.get(inst_key(ns, instance_id, f"poa_doc_{i}")),
                ])

        payload = {"Count": n, "Records": people}
        return payload, uploads

# Register
register_component("natural_persons", NaturalPersonsComponent())
```

#### **Features**

- **Configurable UI**: `title`, `role_label`, `min_count` parameters customize display
- **Multiple ID Types**: SA ID (with Luhn validation), Foreign ID, Foreign Passport
- **Country-Specific Validation**: Different rules for SA vs international identification
- **Document Uploads**: Optional ID/PoA document collection
- **Instance Isolation**: Multiple instances (Directors, UBOs, etc.) on same page
- **Real-time Validation**: Immediate feedback + submission-time validation

#### **Configuration Options**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `title` | str | "Related Natural Persons" | Section heading |
| `role_label` | str | "Person" | Individual item labels |
| `min_count` | int | 0 | Minimum required entries |
| `show_uploads` | bool | True | Enable document uploads |
| `allowed_id_types` | List[str] | All types | Restrict ID type options |

---

### **Address Component** (`app/common_form_sections/address.py`)

Handles physical address collection with country-specific validation rules.

#### **Features**
- **Two-column layout**: Unit/Street Number + Complex/Street Name inputs
- **Country-specific validation**: SA requires 4-digit postal codes and province selection
- **Dynamic province field**: Shows SA provinces or "Other" based on country
- **Comprehensive fields**: Unit, Complex, Street Number/Name, Suburb, City, Province, Country, Postal Code

#### **Validation Rules**
- **Required**: Street Number, Street Name, Suburb, City
- **Conditional**: Province required for South Africa
- **Postal Code**: 4 digits for SA, ≤10 characters for other countries

### **Phone Component** (`app/common_form_sections/phone.py`)

Handles phone number collection with international dialing code support.

#### **Features**
- **Split layout**: Dialing code (1/3 width) + phone number (2/3 width)
- **Dynamic validation**: Different rules based on dialing code
- **International support**: Supports various country formats

#### **Validation Rules**
- **Required**: Both dialing code and phone number
- **SA Numbers (+27)**: Must be 9 digits, no leading zero
- **International**: 6-15 digits allowed

---

## ⚙️ **Form Engine** (`app/forms/engine.py`)

The form engine orchestrates the interaction between entity specifications and reusable components.

### **Core Data Structures**

```python
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Tuple
import streamlit as st
from app.utils import ns_key
from app.utils import (
    persist_text_input, persist_number_input, persist_text_area,
    persist_selectbox, persist_date_input, persist_checkbox, persist_file_uploader
)
from app.common_form_sections import get_component

@dataclass
class Field:
    key: str
    label: str
    kind: str
    required: bool = False
    options: Optional[List[str]] = None
    accept_multiple: bool = False

@dataclass
class Section:
    title: str
    fields: List[Field] = field(default_factory=list)
    # NEW: reference to a shared component
    component_id: Optional[str] = None
    component_args: Dict[str, Any] = field(default_factory=dict)

@dataclass
class FormSpec:
    name: str
    title: str
    sections: List[Section]

def _render_field(ns: str, f: Field):
    k = ns_key(ns, f.key)
    if f.kind == "text":     return persist_text_input(f.label, k)
    if f.kind == "number":   return persist_number_input(f.label, k, min_value=0, step=1)
    if f.kind == "textarea": return persist_text_area(f.label, k)
    if f.kind == "select":   return persist_selectbox(f.label, k, options=f.options or [])
    if f.kind == "date":     return persist_date_input(f.label, k)
    if f.kind == "checkbox": return persist_checkbox(f.label, k)
    if f.kind == "file":     return persist_file_uploader(f.label, k, accept_multiple_files=f.accept_multiple)
    st.info(f"Unsupported field kind '{f.kind}' for {f.label}")

def render_form(spec: FormSpec, ns: str):
    st.subheader(spec.title)
    for sec in spec.sections:
        with st.expander(sec.title, expanded=True):
            for f in sec.fields:
                _render_field(ns, f)
            if sec.component_id:
                comp = get_component(sec.component_id)
                if comp is None:
                    st.warning(f"Component '{sec.component_id}' not found.")
                else:
                    # Require instance_id; if not provided, fallback to section title slug
                    instance_id = sec.component_args.get("instance_id") or sec.title.lower().replace(" ", "_")
                    comp.render(ns=ns, instance_id=instance_id, **sec.component_args)

def serialize_answers(spec: FormSpec, ns: str) -> Tuple[Dict[str, Any], List[Any]]:
    answers: Dict[str, Any] = {"Entity Type": spec.title}
    uploads: List[Any] = []
    for sec in spec.sections:
        sec_dict: Dict[str, Any] = {}
        # Simple fields
        for f in sec.fields:
            val = st.session_state.get(ns_key(ns, f.key))
            if f.kind == "file":
                has_files = bool(val) if not f.accept_multiple else bool(val and len(val) > 0)
                sec_dict[f.label] = has_files
                if f.accept_multiple and isinstance(val, list):
                    uploads.extend([u for u in val if u is not None])
                elif val is not None:
                    uploads.append(val)
            else:
                sec_dict[f.label] = val

        # Component payload
        if sec.component_id:
            comp = get_component(sec.component_id)
            if comp:
                instance_id = sec.component_args.get("instance_id") or sec.title.lower().replace(" ", "_")
                payload, comp_uploads = comp.serialize(ns=ns, instance_id=instance_id, **sec.component_args)
                # If fields + component should both appear, merge; otherwise replace:
                sec_dict.update(payload if isinstance(payload, dict) else {})
                uploads.extend(comp_uploads or [])

        answers[sec.title] = sec_dict
    return answers, uploads

def validate(spec: FormSpec, ns: str) -> List[str]:
    errs: List[str] = []
    # Field-level required checks
    for sec in spec.sections:
        for f in sec.fields:
            v = st.session_state.get(ns_key(ns, f.key))
            if f.required:
                if f.kind == "file":
                    if f.accept_multiple:
                        if not v or len([u for u in v if u is not None]) == 0:
                            errs.append(f"[{sec.title}] {f.label} is required.")
                    else:
                        if v is None:
                            errs.append(f"[{sec.title}] {f.label} is required.")
                else:
                    if v in (None, "", []):
                        errs.append(f"[{sec.title}] {f.label} is required.")
        # Component validation
        if sec.component_id:
            comp = get_component(sec.component_id)
            if comp:
                instance_id = sec.component_args.get("instance_id") or sec.title.lower().replace(" ", "_")
                errs.extend(comp.validate(ns=ns, instance_id=instance_id, **sec.component_args))
    return errs
```

---

## 7) Specs call the common section with an `instance_id`

Update **`app/forms/specs/company.py`**:

```python
from app.forms.engine import FormSpec, Section, Field

SPEC = FormSpec(
    name="company",
    title="Company",
    sections=[
        Section(
            title="Entity Details",
            fields=[Field("legal_name", "Legal / Registered Name", "text", required=True)]
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
            title="Contact Information",
            component_id="phone",
            component_args={
                "instance_id": "contact_phone",
                "title": "Contact Number"
            }
        ),
        Section(
            title="Directors",
            component_id="natural_persons",
            component_args={
                "instance_id": "directors",
                "title": "Directors",
                "role_label": "Director",
                "min_count": 1,           # require at least one
                "show_uploads": True,
                # "allowed_id_types": ["SA ID Number", "Foreign Passport Number"]  # optional override
            }
        ),
        # You can mount it again for UBOs, with different rules:
        Section(
            title="Beneficial Owners (>5%)",
            component_id="natural_persons",
            component_args={
                "instance_id": "ubos",
                "title": "Beneficial Owners (>5%)",
                "role_label": "Owner",
                "min_count": 0,
                "show_uploads": True
            }
        ),
    ]
)
```

> The **same module** (`natural_persons`) now powers **both** Directors and UBOs, with different headings and rules—no duplication.

Repeat analogous patterns in `trust.py`, `partnership.py`, etc. Just pass a different `instance_id` and labels like "Trustees", "Partners", etc.

**`trust.py`**

```python
from app.forms.engine import FormSpec, Section, Field
SPEC = FormSpec(
    name="trust",
    title="Trust",
    sections=[
        Section(title="Entity Details", fields=[Field("legal_name","Trust Name","text", required=True)]),
        Section(title="Physical Address", component_id="address", component_args={"instance_id": "trust_address"}),
        Section(title="Contact", component_id="phone", component_args={"instance_id": "trust_phone"}),
        Section(title="Trustees", component_id="natural_persons", component_args={
            "instance_id": "trustees", "role_label": "Trustee", "min_count": 1
        }),
        Section(title="Beneficiaries", component_id="natural_persons", component_args={
            "instance_id": "beneficiaries", "role_label": "Beneficiary", "min_count": 0
        }),
    ]
)
```

**`partnership.py`**

```python
from app.forms.engine import FormSpec, Section, Field
SPEC = FormSpec(
    name="partnership",
    title="Partnership",
    sections=[
        Section(title="Entity Details", fields=[Field("legal_name","Partnership Name","text", required=True)]),
        Section(title="Physical Address", component_id="address", component_args={"instance_id": "partnership_address"}),
        Section(title="Contact", component_id="phone", component_args={"instance_id": "partnership_phone"}),
        Section(title="Partners", component_id="natural_persons", component_args={
            "instance_id": "partners", "role_label": "Partner", "min_count": 2
        }),
    ]
)
```

**`closed_corporation.py`**

```python
from app.forms.engine import FormSpec, Section, Field
SPEC = FormSpec(
    name="closed_corporation",
    title="Closed Corporation",
    sections=[
        Section(title="Entity Details", fields=[Field("legal_name","CC Registered Name","text", required=True)]),
        Section(title="Physical Address", component_id="address", component_args={"instance_id": "cc_address"}),
        Section(title="Contact", component_id="phone", component_args={"instance_id": "cc_phone"}),
        Section(title="Members", component_id="natural_persons", component_args={
            "instance_id": "members", "role_label": "Member", "min_count": 1
        }),
    ]
)
```

**`other.py`**

```python
from app.forms.engine import FormSpec, Section, Field
SPEC = FormSpec(
    name="other",
    title="Other",
    sections=[
        Section(title="Entity Details", fields=[Field("legal_name","Entity Name","text", required=True)]),
        Section(title="Physical Address", component_id="address", component_args={"instance_id": "other_address"}),
        Section(title="Contact", component_id="phone", component_args={"instance_id": "other_phone"}),
        Section(title="Associated People", component_id="natural_persons", component_args={
            "instance_id": "associated", "role_label": "Person", "min_count": 0
        }),
    ]
)
```

**`__init__.py`**

```python
from . import company, trust, partnership, closed_corporation, other

SPECS = {
    "company": company.SPEC,
    "trust": trust.SPEC,
    "partnership": partnership.SPEC,
    "closed_corporation": closed_corporation.SPEC,
    "other": other.SPEC,
}
```

---

## 8) No changes to your 3‑page flow

* **Introduction** (`app/main.py`) already renders the form by reading the spec and calling `render_form()`.
* **Declaration & Submit** still calls `validate(spec, ns)` → blocks invalid → `serialize_answers()` → email + PDF.
* **AI Assistance**: unchanged.

---

## 9) Migration note (if you used `form_parts.py` earlier)

If you already created `app/components/form_parts.py`, you can either:

* **Replace it** completely with this new `common_form_sections` package; or
* Keep it temporarily as a **shim** that forwards calls to registered components (to avoid touching older code paths). The new approach is more modular.

---

## 10) How to add more shared sections (pattern)

1. Create `app/common_form_sections/<name>.py`.
2. Implement a `SectionComponent` with `render`, `validate`, `serialize`.
3. At the bottom, `register_component("<name>", <YourComponent>())`.
4. In any spec, add:

   ```python
   Section(
       title="My Reused Block",
       component_id="<name>",
       component_args={"instance_id": "my_block", ...your config...}
   )
   ```

---

## 11) Replace **Introduction** page with the dynamic form

**`app/main.py`**:

```python
from __future__ import annotations
import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.styling import GOOGLE_FONTS_CSS, GRADIENT_TITLE_CSS, FADE_IN_CSS
from app.components.sidebar import render_sidebar
from app.utils import initialize_state, persist_selectbox, persist_text_input, current_namespace, ns_key, ENTITY_TYPES
from app.forms.engine import render_form
from app.forms.specs import SPECS

def main():
    favicon_path = Path(__file__).resolve().parent.parent / "assets" / "logos" / "favicon.png"
    st.set_page_config("Entity Onboarding", str(favicon_path), layout="wide", initial_sidebar_state="expanded")

    st.markdown(GOOGLE_FONTS_CSS, unsafe_allow_html=True)
    st.markdown(GRADIENT_TITLE_CSS, unsafe_allow_html=True)
    st.markdown(FADE_IN_CSS, unsafe_allow_html=True)

    initialize_state()
    render_sidebar()

    st.markdown('<h1 class="gradient-title">Entity Onboarding</h1>', unsafe_allow_html=True)
    st.caption("Select an entity type. All information is captured on this page with built-in validation.")

    # Entity selector
    persist_selectbox("Entity Type", "entity_type", options=ENTITY_TYPES)
    ns = current_namespace()

    # EntityUserID immediately after entity type
    persist_text_input("Entity User ID", "entity_user_id")

    # Render the form according to the current spec
    spec = SPECS.get(ns)
    if not spec:
        st.warning("This entity type is not yet configured.")
        return

    render_form(spec, ns)

    # Capture a display name for downstream artifacts (email/PDF)
    legal_name = st.session_state.get(ns_key(ns, "legal_name"), "")
    if legal_name:
        st.session_state["entity_display_name"] = legal_name

    st.markdown("---")
    st.page_link('pages/3_Declaration_and_Submit.py', label='Proceed to Declaration & Submit', icon='📝')

if __name__ == "__main__":
    main()
```

---

## 12) Developer checklist

* [ ] Add `inst_key()` to `utils.py`.
* [ ] Add `common_form_sections` package (base + registry + `natural_persons.py` + `address.py` + `phone.py`).
* [ ] Update `engine.py` to support `component_id` + `component_args`.
* [ ] Refactor specs to use common sections with distinct `instance_id` values.
* [ ] Verify: you can mount **multiple natural\_persons blocks** on one page without collisions.
* [ ] Submit flow validates and serializes the combined payload.

---

## 13) Final page: validate → serialize → submit

Rename old file to **`app/pages/3_Declaration_and_Submit.py`** and replace content:

```python
import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app.components.sidebar import render_sidebar
from app.components.submission import handle_submission
from app.styling import GOOGLE_FONTS_CSS, GRADIENT_TITLE_CSS, FADE_IN_CSS
from app.utils import initialize_state, persist_checkbox, persist_text_input, current_namespace
from app.forms.specs import SPECS
from app.forms.engine import serialize_answers, validate

initialize_state()
st.markdown(GOOGLE_FONTS_CSS, unsafe_allow_html=True)
st.markdown(GRADIENT_TITLE_CSS, unsafe_allow_html=True)
st.markdown(FADE_IN_CSS, unsafe_allow_html=True)
render_sidebar()

st.header("Declaration & Submit")

persist_checkbox("I/we declare the information provided is true, accurate, complete, and up-to-date.", "accept")
cols = st.columns(2)
with cols[0]:
    persist_text_input("Signatory #1 – Full Name", "s1_name")
with cols[1]:
    persist_text_input("Signatory #1 – Designation", "s1_desig")
cols = st.columns(2)
with cols[0]:
    persist_text_input("Signatory #2 – Full Name (optional)", "s2_name")
with cols[1]:
    persist_text_input("Signatory #2 – Designation (optional)", "s2_desig")

st.markdown("---")
st.subheader("Final Submission")

def reconstruct_payload():
    ns = current_namespace()
    spec = SPECS.get(ns)
    if not spec:
        st.error("The selected entity type is not configured.")
        st.stop()

    # Formal validation pass (component + required fields)
    errors = validate(spec, ns)
    if errors:
        st.error("Please resolve the following issues before submitting:")
        for e in errors:
            st.markdown(f"- {e}")
        st.stop()

    answers, uploads = serialize_answers(spec, ns)
    # Attach global submission metadata
    answers["Entity User ID"] = st.session_state.get("entity_user_id", "")
    answers["Declaration"] = {
        "Declaration Accepted": st.session_state.get("accept", False),
        "Signatory 1 Name": st.session_state.get("s1_name", ""),
        "Signatory 1 Designation": st.session_state.get("s1_desig", ""),
        "Signatory 2 Name": st.session_state.get("s2_name", ""),
        "Signatory 2 Designation": st.session_state.get("s2_desig", ""),
    }
    return answers, uploads

if st.button("Confirm & Submit", use_container_width=True, type="primary"):
    answers_data, uploaded_files_data = reconstruct_payload()
    handle_submission(answers_data, uploaded_files_data)
```

---

## 14) Genericize submission, email, and PDF

**`app/components/submission.py`** (change success naming + PDF filename only):

```python
# inside handle_submission(...)
entity_name = st.session_state.get("entity_display_name", "UnknownEntity")
dt = datetime.datetime.now().strftime("%Y%m%d_%H%M")
pdf_name = f"Entity_Onboarding_{entity_name.replace(' ', '')}_{dt}.pdf"
st.success(f"✅ Onboarding submission for **{entity_name}** captured successfully. Please download your files below.")
```

**`app/email_sender.py`** (recipient via secrets; generic subject/body):

```python
recipient_email = st.secrets.get("email_credentials", {}).get("recipient_address", sender_email)
entity_name = st.session_state.get("entity_display_name", "Unknown Entity")
subject = f"New Onboarding Submission: {entity_name}"

body = "A new onboarding submission has been received.\n\n"
body += "Please find the PDF summary and all supporting documents attached.\n\n"
body += "Regards,\nEntity Onboarding App"
```

**`app/pdf_generator.py`** (title line):

```python
c.setFont("Helvetica-Bold", 16)
c.drawString(margin, y, "Entity Onboarding – Response Summary")
```

> `secrets.toml` example:
>
> ```toml
> [email_credentials]
> email_address = "no-reply@your-domain.com"
> app_password = "your_app_pw"
> recipient_address = "ops@your-domain.com"
> ```

---

## 15) (Optional) Make AI page generic

If you want a neutral assistant now (you can swap the knowledge file later), tweak the `SYSTEM_PROMPT` header in **`app/pages/1_AI_Assistance.py`** to describe a generic onboarding assistant. No code logic changes are needed.

---

## 16) Built-in validation rules (current)

* **Address**

  * Required: Street No, Street Name, Suburb, City
  * If Country = **South Africa**, **Province** required and **Postal Code = 4 digits**
  * Non‑SA postal code: free‑form (≤ 10 chars)

* **Phone**

  * Required: Dialing Code, Number
  * If Dialing Code = **+27**, Number must be **9 digits** and **not start with 0**
  * Otherwise: **6–15 digits**

* **Natural Persons**

  * Required: Full Name, Identification Type
  * If **SA ID**: must be **13 digits** and pass a **Luhn check**
  * If **Foreign ID**: number required
  * If **Passport**: number, issue country, and **future** expiry date required

* **Fields marked `required=True`** in specs (e.g., Legal / Registered Name) are enforced engine‑wide.

> All checks run **in the UI** and again on **submit** to prevent malformed payloads.

---

## 17) Developer extension points

* Add new components to `common_form_sections/<name>.py`: implement a `SectionComponent` with `render`, `validate`, `serialize`, then register.
* Add per‑entity sections in `app/forms/specs/*` (mix of simple `Field`s and `component_id`s).
* For advanced phone checks, optionally add `phonenumbers` to `requirements.txt` and upgrade `_phone_ok` accordingly.
* For SA ID, you can extend `_valid_sa_id` to verify YYMMDD birthdate parts.

---

## 18) Quick smoke test

1. App loads with **3 pages** in the sidebar.
2. Introduction → choose **Entity Type**, enter **Entity User ID**, complete sections.
3. Switch entity types and back—data should persist (thanks to namespacing).
4. Go to **Declaration & Submit**. If anything is invalid, you’ll see a list and submit will be blocked.
5. When valid: you receive the **email**, and a **PDF** is offered for download.

---

## 19) Why this meets your goal

* **Single source of truth**: Edit **one** `natural_persons.py` to change labels, validations, or data policy for *all* journeys.
* **Composable**: Mount the same component multiple times with different **instance\_id** and **rules**.
* **Low coupling**: Specs stay declarative; engine guarantees consistent render/validate/serialize.
* **Future‑proof**: Add new common sections (address, contact, bank details) by following the same interface.

---

---

## 📊 **Technical Summary**

### **Architecture Benefits**

| **Aspect** | **Implementation** | **Benefit** |
|------------|-------------------|-------------|
| **Reusability** | Components implement standard interface | Single codebase for all entity types |
| **Modularity** | Component registry + declarative specs | Easy to add new entity types |
| **State Management** | Namespace + instance scoping | No data collisions, entity switching |
| **Validation** | Real-time + submission validation | Immediate feedback + robust submission |
| **Maintainability** | Centralized component logic | Changes update all usages automatically |

### **Data Flow**

```
User Interaction → Session State (namespaced) → Component Validation → Form Submission
     ↓                    ↓                          ↓                       ↓
UI Widgets         ns_key/inst_key            Error Messages         PDF + Email
```

### **Key Files & Responsibilities**

| **File/Package** | **Responsibility** | **Key Features** |
|------------------|-------------------|------------------|
| `utils.py` | State management, key generation | Namespace isolation, instance scoping |
| `common_form_sections/` | Reusable UI components | render/validate/serialize interface |
| `forms/engine.py` | Form orchestration | Component integration, conflict resolution |  
| `forms/specs/` | Entity definitions | Declarative form configuration |
| `main.py` | Dynamic form rendering | Entity type selection, form generation |
| `3_Declaration_and_Submit.py` | Final validation & submission | Error checking, payload assembly |

### **Validation Rules Summary**

| **Component** | **Required Fields** | **Special Validation** |
|---------------|-------------------|----------------------|
| **Natural Persons** | Full Name, ID Type | SA ID Luhn check, future passport expiry |
| **Address** | Street No/Name, Suburb, City | SA postal code (4 digits), province |
| **Phone** | Dialing Code, Number | SA format (9 digits, no leading 0) |
| **Entity Fields** | Legal Name | Per-spec requirements |

### **Instance Usage Examples**

```python
# Company form using same component multiple times
Section(title="Directors", component_id="natural_persons", 
        component_args={"instance_id": "directors", "min_count": 1})
        
Section(title="UBOs", component_id="natural_persons",
        component_args={"instance_id": "ubos", "min_count": 0})
```

### **Session State Structure**

```python
# Global keys
"entity_type" → "Company"
"entity_user_id" → "COMP001"

# Namespaced keys  
"company__legal_name" → "Acme Corp Ltd"

# Instance keys
"company__directors__count" → 2
"company__directors__full_0" → "John Smith"
"company__ubos__count" → 1
"company__ubos__full_0" → "Jane Doe"
```

This architecture provides a robust, scalable foundation for entity onboarding with maximum code reuse and maintainability.
