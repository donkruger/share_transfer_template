# app/pages/1_AI_Assistance.py

import streamlit as st
import sys
from pathlib import Path
import google.generativeai as genai
import json
import random
from streamlit_lottie import st_lottie

# --- PATH SETUP ---
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app.components.sidebar import render_sidebar
from app.styling import GOOGLE_FONTS_CSS, GRADIENT_TITLE_CSS, FADE_IN_CSS
from app.utils import initialize_state, get_favicon_path



# --- PAGE CONFIG ---
favicon_path = Path(__file__).resolve().parent.parent.parent / "assets" / "logos" / "favicon.svg"
st.set_page_config(
    page_title="AI Assistance - Entity Onboarding",
    page_icon=str(favicon_path),
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- INITIALIZE STATE ---
initialize_state()

# Apply styling
st.markdown(GOOGLE_FONTS_CSS, unsafe_allow_html=True)
st.markdown(GRADIENT_TITLE_CSS, unsafe_allow_html=True)
st.markdown(FADE_IN_CSS, unsafe_allow_html=True)

# --- GEMINI API CONFIGURATION ---
try:
    # Get the API key from Streamlit secrets
    GEMINI_API_KEY = st.secrets["llm_api"]["gemini_key"]
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except (KeyError, FileNotFoundError):
    st.error("❗ Gemini API key not found. Please add it to your `secrets.toml` file.")
    st.stop()

# --- KNOWLEDGE BASE LOADING ---
def load_knowledge_base():
    """Loads the knowledge base from the markdown file."""
    try:
        # Correctly navigate to the project root to find the file
        knowledge_path = Path(__file__).resolve().parent.parent.parent / "knowledge_set.md"
        with open(knowledge_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        st.error("`knowledge_set.md` not found in the project root.")
        return ""

KNOWLEDGE_BASE = load_knowledge_base()

# --- AVATAR LOADING ---
def get_user_avatar_path():
    """Returns the path to the user profile SVG avatar."""
    return str(Path(__file__).resolve().parent.parent.parent / "assets" / "logos" / "profile.svg")

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
        st.error(f"Error loading Lottie animation: {e}")
        return None

# --- SYSTEM PROMPT ---
SYSTEM_PROMPT = f"""
You are a specialist assistant for Satrix entity oboarding. Your role is to answer questions pertaining to an entity onboarding journey. 
- If the answer is not in the knowledge base, state: "I'm sorry, but that information is not available in my knowledge base."

**Knowledge Base:**
---
{KNOWLEDGE_BASE}
---
"""

# Render the main sidebar
render_sidebar()

# --- CHATBOT UI ---
# Create two columns for title and animation
col1, col2 = st.columns([3, 1])

with col1:
    st.markdown('<h1 class="gradient-title">Entity Onboarding Assistant</h1>', unsafe_allow_html=True)
    st.caption("Your AI-powered guide to the Entity Onboarding process.")

with col2:
    # Load and display random Lottie animation
    lottie_animation = load_random_lottie()
    if lottie_animation:
        st_lottie(lottie_animation, height=100, width=100, key="ai_assistant_animation")

# Display past messages from session state
for message in st.session_state.messages:
    if message["role"] == "assistant":
        with st.chat_message("assistant", avatar=get_favicon_path()):
            st.markdown(message["content"])
    else:
        with st.chat_message("user", avatar=get_user_avatar_path()):
            st.markdown(message["content"])

# --- USER INPUT & AGENT RESPONSE ---
if prompt := st.chat_input("Ask anything about the Satrix Entity Onboarding process..."):
    # Add user message to session state and display it
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=get_user_avatar_path()):
        st.markdown(prompt)

    # --- GENERATE AGENT RESPONSE ---
    with st.chat_message("assistant", avatar=get_favicon_path()):
        message_placeholder = st.empty()
        full_response = ""
        try:
            # Construct the full conversation history for the model
            conversation_history = [
                {'role': 'user', 'parts': [SYSTEM_PROMPT]}
            ]
            # Add previous messages, ensuring the format is correct
            for msg in st.session_state.messages:
                 conversation_history.append({'role': msg['role'], 'parts': [msg['content']]})
            # Generate content using the model
            response = model.generate_content(conversation_history)
            # Stream the response to the UI
            full_response = response.text
            message_placeholder.markdown(full_response)
        except Exception as e:
            st.error(f"An error occurred with the AI model: {e}")
            full_response = "Sorry, I encountered an error. Please try again."
            message_placeholder.markdown(full_response)
    # Add the final assistant response to session state
    st.session_state.messages.append({"role": "assistant", "content": full_response})
