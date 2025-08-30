#!/usr/bin/env python3
"""
Game test script
Test if game modules work properly
"""

import sys
import pygame

def test_imports():
    """Test module imports"""
    try:
        from game_objects import Tank, Bullet, Wall, Base, Direction, TankType, WallType
        from game_level import GameLevel
        from game_controller import GameController
        from vision_ai import VisionSystem, AdvancedAI
        print("✓ All modules imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Module import failed: {e}")
        return False

def test_game_objects():
    """Test game object creation"""
    try:
        from game_objects import Tank, Bullet, Wall, Base, Direction, TankType, WallType
        
        # 测试坦克创建
        tank = Tank(100, 100, TankType.PLAYER, (255, 0, 0), Direction.UP)
        print(f"✓ Tank created successfully: Position({tank.x}, {tank.y})")
        
        # 测试子弹创建
        bullet = tank.shoot()
        if bullet:
            print(f"✓ Bullet created successfully: Position({bullet.x}, {bullet.y})")
        
        # 测试墙壁创建
        wall = Wall(200, 200, WallType.SOIL)
        print(f"✓ Wall created successfully: Position({wall.x}, {wall.y})")
        
        # 测试总部创建
        base = Base(300, 300)
        print(f"✓ Base created successfully: Position({base.x}, {base.y})")
        
        return True
    except Exception as e:
        print(f"✗ Game object creation failed: {e}")
        return False

def test_pygame_initialization():
    """Test pygame initialization"""
    try:
        pygame.init()
        screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("测试窗口")
        print("✓ Pygame initialized successfully")
        
        # Test basic drawing
        screen.fill((0, 0, 0))
        pygame.draw.rect(screen, (255, 0, 0), (100, 100, 50, 50))
        pygame.display.flip()
        
        # 等待一下看效果
        pygame.time.wait(1000)
        
        pygame.quit()
        return True
    except Exception as e:
        print(f"✗ Pygame initialization failed: {e}")
        return False

def main():
    """Main test function"""
    print("Starting game test...")
    print("=" * 50)
    
    # 测试模块导入
    if not test_imports():
        return False
    
    # 测试游戏对象
    if not test_game_objects():
        return False
    
    # 测试pygame
    if not test_pygame_initialization():
        return False
    
    print("=" * 50)
    print("✓ All tests passed! Game can run properly.")
    print("Run 'python main.py' to start the game.")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)