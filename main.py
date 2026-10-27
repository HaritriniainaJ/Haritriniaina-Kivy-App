from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.properties import (
    NumericProperty, ReferenceListProperty, ObjectProperty, StringProperty
)
from kivy.graphics import Color, Rectangle
from kivy.vector import Vector
from kivy.clock import Clock
from random import choice

class PongPaddle(Widget):
    score = NumericProperty(0)
    orientation = StringProperty('vertical')

    def __init__(self, **kwargs):
        super(PongPaddle, self).__init__(**kwargs)
        self.bind(pos=self.draw_paddle, size=self.draw_paddle)

    def draw_paddle(self, *args):
        self.canvas.clear()
        with self.canvas:
            # Attribution de couleurs claires distinctes pour les 4 joueurs
            if self.orientation == 'vertical':
                if self.x < 400:
                    Color(0.4, 0.9, 1, 1)  # Joueur 1 : Cyan clair
                else:
                    Color(1, 0.4, 0.7, 1)  # Joueur 2 : Rose clair
            else:
                if self.y < 300:
                    Color(0.4, 1, 0.4, 1)  # Joueur 3 : Vert clair (Bas)
                else:
                    Color(1, 0.9, 0.4, 1)  # Joueur 4 : Jaune clair (Haut)
            Rectangle(pos=self.pos, size=self.size)

    def bounce_ball(self, ball):
        if self.collide_widget(ball):
            vx, vy = ball.velocity
            speedup = 1.05  # Légère accélération

            if self.orientation == 'vertical':
                if (vx < 0 and ball.center_x > self.center_x) or (vx > 0 and ball.center_x < self.center_x):
                    # Inversion horizontale et ajout d'un léger effet vertical selon l'impact
                    offset = (ball.center_y - self.center_y) / (self.height / 2)
                    ball.velocity = (-1 * vx * speedup, vy + offset)
            else:
                if (vy < 0 and ball.center_y > self.center_y) or (vy > 0 and ball.center_y < self.center_y):
                    # Inversion verticale et ajout d'un léger effet horizontal selon l'impact
                    offset = (ball.center_x - self.center_x) / (self.width / 2)
                    ball.velocity = (vx + offset, -1 * vy * speedup)

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
    player3 = ObjectProperty(None)
    player4 = ObjectProperty(None)
    winner_label = ObjectProperty(None)
    menu_btn = ObjectProperty(None)
    
    game_state = StringProperty('MENU')

    def serve_ball(self):
        self.ball.center = self.center
        # La balle part maintenant dans une direction complètement aléatoire sur 360°
        self.ball.velocity = Vector(5, 0).rotate(choice([randint(30, 60), randint(120, 150), randint(210, 240), randint(300, 330)]))

    def toggle_menu(self):
        if self.game_state == 'MENU':
            self.game_state = 'PLAYING'
            self.menu_btn.text = "PAUSE"
            self.winner_label.text = ""
            self.serve_ball()
        elif self.game_state == 'PLAYING':
            self.game_state = 'PAUSED'
            self.menu_btn.text = "REPRENDRE"
            self.winner_label.text = "JEU EN PAUSE"
            self.ball.velocity = (0, 0)
        elif self.game_state == 'PAUSED':
            self.game_state = 'PLAYING'
            self.menu_btn.text = "PAUSE"
            self.winner_label.text = ""
            self.serve_ball()
        elif self.game_state == 'GAMEOVER':
            self.player1.score = 0
            self.player2.score = 0
            self.player3.score = 0
            self.player4.score = 0
            self.winner_label.text = ""
            self.game_state = 'PLAYING'
            self.menu_btn.text = "PAUSE"
            self.serve_ball()

    def update(self, dt):
        if self.game_state != 'PLAYING':
            return

        # Vérification du vainqueur à 10 points
        if self.player1.score >= 10:
            self.end_game("JOUEUR 1 (GAUCHE) GAGNE !")
            return
        if self.player2.score >= 10:
            self.end_game("JOUEUR 2 (DROITE) GAGNE !")
            return
        if self.player3.score >= 10:
            self.end_game("JOUEUR 3 (BAS) GAGNE !")
            return
        if self.player4.score >= 10:
            self.end_game("JOUEUR 4 (HAUT) GAGNE !")
            return

        self.ball.move()

        # Rebonds sur les 4 raquettes
        self.player1.bounce_ball(self.ball)
        self.player2.bounce_ball(self.ball)
        self.player3.bounce_ball(self.ball)
        self.player4.bounce_ball(self.ball)

        # Attribution des points selon la sortie de route de la balle
        if self.ball.x < self.x:
            self.player2.score += 1  # Sortie à gauche -> point pour J2
            self.serve_ball()
        elif self.ball.right > self.width:
            self.player1.score += 1  # Sortie à droite -> point pour J1
            self.serve_ball()
        elif self.ball.y < self.y:
            self.player4.score += 1  # Sortie en bas -> point pour J4 (Haut)
            self.serve_ball()
        elif self.ball.top > self.height:
            self.player3.score += 1  # Sortie en haut -> point pour J3 (Bas)
            self.serve_ball()

    def end_game(self, text):
        self.winner_label.text = text + "\nCliquez sur RECOMMENCER"
        self.game_state = 'GAMEOVER'
        self.menu_btn.text = "RECOMMENCER"
        self.ball.velocity = (0, 0)

    def on_touch_move(self, touch):
        if self.game_state != 'PLAYING':
            return
        
        # Division de l'écran en 4 zones de contrôle pour le multitouch
        if touch.x < self.width * 0.25:
            self.player1.center_y = touch.y
        elif touch.x > self.width * 0.75:
            self.player2.center_y = touch.y
        elif touch.y < self.height * 0.25:
            self.player3.center_x = touch.x
        elif touch.y > self.height * 0.75:
            self.player4.center_x = touch.x

class PongApp(App):
    def build(self):
        game = PongGame()
        Clock.schedule_interval(game.update, 1.0 / 60.0)
        return game

if __name__ == '__main__':
    PongApp().run()
