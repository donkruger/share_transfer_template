from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Tuple
import streamlit as st
from app.utils import ns_key
from app.field_specifications import get_date_bounds
from app.utils import (
    persist_text_input, persist_number_input, persist_text_area,
    persist_selectbox, persist_date_input, persist_checkbox, persist_file_uploader,
    persist_multiselect
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
    help_text: Optional[str] = None

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
    if f.kind == "multiselect": return persist_multiselect(f.label, k, options=f.options or [])
    if f.kind == "date":
        min_d, max_d = get_date_bounds(f.key)
        # Fallback for Date of Registration if specs are missing at runtime
        if f.key == "date_of_registration":
            try:
                import datetime as _dt
                if min_d is None:
                    min_d = _dt.date(1800, 1, 1)
                if max_d is None:
                    max_d = _dt.date.today()
            except Exception:
                pass
        kwargs = {}
        if min_d is not None:
            kwargs["min_value"] = min_d
        if max_d is not None:
            kwargs["max_value"] = max_d
        return persist_date_input(f.label, k, **kwargs)
    if f.kind == "checkbox": return persist_checkbox(f.label, k)
    if f.kind == "file":     return persist_file_uploader(f.label, k, accept_multiple_files=f.accept_multiple)
    if f.kind == "info":     
        # Display info message with help text if available
        if f.help_text:
            st.info(f"{f.label}\n\n{f.help_text}")
        else:
            st.info(f.label)
        return
    st.info(f"Unsupported field kind '{f.kind}' for {f.label}")

def render_form(spec: FormSpec, ns: str):
    st.subheader(spec.title)
    for sec in spec.sections:
        with st.expander(sec.title, expanded=False):
            for f in sec.fields:
                _render_field(ns, f)
            if sec.component_id:
                comp = get_component(sec.component_id)
                if comp is None:
                    st.warning(f"Component '{sec.component_id}' not found.")
                else:
                    # Require instance_id; if not provided, fallback to section title slug
                    instance_id = sec.component_args.get("instance_id") or sec.title.lower().replace(" ", "_")
                    # Create a copy of component_args without instance_id to avoid duplicate keyword argument
                    component_kwargs = {k: v for k, v in sec.component_args.items() if k != "instance_id"}
                    comp.render(ns=ns, instance_id=instance_id, **component_kwargs)

def serialize_answers(spec: FormSpec, ns: str) -> Tuple[Dict[str, Any], List[Any]]:
    answers: Dict[str, Any] = {"Entity Type": spec.title}
    uploads: List[Any] = []
    
    # Debug information for development mode
    try:
        from app.utils import is_dev_mode
        if is_dev_mode():
            st.info(f"🔧 **Dev Mode Active** - Serializing answers for {spec.title}")
    except ImportError:
        pass
    
    for sec in spec.sections:
        sec_dict: Dict[str, Any] = {}
        # Simple fields
        for f in sec.fields:
            # Skip info fields as they are just display messages
            if f.kind == "info":
                continue
                
            val = st.session_state.get(ns_key(ns, f.key))
            if f.kind == "file":
                has_files = bool(val) if not f.accept_multiple else bool(val and len(val) > 0)
                sec_dict[f.label] = has_files
                if f.accept_multiple and isinstance(val, list):
                    uploads.extend([u for u in val if u is not None])
                elif val is not None:
                    uploads.append(val)
            else:
                # Normalize date to YYYY/MM/DD for consistency when serializing
                if f.kind == "date" and val is not None:
                    try:
                        # Streamlit date_input returns datetime.date
                        sec_dict[f.label] = val.strftime("%Y/%m/%d")
                    except Exception:
                        sec_dict[f.label] = val
                else:
                    sec_dict[f.label] = val

        # Component payload
        if sec.component_id:
            comp = get_component(sec.component_id)
            if comp:
                instance_id = sec.component_args.get("instance_id") or sec.title.lower().replace(" ", "_")
                component_kwargs = {k: v for k, v in sec.component_args.items() if k != "instance_id"}
                
                # Debug component serialization
                try:
                    payload, comp_uploads = comp.serialize(ns=ns, instance_id=instance_id, **component_kwargs)
                    
                    # Debug information for development mode
                    try:
                        from app.utils import is_dev_mode
                        if is_dev_mode():
                            st.info(f"🔧 **Dev Mode Active** - Component {sec.component_id} returned: {type(payload).__name__}")
                            if isinstance(payload, dict):
                                st.info(f"  Keys: {list(payload.keys())}")
                            else:
                                st.warning(f"  ⚠️ Unexpected payload type: {type(payload).__name__}")
                                st.warning(f"  Content: {str(payload)[:100]}...")
                    except ImportError:
                        pass
                    
                    # If fields + component should both appear, merge; otherwise replace:
                    sec_dict.update(payload if isinstance(payload, dict) else {})
                    uploads.extend(comp_uploads or [])
                    
                except Exception as e:
                    st.error(f"❌ Error serializing component {sec.component_id}: {e}")
                    # Continue with other components instead of failing completely
                    continue

        answers[sec.title] = sec_dict
    
    # Debug information for development mode
    try:
        from app.utils import is_dev_mode
        if is_dev_mode():
            st.info(f"🔧 **Dev Mode Active** - Serialized {len(answers)} sections")
            st.json({
                "sections": list(answers.keys()),
                "total_uploads": len(uploads)
            })
            
            # Show the structure of each section
            for section_name, section_data in answers.items():
                st.info(f"Section '{section_name}': {type(section_data).__name__}")
                if isinstance(section_data, dict):
                    st.info(f"  Keys: {list(section_data.keys())}")
                else:
                    st.warning(f"  ⚠️ Unexpected section data type: {type(section_data).__name__}")
                    st.warning(f"  Content: {str(section_data)[:100]}...")
    except ImportError:
        pass
    
    # Safety check: ensure we always return a valid dictionary structure
    if not isinstance(answers, dict):
        st.warning(f"⚠️ serialize_answers returned {type(answers).__name__}, converting to dict")
        answers = {"Entity Type": spec.title, "Error": f"Invalid data type: {type(answers).__name__}"}
    
    # Ensure all values in answers are serializable
    for key, value in list(answers.items()):
        if not isinstance(value, (dict, list, str, int, float, bool)) and value is not None:
            answers[key] = str(value)
    
    return answers, uploads

def validate(spec: FormSpec, ns: str) -> List[str]:
    # Check if development mode is enabled - if so, skip all validation
    try:
        from app.utils import is_dev_mode
        if is_dev_mode():
            return []  # Return empty list (no errors) when dev mode is enabled
    except ImportError:
        pass  # If utils import fails, continue with normal validation
    
    errs: List[str] = []
    # Field-level required checks
    for sec in spec.sections:
        for f in sec.fields:
            # Skip info fields as they are just display messages
            if f.kind == "info":
                continue
                
            v = st.session_state.get(ns_key(ns, f.key))
            if f.required:
                if f.kind == "file":
                    if f.accept_multiple:
                        if not v or len([u for u in v if u is not None]) == 0:
                            errs.append(f"[{sec.title}] {f.label} is required.")
                    else:
                        if v is None:
                            errs.append(f"[{sec.title}] {f.label} is required.")
                elif f.kind == "multiselect":
                    if not v or len(v) == 0:
                        errs.append(f"[{sec.title}] {f.label} is required.")
                else:
                    if v in (None, "", []):
                        errs.append(f"[{sec.title}] {f.label} is required.")
            # Date bounds validation (no future, not before min_date)
            if f.kind == "date" and v is not None:
                try:
                    min_d, max_d = get_date_bounds(f.key)
                except Exception:
                    min_d, max_d = (None, None)
                # Fallback for Date of Registration
                if f.key == "date_of_registration":
                    try:
                        import datetime as _dt
                        if min_d is None:
                            min_d = _dt.date(1800, 1, 1)
                        if max_d is None:
                            max_d = _dt.date.today()
                    except Exception:
                        pass
                # If max bound provided, disallow dates after it
                if max_d is not None and v > max_d:
                    errs.append(f"[{sec.title}] {f.label} cannot be in the future.")
                # If min bound provided, disallow dates before it
                if min_d is not None and v < min_d:
                    errs.append(f"[{sec.title}] {f.label} cannot be before {min_d.strftime('%Y/%m/%d')}.")
        # Component validation
        if sec.component_id:
            comp = get_component(sec.component_id)
            if comp:
                instance_id = sec.component_args.get("instance_id") or sec.title.lower().replace(" ", "_")
                component_kwargs = {k: v for k, v in sec.component_args.items() if k != "instance_id"}
                errs.extend(comp.validate(ns=ns, instance_id=instance_id, **component_kwargs))
    
    # Custom validation rules for conditional requirements
    _add_conditional_validation_rules(spec, ns, errs)
    
    return errs

def _add_conditional_validation_rules(spec: FormSpec, ns: str, errs: List[str]):
    """Add custom validation rules for conditional field requirements."""
    
    # Rule: If Registration Number is provided, Country of Registration is required
    reg_number = st.session_state.get(ns_key(ns, "registration_number"), "")
    if reg_number and reg_number.strip():
        country_of_reg = st.session_state.get(ns_key(ns, "country_of_registration"), "")
        if not country_of_reg or country_of_reg.strip() == "":
            errs.append("[Entity Details] Country of Registration is required when Registration Number is provided.")
    
    # Rule: Masters Office field validation for Trust entity type
    if spec.name == "trust":
        masters_office = st.session_state.get(ns_key(ns, "masters_office"), "")
        if not masters_office or masters_office.strip() == "":
            errs.append("[Entity Details] Masters Office where the Trust was registered is required for Trust entities.")
        elif len(masters_office.strip()) > 200:
            errs.append("[Entity Details] Masters Office field must not exceed 200 characters.")
    
    # Rule: Registration Number character limit validation (3-50 chars)
    if reg_number and reg_number.strip():
        if len(reg_number.strip()) < 3 or len(reg_number.strip()) > 50:
            errs.append("[Entity Details] Registration Number must be between 3 and 50 characters.")
