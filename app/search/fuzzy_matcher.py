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
        
        # Check if searching across all wallets
        if wallet_id == "all" or wallet_id == "":
            logger.info(f"Searching across ALL wallets - no wallet filtering applied")
            return active_df
        
        # Filter by wallet availability in accountFiltersArray
        if wallet_id and wallet_id.isdigit():
            logger.info(f"Filtering by specific wallet ID: {wallet_id}")
            
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
        """Find exact and high-confidence matches with enhanced priority ranking."""
        results = []
        query_upper = query.upper()
        query_lower = query.lower()
        
        # Priority 1: Exact name matches (highest priority)
        exact_name = df[df['Name'].str.upper() == query_upper]
        for _, row in exact_name.iterrows():
            results.append(self._create_result_dict(row, 100, "exact_name", priority=1))
        
        # Priority 1.5: Exact ticker matches (very high priority)
        exact_ticker = df[df['Ticker'].str.upper() == query_upper]
        for _, row in exact_ticker.iterrows():
            results.append(self._create_result_dict(row, 99, "exact_ticker", priority=1))
        
        # Priority 2: Name starts with query (high confidence partial match)
        if len(query) >= 3:  # Only for meaningful queries
            starts_with_name = df[df['Name'].str.lower().str.startswith(query_lower)]
            # Exclude already found exact matches
            starts_with_name = starts_with_name[~starts_with_name['Name'].str.upper().isin([query_upper])]
            for _, row in starts_with_name.iterrows():
                # Score based on how much of the name matches
                name_len = len(row['Name'])
                query_len = len(query)
                score = min(95, 85 + (query_len / name_len * 10))
                results.append(self._create_result_dict(row, int(score), "starts_with_name", priority=2))
        
        return results
    
    def _find_fuzzy_name_matches(self, df: pd.DataFrame, query: str) -> List[Dict]:
        """Find fuzzy matches in instrument names with enhanced scoring."""
        results = []
        names = df['Name'].dropna().tolist()
        
        if not names:
            return results
        
        # Use multiple fuzzy matching algorithms for better accuracy
        # Token sort ratio is good for reordered words
        token_sort_matches = process.extract(query, names, scorer=fuzz.token_sort_ratio, limit=None)
        # WRatio is good for partial matches
        wratio_matches = process.extract(query, names, scorer=fuzz.WRatio, limit=None)
        
        # Combine scores from different algorithms
        combined_scores = {}
        for name, score in token_sort_matches:
            if score >= self.threshold - 10:  # Slightly lower threshold for initial filtering
                combined_scores[name] = score
        
        for name, score in wratio_matches:
            if score >= self.threshold - 10:
                if name in combined_scores:
                    # Take the maximum of the two scores
                    combined_scores[name] = max(combined_scores[name], score)
                else:
                    combined_scores[name] = score
        
        # Filter and add results
        for name, score in combined_scores.items():
            if score >= self.threshold:
                matching_rows = df[df['Name'] == name]
                for _, row in matching_rows.iterrows():
                    # Priority 3: Fuzzy name matches (high priority, after exact matches)
                    results.append(self._create_result_dict(row, score, "fuzzy_name", priority=3))
        
        return results
    
    def _find_ticker_matches(self, df: pd.DataFrame, query: str) -> List[Dict]:
        """Find ticker matches with enhanced priority ranking and variation handling."""
        results = []
        tickers = df['Ticker'].dropna().tolist()
        tickers = [t for t in tickers if t != '']
        
        if not tickers:
            return results
        
        query_upper = query.upper()
        
        # First check for exact ticker matches (case-insensitive) that weren't caught earlier
        for ticker in tickers:
            if ticker.upper() == query_upper:
                matching_rows = df[df['Ticker'] == ticker]
                for _, row in matching_rows.iterrows():
                    # High score for exact ticker match
                    results.append(self._create_result_dict(row, 95, "ticker_exact", priority=2))
        
        # Then do fuzzy matching for partial matches
        matches = process.extract(query, tickers, scorer=fuzz.ratio, limit=None)
        
        for ticker, score in matches:
            # Skip if we already added this as exact match
            if ticker.upper() != query_upper:
                if score >= max(60, self.threshold - 20):  # Lower threshold for tickers
                    matching_rows = df[df['Ticker'] == ticker]
                    for _, row in matching_rows.iterrows():
                        # Priority 4: Fuzzy ticker matches (after name matches)
                        results.append(self._create_result_dict(row, score, "fuzzy_ticker", priority=4))
        
        return results
    
    def _find_isin_matches(self, df: pd.DataFrame, query: str) -> List[Dict]:
        """Find ISIN code matches with lowest priority (secondary ranking)."""
        results = []
        
        if 'ISINCode' not in df.columns:
            return results
        
        isins = df['ISINCode'].dropna().tolist()
        isins = [i for i in isins if i != '']
        
        if not isins:
            return results
        
        query_upper = query.upper()
        
        # First check for exact ISIN matches
        for isin in isins:
            if isin.upper() == query_upper:
                matching_rows = df[df['ISINCode'] == isin]
                for _, row in matching_rows.iterrows():
                    # Exact ISIN match gets high score but still lower priority than name/ticker
                    results.append(self._create_result_dict(row, 90, "isin_exact", priority=5))
        
        # Then do fuzzy matching for partial ISIN matches
        # ISINs are standardized codes, so only look for high-confidence matches
        matches = process.extract(query, isins, scorer=fuzz.ratio, limit=None)
        
        for isin, score in matches:
            # Skip if already added as exact match
            if isin.upper() != query_upper:
                if score >= max(85, self.threshold):  # High threshold for ISINs (they should match closely)
                    matching_rows = df[df['ISINCode'] == isin]
                    for _, row in matching_rows.iterrows():
                        # Priority 5: ISIN matches (lowest priority - secondary ranking)
                        results.append(self._create_result_dict(row, score, "isin_fuzzy", priority=5))
        
        return results
    
    def _determine_currency(self, row: pd.Series) -> str:
        """
        Determine the trading currency based on exchange or wallet filters.
        """
        exchange = row.get('Exchange', '').upper()
        
        # Map exchanges to currencies
        exchange_currency_map = {
            'JSE': 'ZAR',
            'NYSE': 'USD',
            'NASDAQ': 'USD',
            'LSE': 'GBP',
            'EURONEXT': 'EUR',
            'ASX': 'AUD',
            'TSX': 'CAD',
            'HKEX': 'HKD',
            'SSE': 'CNY',
            'NSE': 'INR',
            'BOVESPA': 'BRL'
        }
        
        # First try to get currency from exchange
        if exchange in exchange_currency_map:
            return exchange_currency_map[exchange]
        
        # Check if any wallet filter columns have values to infer currency
        # Look for accountFilters/TradingCurrency* columns
        for col in row.index:
            if col.startswith('accountFilters/TradingCurrency'):
                if pd.notna(row[col]) and row[col] != 0:
                    # Extract currency from column name
                    currency_part = col.replace('accountFilters/TradingCurrency', '')
                    # Map common wallet types to currencies
                    if currency_part in ['ZAR', 'TFSA', 'RA']:
                        return 'ZAR'
                    elif currency_part == 'USD':
                        return 'USD'
                    elif currency_part == 'GBP':
                        return 'GBP'
                    elif currency_part == 'EUR':
                        return 'EUR'
                    elif currency_part == 'AUD':
                        return 'AUD'
        
        # Default to ZAR if no currency can be determined
        return 'ZAR'
    
    def _create_result_dict(self, row: pd.Series, score: int, match_type: str, priority: int = 10) -> Dict:
        """Create standardized result dictionary with priority-based ranking."""
        # Determine currency based on exchange or wallet filters
        currency = self._determine_currency(row)
        
        return {
            # Core identifiers
            'instrument_id': row.get('InstrumentID', ''),
            'name': row.get('Name', ''),
            'ticker': row.get('Ticker', ''),
            'isin': row.get('ISINCode', ''),
            'contract_code': row.get('ContractCode', ''),
            
            # Asset classification - using correct CSV column names
            'asset_group': row.get('AssetGroup', ''),
            'asset_sub_group': row.get('AssetSubGroup', ''),
            'asset_type': row.get('AssetGroup', ''),  # Map AssetGroup to asset_type for backward compatibility
            
            # Exchange and currency info
            'exchange': row.get('Exchange', ''),
            'currency': currency,
            
            # Description
            'description': row.get('*Description', ''),
            
            # Search metadata with priority
            'relevance_score': score,
            'match_type': match_type,
            'priority': priority,  # Lower number = higher priority
            
            # Wallet eligibility
            'account_filters': row.get('accountFiltersArray', ''),
            
            # Keep raw data for any additional fields needed
            'raw_data': row.to_dict()
        }
    
    def _deduplicate_and_rank(self, results: List[Dict]) -> List[Dict]:
        """Remove duplicates and sort by enhanced priority system."""
        seen_instruments = {}
        
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
            
            # Keep only the best match for each instrument
            if instrument_key not in seen_instruments:
                seen_instruments[instrument_key] = result
            else:
                existing = seen_instruments[instrument_key]
                # Use priority if available, otherwise use match_type_priority
                result_priority = result.get('priority', 99)
                existing_priority = existing.get('priority', 99)
                
                if (result_priority < existing_priority or 
                    (result_priority == existing_priority and 
                     result['relevance_score'] > existing['relevance_score'])):
                    seen_instruments[instrument_key] = result
        
        unique_results = list(seen_instruments.values())
        
        # Enhanced sorting: priority first, then relevance score
        # Priority: 1=exact_name, 2=exact_ticker, 3=fuzzy_name, 4=fuzzy_ticker, 5=isin
        unique_results.sort(
            key=lambda x: (
                x.get('priority', 99),  # Use explicit priority if set
                -x['relevance_score']    # Then by relevance score (higher is better)
            )
        )
        
        return unique_results
