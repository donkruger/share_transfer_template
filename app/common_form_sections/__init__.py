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

# Import component modules
from . import natural_persons
from . import address
from . import phone
from . import authorised_representative
from . import juristic_entities

# Register all components (done after imports to avoid circular dependencies)
register_component("natural_persons", natural_persons.NaturalPersonsComponent())
register_component("address", address.AddressComponent())
register_component("phone", phone.PhoneComponent())
register_component("authorised_representative", authorised_representative.AuthorisedRepresentativeComponent())
register_component("juristic_entities", juristic_entities.JuristicEntitiesComponent())
