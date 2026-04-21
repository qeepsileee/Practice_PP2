import pygame
import random
import sys

pygame.init()

CELL = 20
COLS = 30
ROWS = 30
SCREEN_W = CELL * COLS
SCREEN_H = CELL * ROWS

BLACK      = (0,   0,   0)
WHITE      = (255, 255, 255)
GRAY       = (40,  40,  40)
GREEN      = (50,  200, 50)
DARK_GREEN = (30,  140, 30)
RED        = (220, 50,  50)
YELLOW     = (255, 215, 0)
ORANGE     = (255, 140, 0)
BLUE       = (50,  100, 220)

LEVELS = [
    {"speed": 8,  "food_to_next": 3},
    {"speed": 12, "food_to_next": 3},
    {"speed": 16, "food_to_next": 3},
    {"speed": 20, "food_to_next": 3},
    {"speed": 26, "food_to_next": 999},
]

UP    = (0,  -1)
DOWN  = (0,   1)
LEFT  = (-1,  0)
RIGHT = (1,   0)

screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Snake")
clock = pygame.time.Clock()

font_big   = pygame.font.SysFont("Arial", 42, bold=True)
font_med   = pygame.font.SysFont("Arial", 28, bold=True)
font_small = pygame.font.SysFont("Arial", 20)


def draw_grid():
    for x in range(0, SCREEN_W, CELL):
        pygame.draw.line(screen, GRAY, (x, 0), (x, SCREEN_H))
    for y in range(0, SCREEN_H, CELL):
        pygame.draw.line(screen, GRAY, (0, y), (SCREEN_W, y))


def draw_cell(col, row, color, inner_color=None):
    rect = pygame.Rect(col * CELL + 1, row * CELL + 1, CELL - 2, CELL - 2)
    pygame.draw.rect(screen, color, rect, border_radius=3)
    if inner_color:
        inner = rect.inflate(-6, -6)
        pygame.draw.rect(screen, inner_color, inner, border_radius=2)


def draw_snake(snake):
    for i, (col, row) in enumerate(snake):
        if i == 0:
            draw_cell(col, row, GREEN, DARK_GREEN)
        else:
            draw_cell(col, row, GREEN)


def draw_food(food):
    col, row = food
    draw_cell(col, row, RED, ORANGE)


def draw_walls(walls):
    for col, row in walls:
        draw_cell(col, row, (120, 120, 120), (80, 80, 80))


def draw_hud(score, level, food_count, food_to_next):
    score_surf = font_small.render(f"Score: {score}", True, WHITE)
    screen.blit(score_surf, (8, 8))

    level_surf = font_small.render(f"Level: {level}", True, YELLOW)
    screen.blit(level_surf, (8, 30))

    next_surf = font_small.render(f"Next: {food_to_next - food_count % food_to_next}", True, ORANGE)
    screen.blit(next_surf, (8, 52))


def show_message(title, lines=None):
    screen.fill(BLACK)
    draw_grid()
    msg = font_big.render(title, True, WHITE)
    screen.blit(msg, (SCREEN_W // 2 - msg.get_width() // 2, SCREEN_H // 2 - 80))
    if lines:
        for i, line in enumerate(lines):
            surf = font_small.render(line, True, GRAY.__class__ and (180, 180, 180))
            screen.blit(surf, (SCREEN_W // 2 - surf.get_width() // 2, SCREEN_H // 2 - 20 + i * 26))
    pygame.display.flip()


def random_free_cell(snake, walls):
    occupied = set(snake) | set(walls)
    while True:
        pos = (random.randint(1, COLS - 2), random.randint(1, ROWS - 2))
        if pos not in occupied:
            return pos


def build_walls(level):
    walls = set()
    for c in range(COLS):
        walls.add((c, 0))
        walls.add((c, ROWS - 1))
    for r in range(ROWS):
        walls.add((0, r))
        walls.add((COLS - 1, r))
    if level >= 2:
        for c in range(5, 12):
            walls.add((c, ROWS // 2))
    if level >= 3:
        for r in range(5, 12):
            walls.add((COLS // 2, r))
    if level >= 4:
        for c in range(COLS - 12, COLS - 5):
            walls.add((c, ROWS // 2))
    return list(walls)


def game_loop():
    level = 1
    score = 0
    food_count = 0

    start_col = COLS // 2
    start_row = ROWS // 2
    snake = [(start_col, start_row), (start_col - 1, start_row), (start_col - 2, start_row)]
    direction = RIGHT
    next_direction = RIGHT

    walls = build_walls(level)
    food = random_free_cell(snake, walls)

    level_data = LEVELS[level - 1]
    speed = level_data["speed"]
    food_to_next = level_data["food_to_next"]

    while True:
        clock.tick(speed)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP    and direction != DOWN:
                    next_direction = UP
                elif event.key == pygame.K_DOWN  and direction != UP:
                    next_direction = DOWN
                elif event.key == pygame.K_LEFT  and direction != RIGHT:
                    next_direction = LEFT
                elif event.key == pygame.K_RIGHT and direction != LEFT:
                    next_direction = RIGHT
                elif event.key == pygame.K_ESCAPE:
                    return score

        direction = next_direction
        head = (snake[0][0] + direction[0], snake[0][1] + direction[1])

        wall_set = set(walls)
        if head in wall_set or head in set(snake):
            return score

        snake.insert(0, head)

        if head == food:
            score += 10 * level
            food_count += 1

            if food_count % food_to_next == 0 and level < len(LEVELS):
                level += 1
                walls = build_walls(level)
                wall_set = set(walls)
                snake_set = set(snake)
                level_data = LEVELS[level - 1]
                speed = level_data["speed"]
                food_to_next = level_data["food_to_next"]

                show_message(f"Level {level}!", ["Get ready...", ""])
                pygame.time.wait(1500)

            food = random_free_cell(snake, set(walls))
        else:
            snake.pop()

        screen.fill(BLACK)
        draw_grid()
        draw_walls(walls)
        draw_food(food)
        draw_snake(snake)
        draw_hud(score, level, food_count, food_to_next)
        pygame.display.flip()


def main():
    while True:
        show_message("SNAKE", [
            "Arrow keys to move",
            "Collect food to level up",
            "SPACE to start"
        ])

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    waiting = False

        final_score = game_loop()

        show_message("GAME OVER", [
            f"Score: {final_score}",
            "SPACE to restart"
        ])

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    waiting = False


if __name__ == "__main__":
    main()