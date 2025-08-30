#!/usr/bin/env python3
"""
Test tank movement and bullet functionality
"""

import pygame
import sys
from game_objects import Tank, Direction, TankType

def test_tank_movement():
    """Test tank movement functionality"""
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Tank Movement Test")
    clock = pygame.time.Clock()
    
    # Create a player tank
    tank = Tank(100, 100, TankType.PLAYER, (255, 0, 0), Direction.UP)
    bullets = []
    
    # Test keys
    keys_pressed = set()
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                keys_pressed.add(event.key)
                
                # Handle tank rotation
                if event.key == pygame.K_w:
                    tank.rotate(Direction.UP)
                elif event.key == pygame.K_s:
                    tank.rotate(Direction.DOWN)
                elif event.key == pygame.K_a:
                    tank.rotate(Direction.LEFT)
                elif event.key == pygame.K_d:
                    tank.rotate(Direction.RIGHT)
                elif event.key == pygame.K_j:
                    bullet = tank.shoot()
                    if bullet:
                        bullets.append(bullet)
                elif event.key == pygame.K_ESCAPE:
                    running = False
            
            elif event.type == pygame.KEYUP:
                keys_pressed.discard(event.key)
        
        # Handle continuous movement
        dx, dy = 0, 0
        if tank.direction == Direction.UP and pygame.K_w in keys_pressed:
            dy = -1
        elif tank.direction == Direction.DOWN and pygame.K_s in keys_pressed:
            dy = 1
        elif tank.direction == Direction.LEFT and pygame.K_a in keys_pressed:
            dx = -1
        elif tank.direction == Direction.RIGHT and pygame.K_d in keys_pressed:
            dx = 1
        
        if dx != 0 or dy != 0:
            tank.move(dx, dy)
        
        # Update bullets
        for bullet in bullets[:]:
            bullet.update()
            if bullet.is_off_screen():
                bullets.remove(bullet)
        
        # Draw everything
        screen.fill((0, 0, 0))
        tank.draw(screen)
        for bullet in bullets:
            bullet.draw(screen)
        
        # Draw instructions
        font = pygame.font.Font(None, 24)
        instructions = [
            "WASD: Rotate tank",
            "Hold direction key: Move tank",
            "J: Shoot bullet",
            "ESC: Exit"
        ]
        
        y_offset = 10
        for instruction in instructions:
            text = font.render(instruction, True, (255, 255, 255))
            screen.blit(text, (10, y_offset))
            y_offset += 25
        
        # Draw tank position
        pos_text = font.render(f"Tank Position: ({tank.x}, {tank.y})", True, (255, 255, 255))
        screen.blit(pos_text, (10, y_offset))
        
        # Draw bullet count
        bullet_text = font.render(f"Bullets: {len(bullets)}", True, (255, 255, 255))
        screen.blit(bullet_text, (10, y_offset + 25))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    test_tank_movement()