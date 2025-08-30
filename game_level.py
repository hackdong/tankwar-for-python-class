import pygame
import random
from game_objects import *
from config_manager import config

# Game constants from config
SCREEN_WIDTH = config.get('game_settings.screen_width', 800)
SCREEN_HEIGHT = config.get('game_settings.screen_height', 600)
TANK_SIZE = config.get('game_settings.tank_size', 40)
WALL_SIZE = config.get('game_settings.wall_size', 40)

class GameLevel:
    def __init__(self, game):
        self.game = game
        self.level = 1
        self.player_count = 1
        
    def generate_random_map(self):
        """Generate random map"""
        self.game.walls.clear()
        self.game.tanks.clear()
        self.game.bullets.clear()
        
        # Generate boundary walls
        for x in range(0, SCREEN_WIDTH, WALL_SIZE):
            self.game.walls.append(Wall(x, 0, WallType.METAL))
            self.game.walls.append(Wall(x, SCREEN_HEIGHT - WALL_SIZE, WallType.METAL))
        
        for y in range(0, SCREEN_HEIGHT, WALL_SIZE):
            self.game.walls.append(Wall(0, y, WallType.METAL))
            self.game.walls.append(Wall(SCREEN_WIDTH - WALL_SIZE, y, WallType.METAL))
        
        # Generate random soil walls
        map_settings = config.get_map_settings()
        soil_wall_count = map_settings.get('random_soil_walls', 15)
        for _ in range(soil_wall_count):
            x = random.randint(2, (SCREEN_WIDTH // WALL_SIZE) - 3) * WALL_SIZE
            y = random.randint(2, (SCREEN_HEIGHT // WALL_SIZE) - 3) * WALL_SIZE
            self.game.walls.append(Wall(x, y, WallType.SOIL))
        
        # Generate random metal walls
        metal_wall_count = map_settings.get('random_metal_walls', 8)
        for _ in range(metal_wall_count):
            x = random.randint(2, (SCREEN_WIDTH // WALL_SIZE) - 3) * WALL_SIZE
            y = random.randint(2, (SCREEN_HEIGHT // WALL_SIZE) - 3) * WALL_SIZE
            self.game.walls.append(Wall(x, y, WallType.METAL))
        
        # Place base
        base_x = (SCREEN_WIDTH // WALL_SIZE // 2 - 1) * WALL_SIZE
        base_y = (SCREEN_HEIGHT - WALL_SIZE * 3)
        self.game.base = Base(base_x, base_y)
        
        # Place protective walls around base
        for dx in [-1, 0, 1]:
            for dy in [-1, 0]:
                wall_x = base_x + dx * WALL_SIZE
                wall_y = base_y + dy * WALL_SIZE
                if dx == 0 and dy == 0:
                    continue  # Skip base position
                self.game.walls.append(Wall(wall_x, wall_y, WallType.SOIL))
    
    def spawn_tanks(self):
        """Spawn tanks"""
        # Generate player tank
        player_settings = config.get_player_settings()
        player_colors = player_settings.get('colors', ['red', 'yellow'])
        player_color = self.get_color_by_name(random.choice(player_colors))
        player_x = SCREEN_WIDTH // 2 - TANK_SIZE // 2
        player_y = SCREEN_HEIGHT - TANK_SIZE * 2
        
        player_tank = Tank(player_x, player_y, TankType.PLAYER, player_color)
        
        # Apply player settings
        player_tank.speed = player_settings.get('speed', 2)
        player_tank.shot_cooldown = player_settings.get('shot_cooldown', 500)
        player_tank.vision_range = player_settings.get('vision_range', 150)
        player_tank.hit_points = player_settings.get('hit_points', 1)
        
        self.game.tanks.append(player_tank)
        
        # Get enemy tank counts from config
        normal_tank_count = config.get_normal_tank_count()
        commander_tank_count = config.get_commander_tank_count()
        
        # Spawn commander tanks
        for i in range(commander_tank_count):
            self.spawn_enemy_tank(TankType.ENEMY_COMMANDER, i)
        
        # Spawn normal tanks
        for i in range(normal_tank_count):
            self.spawn_enemy_tank(TankType.ENEMY_NORMAL, i + commander_tank_count)
    
    def spawn_enemy_tank(self, tank_type, index):
        """Spawn a single enemy tank with configuration"""
        tank_config = config.get_enemy_tank_config(
            'commander_tank' if tank_type == TankType.ENEMY_COMMANDER else 'normal_tank'
        )
        
        # Find valid position
        max_attempts = 50
        for attempt in range(max_attempts):
            x = random.randint(1, (SCREEN_WIDTH // WALL_SIZE) - 3) * WALL_SIZE
            y = random.randint(1, 8) * WALL_SIZE
            
            # Ensure no overlap with other tanks
            valid_position = True
            for tank in self.game.tanks:
                if abs(tank.x - x) < TANK_SIZE and abs(tank.y - y) < TANK_SIZE:
                    valid_position = False
                    break
            
            if valid_position:
                color = self.get_color_by_name(tank_config.get('color', 'blue'))
                enemy_tank = Tank(x, y, tank_type, color)
                
                # Apply tank configuration
                enemy_tank.speed = tank_config.get('speed', 1.5)
                enemy_tank.shot_cooldown = tank_config.get('shot_cooldown', 800)
                enemy_tank.vision_range = tank_config.get('vision_range', 120)
                enemy_tank.hit_points = tank_config.get('hit_points', 1)
                
                # Set AI parameters
                enemy_tank.ai_decision_interval = tank_config.get('ai_decision_interval', 1000)
                enemy_tank.attack_chance = tank_config.get('attack_chance', 0.2)
                enemy_tank.direction_change_chance = tank_config.get('direction_change_chance', 0.3)
                
                self.game.tanks.append(enemy_tank)
                break
    
    def get_color_by_name(self, color_name):
        """Convert color name to RGB tuple"""
        color_map = {
            'red': RED,
            'yellow': YELLOW,
            'green': GREEN,
            'blue': BLUE,
            'white': WHITE,
            'black': BLACK,
            'gray': GRAY,
            'brown': BROWN,
            'dark_gray': DARK_GRAY
        }
        return color_map.get(color_name.lower(), BLUE)
    
    def load_map_from_file(self, filename):
        """Load map from file"""
        try:
            with open(filename, 'r') as f:
                lines = f.readlines()
            
            self.game.walls.clear()
            self.game.tanks.clear()
            self.game.bullets.clear()
            
            for y, line in enumerate(lines):
                for x, char in enumerate(line.strip()):
                    if char == '#':  # Soil wall
                        self.game.walls.append(Wall(x * WALL_SIZE, y * WALL_SIZE, WallType.SOIL))
                    elif char == '@':  # Metal wall
                        self.game.walls.append(Wall(x * WALL_SIZE, y * WALL_SIZE, WallType.METAL))
                    elif char == 'B':  # Base
                        self.game.base = Base(x * WALL_SIZE, y * WALL_SIZE)
                    elif char == 'P':  # Player
                        player_tank = Tank(x * WALL_SIZE, y * WALL_SIZE, TankType.PLAYER, RED)
                        self.game.tanks.append(player_tank)
                    elif char == 'E':  # Enemy
                        enemy_tank = Tank(x * WALL_SIZE, y * WALL_SIZE, TankType.ENEMY_NORMAL, BLUE)
                        self.game.tanks.append(enemy_tank)
                    elif char == 'C':  # Commander tank
                        commander_tank = Tank(x * WALL_SIZE, y * WALL_SIZE, TankType.ENEMY_COMMANDER, GREEN)
                        self.game.tanks.append(commander_tank)
        
        except FileNotFoundError:
            print(f"Map file {filename} does not exist, using random map")
            self.generate_random_map()
            self.spawn_tanks()
    
    def save_map_to_file(self, filename):
        """Save map to file"""
        map_data = []
        for y in range(0, SCREEN_HEIGHT, WALL_SIZE):
            row = []
            for x in range(0, SCREEN_WIDTH, WALL_SIZE):
                char = '.'
                
                # Check if there is a wall
                for wall in self.game.walls:
                    if wall.x == x and wall.y == y:
                        if wall.wall_type == WallType.SOIL:
                            char = '#'
                        elif wall.wall_type == WallType.METAL:
                            char = '@'
                        break
                
                # Check if there is a base
                if self.game.base and self.game.base.x == x and self.game.base.y == y:
                    char = 'B'
                
                # Check if there is a tank
                for tank in self.game.tanks:
                    if tank.x == x and tank.y == y:
                        if tank.tank_type == TankType.PLAYER:
                            char = 'P'
                        elif tank.tank_type == TankType.ENEMY_NORMAL:
                            char = 'E'
                        elif tank.tank_type == TankType.ENEMY_COMMANDER:
                            char = 'C'
                        break
                
                row.append(char)
            map_data.append(''.join(row))
        
        with open(filename, 'w') as f:
            f.write('\n'.join(map_data))
    
    def start_level(self, use_random_map=True):
        """Start level"""
        # Clear existing game objects
        self.game.tanks.clear()
        self.game.bullets.clear()
        self.game.walls.clear()
        self.game.base = None
        
        if use_random_map:
            self.generate_random_map()
        else:
            # Here you can add logic to load preset maps
            self.generate_random_map()
        
        self.spawn_tanks()
        self.game.game_over = False
        self.game.winner = None