from app.forms.engine import FormSpec, Section
from app.forms.field_helpers import create_entity_details_fields

SPEC = FormSpec(
    name="company",
    title="Company",
    sections=[
        Section(
            title="Entity Details",
            fields=create_entity_details_fields()
        ),
        Section(
            title="Authorised Representative",
            component_id="authorised_representative",
            component_args={
                "instance_id": "auth_rep",
                "title": "Authorised Representative"
            }
        ),
        Section(
            title="Authorised Representative Address",
            component_id="address",
            component_args={
                "instance_id": "auth_rep_address",
                "title": "Authorised Representative Address"
            }
        ),
        Section(
            title="Entity Physical Address",
            component_id="address",
            component_args={
                "instance_id": "physical_address",
                "title": "Entity Physical Address"
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
        # Required Roles per Entity Roles Rules Specification - Companies
        Section(
            title="Company Directors",
            component_id="natural_persons",
            component_args={
                "instance_id": "directors",
                "title": "Company Directors (Natural Persons Only)",
                "role_label": "Director",
                "min_count": 1,           # At least one Director required
                "show_uploads": True,
                "help_text": "All Company Directors must be natural persons. Executive Control field is required."
            }
        ),
        
        # Additional Roles - Shareholders (Natural Person or Juristic Entity)
        Section(
            title="Shareholders (Natural Persons)",
            component_id="natural_persons",
            component_args={
                "instance_id": "shareholders_natural",
                "title": "Natural Person Shareholders",
                "role_label": "Shareholder",
                "min_count": 0,
                "show_uploads": True,
                "help_text": "Natural person shareholders with percentage shareholding capture."
            }
        ),
        Section(
            title="Shareholders (Juristic Entities)",
            component_id="juristic_entities",
            component_args={
                "instance_id": "shareholders_juristic", 
                "title": "Juristic Entity Shareholders",
                "role_label": "Shareholder",
                "min_count": 0,
                "help_text": "Juristic entity shareholders with percentage shareholding capture."
            }
        ),
    ]
)
