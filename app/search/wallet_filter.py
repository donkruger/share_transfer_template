# app/search/wallet_filter.py
import json
import pandas as pd
from typing import List, Dict, Set
from pathlib import Path

class WalletFilterEngine:
    """
    Handles wallet filtering logic and account filter array parsing
    for precise instrument availability validation.
    """
    
    def __init__(self, wallet_config_path: str):
        self.wallet_mappings = self._load_wallet_mappings(wallet_config_path)
        self.id_to_name = {id_str: info['name'] for id_str, info in self.wallet_mappings.items()}
        self.name_to_id = {info['name']: id_str for id_str, info in self.wallet_mappings.items()}
    
    def _load_wallet_mappings(self, config_path: str) -> Dict:
        """Load wallet configuration from JSON file."""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                return config.get('wallet_mappings', {})
        except Exception:
            # Fallback hardcoded mappings
            return {
                "2": {"name": "ZAR", "display_name": "EasyEquities ZAR", "currency": "ZAR", "active": True},
                "3": {"name": "TFSA", "display_name": "Tax-Free Savings Account", "currency": "ZAR", "active": True},
                "9": {"name": "RA", "display_name": "Retirement Annuity", "currency": "ZAR", "active": True},
                "10": {"name": "USD", "display_name": "EasyEquities USD", "currency": "USD", "active": True},
                "74": {"name": "GBP", "display_name": "EasyEquities GBP", "currency": "GBP", "active": True},
                "75": {"name": "EUR", "display_name": "EasyEquities EUR", "currency": "EUR", "active": True},
                "16": {"name": "AUD", "display_name": "EasyEquities AUD", "currency": "AUD", "active": True},
                "55": {"name": "LA", "display_name": "Living Annuity", "currency": "ZAR", "active": True},
                "48": {"name": "PENS", "display_name": "Preservation Pension Fund", "currency": "ZAR", "active": True},
                "24": {"name": "PROV", "display_name": "Preservation Provident Fund", "currency": "ZAR", "active": True}
            }
    
    def parse_account_filters(self, account_filters_str: str) -> Set[str]:
        """Parse accountFiltersArray string into set of wallet IDs."""
        if not account_filters_str or pd.isna(account_filters_str):
            return set()
        
        try:
            # Handle comma-separated values with possible quotes
            ids = str(account_filters_str).replace('"', '').split(',')
            return {id_str.strip() for id_str in ids if id_str.strip()}
        except Exception:
            return set()
    
    def is_available_in_wallet(self, account_filters_str: str, wallet_name: str) -> bool:
        """Check if instrument is available in specified wallet."""
        wallet_id = self.name_to_id.get(wallet_name)
        if not wallet_id:
            return False
        
        available_wallets = self.parse_account_filters(account_filters_str)
        return wallet_id in available_wallets
    
    def get_available_wallets(self, account_filters_str: str) -> List[Dict]:
        """Get list of wallets where instrument is available."""
        available_ids = self.parse_account_filters(account_filters_str)
        
        available_wallets = []
        for wallet_id in available_ids:
            if wallet_id in self.wallet_mappings:
                wallet_info = self.wallet_mappings[wallet_id].copy()
                wallet_info['id'] = wallet_id
                available_wallets.append(wallet_info)
        
        return sorted(available_wallets, key=lambda x: x['name'])
    
    def get_wallet_display_name(self, wallet_id: str) -> str:
        """Get display name for wallet ID."""
        wallet_info = self.wallet_mappings.get(wallet_id, {})
        return wallet_info.get('display_name', wallet_info.get('name', f'Wallet {wallet_id}'))
    
    def get_all_wallets(self) -> List[Dict]:
        """Get all available wallets with their information."""
        wallets = []
        for wallet_id, info in self.wallet_mappings.items():
            if info.get('active', True):
                wallet_info = info.copy()
                wallet_info['id'] = wallet_id
                wallets.append(wallet_info)
        
        return sorted(wallets, key=lambda x: x['name'])
