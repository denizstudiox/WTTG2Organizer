"""
WTTG2 Organizer - Data Manager
Thread-safe data persistence layer with file locking.
"""
import json
import os
import threading
from typing import Dict, Any


class DataManager:
    """
    Thread-safe data manager for JSON persistence.
    Handles loading, saving, and accessing game data.
    """
    
    def __init__(self, data_file: str):
        """
        Initialize data manager.
        
        Args:
            data_file: Path to JSON data file
        """
        self.data_file = data_file
        self._lock = threading.Lock()
        self._data = self._load_data()
    
    def _get_default_data(self) -> Dict[str, Any]:
        """Get default data structure"""
        return {
            "keys": [""] * 8,
            "sites": {},  # { "SiteName": { "green": bool, "red": bool, "yellow": bool } }
            "notes": "",
            "wifi": [],  # [ { "ssid": "", "pass": "", "loc": "" } ]
            "mode1337": False,
            "key_markers": [[0, 0, 0] for _ in range(8)]  # [wiki1, wiki2, wiki3]
        }
    
    def _load_data(self) -> Dict[str, Any]:
        """
        Load data from file with validation and migration.
        
        Returns:
            Loaded and validated data dictionary
        """
        if not os.path.exists(self.data_file):
            default_data = self._get_default_data()
            self._save_data(default_data)
            return default_data
        
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Validate and migrate data
            if "keys" not in data or not isinstance(data["keys"], list):
                data["keys"] = [""] * 8
            if "sites" not in data:
                data["sites"] = {}
            if "notes" not in data:
                data["notes"] = ""
            if "wifi" not in data:
                data["wifi"] = []
            if "mode1337" not in data:
                data["mode1337"] = False
            if "key_markers" not in data:
                data["key_markers"] = [[0, 0, 0] for _ in range(8)]
            
            return data
            
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading data: {e}")
            return self._get_default_data()
    
    def _save_data(self, data: Dict[str, Any]) -> bool:
        """
        Save data to file atomically.
        
        Args:
            data: Data dictionary to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Write to temporary file first
            temp_file = self.data_file + '.tmp'
            with open(temp_file, 'w', encoding='utf-8') as f:
                  # Use compact JSON for faster I/O
                json.dump(data, f, ensure_ascii=False)
            
            # Atomic rename
            # Atomic replace (works on Windows Python 3.3+)
            os.replace(temp_file, self.data_file)
            
            return True
            
        except (IOError, OSError) as e:
            print(f"Error saving data: {e}")
            return False
    
    def get_data(self) -> Dict[str, Any]:
        """
        Get current data (thread-safe).
        
        Returns:
            Copy of current data
        """
        with self._lock:
            return self._data.copy()
    
    def update_data(self, updates: Dict[str, Any]) -> bool:
        """
        Update data with given changes (thread-safe).
        
        Args:
            updates: Dictionary of updates to apply
            
        Returns:
            True if successful, False otherwise
        """
        with self._lock:
            self._data.update(updates)
            return self._save_data(self._data)
    
    def set_key(self, index: int, value: str) -> bool:
        """Update specific key value"""
        if 0 <= index < 8:
            with self._lock:
                self._data['keys'][index] = value
                return self._save_data(self._data)
        return False
    
    def toggle_key_marker(self, key_index: int, marker_index: int) -> bool:
        """Toggle wiki marker for a key"""
        if 0 <= key_index < 8 and 0 <= marker_index < 3:
            with self._lock:
                current = self._data['key_markers'][key_index][marker_index]
                self._data['key_markers'][key_index][marker_index] = 1 if current == 0 else 0
                return self._save_data(self._data)
        return False
    
    def set_notes(self, text: str) -> bool:
        """Update notes"""
        with self._lock:
            self._data['notes'] = text
            return self._save_data(self._data)
    
    def toggle_site_marker(self, site_name: str, color: str) -> bool:
        """Toggle site marker (green/red/yellow)"""
        if color not in ['green', 'red', 'yellow']:
            return False
        
        with self._lock:
            if site_name not in self._data['sites']:
                self._data['sites'][site_name] = {'green': False, 'red': False, 'yellow': False}
            
            # Ensure dict structure
            if not isinstance(self._data['sites'][site_name], dict):
                self._data['sites'][site_name] = {'green': False, 'red': False, 'yellow': False}
            
            # Migration/Safe check
            if color not in self._data['sites'][site_name]:
                self._data['sites'][site_name][color] = False
            
            # Toggle
            current_val = self._data['sites'][site_name].get(color, False)
            self._data['sites'][site_name][color] = not current_val
            
            return self._save_data(self._data)
    
    def set_mode_1337(self, enabled: bool) -> bool:
        """Set 1337 mode"""
        with self._lock:
            self._data['mode1337'] = enabled
            return self._save_data(self._data)
    
    def add_wifi(self, ssid: str, password: str, location: str) -> bool:
        """Add wifi entry"""
        with self._lock:
            self._data['wifi'].append({
                'ssid': ssid,
                'pass': password,
                'loc': location
            })
            return self._save_data(self._data)
    
    def delete_wifi(self, index: int) -> bool:
        """Delete wifi entry by index"""
        with self._lock:
            if 0 <= index < len(self._data['wifi']):
                self._data['wifi'].pop(index)
                return self._save_data(self._data)
        return False

    def reset_data(self) -> bool:
        """Reset all data to default values"""
        with self._lock:
            self._data = self._get_default_data()
            return self._save_data(self._data)
