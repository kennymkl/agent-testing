import curses
import time
import random

# Game dimensions
WIDTH = 60
HEIGHT = 20
GROUND_Y = HEIGHT - 2
FLAG_X = WIDTH - 3
FLAG_HEIGHT = 4

PLAYER_CHAR = 'M'
DUCK_CHAR = 'm'
ENEMY_CHAR = 'E'

GRAVITY = 1
JUMP_VELOCITY = -4

def draw_screen(stdscr, player_x, player_y, ducking, enemies):
    stdscr.clear()
    # Draw instructions
    stdscr.addstr(0, 0, "Arrows/WASD to move, 's' to duck, 'q' to quit")
    # Draw ground
    for x in range(WIDTH):
        stdscr.addch(GROUND_Y + 1, x, '-')
    # Draw castle with flag
    for i in range(FLAG_HEIGHT):
        y = GROUND_Y - i
        if 0 <= y < HEIGHT:
            stdscr.addch(y, FLAG_X, '#')
    flag_y = GROUND_Y - FLAG_HEIGHT
    if 0 <= flag_y < HEIGHT:
        stdscr.addch(flag_y, FLAG_X, 'F')
    # Draw player
    ch = DUCK_CHAR if ducking else PLAYER_CHAR
    if 0 <= player_x < WIDTH and 0 <= player_y < HEIGHT:
        stdscr.addch(player_y, player_x, ch)
    # Draw enemies
    for ex, ey in enemies:
        if 0 <= ex < WIDTH and 0 <= ey < HEIGHT:
            stdscr.addch(ey, ex, ENEMY_CHAR)
    stdscr.refresh()


def play_game(stdscr):
    stdscr.nodelay(True)
    stdscr.timeout(50)

    player_x = 2
    player_y = GROUND_Y
    player_vy = 0
    ducking = False

    enemies = [
        [WIDTH + 10, GROUND_Y],
        [WIDTH + 30, GROUND_Y]
    ]

    while True:
        key = stdscr.getch()
        if key in (ord('q'), ord('Q')):
            return False
        elif key in (curses.KEY_LEFT, ord('a'), ord('A')):
            player_x = max(0, player_x - 1)
        elif key in (curses.KEY_RIGHT, ord('d'), ord('D')):
            player_x = min(WIDTH - 1, player_x + 1)
        elif key in (curses.KEY_UP, ord('w'), ord('W'), ord(' ')):
            if player_y == GROUND_Y and not ducking:
                player_vy = JUMP_VELOCITY
        elif key in (curses.KEY_DOWN, ord('s'), ord('S')):
            ducking = not ducking

        # Apply gravity
        if player_y < GROUND_Y or player_vy < 0:
            player_vy += GRAVITY
            player_y += player_vy
            if player_y >= GROUND_Y:
                player_y = GROUND_Y
                player_vy = 0

        # Move enemies
        for enemy in enemies:
            enemy[0] -= 1
            if enemy[0] < 0:
                enemy[0] = WIDTH + random.randint(5, 15)

        # Check collision
        for ex, ey in enemies:
            if ex == player_x and ey == player_y:
                stdscr.addstr(HEIGHT // 2, WIDTH // 2 - 5, "Game Over!")
                stdscr.refresh()
                time.sleep(2)
                return True

        # Check win
        if player_x >= FLAG_X - 1:
            stdscr.addstr(HEIGHT // 2, WIDTH // 2 - 4, "You Win!")
            stdscr.refresh()
            time.sleep(2)
            return True

        draw_screen(stdscr, player_x, player_y, ducking, enemies)
        time.sleep(0.05)


def main(stdscr):
    curses.curs_set(0)
    while True:
        result = play_game(stdscr)
        if result is False:
            break
        stdscr.nodelay(False)
        msg = "Press Enter to play again or 'q' to quit"
        stdscr.addstr(HEIGHT // 2 + 1, WIDTH // 2 - len(msg)//2, msg)
        stdscr.refresh()
        while True:
            key = stdscr.getch()
            if key in (ord('q'), ord('Q')):
                return
            if key in (curses.KEY_ENTER, 10, 13):
                break
        stdscr.clear()
        stdscr.nodelay(True)
        

if __name__ == '__main__':
    curses.wrapper(main)
