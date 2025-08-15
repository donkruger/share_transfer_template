from . import (
    company, trust, partnership, closed_corporation, other,
    burial_society, charity_organisation, church, community_group,
    cultural_association, environmental_group, investment_club,
    savings_club, school, social_club, sports_club, stokvel
)

SPECS = {
    "burial_society": burial_society.SPEC,
    "charity_organisation": charity_organisation.SPEC,
    "church": church.SPEC,
    "closed_corporation": closed_corporation.SPEC,
    "company": company.SPEC,
    "community_group": community_group.SPEC,
    "cultural_association": cultural_association.SPEC,
    "environmental_group": environmental_group.SPEC,
    "investment_club": investment_club.SPEC,
    "partnership": partnership.SPEC,
    "savings_club": savings_club.SPEC,
    "school": school.SPEC,
    "social_club": social_club.SPEC,
    "sports_club": sports_club.SPEC,
    "stokvel": stokvel.SPEC,
    "trust": trust.SPEC,
    "other": other.SPEC,
}
