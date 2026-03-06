from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.properties import *
from kivy.core.window import Window
from kivy.core.text import Label as CoreLabel
from kivy.core.text import LabelBase
import random
import smooth
import os
os.environ['KIVY_TEXT'] = 'pil'  # Переключаем на PIL


class Cell(Widget):
    graphical_size = ListProperty([1, 1])
    graphical_pos = ListProperty([1, 1])
    color = ListProperty([1, 1, 1, 1])

    def __init__(self, x, y, size, margin=4):
        super().__init__()
        self.actual_size = (size, size)
        self.graphical_size = (size - margin, size - margin)
        self.margin = margin
        self.actual_pos = (x, y)
        self.graphical_pos_attach()
        self.color = (0.2, 1.0, 0.2, 1.0)

    def graphical_pos_attach(self, smooth_motion=None):
        to_x, to_y = self.actual_pos[0] - self.graphical_size[0] / 2, self.actual_pos[1] - self.graphical_size[1] / 2
        if smooth_motion is None:
            self.graphical_pos = to_x, to_y
        else:
            smoother, t = smooth_motion
            smoother.move_to(self, to_x, to_y, t)

    def move_to(self, x, y, **kwargs):
        self.actual_pos = (x, y)
        self.graphical_pos_attach(**kwargs)

    def move_by(self, x, y, **kwargs):
        self.move_to(self.actual_pos[0] + x, self.actual_pos[1] + y, **kwargs)

    def get_pos(self):
        return self.actual_pos

    def step_by(self, direction, **kwargs):
        self.move_by(self.actual_size[0] * direction[0], self.actual_size[1] * direction[1], **kwargs)


class Head(Cell):
    def __init__(self, x, y, size, margin=4):
        super().__init__(x, y, size, margin)
        self.color = (0.0, 0.8, 0.0, 1.0)  # Темно-зеленый для головы


class Fruit(Widget):
    graphical_size = ListProperty([1, 1])
    graphical_pos = ListProperty([1, 1])
    fruit_texture = ObjectProperty(None)
    fruit_type = StringProperty('')  # Тип фрукта
    points = NumericProperty(1)      # Сколько очков дает
    
    def __init__(self, x, y, size, fruit_type='apple'):
        super().__init__()
        self.actual_size = (size, size)
        self.graphical_size = (size, size)
        self.actual_pos = (x, y)
        self.graphical_pos = (x - size/2, y - size/2)
        self.fruit_type = fruit_type
        self.set_fruit_properties()
        self.create_texture()
    
    def set_fruit_properties(self):
        """Устанавливаем свойства в зависимости от типа фрукта"""
        fruits = {
            'apple': {'emoji': '🍎', 'points': 1, 'color': (1, 0, 0, 1)},
            'orange': {'emoji': '🍊', 'points': 2, 'color': (1, 0.5, 0, 1)},
            'banana': {'emoji': '🍌', 'points': 3, 'color': (1, 1, 0, 1)},
            'grapes': {'emoji': '🍇', 'points': 4, 'color': (0.5, 0, 0.5, 1)},
            'strawberry': {'emoji': '🍓', 'points': 5, 'color': (1, 0, 0.5, 1)}
        }
        self.fruit_data = fruits.get(self.fruit_type, fruits['apple'])
        self.points = self.fruit_data['points']
    
    def create_texture(self):
        # Регистрируем шрифт с эмодзи
        LabelBase.register(
            name='EmojiFont',
            fn_regular='C:/Windows/Fonts/seguiemj.ttf'
        )
        
        label = CoreLabel(
            text=self.fruit_data['emoji'],
            font_size=self.actual_size[0],
            font_name='EmojiFont'
        )
        label.refresh()
        self.fruit_texture = label.texture
    
    def move_to(self, x, y):
        self.actual_pos = (x, y)
        self.graphical_pos = (x - self.actual_size[0]/2, y - self.actual_size[1]/2)
    
    def get_pos(self):
        return self.actual_pos


class Worm(Widget):
    def __init__(self, config):
        super().__init__()
        self.cells = []
        self.config = config
        self.cell_size = config.CELL_SIZE
        self.head_init((100, 100))
        for i in range(config.DEFAULT_LENGTH - 1):  # -1 потому что голова уже создана
            self.lengthen()

    def destroy(self):
        for i in range(len(self.cells)):
            self.remove_widget(self.cells[i])
        self.cells = []

    def lengthen(self, pos=None, direction=(0, 1)):
        if pos is None:
            px = self.cells[-1].get_pos()[0] + direction[0] * self.cell_size
            py = self.cells[-1].get_pos()[1] + direction[1] * self.cell_size
            pos = (px, py)
        
        # Тело - обычный Cell, но светлее
        body = Cell(*pos, self.cell_size, margin=self.config.MARGIN)
        body.color = (0.3, 1.0, 0.3, 1.0)  # Светло-зеленый для тела
        
        self.cells.append(body)
        self.add_widget(self.cells[-1])

    def head_init(self, pos):
        # Голова - специальный класс Head
        head = Head(*pos, self.cell_size, margin=self.config.MARGIN)
        self.cells.append(head)
        self.add_widget(head)

    def move(self, direction, **kwargs):
        for i in range(len(self.cells) - 1, 0, -1):
            self.cells[i].move_to(*self.cells[i - 1].get_pos(), **kwargs)
        self.cells[0].step_by(direction, **kwargs)

    def gather_positions(self):
        return [cell.get_pos() for cell in self.cells]

    def head_intersect(self, cell):
        return self.cells[0].get_pos() == cell.get_pos()


class Form(Widget):
    worm_len = NumericProperty(0)
    current_speed = NumericProperty(0.3)

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.worm = None
        self.cur_dir = (0, 0)
        self.fruit = None
        self.game_on = True
        self.smooth = smooth.XSmooth(["graphical_pos[0]", "graphical_pos[1]"])
        self.current_speed = config.INTERVAL
        
        self._keyboard = None
        self._request_keyboard()

    def _request_keyboard(self):
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

    def _keyboard_closed(self):
        print("Клавиатура закрыта")
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        key = keycode[1]
        
        if not self.game_on:
            self.worm.destroy()
            self.start()
            return True
        
        if key in ['up', 'w']:
            if self.cur_dir != (0, -1):
                self.cur_dir = (0, 1)
        elif key in ['down', 's']:
            if self.cur_dir != (0, 1):
                self.cur_dir = (0, -1)
        elif key in ['left', 'a']:
            if self.cur_dir != (1, 0):
                self.cur_dir = (-1, 0)
        elif key in ['right', 'd']:
            if self.cur_dir != (-1, 0):
                self.cur_dir = (1, 0)
        elif key == 'spacebar':
            if self.game_on:
                self.stop("⏸ PAUSE\nPress SPACE to continue")
            else:
                self.start()
        
        return True

    def random_cell_location(self, offset):
        x_row = (self.size[0] - 2 * self.config.CELL_SIZE) // self.config.CELL_SIZE  # Учитываем стены
        x_col = (self.size[1] - 2 * self.config.CELL_SIZE) // self.config.CELL_SIZE
        return random.randint(offset, x_row - offset), random.randint(offset, x_col - offset)

    def random_location(self, offset):
        x_row, x_col = self.random_cell_location(offset)
        # Добавляем отступ от стен
        return self.config.CELL_SIZE * (x_row + 1), self.config.CELL_SIZE * (x_col + 1)

    def fruit_dislocate(self):
        x, y = self.random_location(2)
        while (x, y) in self.worm.gather_positions():
            x, y = self.random_location(2)
        
        # Случайно выбираем фрукт
        fruits = ['apple', 'orange', 'banana', 'grapes', 'strawberry']
        fruit_type = random.choice(fruits)
        
        # Удаляем старый фрукт и создаем новый
        if self.fruit is not None:
            self.remove_widget(self.fruit)
        
        self.fruit = Fruit(x, y, self.config.APPLE_SIZE, fruit_type)
        self.add_widget(self.fruit)

    def update_speed(self):
        """Увеличиваем скорость в зависимости от длины змеи"""
        length_factor = 1.0 + (len(self.worm.cells) * 0.03)
        new_speed = self.config.INTERVAL / length_factor
        
        if new_speed < 0.1:
            new_speed = 0.1
        
        self.current_speed = new_speed
        
        Clock.unschedule(self.update)
        Clock.schedule_interval(self.update, self.current_speed)

    def check_wall_collision(self):
        """Проверяем столкновение со стенами"""
        head = self.worm.cells[0]
        x, y = head.get_pos()
        
        # Границы игрового поля с отступом
        margin = self.config.CELL_SIZE
        if (x < margin or x > self.width - margin or 
            y < margin or y > self.height - margin):
            return True
        return False

    def start(self):
        self.worm = Worm(self.config)
        self.add_widget(self.worm)
        
        if self.fruit is not None:
            self.remove_widget(self.fruit)
        
        # Создаем первый фрукт
        fruits = ['apple', 'orange', 'banana', 'grapes', 'strawberry']
        fruit_type = random.choice(fruits)
        self.fruit = Fruit(0, 0, self.config.APPLE_SIZE, fruit_type)
        
        self.fruit_dislocate()
        self.game_on = True
        self.cur_dir = (0, -1)
        self.current_speed = self.config.INTERVAL
        Clock.schedule_interval(self.update, self.current_speed)
        self.popup_label.text = ""

    def stop(self, text=""):
        self.game_on = False
        self.popup_label.text = text
        Clock.unschedule(self.update)

    def game_over(self):
        self.stop("GAME OVER 💀\ntap or press any key to reset")

    def align_labels(self):
        try:
            self.popup_label.pos = ((self.size[0] - self.popup_label.width) / 2, self.size[1] / 2)
            self.score_label.pos = ((self.size[0] - self.score_label.width) / 2, self.size[1] - 80)
        except:
            print(self.__dict__)
            assert False

    def show_points_effect(self, points):
        """Показываем всплывающие очки"""
        from kivy.uix.label import Label
        from kivy.animation import Animation
        
        points_label = Label(
            text=f'+{points}',
            color=(1, 1, 0, 1),
            font_size=40,
            bold=True,
            center=self.fruit.center
        )
        self.add_widget(points_label)
        
        anim = Animation(y=points_label.y + 100, opacity=0, duration=0.5)
        anim.bind(on_complete=lambda *args: self.remove_widget(points_label))
        anim.start(points_label)

    def update(self, _):
        if not self.game_on:
            return
        
        self.worm.move(self.cur_dir, smooth_motion=(self.smooth, self.config.INTERVAL))
        
        # Проверка столкновения со стенами
        if self.check_wall_collision():
            self.game_over()
            return
        
        # Проверка съедания фрукта
        if self.worm.head_intersect(self.fruit):
            # Добавляем очки за фрукт
            for _ in range(self.fruit.points):
                directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
                self.worm.lengthen(direction=random.choice(directions))
            
            self.show_points_effect(self.fruit.points)
            self.update_speed()
            self.fruit_dislocate()
        
        # Проверка укуса себя
        cell = self.worm_bite_self()
        if cell:
            cell.color = (1.0, 0.2, 0.2, 1.0)
            self.game_over()
        
        self.worm_len = len(self.worm.cells)
        self.align_labels()

    def on_touch_down(self, touch):
        if not self.game_on:
            self.worm.destroy()
            self.start()
            return
        ws = touch.x / self.size[0]
        hs = touch.y / self.size[1]
        aws = 1 - ws
        if ws > hs and aws > hs:
            cur_dir = (0, -1)
        elif ws > hs >= aws:
            cur_dir = (1, 0)
        elif ws <= hs < aws:
            cur_dir = (-1, 0)
        else:
            cur_dir = (0, 1)
        self.cur_dir = cur_dir

    def worm_bite_self(self):
        for cell in self.worm.cells[1:]:
            if self.worm.head_intersect(cell):
                return cell
        return False


class Config:
    DEFAULT_LENGTH = 5
    CELL_SIZE = 25
    APPLE_SIZE = 35
    MARGIN = 4
    INTERVAL = 0.3
    DEAD_CELL = (1, 0, 0, 1)
    APPLE_COLOR = (1, 1, 0, 1)


class WormApp(App):
    def build(self):
        self.config = Config()
        self.form = Form(self.config)
        return self.form

    def on_start(self):
        self.form.start()


if __name__ == '__main__':
    WormApp().run()