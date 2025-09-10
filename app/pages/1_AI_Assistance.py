# app/pages/1_AI_Assistance.py

import streamlit as st
import sys
from pathlib import Path
import google.generativeai as genai
import json
import random

# --- PATH SETUP ---
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from app.components.sidebar import render_sidebar
from app.styling import GOOGLE_FONTS_CSS, GRADIENT_TITLE_CSS, FADE_IN_CSS, SIDEBAR_GRADIENT_CSS
from app.utils import initialize_state

def get_favicon_path() -> str:
    """Returns the absolute path to the favicon SVG, checking for existence."""
    try:
        # Correct path from the pages directory
        favicon_path = Path(__file__).resolve().parent.parent.parent / "assets" / "logos" / "favicon.svg"
        if favicon_path.exists():
            return str(favicon_path)
    except Exception:
        pass
    # Return an empty string if not found to let Streamlit use its default
    return ""

# --- PAGE CONFIG ---
favicon_path_str = get_favicon_path()
st.set_page_config(
    page_title="AI Assistance - Smart Instrument Finder",
    page_icon=favicon_path_str if favicon_path_str else "AI",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- INITIALIZE STATE ---
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Apply styling
st.markdown(GOOGLE_FONTS_CSS, unsafe_allow_html=True)
st.markdown(GRADIENT_TITLE_CSS, unsafe_allow_html=True)
st.markdown(FADE_IN_CSS, unsafe_allow_html=True)

# Apply sidebar gradient styling to match main page
st.markdown(SIDEBAR_GRADIENT_CSS, unsafe_allow_html=True)

# Additional comprehensive spacing removal for this page
st.markdown("""
<style>
    /* Ensure gradient title sits flush at top */
    .gradient-title {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }
    
    /* Remove any remaining top spacing */
    .main .block-container > div:first-child {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- GEMINI API CONFIGURATION ---
try:
    # Get the API key from Streamlit secrets
    GEMINI_API_KEY = st.secrets["llm_api"]["gemini_key"]
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except (KeyError, FileNotFoundError):
    st.error("❗ Gemini API key not found. Please add it to your `secrets.toml` file.")
    st.stop()

# --- LOTTIE ANIMATION LOADING ---
def load_random_lottie():
    """Loads a random Lottie animation from the available JSON files."""
    try:
        lottie_dir = Path(__file__).resolve().parent.parent.parent / "assets" / "logos" / "lottie-jsons"
        lottie_files = list(lottie_dir.glob("*.json"))
        
        if not lottie_files:
            return None
            
        # Randomly select a Lottie file
        selected_file = random.choice(lottie_files)
        
        with open(selected_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        st.warning(f"Could not load animation: {e}")
        return None

# --- AVATAR LOADING ---
def get_user_avatar_path():
    """Returns the path to the user profile SVG avatar."""
    profile_path = Path(__file__).resolve().parent.parent.parent / "assets" / "logos" / "profile.svg"
    if profile_path.exists():
        return str(profile_path)
    else:
        # Fallback to emoji if file doesn't exist
        return "User"

# --- KNOWLEDGE BASE LOADING ---
def load_knowledge_base():
    """Loads the knowledge base from the markdown file."""
    try:
        # Correctly navigate to the project root to find the file
        knowledge_path = Path(__file__).resolve().parent.parent.parent / "instrument_finder_knowledge_base.md"
        with open(knowledge_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        # Fallback to a basic knowledge base if file not found
        return """
        # Smart Instrument Finder Knowledge Base
        
        ## About the Application
        The Smart Instrument Finder helps users discover if instruments from their external investment portfolio are available within the EasyEquities ecosystem.
        
        ## Search Features
        - Multi-field search: Search by instrument name, ticker symbol, or ISIN code
        - Fuzzy matching: Find instruments even with partial or misspelled names
        - Wallet filtering: See only instruments available in your selected wallet
        - Real-time results: Instant search through thousands of instruments
        
        ## Available Wallets
        - ZAR: South African Rand accounts
        - USD: US Dollar accounts  
        - TFSA: Tax-Free Savings Account
        - RA: Retirement Annuity
        - GBP/EUR/AUD: Foreign currency accounts
        
        ## Search Tips
        - Use full company names for better results
        - Try ticker symbols for exact matches
        - Use ISIN codes for precise identification
        - Adjust fuzzy threshold in search options
        - Try different wallet contexts if no results found
        """

KNOWLEDGE_BASE = load_knowledge_base()

# --- SYSTEM PROMPT ---
SYSTEM_PROMPT = f"""
You are a specialist assistant for Smart Instrument Finder. Your role is to answer questions pertaining to instrument searching and portfolio discovery.
- If the answer is not in the knowledge base, state: "I'm sorry, but that information is not available in my knowledge base."

**Knowledge Base:**
---
{KNOWLEDGE_BASE}
---
"""

# Render the main sidebar
render_sidebar()

def generate_agent_response(prompt: str):
    """Generates and displays the agent's response, updating session state."""
    # Add user message to session state
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message
    with st.chat_message("user", avatar=get_user_avatar_path()):
        st.markdown(prompt)

    # Generate and display assistant response
    with st.chat_message("assistant", avatar=get_favicon_path()):
        message_placeholder = st.empty()
        full_response = ""
        try:
            conversation_history = [
                {'role': 'user', 'parts': [SYSTEM_PROMPT]}
            ]
            for msg in st.session_state.messages:
                conversation_history.append({'role': msg['role'], 'parts': [msg['content']]})
            
            response = model.generate_content(conversation_history)
            full_response = response.text
            message_placeholder.markdown(full_response)
        except Exception as e:
            st.error(f"An error occurred with the AI model: {e}")
            full_response = "Sorry, I encountered an error. Please try again."
            message_placeholder.markdown(full_response)
    
    # Add assistant response to session state
    st.session_state.messages.append({"role": "assistant", "content": full_response})

# --- CHATBOT UI ---
# Create two columns for title and animation
col1, col2 = st.columns([3, 1])

with col1:
    st.markdown('<h1 class="gradient-title">Smart Search Assistant</h1>', unsafe_allow_html=True)
    st.caption("Your AI-powered guide to finding instruments in the EasyEquities ecosystem.")

with col2:
    # Load and display random Lottie animation
    try:
        from streamlit_lottie import st_lottie
        lottie_animation = load_random_lottie()
        if lottie_animation:
            st_lottie(lottie_animation, height=100, width=100, key="ai_assistant_animation")
    except ImportError:
        st.info("AI assistant ready")

# Show current context information
if st.session_state.get("user_name") or st.session_state.get("selected_instruments"):
    with st.expander("Current Session Context", expanded=False):
        if st.session_state.get("user_name"):
            st.write(f"**User:** {st.session_state.get('user_name')}")
        if st.session_state.get("selected_wallet"):
            st.write(f"**Wallet:** {st.session_state.get('selected_wallet')}")
        
        current_results = st.session_state.get("current_results", [])
        selected_instruments = st.session_state.get("selected_instruments", [])
        
        if current_results:
            st.write(f"**Current Results:** {len(current_results)} instruments found")
        if selected_instruments:
            st.write(f"**Selected:** {len(selected_instruments)} instruments")
            
        if st.session_state.get("search_history"):
            st.write(f"**Total Searches:** {len(st.session_state.search_history)}")

# Display past messages from session state
for message in st.session_state.messages:
    if message["role"] == "assistant":
        with st.chat_message("assistant", avatar=get_favicon_path()):
            st.markdown(message["content"])
    else:
        with st.chat_message("user", avatar=get_user_avatar_path()):
            st.markdown(message["content"])

# --- USER INPUT & AGENT RESPONSE ---
if prompt := st.chat_input("Ask anything about the Smart Instrument Finder process..."):
    generate_agent_response(prompt)

# --- QUICK ACTIONS REMOVED ---
# Quick Questions section has been removed for cleaner UI