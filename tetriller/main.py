# main.py - ИСПРАВЛЕННАЯ ВЕРСИЯ БЕЗ БАГОВ
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Rectangle, Line, Ellipse
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import NumericProperty
from kivy.metrics import dp
import random
import math

# Game constants
CELL_SIZE = dp(30)
BASE_GRID_WIDTH = 10
GRID_HEIGHT = 20
MAX_LEVEL = 5
DEATH_PAUSE_DURATION = 2.0

COLORS = {
    1: (1, 0, 0, 1),      # Red
    2: (0, 1, 0, 1),      # Green
    3: (0, 0, 1, 1),      # Blue
    4: (1, 1, 0, 1),      # Yellow
    5: (1, 0, 1, 1),      # Magenta
    6: (0, 1, 1, 1),      # Cyan
    7: (1, 0.5, 0, 1),    # Orange
}

SHAPES = [
    [[0, 0, 0, 0], [1, 1, 1, 1], [0, 0, 0, 0], [0, 0, 0, 0]],
    [[2, 0, 0], [2, 2, 2], [0, 0, 0]],
    [[0, 0, 3], [3, 3, 3], [0, 0, 0]],
    [[4, 4], [4, 4]],
    [[0, 5, 5], [5, 5, 0], [0, 0, 0]],
    [[0, 6, 0], [6, 6, 6], [0, 0, 0]],
    [[7, 7, 0], [0, 7, 7], [0, 0, 0]]
]

class GameWidget(Widget):
    score = NumericProperty(0)
    level = NumericProperty(1)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (0.7, 1)
        
        # Game state
        self.grid_width = self.get_grid_width_for_level(self.level)
        self.escape_height = self.get_escape_door_height(self.level)
        self.grid = self.create_empty_grid()
        self.game_over = False
        self.game_active = False
        self.prisoner_died = False
        self.death_timestamp = 0
        self.message = ""
        
        # Tetris mechanics
        self.drop_counter = 0
        self.drop_interval = 1.0
        self.current_piece = None
        self.current_pos = {'x': 0, 'y': 0}
        
        # Prisoner
        self.prisoner = {
            'x': self.grid_width / 2,
            'y': GRID_HEIGHT - 2,
            'direction': 1,
            'escaped': False,
            'move_timer': 0,
            'move_delay': 0.5
        }
        
        self.create_piece()
        
        # Start update loops
        Clock.schedule_interval(self.update, 1/60)
        Clock.schedule_interval(self.draw, 1/60)
    
    def get_grid_width_for_level(self, level):
        return BASE_GRID_WIDTH + (level - 1) * 2
    
    def get_escape_door_height(self, level):
        heights = {
            1: GRID_HEIGHT - 3,
            2: GRID_HEIGHT - 6, 
            3: GRID_HEIGHT - 9,
            4: GRID_HEIGHT - 12,
            5: GRID_HEIGHT - 15
        }
        return heights.get(level, GRID_HEIGHT - 3)
    
    def create_empty_grid(self):
        return [[0 for _ in range(self.grid_width)] for _ in range(GRID_HEIGHT)]
    
    def create_piece(self):
        shape_index = random.randint(0, len(SHAPES) - 1)
        shape = [row[:] for row in SHAPES[shape_index]]
        
        self.current_piece = shape
        self.current_pos['x'] = (self.grid_width - len(shape[0])) // 2
        self.current_pos['y'] = 0
        
        if self.check_collision():
            self.game_over = True
            self.message = "GAME OVER - Blocks reached top!"
            self.game_active = False
    
    def check_collision(self):
        for y in range(len(self.current_piece)):
            for x in range(len(self.current_piece[y])):
                if self.current_piece[y][x] != 0:
                    grid_x = self.current_pos['x'] + x
                    grid_y = self.current_pos['y'] + y
                    
                    if grid_x < 0 or grid_x >= self.grid_width or grid_y >= GRID_HEIGHT:
                        return True
                    
                    if grid_y >= 0 and self.grid[grid_y][grid_x] != 0:
                        return True
                    
                    if (int(self.prisoner['x']) == grid_x and 
                        self.prisoner['y'] == grid_y and 
                        not self.prisoner_died):
                        self.prisoner_died = True
                        self.death_timestamp = Clock.get_time()
                        self.game_over = True
                        self.message = "PRISONER CRUSHED!"
                        return True
        return False
    
    def check_prisoner_stuck(self):
        """Проверяет, не застрял ли заключенный внутри фигуры"""
        prisoner_x = int(self.prisoner['x'])
        prisoner_y = self.prisoner['y']
        
        if 0 <= prisoner_x < self.grid_width and 0 <= prisoner_y < GRID_HEIGHT:
            if self.grid[prisoner_y][prisoner_x] != 0:
                self.prisoner_died = True
                self.death_timestamp = Clock.get_time()
                self.game_over = True
                self.message = "PRISONER STUCK IN BLOCK!"
                return True
        return False
    
    def place_piece(self):
        for y in range(len(self.current_piece)):
            for x in range(len(self.current_piece[y])):
                if self.current_piece[y][x] != 0:
                    grid_x = self.current_pos['x'] + x
                    grid_y = self.current_pos['y'] + y
                    
                    if 0 <= grid_y < GRID_HEIGHT:
                        self.grid[grid_y][grid_x] = self.current_piece[y][x]
        
        self.check_lines()
        self.check_prisoner_stuck()
        self.create_piece()
    
    def check_lines(self):
        lines_cleared = 0
        y = GRID_HEIGHT - 1
        
        while y >= 0:
            if all(cell != 0 for cell in self.grid[y]):
                del self.grid[y]
                self.grid.insert(0, [0 for _ in range(self.grid_width)])
                lines_cleared += 1
            else:
                y -= 1
        
        if lines_cleared > 0:
            self.score += lines_cleared * 100 * self.level
            self.drop_interval = max(0.3, 1.0 - (self.level - 1) * 0.05 - lines_cleared * 0.01)
    
    def rotate_piece(self):
        if not self.game_active or self.game_over or self.current_piece is None:
            return
            
        rotated = []
        for i in range(len(self.current_piece[0])):
            row = []
            for j in range(len(self.current_piece) - 1, -1, -1):
                row.append(self.current_piece[j][i])
            rotated.append(row)
        
        original_piece = self.current_piece
        self.current_piece = rotated
        
        if self.check_collision():
            self.current_piece = original_piece
    
    def move_piece(self, dx, dy):
        if not self.game_active or self.game_over or self.current_piece is None:
            return False
            
        self.current_pos['x'] += dx
        self.current_pos['y'] += dy
        
        if self.check_collision():
            self.current_pos['x'] -= dx
            self.current_pos['y'] -= dy
            
            if dy > 0:
                self.place_piece()
            return False
        return True
    
    def hard_drop(self):
        if not self.game_active or self.game_over or self.current_piece is None:
            return
        while self.move_piece(0, 1):
            pass
    
    def can_move_to(self, x):
        return 0 <= x < self.grid_width
    
    def is_block_at(self, x, y):
        if 0 <= x < self.grid_width and 0 <= y < GRID_HEIGHT:
            return self.grid[y][x] != 0
        return False
    
    def check_escape(self):
        if self.prisoner['y'] != self.escape_height:
            return False
        
        prisoner_x = int(self.prisoner['x'])
        return prisoner_x == 0 or prisoner_x == self.grid_width - 1
    
    def update_prisoner(self, dt):
        if self.prisoner_died or not self.game_active or self.game_over:
            return
        
        self.prisoner['move_timer'] += dt
        if self.prisoner['move_timer'] < self.prisoner['move_delay']:
            return
        
        self.prisoner['move_timer'] = 0
        next_x = int(self.prisoner['x']) + self.prisoner['direction']
        
        if self.can_move_to(next_x):
            current_y = self.prisoner['y']
            current_x = int(self.prisoner['x'])
            
            # Step up
            if (current_y > 0 and 
                self.is_block_at(next_x, current_y) and 
                not self.is_block_at(next_x, current_y - 1) and 
                not self.is_block_at(current_x, current_y - 1)):
                self.prisoner['x'] = next_x
                self.prisoner['y'] = current_y - 1
            # Move straight
            elif (not self.is_block_at(next_x, current_y) and 
                  (current_y >= GRID_HEIGHT - 1 or self.is_block_at(next_x, current_y + 1))):
                self.prisoner['x'] = next_x
            # Fall down
            elif (current_y < GRID_HEIGHT - 1 and 
                  not self.is_block_at(next_x, current_y) and 
                  not self.is_block_at(next_x, current_y + 1)):
                fall_depth = 0
                y = current_y + 1
                
                while y < GRID_HEIGHT and not self.is_block_at(next_x, y):
                    fall_depth += 1
                    y += 1
                
                if fall_depth > 3:
                    self.prisoner['direction'] *= -1
                else:
                    self.prisoner['x'] = next_x
                    self.prisoner['y'] = current_y + fall_depth
            else:
                self.prisoner['direction'] *= -1
        else:
            self.prisoner['direction'] *= -1
        
        self.check_prisoner_stuck()
        
        if self.check_escape():
            self.prisoner['escaped'] = True
            self.game_over = True
            if self.level < MAX_LEVEL:
                self.message = f"LEVEL {self.level} COMPLETE! Press START for next level"
            else:
                self.message = "GAME COMPLETE! You won!"
    
    def update(self, dt):
        if not self.game_active or self.game_over:
            return
        
        self.drop_counter += dt
        if self.drop_counter >= self.drop_interval:
            self.move_piece(0, 1)
            self.drop_counter = 0
        
        self.update_prisoner(dt)
    
    def draw_goal_indicator(self):
        """Рисует индикатор цели"""
        with self.canvas:
            # Подсветка уровня дверей
            Color(1, 0.84, 0, 0.15)
            door_y = self.y + (GRID_HEIGHT - 1 - self.escape_height) * CELL_SIZE
            Rectangle(pos=(self.x, door_y), 
                     size=(self.grid_width * CELL_SIZE, CELL_SIZE))
            
            # Рисуем стрелки к дверям
            Color(1, 0.84, 0, 0.8)
            # Левая стрелка
            Line(points=[self.x - 15, door_y + CELL_SIZE/2,
                        self.x, door_y + CELL_SIZE/2], width=2)
            Line(points=[self.x - 10, door_y + CELL_SIZE/2 - 4,
                        self.x, door_y + CELL_SIZE/2,
                        self.x - 10, door_y + CELL_SIZE/2 + 4], width=2)
            
            # Правая стрелка
            Line(points=[self.x + self.grid_width * CELL_SIZE + 15, door_y + CELL_SIZE/2,
                        self.x + self.grid_width * CELL_SIZE, door_y + CELL_SIZE/2], width=2)
            Line(points=[self.x + self.grid_width * CELL_SIZE + 10, door_y + CELL_SIZE/2 - 4,
                        self.x + self.grid_width * CELL_SIZE, door_y + CELL_SIZE/2,
                        self.x + self.grid_width * CELL_SIZE + 10, door_y + CELL_SIZE/2 + 4], width=2)
    
    def draw_progress_bar(self):
        """Рисует прогресс заключенного к цели"""
        with self.canvas:
            # Фон прогресс-бара
            Color(0.2, 0.2, 0.2, 1)
            bar_x = self.x + self.grid_width * CELL_SIZE + 10
            bar_y = self.y + GRID_HEIGHT * CELL_SIZE - 150
            bar_width = 20
            bar_height = 100
            
            Rectangle(pos=(bar_x, bar_y), size=(bar_width, bar_height))
            
            # Вычисляем прогресс
            current_y = self.prisoner['y']
            target_y = self.escape_height
            total_distance = GRID_HEIGHT - target_y
            traveled = max(0, current_y - target_y)
            progress = min(1.0, traveled / total_distance) if total_distance > 0 else 0
            
            # Заполнение прогресс-бара
            Color(0, 1, 0, 1)
            fill_height = bar_height * progress
            Rectangle(pos=(bar_x, bar_y), size=(bar_width, fill_height))
            
            # Отметка цели
            Color(1, 0.84, 0, 1)
            target_pos = bar_y + bar_height * (1 - (target_y / GRID_HEIGHT))
            Line(points=[bar_x - 5, target_pos, bar_x + bar_width + 5, target_pos], width=2)
    
    def draw(self, dt):
        self.canvas.clear()
        
        with self.canvas:
            # Background
            Color(0, 0, 0, 1)
            Rectangle(pos=self.pos, size=self.size)
            
            # Draw vertical grid lines
            Color(0.3, 0.3, 0.3, 1)
            for x in range(self.grid_width + 1):
                Line(points=[self.x + x * CELL_SIZE, self.y,
                            self.x + x * CELL_SIZE, self.y + GRID_HEIGHT * CELL_SIZE],
                     width=1)
            
            # Draw horizontal grid lines
            for y in range(GRID_HEIGHT + 1):
                y_pos = self.y + y * CELL_SIZE
                Line(points=[self.x, y_pos,
                            self.x + self.grid_width * CELL_SIZE, y_pos],
                     width=1)
            
            # Draw placed blocks
            for y in range(GRID_HEIGHT):
                for x in range(self.grid_width):
                    if self.grid[y][x] != 0:
                        Color(*COLORS[self.grid[y][x]])
                        block_y = self.y + (GRID_HEIGHT - 1 - y) * CELL_SIZE
                        Rectangle(pos=(self.x + x * CELL_SIZE, block_y),
                                size=(CELL_SIZE, CELL_SIZE))
                        Color(0, 0, 0, 1)
                        Line(rectangle=(self.x + x * CELL_SIZE, block_y,
                                      CELL_SIZE, CELL_SIZE), width=1)
            
            # Draw goal indicator
            self.draw_goal_indicator()
            
            # Draw escape doors
            Color(0.54, 0.27, 0.07, 1)
            door_y = self.y + (GRID_HEIGHT - 1 - self.escape_height) * CELL_SIZE
            
            # Left door
            Rectangle(pos=(self.x, door_y),
                     size=(CELL_SIZE / 2, CELL_SIZE))
            # Right door
            Rectangle(pos=(self.x + self.grid_width * CELL_SIZE - CELL_SIZE / 2, door_y),
                     size=(CELL_SIZE / 2, CELL_SIZE))
            
            # Door handles
            Color(1, 0.84, 0, 1)
            Ellipse(pos=(self.x + CELL_SIZE / 4 - 3, door_y + CELL_SIZE / 2 - 3),
                   size=(6, 6))
            Ellipse(pos=(self.x + self.grid_width * CELL_SIZE - CELL_SIZE / 4 - 3, 
                        door_y + CELL_SIZE / 2 - 3),
                   size=(6, 6))
            
            # Draw current piece
            if self.current_piece and not self.game_over:
                for y in range(len(self.current_piece)):
                    for x in range(len(self.current_piece[y])):
                        if self.current_piece[y][x] != 0:
                            grid_x = self.current_pos['x'] + x
                            grid_y = self.current_pos['y'] + y
                            if 0 <= grid_y < GRID_HEIGHT:
                                Color(*COLORS[self.current_piece[y][x]])
                                piece_y = self.y + (GRID_HEIGHT - 1 - grid_y) * CELL_SIZE
                                Rectangle(pos=(self.x + grid_x * CELL_SIZE, piece_y),
                                        size=(CELL_SIZE, CELL_SIZE))
                                Color(0, 0, 0, 1)
                                Line(rectangle=(self.x + grid_x * CELL_SIZE, piece_y,
                                              CELL_SIZE, CELL_SIZE), width=1)
            
            # Draw prisoner
            prisoner_x = int(self.prisoner['x'])
            prisoner_y_screen = self.y + (GRID_HEIGHT - 1 - self.prisoner['y']) * CELL_SIZE
            
            if self.prisoner_died:
                Color(1, 0, 0, 1)
                center_x = self.x + prisoner_x * CELL_SIZE + CELL_SIZE / 2
                center_y = prisoner_y_screen + CELL_SIZE / 2
                for _ in range(12):
                    angle = random.random() * 2 * math.pi
                    distance = random.random() * CELL_SIZE * 0.5
                    radius = CELL_SIZE * (0.08 + random.random() * 0.12)
                    Ellipse(pos=(center_x + math.cos(angle) * distance - radius,
                               center_y + math.sin(angle) * distance - radius),
                           size=(radius * 2, radius * 2))
            else:
                Color(1, 1, 1, 1)
                Rectangle(pos=(self.x + prisoner_x * CELL_SIZE + CELL_SIZE * 0.25,
                              prisoner_y_screen),
                         size=(CELL_SIZE * 0.5, CELL_SIZE))
                Color(0, 0, 0, 1)
                Ellipse(pos=(self.x + prisoner_x * CELL_SIZE + CELL_SIZE * 0.32,
                            prisoner_y_screen + CELL_SIZE * 0.25),
                       size=(CELL_SIZE * 0.08, CELL_SIZE * 0.08))
                Ellipse(pos=(self.x + prisoner_x * CELL_SIZE + CELL_SIZE * 0.6,
                            prisoner_y_screen + CELL_SIZE * 0.25),
                       size=(CELL_SIZE * 0.08, CELL_SIZE * 0.08))
            
            # Draw progress bar
            self.draw_progress_bar()
    
    def start_game(self):
        if self.prisoner_died and Clock.get_time() - self.death_timestamp < DEATH_PAUSE_DURATION:
            return
        
        if self.game_over:
            if self.prisoner.get('escaped', False) and self.level < MAX_LEVEL:
                self.advance_to_next_level()
            elif self.prisoner_died:
                self.restart_current_level()
            else:
                self.reset_game()
        elif not self.game_active:
            self.reset_game()
    
    def advance_to_next_level(self):
        self.level += 1
        self.grid_width = self.get_grid_width_for_level(self.level)
        self.escape_height = self.get_escape_door_height(self.level)
        self.grid = self.create_empty_grid()
        self.prisoner_died = False
        self.prisoner = {
            'x': self.grid_width / 2,
            'y': GRID_HEIGHT - 2,
            'direction': 1,
            'escaped': False,
            'move_timer': 0,
            'move_delay': 0.5
        }
        self.drop_interval = max(0.3, 1.0 - (self.level - 1) * 0.05)
        self.create_piece()
        self.game_over = False
        self.game_active = True
        self.message = f"LEVEL {self.level}! Reach Y={self.escape_height}"
    
    def restart_current_level(self):
        self.grid = self.create_empty_grid()
        self.prisoner_died = False
        self.prisoner = {
            'x': self.grid_width / 2,
            'y': GRID_HEIGHT - 2,
            'direction': 1,
            'escaped': False,
            'move_timer': 0,
            'move_delay': 0.5
        }
        self.drop_interval = max(0.3, 1.0 - (self.level - 1) * 0.05)
        self.create_piece()
        self.game_over = False
        self.game_active = True
        self.message = f"Level {self.level} restarted! Reach Y={self.escape_height}"
    
    def reset_game(self):
        self.level = 1
        self.score = 0
        self.grid_width = self.get_grid_width_for_level(self.level)
        self.escape_height = self.get_escape_door_height(self.level)
        self.grid = self.create_empty_grid()
        self.prisoner_died = False
        self.prisoner = {
            'x': self.grid_width / 2,
            'y': GRID_HEIGHT - 2,
            'direction': 1,
            'escaped': False,
            'move_timer': 0,
            'move_delay': 0.5
        }
        self.game_over = False
        self.game_active = True
        self.drop_counter = 0
        self.drop_interval = 1.0
        self.message = f"Build path to reach Y={self.escape_height}!"
        self.create_piece()

class GameApp(App):
    def build(self):
        Window.clearcolor = (0.133, 0.133, 0.133, 1)
        Window.size = (1100, 750)
        
        main_layout = BoxLayout(orientation='horizontal', padding=10, spacing=10)
        
        # Game widget
        self.game_widget = GameWidget()
        main_layout.add_widget(self.game_widget)
        
        # Control panel
        control_panel = BoxLayout(orientation='vertical', size_hint=(0.3, 1), spacing=10)
        
        # Start button
        self.start_button = Button(text='START GAME', size_hint=(1, 0.08),
                                   font_size='18sp', background_color=(0.2, 0.6, 0.2, 1))
        self.start_button.bind(on_press=self.start_game)
        control_panel.add_widget(self.start_button)
        
        control_panel.add_widget(Label(size_hint=(1, 0.02)))
        
        # Score and Level
        self.score_label = Label(text='SCORE: 0', size_hint=(1, 0.08),
                                 color=(1, 1, 1, 1), font_size='24sp', bold=True)
        self.level_label = Label(text='LEVEL: 1', size_hint=(1, 0.08),
                                 color=(1, 1, 1, 1), font_size='24sp', bold=True)
        
        control_panel.add_widget(self.score_label)
        control_panel.add_widget(self.level_label)
        
        # Goal info
        self.goal_label = Label(text='GOAL: Reach Y=17', size_hint=(1, 0.08),
                                 color=(1, 0.84, 0, 1), font_size='18sp', bold=True)
        control_panel.add_widget(self.goal_label)
        
        # Prisoner position
        self.pos_label = Label(text='PRISONER Y: 18', size_hint=(1, 0.08),
                                color=(0.5, 0.5, 1, 1), font_size='16sp')
        control_panel.add_widget(self.pos_label)
        
        # Message label
        self.message_label = Label(text='', size_hint=(1, 0.12),
                                   color=(1, 1, 0, 1), font_size='16sp',
                                   halign='center', valign='middle')
        self.message_label.bind(size=self.message_label.setter('text_size'))
        control_panel.add_widget(self.message_label)
        
        control_panel.add_widget(Label(size_hint=(1, 0.05)))
        
        # Instructions
        instructions = Label(
            text='⚡ HOW TO PLAY ⚡\n\n'
                 '1️⃣ Build stairs with blocks\n'
                 '2️⃣ Prisoner walks automatically\n'
                 '3️⃣ Guide him to the GOLDEN DOORS\n'
                 '4️⃣ Doors are at different heights\n\n'
                 '🎮 CONTROLS:\n'
                 '← → : Move block\n'
                 '↑ : Rotate block\n'
                 '↓ : Fast drop\n'
                 'SPACE : Hard drop\n'
                 'ENTER : Start/Restart\n\n'
                 '💀 GAME OVER:\n'
                 '- Prisoner crushed by block\n'
                 '- Prisoner stuck in block\n'
                 '- Blocks reach the top',
            size_hint=(1, 0.5),
            color=(0.8, 0.8, 0.8, 1),
            halign='center',
            valign='middle',
            font_size='13sp'
        )
        instructions.bind(size=instructions.setter('text_size'))
        control_panel.add_widget(instructions)
        
        main_layout.add_widget(control_panel)
        
        # Bind keyboard
        Window.bind(on_key_down=self.on_key_down)
        
        # Update UI
        Clock.schedule_interval(self.update_ui, 0.1)
        
        return main_layout
    
    def start_game(self, instance):
        self.game_widget.start_game()
    
    def update_ui(self, dt):
        self.score_label.text = f'SCORE: {int(self.game_widget.score)}'
        self.level_label.text = f'LEVEL: {self.game_widget.level}'
        self.message_label.text = self.game_widget.message
        self.goal_label.text = f'🎯 GOAL: Reach Y={self.game_widget.escape_height} 🎯'
        self.pos_label.text = f'📍 PRISONER Y: {int(self.game_widget.prisoner["y"])} 📍'
        
        # Auto restart after death
        if self.game_widget.prisoner_died:
            time_since_death = Clock.get_time() - self.game_widget.death_timestamp
            if time_since_death >= DEATH_PAUSE_DURATION and self.game_widget.game_over:
                self.game_widget.restart_current_level()
    
    def on_key_down(self, window, key, scancode, codepoint, modifier):
        if self.game_widget.prisoner_died:
            time_since_death = Clock.get_time() - self.game_widget.death_timestamp
            if time_since_death < DEATH_PAUSE_DURATION:
                return
        
        key_map = {
            276: 'left', 275: 'right', 273: 'up', 274: 'down',
            32: 'spacebar', 13: 'enter'
        }
        
        if key in key_map:
            action = key_map[key]
            if action == 'left':
                self.game_widget.move_piece(-1, 0)
            elif action == 'right':
                self.game_widget.move_piece(1, 0)
            elif action == 'down':
                self.game_widget.move_piece(0, 1)
            elif action == 'up':
                self.game_widget.rotate_piece()
            elif action == 'spacebar':
                self.game_widget.hard_drop()
            elif action == 'enter':
                self.game_widget.start_game()

if __name__ == '__main__':
    GameApp().run()