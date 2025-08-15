from app.forms.engine import FormSpec, Section
from app.forms.field_helpers import create_entity_details_fields

SPEC = FormSpec(
    name="partnership",
    title="Partnership",
    sections=[
        Section(
            title="Entity Details",
            fields=create_entity_details_fields("Entity Name (Partnership Name)")
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
        Section(title="Partners", component_id="natural_persons", component_args={
            "instance_id": "partners", "role_label": "Partner", "min_count": 2
        }),
    ]
)
