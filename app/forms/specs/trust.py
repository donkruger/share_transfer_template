from app.forms.engine import FormSpec, Section
from app.forms.field_helpers import create_entity_details_fields

SPEC = FormSpec(
    name="trust",
    title="Trust",
    sections=[
        Section(
            title="Entity Details",
            fields=create_entity_details_fields("Entity Name (Trust Name)", include_trust_fields=True)
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
        Section(title="Trustees", component_id="natural_persons", component_args={
            "instance_id": "trustees", "role_label": "Trustee", "min_count": 1
        }),
        Section(title="Beneficiaries", component_id="natural_persons", component_args={
            "instance_id": "beneficiaries", "role_label": "Beneficiary", "min_count": 0
        }),
    ]
)
