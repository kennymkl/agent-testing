import os
import sys
import termios
import tty

WIDTH = 30
PLAYER_CHAR = 'M'

INSTRUCTIONS = "Use arrow keys or 'a'/'d' to move. Press 'q' to quit."


def get_key():
    """Read a single keypress from stdin and return it."""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
        if ch == '\x1b':  # Arrow keys
            ch += sys.stdin.read(2)
        return ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def draw(player_x):
    os.system('clear')  # Clear screen
    print(INSTRUCTIONS)
    line = [' '] * WIDTH
    line[player_x] = PLAYER_CHAR
    print('|' + ''.join(line) + '|')


def main():
    player_x = 0
    draw(player_x)
    while True:
        key = get_key()
        if key in ('d', 'D', '\x1b[C'):
            player_x += 1
        elif key in ('a', 'A', '\x1b[D'):
            player_x -= 1
        elif key in ('q', 'Q'):
            break
        player_x = max(0, min(WIDTH - 1, player_x))
        draw(player_x)
        if player_x == WIDTH - 1:
            print('You Win!')
            break


if __name__ == '__main__':
    main()
