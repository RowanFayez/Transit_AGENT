"""
Memory system for storing user preferences and recent locations
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)

@dataclass
class RecentLocation:
    """Represents a recently used location"""
    name: str
    lat: float
    lon: float
    timestamp: str
    usage_count: int = 1

@dataclass
class UserPreference:
    """Represents user preferences"""
    preferred_transit_modes: List[str]
    max_walking_distance: int  # in meters
    max_transfers: int
    language: str  # 'ar' or 'en'
    wheelchair_accessible: bool = False

class MemoryManager:
    """Manages user memory and preferences"""
    
    def __init__(self, memory_file: str = "user_memory.json"):
        self.memory_file = memory_file
        self.memory = self._load_memory()
    
    def _load_memory(self) -> Dict[str, Any]:
        """Load memory from file"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load memory: {e}")
        
        # Default memory structure
        return {
            "recent_locations": [],
            "user_preferences": {
                "preferred_transit_modes": ["TRANSIT", "BUS"],
                "max_walking_distance": 1000,
                "max_transfers": 2,
                "language": "en",
                "wheelchair_accessible": False
            },
            "favorite_locations": [],
            "search_history": []
        }
    
    def _save_memory(self):
        """Save memory to file"""
        try:
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.memory, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save memory: {e}")
    
    def add_recent_location(self, name: str, lat: float, lon: float):
        """Add a location to recent locations"""
        now = datetime.now().isoformat()
        
        # Check if location already exists
        for location in self.memory["recent_locations"]:
            if (abs(location["lat"] - lat) < 0.001 and 
                abs(location["lon"] - lon) < 0.001):
                location["timestamp"] = now
                location["usage_count"] += 1
                self._save_memory()
                return
        
        # Add new location
        new_location = RecentLocation(
            name=name,
            lat=lat,
            lon=lon,
            timestamp=now
        )
        
        self.memory["recent_locations"].append(asdict(new_location))
        
        # Keep only last 20 locations
        if len(self.memory["recent_locations"]) > 20:
            self.memory["recent_locations"] = self.memory["recent_locations"][-20:]
        
        self._save_memory()
    
    def get_recent_locations(self, limit: int = 5) -> List[RecentLocation]:
        """Get recent locations sorted by usage"""
        locations = []
        for loc_data in self.memory["recent_locations"]:
            location = RecentLocation(**loc_data)
            locations.append(location)
        
        # Sort by usage count and timestamp
        locations.sort(key=lambda x: (x.usage_count, x.timestamp), reverse=True)
        return locations[:limit]
    
    def add_favorite_location(self, name: str, lat: float, lon: float):
        """Add a location to favorites"""
        favorite = {
            "name": name,
            "lat": lat,
            "lon": lon,
            "added_at": datetime.now().isoformat()
        }
        
        # Check if already exists
        for fav in self.memory["favorite_locations"]:
            if (abs(fav["lat"] - lat) < 0.001 and 
                abs(fav["lon"] - lon) < 0.001):
                return
        
        self.memory["favorite_locations"].append(favorite)
        self._save_memory()
    
    def get_favorite_locations(self) -> List[Dict[str, Any]]:
        """Get favorite locations"""
        return self.memory["favorite_locations"]
    
    def update_preferences(self, **kwargs):
        """Update user preferences"""
        for key, value in kwargs.items():
            if key in self.memory["user_preferences"]:
                self.memory["user_preferences"][key] = value
        
        self._save_memory()
    
    def get_preferences(self) -> UserPreference:
        """Get user preferences"""
        prefs_data = self.memory["user_preferences"]
        return UserPreference(
            preferred_transit_modes=prefs_data["preferred_transit_modes"],
            max_walking_distance=prefs_data["max_walking_distance"],
            max_transfers=prefs_data["max_transfers"],
            language=prefs_data["language"],
            wheelchair_accessible=prefs_data["wheelchair_accessible"]
        )
    
    def add_search_history(self, query: str, from_location: str, to_location: str):
        """Add search to history"""
        search_entry = {
            "query": query,
            "from_location": from_location,
            "to_location": to_location,
            "timestamp": datetime.now().isoformat()
        }
        
        self.memory["search_history"].append(search_entry)
        
        # Keep only last 50 searches
        if len(self.memory["search_history"]) > 50:
            self.memory["search_history"] = self.memory["search_history"][-50:]
        
        self._save_memory()
    
    def get_search_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get search history"""
        return self.memory["search_history"][-limit:]
    
    def clear_old_data(self, days: int = 30):
        """Clear data older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        cutoff_str = cutoff_date.isoformat()
        
        # Clear old recent locations
        self.memory["recent_locations"] = [
            loc for loc in self.memory["recent_locations"]
            if loc["timestamp"] > cutoff_str
        ]
        
        # Clear old search history
        self.memory["search_history"] = [
            search for search in self.memory["search_history"]
            if search["timestamp"] > cutoff_str
        ]
        
        self._save_memory()

# Global memory manager instance
memory_manager = MemoryManager()
