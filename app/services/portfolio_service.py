# app/services/portfolio_service.py

import streamlit as st
from typing import Dict, List, Optional, Any
from datetime import datetime, date
import pandas as pd
from pathlib import Path
import json

class PortfolioService:
    """
    Central service for managing portfolio data and share transfer information.
    Follows existing project patterns for session state and component integration.
    """
    
    @staticmethod
    def initialize_portfolio_state():
        """Initialize portfolio-specific session state variables using existing patterns."""
        # Use setdefault pattern from existing utils.py initialize_state()
        st.session_state.setdefault("portfolio_entries", {})
        st.session_state.setdefault("portfolio_metadata", {
            'default_platform': 'EE',
            'default_broker_from': '9',
            'default_broker_to': '9',
            'last_updated': None
        })
        st.session_state.setdefault("portfolio_form_data", {})  # Temporary form state
    
    @staticmethod
    def get_portfolio_entry(instrument_id: str) -> Optional[Dict]:
        """Get portfolio data for specific instrument."""
        PortfolioService.initialize_portfolio_state()
        return st.session_state.portfolio_entries.get(instrument_id)
    
    @staticmethod
    def update_portfolio_entry(instrument_id: str, portfolio_data: Dict):
        """Update portfolio data for specific instrument."""
        PortfolioService.initialize_portfolio_state()
        
        # Validate required fields
        required_fields = ['trust_account_id', 'quantity', 'base_cost', 
                          'settlement_date', 'last_price', 'broker_from', 'broker_to']
        
        for field in required_fields:
            if field not in portfolio_data or portfolio_data[field] in [None, '', 0]:
                if field == 'quantity':
                    continue  # Quantity can be 0 or negative
                raise ValueError(f"Required field '{field}' is missing or invalid")
        
        # Store with timestamp
        portfolio_data['updated_at'] = datetime.now().isoformat()
        st.session_state.portfolio_entries[instrument_id] = portfolio_data
        
        # Update metadata
        st.session_state.portfolio_metadata['last_updated'] = datetime.now().isoformat()
    
    @staticmethod
    def get_all_portfolio_entries() -> Dict[str, Dict]:
        """Get all portfolio entries."""
        PortfolioService.initialize_portfolio_state()
        return st.session_state.portfolio_entries
    
    @staticmethod
    def is_portfolio_complete() -> bool:
        """Check if portfolio data is complete for all selected instruments."""
        from app.services.selection_manager import SelectionManager
        
        selected_instruments = SelectionManager.get_selections()
        portfolio_entries = PortfolioService.get_all_portfolio_entries()
        
        if not selected_instruments:
            return False
        
        for instrument in selected_instruments:
            instrument_id = str(instrument.get('instrument_id'))
            if instrument_id not in portfolio_entries:
                return False
                
            # Verify all required fields are present
            entry = portfolio_entries[instrument_id]
            required_fields = ['trust_account_id', 'quantity', 'base_cost', 
                              'settlement_date', 'last_price', 'broker_from', 'broker_to']
            
            for field in required_fields:
                if field not in entry or entry[field] in [None, '', 0]:
                    if field == 'quantity':
                        continue  # Quantity can be 0 or negative
                    return False
        
        return True
    
    @staticmethod
    def generate_share_transfer_data() -> List[Dict]:
        """Generate share transfer data in exact target CSV format."""
        from app.services.selection_manager import SelectionManager
        
        selected_instruments = SelectionManager.get_selections()
        portfolio_entries = PortfolioService.get_all_portfolio_entries()
        
        user_id = st.session_state.get('user_id', '')
        platform = st.session_state.portfolio_metadata.get('default_platform', 'EE')
        
        transfer_data = []
        
        for instrument in selected_instruments:
            instrument_id = str(instrument.get('instrument_id'))
            portfolio_entry = portfolio_entries.get(instrument_id)
            
            if not portfolio_entry:
                continue
            
            # Generate exact reference format from example: "NT -2025-09-10,NT -,2025/09/10"
            settlement_date = portfolio_entry.get('settlement_date')  # YYYY-MM-DD format
            excel_date = settlement_date.replace('-', '/')  # Convert to YYYY/MM/DD
            reference = f"NT -{settlement_date},NT -,{excel_date}"
            
            # Create record matching exact CSV column order and format
            transfer_record = {
                'SX/EE': platform,
                'User ID ': user_id,  # Note: space after "User ID" matches target format
                'TrustAccountID': portfolio_entry.get('trust_account_id'),
                'ShareCode': instrument.get('ticker', ''),
                'InstrumentID': int(instrument.get('instrument_id', 0)),
                'Qty': int(portfolio_entry.get('quantity', 0)),  # Can be negative
                'Base Cost ©': float(portfolio_entry.get('base_cost', 0.0)),
                'Excel Date': excel_date,
                'SettlementDate': settlement_date,
                'Last Price': float(portfolio_entry.get('last_price', 0.0)),
                'BrokerID_From': f"{portfolio_entry.get('broker_from', '')} ",  # Space after value
                'BrokerID_To': f"{portfolio_entry.get('broker_to', '')} ",  # Space after value  
                'Reference': reference,
                '': '',  # Empty column 1
                ' ': ''  # Empty column 2 (note: space as column name)
            }
            
            transfer_data.append(transfer_record)
        
        return transfer_data
    
    @staticmethod
    def clear_portfolio_data():
        """Clear all portfolio data."""
        st.session_state.portfolio_entries = {}
        st.session_state.portfolio_metadata = {
            'default_platform': 'EE',
            'default_broker_from': '9',
            'default_broker_to': '9',
            'last_updated': None
        }
    
    @staticmethod
    def import_ai_portfolio_data(json_data: Dict) -> Dict[str, Any]:
        """
        Import portfolio data from AI agent JSON.
        
        Args:
            json_data: Validated JSON data from AI agent
            
        Returns:
            Dict containing import results and any errors
        """
        from app.json_validators import validate_portfolio_json
        from app.services.selection_manager import SelectionManager
        
        # Validate JSON schema
        is_valid, validation_errors = validate_portfolio_json(json_data)
        if not is_valid:
            return {
                'success': False,
                'errors': validation_errors,
                'imported_count': 0
            }
        
        imported_count = 0
        errors = []
        selected_instruments = SelectionManager.get_selections()
        
        # Create lookup for selected instruments
        instrument_lookup = {}
        for inst in selected_instruments:
            # Multiple lookup keys for flexible matching
            if inst.get('ticker'):
                instrument_lookup[inst['ticker'].upper()] = inst
            if inst.get('isin'):
                instrument_lookup[inst['isin'].upper()] = inst
            if inst.get('name'):
                instrument_lookup[inst['name'].upper()] = inst
            if inst.get('instrument_id'):
                instrument_lookup[str(inst['instrument_id'])] = inst
        
        # Process each portfolio entry from AI
        for entry in json_data.get('portfolio_entries', []):
            try:
                # Match instrument
                identifier = entry['instrument_identifier']
                matched_instrument = None
                
                # Try different matching strategies
                for key in ['ticker', 'isin', 'name', 'instrument_id']:
                    if key in identifier and identifier[key]:
                        lookup_key = str(identifier[key]).upper()
                        if lookup_key in instrument_lookup:
                            matched_instrument = instrument_lookup[lookup_key]
                            break
                
                if not matched_instrument:
                    errors.append(f"No matching instrument found for {identifier}")
                    continue
                
                # Prepare portfolio data with AI metadata
                portfolio_data = entry['portfolio_data'].copy()
                portfolio_data.update({
                    'data_source': json_data['metadata']['source'],
                    'ai_confidence': json_data['metadata'].get('confidence_score', 0.0),
                    'extraction_timestamp': json_data['metadata']['extraction_timestamp'],
                    'source_document': json_data['metadata'].get('source_document', ''),
                    'requires_review': True,  # Always require user review for AI data
                    'ai_extracted_fields': entry['portfolio_data'].get('ai_extracted_fields', {})
                })
                
                # Store with special AI prefix to indicate source
                instrument_id = str(matched_instrument['instrument_id'])
                PortfolioService.update_portfolio_entry(instrument_id, portfolio_data)
                imported_count += 1
                
            except Exception as e:
                errors.append(f"Error processing entry {entry}: {str(e)}")
        
        return {
            'success': imported_count > 0,
            'imported_count': imported_count,
            'errors': errors,
            'total_entries': len(json_data.get('portfolio_entries', [])),
            'metadata': json_data['metadata']
        }
