# app/search/fuzzy_matcher.py
from fuzzywuzzy import fuzz, process
import pandas as pd
from typing import List, Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class InstrumentFuzzyMatcher:
    """
    Advanced fuzzy matching engine for financial instruments
    supporting multiple search strategies and relevance scoring.
    """
    
    def __init__(self, instruments_df: pd.DataFrame, threshold: int = 80):
        self.instruments_df = instruments_df
        self.threshold = threshold
        
        # Prepare search indices for different field types
        self.name_index = self._prepare_name_index()
        self.ticker_index = self._prepare_ticker_index()
        self.isin_index = self._prepare_isin_index()
    
    def _prepare_name_index(self) -> Dict[str, int]:
        """Create name-to-index mapping for fast lookups."""
        return {row['Name']: idx for idx, row in self.instruments_df.iterrows() 
                if pd.notna(row['Name'])}
    
    def _prepare_ticker_index(self) -> Dict[str, int]:
        """Create ticker-to-index mapping for fast lookups."""
        return {row['Ticker']: idx for idx, row in self.instruments_df.iterrows() 
                if pd.notna(row['Ticker']) and row['Ticker'] != ''}
    
    def _prepare_isin_index(self) -> Dict[str, int]:
        """Create ISIN-to-index mapping for fast lookups."""
        return {row['ISINCode']: idx for idx, row in self.instruments_df.iterrows() 
                if pd.notna(row.get('ISINCode', '')) and row.get('ISINCode', '') != ''}
    
    def search_instruments(self, query: str, selected_wallet_id: str, 
                          max_results: int = 50) -> List[Dict]:
        """
        Perform comprehensive fuzzy search across multiple fields.
        Returns ranked results with relevance scores.
        """
        logger.info(f"FuzzyMatcher.search_instruments called with query='{query}', wallet_id='{selected_wallet_id}', max_results={max_results}")
        
        query = query.strip()
        if not query:
            logger.warning("Empty query provided to search_instruments")
            return []
        
        logger.info(f"Starting search with cleaned query: '{query}'")
        logger.info(f"Total instruments in dataset: {len(self.instruments_df)}")
        
        # Filter active instruments and wallet availability first
        logger.info("Filtering by wallet and status...")
        filtered_df = self._filter_by_wallet_and_status(selected_wallet_id)
        logger.info(f"After wallet/status filtering: {len(filtered_df)} instruments")
        
        if filtered_df.empty:
            logger.warning("No instruments available after wallet/status filtering")
            return []
        
        # Multi-strategy search
        results = []
        
        # 1. Exact matches (highest priority)
        logger.info("Searching for exact matches...")
        exact_matches = self._find_exact_matches(filtered_df, query)
        logger.info(f"Found {len(exact_matches)} exact matches")
        results.extend(exact_matches)
        
        # 2. Fuzzy name matches
        logger.info("Searching for fuzzy name matches...")
        fuzzy_name_matches = self._find_fuzzy_name_matches(filtered_df, query)
        logger.info(f"Found {len(fuzzy_name_matches)} fuzzy name matches")
        results.extend(fuzzy_name_matches)
        
        # 3. Ticker matches
        logger.info("Searching for ticker matches...")
        ticker_matches = self._find_ticker_matches(filtered_df, query)
        logger.info(f"Found {len(ticker_matches)} ticker matches")
        results.extend(ticker_matches)
        
        # 4. ISIN matches
        logger.info("Searching for ISIN matches...")
        isin_matches = self._find_isin_matches(filtered_df, query)
        logger.info(f"Found {len(isin_matches)} ISIN matches")
        results.extend(isin_matches)
        
        logger.info(f"Total matches before deduplication: {len(results)}")
        
        # Remove duplicates and rank by relevance
        logger.info("Deduplicating and ranking results...")
        unique_results = self._deduplicate_and_rank(results)
        logger.info(f"Final unique results: {len(unique_results)}")
        
        final_results = unique_results[:max_results]
        logger.info(f"Returning {len(final_results)} results (limited by max_results={max_results})")
        
        return final_results
    
    def _filter_by_wallet_and_status(self, wallet_id: str) -> pd.DataFrame:
        """Filter instruments by active status and wallet availability."""
        logger.info(f"Filtering by wallet_id='{wallet_id}' and active status")
        
        # Filter out inactive instruments (ActiveData = 0)
        active_df = self.instruments_df[self.instruments_df['ActiveData'] != 0].copy()
        logger.info(f"Active instruments (ActiveData != 0): {len(active_df)}")
        
        # Filter by wallet availability in accountFiltersArray
        if wallet_id and wallet_id.isdigit():
            logger.info(f"Filtering by wallet ID: {wallet_id}")
            
            # Debug: Show some sample accountFiltersArray values
            sample_filters = active_df['accountFiltersArray'].fillna('').astype(str).head(10).tolist()
            logger.info(f"Sample accountFiltersArray values: {sample_filters}")
            
            mask = active_df['accountFiltersArray'].fillna('').astype(str).str.contains(
                f'\\b{wallet_id}\\b', na=False, regex=True
            )
            filtered_df = active_df[mask]
            logger.info(f"After wallet filtering: {len(filtered_df)} instruments")
            
            # Debug: Show which instruments match
            if len(filtered_df) > 0:
                sample_names = filtered_df['Name'].head(5).tolist()
                logger.info(f"Sample filtered instrument names: {sample_names}")
            
            return filtered_df
        else:
            logger.info(f"No valid wallet_id provided ('{wallet_id}'), returning all active instruments")
            return active_df
    
    def _find_exact_matches(self, df: pd.DataFrame, query: str) -> List[Dict]:
        """Find exact matches in name or ticker fields."""
        results = []
        query_upper = query.upper()
        
        # Exact name matches
        exact_name = df[df['Name'].str.upper() == query_upper]
        for _, row in exact_name.iterrows():
            results.append(self._create_result_dict(row, 100, "exact_name"))
        
        # Exact ticker matches  
        exact_ticker = df[df['Ticker'].str.upper() == query_upper]
        for _, row in exact_ticker.iterrows():
            results.append(self._create_result_dict(row, 95, "exact_ticker"))
        
        return results
    
    def _find_fuzzy_name_matches(self, df: pd.DataFrame, query: str) -> List[Dict]:
        """Find fuzzy matches in instrument names."""
        results = []
        names = df['Name'].dropna().tolist()
        
        if not names:
            return results
        
        # Use fuzzywuzzy for intelligent matching
        matches = process.extract(query, names, scorer=fuzz.token_sort_ratio, limit=None)
        
        for name, score in matches:
            if score >= self.threshold:
                matching_rows = df[df['Name'] == name]
                for _, row in matching_rows.iterrows():
                    results.append(self._create_result_dict(row, score, "fuzzy_name"))
        
        return results
    
    def _find_ticker_matches(self, df: pd.DataFrame, query: str) -> List[Dict]:
        """Find ticker matches with fuzzy search."""
        results = []
        tickers = df['Ticker'].dropna().tolist()
        tickers = [t for t in tickers if t != '']
        
        if not tickers:
            return results
        
        matches = process.extract(query, tickers, scorer=fuzz.ratio, limit=None)
        
        for ticker, score in matches:
            if score >= max(60, self.threshold - 20):  # Lower threshold for tickers
                matching_rows = df[df['Ticker'] == ticker]
                for _, row in matching_rows.iterrows():
                    results.append(self._create_result_dict(row, score, "ticker"))
        
        return results
    
    def _find_isin_matches(self, df: pd.DataFrame, query: str) -> List[Dict]:
        """Find ISIN code matches."""
        results = []
        
        if 'ISINCode' not in df.columns:
            return results
        
        isins = df['ISINCode'].dropna().tolist()
        isins = [i for i in isins if i != '']
        
        if not isins:
            return results
        
        matches = process.extract(query, isins, scorer=fuzz.ratio, limit=None)
        
        for isin, score in matches:
            if score >= max(80, self.threshold):  # High threshold for ISINs
                matching_rows = df[df['ISINCode'] == isin]
                for _, row in matching_rows.iterrows():
                    results.append(self._create_result_dict(row, score, "isin"))
        
        return results
    
    def _create_result_dict(self, row: pd.Series, score: int, match_type: str) -> Dict:
        """Create standardized result dictionary."""
        return {
            'instrument_id': row.get('InstrumentID', ''),
            'name': row.get('Name', ''),
            'ticker': row.get('Ticker', ''),
            'isin': row.get('ISINCode', ''),
            'contract_code': row.get('ContractCode', ''),
            'asset_type': row.get('AssetType', ''),
            'exchange': row.get('Exchange', ''),
            'currency': row.get('TradingCurrency', ''),
            'relevance_score': score,
            'match_type': match_type,
            'account_filters': row.get('accountFiltersArray', ''),
            'raw_data': row.to_dict()
        }
    
    def _deduplicate_and_rank(self, results: List[Dict]) -> List[Dict]:
        """Remove duplicates and sort by relevance."""
        seen_instruments = set()
        unique_results = []
        
        for result in results:
            # Prefer business key (Exchange, Ticker, ContractCode); fallback to instrument_id+name
            business_key = (
                (result.get('exchange') or '').upper(),
                (result.get('ticker') or '').upper(),
                (result.get('contract_code') or '').upper(),
            )
            if any(business_key):
                instrument_key = ('BUSINESS_KEY',) + business_key
            else:
                instrument_key = ('LEGACY_KEY', result.get('instrument_id', ''), (result.get('name') or '').upper())
            if instrument_key not in seen_instruments:
                seen_instruments.add(instrument_key)
                unique_results.append(result)
        
        # Sort by relevance score (descending) and match type priority
        match_type_priority = {
            'exact_name': 0,
            'exact_ticker': 1,
            'fuzzy_name': 2,
            'ticker': 3,
            'isin': 4
        }
        
        unique_results.sort(
            key=lambda x: (
                match_type_priority.get(x['match_type'], 99),
                -x['relevance_score']
            )
        )
        
        return unique_results
