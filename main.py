import pygame
import sys

# 初始化Pygame
pygame.init()

# 游戏常量
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TANK_SIZE = 40
BULLET_SIZE = 8
WALL_SIZE = 40
FPS = 60

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)
BROWN = (139, 69, 19)
DARK_GRAY = (64, 64, 64)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tank Battle - Python Tutorial")
        self.clock = pygame.time.Clock()
        self.running = True
        self.tanks = []
        self.bullets = []
        self.walls = []
        self.base = None
        self.game_over = False
        self.winner = None
        self.controller: GameController | None = None    # Will be set to GameController instance at runtime
    
    def run(self):
        """Game main loop"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()
    
    def handle_events(self):
        """Handle game events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
            
            # Use controller to handle input
            if self.controller:
                if self.controller.show_menu:
                    self.controller.handle_menu_input(event)
                else:
                    self.controller.handle_game_input(event)
    
    def update(self):
        """Update game state"""
        if not self.game_over:
            # Update controller
            if self.controller:
                self.controller.update()
            
            # Only update game logic if game has started
            if self.controller and self.controller.game_started:
                # Update tanks
                for tank in self.tanks:
                    tank.update()
                
                # Update bullets
                for bullet in self.bullets[:]:
                    bullet.update()
                    if bullet.is_off_screen():
                        self.bullets.remove(bullet)
                
                # Check collisions
                self.check_collisions()
                
                # Check game over conditions
                self.check_game_over()
    
    def draw(self):
        """Draw game screen"""
        # If controller exists and shows menu, draw menu
        if self.controller and self.controller.show_menu:
            self.controller.draw_menu()
            return
        
        self.screen.fill(BLACK)
        
        # Draw walls
        for wall in self.walls:
            wall.draw(self.screen)
        
        # Draw base
        if self.base:
            self.base.draw(self.screen)
        
        # Draw tanks
        for tank in self.tanks:
            tank.draw(self.screen)
        
        # Draw bullets
        for bullet in self.bullets:
            bullet.draw(self.screen)
        
        # Draw game over info
        if self.game_over:
            self.draw_game_over()
        
        pygame.display.flip()
    
    def draw_game_over(self):
        """Draw game over screen"""
        font = pygame.font.Font(None, 74)
        if self.winner == "player":
            text = font.render("Player Wins!", True, GREEN)
        else:
            text = font.render("Game Over!", True, RED)
        
        text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        self.screen.blit(text, text_rect)
    
    def check_collisions(self):
        """Check collisions"""
        from game_objects import WallType
        
        # Bullet-wall collisions
        for bullet in self.bullets[:]:
            for wall in self.walls[:]:
                if bullet.rect.colliderect(wall.rect):
                    if wall.wall_type == WallType.SOIL:
                        self.walls.remove(wall)
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    break
        
        # Bullet-tank collisions
        for bullet in self.bullets[:]:
            for tank in self.tanks[:]:
                if bullet.rect.colliderect(tank.rect) and bullet.owner != tank:
                    # Add a small delay to prevent immediate collision with owner
                    tank.hit()
                    # Remove tank from list if destroyed
                    if not tank.is_alive and tank in self.tanks:
                        self.tanks.remove(tank)
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    break
        
        # Bullet-base collisions
        for bullet in self.bullets[:]:
            if self.base and bullet.rect.colliderect(self.base.rect):
                self.game_over = True
                self.winner = "en玩家emy"
                if bullet in self.bullets:
                    self.bullets.remove(bullet)
    
    def check_game_over(self):
        """Check game over conditions"""
        # Only check game over if game has started
        if not self.controller or not self.controller.game_started:
            return
        
        # Import enums from game_objects
        from game_objects import TankType
        
        # Check if all enemies are destroyed
        enemy_tanks = [t for t in self.tanks if t.tank_type != TankType.PLAYER]
        if not enemy_tanks:
            self.game_over = True
            self.winner = "player"
        
        # Check if all players are destroyed
        player_tanks = [t for t in self.tanks if t.tank_type == TankType.PLAYER]
        if not player_tanks:
            self.game_over = True
            self.winner = "enemy"

if __name__ == "__main__":
    game = Game()
    from game_controller import GameController
    game.controller = GameController(game)
    game.run()