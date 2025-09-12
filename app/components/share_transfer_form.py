# app/components/share_transfer_form.py

import streamlit as st
from typing import Dict, Any, Optional
from datetime import datetime, date
import json
from pathlib import Path
from app.services.portfolio_service import PortfolioService
# Remove this import as it's not used in this file

class ShareTransferForm:
    """
    Form component for capturing portfolio data following existing component patterns.
    Uses existing persist_widget utilities for form state management.
    """
    
    def __init__(self):
        self.broker_config = self._load_broker_config()
    
    def _load_broker_config(self) -> Dict:
        """Load broker configuration using existing pattern."""
        config_path = Path(__file__).parent.parent / "data" / "broker_specifications.json"
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception:
            # Fallback configuration following existing pattern
            return {
                "broker_mappings": {
                    "7": {"name": "EasyEquities Retail", "display_name": "EasyEquities Retail Platform"},
                    "9": {"name": "EasyEquities", "display_name": "EasyEquities Standard"},
                    "14": {"name": "Institutional", "display_name": "Institutional Platform"},
                    "26": {"name": "External Transfer", "display_name": "External Transfer Agent"},
                    "27": {"name": "Corporate Actions", "display_name": "Corporate Actions Desk"}
                },
                "default_brokers": {"from": "9", "to": "9"},
                "platform_options": [
                    {"value": "EE", "label": "EasyEquities", "default": True},
                    {"value": "SX", "label": "Satrix", "default": False}
                ]
            }
    
    def render_form(self, instrument: Dict, form_key: str) -> None:
        """
        Render share transfer form for a specific instrument.
        
        Args:
            instrument: Instrument data dictionary
            form_key: Unique key for this form instance
        """
        instrument_id = str(instrument.get('instrument_id'))
        
        # Get existing portfolio entry if available
        existing_entry = PortfolioService.get_portfolio_entry(instrument_id) or {}
        
        # Form container
        with st.form(key=f"share_transfer_form_{form_key}"):
            st.markdown("**Share Transfer Details**")
            
            # Platform selection
            platform_options = self.broker_config.get("platform_options", [])
            platform_labels = [opt["label"] for opt in platform_options]
            platform_values = [opt["value"] for opt in platform_options]
            
            default_platform_index = 0
            for i, opt in enumerate(platform_options):
                if opt.get("default", False):
                    default_platform_index = i
                    break
            
            selected_platform_index = st.selectbox(
                "Platform",
                range(len(platform_options)),
                format_func=lambda x: platform_labels[x],
                index=default_platform_index,
                key=f"platform_{form_key}",
                help="Select the trading platform"
            )
            selected_platform = platform_values[selected_platform_index]
            
            # Account and quantity information
            col1, col2 = st.columns(2)
            
            with col1:
                trust_account_id = st.text_input(
                    "Trust Account ID *",
                    value=existing_entry.get('trust_account_id', ''),
                    key=f"trust_account_id_{form_key}",
                    help="Enter the trust account identifier",
                    placeholder="e.g., 8275727"
                )
                
                quantity = st.number_input(
                    "Quantity *",
                    min_value=-999999999.0,
                    max_value=999999999.0,
                    value=float(existing_entry.get('quantity', 0.0)),
                    key=f"quantity_{form_key}",
                    help="Number of shares/units (can be negative for sales)",
                    format="%.0f"
                )
                
                base_cost = st.number_input(
                    "Base Cost per Unit *",
                    min_value=0.0,
                    value=float(existing_entry.get('base_cost', 0.0)),
                    key=f"base_cost_{form_key}",
                    help="Original cost per unit",
                    format="%.6f"
                )
            
            with col2:
                # Handle settlement date - convert string to date if needed
                settlement_date_value = existing_entry.get('settlement_date', date.today())
                if isinstance(settlement_date_value, str):
                    try:
                        settlement_date_value = datetime.strptime(settlement_date_value, "%Y-%m-%d").date()
                    except ValueError:
                        settlement_date_value = date.today()
                
                settlement_date = st.date_input(
                    "Settlement Date *",
                    value=settlement_date_value,
                    key=f"settlement_date_{form_key}",
                    help="Date when the transfer settles"
                )
                
                last_price = st.number_input(
                    "Last/Current Price *",
                    min_value=0.0,
                    value=float(existing_entry.get('last_price', 0.0)),
                    key=f"last_price_{form_key}",
                    help="Current market price per unit",
                    format="%.2f"
                )
            
            # Broker selection
            st.markdown("**Broker Information**")
            col1, col2 = st.columns(2)
            
            broker_options = [(broker_id, info["display_name"]) 
                            for broker_id, info in self.broker_config["broker_mappings"].items()]
            broker_ids = [opt[0] for opt in broker_options]
            broker_labels = [opt[1] for opt in broker_options]
            
            with col1:
                # Find default "from" broker index
                default_from_id = self.broker_config["default_brokers"]["from"]
                default_from_index = broker_ids.index(default_from_id) if default_from_id in broker_ids else 0
                
                # Get existing broker from selection
                existing_broker_from = existing_entry.get('broker_from', default_from_id)
                try:
                    existing_from_index = broker_ids.index(existing_broker_from)
                except ValueError:
                    existing_from_index = default_from_index
                
                selected_from_index = st.selectbox(
                    "Broker From *",
                    range(len(broker_options)),
                    format_func=lambda x: f"{broker_ids[x]} - {broker_labels[x]}",
                    index=existing_from_index,
                    key=f"broker_from_{form_key}",
                    help="Source broker for the transfer"
                )
                broker_from = broker_ids[selected_from_index]
            
            with col2:
                # Find default "to" broker index
                default_to_id = self.broker_config["default_brokers"]["to"]
                default_to_index = broker_ids.index(default_to_id) if default_to_id in broker_ids else 0
                
                # Get existing broker to selection
                existing_broker_to = existing_entry.get('broker_to', default_to_id)
                try:
                    existing_to_index = broker_ids.index(existing_broker_to)
                except ValueError:
                    existing_to_index = default_to_index
                
                selected_to_index = st.selectbox(
                    "Broker To *",
                    range(len(broker_options)),
                    format_func=lambda x: f"{broker_ids[x]} - {broker_labels[x]}",
                    index=existing_to_index,
                    key=f"broker_to_{form_key}",
                    help="Destination broker for the transfer"
                )
                broker_to = broker_ids[selected_to_index]
            
            # Optional notes
            notes = st.text_area(
                "Notes (Optional)",
                value=existing_entry.get('notes', ''),
                key=f"notes_{form_key}",
                help="Additional information or comments",
                height=70  # Minimum height is 68px in newer Streamlit versions
            )
            
            # Form submission - following current button styling conventions
            col1, col2 = st.columns([3, 1])
            with col2:
                submitted = st.form_submit_button(
                    "Save Entry",
                    type="primary",
                    use_container_width=True
                )
                # Note: Button styling automatically applied via FADE_IN_CSS and form submit button targeting
            
            # Validation and saving
            if submitted:
                # Validate required fields
                errors = []
                
                if not trust_account_id.strip():
                    errors.append("Trust Account ID is required")
                
                if quantity == 0:
                    errors.append("Quantity cannot be zero")
                
                if base_cost < 0:
                    errors.append("Base cost cannot be negative")
                
                if last_price <= 0:
                    errors.append("Last price must be greater than zero")
                
                if not settlement_date:
                    errors.append("Settlement date is required")
                
                if errors:
                    for error in errors:
                        st.error(f"{error}")
                else:
                    # Save portfolio entry
                    portfolio_data = {
                        'platform': selected_platform,
                        'trust_account_id': trust_account_id.strip(),
                        'quantity': int(quantity),
                        'base_cost': base_cost,
                        'settlement_date': settlement_date.strftime("%Y-%m-%d"),
                        'last_price': last_price,
                        'broker_from': broker_from,
                        'broker_to': broker_to,
                        'notes': notes.strip(),
                        'data_source': 'manual_entry'  # Track that this was manually entered
                    }
                    
                    try:
                        PortfolioService.update_portfolio_entry(instrument_id, portfolio_data)
                        st.success("Portfolio entry saved successfully!")
                        st.rerun()
                    except ValueError as e:
                        st.error(f"Validation error: {e}")
                    except Exception as e:
                        st.error(f"Error saving entry: {e}")
        
        # Display current status using custom badge styling
        current_entry = PortfolioService.get_portfolio_entry(instrument_id)
        if current_entry:
            # Use custom success badge following current styling conventions
            st.markdown("""
            <div class="custom-success-badge">
                Portfolio entry configured
            </div>
            """, unsafe_allow_html=True)
            
            # Show summary in compact format (no expander to avoid nesting)
            st.markdown("**Entry Summary:**")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.caption(f"**Platform:** {current_entry.get('platform', 'N/A')}")
                st.caption(f"**Account:** {current_entry.get('trust_account_id', 'N/A')}")
            with col2:
                st.caption(f"**Quantity:** {current_entry.get('quantity', 'N/A'):,}")
                st.caption(f"**Cost:** {current_entry.get('base_cost', 'N/A')}")
            with col3:
                st.caption(f"**Price:** {current_entry.get('last_price', 'N/A')}")
                st.caption(f"**Date:** {current_entry.get('settlement_date', 'N/A')}")
        else:
            # Use custom warning badge following current styling conventions
            st.markdown("""
            <div class="custom-warning-badge">
                Portfolio entry not configured
            </div>
            """, unsafe_allow_html=True)
