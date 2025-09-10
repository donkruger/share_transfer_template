# app/services/selection_manager.py

import streamlit as st
import datetime
from typing import Dict, List, Any, Optional

class SelectionManager:
    """
    Centralized service for managing instrument selections with persistence,
    deduplication, and enhanced user control.
    
    Implements the separation of concerns between search results and user selections,
    ensuring selections persist across multiple search sessions.
    """
    
    @staticmethod
    def get_instrument_key(instrument: Dict[str, Any]) -> str:
        """
        Generate unique key for instrument deduplication using business key approach.
        
        Uses (Exchange, Ticker, ContractCode) as primary key with fallback to legacy key.
        """
        # Use business key as recommended in CSV analysis
        exchange = (instrument.get('exchange') or '').upper()
        ticker = (instrument.get('ticker') or '').upper()
        contract_code = (instrument.get('contract_code') or '').upper()
        
        if exchange and ticker and contract_code:
            return f"BUSINESS_KEY|{exchange}|{ticker}|{contract_code}"
        
        # Fallback to legacy key
        instrument_id = instrument.get('instrument_id', '')
        name = (instrument.get('name') or '').upper()
        return f"LEGACY_KEY|{instrument_id}|{name}"
    
    @staticmethod
    def _ensure_selection_state():
        """Ensure selection state is properly initialized."""
        if 'selected_instruments' not in st.session_state:
            st.session_state.selected_instruments = []
        
        if 'selection_metadata' not in st.session_state:
            st.session_state.selection_metadata = {
                "total_selected": 0,
                "selection_timestamps": {},
                "selection_sources": {},
                "last_modified": None
            }
    
    @staticmethod
    def add_instrument(instrument: Dict[str, Any], source_query: str = "") -> bool:
        """
        Add instrument to selections with metadata tracking.
        
        Args:
            instrument: Instrument data dictionary
            source_query: Search query that led to this selection
            
        Returns:
            bool: True if added successfully, False if already selected
        """
        SelectionManager._ensure_selection_state()
        
        instrument_key = SelectionManager.get_instrument_key(instrument)
        
        # Check if already selected
        if SelectionManager.is_selected(instrument):
            return False
        
        # Add to selections
        st.session_state.selected_instruments.append(instrument)
        
        # Update metadata
        current_time = datetime.datetime.now().isoformat()
        st.session_state.selection_metadata["selection_timestamps"][instrument_key] = current_time
        st.session_state.selection_metadata["selection_sources"][instrument_key] = source_query
        st.session_state.selection_metadata["total_selected"] = len(st.session_state.selected_instruments)
        st.session_state.selection_metadata["last_modified"] = current_time
        
        return True
    
    @staticmethod
    def remove_instrument(instrument: Dict[str, Any]) -> bool:
        """
        Remove instrument from selections by unique key.
        
        Args:
            instrument: Instrument data dictionary or instrument key string
            
        Returns:
            bool: True if removed successfully, False if not found
        """
        SelectionManager._ensure_selection_state()
        
        if isinstance(instrument, str):
            instrument_key = instrument
        else:
            instrument_key = SelectionManager.get_instrument_key(instrument)
        
        # Find and remove instrument
        original_count = len(st.session_state.selected_instruments)
        st.session_state.selected_instruments = [
            inst for inst in st.session_state.selected_instruments
            if SelectionManager.get_instrument_key(inst) != instrument_key
        ]
        
        # Update metadata if instrument was removed
        if len(st.session_state.selected_instruments) < original_count:
            # Clean up metadata
            if instrument_key in st.session_state.selection_metadata["selection_timestamps"]:
                del st.session_state.selection_metadata["selection_timestamps"][instrument_key]
            if instrument_key in st.session_state.selection_metadata["selection_sources"]:
                del st.session_state.selection_metadata["selection_sources"][instrument_key]
            
            st.session_state.selection_metadata["total_selected"] = len(st.session_state.selected_instruments)
            st.session_state.selection_metadata["last_modified"] = datetime.datetime.now().isoformat()
            return True
        
        return False
    
    @staticmethod
    def clear_selections(confirm: bool = False) -> bool:
        """
        Clear all selections with confirmation requirement.
        
        Args:
            confirm: Whether user has confirmed the clear action
            
        Returns:
            bool: True if cleared successfully
        """
        if not confirm:
            return False
        
        SelectionManager._ensure_selection_state()
        
        st.session_state.selected_instruments = []
        st.session_state.selection_metadata = {
            "total_selected": 0,
            "selection_timestamps": {},
            "selection_sources": {},
            "last_modified": datetime.datetime.now().isoformat()
        }
        
        return True
    
    @staticmethod
    def get_selections() -> List[Dict[str, Any]]:
        """
        Get current selections with metadata.
        
        Returns:
            List of selected instruments
        """
        SelectionManager._ensure_selection_state()
        return st.session_state.selected_instruments.copy()
    
    @staticmethod
    def is_selected(instrument: Dict[str, Any]) -> bool:
        """
        Check if instrument is already selected.
        
        Args:
            instrument: Instrument data dictionary
            
        Returns:
            bool: True if instrument is already selected
        """
        SelectionManager._ensure_selection_state()
        
        instrument_key = SelectionManager.get_instrument_key(instrument)
        selected_keys = [
            SelectionManager.get_instrument_key(inst) 
            for inst in st.session_state.selected_instruments
        ]
        
        return instrument_key in selected_keys
    
    @staticmethod
    def get_selection_summary() -> Dict[str, Any]:
        """
        Get summary statistics about current selections.
        
        Returns:
            Dictionary with selection statistics
        """
        SelectionManager._ensure_selection_state()
        
        selections = st.session_state.selected_instruments
        metadata = st.session_state.selection_metadata
        
        if not selections:
            return {
                "total_count": 0,
                "last_modified": None,
                "unique_exchanges": [],
                "unique_asset_types": [],
                "selection_sources": []
            }
        
        # Calculate statistics
        exchanges = list(set(inst.get('exchange', 'Unknown') for inst in selections))
        asset_types = list(set(inst.get('asset_type', 'Unknown') for inst in selections))
        sources = list(set(metadata.get("selection_sources", {}).values()))
        
        return {
            "total_count": len(selections),
            "last_modified": metadata.get("last_modified"),
            "unique_exchanges": exchanges,
            "unique_asset_types": asset_types,
            "selection_sources": [s for s in sources if s],  # Filter empty sources
            "oldest_selection": min(metadata.get("selection_timestamps", {}).values()) if metadata.get("selection_timestamps") else None,
            "newest_selection": max(metadata.get("selection_timestamps", {}).values()) if metadata.get("selection_timestamps") else None
        }
    
    @staticmethod
    def get_selection_by_key(instrument_key: str) -> Optional[Dict[str, Any]]:
        """
        Get selected instrument by its unique key.
        
        Args:
            instrument_key: Unique instrument key
            
        Returns:
            Instrument dictionary if found, None otherwise
        """
        SelectionManager._ensure_selection_state()
        
        for instrument in st.session_state.selected_instruments:
            if SelectionManager.get_instrument_key(instrument) == instrument_key:
                return instrument
        
        return None
    
    @staticmethod
    def get_selection_metadata(instrument: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get metadata for a specific selected instrument.
        
        Args:
            instrument: Instrument data dictionary
            
        Returns:
            Metadata dictionary for the instrument
        """
        SelectionManager._ensure_selection_state()
        
        instrument_key = SelectionManager.get_instrument_key(instrument)
        metadata = st.session_state.selection_metadata
        
        return {
            "selected_at": metadata.get("selection_timestamps", {}).get(instrument_key),
            "source_query": metadata.get("selection_sources", {}).get(instrument_key),
            "instrument_key": instrument_key
        }
