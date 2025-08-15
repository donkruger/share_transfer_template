"""
Controlled Lists for Entity Onboarding System

This module contains all predefined/controlled lists used throughout the application.
These lists can be easily managed and expanded as requirements change.

Sections:
- 4.1 Source of Funds Options
- 4.2 Industry Options  
- 4.3 Member Role Options
"""

# 4.1 Source of Funds Options
SOURCE_OF_FUNDS_OPTIONS = [
    "",  # Empty option for unselected state
    "Business Operating Income",
    "Commission",
    "Company Profits",
    "Company Sale / Sale of Interest in Company",
    "Contribution from Third Party",
    "Cryptocurrency",
    "Debt Capital",
    "Dividends from Investments",
    "Employee Benefits",
    "Equity Capital",
    "Gift / Donation",
    "Inheritance",
    "Maturing Investments",
    "Member Contributions",
    "Pension",
    "Provident Funds",
    "Rental of Property",
    "Retained Earnings",
    "Retirement Funds",
    "Sale Asset / Property",
    "Sale of Shares",
    "Sanlam Payout",
    "Savings",
    "Settlement",
    "Tax Rebate",
    "Transfer to/from Approved Funds",
    "Trust Income"
]

# 4.2 Industry Options
INDUSTRY_OPTIONS = [
    "",  # Empty option for unselected state
    "Accounting Services",
    "Administrative and Support Services",
    "Adult Entertainment",
    "Aerospace & Defense",
    "Agriculture, Forestry and Fishing",
    "Arms Dealers",
    "Arts, Entertainment and Recreation",
    "Automobiles & Parts",
    "Banks",
    "Beverages",
    "Broadcasting and Entertainment",
    "Cannabis/CBD Industry",
    "Cash Aggregators",
    "Chemical Engineering / Manufacturing",
    "Community and Social Activities",
    "Construction and Civil Engineering",
    "Consumer Goods: Wholesale and Retail",
    "Education",
    "Electricity, Solar, Water, Gas and Waste Services",
    "Electronic & Electrical Equipment",
    "Entrepreneurship",
    "Equity Investment Instruments",
    "Estate, Living and Family Trusts",
    "Extractive Services, Mining and Quarrying",
    "Financial and Insurance",
    "Food Producers",
    "Gambling",
    "Government Services, Arms and State Owned Enterprises",
    "Healthcare and Medical",
    "Human Health and Social Work Activities",
    "Information and Communication",
    "Manufacturing",
    "Mining and Quarrying",
    "Other Service Activities",
    "Professional, Scientific and Technical Activities",
    "Public Administration and Defence; Compulsory Social Security",
    "Real Estate Activities",
    "Transportation and Storage",
    "Water Supply; Sewerage, Waste Management and Remediation Activities",
    "Wholesale and Retail Trade; Repair of Motor Vehicles and Motorcycles"
]

# 4.3 Member Role Options
MEMBER_ROLE_OPTIONS = [
    "",  # Empty option for unselected state
    "Chairperson",
    "Deputy Chairperson",
    "Secretary",
    "Deputy Secretary",
    "Treasurer",
    "Deputy Treasurer",
    "Member",
    "Trustee",
    "Founder",
    "Director",
    "Other (specify)"
]

# Country options for registration and other purposes
COUNTRIES = [
    "",
    "South Africa",
    "United Kingdom", 
    "United States",
    "Australia",
    "Canada",
    "Germany",
    "France",
    "Netherlands",
    "Switzerland",
    "Other"
]

# Entity types for the onboarding system (alphabetical order with "Other" last)
ENTITY_TYPES = [
    "Burial Society",
    "Charity Organisation", 
    "Church",
    "Closed Corporation",
    "Community Group",
    "Company",
    "Cultural Association",
    "Environmental Group",
    "Investment Club",
    "Partnership",
    "Savings Club",
    "School",
    "Social Club",
    "Sports Club",
    "Stokvel",
    "Trust",
    "Other"
]

def get_source_of_funds_options():
    """Get the list of Source of Funds options."""
    return SOURCE_OF_FUNDS_OPTIONS.copy()

def get_industry_options():
    """Get the list of Industry options.""" 
    return INDUSTRY_OPTIONS.copy()

def get_member_role_options():
    """Get the list of Member Role options."""
    return MEMBER_ROLE_OPTIONS.copy()

def get_countries():
    """Get the list of Country options."""
    return COUNTRIES.copy()

def get_entity_types():
    """Get the list of Entity Type options."""
    return ENTITY_TYPES.copy()

# For backwards compatibility, export the multiselect-ready versions (without empty option)
def get_source_of_funds_multiselect():
    """Get Source of Funds options for multiselect widgets (excludes empty option)."""
    return [opt for opt in SOURCE_OF_FUNDS_OPTIONS if opt != ""]

def get_industry_select():
    """Get Industry options for select widgets (includes empty option)."""
    return INDUSTRY_OPTIONS.copy()

def get_member_role_select():
    """Get Member Role options for select widgets (includes empty option)."""
    return MEMBER_ROLE_OPTIONS.copy()
