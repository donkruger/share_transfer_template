# app/utils.py
"""
Smart Instrument Finder - Utility Functions
Enhanced session state management with namespace isolation and robust persistence.
"""

import base64
import re
from pathlib import Path
from typing import List, Any, Dict, Optional
import streamlit as st
import datetime
import pandas as pd
import uuid

def current_namespace() -> str:
    """Return current namespace for component isolation."""
    return "instrument_finder"

def ns_key(namespace: str, key: str) -> str:
    """Create namespaced key for session state isolation."""
    return f"{namespace}__{key}"

def generate_session_id() -> str:
    """Generate unique session identifier for tracking."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"session_{timestamp}_{str(uuid.uuid4())[:8]}"

def initialize_state():
    """
    Initialize all required session state variables with namespace isolation.
    Implements enterprise-grade session management patterns with enhanced selection persistence.
    """
    if 'state_initialized' not in st.session_state:
        # User information
        st.session_state.setdefault("user_name", "")
        st.session_state.setdefault("user_id", "") 
        st.session_state.setdefault("selected_wallet", "All Wallets")
        st.session_state.setdefault("selected_wallet_id", "all")
        
        # Search functionality (temporary state - cleared on new search)
        st.session_state.setdefault("search_history", [])
        st.session_state.setdefault("current_results", [])
        st.session_state.setdefault("last_search_query", "")
        st.session_state.setdefault("search_preferences", {})
        
        # Selection functionality (persistent state - survives searches)
        st.session_state.setdefault("selected_instruments", [])  # PERSISTENT across searches
        st.session_state.setdefault("selection_metadata", {      # Enhanced selection tracking
            "total_selected": 0,
            "selection_timestamps": {},   # When each instrument was selected
            "selection_sources": {},      # Which search query led to each selection
            "last_modified": None
        })
        
        # User workflow state
        st.session_state.setdefault("selection_mode", "accumulate")  # "accumulate" | "replace" | "review"
        st.session_state.setdefault("show_selection_panel", True)    # Whether to show persistent selection panel
        st.session_state.setdefault("show_selection_details", False) # Whether to show detailed selection list
        
        # Multi-page navigation
        st.session_state.setdefault("messages", [])  # AI Assistant chat
        st.session_state.setdefault("submission_notes", "")
        
        # NEW: Portfolio management state (persistent like selections)
        st.session_state.setdefault("portfolio_entries", {})
        st.session_state.setdefault("portfolio_metadata", {
            'default_platform': 'EE',
            'default_broker_from': '9',
            'default_broker_to': '9',
            'last_updated': None
        })
        st.session_state.setdefault("portfolio_form_data", {})
        
        # Data caching
        st.session_state.setdefault("instruments_df", None)
        st.session_state.setdefault("wallet_config", None)
        
        # Session metadata  
        st.session_state.setdefault("session_id", generate_session_id())
        st.session_state.setdefault("page_visits", {
            "main": 0, 
            "ai_assistance": 0, 
            "submit": 0,
            "portfolio": 0  # NEW: Track portfolio page visits
        })
        
        # Selection management flags
        st.session_state.setdefault("confirm_clear_selections", False)
        st.session_state.setdefault("confirm_clear_all", False)
        
        # NEW: Portfolio management flags
        st.session_state.setdefault("confirm_clear_portfolio", False)
        
        st.session_state.state_initialized = True

@st.cache_data
def load_instruments_data(csv_path: str) -> pd.DataFrame:
    """
    Load and preprocess instruments CSV data with caching.
    Handles large datasets efficiently.
    """
    try:
        df = pd.read_csv(csv_path, low_memory=False)

        # Normalize column names for easier programmatic access
        columns = list(df.columns)

        # Data cleaning and preprocessing
        df['Name'] = df.get('Name', '').fillna('').astype(str)
        df['Ticker'] = df.get('Ticker', '').fillna('').astype(str)
        df['Exchange'] = df.get('Exchange', '').fillna('').astype(str)
        df['ContractCode'] = df.get('ContractCode', '').fillna('').astype(str)
        df['ISINCode'] = df.get('ISINCode', '').fillna('').astype(str)

        df['ActiveData'] = pd.to_numeric(df.get('ActiveData', 0), errors='coerce').fillna(0)

        # Build accountFiltersArray from 22 wrapper columns when missing or empty
        # Identify wrapper columns that start with 'accountFilters/'
        wrapper_cols = [c for c in columns if c.startswith('accountFilters/')]

        def derive_filters_array(row) -> str:
            codes: list[str] = []
            for c in wrapper_cols:
                val = row.get(c)
                try:
                    ival = int(val)
                except Exception:
                    continue
                if ival and ival != 0:
                    codes.append(str(ival))
            # Deduplicate while preserving order
            seen = set()
            deduped: list[str] = []
            for code in codes:
                if code not in seen:
                    seen.add(code)
                    deduped.append(code)
            return ','.join(deduped)

        # If accountFiltersArray exists, keep non-empty; else derive
        if 'accountFiltersArray' in df.columns:
            df['accountFiltersArray'] = df['accountFiltersArray'].fillna('').astype(str)
            if wrapper_cols:
                derived = df.apply(derive_filters_array, axis=1)
                df.loc[df['accountFiltersArray'].str.strip() == '', 'accountFiltersArray'] = derived[df['accountFiltersArray'].str.strip() == '']
        else:
            if wrapper_cols:
                df['accountFiltersArray'] = df.apply(derive_filters_array, axis=1)
            else:
                df['accountFiltersArray'] = ''

        # Filter active instruments only
        active_df = df[df['ActiveData'] != 0].copy()
        
        return active_df
        
    except Exception as e:
        st.error(f"Error loading instruments data: {e}")
        return pd.DataFrame()

def add_to_search_history(query: str, results_count: int, wallet: str):
    """Track search history for analytics and user experience."""
    if 'search_history' not in st.session_state:
        st.session_state.search_history = []
    
    search_entry = {
        'timestamp': datetime.datetime.now().isoformat(),
        'query': query,
        'results_count': results_count,
        'wallet': wallet,
        'session_id': st.session_state.get('session_id', 'unknown')
    }
    
    st.session_state.search_history.append(search_entry)
    
    # Keep only last 50 searches to manage memory
    if len(st.session_state.search_history) > 50:
        st.session_state.search_history = st.session_state.search_history[-50:]

def clear_search_results():
    """Clear current search results ONLY, preserve selections."""
    st.session_state.current_results = []
    # ✅ DO NOT clear selected_instruments - selections persist across searches

def convert_date_to_excel_format(date_string: str) -> str:
    """Convert YYYY-MM-DD to YYYY/MM/DD format for Excel Date column."""
    if isinstance(date_string, str) and len(date_string) == 10:
        return date_string.replace('-', '/')
    return date_string

def validate_portfolio_entry(portfolio_data: Dict) -> List[str]:
    """Validate portfolio entry using existing validation patterns."""
    errors = []
    
    required_fields = [
        ('trust_account_id', 'Trust Account ID'),
        ('quantity', 'Quantity'),
        ('base_cost', 'Base Cost'),
        ('settlement_date', 'Settlement Date'),
        ('last_price', 'Last Price'),
        ('broker_from', 'Source Broker'),
        ('broker_to', 'Destination Broker')
    ]
    
    for field, display_name in required_fields:
        if field not in portfolio_data or portfolio_data[field] in [None, '', 0]:
            if field == 'quantity':
                continue  # Quantity can be 0 or negative
            errors.append(f"{display_name} is required")
    
    # Quantity validation (can be negative but not zero for transfers)
    quantity = portfolio_data.get('quantity', 0)
    if quantity == 0:
        errors.append("Quantity cannot be zero for transfers")
    
    return errors

def get_favicon_path():
    """Returns the path to the favicon for chat avatars."""
    favicon_path = Path(__file__).resolve().parent.parent / "assets" / "logos" / "favicon.svg"
    return str(favicon_path) if favicon_path.exists() else ""

def persist_widget(widget_func, label: str, state_key: str, **kwargs):
    """Enhanced widget persistence with error handling."""
    tmp_key = f"_{state_key}"
    
    # Initialize temp key from persistent state
    if tmp_key not in st.session_state and state_key in st.session_state:
        st.session_state[tmp_key] = st.session_state[state_key]

    def _store_value():
        if tmp_key in st.session_state:
            st.session_state[state_key] = st.session_state[tmp_key]

    try:
        widget_func(label, key=tmp_key, on_change=_store_value, **kwargs)
        return st.session_state.get(state_key)
    except Exception as e:
        st.error(f"Widget error for {label}: {e}")
        return st.session_state.get(state_key)

def persist_text_input(label: str, state_key: str, **kwargs) -> str:
    return persist_widget(st.text_input, label, state_key, **kwargs) or ""

def persist_selectbox(label: str, state_key: str, **kwargs) -> Any:
    return persist_widget(st.selectbox, label, state_key, **kwargs)

def persist_text_area(label: str, state_key: str, **kwargs) -> str:
    return persist_widget(st.text_area, label, state_key, **kwargs) or ""

def _legacy_initialize_state():
    """Initializes all required session state variables using setdefault."""
    if 'state_initialized' not in st.session_state:
        
        # Calculate favicon path once and store it
        favicon_path = Path(__file__).resolve().parent.parent / "assets" / "logos" / "favicon.svg"
        
        # Define all default values in a dictionary
        defaults = {
            # New entity onboarding system
            "messages": [],
            "accept": False,
            "entity_type": ENTITY_TYPES[0],
            "entity_user_id": "",
            "entity_display_name": "",
            "s1_name": "", "s1_desig": "",
            "s2_name": "", "s2_desig": "",
            # Development mode toggle for testing
            "dev_mode": False,
            "dev_recipient_email": "don.kruger123@gmail.com",
            # Favicon path for consistent use across pages
            "favicon_path": str(favicon_path),
            
            # Legacy DDQ fields (kept for backward compatibility during transition)
            "reg_name": "", "trading_name": "", "reg_no": "", "fsp_no": "",
            "aum": 0.0, "phys_addr": "", "bus_overview": "", "inv_phil": "",
            "research": "", "compliance_proc": "", "regulatory_matters": "",
            "final_notes": "",
            "n_auth": 1, "n_dir": 1, "n_ubo": 0, "n_staff": 1, "n_ic": 1,
            # Completion step tracking
            "step_1_complete": False, "step_2_complete": False, "step_3_complete": False,
            "step_4_complete": False, "step_5_complete": False, "step_6_complete": False,
            "step_7_complete": False, "step_8_complete": False,
        }
        
        # Use setdefault to initialize keys without overwriting existing ones
        for key, value in defaults.items():
            st.session_state.setdefault(key, value)
        
        st.session_state.state_initialized = True
    
    # Always run cleanup to handle legacy values
    _cleanup_legacy_values()

def is_dev_mode() -> bool:
    """Check if development mode is enabled."""
    return st.session_state.get("dev_mode", False)

def toggle_dev_mode():
    """Toggle development mode on/off."""
    st.session_state.dev_mode = not st.session_state.get("dev_mode", False)

def persist_widget(widget_func, label: str, state_key: str, **kwargs):
    """A generic helper to make any widget's state survive page switches."""
    tmp_key = f"_{state_key}"  # Temporary key for the widget

    # On the first run, copy the value from the permanent key to the temporary key
    if tmp_key not in st.session_state and state_key in st.session_state:
        st.session_state[tmp_key] = st.session_state[state_key]

    # The callback to copy the widget's value to the permanent key
    def _store_value():
        if tmp_key in st.session_state:
            st.session_state[state_key] = st.session_state[tmp_key]

    # Create the widget with the temporary key and the callback
    widget_func(label, key=tmp_key, on_change=_store_value, **kwargs)

    # Return the value from the permanent key
    return st.session_state.get(state_key)

# Specific helpers for each widget type
def persist_text_input(label: str, state_key: str, **kwargs):
    """Persistent text input widget."""
    return persist_widget(st.text_input, label, state_key, **kwargs)

def persist_text_area(label: str, state_key: str, **kwargs):
    """Persistent text area widget."""
    return persist_widget(st.text_area, label, state_key, **kwargs)

def persist_number_input(label: str, state_key: str, **kwargs):
    """Persistent number input widget."""
    return persist_widget(st.number_input, label, state_key, **kwargs)

def persist_date_input(label: str, state_key: str, **kwargs):
    """Persistent date input widget."""
    return persist_widget(st.date_input, label, state_key, **kwargs)
    
def persist_selectbox(label: str, state_key: str, **kwargs):
    """Persistent selectbox widget."""
    return persist_widget(st.selectbox, label, state_key, **kwargs)

def persist_checkbox(label: str, state_key: str, **kwargs):
    """Persistent checkbox widget."""
    return persist_widget(st.checkbox, label, state_key, **kwargs)

def persist_file_uploader(label: str, state_key: str, **kwargs):
    """Persistent file uploader widget with max file size enforcement.

    Enforces a per-file size limit (default 4 MB). Oversized files are ignored
    and a user-facing error is displayed. For multiple uploads, oversized files
    are filtered out while valid files are retained.
    
    Note: File uploaders use direct session state management to avoid 
    StreamlitValueAssignmentNotAllowedError in cloud environments.
    """
    def _get_max_upload_mb() -> int:
        try:
            # Optional override via secrets: [app] max_upload_mb = 4
            return int(st.secrets.get("app", {}).get("max_upload_mb", 4))
        except Exception:
            return 4

    def _file_size_bytes(uploaded_file) -> int | None:
        """Get file size in bytes safely."""
        if uploaded_file is None:
            return None
        try:
            size_attr = getattr(uploaded_file, "size", None)
            if isinstance(size_attr, int):
                return size_attr
        except Exception:
            pass
        try:
            # Prefer buffer size if available
            buf = uploaded_file.getbuffer()  # type: ignore[attr-defined]
            return getattr(buf, "nbytes", None) or len(buf)
        except Exception:
            try:
                return len(uploaded_file.getvalue())
            except Exception:
                return None

    # File uploaders don't need the persist_widget pattern - use direct approach
    # to avoid session state assignment conflicts in Streamlit Cloud
    
    # Create a unique key for the widget to avoid conflicts
    widget_key = f"_upload_{state_key}"
    
    # Render the file uploader widget directly
    uploaded_files = st.file_uploader(label, key=widget_key, **kwargs)
    
    # Process and validate uploaded files
    max_mb = _get_max_upload_mb()
    limit_bytes = max_mb * 1024 * 1024
    accept_multiple = bool(kwargs.get("accept_multiple_files", False))
    
    if accept_multiple:
        if uploaded_files:
            valid_files = []
            oversized: list[tuple[str, float]] = []
            for f in uploaded_files:
                if f is None:
                    continue
                size_bytes = _file_size_bytes(f)
                if size_bytes is not None and size_bytes > limit_bytes:
                    oversized.append((getattr(f, "name", "<file>"), size_bytes / (1024 * 1024)))
                else:
                    valid_files.append(f)
            
            if oversized:
                names = ", ".join([f"{n} ({sz:.2f} MB)" for n, sz in oversized])
                st.error(f"The following files exceed the {max_mb} MB limit and were ignored: {names}")
            
            # Store valid files in session state
            if valid_files:
                st.session_state[state_key] = valid_files
            elif state_key in st.session_state:
                # Clear the state if no valid files
                st.session_state[state_key] = None
        elif uploaded_files is None and state_key in st.session_state:
            # File uploader returned None - keep existing state
            pass  # Don't modify existing uploads
    else:
        # Single file upload
        if uploaded_files is not None:
            size_bytes = _file_size_bytes(uploaded_files)
            if size_bytes is not None and size_bytes > limit_bytes:
                mb = size_bytes / (1024 * 1024)
                name = getattr(uploaded_files, "name", "<file>")
                st.error(f"File exceeds the {max_mb} MB limit: {name} ({mb:.2f} MB). Please upload a smaller file.")
                # Don't store oversized files
                if state_key in st.session_state:
                    st.session_state[state_key] = None
            else:
                # Store valid file
                st.session_state[state_key] = uploaded_files
        elif uploaded_files is None and state_key not in st.session_state:
            # Initialize state for new uploader
            st.session_state[state_key] = None

    return st.session_state.get(state_key)

def persist_multiselect(label: str, state_key: str, **kwargs):
    """Persistent multiselect widget."""
    return persist_widget(st.multiselect, label, state_key, **kwargs)

def repeat_prefix(idx: int, label: str) -> str:
    """Prefix repeated-section labels with an enumerator (1-based)."""
    return f"**{label} #{idx+1}**"

def text_wrap(text: str, width: int) -> List[str]:
    """Rudimentary word wrap for PDF lines to prevent overflow."""
    words, out, line = str(text).split(), [], ""
    for w in words:
        if len(line) + len(w) + 1 > width:
            out.append(line)
            line = w
        else:
            line = f"{line} {w}".strip()
    if line:
        out.append(line)
    return out

def get_completion_progress() -> tuple[int, float]:
    """Calculate completion progress for DDQ steps.
    
    Returns:
        tuple: (completed_steps, progress_percentage)
    """
    completion_steps = [
        "step_1_complete", "step_2_complete", "step_3_complete", "step_4_complete",
        "step_5_complete", "step_6_complete", "step_7_complete", "step_8_complete"
    ]
    
    completed_steps = sum(st.session_state.get(step, False) for step in completion_steps)
    progress_percentage = (completed_steps / 8) * 100
    
    return completed_steps, progress_percentage

def get_favicon_path() -> str:
    """Get the favicon path from session state.
    
    Returns:
        str: Path to the favicon file
    """
    return st.session_state.get("favicon_path", "")

def svg_image_html(path: Path, width: int = 200) -> str:
    """Return an <img> tag with the SVG at the supplied width encoded as base64."""
    try:
        svg_txt = path.read_text(encoding="utf-8")
        encoded = base64.b64encode(svg_txt.encode()).decode()
        return (
            f'<img src="data:image/svg+xml;base64,{encoded}" '
            f'width="{width}" style="margin-bottom:1rem;" />'
        )
    except Exception:
        # If the file cannot be read, return empty string to avoid breaking the UI
        return "" 