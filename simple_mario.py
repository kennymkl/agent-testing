import curses
import time

WIDTH = 50
HEIGHT = 10
GROUND_Y = HEIGHT - 2
PLAYER_CHAR = 'M'

INSTRUCTIONS = "Move right with arrow keys or 'd'. Press 'q' to quit."


def draw(stdscr, player_x):
    stdscr.clear()
    stdscr.addstr(0, 0, INSTRUCTIONS)
    # draw ground
    for x in range(WIDTH):
        stdscr.addch(GROUND_Y + 1, x, '-')
    # draw player
    stdscr.addch(GROUND_Y, player_x, PLAYER_CHAR)
    stdscr.refresh()


def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(100)

    player_x = 0

    while True:
        key = stdscr.getch()
        if key in (ord('q'), ord('Q')):
            break
        elif key in (curses.KEY_RIGHT, ord('d'), ord('D')):
            if player_x < WIDTH - 1:
                player_x += 1
        elif key in (curses.KEY_LEFT, ord('a'), ord('A')):
            if player_x > 0:
                player_x -= 1

        draw(stdscr, player_x)

        if player_x >= WIDTH - 2:
            stdscr.addstr(HEIGHT // 2, WIDTH // 2 - 4, "You Win!")
            stdscr.refresh()
            time.sleep(2)
            break

        time.sleep(0.05)


if __name__ == '__main__':
    curses.wrapper(main)
