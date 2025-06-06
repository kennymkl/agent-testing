import tkinter as tk

WIDTH = 800
HEIGHT = 300
GROUND_Y = 250
PLAYER_SIZE = 20
ENEMY_SIZE = 20
GRAVITY = 1
JUMP_VELOCITY = -15
ENEMY_SPEED = -5

class MarioGame:
    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg='skyblue')
        self.canvas.pack()

        self.player_x = 20
        self.player_y = GROUND_Y
        self.player_vy = 0
        self.is_jumping = False
        self.is_ducking = False

        # Draw player and ground
        self.ground = self.canvas.create_rectangle(0, GROUND_Y + PLAYER_SIZE, WIDTH, HEIGHT, fill='green')
        self.player = self.canvas.create_rectangle(self.player_x, self.player_y - PLAYER_SIZE,
                                                   self.player_x + PLAYER_SIZE, self.player_y,
                                                   fill='red')

        # Enemies
        self.enemies = [
            self.canvas.create_rectangle(WIDTH + 100, GROUND_Y - ENEMY_SIZE,
                                          WIDTH + 100 + ENEMY_SIZE, GROUND_Y,
                                          fill='black'),
            self.canvas.create_rectangle(WIDTH + 300, GROUND_Y - ENEMY_SIZE,
                                          WIDTH + 300 + ENEMY_SIZE, GROUND_Y,
                                          fill='black')
        ]

        self.bind_keys()
        self.update()

    def bind_keys(self):
        self.root.bind('<KeyPress>', self.on_key_press)
        self.root.bind('<KeyRelease>', self.on_key_release)

    def on_key_press(self, event):
        key = event.keysym.lower()
        if key in ('left', 'a'):
            self.player_x -= 5
        elif key in ('right', 'd'):
            self.player_x += 5
        elif key in ('up', 'w') and not self.is_jumping and not self.is_ducking:
            self.player_vy = JUMP_VELOCITY
            self.is_jumping = True
        elif key in ('down', 's'):
            self.is_ducking = True
            self.canvas.coords(self.player, self.player_x, self.player_y - PLAYER_SIZE/2,
                               self.player_x + PLAYER_SIZE, self.player_y)

    def on_key_release(self, event):
        key = event.keysym.lower()
        if key in ('down', 's'):
            self.is_ducking = False
            self.canvas.coords(self.player, self.player_x, self.player_y - PLAYER_SIZE,
                               self.player_x + PLAYER_SIZE, self.player_y)

    def move_enemies(self):
        for enemy in self.enemies:
            self.canvas.move(enemy, ENEMY_SPEED, 0)
            ex1, ey1, ex2, ey2 = self.canvas.coords(enemy)
            if ex2 < 0:
                self.canvas.move(enemy, WIDTH + random.randint(50, 150), 0)

    def check_collision(self):
        px1, py1, px2, py2 = self.canvas.coords(self.player)
        for enemy in self.enemies:
            ex1, ey1, ex2, ey2 = self.canvas.coords(enemy)
            if px2 > ex1 and px1 < ex2 and py2 > ey1 and py1 < ey2:
                self.game_over("Game Over!")
                return True
        return False

    def check_win(self):
        px1, _, px2, _ = self.canvas.coords(self.player)
        if px2 >= WIDTH:
            self.game_over("You Win!")
            return True
        return False

    def game_over(self, msg):
        self.canvas.create_text(WIDTH/2, HEIGHT/2, text=msg, font=('Arial', 24), fill='yellow')

    def update(self):
        # Gravity
        if self.is_jumping:
            self.player_vy += GRAVITY
            self.player_y += self.player_vy
            if self.player_y >= GROUND_Y:
                self.player_y = GROUND_Y
                self.player_vy = 0
                self.is_jumping = False
        # Update player position
        self.canvas.coords(self.player, self.player_x,
                           self.player_y - (PLAYER_SIZE/2 if self.is_ducking else PLAYER_SIZE),
                           self.player_x + PLAYER_SIZE,
                           self.player_y)

        self.move_enemies()

        if not self.check_collision() and not self.check_win():
            self.root.after(20, self.update)

if __name__ == '__main__':
    import random
    root = tk.Tk()
    root.title('Simple Mario Game')
    game = MarioGame(root)
    root.mainloop()
