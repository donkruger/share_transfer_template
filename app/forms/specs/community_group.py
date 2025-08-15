from app.forms.engine import FormSpec, Section
from app.forms.field_helpers import create_entity_details_fields

SPEC = FormSpec(
    name="community_group",
    title="Community Group",
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
            title="Committee Members",
            component_id="natural_persons",
            component_args={
                "instance_id": "committee_members",
                "title": "Committee Members",
                "role_label": "Committee Member",
                "min_count": 1,
                "show_uploads": True
            }
        ),
    ]
)