from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Tuple
import streamlit as st
from app.utils import ns_key
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
                    # Create a copy of component_args without instance_id to avoid duplicate keyword argument
                    component_kwargs = {k: v for k, v in sec.component_args.items() if k != "instance_id"}
                    comp.render(ns=ns, instance_id=instance_id, **component_kwargs)

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
                component_kwargs = {k: v for k, v in sec.component_args.items() if k != "instance_id"}
                payload, comp_uploads = comp.serialize(ns=ns, instance_id=instance_id, **component_kwargs)
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
                elif f.kind == "multiselect":
                    if not v or len(v) == 0:
                        errs.append(f"[{sec.title}] {f.label} is required.")
                else:
                    if v in (None, "", []):
                        errs.append(f"[{sec.title}] {f.label} is required.")
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
