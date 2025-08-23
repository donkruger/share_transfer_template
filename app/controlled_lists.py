"""
Controlled Lists for Entity Onboarding System

This module contains all predefined/controlled lists used throughout the application.
These lists can be easily managed and expanded as requirements change.

As per functional specification section 4:
- 4.1 Source of Funds Options
- 4.2 Industry Options  
- 4.3 Member Role Options
- 4.4 Title Options
- 4.5 Marital Status Options
- 4.6 Gender Options
- 4.6 Entity Type Options
"""

# ===== 4.1 SOURCE OF FUNDS OPTIONS =====

SOURCE_OF_FUNDS_OPTIONS = [
    "",  # Empty option for selectbox
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

def get_source_of_funds_options():
    """Get the list of Source of Funds options."""
    return SOURCE_OF_FUNDS_OPTIONS.copy()

def get_source_of_funds_multiselect():
    """Get Source of Funds options for selectbox widgets (excludes empty option).
    
    Note: This function name is kept for backward compatibility but now supports single select.
    """
    return [opt for opt in SOURCE_OF_FUNDS_OPTIONS if opt != ""]


# ===== 4.2 INDUSTRY OPTIONS =====

INDUSTRY_OPTIONS = [
    "",  # Empty option for selectbox
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
    "High Transaction Volume Import/Export Companies",
    "High Value Goods Dealers (Including Motor Vehicle Dealers, Art Dealers, Luxury Goods/Services Etc)",
    "Household Goods & Home Construction Materials",
    "Industrial Engineering",
    "Industrial Metals",
    "Information Technology, Communication And Telecoms",
    "Legal Practitioner",
    "Manufacturing",
    "Minor/Scholar",
    "Media",
    "Money Transfer / Service Businesses",
    "Motor Wholesale, Retail Trade And Repair",
    "Non Equity Investment Instruments",
    "Non Profit Organisation / Regulated Charity",
    "Non-Government Organisation (NGO)",
    "Oil & Gas Producers / Suppliers",
    "Pawn Brokers/Second Hand Dealers",
    "Pharmaceuticals & Biotechnology",
    "Precious Metals And Stone Dealers",
    "Professional Sport",
    "Public Finance Management Act Schedule",
    "Real Estate And Property Services",
    "Retired",
    "Scrap Metal Industry",
    "Shell Banking",
    "Tobacco",
    "Transport, Storage, Courier And Freight",
    "Travel, Tourism, Accommodation And Food Services",
    "Unemployed",
    "Virtual Currencies"
]

def get_industry_options():
    """Get the list of Industry options.""" 
    return INDUSTRY_OPTIONS.copy()

def get_industry_select():
    """Get Industry options for select widgets (includes empty option)."""
    return INDUSTRY_OPTIONS.copy()


# ===== 4.3 MEMBER ROLE OPTIONS =====

MEMBER_ROLE_OPTIONS = [
    "",  # Empty option for selectbox
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

def get_member_role_options():
    """Get the list of Member Role options."""
    return MEMBER_ROLE_OPTIONS.copy()

def get_member_role_select():
    """Get Member Role options for select widgets (includes empty option)."""
    return MEMBER_ROLE_OPTIONS.copy()


# ===== 4.4 TITLE OPTIONS =====

TITLE_OPTIONS = [
    "",
    "Mr",
    "Mrs",
    "Ms", 
    "Dr",
    "Prof",
    "Adv"
]

def get_title_options():
    """Returns list of title options for Authorised Representative."""
    return TITLE_OPTIONS.copy()


# ===== 4.5 MARITAL STATUS OPTIONS =====

MARITAL_STATUS_OPTIONS = [
    "",
    "Single",
    "Married"
]

def get_marital_status_options():
    """Returns list of marital status options for Authorised Representative."""
    return MARITAL_STATUS_OPTIONS.copy()


# ===== 4.6 GENDER OPTIONS =====

GENDER_OPTIONS = [
    "",
    "Male",
    "Female"
]

def get_gender_options():
    """Returns list of gender options for Authorised Representative."""
    return GENDER_OPTIONS.copy()


# ===== 4.6 ENTITY TYPE OPTIONS =====

ENTITY_TYPES = [
    "Burial Society",
    "Charity Organisation", 
    "Church",
    "Closed Corporation",
    "Company",
    "Community Group",
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
    "Other"  # Always last
]

def get_entity_types():
    """Get the list of Entity Type options."""
    return ENTITY_TYPES.copy()


# ===== COUNTRIES =====

def _load_countries_from_csv():
    """Load countries from CSV file and return sorted list with South Africa first."""
    import csv
    from pathlib import Path
    
    try:
        # Path to the CSV file
        csv_path = Path(__file__).parent / "common_form_sections" / "CountryList.csv"
        
        countries = [""]  # Empty option first
        
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            country_names = []
            
            for row in reader:
                country_name = row.get('Country Name', '').strip()
                if country_name and country_name != '':  # Skip empty rows
                    country_names.append(country_name)
            
            # Sort alphabetically but put South Africa first (after empty option)
            country_names.sort()
            
            # Ensure South Africa is at the top of the list (after empty option)
            if "South Africa" in country_names:
                country_names.remove("South Africa")
                countries.append("South Africa")
            
            # Add all other countries
            countries.extend(country_names)
            
        return countries
        
    except Exception as e:
        # Fallback to basic country list if CSV loading fails
        print(f"Warning: Could not load countries from CSV: {e}")
        return [
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

# Load countries once at module level
COUNTRIES = _load_countries_from_csv()

def get_countries():
    """Get the comprehensive list of Country options with South Africa prioritized."""
    return COUNTRIES.copy()