# app/services/portfolio_service.py

import streamlit as st
from typing import Dict, List, Optional, Any
from datetime import datetime, date
import pandas as pd
from pathlib import Path
import json
import logging
from app.search.fuzzy_matcher import InstrumentFuzzyMatcher

logger = logging.getLogger(__name__)

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
        
        # Check if there's an existing entry to preserve data_source history
        existing_entry = st.session_state.portfolio_entries.get(instrument_id)
        if existing_entry and 'data_source' not in portfolio_data:
            # Preserve existing data_source if not provided in update
            portfolio_data['data_source'] = existing_entry.get('data_source', 'manual_entry')
        elif not existing_entry and 'data_source' not in portfolio_data:
            # Default to manual_entry if not specified
            portfolio_data['data_source'] = 'manual_entry'
        
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
    
    @staticmethod
    def import_from_pdf_extraction(extracted_data: Dict, selected_instruments: List[Dict]) -> Dict:
        """
        Import PDF-extracted data into portfolio, matching against selected instruments.
        
        Args:
            extracted_data: Data extracted from PDF by Gemini
            selected_instruments: User's selected instruments from search
            
        Returns:
            Import result with success/error information
        """
        try:
            PortfolioService.initialize_portfolio_state()
            
            validated_entries = []
            unmatched_entries = []
            errors = []
            newly_selected_instruments = []
            
            # Load instruments data for matching - using same approach as main page
            from app.utils import load_instruments_data
            from app.services.selection_manager import SelectionManager
            from app.search.fuzzy_matcher import InstrumentFuzzyMatcher
            
            # Try multiple possible CSV locations
            possible_paths = [
                Path(__file__).parent.parent.parent / "data" / "Instrument_data.csv",
                Path(__file__).parent / "data" / "Instrument_Data_Format_Example.csv",
                Path(__file__).parent.parent.parent / "data" / "Instrument_Data_Format_Example.csv"
            ]
            
            csv_path = None
            for path in possible_paths:
                if path.exists():
                    csv_path = path
                    logger.info(f"Found CSV file at: {csv_path}")
                    break
            
            if csv_path:
                instruments_df = load_instruments_data(str(csv_path))
                # Use same threshold as main page (75 from main.py line 127)
                fuzzy_matcher = InstrumentFuzzyMatcher(instruments_df, threshold=75)
                logger.info(f"Loaded {len(instruments_df)} instruments for matching")
            else:
                logger.error("Instruments CSV not found - cannot match PDF entries")
                return {
                    'success': False,
                    'error': 'Instruments database not available',
                    'imported_count': 0
                }
            
            # Process each PDF entry
            for entry in extracted_data.get('portfolio_entries', []):
                try:
                    # First try to match with already selected instruments
                    matched_instrument = PortfolioService._match_with_selected(
                        entry, selected_instruments
                    )
                    
                    # If not in selected instruments, search the database using multiple strategies
                    if not matched_instrument and fuzzy_matcher:
                        search_queries = []
                        
                        # Build list of search queries to try
                        ticker = entry.get('ticker_symbol', '').strip()
                        # Remove parentheses from ticker if present (e.g., "(AAPL)" -> "AAPL")
                        if ticker.startswith('(') and ticker.endswith(')'):
                            ticker = ticker[1:-1]
                        name = entry.get('instrument_name', '').strip()
                        
                        if ticker:
                            search_queries.append(("ticker", ticker))
                        if name:
                            search_queries.append(("name", name))
                            # Also try name without common suffixes
                            clean_name = name.replace(" Inc", "").replace(" Corp", "").replace(" Corporation", "").strip()
                            if clean_name != name:
                                search_queries.append(("clean_name", clean_name))
                        
                        logger.info(f"Trying {len(search_queries)} search queries for entry: {name} ({ticker})")
                        
                        for query_type, search_query in search_queries:
                            if matched_instrument:
                                break  # Already found a match
                                
                            logger.info(f"Searching by {query_type}: '{search_query}'")
                            
                            # For PDF extraction, always search across ALL wallets first
                            # This ensures we find instruments regardless of wallet restrictions
                            # Strategy 1: Search across all wallets (primary strategy for PDF import)
                            search_results = fuzzy_matcher.search_instruments(
                                search_query, 
                                selected_wallet_id="all",  # Search across all wallets
                                max_results=10
                            )
                            logger.info(f"All-wallets search for '{search_query}': {len(search_results)} results")
                            
                            # Strategy 2: If user has specific wallet selected and no results, try that wallet
                            # (This is actually redundant now but kept for backward compatibility)
                            if not search_results and st.session_state.get('selected_wallet_id') and st.session_state.get('selected_wallet_id') != 'all':
                                logger.info(f"No results in all wallets, trying user's specific wallet")
                                search_results = fuzzy_matcher.search_instruments(
                                    search_query, 
                                    selected_wallet_id=st.session_state.get('selected_wallet_id'),
                                    max_results=10
                                )
                                logger.info(f"Wallet-specific search for '{search_query}': {len(search_results)} results")
                            
                            # Strategy 3: If still no results, try with lower threshold
                            if not search_results:
                                logger.info(f"No results, trying with lower threshold")
                                original_threshold = fuzzy_matcher.threshold
                                fuzzy_matcher.threshold = 60  # Lower threshold
                                search_results = fuzzy_matcher.search_instruments(
                                    search_query, 
                                    selected_wallet_id="all",  # Search across all wallets with lower threshold
                                    max_results=10
                                )
                                fuzzy_matcher.threshold = original_threshold
                                logger.info(f"Low-threshold search for '{search_query}': {len(search_results)} results")
                            
                            # Take the best match if relevance is reasonable
                            if search_results:
                                best_match = search_results[0]
                                relevance = best_match.get('relevance_score', 0)
                                logger.info(f"Best match for '{search_query}': '{best_match.get('name')}' ({relevance}% relevance)")
                                
                                if relevance > 60:  # Good match
                                    matched_instrument = best_match
                                    logger.info(f"✅ Matched '{search_query}' to '{matched_instrument.get('name')}'")
                                    
                                    # Add to user's selection automatically
                                    if SelectionManager.add_instrument(matched_instrument, f"PDF Import: {search_query}"):
                                        newly_selected_instruments.append(matched_instrument)
                                        logger.info(f"✅ Auto-selected: {matched_instrument.get('name')}")
                                    else:
                                        logger.warning(f"❌ Failed to add to selection: {matched_instrument.get('name')}")
                                    break
                                else:
                                    logger.info(f"⚠️ Low relevance ({relevance}%), trying next query")
                        
                        if not matched_instrument:
                            logger.warning(f"❌ No matches found for {name} ({ticker}) after trying all strategies")
                    
                    if matched_instrument:
                        instrument_id = str(matched_instrument.get('instrument_id', ''))
                        
                        # Check if there's already an existing portfolio entry
                        existing_entry = st.session_state.portfolio_entries.get(instrument_id)
                        
                        # Create portfolio entry data from PDF
                        pdf_data = {
                            # Share transfer data from PDF
                            'platform': extracted_data.get('document_metadata', {}).get('platform', 'EE'),
                            'trust_account_id': entry.get('account_number') or 
                                               extracted_data.get('document_metadata', {}).get('account_number', ''),
                            'quantity': int(entry.get('quantity', 0)),
                            'base_cost': float(entry.get('cost_basis', 0)),
                            'settlement_date': entry.get('purchase_date', str(date.today())),
                            'last_price': float(entry.get('current_value', 0) / abs(entry.get('quantity', 1)) 
                                              if entry.get('quantity') else 0),
                            'broker_from': '9',  # Default EasyEquities
                            'broker_to': '26',   # Default destination
                            
                            # Metadata
                            'data_source': 'pdf_extraction',
                            'extraction_confidence': extracted_data.get('confidence_scores', {}).get('overall', 0),
                            'source_document': extracted_data.get('document_metadata', {}).get('document_name', 'PDF Import'),
                            'pdf_entry_name': entry.get('instrument_name', ''),
                            'pdf_ticker': entry.get('ticker_symbol', ''),
                            'matched_instrument_id': str(matched_instrument.get('instrument_id', ''))
                        }
                        
                        # If there's an existing entry, merge data intelligently
                        if existing_entry:
                            logger.info(f"Merging PDF data with existing portfolio entry for {matched_instrument.get('name')}")
                            
                            # Create merged entry starting with existing data
                            portfolio_entry = existing_entry.copy()
                            
                            # Only update fields that are empty or default in the existing entry
                            for key, pdf_value in pdf_data.items():
                                existing_value = existing_entry.get(key)
                                
                                # Skip metadata fields that should always be updated
                                if key in ['data_source', 'extraction_confidence', 'source_document', 
                                          'pdf_entry_name', 'pdf_ticker', 'matched_instrument_id']:
                                    # Update metadata to indicate PDF source but preserve manual edits
                                    if existing_entry.get('data_source') == 'manual_entry':
                                        portfolio_entry['data_source'] = 'manual_then_pdf'
                                    else:
                                        portfolio_entry[key] = pdf_value
                                    continue
                                
                                # For data fields, only update if existing value is empty/default
                                if key == 'trust_account_id' and (not existing_value or existing_value == ''):
                                    portfolio_entry[key] = pdf_value
                                elif key == 'quantity' and existing_value in [None, 0]:
                                    portfolio_entry[key] = pdf_value
                                elif key == 'base_cost' and existing_value in [None, 0, 0.0]:
                                    portfolio_entry[key] = pdf_value
                                elif key == 'last_price' and existing_value in [None, 0, 0.0]:
                                    portfolio_entry[key] = pdf_value
                                elif key == 'settlement_date' and (not existing_value or existing_value == str(date.today())):
                                    portfolio_entry[key] = pdf_value
                                elif key in ['broker_from', 'broker_to'] and existing_value in [None, '', '9', '26']:
                                    # Only update brokers if they're still at defaults
                                    portfolio_entry[key] = pdf_value
                                # Otherwise preserve existing value
                            
                            # Add a flag to indicate this entry has been merged
                            portfolio_entry['pdf_merged'] = True
                            portfolio_entry['merge_timestamp'] = datetime.now().isoformat()
                        else:
                            # No existing entry, use PDF data as-is
                            portfolio_entry = pdf_data
                        
                        # Save to portfolio
                        st.session_state.portfolio_entries[instrument_id] = portfolio_entry
                        validated_entries.append({
                            'instrument_id': instrument_id,
                            'instrument_name': matched_instrument.get('name', ''),
                            'portfolio_entry': portfolio_entry
                        })
                        
                        logger.info(f"Matched and imported: {entry.get('instrument_name')} -> {matched_instrument.get('name')}")
                    else:
                        unmatched_entries.append(entry)
                        logger.warning(f"Could not match: {entry.get('instrument_name')}")
                        
                except Exception as e:
                    errors.append({
                        'entry': entry,
                        'error': str(e)
                    })
                    logger.error(f"Error processing entry: {e}")
            
            # Update metadata
            st.session_state.portfolio_metadata['last_updated'] = datetime.now().isoformat()
            st.session_state.portfolio_metadata['pdf_import'] = {
                'timestamp': datetime.now().isoformat(),
                'document_type': extracted_data.get('document_metadata', {}).get('document_type'),
                'confidence': extracted_data.get('confidence_scores', {}).get('overall', 0)
            }
            
            return {
                'success': True,
                'imported_count': len(validated_entries),
                'newly_selected_count': len(newly_selected_instruments),
                'unmatched_count': len(unmatched_entries),
                'error_count': len(errors),
                'entries': validated_entries,
                'newly_selected': newly_selected_instruments,
                'unmatched': unmatched_entries,
                'errors': errors,
                'extraction_metadata': extracted_data.get('document_metadata', {})
            }
            
        except Exception as e:
            logger.error(f"PDF import failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'imported_count': 0
            }
    
    @staticmethod
    def _match_with_selected(pdf_entry: Dict, selected_instruments: List[Dict]) -> Optional[Dict]:
        """
        Try to match a PDF entry with selected instruments.
        
        Args:
            pdf_entry: Entry from PDF extraction
            selected_instruments: User's selected instruments
            
        Returns:
            Matched instrument or None
        """
        if not selected_instruments:
            return None
        
        # Safely get values and handle None cases
        entry_name = (pdf_entry.get('instrument_name') or '').lower().strip()
        entry_ticker = (pdf_entry.get('ticker_symbol') or '').lower().strip()
        # Remove parentheses from ticker if present
        if entry_ticker.startswith('(') and entry_ticker.endswith(')'):
            entry_ticker = entry_ticker[1:-1]
        entry_isin = (pdf_entry.get('isin_code') or '').lower().strip()
        
        for instrument in selected_instruments:
            # Try exact ticker match first
            inst_ticker = (instrument.get('ticker') or '').lower().strip()
            if entry_ticker and inst_ticker == entry_ticker:
                return instrument
            
            # Try ISIN match
            inst_isin = (instrument.get('isin') or '').lower().strip()
            if entry_isin and inst_isin == entry_isin:
                return instrument
            
            # Try name match (fuzzy)
            inst_name = (instrument.get('name') or '').lower().strip()
            if entry_name and inst_name and (
                entry_name in inst_name or 
                inst_name in entry_name or
                PortfolioService._fuzzy_match(entry_name, inst_name, threshold=0.8)
            ):
                return instrument
        
        return None
    
    @staticmethod
    def _fuzzy_match(str1: str, str2: str, threshold: float = 0.8) -> bool:
        """Simple fuzzy matching for instrument names."""
        from difflib import SequenceMatcher
        return SequenceMatcher(None, str1, str2).ratio() >= threshold
