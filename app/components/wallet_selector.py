# app/components/wallet_selector.py

import streamlit as st
from typing import Dict, List, Tuple, Optional
import json
from pathlib import Path

class WalletSelectorComponent:
    """
    Enhanced wallet selection component with display names
    and currency information.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            config_path = Path(__file__).parent.parent / "data" / "wallet_specifications.json"
        self.wallet_config = self._load_wallet_config(config_path)
    
    def _load_wallet_config(self, config_path: str) -> Dict:
        """Load wallet configuration from JSON file."""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception:
            # Fallback configuration
            return {
                "wallet_mappings": {
                    "2": {"name": "ZAR", "display_name": "EasyEquities ZAR", "currency": "ZAR", "active": True},
                    "3": {"name": "TFSA", "display_name": "Tax-Free Savings Account", "currency": "ZAR", "active": True},
                    "9": {"name": "RA", "display_name": "Retirement Annuity", "currency": "ZAR", "active": True},
                    "10": {"name": "USD", "display_name": "EasyEquities USD", "currency": "USD", "active": True}
                },
                "default_wallets": ["ZAR", "USD", "TFSA", "RA"]
            }
    
    def render_selector(self, key: str = "wallet_selector") -> Tuple[str, str]:
        """
        Render wallet selector and return (wallet_name, wallet_id).
        """
        st.markdown("### Wallet Selection")
        
        # Get active wallets
        wallet_options = [
            (wallet_id, info) 
            for wallet_id, info in self.wallet_config["wallet_mappings"].items() 
            if info.get("active", True)
        ]
        
        # Create display labels
        wallet_labels = []
        wallet_ids = []
        
        for wallet_id, info in wallet_options:
            currency = info.get("currency", "")
            currency_display = f" ({currency})" if currency else ""
            label = f"{info['name']} - {info['display_name']}{currency_display}"
            wallet_labels.append(label)
            wallet_ids.append(wallet_id)
        
        if not wallet_options:
            st.error("No active wallets found in configuration.")
            return "", ""
        
        # Wallet selector
        selected_index = st.selectbox(
            "Select Wallet Context",
            range(len(wallet_options)),
            format_func=lambda x: wallet_labels[x],
            key=f"{key}_index",
            help="Choose the wallet context for your search"
        )
        
        selected_wallet_id = wallet_ids[selected_index]
        selected_wallet_info = wallet_options[selected_index][1]
        selected_wallet_name = selected_wallet_info["name"]
        
        # Store in session state
        st.session_state.selected_wallet = selected_wallet_name
        st.session_state.selected_wallet_id = selected_wallet_id
        
        # Display additional wallet information
        self._render_wallet_details(selected_wallet_info, selected_wallet_id)
        
        return selected_wallet_name, selected_wallet_id
    
    def _render_wallet_details(self, wallet_info: Dict, wallet_id: str):
        """Render additional details about the selected wallet."""
        with st.expander("ℹ️ Wallet Details", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Name:** {wallet_info.get('name', 'N/A')}")
                st.write(f"**Currency:** {wallet_info.get('currency', 'N/A')}")
            
            with col2:
                st.write(f"**ID:** {wallet_id}")
                st.write(f"**Status:** {'Active' if wallet_info.get('active', False) else 'Inactive'}")
            
            st.info(f"You are searching for instruments available in your **{wallet_info.get('display_name', 'Unknown')}** wallet.")

def render_user_info_section():
    """Render user information input section."""
    st.markdown("### User Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        user_name = st.text_input(
            "Your Name",
            key="user_name_input",
            placeholder="Enter your full name",
            value=st.session_state.get("user_name", "")
        )
    
    with col2:
        user_id = st.text_input(
            "User ID",
            key="user_id_input", 
            placeholder="Enter your user ID",
            value=st.session_state.get("user_id", "")
        )
    
    # Update session state
    if user_name:
        st.session_state.user_name = user_name
    if user_id:
        st.session_state.user_id = user_id
    
    return user_name, user_id

def render_search_stats():
    """Render search statistics and session information."""
    if st.session_state.get("search_history"):
        st.markdown("### Search Stats")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Searches Today", len(st.session_state.search_history))
        
        with col2:
            current_results = st.session_state.get("current_results", [])
            st.metric("Current Results", len(current_results))
        
        # Show recent searches
        if len(st.session_state.search_history) > 0:
            with st.expander("Recent Searches", expanded=False):
                for search in st.session_state.search_history[-5:]:  # Last 5 searches
                    st.caption(f"'{search.get('query', 'N/A')}' → {search.get('results_count', 0)} results")

def get_wallet_info(wallet_name: str) -> Dict:
    """Get wallet information by name."""
    config_path = Path(__file__).parent.parent / "data" / "wallet_specifications.json"
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
            for wallet_id, info in config["wallet_mappings"].items():
                if info["name"] == wallet_name:
                    return {"id": wallet_id, **info}
    except Exception:
        pass
    
    return {}
