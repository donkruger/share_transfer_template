# app/pages/1_AI_Assistance.py

import streamlit as st
import sys
from pathlib import Path
import google.generativeai as genai
import json
import random
import base64

# --- PATH SETUP ---
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from app.components.sidebar import render_sidebar
from app.styling import GOOGLE_FONTS_CSS, GRADIENT_TITLE_CSS, FADE_IN_CSS, SIDEBAR_GRADIENT_CSS
from app.utils import initialize_state
from app.services.gemini_pdf_processor import GeminiPDFProcessor
from app.services.portfolio_service import PortfolioService
from app.services.selection_manager import SelectionManager

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

# Fix sidebar metrics white background issue on this page
st.markdown("""
<style>
    /* Remove white background from sidebar metrics - using correct selectors */
    [data-testid="stSidebar"] .stMetric {
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }
    
    [data-testid="stSidebar"] div[data-testid="metric-container"] {
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }
    
    /* Target the emotion-cache classes directly if needed */
    [data-testid="stSidebar"] .st-emotion-cache-0,
    [data-testid="stSidebar"] .e14qm3310,
    [data-testid="stSidebar"] .e1f1d6gn0,
    [data-testid="stSidebar"] [class*="st-emotion-cache"] {
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }
    
    /* Ensure all child elements are also transparent */
    [data-testid="stSidebar"] .stMetric * {
        background-color: transparent !important;
    }
</style>
""", unsafe_allow_html=True)

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

def process_uploaded_pdf(uploaded_file):
    """
    Process the uploaded PDF and integrate results into chat conversation.
    """
    with st.spinner("🔍 Analyzing your document..."):
        try:
            # Initialize Gemini processor
            processor = GeminiPDFProcessor(st.secrets["llm_api"]["gemini_key"])
            pdf_bytes = uploaded_file.read()
            
            # Add upload notification to chat
            st.session_state.messages.append({
                "role": "user",
                "content": f"📎 I've uploaded: {uploaded_file.name}"
            })
            
            # Analyze document
            analysis = processor.analyze_document(pdf_bytes, uploaded_file.name)
            
            # Add AI analysis to chat
            st.session_state.messages.append({
                "role": "assistant",
                "content": analysis
            })
            
            # Store PDF data for extraction
            st.session_state['pending_pdf'] = {
                'file_name': uploaded_file.name,
                'pdf_bytes': pdf_bytes,
                'processor': processor
            }
            # Reset extraction completed flag for new PDF
            st.session_state['pdf_extraction_completed'] = False
            
            # Rerun to show the analysis in chat
            st.rerun()
            
        except Exception as e:
            st.error(f"Error analyzing document: {str(e)}")
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"I encountered an error analyzing your document: {str(e)}. Please try uploading again or proceed with manual portfolio configuration."
            })
            st.rerun()

def extract_and_populate_portfolio():
    """
    Extract structured data from PDF and populate portfolio.
    """
    st.write("**FUNCTION CALLED**: extract_and_populate_portfolio() started")
    
    if 'pending_pdf' not in st.session_state:
        st.error("No PDF data available for extraction.")
        st.write("**ERROR**: No pending PDF found in session state")
        return
    
    # Check if user has completed onboarding
    if not st.session_state.get('user_name') or not st.session_state.get('user_id') or not st.session_state.get('selected_wallet_id'):
        st.warning("""
        **Please complete your setup first!**
        
        To extract and match instruments from your PDF, I need to know:
        1. Your name and user ID
        2. Your wallet context
        
        Please use the sidebar to navigate to the main search page and complete these steps first.
        """)
        return
    
    pdf_data = st.session_state['pending_pdf']
    
    with st.spinner("Extracting portfolio data..."):
        try:
            st.write("**DEBUG**: Starting PDF extraction process...")
            # Extract structured data
            extracted_data = pdf_data['processor'].process_pdf(pdf_data['pdf_bytes'])
            st.write(f"**DEBUG**: Extraction completed. Success: {extracted_data.get('success', 'Unknown')}")
            
            if not extracted_data.get('success'):
                st.error(f"Extraction failed: {extracted_data.get('error', 'Unknown error')}")
                if extracted_data.get('raw_response'):
                    with st.expander("Debug: Raw Response"):
                        st.code(extracted_data['raw_response'])
                return
            
            # ALWAYS show debug info, regardless of entries found
            with st.expander("Full Extraction Debug (Always Shown)", expanded=True):
                st.write("**Extraction Success:**", extracted_data.get('success', False))
                st.write("**Portfolio Entries Found:**", len(extracted_data.get('portfolio_entries', [])))
                st.write("**Document Type:**", extracted_data.get('document_metadata', {}).get('document_type', 'Unknown'))
                st.write("**Broker:**", extracted_data.get('document_metadata', {}).get('broker_name', 'Unknown'))
                
                # Show confidence scores
                confidence = extracted_data.get('confidence_scores', {})
                if confidence:
                    st.write("**Confidence Scores:**")
                    for key, value in confidence.items():
                        st.write(f"• {key}: {value}")
                
                # Show extraction notes
                notes = extracted_data.get('extraction_notes', [])
                if notes:
                    st.write("**Extraction Notes:**")
                    for note in notes:
                        st.write(f"• {note}")
                else:
                    st.write("**Extraction Notes:** None")
                
                # Show ALL extracted data
                st.write("**Full Extracted Data Structure:**")
                st.json(extracted_data)
                
                # Show raw response if available
                if extracted_data.get('raw_response'):
                    with st.expander("Raw Gemini Response", expanded=False):
                        st.code(extracted_data['raw_response'][:3000] + "..." if len(extracted_data['raw_response']) > 3000 else extracted_data['raw_response'])
            
            # Show detailed extraction debug info
            with st.expander("Extraction Debug Details", expanded=True):
                st.write(f"**Portfolio Entries Found:** {len(extracted_data.get('portfolio_entries', []))}")
                st.write(f"**Document Type:** {extracted_data.get('document_metadata', {}).get('document_type', 'Unknown')}")
                st.write(f"**Broker:** {extracted_data.get('document_metadata', {}).get('broker_name', 'Unknown')}")
                
                # Show confidence scores
                confidence = extracted_data.get('confidence_scores', {})
                if confidence:
                    st.write("**Confidence Scores:**")
                    for key, value in confidence.items():
                        st.write(f"• {key}: {value}")
                
                # Show raw extraction notes
                notes = extracted_data.get('extraction_notes', [])
                if notes:
                    st.write("**Extraction Notes:**")
                    for note in notes:
                        st.write(f"• {note}")
                
                # Show portfolio entries details
                entries = extracted_data.get('portfolio_entries', [])
                if entries:
                    st.write("**Extracted Portfolio Entries:**")
                    for i, entry in enumerate(entries):
                        st.write(f"{i+1}. {entry.get('instrument_name', 'N/A')} ({entry.get('ticker_symbol', 'N/A')}) - Qty: {entry.get('quantity', 'N/A')}")
                else:
                    st.warning("No portfolio entries were extracted from the PDF")
                
                # Show raw response if available for debugging
                if extracted_data.get('raw_response'):
                    with st.expander("🔍 Raw Gemini Response (Debug)", expanded=False):
                        st.code(extracted_data['raw_response'][:2000] + "..." if len(extracted_data['raw_response']) > 2000 else extracted_data['raw_response'])
            
            # Get selected instruments
            selected_instruments = SelectionManager.get_selections()
            st.write(f"Debug: Currently have {len(selected_instruments)} selected instruments")
            
            # Import to portfolio service
            import_result = PortfolioService.import_from_pdf_extraction(
                extracted_data=extracted_data,
                selected_instruments=selected_instruments
            )
            
            # Show import results
            with st.expander("Import Results", expanded=True):
                st.write(f"**Newly Selected Instruments:** {import_result.get('newly_selected_count', 0)}")
                st.write(f"**Portfolio Entries Created:** {import_result.get('imported_count', 0)}")
                st.write(f"**Unmatched Entries:** {import_result.get('unmatched_count', 0)}")
                
                if import_result.get('errors'):
                    st.write("**Errors:**")
                    for error in import_result['errors']:
                        st.write(f"• {error}")
                        
                if import_result.get('newly_selected'):
                    st.write("**Newly Selected Instruments:**")
                    for inst in import_result['newly_selected']:
                        st.write(f"• {inst.get('name')} ({inst.get('ticker', 'N/A')})")
            
            # Store results in session
            st.session_state['pdf_extraction'] = extracted_data
            st.session_state['pdf_import_result'] = import_result
            # Mark extraction as completed to hide the button
            st.session_state['pdf_extraction_completed'] = True
            
            # Add success message to chat with detailed debug info
            newly_selected = import_result.get('newly_selected_count', 0)
            imported = import_result.get('imported_count', 0)
            unmatched = import_result.get('unmatched_count', 0)
            
            # Debug information
            portfolio_entries = extracted_data.get('portfolio_entries', [])
            extraction_notes = extracted_data.get('extraction_notes', [])
            
            success_message = f"""
**Portfolio Data Extracted Successfully!**

I've processed your document and here's what I found:

**Extraction Summary:**
- Document Type: {extracted_data.get('document_metadata', {}).get('document_type', 'Unknown')}
- Broker: {extracted_data.get('document_metadata', {}).get('broker_name', 'Unknown')}
- Confidence Score: {extracted_data.get('confidence_scores', {}).get('overall', 0):.0%}

**DEBUG - Raw Extraction Results:**
- Portfolio Entries Found in JSON: {len(portfolio_entries)}
- Extraction Notes: {', '.join(extraction_notes) if extraction_notes else 'None'}

**Matching Results:**
- **Instruments Found & Selected**: {newly_selected}
- **Portfolio Entries Created**: {imported}
- **Unmatched Entries**: {unmatched}

"""
            
            # Add portfolio entries details if found
            if portfolio_entries:
                success_message += "**DEBUG - Extracted Portfolio Entries:**\n"
                for i, entry in enumerate(portfolio_entries[:5]):  # Show first 5
                    success_message += f"• {entry.get('instrument_name', 'N/A')} ({entry.get('ticker_symbol', 'N/A')}) - Qty: {entry.get('quantity', 'N/A')}\n"
            else:
                success_message += "**DEBUG - No portfolio entries were extracted from the JSON response**\n"
            
            # Add details about newly selected instruments
            if newly_selected > 0:
                success_message += """
**Instruments Automatically Added to Your Selection:**
"""
                for inst in import_result.get('newly_selected', [])[:5]:  # Show first 5
                    success_message += f"• {inst.get('name')} ({inst.get('ticker', 'N/A')})\n"
                if newly_selected > 5:
                    success_message += f"• ... and {newly_selected - 5} more\n"
            
            # Add info about unmatched entries
            if unmatched > 0:
                success_message += f"""
**Note**: {unmatched} entries from your PDF couldn't be matched to instruments in our database. 
You may need to search for these manually on the main search page.
"""
            
            success_message += """
**Next Steps:**
1. Navigate to the 'My Portfolio' page to review the pre-populated share transfer data
2. Confirm or edit the extracted values as needed
3. Complete any missing information
4. Proceed to submit your results

The system has automatically searched for and selected the instruments from your PDF that were found in our database.
            """
            
            st.session_state.messages.append({
                "role": "assistant",
                "content": success_message
            })
            
            # Clear the pending PDF
            del st.session_state['pending_pdf']
            
            st.success("Data extracted successfully! Navigate to 'My Portfolio' to review.")
            if st.button("📊 Go to My Portfolio", type="primary", use_container_width=True):
                st.switch_page("pages/2_Portfolio.py")
            
            st.rerun()
            
        except Exception as e:
            error_message = f"I encountered an error extracting data: {str(e)}. You can still proceed with manual portfolio configuration."
            
            st.error(error_message)
            st.write(f"🔍 **DEBUG**: Exception details: {type(e).__name__}: {str(e)}")
            
            # Show full traceback for debugging
            import traceback
            with st.expander("🔍 Full Error Traceback", expanded=False):
                st.code(traceback.format_exc())
            st.session_state.messages.append({
                "role": "assistant",
                "content": error_message
            })
            st.rerun()

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
    st.markdown('<h1 class="gradient-title">Portfolio Transfer Assistant</h1>', unsafe_allow_html=True)
    st.caption("An AI-powered guide that can help transfer your portfolio to EasyEquities.")

with col2:
    # Load and display random Lottie animation
    try:
        from streamlit_lottie import st_lottie
        lottie_animation = load_random_lottie()
        if lottie_animation:
            st_lottie(lottie_animation, height=100, width=100, key="ai_assistant_animation")
    except ImportError:
        st.info("AI assistant ready")

# --- PDF UPLOAD SECTION (MOVED TO TOP) ---
st.markdown("### 📄 Upload Portfolio Statement")
st.markdown("Upload your broker statement or portfolio document for automatic data extraction")

with st.container():
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=['pdf'],
        key="ai_pdf_upload",
        help="Upload your PDF and I'll analyze it for portfolio data extraction",
        accept_multiple_files=False
    )
    
    if uploaded_file:
        # Add CSS for better file upload display alignment
        st.markdown("""
        <style>
        .uploaded-file-display {
            display: flex;
            align-items: center;
            padding: 0.75rem 1rem;
            background-color: #d4edda;
            border: 1px solid #c3e6cb;
            border-radius: 0.375rem;
            color: #155724;
            margin-bottom: 1rem;
            min-height: 3rem;
        }
        .uploaded-file-display .file-icon {
            margin-right: 0.5rem;
            font-size: 1.2em;
        }
        .uploaded-file-display .file-info {
            flex: 1;
            display: flex;
            align-items: center;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Show file info with better alignment
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"""
            <div class="uploaded-file-display">
                <div class="file-icon">📎</div>
                <div class="file-info">
                    <strong>{uploaded_file.name}</strong> ({uploaded_file.size / 1024:.1f} KB uploaded)
                </div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            # Add CSS for analyze button styling
            st.markdown("""
            <style>
            .stButton > button[kind="primary"] {
                background-color: #f4942a !important;
                border-color: #f4942a !important;
            }
            .stButton > button[kind="primary"]:hover {
                background-color: #e8530f !important;
                border-color: #e8530f !important;
            }
            .stButton > button[kind="primary"]:focus {
                background-color: #f4942a !important;
                border-color: #f4942a !important;
                box-shadow: 0 0 0 0.2rem rgba(244, 148, 42, 0.25) !important;
            }
            </style>
            """, unsafe_allow_html=True)
            
            if st.button("Analyze Document", type="primary", use_container_width=True):
                process_uploaded_pdf(uploaded_file)

st.markdown("---")

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
for i, message in enumerate(st.session_state.messages):
    if message["role"] == "assistant":
        with st.chat_message("assistant", avatar=get_favicon_path()):
            st.markdown(message["content"])
            
            # Show extraction button after the latest PDF analysis (but only if extraction hasn't been completed)
            if (i == len(st.session_state.messages) - 1 and 
                'pending_pdf' in st.session_state and
                not st.session_state.get('pdf_extraction_completed', False) and
                ("extracted" in message["content"].lower() or "portfolio" in message["content"].lower())):
                
                # Add CSS for button styling
                st.markdown("""
                <style>
                .stButton > button[kind="primary"] {
                    background-color: #f4942a !important;
                    border-color: #f4942a !important;
                }
                .stButton > button[kind="primary"]:hover {
                    background-color: #e8530f !important;
                    border-color: #e8530f !important;
                }
                .stButton > button[kind="primary"]:focus {
                    background-color: #f4942a !important;
                    border-color: #f4942a !important;
                    box-shadow: 0 0 0 0.2rem rgba(244, 148, 42, 0.25) !important;
                }
                </style>
                """, unsafe_allow_html=True)
                
                if st.button("Extract & Pre-populate Portfolio", 
                           type="primary", 
                           use_container_width=True,
                           key=f"extract_portfolio_{i}"):
                    extract_and_populate_portfolio()
    else:
        with st.chat_message("user", avatar=get_user_avatar_path()):
            st.markdown(message["content"])

# --- CHAT INPUT ---
if prompt := st.chat_input("Ask anything about the Smart Instrument Finder process..."):
    generate_agent_response(prompt)
