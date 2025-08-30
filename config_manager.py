import json
import os
from typing import Dict, Any

class ConfigManager:
    """Configuration manager for the Tank Battle game"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Config file {self.config_file} not found, using default configuration")
            return self.get_default_config()
        except json.JSONDecodeError as e:
            print(f"Error parsing config file: {e}")
            return self.get_default_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "game_settings": {
                "screen_width": 800,
                "screen_height": 600,
                "fps": 60,
                "tank_size": 40,
                "bullet_size": 8,
                "wall_size": 40
            },
            "enemy_settings": {
                "normal_tank": {
                    "count": 5,
                    "speed": 1.5,
                    "shot_cooldown": 800,
                    "vision_range": 120,
                    "hit_points": 1,
                    "color": "blue"
                }
            }
        }
    
    def save_config(self):
        """Save current configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            print(f"Configuration saved to {self.config_file}")
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """Set configuration value using dot notation"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def get_normal_tank_count(self) -> int:
        """Get the number of normal enemy tanks"""
        return self.get("enemy_settings.normal_tank.count", 5)
    
    def get_commander_tank_count(self) -> int:
        """Get the number of commander enemy tanks"""
        return self.get("enemy_settings.commander_tank.count", 1)
    
    def get_enemy_tank_config(self, tank_type: str) -> Dict[str, Any]:
        """Get configuration for specific tank type"""
        return self.get(f"enemy_settings.{tank_type}", {})
    
    def get_difficulty_settings(self, difficulty: str) -> Dict[str, Any]:
        """Get settings for specific difficulty level"""
        return self.get(f"difficulty_levels.{difficulty}", {})
    
    def set_difficulty(self, difficulty: str):
        """Apply difficulty settings to the configuration"""
        difficulty_settings = self.get_difficulty_settings(difficulty)
        if difficulty_settings:
            # Apply enemy count
            normal_count = difficulty_settings.get("normal_tank_count")
            if normal_count:
                self.set("enemy_settings.normal_tank.count", normal_count)
            
            # Apply multipliers
            speed_multiplier = difficulty_settings.get("enemy_speed_multiplier", 1.0)
            vision_multiplier = difficulty_settings.get("enemy_vision_multiplier", 1.0)
            attack_chance = difficulty_settings.get("enemy_attack_chance", 0.2)
            
            # Apply to normal tanks
            normal_config = self.get("enemy_settings.normal_tank", {})
            if "speed" in normal_config:
                self.set("enemy_settings.normal_tank.speed", 
                         normal_config["speed"] * speed_multiplier)
            if "vision_range" in normal_config:
                self.set("enemy_settings.normal_tank.vision_range", 
                         normal_config["vision_range"] * vision_multiplier)
            if "attack_chance" in normal_config:
                self.set("enemy_settings.normal_tank.attack_chance", attack_chance)
            
            # Apply to commander tanks
            commander_config = self.get("enemy_settings.commander_tank", {})
            if "speed" in commander_config:
                self.set("enemy_settings.commander_tank.speed", 
                         commander_config["speed"] * speed_multiplier)
            if "vision_range" in commander_config:
                self.set("enemy_settings.commander_tank.vision_range", 
                         commander_config["vision_range"] * vision_multiplier)
            if "attack_chance" in commander_config:
                self.set("enemy_settings.commander_tank.attack_chance", attack_chance)
    
    def get_game_constants(self) -> Dict[str, Any]:
        """Get all game constants"""
        return self.get("game_settings", {})
    
    def get_player_settings(self) -> Dict[str, Any]:
        """Get player tank settings"""
        return self.get("player_settings", {})
    
    def get_bullet_settings(self) -> Dict[str, Any]:
        """Get bullet settings"""
        return self.get("bullet_settings", {})
    
    def get_map_settings(self) -> Dict[str, Any]:
        """Get map generation settings"""
        return self.get("map_settings", {})
    
    def print_config(self):
        """Print current configuration"""
        print("Current Game Configuration:")
        print("=" * 50)
        print(f"Normal Enemy Tanks: {self.get_normal_tank_count()}")
        print(f"Commander Enemy Tanks: {self.get_commander_tank_count()}")
        print(f"Screen Size: {self.get('game_settings.screen_width')}x{self.get('game_settings.screen_height')}")
        print(f"FPS: {self.get('game_settings.fps')}")
        print("=" * 50)


# Global configuration instance
config = ConfigManager()

# Convenience functions
def get_config(key: str, default: Any = None) -> Any:
    """Get configuration value"""
    return config.get(key, default)

def set_config(key: str, value: Any):
    """Set configuration value"""
    config.set(key, value)

def get_normal_tank_count() -> int:
    """Get normal tank count"""
    return config.get_normal_tank_count()

def get_commander_tank_count() -> int:
    """Get commander tank count"""
    return config.get_commander_tank_count()