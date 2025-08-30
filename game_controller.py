import pygame
import sys
import os
from game_objects import *
from game_level import *
from vision_ai import *

# Game constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TANK_SIZE = 40
BULLET_SIZE = 8

class GameController:
    def __init__(self, game):
        self.game = game
        self.level = GameLevel(game)
        self.keys_pressed = set()
        self.game_started = False
        self.show_menu = True
        self.vision_system = VisionSystem(game)
        self.ai_system = AdvancedAI(game, self.vision_system)
        
    def handle_menu_input(self, event):
        """Handle menu input"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                # Start new game - random map
                self.start_new_game(True)
            elif event.key == pygame.K_2:
                # Start new game - load map
                self.load_and_start_game()
            elif event.key == pygame.K_ESCAPE:
                self.game.running = False
    
    def start_new_game(self, use_random_map=True):
        """Start new game"""
        self.level.start_level(use_random_map)
        self.game_started = True
        self.show_menu = False
    
    def load_and_start_game(self):
        """Load and start game"""
        # Check maps folder
        if not os.path.exists('maps'):
            os.makedirs('maps')
        
        # List available map files
        map_files = [f for f in os.listdir('maps') if f.endswith('.map')]
        
        if not map_files:
            print("No map files found, using random map")
            self.start_new_game(True)
        else:
            # Select first map file
            map_file = os.path.join('maps', map_files[0])
            self.level.load_map_from_file(map_file)
            self.game_started = True
            self.show_menu = False
    
    def handle_game_input(self, event):
        """Handle game input"""
        if event.type == pygame.KEYDOWN:
            self.keys_pressed.add(event.key)
            
            # Handle player tank control
            player_tank = self.get_player_tank()
            if player_tank and player_tank.is_alive:
                if event.key == pygame.K_w:
                    player_tank.rotate(Direction.UP)
                elif event.key == pygame.K_s:
                    player_tank.rotate(Direction.DOWN)
                elif event.key == pygame.K_a:
                    player_tank.rotate(Direction.LEFT)
                elif event.key == pygame.K_d:
                    player_tank.rotate(Direction.RIGHT)
                elif event.key == pygame.K_j:
                    bullet = player_tank.shoot()
                    if bullet:
                        self.game.bullets.append(bullet)
                
                # Movement
                if event.key in [pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d]:
                    dx, dy = 0, 0
                    if event.key == pygame.K_w:
                        dy = -1
                    elif event.key == pygame.K_s:
                        dy = 1
                    elif event.key == pygame.K_a:
                        dx = -1
                    elif event.key == pygame.K_d:
                        dx = 1
                    
                    # Check collision
                    if not self.check_tank_wall_collision(player_tank, dx, dy):
                        player_tank.move(dx, dy)
            
            # Game control
            if event.key == pygame.K_r:
                # Restart
                self.start_new_game(True)
            elif event.key == pygame.K_ESCAPE:
                # Return to menu
                self.show_menu = True
                self.game_started = False
        
        elif event.type == pygame.KEYUP:
            self.keys_pressed.discard(event.key)
    
    def get_player_tank(self):
        """Get player tank"""
        for tank in self.game.tanks:
            if tank.tank_type == TankType.PLAYER:
                return tank
        return None
    
    def check_tank_wall_collision(self, tank, dx, dy):
        """Check tank-wall collision"""
        future_rect = tank.rect.copy()
        future_rect.x += dx * tank.speed
        future_rect.y += dy * tank.speed
        
        for wall in self.game.walls:
            if future_rect.colliderect(wall.rect):
                return True
        
        # Check collision with other tanks
        for other_tank in self.game.tanks:
            if other_tank != tank and other_tank.is_alive:
                if future_rect.colliderect(other_tank.rect):
                    return True
        
        return False
    
    def update(self):
        """Update game controller"""
        if not self.game_started:
            return
        
        # Update vision system
        self.vision_system.update_vision()
        
        # Update AI system
        self.ai_system.update_ai()
        
        # Handle continuous key presses for player movement
        self.handle_continuous_input()
    
    def handle_continuous_input(self):
        """Handle continuous key presses for smooth movement"""
        player_tank = self.get_player_tank()
        if not player_tank or not player_tank.is_alive:
            return
        
        # Handle movement keys - move in current direction
        dx, dy = 0, 0
        if player_tank.direction == Direction.UP:
            if pygame.K_w in self.keys_pressed:
                dy = -1
        elif player_tank.direction == Direction.DOWN:
            if pygame.K_s in self.keys_pressed:
                dy = 1
        elif player_tank.direction == Direction.LEFT:
            if pygame.K_a in self.keys_pressed:
                dx = -1
        elif player_tank.direction == Direction.RIGHT:
            if pygame.K_d in self.keys_pressed:
                dx = 1
        
        # Move tank if there's movement input
        if dx != 0 or dy != 0:
            if not self.check_tank_wall_collision(player_tank, dx, dy):
                player_tank.move(dx, dy)
    
    def check_bullet_wall_collision(self, bullet):
        """Check bullet-wall collision"""
        bullet_rect = pygame.Rect(bullet.x, bullet.y, bullet.size, bullet.size)
        
        for wall in self.game.walls:
            if bullet_rect.colliderect(wall.rect):
                return True
        
        return False
    
    def draw_menu(self):
        """Draw menu"""
        self.game.screen.fill(BLACK)
        
        font = pygame.font.Font(None, 74)
        title = font.render("Tank Battle", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 100))
        self.game.screen.blit(title, title_rect)
        
        font = pygame.font.Font(None, 36)
        options = [
            "1. Start New Game (Random Map)",
            "2. Load Map Game",
            "ESC. Exit Game"
        ]
        
        y_offset = 250
        for option in options:
            text = font.render(option, True, WHITE)
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, y_offset))
            self.game.screen.blit(text, text_rect)
            y_offset += 50
        
        # Show controls
        font = pygame.font.Font(None, 24)
        controls = [
            "Controls:",
            "WASD - Move Tank",
            "J - Fire Bullet",
            "R - Restart",
            "ESC - Return to Menu"
        ]
        
        y_offset = 450
        for control in controls:
            text = font.render(control, True, GRAY)
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, y_offset))
            self.game.screen.blit(text, text_rect)
            y_offset += 30
        
        pygame.display.flip()