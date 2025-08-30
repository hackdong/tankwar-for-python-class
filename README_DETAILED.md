# 坦克大战游戏 - 程序执行逻辑详解

## 程序概述
这是一个基于Python的坦克大战游戏，使用pygame库实现图形界面。游戏采用模块化设计，每个模块负责不同的功能， demonstrates various programming concepts through a complete game implementation.

## 程序执行流程图
```
程序启动 → main.py → game_controller.py → game_level.py → vision_ai.py → game_objects.py
```

## 1. main.py - 游戏主引擎

### 文件功能
- **主游戏引擎**：负责游戏循环、事件处理、状态管理
- **核心控制器**：协调所有游戏模块的执行
- **渲染管理**：统一管理游戏画面绘制

### 核心函数执行思路

#### 1.1 程序入口
```python
if __name__ == "__main__":
    game = Game()                    # 创建游戏对象
    from game_controller import GameController
    game.controller = GameController(game)  # 创建游戏控制器
    game.run()                       # 启动游戏循环
```

#### 1.2 Game.__init__() - 游戏初始化
```python
def __init__(self):
    self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))  # 创建游戏窗口
    self.tanks = []                   # 坦克列表初始化
    self.bullets = []                 # 子弹列表初始化
    self.walls = []                   # 墙壁列表初始化
    self.base = None                  # 基地初始化
    self.game_over = False            # 游戏结束状态
    self.winner = None                # 获胜者
```

#### 1.3 Game.run() - 游戏主循环
```python
def run(self):
    """Game main loop"""
    while self.running:
        self.handle_events()           # 处理事件
        self.update()                  # 更新游戏状态
        self.draw()                    # 绘制游戏画面
        self.clock.tick(FPS)          # 控制帧率
```

#### 1.4 Game.update() - 游戏状态更新
```python
def update(self):
    if not self.game_over:
        if self.controller:
            self.controller.update()    # 更新控制器
        
        if self.controller and self.controller.game_started:
            # 更新所有游戏对象
            for tank in self.tanks:
                tank.update()
            
            # 更新子弹
            for bullet in self.bullets[:]:
                bullet.update()
                if bullet.is_off_screen():
                    self.bullets.remove(bullet)
            
            # 检查碰撞
            self.check_collisions()
            
            # 检查游戏结束条件
            self.check_game_over()
```

#### 1.5 Game.check_collisions() - 碰撞检测
```python
def check_collisions(self):
    # 1. 子弹与墙壁碰撞
    for bullet in self.bullets[:]:
        for wall in self.walls[:]:
            if bullet.rect.colliderect(wall.rect):
                if wall.wall_type == WallType.SOIL:
                    self.walls.remove(wall)
                self.bullets.remove(bullet)
                break
    
    # 2. 子弹与坦克碰撞
    for bullet in self.bullets[:]:
        for tank in self.tanks[:]:
            if bullet.rect.colliderect(tank.rect) and bullet.owner != tank:
                tank.hit()
                if not tank.is_alive:
                    self.tanks.remove(tank)
                self.bullets.remove(bullet)
                break
    
    # 3. 子弹与基地碰撞
    for bullet in self.bullets[:]:
        if self.base and bullet.rect.colliderect(self.base.rect):
            self.game_over = True
            self.winner = "enemy"
            self.bullets.remove(bullet)
```

#### 1.6 Game.check_game_over() - 游戏结束检查
```python
def check_game_over(self):
    # 只在游戏开始后检查
    if not self.controller or not self.controller.game_started:
        return
    
    # 检查是否所有敌人都被消灭
    enemy_tanks = [t for t in self.tanks if t.tank_type != TankType.PLAYER]
    if not enemy_tanks:
        self.game_over = True
        self.winner = "player"
    
    # 检查是否所有玩家都被消灭
    player_tanks = [t for t in self.tanks if t.tank_type == TankType.PLAYER]
    if not player_tanks:
        self.game_over = True
        self.winner = "enemy"
```

## 2. game_controller.py - 游戏控制器

### 文件功能
- **输入处理**：处理键盘输入和菜单选择
- **游戏状态管理**：管理菜单、游戏进行、游戏结束等状态
- **碰撞检测**：提供精确的碰撞检测方法
- **游戏流程控制**：控制游戏的整体流程

### 核心函数执行思路

#### 2.1 GameController.__init__() - 控制器初始化
```python
def __init__(self, game):
    self.game = game                  # 引用游戏对象
    self.level = GameLevel(game)      # 创建关卡管理器
    self.show_menu = True             # 显示主菜单
    self.game_started = False         # 游戏未开始
    self.keys_pressed = set()         # 按键状态集合
    self.menu_selection = 1           # 菜单选择
    self.game_state = "menu"          # 游戏状态
```

#### 2.2 GameController.handle_menu_input() - 菜单输入处理
```python
def handle_menu_input(self, event):
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_UP:
            self.menu_selection = 1    # 选择"开始游戏"
        elif event.key == pygame.K_DOWN:
            self.menu_selection = 2    # 选择"退出游戏"
        elif event.key == pygame.K_RETURN:
            if self.menu_selection == 1:
                self.start_new_game()  # 开始新游戏
            else:
                self.game.running = False  # 退出游戏
```

#### 2.3 GameController.start_new_game() - 开始新游戏
```python
def start_new_game(self, use_random_map=True):
    """Start new game"""
    self.level.start_level(use_random_map)  # 初始化关卡
    self.game_started = True                # 标记游戏开始
    self.show_menu = False                  # 隐藏菜单
```

#### 2.4 GameController.handle_continuous_input() - 连续输入处理
```python
def handle_continuous_input(self):
    """Handle continuous key presses for smooth movement"""
    player_tank = self.get_player_tank()
    if not player_tank or not player_tank.is_alive:
        return
    
    # 根据当前方向和按键状态移动
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
    
    # 检查碰撞后移动
    if dx != 0 or dy != 0:
        if not self.check_tank_wall_collision(player_tank, dx, dy):
            player_tank.move(dx, dy)
```

#### 2.5 GameController.check_tank_wall_collision() - 坦克碰撞检测
```python
def check_tank_wall_collision(self, tank, dx, dy):
    """Check tank-wall collision"""
    future_rect = tank.rect.copy()
    future_rect.x += dx * tank.speed
    future_rect.y += dy * tank.speed
    
    # 检查与墙壁的碰撞
    for wall in self.game.walls:
        if future_rect.colliderect(wall.rect):
            return True
    
    # 检查与其他坦克的碰撞
    for other_tank in self.game.tanks:
        if other_tank != tank and other_tank.is_alive:
            if future_rect.colliderect(other_tank.rect):
                return True
    
    return False
```

## 3. game_level.py - 关卡管理器

### 文件功能
- **地图生成**：随机生成地图或从文件加载地图
- **实体管理**：管理坦克、墙壁、基地等实体的生成和放置
- **关卡配置**：根据配置文件设置关卡参数

### 核心函数执行思路

#### 3.1 GameLevel.start_level() - 开始关卡
```python
def start_level(self, use_random_map=True):
    """Start level"""
    # 清理现有游戏对象
    self.game.tanks.clear()
    self.game.bullets.clear()
    self.game.walls.clear()
    self.game.base = None
    
    # 生成地图
    if use_random_map:
        self.generate_random_map()
    else:
        self.generate_random_map()
    
    # 生成坦克
    self.spawn_tanks()
    
    # 重置游戏状态
    self.game.game_over = False
    self.game.winner = None
```

#### 3.2 GameLevel.generate_random_map() - 生成随机地图
```python
def generate_random_map(self):
    """Generate random map"""
    # 生成边界墙
    for x in range(0, SCREEN_WIDTH, WALL_SIZE):
        self.game.walls.append(Wall(x, 0, WallType.METAL))
        self.game.walls.append(Wall(x, SCREEN_HEIGHT - WALL_SIZE, WallType.METAL))
    
    for y in range(0, SCREEN_HEIGHT, WALL_SIZE):
        self.game.walls.append(Wall(0, y, WallType.METAL))
        self.game.walls.append(Wall(SCREEN_WIDTH - WALL_SIZE, y, WallType.METAL))
    
    # 生成随机土墙
    map_settings = config.get_map_settings()
    soil_wall_count = map_settings.get('random_soil_walls', 15)
    for _ in range(soil_wall_count):
        x = random.randint(2, (SCREEN_WIDTH // WALL_SIZE) - 3) * WALL_SIZE
        y = random.randint(2, (SCREEN_HEIGHT // WALL_SIZE) - 3) * WALL_SIZE
        self.game.walls.append(Wall(x, y, WallType.SOIL))
    
    # 生成随机金属墙
    metal_wall_count = map_settings.get('random_metal_walls', 8)
    for _ in range(metal_wall_count):
        x = random.randint(2, (SCREEN_WIDTH // WALL_SIZE) - 3) * WALL_SIZE
        y = random.randint(2, (SCREEN_HEIGHT // WALL_SIZE) - 3) * WALL_SIZE
        self.game.walls.append(Wall(x, y, WallType.METAL))
    
    # 放置基地
    base_x = (SCREEN_WIDTH // WALL_SIZE // 2 - 1) * WALL_SIZE
    base_y = (SCREEN_HEIGHT - WALL_SIZE * 3)
    self.game.base = Base(base_x, base_y)
    
    # 放置保护墙
    for dx in [-1, 0, 1]:
        for dy in [-1, 0]:
            wall_x = base_x + dx * WALL_SIZE
            wall_y = base_y + dy * WALL_SIZE
            if dx == 0 and dy == 0:
                continue
            self.game.walls.append(Wall(wall_x, wall_y, WallType.SOIL))
```

#### 3.3 GameLevel.spawn_tanks() - 生成坦克
```python
def spawn_tanks(self):
    """Spawn tanks"""
    # 生成玩家坦克
    player_settings = config.get_player_settings()
    player_colors = player_settings.get('colors', ['red', 'yellow'])
    player_color = self.get_color_by_name(random.choice(player_colors))
    player_x = SCREEN_WIDTH // 2 - TANK_SIZE // 2
    player_y = SCREEN_HEIGHT - TANK_SIZE * 2
    
    player_tank = Tank(player_x, player_y, TankType.PLAYER, player_color)
    
    # 应用玩家设置
    player_tank.speed = player_settings.get('speed', 2)
    player_tank.shot_cooldown = player_settings.get('shot_cooldown', 500)
    player_tank.vision_range = player_settings.get('vision_range', 150)
    player_tank.hit_points = player_settings.get('hit_points', 1)
    
    self.game.tanks.append(player_tank)
    
    # 获取敌军坦克数量
    normal_tank_count = config.get_normal_tank_count()
    commander_tank_count = config.get_commander_tank_count()
    
    # 生成指挥坦克
    for i in range(commander_tank_count):
        self.spawn_enemy_tank(TankType.ENEMY_COMMANDER, i)
    
    # 生成普通坦克
    for i in range(normal_tank_count):
        self.spawn_enemy_tank(TankType.ENEMY_NORMAL, i + commander_tank_count)
```

#### 3.4 GameLevel.spawn_enemy_tank() - 生成敌方坦克
```python
def spawn_enemy_tank(self, tank_type, index):
    """Spawn a single enemy tank with configuration"""
    tank_config = config.get_enemy_tank_config(
        'commander_tank' if tank_type == TankType.ENEMY_COMMANDER else 'normal_tank'
    )
    
    # 寻找有效位置
    max_attempts = 50
    for attempt in range(max_attempts):
        x = random.randint(1, (SCREEN_WIDTH // WALL_SIZE) - 3) * WALL_SIZE
        y = random.randint(1, 8) * WALL_SIZE
        
        # 确保不与其他坦克重叠
        valid_position = True
        for tank in self.game.tanks:
            if abs(tank.x - x) < TANK_SIZE and abs(tank.y - y) < TANK_SIZE:
                valid_position = False
                break
        
        if valid_position:
            color = self.get_color_by_name(tank_config.get('color', 'blue'))
            enemy_tank = Tank(x, y, tank_type, color)
            
            # 应用坦克配置
            enemy_tank.speed = tank_config.get('speed', 1.5)
            enemy_tank.shot_cooldown = tank_config.get('shot_cooldown', 800)
            enemy_tank.vision_range = tank_config.get('vision_range', 120)
            enemy_tank.hit_points = tank_config.get('hit_points', 1)
            
            # 设置AI参数
            enemy_tank.ai_decision_interval = tank_config.get('ai_decision_interval', 1000)
            enemy_tank.attack_chance = tank_config.get('attack_chance', 0.2)
            enemy_tank.direction_change_chance = tank_config.get('direction_change_chance', 0.3)
            
            self.game.tanks.append(enemy_tank)
            break
```

## 4. vision_ai.py - 视野和AI系统

### 文件功能
- **视野系统**：计算坦克的视野范围和视线检测
- **AI行为**：实现敌方坦克的智能行为（巡逻、攻击、防御）
- **状态管理**：管理AI状态机
- **战术决策**：基于视野和战术信息做出决策

### 核心函数执行思路

#### 4.1 VisionSystem.update_vision() - 更新视野系统
```python
def update_vision(self):
    """Update vision for all tanks"""
    self.vision_map.clear()
    
    # 检查指挥坦克是否存活
    commander_alive = any(tank.tank_type == TankType.ENEMY_COMMANDER and tank.is_alive 
                        for tank in self.game.tanks)
    
    # 如果指挥坦克存活，启用共享视野
    self.shared_vision_enabled = commander_alive
    
    # 更新每个坦克的视野
    for tank in self.game.tanks:
        if tank.is_alive:
            self.update_tank_vision(tank)
```

#### 4.2 VisionSystem.update_tank_vision() - 更新单个坦克视野
```python
def update_tank_vision(self, tank):
    """Update vision for a single tank"""
    # 计算视野参数
    if tank.tank_type == TankType.PLAYER:
        forward_range = tank.vision_range
        side_range = tank.vision_range * 0.7
    else:
        forward_range = tank.vision_range * 0.8
        side_range = tank.vision_range * 0.5
    
    # 获取方向向量
    dir_x, dir_y = self.get_direction_vector(tank.direction)
    
    # 计算视野区域
    vision_area = self.calculate_vision_area(
        tank.x + tank.size // 2, 
        tank.y + tank.size // 2,
        forward_range, side_range, dir_x, dir_y
    )
    
    # 添加到视野地图
    self.vision_map[tank] = vision_area
```

#### 4.3 AdvancedAI.update_ai() - 更新AI系统
```python
def update_ai(self):
    """Update behavior for all AI tanks"""
    for tank in self.game.tanks:
        if tank.tank_type != TankType.PLAYER and tank.is_alive:
            # 获取或创建AI状态
            if tank not in self.ai_states:
                self.ai_states[tank] = {
                    'state': 'patrol',
                    'patrol_target': None,
                    'target': None,
                    'attack_cooldown': 0,
                    'stuck_counter': 0
                }
            
            # 更新AI决策
            self.update_tank_ai(tank)
```

#### 4.4 AdvancedAI.update_tank_ai() - 更新单个坦克AI
```python
def update_tank_ai(self, tank):
    """Update AI for a single tank"""
    state = self.ai_states[tank]
    
    # 更新冷却时间
    if state['attack_cooldown'] > 0:
        state['attack_cooldown'] -= 1
    
    # 根据状态执行行为
    if state['state'] == 'patrol':
        self.execute_patrol(tank, state)
        # 检查是否发现玩家
        player_tank = self.get_player_tank()
        if player_tank and self.can_see_target(tank, player_tank):
            state['state'] = 'attack'
            state['target'] = player_tank
    
    elif state['state'] == 'attack':
        self.execute_attack(tank, state)
    
    elif state['state'] == 'defend':
        self.execute_defend(tank, state)
```

#### 4.5 AdvancedAI.execute_patrol() - 执行巡逻行为
```python
def execute_patrol(self, tank, state):
    """Execute patrol behavior"""
    if not state['patrol_target']:
        state['patrol_target'] = self.get_random_position()
        state['stuck_counter'] = 0
    
    # 检查坦克是否卡住
    old_distance = math.sqrt((tank.x - state['patrol_target'][0])**2 + 
                           (tank.y - state['patrol_target'][1])**2)
    
    # 向巡逻目标移动
    self.move_towards(tank, state['patrol_target'][0], state['patrol_target'][1])
    
    # 检查是否取得进展
    new_distance = math.sqrt((tank.x - state['patrol_target'][0])**2 + 
                           (tank.y - state['patrol_target'][1])**2)
    
    if new_distance >= old_distance:
        state['stuck_counter'] = state.get('stuck_counter', 0) + 1
        if state['stuck_counter'] > 10:
            state['patrol_target'] = self.get_random_position()
            state['stuck_counter'] = 0
    else:
        state['stuck_counter'] = 0
    
    # 如果到达巡逻目标，选择新目标
    if new_distance < 20:
        state['patrol_target'] = self.get_random_position()
        state['stuck_counter'] = 0
    
    # 随机改变方向
    if random.random() < tank.direction_change_chance:
        tank.direction = random.choice(list(Direction))
```

#### 4.6 AdvancedAI.execute_attack() - 执行攻击行为
```python
def execute_attack(self, tank, state):
    """Execute attack behavior"""
    if not state['target'] or not state['target'].is_alive:
        state['state'] = 'patrol'
        return
    
    target = state['target']
    
    # 计算到目标的距离和方向
    dx = target.x - tank.x
    dy = target.y - tank.y
    distance = math.sqrt(dx**2 + dy**2)
    
    # 如果目标超出视野，返回巡逻
    if not self.can_see_target(tank, target):
        state['state'] = 'patrol'
        state['target'] = None
        return
    
    # 调整朝向
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
    
    # 向目标移动
    self.move_towards(tank, target.x, target.y)
    
    # 如果在射程内且冷却时间为0，则射击
    if distance < 200 and state['attack_cooldown'] == 0:
        if random.random() < tank.attack_chance:
            bullet = tank.shoot()
            if bullet:
                self.game.bullets.append(bullet)
                state['attack_cooldown'] = 30
```

#### 4.7 AdvancedAI.move_towards() - 智能移动
```python
def move_towards(self, tank, target_x, target_y):
    """Move towards target position with intelligent obstacle avoidance"""
    dx = target_x - tank.x
    dy = target_y - tank.y
    
    # 如果足够接近目标，不移动
    if abs(dx) <= 5 and abs(dy) <= 5:
        return
    
    # 计算首选移动方向
    preferred_dx = 1 if dx > 0 else -1 if dx < 0 else 0
    preferred_dy = 1 if dy > 0 else -1 if dy < 0 else 0
    
    # 按优先级尝试不同的移动策略
    movements = []
    
    # 主要：向目标移动
    if abs(dx) > abs(dy):
        movements = [(preferred_dx, 0), (0, preferred_dy), (0, -preferred_dy), (-preferred_dx, 0)]
    else:
        movements = [(0, preferred_dy), (preferred_dx, 0), (-preferred_dx, 0), (0, -preferred_dy)]
    
    # 尝试每个移动选项
    for move_dx, move_dy in movements:
        if move_dx == 0 and move_dy == 0:
            continue
        
        # 设置坦克方向
        if move_dx > 0:
            tank.direction = Direction.RIGHT
        elif move_dx < 0:
            tank.direction = Direction.LEFT
        elif move_dy > 0:
            tank.direction = Direction.DOWN
        elif move_dy < 0:
            tank.direction = Direction.UP
        
        # 检查移动是否可能
        if self.game.controller and hasattr(self.game.controller, 'check_tank_wall_collision'):
            if not self.game.controller.check_tank_wall_collision(tank, move_dx, move_dy):
                tank.move(move_dx, move_dy)
                return
    
    # 如果所有首选移动都被阻挡，尝试任何可能的移动
    all_movements = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    for move_dx, move_dy in all_movements:
        if self.game.controller and hasattr(self.game.controller, 'check_tank_wall_collision'):
            if not self.game.controller.check_tank_wall_collision(tank, move_dx, move_dy):
                # 为此移动设置方向
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
    
    # 如果完全卡住，不移动（坦克将在下一帧再次尝试）
```

## 5. game_objects.py - 游戏对象定义

### 文件功能
- **实体定义**：定义所有游戏实体（坦克、子弹、墙壁、基地）
- **物理模拟**：实现移动、碰撞检测等物理效果
- **渲染实现**：提供实体的绘制方法
- **状态管理**：管理实体的生命周期和状态

### 核心函数执行思路

#### 5.1 Tank.__init__() - 坦克初始化
```python
def __init__(self, x, y, tank_type, color, direction=Direction.UP):
    self.x = x
    self.y = y
    self.size = TANK_SIZE
    self.tank_type = tank_type
    self.color = color
    self.direction = direction
    self.speed = 1.5 if tank_type != TankType.PLAYER else 2
    self.rect = pygame.Rect(x, y, self.size, self.size)
    self.is_alive = True
    self.hit_points = 2 if tank_type == TankType.ENEMY_COMMANDER else 1
    
    # 为敌方坦克添加AI相关属性
    if tank_type != TankType.PLAYER:
        self.ai_timer = 0
        self.ai_decision_interval = 1000
        self.attack_chance = 0.2
        self.direction_change_chance = 0.3
        self.target = None
        self.patrol_direction = random.choice(list(Direction))
```

#### 5.2 Tank.update() - 坦克状态更新
```python
def update(self):
    """Update tank state"""
    if not self.is_alive:
        return
    
    # 更新矩形位置
    self.rect.x = self.x
    self.rect.y = self.y
    
    # AI更新
    if self.tank_type != TankType.PLAYER:
        self.update_ai()
```

#### 5.3 Tank.move() - 坦克移动
```python
def move(self, dx, dy):
    """Move tank"""
    new_x = self.x + dx * self.speed
    new_y = self.y + dy * self.speed
    
    # 边界检查
    if 0 <= new_x <= SCREEN_WIDTH - self.size:
        self.x = new_x
    if 0 <= new_y <= SCREEN_HEIGHT - self.size:
        self.y = new_y
    
    # 更新矩形位置
    self.rect.x = self.x
    self.rect.y = self.y
```

#### 5.4 Tank.shoot() - 坦克射击
```python
def shoot(self):
    """Shoot bullet"""
    current_time = pygame.time.get_ticks()
    if current_time - self.last_shot_time < self.shot_cooldown:
        return None
    
    self.last_shot_time = current_time
    
    # 计算子弹生成位置
    bullet_x = self.x + self.size // 2
    bullet_y = self.y + self.size // 2
    
    # 根据方向调整子弹位置
    if self.direction == Direction.UP:
        bullet_y -= self.size // 2 + BULLET_SIZE
    elif self.direction == Direction.DOWN:
        bullet_y += self.size // 2 + BULLET_SIZE
    elif self.direction == Direction.LEFT:
        bullet_x -= self.size // 2 + BULLET_SIZE
    elif self.direction == Direction.RIGHT:
        bullet_x += self.size // 2 + BULLET_SIZE
    
    return Bullet(bullet_x, bullet_y, self.direction, self)
```

#### 5.5 Tank.hit() - 坦克被击中
```python
def hit(self):
    """Tank is hit"""
    self.hit_points -= 1
    if self.hit_points <= 0:
        self.is_alive = False
```

#### 5.6 Bullet.__init__() - 子弹初始化
```python
def __init__(self, x, y, direction, owner):
    self.x = x
    self.y = y
    self.direction = direction
    self.owner = owner
    self.size = BULLET_SIZE
    self.speed = 5
    self.rect = pygame.Rect(x, y, self.size, self.size)
    
    # 设置子弹颜色
    if owner.tank_type == TankType.PLAYER:
        self.color = YELLOW
    else:
        self.color = RED
```

#### 5.7 Bullet.update() - 子弹更新
```python
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
```

#### 5.8 Bullet.is_off_screen() - 检查子弹是否超出屏幕
```python
def is_off_screen(self):
    """Check if bullet is off screen"""
    return (self.x < 0 or self.x > SCREEN_WIDTH or 
            self.y < 0 or self.y > SCREEN_HEIGHT)
```

## 6. config_manager.py - 配置管理器

### 文件功能
- **配置加载**：从JSON文件加载游戏配置
- **配置管理**：提供配置值的读取和设置
- **难度系统**：支持不同难度级别的配置
- **游戏模式**：支持不同游戏模式的配置

### 核心函数执行思路

#### 6.1 ConfigManager.__init__() - 配置管理器初始化
```python
def __init__(self, config_file: str = "config.json"):
    self.config_file = config_file
    self.config = self.load_config()
```

#### 6.2 ConfigManager.load_config() - 加载配置
```python
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
```

#### 6.3 ConfigManager.get() - 获取配置值
```python
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
```

#### 6.4 ConfigManager.set() - 设置配置值
```python
def set(self, key: str, value: Any):
    """Set configuration value using dot notation"""
    keys = key.split('.')
    config = self.config
    
    for k in keys[:-1]:
        if k not in config:
            config[k] = {}
        config = config[k]
    
    config[keys[-1]] = value
```

## 7. config.json - 配置文件

### 文件功能
- **参数配置**：定义游戏的各种参数
- **难度设置**：配置不同难度级别的参数
- **游戏模式**：配置不同游戏模式的规则
- **AI参数**：配置AI行为的各种参数

### 配置结构
```json
{
    "game_settings": {
        "screen_width": 800,
        "screen_height": 600,
        "fps": 60,
        "tank_size": 40,
        "bullet_size": 8,
        "wall_size": 40
    },
    "player_settings": {
        "speed": 2,
        "shot_cooldown": 500,
        "vision_range": 150,
        "hit_points": 1,
        "colors": ["red", "yellow"]
    },
    "enemy_settings": {
        "normal_tank": {
            "count": 3,
            "speed": 1.5,
            "shot_cooldown": 800,
            "vision_range": 120,
            "hit_points": 1,
            "color": "blue",
            "ai_decision_interval": 1000,
            "attack_chance": 0.2,
            "direction_change_chance": 0.3
        },
        "commander_tank": {
            "count": 1,
            "speed": 1.8,
            "shot_cooldown": 600,
            "vision_range": 180,
            "hit_points": 2,
            "color": "green",
            "ai_decision_interval": 800,
            "attack_chance": 0.3,
            "direction_change_chance": 0.2,
            "defense_range": 150
        }
    },
    "difficulty_levels": {
        "easy": {
            "normal_tank_count": 3,
            "enemy_speed_multiplier": 0.8,
            "enemy_vision_multiplier": 0.7,
            "enemy_attack_chance": 0.15
        },
        "medium": {
            "normal_tank_count": 5,
            "enemy_speed_multiplier": 1.0,
            "enemy_vision_multiplier": 1.0,
            "enemy_attack_chance": 0.2
        },
        "hard": {
            "normal_tank_count": 8,
            "enemy_speed_multiplier": 1.3,
            "enemy_vision_multiplier": 1.3,
            "enemy_attack_chance": 0.3
        }
    }
}
```

## 总结

这个坦克大战游戏采用模块化设计，每个模块负责不同的功能：

1. **main.py** - 主游戏引擎，负责游戏循环和状态管理
2. **game_controller.py** - 游戏控制器，负责输入处理和游戏流程
3. **game_level.py** - 关卡管理器，负责地图生成和实体管理
4. **vision_ai.py** - 视野和AI系统，负责智能行为和视野计算
5. **game_objects.py** - 游戏对象定义，负责实体和物理模拟
6. **config_manager.py** - 配置管理器，负责配置加载和管理
7. **config.json** - 配置文件，定义游戏参数和规则

整个游戏采用事件驱动架构，具有智能的AI系统、完整的碰撞检测、灵活的配置系统，是一个很好的Python编程教学案例。