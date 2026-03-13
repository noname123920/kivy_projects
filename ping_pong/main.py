from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import (
    NumericProperty, ReferenceListProperty, ObjectProperty, BooleanProperty, StringProperty
)
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.core.window import Window
import random

class PongPaddle(Widget):
    score = NumericProperty(0)
    
    def bounce_ball(self, ball):
        if self.collide_widget(ball):
            vx, vy = ball.velocity
            offset = (ball.center_y - self.center_y) / (self.height / 2)
            bounced = Vector(-1 * vx, vy)
            vel = bounced * 1.1
            ball.velocity = vel.x, vel.y + offset


class PongBall(Widget):
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)
    
    def move(self):
        self.pos = Vector(*self.velocity) + self.pos


class PongGame(Widget):
    ball = ObjectProperty(None)
    player1 = ObjectProperty(None)
    player2 = ObjectProperty(None)
    
    is_bot_mode = BooleanProperty(True)
    game_state = StringProperty("waiting")  # waiting, playing, game_over
    serving_player = NumericProperty(1)
    points_to_win = NumericProperty(11)
    rallies_since_serve = NumericProperty(0)
    
    status_text = StringProperty("👋 Нажмите ПРОБЕЛ для начала игры | B - бот")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Привязываем клавиатуру
        Window.bind(on_key_down=self._on_keyboard_down)
        Window.bind(on_key_up=self._on_keyboard_up)
        
        # Запускаем обновление для бота
        Clock.schedule_interval(self.bot_update, 1.0/60.0)
    
    def _on_keyboard_down(self, window, key, scancode, codepoint, modifier):
        print(f"Key pressed: {key}, codepoint: {codepoint}")  # Для отладки
        
        # Код 32 - это пробел
        if key == 32 or key == 273:  # 32 = пробел, 273 = Enter
            if self.game_state == "waiting" or self.game_state == "game_over":
                self.start_game()
            return True
        
        # Клавиша B (код 98 - маленькая b, 66 - большая B)
        elif key == 98 or key == 66:
            self.toggle_bot_mode()
            return True
        
        return False
    
    def _on_keyboard_up(self, window, key, scancode):
        pass
    
    def toggle_bot_mode(self):
        self.is_bot_mode = not self.is_bot_mode
        self.status_text = f"🤖 Режим бота: {'ВКЛ' if self.is_bot_mode else 'ВЫКЛ'}"
        self.reset_game()
    
    def start_game(self):
        self.reset_game()
        self.game_state = "playing"
        self.status_text = f"🎮 Игра началась! Подает Игрок {self.serving_player}"
        self.serve_ball()
    
    def reset_game(self):
        self.player1.score = 0
        self.player2.score = 0
        self.serving_player = 1
        self.rallies_since_serve = 0
        self.ball.center = self.center
    
    def serve_ball(self, vel=None):
        self.ball.center = self.center
        
        if vel is None:
            if self.serving_player == 1:
                vel_x = 4
            else:
                vel_x = -4
            
            vel_y = random.choice([-2, -1, 1, 2])
            vel = (vel_x, vel_y)
        
        self.ball.velocity = vel
        self.rallies_since_serve += 1
    
    def check_win_condition(self):
        if self.player1.score >= self.points_to_win and self.player1.score - self.player2.score >= 2:
            self.game_state = "game_over"
            self.status_text = "🏆 ИГРОК 1 ПОБЕДИЛ! Пробел - новая игра, B - бот"
            return True
        elif self.player2.score >= self.points_to_win and self.player2.score - self.player1.score >= 2:
            self.game_state = "game_over"
            self.status_text = "🏆 ИГРОК 2 ПОБЕДИЛ! Пробел - новая игра, B - бот"
            return True
        return False
    
    def check_serve_change(self):
        if self.rallies_since_serve >= 2:
            self.serving_player = 3 - self.serving_player
            self.rallies_since_serve = 0
            self.status_text = f"🎯 Подает Игрок {self.serving_player}"
    
    def update(self, dt):
        if self.game_state != "playing":
            return
        
        self.ball.move()
        
        self.player1.bounce_ball(self.ball)
        self.player2.bounce_ball(self.ball)
        
        if (self.ball.y < self.y) or (self.ball.top > self.top):
            self.ball.velocity_y *= -1
        
        if self.ball.x < self.x:
            self.player2.score += 1
            if not self.check_win_condition():
                self.check_serve_change()
                self.serve_ball()
                
        if self.ball.right > self.width:
            self.player1.score += 1
            if not self.check_win_condition():
                self.check_serve_change()
                self.serve_ball()
    
    def bot_update(self, dt):
        if not self.is_bot_mode or self.game_state != "playing":
            return
        
        target_y = self.ball.center_y
        
        if abs(self.player2.center_y - target_y) > 10:
            if self.player2.center_y < target_y:
                self.player2.center_y += min(5, target_y - self.player2.center_y)
            elif self.player2.center_y > target_y:
                self.player2.center_y -= min(5, self.player2.center_y - target_y)
        
        if self.player2.y < self.y:
            self.player2.y = self.y
        if self.player2.top > self.top:
            self.player2.top = self.top
    
    def on_touch_move(self, touch):
        if self.game_state != "playing":
            return
        
        if touch.x < self.width / 2:
            self.player1.center_y = touch.y
            if self.player1.y < self.y:
                self.player1.y = self.y
            if self.player1.top > self.top:
                self.player1.top = self.top
        
        if not self.is_bot_mode and touch.x > self.width / 2:
            self.player2.center_y = touch.y
            if self.player2.y < self.y:
                self.player2.y = self.y
            if self.player2.top > self.top:
                self.player2.top = self.top


class PongApp(App):
    def build(self):
        game = PongGame()
        Clock.schedule_interval(game.update, 1.0 / 60.0)
        return game


if __name__ == '__main__':
    PongApp().run()