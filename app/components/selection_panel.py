# app/components/selection_panel.py

import streamlit as st
from typing import Dict, List, Any
from app.services.selection_manager import SelectionManager

class SelectionPanel:
    """
    Persistent panel showing user's selected instruments across all searches.
    Always visible, provides selection management capabilities.
    """
    
    def __init__(self):
        pass
    
    def render_persistent_panel(self, location: str = "sidebar") -> None:
        """
        Render always-visible selection panel in sidebar or main area.
        
        Args:
            location: "sidebar" or "main" - where to render the panel
        """
        selected = SelectionManager.get_selections()
        summary = SelectionManager.get_selection_summary()
        
        if location == "sidebar":
            self._render_sidebar_panel(selected, summary)
        else:
            self._render_main_panel(selected, summary)
    
    def _render_sidebar_panel(self, selected: List[Dict], summary: Dict[str, Any]) -> None:
        """Render compact selection panel for sidebar."""
        st.markdown("### Your Portfolio")
        
        if selected:
            # Compact summary
            st.metric("Selected", summary['total_count'])
            
            # Quick actions
            col1, col2 = st.columns(2)
            with col1:
                if st.button("View All", key="sidebar_view_all", use_container_width=True):
                    st.session_state.show_selection_details = True
            with col2:
                if st.button("Clear", key="sidebar_clear", use_container_width=True, type="secondary"):
                    self._handle_clear_selections()
            
            # Recent selections (last 3)
            st.markdown("**Recent Selections:**")
            recent_selections = selected[-3:] if len(selected) > 3 else selected
            
            for i, instrument in enumerate(recent_selections):
                with st.container():
                    st.caption(f"• {instrument.get('name', 'Unknown')[:25]}...")
                    if st.button("Remove", key=f"sidebar_remove_{i}", 
                               help=f"Remove {instrument.get('name', 'Unknown')}"):
                        SelectionManager.remove_instrument(instrument)
                        st.rerun()
            
            if len(selected) > 3:
                st.caption(f"... and {len(selected) - 3} more")
        else:
            st.info("No instruments selected yet")
            st.caption("Select instruments from search results to build your portfolio")
    
    def _render_main_panel(self, selected: List[Dict], summary: Dict[str, Any]) -> None:
        """Render detailed selection panel for main area."""
        st.markdown("### Portfolio Management")
        
        if selected:
            # Detailed summary
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Selected", summary['total_count'])
            with col2:
                st.metric("Exchanges", len(summary['unique_exchanges']))
            with col3:
                st.metric("Asset Types", len(summary['unique_asset_types']))
            with col4:
                if summary.get('newest_selection'):
                    last_selected = summary['newest_selection'][:19].replace('T', ' ')
                    st.metric("Last Selected", last_selected[-8:])  # Show time only
            
            # Bulk actions
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("Export List", key="main_export", use_container_width=True):
                    self._export_selection_list(selected)
            with col2:
                if st.button("View Details", key="main_details", use_container_width=True):
                    st.session_state.show_selection_details = not st.session_state.get('show_selection_details', False)
            with col3:
                if st.button("Clear All", key="main_clear", use_container_width=True, type="secondary"):
                    self._handle_clear_selections()
            
            # Detailed selection list (if requested)
            if st.session_state.get('show_selection_details', False):
                self._render_detailed_selection_list(selected)
        else:
            st.info("Your portfolio is empty")
            st.markdown("""
            **How to build your portfolio:**
            1. Search for instruments using the search box above
            2. Click "Select" next to instruments you're interested in
            3. Your selections will persist across multiple searches
            4. Review and submit when ready
            """)
    
    def _render_detailed_selection_list(self, selected: List[Dict]) -> None:
        """Render detailed list of selected instruments."""
        st.markdown("#### Selected Instruments")
        
        # Group by exchange for better organization
        exchanges = {}
        for instrument in selected:
            exchange = instrument.get('exchange', 'Unknown')
            if exchange not in exchanges:
                exchanges[exchange] = []
            exchanges[exchange].append(instrument)
        
        for exchange, instruments in exchanges.items():
            with st.expander(f"{exchange} ({len(instruments)} instruments)", expanded=True):
                for i, instrument in enumerate(instruments):
                    self.render_selection_item(instrument, f"{exchange}_{i}")
    
    def render_selection_item(self, instrument: Dict, index: str) -> None:
        """Render individual selected instrument with remove option and metadata."""
        col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
        
        with col1:
            st.write(f"**{instrument.get('name', 'Unknown Instrument')}**")
            if instrument.get('ticker'):
                st.caption(f"Ticker: {instrument.get('ticker')}")
        
        with col2:
            st.write(f"{instrument.get('asset_type', 'N/A')}")
            st.caption(f"Exchange: {instrument.get('exchange', 'N/A')}")
        
        with col3:
            # Show selection metadata
            metadata = SelectionManager.get_selection_metadata(instrument)
            if metadata.get('selected_at'):
                selected_time = metadata['selected_at'][:19].replace('T', ' ')
                st.caption(f"Selected: {selected_time}")
            if metadata.get('source_query'):
                st.caption(f"From: '{metadata['source_query'][:20]}...'")
        
        with col4:
            if st.button("Remove", key=f"panel_remove_{index}", 
                        type="secondary", use_container_width=True,
                        help=f"Remove {instrument.get('name', 'Unknown')} from selection"):
                SelectionManager.remove_instrument(instrument)
                st.rerun()
        
        st.divider()
    
    def render_selection_actions(self) -> None:
        """Render bulk actions for selections (clear all, export, etc.)."""
        selected = SelectionManager.get_selections()
        
        if not selected:
            return
        
        st.markdown("#### Portfolio Actions")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("Clear All Selections", key="bulk_clear", 
                        type="secondary", use_container_width=True):
                self._handle_clear_selections()
        
        with col2:
            if st.button("Export as CSV", key="bulk_export_csv", 
                        use_container_width=True):
                self._export_selection_list(selected, format="csv")
        
        with col3:
            if st.button("Export as Text", key="bulk_export_text", 
                        use_container_width=True):
                self._export_selection_list(selected, format="text")
        
        with col4:
            if st.button("Get AI Analysis", key="bulk_ai_analysis", 
                        use_container_width=True):
                st.switch_page("pages/1_AI_Assistance.py")
    
    def _handle_clear_selections(self) -> None:
        """Handle clearing all selections with confirmation."""
        if st.session_state.get('confirm_clear_all', False):
            SelectionManager.clear_selections(confirm=True)
            st.session_state.confirm_clear_all = False
            st.success("All selections cleared!")
            st.rerun()
        else:
            st.session_state.confirm_clear_all = True
            st.warning("⚠️ This will clear ALL selected instruments. Click 'Clear All' again to confirm.")
            
            # Auto-reset confirmation after 10 seconds (simulated with button)
            if st.button("Cancel", key="cancel_clear_all"):
                st.session_state.confirm_clear_all = False
                st.rerun()
    
    def _export_selection_list(self, selected: List[Dict], format: str = "csv") -> None:
        """Export selection list in specified format."""
        if not selected:
            st.warning("No instruments selected to export")
            return
        
        if format == "csv":
            # Generate CSV content
            import io
            import csv
            
            output = io.StringIO()
            fieldnames = ['name', 'ticker', 'exchange', 'asset_type', 'isin', 'selected_at', 'source_query']
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            
            for instrument in selected:
                metadata = SelectionManager.get_selection_metadata(instrument)
                row = {
                    'name': instrument.get('name', ''),
                    'ticker': instrument.get('ticker', ''),
                    'exchange': instrument.get('exchange', ''),
                    'asset_type': instrument.get('asset_type', ''),
                    'isin': instrument.get('isin', ''),
                    'selected_at': metadata.get('selected_at', ''),
                    'source_query': metadata.get('source_query', '')
                }
                writer.writerow(row)
            
            csv_content = output.getvalue()
            
            st.download_button(
                label="Download Portfolio as CSV",
                data=csv_content,
                file_name=f"portfolio_selection_{len(selected)}_instruments.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        elif format == "text":
            # Generate text content
            text_content = f"Selected Instruments Portfolio ({len(selected)} instruments)\n"
            text_content += "=" * 50 + "\n\n"
            
            for i, instrument in enumerate(selected, 1):
                metadata = SelectionManager.get_selection_metadata(instrument)
                text_content += f"{i}. {instrument.get('name', 'Unknown')}\n"
                text_content += f"   Ticker: {instrument.get('ticker', 'N/A')}\n"
                text_content += f"   Exchange: {instrument.get('exchange', 'N/A')}\n"
                text_content += f"   Asset Type: {instrument.get('asset_type', 'N/A')}\n"
                if metadata.get('selected_at'):
                    text_content += f"   Selected: {metadata['selected_at'][:19].replace('T', ' ')}\n"
                if metadata.get('source_query'):
                    text_content += f"   From Search: {metadata['source_query']}\n"
                text_content += "\n"
            
            st.download_button(
                label="Download Portfolio as Text",
                data=text_content,
                file_name=f"portfolio_selection_{len(selected)}_instruments.txt",
                mime="text/plain",
                use_container_width=True
            )
    
    def render_selection_stats(self) -> None:
        """Render selection statistics and insights."""
        selected = SelectionManager.get_selections()
        summary = SelectionManager.get_selection_summary()
        
        if not selected:
            return
        
        st.markdown("#### Portfolio Statistics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**By Exchange:**")
            for exchange in summary['unique_exchanges']:
                count = sum(1 for inst in selected if inst.get('exchange') == exchange)
                st.caption(f"• {exchange}: {count} instruments")
        
        with col2:
            st.markdown("**By Asset Type:**")
            for asset_type in summary['unique_asset_types']:
                count = sum(1 for inst in selected if inst.get('asset_type') == asset_type)
                st.caption(f"• {asset_type}: {count} instruments")
        
        if summary.get('selection_sources'):
            st.markdown("**Search Sources:**")
            for source in summary['selection_sources'][:5]:  # Show top 5 sources
                count = sum(1 for metadata in st.session_state.selection_metadata.get('selection_sources', {}).values() if metadata == source)
                st.caption(f"• '{source}': {count} selections")
