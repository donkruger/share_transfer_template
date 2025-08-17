from app.forms.engine import FormSpec, Section
from app.forms.field_helpers import create_entity_details_fields

SPEC = FormSpec(
    name="burial_society",
    title="Burial Society",
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
            title="Contact Information",
            component_id="phone",
            component_args={
                "instance_id": "contact_phone",
                "title": "Contact Number"
            }
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
        # Required Roles per Entity Roles Rules Specification - Informal Associations
        Section(
            title="Members (Natural Persons)",
            component_id="natural_persons",
            component_args={
                "instance_id": "members_natural",
                "title": "Natural Person Members",
                "role_label": "Member",
                "min_count": 1,           # At least one Member required
                "show_uploads": True,
                "show_member_roles": True,  # Enable Member Role selection for informal associations
                "help_text": "Natural person members with Member Role selection required."
            }
        ),
        Section(
            title="Members (Juristic Entities)",
            component_id="juristic_entities",
            component_args={
                "instance_id": "members_juristic", 
                "title": "Juristic Entity Members",
                "role_label": "Member",
                "min_count": 0,
                "help_text": "Juristic entity members (beneficial owners not required for informal associations)."
            }
        ),
    ]
)