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
