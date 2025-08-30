import pygame
import random
from enum import Enum

# Game constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TANK_SIZE = 40
BULLET_SIZE = 8
WALL_SIZE = 40

# Color definitions
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)
BROWN = (139, 69, 19)
DARK_GRAY = (64, 64, 64)

# Direction enum
class Direction(Enum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3

# Tank type enum
class TankType(Enum):
    PLAYER = 1
    ENEMY_NORMAL = 2
    ENEMY_COMMANDER = 3

# Wall type enum
class WallType(Enum):
    SOIL = 1  # Soil wall
    METAL = 2  # Metal wall
    BASE = 3   # Base

class Tank:
    def __init__(self, x, y, tank_type, color, direction=Direction.UP):
        self.x = x
        self.y = y
        self.tank_type = tank_type
        self.color = color
        self.direction = direction
        self.speed = 2
        self.size = TANK_SIZE
        self.rect = pygame.Rect(x, y, self.size, self.size)
        self.last_shot_time = 0
        self.shot_cooldown = 500  # milliseconds
        self.vision_range = 150
        self.is_alive = True
        self.hit_points = 2 if tank_type == TankType.ENEMY_COMMANDER else 1
        
        # Add AI-related properties for enemy tanks
        if tank_type != TankType.PLAYER:
            self.ai_timer = 0
            self.ai_decision_interval = 1000  # milliseconds
            self.attack_chance = 0.2  # probability of attacking when player is in range
            self.direction_change_chance = 0.3  # probability of changing direction during patrol
            self.target = None
            self.patrol_direction = random.choice(list(Direction))
    
    def update(self):
        """Update tank state"""
        if not self.is_alive:
            return
        
        self.rect.x = self.x
        self.rect.y = self.y
        
        # AI update
        if self.tank_type != TankType.PLAYER:
            self.update_ai()
    
    def move(self, dx, dy):
        """Move tank"""
        new_x = self.x + dx * self.speed
        new_y = self.y + dy * self.speed
        
        # Boundary check
        if 0 <= new_x <= SCREEN_WIDTH - self.size:
            self.x = new_x
        if 0 <= new_y <= SCREEN_HEIGHT - self.size:
            self.y = new_y
        
        # Update rect position
        self.rect.x = self.x
        self.rect.y = self.y
    
    def rotate(self, direction):
        """Rotate tank direction"""
        self.direction = direction
    
    def shoot(self):
        """Shoot bullet"""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time < self.shot_cooldown:
            return None
        
        self.last_shot_time = current_time
        
        # Calculate bullet initial position
        bullet_x = self.x + self.size // 2 - BULLET_SIZE // 2
        bullet_y = self.y + self.size // 2 - BULLET_SIZE // 2
        
        # Adjust bullet position based on direction
        if self.direction == Direction.UP:
            bullet_y = self.y - BULLET_SIZE - 5
        elif self.direction == Direction.DOWN:
            bullet_y = self.y + self.size + 5
        elif self.direction == Direction.LEFT:
            bullet_x = self.x - BULLET_SIZE - 5
        elif self.direction == Direction.RIGHT:
            bullet_x = self.x + self.size + 5
        
        return Bullet(bullet_x, bullet_y, self.direction, self)
    
    def hit(self):
        """Tank is hit"""
        self.hit_points -= 1
        if self.hit_points <= 0:
            self.is_alive = False
    
    def draw(self, screen):
        """Draw tank"""
        if not self.is_alive:
            return
        
        # Draw tank body
        pygame.draw.rect(screen, self.color, self.rect)
        
        # Draw tank barrel
        center_x = self.x + self.size // 2
        center_y = self.y + self.size // 2
        
        if self.direction == Direction.UP:
            pygame.draw.rect(screen, self.color, 
                           (center_x - 3, self.y - 10, 6, 15))
        elif self.direction == Direction.DOWN:
            pygame.draw.rect(screen, self.color, 
                           (center_x - 3, self.y + self.size - 5, 6, 15))
        elif self.direction == Direction.LEFT:
            pygame.draw.rect(screen, self.color, 
                           (self.x - 10, center_y - 3, 15, 6))
        elif self.direction == Direction.RIGHT:
            pygame.draw.rect(screen, self.color, 
                           (self.x + self.size - 5, center_y - 3, 15, 6))
        
        # Draw commander tank indicator
        if self.tank_type == TankType.ENEMY_COMMANDER:
            pygame.draw.circle(screen, WHITE, 
                             (center_x, center_y), 8)
            pygame.draw.circle(screen, RED, 
                             (center_x, center_y), 5)
    
    def update_ai(self):
        """Update AI behavior"""
        current_time = pygame.time.get_ticks()
        if current_time - self.ai_timer < self.ai_decision_interval:
            return
        
        self.ai_timer = current_time
        
        # Simple AI logic
        if random.random() < 0.3:  # 30% chance to change direction
            self.direction = random.choice(list(Direction))
        
        # Movement
        if self.direction == Direction.UP:
            self.move(0, -1)
        elif self.direction == Direction.DOWN:
            self.move(0, 1)
        elif self.direction == Direction.LEFT:
            self.move(-1, 0)
        elif self.direction == Direction.RIGHT:
            self.move(1, 0)
        
        # Random shooting
        if random.random() < 0.2:  # 20% chance to shoot
            return self.shoot()
        
        return None

class Bullet:
    def __init__(self, x, y, direction, owner):
        self.x = x
        self.y = y
        self.direction = direction
        self.owner = owner
        self.speed = 5
        self.size = BULLET_SIZE
        self.rect = pygame.Rect(x, y, self.size, self.size)
    
    def update(self):
        """Update bullet position"""
        if self.direction == Direction.UP:
            self.y -= self.speed
        elif self.direction == Direction.DOWN:
            self.y += self.speed
        elif self.direction == Direction.LEFT:
            self.x -= self.speed
        elif self.direction == Direction.RIGHT:
            self.x += self.speed
        
        self.rect.x = self.x
        self.rect.y = self.y
    
    def is_off_screen(self):
        """Check if bullet is off screen"""
        return (self.x < 0 or self.x > SCREEN_WIDTH or 
                self.y < 0 or self.y > SCREEN_HEIGHT)
    
    def draw(self, screen):
        """Draw bullet"""
        pygame.draw.circle(screen, YELLOW, 
                         (self.x + self.size // 2, self.y + self.size // 2), 
                         self.size // 2)

class Wall:
    def __init__(self, x, y, wall_type):
        self.x = x
        self.y = y
        self.wall_type = wall_type
        self.size = WALL_SIZE
        self.rect = pygame.Rect(x, y, self.size, self.size)
    
    def draw(self, screen):
        """Draw wall"""
        if self.wall_type == WallType.SOIL:
            pygame.draw.rect(screen, BROWN, self.rect)
            pygame.draw.rect(screen, BLACK, self.rect, 2)
        elif self.wall_type == WallType.METAL:
            pygame.draw.rect(screen, GRAY, self.rect)
            pygame.draw.rect(screen, DARK_GRAY, self.rect, 3)

class Base:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = WALL_SIZE
        self.rect = pygame.Rect(x, y, self.size, self.size)
    
    def draw(self, screen):
        """Draw base"""
        # Draw base platform
        pygame.draw.rect(screen, DARK_GRAY, self.rect)
        
        # Draw red flag
        flag_x = self.x + self.size // 2
        flag_y = self.y + 5
        pygame.draw.line(screen, BLACK, (flag_x, flag_y), (flag_x, flag_y + 20), 2)
        pygame.draw.polygon(screen, RED, [
            (flag_x, flag_y),
            (flag_x + 15, flag_y + 5),
            (flag_x, flag_y + 10)
        ])