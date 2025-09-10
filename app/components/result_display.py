# app/components/result_display.py

import streamlit as st
from typing import List, Dict, Any
from app.search.wallet_filter import WalletFilterEngine
from app.services.selection_manager import SelectionManager

class ResultDisplayComponent:
    """
    Professional search results display with selection capabilities
    and detailed instrument information.
    """
    
    def __init__(self, wallet_filter: WalletFilterEngine):
        self.wallet_filter = wallet_filter
    
    def render_results(self, results: List[Dict], allow_selection: bool = True) -> List[Dict]:
        """
        Render search results with selection checkboxes.
        Returns list of selected instruments.
        """
        if not results:
            self._render_no_results()
            return []
        
        st.markdown(f"### Search Results ({len(results)} found)")
        
        # Results summary
        self._render_results_summary(results)
        
        # Results display
        selected_instruments = []
        
        if allow_selection:
            st.markdown("**Select instruments to add to your submission:**")
        
        for idx, result in enumerate(results):
            selected = self._render_result_item(result, idx, allow_selection)
            if selected:
                selected_instruments.append(result)
        
        return selected_instruments
    
    def _render_results_summary(self, results: List[Dict]):
        """Render summary statistics for search results."""
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Results", len(results))
        
        with col2:
            exact_matches = sum(1 for r in results if r.get('match_type', '').startswith('exact'))
            st.metric("Exact Matches", exact_matches)
        
        with col3:
            avg_score = sum(r.get('relevance_score', 0) for r in results) / len(results) if results else 0
            st.metric("Avg. Relevance", f"{avg_score:.1f}%")
    
    def _render_result_item(self, result: Dict, idx: int, allow_selection: bool = True) -> bool:
        """Enhanced result item with better selection feedback and duplicate prevention."""
        with st.container():
            # Check if already selected using SelectionManager
            is_already_selected = SelectionManager.is_selected(result)
            
            if allow_selection:
                col1, col2, col3, col4 = st.columns([0.7, 2.8, 2, 1.5])
            else:
                col1, col2, col3 = st.columns([3.5, 2, 1.5])
            
            selection_changed = False
            
            if allow_selection:
                with col1:
                    if is_already_selected:
                        # Show selected indicator with custom styling
                        st.markdown("""
                        <div class="custom-success-badge">
                            ✓ Selected
                        </div>
                        """, unsafe_allow_html=True)
                        if st.button("Remove", key=f"remove_{idx}", 
                                   help="Remove from your selection", 
                                   type="secondary"):
                            SelectionManager.remove_instrument(result)
                            selection_changed = True
                            st.rerun()
                    else:
                        # Show selection checkbox
                        selected = st.checkbox("Select", key=f"select_{idx}", 
                                             help="Add to your instrument portfolio")
                        if selected:
                            success = SelectionManager.add_instrument(
                                result, 
                                st.session_state.get('last_search_query', '')
                            )
                            if success:
                                selection_changed = True
                                st.rerun()
            
            with col2 if allow_selection else col1:
                # Instrument name with selection status
                name_display = f"**{result.get('name', 'N/A')}**"
                
                if is_already_selected and allow_selection:
                    name_display += " 🔖"  # Visual indicator for selected items
                
                st.markdown(name_display)
                if result.get('ticker'):
                    st.caption(f"Ticker: {result.get('ticker')}")
            
            with col3 if allow_selection else col2:
                asset_type = result.get('asset_type', 'N/A')
                exchange = result.get('exchange', 'N/A')
                st.text(f"{asset_type} • {exchange}")
                st.caption(f"Relevance: {result.get('relevance_score', 0)}%")
            
            with col4 if allow_selection else col3:
                # Available wallets for this instrument
                self._render_wallet_availability(result)
            
            # Show selection metadata for already selected items
            if is_already_selected and allow_selection:
                metadata = SelectionManager.get_selection_metadata(result)
                if metadata.get('selected_at'):
                    selected_time = metadata['selected_at'][:19].replace('T', ' ')
                    st.caption(f"Selected: {selected_time}")
                if metadata.get('source_query'):
                    st.caption(f"From search: '{metadata['source_query']}'")
            
        st.divider()
        return selection_changed
    
    def _render_wallet_availability(self, result: Dict):
        """Render wallet availability information for an instrument."""
        available_wallets = self.wallet_filter.get_available_wallets(
            result.get('account_filters', '')
        )
        
        if available_wallets:
            wallet_names = [w['name'] for w in available_wallets[:3]]
            wallet_display = ', '.join(wallet_names)
            if len(available_wallets) > 3:
                wallet_display += f" (+{len(available_wallets) - 3} more)"
            st.markdown(f"""
            <div class="custom-wallet-badge">
                Available in: {wallet_display}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="custom-warning-badge">
                Wallet availability unknown
            </div>
            """, unsafe_allow_html=True)
    
    
    def _render_no_results(self):
        """Render message when no results are found."""
        st.info("No instruments found matching your search criteria. Try adjusting your search terms or fuzzy match threshold.")
        
        with st.expander("Suggestions to improve your search"):
            st.markdown("""
            - Try **broader terms** (e.g., "Apple" instead of "Apple Inc Class A")
            - Check **spelling** of instrument names
            - Use **ticker symbols** if you know them (e.g., "AAPL")
            - **Lower the fuzzy threshold** in search options
            - **Change wallet context** if the instrument might be in a different wallet
            """)

def render_selection_summary():
    """Render enhanced summary of selected instruments with management options."""
    selected = SelectionManager.get_selections()
    summary = SelectionManager.get_selection_summary()
    
    if selected:
        # Enhanced selection summary
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Selected Instruments", summary['total_count'])
        with col2:
            st.metric("Unique Exchanges", len(summary['unique_exchanges']))
        with col3:
            st.metric("Asset Types", len(summary['unique_asset_types']))
        
        # Selection management options
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Get AI Assistance", use_container_width=True):
                st.switch_page("pages/1_AI_Assistance.py")
        with col2:
            if st.button("Proceed to Submit", type="primary", use_container_width=True):
                st.switch_page("pages/2_Submit.py")
        with col3:
            if st.button("Clear All Selections", type="secondary", use_container_width=True):
                if st.session_state.get('confirm_clear_selections', False):
                    SelectionManager.clear_selections(confirm=True)
                    st.session_state.confirm_clear_selections = False
                    st.success("All selections cleared!")
                    st.rerun()
                else:
                    st.session_state.confirm_clear_selections = True
                    st.warning("Click again to confirm clearing all selections")
        
        # Reset confirmation if user doesn't follow through
        if 'confirm_clear_selections' in st.session_state and st.session_state.confirm_clear_selections:
            if st.button("Cancel Clear", key="cancel_clear"):
                st.session_state.confirm_clear_selections = False
                st.rerun()
        
        # Show selection details in expandable section
        with st.expander(f"View Selected Instruments ({len(selected)})", expanded=False):
            for i, instrument in enumerate(selected):
                col1, col2, col3 = st.columns([3, 2, 1])
                with col1:
                    st.write(f"**{instrument.get('name', 'N/A')}**")
                    st.caption(f"Ticker: {instrument.get('ticker', 'N/A')}")
                with col2:
                    st.write(f"{instrument.get('exchange', 'N/A')}")
                    st.caption(f"{instrument.get('asset_type', 'N/A')}")
                with col3:
                    if st.button("Remove", key=f"remove_summary_{i}", type="secondary"):
                        SelectionManager.remove_instrument(instrument)
                        st.rerun()
                st.divider()
    else:
        st.info("Select instruments above to build your portfolio and proceed to submission")
