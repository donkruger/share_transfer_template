from __future__ import annotations
from typing import Dict
from app.common_form_sections.base import SectionComponent

# Simple in-process registry
_REGISTRY: Dict[str, SectionComponent] = {}

def register_component(name: str, component: SectionComponent):
    """Register a reusable section under a stable name."""
    _REGISTRY[name] = component

def get_component(name: str) -> SectionComponent | None:
    return _REGISTRY.get(name)

def get_component_registry() -> Dict[str, SectionComponent]:
    """Get the complete component registry."""
    return _REGISTRY.copy()

# Import component modules
from . import natural_persons
from . import address
from . import phone
from . import authorised_representative
from . import juristic_entities
from . import controlling_person
from . import fatca_section
from . import crs_section

# Register all components (done after imports to avoid circular dependencies)
register_component("natural_persons", natural_persons.NaturalPersonsComponent())
register_component("address", address.AddressComponent())
register_component("phone", phone.PhoneComponent())
register_component("authorised_representative", authorised_representative.AuthorisedRepresentativeComponent())
register_component("juristic_entities", juristic_entities.JuristicEntitiesComponent())
register_component("controlling_person", controlling_person.ControllingPersonComponent())
register_component("fatca_section", fatca_section.FatcaSectionComponent())
register_component("crs_section", crs_section.CrsSectionComponent())
