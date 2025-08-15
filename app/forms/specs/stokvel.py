from app.forms.engine import FormSpec, Section
from app.forms.field_helpers import create_entity_details_fields

SPEC = FormSpec(
    name="stokvel",
    title="Stokvel",
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
            title="Members",
            component_id="natural_persons",
            component_args={
                "instance_id": "members",
                "title": "Stokvel Members",
                "role_label": "Member",
                "min_count": 2,
                "show_uploads": True
            }
        ),
    ]
)