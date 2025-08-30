import pygame
import math
import random
from game_objects import *

# Game constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TANK_SIZE = 40

class VisionSystem:
    def __init__(self, game):
        self.game = game
        self.vision_map = {}
        self.shared_vision_enabled = True
        
    def update_vision(self):
        """Update vision for all tanks"""
        self.vision_map.clear()
        
        # First check if commander tank is alive
        commander_alive = any(tank.tank_type == TankType.ENEMY_COMMANDER and tank.is_alive 
                            for tank in self.game.tanks)
        
        # If commander tank is alive, enable shared vision
        self.shared_vision_enabled = commander_alive
        
        for tank in self.game.tanks:
            if tank.is_alive:
                self.update_tank_vision(tank)
    
    def update_tank_vision(self, tank):
        """Update vision for single tank"""
        vision_cells = set()
        
        # Calculate vision based on tank type and direction
        if tank.tank_type == TankType.PLAYER:
            # Player tanks have better vision
            forward_range = tank.vision_range
            side_range = tank.vision_range * 0.7
        else:
            # Enemy tanks have smaller vision
            forward_range = tank.vision_range * 0.8
            side_range = tank.vision_range * 0.5
        
        # Calculate vision range
        center_x = tank.x + tank.size // 2
        center_y = tank.y + tank.size // 2
        
        # Adjust vision based on direction
        if tank.direction == Direction.UP:
            vision_cells = self.calculate_vision_area(
                center_x, center_y, forward_range, side_range, 0, -1
            )
        elif tank.direction == Direction.DOWN:
            vision_cells = self.calculate_vision_area(
                center_x, center_y, forward_range, side_range, 0, 1
            )
        elif tank.direction == Direction.LEFT:
            vision_cells = self.calculate_vision_area(
                center_x, center_y, forward_range, side_range, -1, 0
            )
        elif tank.direction == Direction.RIGHT:
            vision_cells = self.calculate_vision_area(
                center_x, center_y, forward_range, side_range, 1, 0
            )
        
        # Store vision information
        tank_id = id(tank)
        self.vision_map[tank_id] = {
            'cells': vision_cells,
            'tank': tank
        }
    
    def calculate_vision_area(self, center_x, center_y, forward_range, side_range, dir_x, dir_y):
        """Calculate vision area"""
        vision_cells = set()
        
        # Calculate perpendicular direction
        perp_x = -dir_y
        perp_y = dir_x
        
        # Sample points within vision area
        for distance in range(0, int(forward_range), 10):
            for side_offset in range(-int(side_range), int(side_range), 10):
                x = center_x + dir_x * distance + perp_x * side_offset
                y = center_y + dir_y * distance + perp_y * side_offset
                
                # Check if within screen bounds
                if 0 <= x <= SCREEN_WIDTH and 0 <= y <= SCREEN_HEIGHT:
                    # Check if blocked by walls
                    if not self.is_vision_blocked(center_x, center_y, x, y):
                        vision_cells.add((int(x // 20), int(y // 20)))  # Grid
        
        return vision_cells
    
    def is_vision_blocked(self, start_x, start_y, end_x, end_y):
        """Check if vision is blocked by walls"""
        # Simple ray detection
        steps = int(max(abs(end_x - start_x), abs(end_y - start_y)) // 10)
        if steps == 0:
            return False
        
        dx = (end_x - start_x) / steps
        dy = (end_y - start_y) / steps
        
        for i in range(steps):
            check_x = start_x + dx * i
            check_y = start_y + dy * i
            
            # Check if hit wall
            for wall in self.game.walls:
                if (wall.x <= check_x <= wall.x + wall.size and 
                    wall.y <= check_y <= wall.y + wall.size):
                    return True
        
        return False
    
    def get_shared_vision(self):
        """Get shared vision"""
        if not self.shared_vision_enabled:
            return set()
        
        shared_vision = set()
        for vision_data in self.vision_map.values():
            if vision_data['tank'].tank_type != TankType.PLAYER:  # Enemy shared vision
                shared_vision.update(vision_data['cells'])
        
        return shared_vision
    
    def is_in_vision(self, tank, target_x, target_y):
        """Check if target position is in tank vision"""
        tank_id = id(tank)
        if tank_id not in self.vision_map:
            return False
        
        target_cell = (int(target_x // 20), int(target_y // 20))
        
        # Check direct vision
        if target_cell in self.vision_map[tank_id]['cells']:
            return True
        
        # Check shared vision
        if self.shared_vision_enabled and tank.tank_type != TankType.PLAYER:
            shared_vision = self.get_shared_vision()
            return target_cell in shared_vision
        
        return False
    
    def draw_vision(self, screen):
        """Draw vision (for debugging)"""
        for vision_data in self.vision_map.values():
            tank = vision_data['tank']
            cells = vision_data['cells']
            
            # Use different colors for different tank types
            if tank.tank_type == TankType.PLAYER:
                color = (0, 255, 0, 30)  # Semi-transparent green
            else:
                color = (255, 0, 0, 30)  # Semi-transparent red
            
            # Draw vision area
            for cell_x, cell_y in cells:
                rect = pygame.Rect(cell_x * 20, cell_y * 20, 20, 20)
                s = pygame.Surface((20, 20))
                s.set_alpha(30)
                s.fill(color[:3])
                screen.blit(s, rect)

class AdvancedAI:
    def __init__(self, game, vision_system):
        self.game = game
        self.vision_system = vision_system
        self.ai_states = {}  # Store AI state for each tank
        
    def update_ai(self):
        """Update behavior for all AI tanks"""
        for tank in self.game.tanks:
            if tank.tank_type != TankType.PLAYER and tank.is_alive:
                self.update_tank_ai(tank)
    
    def update_tank_ai(self, tank):
        """Update AI behavior for single tank"""
        tank_id = id(tank)
        
        # Initialize AI state
        if tank_id not in self.ai_states:
            self.ai_states[tank_id] = {
                'state': 'patrol',  # patrol, attack, defend
                'target': None,
                'last_decision_time': 0,
                'patrol_target': self.get_random_position(),
                'attack_cooldown': 0
            }
        
        current_time = pygame.time.get_ticks()
        state = self.ai_states[tank_id]
        
        # Update cooldown
        if state['attack_cooldown'] > 0:
            state['attack_cooldown'] -= 1
        
        # Make decision periodically
        if current_time - state['last_decision_time'] > 1000:  # 1 second
            self.make_ai_decision(tank, state)
            state['last_decision_time'] = current_time
        
        # Execute behavior based on state
        if state['state'] == 'patrol':
            self.execute_patrol(tank, state)
        elif state['state'] == 'attack':
            self.execute_attack(tank, state)
        elif state['state'] == 'defend':
            self.execute_defend(tank, state)
    
    def make_ai_decision(self, tank, state):
        """AI decision logic"""
        # Find player tank
        player_tank = self.find_player_tank(tank)
        
        if player_tank and self.can_see_target(tank, player_tank):
            # Can see player, enter attack state
            state['state'] = 'attack'
            state['target'] = player_tank
        elif tank.tank_type == TankType.ENEMY_COMMANDER:
            # Commander tank tends to defend base
            state['state'] = 'defend'
        else:
            # Patrol state
            state['state'] = 'patrol'
            if not state['patrol_target'] or self.reached_position(tank, state['patrol_target']):
                state['patrol_target'] = self.get_random_position()
    
    def find_player_tank(self, tank):
        """Find player tank"""
        for other_tank in self.game.tanks:
            if other_tank.tank_type == TankType.PLAYER and other_tank.is_alive:
                return other_tank
        return None
    
    def can_see_target(self, tank, target):
        """Check if can see target"""
        target_center_x = target.x + target.size // 2
        target_center_y = target.y + target.size // 2
        
        return self.vision_system.is_in_vision(tank, target_center_x, target_center_y)
    
    def execute_patrol(self, tank, state):
        """Execute patrol behavior"""
        if not state['patrol_target']:
            state['patrol_target'] = self.get_random_position()
            state['stuck_counter'] = 0
        
        # Check if tank is stuck (not moving towards target)
        old_distance = math.sqrt((tank.x - state['patrol_target'][0])**2 + (tank.y - state['patrol_target'][1])**2)
        
        # Move towards patrol target
        self.move_towards(tank, state['patrol_target'][0], state['patrol_target'][1])
        
        # Check if tank made progress
        new_distance = math.sqrt((tank.x - state['patrol_target'][0])**2 + (tank.y - state['patrol_target'][1])**2)
        
        if new_distance >= old_distance:  # Tank didn't make progress
            state['stuck_counter'] = state.get('stuck_counter', 0) + 1
            if state['stuck_counter'] > 10:  # If stuck for too long, choose new target
                state['patrol_target'] = self.get_random_position()
                state['stuck_counter'] = 0
        else:
            state['stuck_counter'] = 0
        
        # If reached patrol target, choose new one
        if new_distance < 20:
            state['patrol_target'] = self.get_random_position()
            state['stuck_counter'] = 0
        
        # Change direction randomly
        if random.random() < tank.direction_change_chance:
            tank.direction = random.choice(list(Direction))
    
    def execute_attack(self, tank, state):
        """Execute attack behavior"""
        if not state['target'] or not state['target'].is_alive:
            state['state'] = 'patrol'
            return
        
        target = state['target']
        
        # Calculate direction to target
        dx = target.x - tank.x
        dy = target.y - tank.y
        
        # Choose best direction
        if abs(dx) > abs(dy):
            if dx > 0:
                tank.direction = Direction.RIGHT
            else:
                tank.direction = Direction.LEFT
        else:
            if dy > 0:
                tank.direction = Direction.DOWN
            else:
                tank.direction = Direction.UP
        
        # Try to move towards target
        self.move_towards(tank, target.x, target.y)
        
        # If in shooting range and no cooldown, shoot
        distance = math.sqrt(dx**2 + dy**2)
        if distance < 200 and state['attack_cooldown'] == 0:
            bullet = tank.shoot()
            if bullet:
                self.game.bullets.append(bullet)
                state['attack_cooldown'] = 30  # 0.5 second cooldown
    
    def execute_defend(self, tank, state):
        """Execute defense behavior"""
        if not self.game.base:
            state['state'] = 'patrol'
            return
        
        # Patrol near base
        base_x = self.game.base.x + self.game.base.size // 2
        base_y = self.game.base.y + self.game.base.size // 2
        
        # Calculate defense position
        defend_distance = 100
        angle = random.uniform(0, 2 * math.pi)
        defend_x = base_x + math.cos(angle) * defend_distance
        defend_y = base_y + math.sin(angle) * defend_distance
        
        # Ensure defense position is within map
        defend_x = max(TANK_SIZE, min(SCREEN_WIDTH - TANK_SIZE, defend_x))
        defend_y = max(TANK_SIZE, min(SCREEN_HEIGHT - TANK_SIZE, defend_y))
        
        # Move towards defense position
        self.move_towards(tank, defend_x, defend_y)
        
        # Check for threats
        player_tank = self.find_player_tank(tank)
        if player_tank and self.can_see_target(tank, player_tank):
            state['state'] = 'attack'
            state['target'] = player_tank
    
    def move_towards(self, tank, target_x, target_y):
        """Move towards target position with intelligent obstacle avoidance"""
        dx = target_x - tank.x
        dy = target_y - tank.y
        
        # If close enough to target, don't move
        if abs(dx) <= 5 and abs(dy) <= 5:
            return
        
        # Calculate preferred movement direction
        preferred_dx = 1 if dx > 0 else -1 if dx < 0 else 0
        preferred_dy = 1 if dy > 0 else -1 if dy < 0 else 0
        
        # Try different movement strategies in order of preference
        movements = []
        
        # Primary: Move towards target
        if abs(dx) > abs(dy):
            movements = [(preferred_dx, 0), (0, preferred_dy), (0, -preferred_dy), (-preferred_dx, 0)]
        else:
            movements = [(0, preferred_dy), (preferred_dx, 0), (-preferred_dx, 0), (0, -preferred_dy)]
        
        # Try each movement option
        for move_dx, move_dy in movements:
            if move_dx == 0 and move_dy == 0:
                continue
                
            # Set tank direction
            if move_dx > 0:
                tank.direction = Direction.RIGHT
            elif move_dx < 0:
                tank.direction = Direction.LEFT
            elif move_dy > 0:
                tank.direction = Direction.DOWN
            elif move_dy < 0:
                tank.direction = Direction.UP
            
            # Check if movement is possible
            if self.game.controller and hasattr(self.game.controller, 'check_tank_wall_collision'):
                if not self.game.controller.check_tank_wall_collision(tank, move_dx, move_dy):
                    tank.move(move_dx, move_dy)
                    return
        
        # If all preferred movements are blocked, try any possible movement
        all_movements = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        for move_dx, move_dy in all_movements:
            if self.game.controller and hasattr(self.game.controller, 'check_tank_wall_collision'):
                if not self.game.controller.check_tank_wall_collision(tank, move_dx, move_dy):
                    # Set direction for this movement
                    if move_dx > 0:
                        tank.direction = Direction.RIGHT
                    elif move_dx < 0:
                        tank.direction = Direction.LEFT
                    elif move_dy > 0:
                        tank.direction = Direction.DOWN
                    elif move_dy < 0:
                        tank.direction = Direction.UP
                    
                    tank.move(move_dx, move_dy)
                    return
        
        # If completely stuck, don't move (tank will try again next frame)
    
    def get_random_position(self):
        """Get random position"""
        x = random.randint(TANK_SIZE, SCREEN_WIDTH - TANK_SIZE)
        y = random.randint(TANK_SIZE, SCREEN_HEIGHT - TANK_SIZE)
        return (x, y)
    
    def reached_position(self, tank, position):
        """Check if reached target position"""
        distance = math.sqrt((tank.x - position[0])**2 + (tank.y - position[1])**2)
        return distance < 20