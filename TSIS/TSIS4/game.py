"""
game.py – Snake core gameplay for TSIS 4.
Handles the game loop, snake movement, food/power-up/obstacle logic.
Returns (final_score, level_reached) to main.py.
"""

import pygame
import random
import sys

from config import *
import db as database


# ── Utility ───────────────────────────────────────────────────────────────────

def random_free_cell(snake, walls, obstacles, extra=None):
    occupied = set(snake) | set(walls) | set(obstacles)
    if extra:
        occupied |= set(extra)
    attempts = 0
    while attempts < 5000:
        pos = (random.randint(1, COLS - 2), random.randint(1, ROWS - 2))
        if pos not in occupied:
            return pos
        attempts += 1
    return None


def build_border_walls():
    walls = set()
    for c in range(COLS):
        walls.add((c, 0))
        walls.add((c, ROWS - 1))
    for r in range(ROWS):
        walls.add((0, r))
        walls.add((COLS - 1, r))
    return walls


def build_obstacles(level, snake, walls):
    """
    From level 3 onward, add random wall blocks inside the arena.
    Guarantees the snake's head area (3-cell radius) is kept clear.
    """
    if level < 3:
        return set()
    n_blocks = min(5 + (level - 3) * 3, 20)
    occupied = set(walls) | set(snake)
    head = snake[0]
    # Keep a safe zone around the head
    safe = {(head[0] + dx, head[1] + dy)
            for dx in range(-3, 4) for dy in range(-3, 4)}
    candidates = [
        (c, r)
        for c in range(2, COLS - 2)
        for r in range(2, ROWS - 2)
        if (c, r) not in occupied and (c, r) not in safe
    ]
    random.shuffle(candidates)
    return set(candidates[:n_blocks])


# ── Drawing ───────────────────────────────────────────────────────────────────

def draw_grid(screen):
    for x in range(0, SCREEN_W, CELL):
        pygame.draw.line(screen, GRAY, (x, 0), (x, SCREEN_H))
    for y in range(0, SCREEN_H, CELL):
        pygame.draw.line(screen, GRAY, (0, y), (SCREEN_W, y))


def draw_cell(screen, col, row, color, inner_color=None):
    rect = pygame.Rect(col * CELL + 1, row * CELL + 1, CELL - 2, CELL - 2)
    pygame.draw.rect(screen, color, rect, border_radius=3)
    if inner_color:
        inner = rect.inflate(-6, -6)
        pygame.draw.rect(screen, inner_color, inner, border_radius=2)


def draw_snake(screen, snake, snake_color):
    dark = tuple(max(0, c - 60) for c in snake_color)
    for i, (col, row) in enumerate(snake):
        if i == 0:
            draw_cell(screen, col, row, snake_color, dark)
        else:
            draw_cell(screen, col, row, snake_color)


def draw_food_item(screen, food_item):
    col, row = food_item["pos"]
    ftype = food_item["type"]
    if ftype == FOOD_NORMAL:
        draw_cell(screen, col, row, RED, ORANGE)
    elif ftype == FOOD_BONUS:
        draw_cell(screen, col, row, YELLOW, WHITE)
    elif ftype == FOOD_POISON:
        draw_cell(screen, col, row, DARK_RED, (80, 0, 0))
        # skull-ish dot
        cx = col * CELL + CELL // 2
        cy = row * CELL + CELL // 2
        pygame.draw.circle(screen, (200, 0, 0), (cx, cy), 4)


def draw_powerup(screen, pu):
    if pu is None:
        return
    col, row = pu["pos"]
    color = PU_COLORS[pu["type"]]
    draw_cell(screen, col, row, color)
    cx = col * CELL + CELL // 2
    cy = row * CELL + CELL // 2
    pygame.draw.circle(screen, WHITE, (cx, cy), 4)


def draw_walls(screen, walls):
    for col, row in walls:
        draw_cell(screen, col, row, WALL_COLOR, WALL_INNER)


def draw_obstacles(screen, obstacles):
    for col, row in obstacles:
        draw_cell(screen, col, row, OBSTACLE_COLOR, OBSTACLE_INNER)


def draw_hud(screen, fonts, score, level, food_count, food_to_next,
             personal_best, active_pu, shield_active):
    font_small = fonts["small"]
    font_tiny  = fonts.get("tiny", fonts["small"])

    texts = [
        (f"Score: {score}",      WHITE,  8,  8),
        (f"Level: {level}",      YELLOW, 8, 28),
        (f"Next: {food_to_next - food_count % food_to_next}", ORANGE, 8, 48),
        (f"Best:  {personal_best}", CYAN, 8, 68),
    ]
    for text, color, x, y in texts:
        surf = font_small.render(text, True, color)
        screen.blit(surf, (x, y))

    if shield_active:
        s = font_small.render("SHIELD ON", True, PURPLE)
        screen.blit(s, (SCREEN_W - s.get_width() - 8, 8))

    if active_pu:
        now = pygame.time.get_ticks()
        remaining = max(0, (active_pu["expires_at"] - now) // 1000)
        label = active_pu["type"].replace("_", " ").upper()
        color = PU_COLORS[active_pu["type"]]
        s = font_small.render(f"{label} {remaining}s", True, color)
        screen.blit(s, (SCREEN_W - s.get_width() - 8, 28))


# ── Main game loop ────────────────────────────────────────────────────────────

def game_loop(screen, clock, fonts, settings, username, personal_best):
    """
    Run one game. Returns (final_score, level_reached).
    """
    # --- State init ---
    level = 1
    score = 0
    food_count = 0

    start_col = COLS // 2
    start_row = ROWS // 2
    snake = [
        (start_col,     start_row),
        (start_col - 1, start_row),
        (start_col - 2, start_row),
    ]
    direction      = RIGHT
    next_direction = RIGHT

    walls     = build_border_walls()
    obstacles = build_obstacles(level, snake, walls)

    snake_color = SNAKE_COLOR_OPTIONS.get(settings.get("snake_color", "Green"), GREEN)

    level_data   = LEVELS[level - 1]
    base_speed   = level_data["speed"]
    food_to_next = level_data["food_to_next"]

    def current_speed():
        if active_powerup and active_powerup["type"] == PU_SPEED_BOOST:
            return int(base_speed * 1.7)
        if active_powerup and active_powerup["type"] == PU_SLOW_MOTION:
            return max(4, int(base_speed * 0.5))
        return base_speed

    # Foods list: each dict has pos, type, points, spawn_time (or None)
    foods = []

    def spawn_food():
        occupied_by_food = [f["pos"] for f in foods]
        pos = random_free_cell(snake, walls, obstacles, extra=occupied_by_food)
        if pos is None:
            return
        roll = random.random()
        if roll < 0.15:
            ftype  = FOOD_POISON
            points = 0
            timed  = False
        elif roll < 0.35:
            ftype  = FOOD_BONUS
            points = 30
            timed  = True
        else:
            ftype  = FOOD_NORMAL
            points = 10
            timed  = False

        foods.append({
            "pos":        pos,
            "type":       ftype,
            "points":     points * level,
            "timed":      timed,
            "spawn_time": pygame.time.get_ticks() if timed else None,
        })

    # Start with one food
    spawn_food()

    # Power-up on field
    field_powerup  = None   # currently on the grid
    active_powerup = None   # currently affecting the snake
    shield_active  = False

    pu_types = [PU_SPEED_BOOST, PU_SLOW_MOTION, PU_SHIELD]
    next_pu_spawn = pygame.time.get_ticks() + random.randint(5000, 12000)

    # ── Loop ──────────────────────────────────────────────────────────────────
    while True:
        clock.tick(current_speed())
        now = pygame.time.get_ticks()

        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if   event.key == pygame.K_UP    and direction != DOWN:
                    next_direction = UP
                elif event.key == pygame.K_DOWN  and direction != UP:
                    next_direction = DOWN
                elif event.key == pygame.K_LEFT  and direction != RIGHT:
                    next_direction = LEFT
                elif event.key == pygame.K_RIGHT and direction != LEFT:
                    next_direction = RIGHT
                elif event.key == pygame.K_ESCAPE:
                    return score, level

        # Move
        direction = next_direction
        head = (snake[0][0] + direction[0], snake[0][1] + direction[1])

        # Collision detection
        hit_wall     = head in walls
        hit_obstacle = head in obstacles
        hit_self     = head in set(snake)

        if (hit_wall or hit_obstacle or hit_self):
            if shield_active:
                shield_active = False
                # Teleport head back to safe position (don't die, skip move)
                # Just skip the death — don't advance head
                pass
            else:
                return score, level

        else:
            snake.insert(0, head)

            # Check food
            ate_food = False
            for food in foods[:]:
                if head == food["pos"]:
                    ftype = food["type"]
                    if ftype == FOOD_POISON:
                        # Shorten by 2
                        for _ in range(2):
                            if len(snake) > 1:
                                snake.pop()
                        if len(snake) <= 1:
                            return score, level
                    else:
                        score += food["points"]
                        food_count += 1

                    foods.remove(food)
                    ate_food = True

                    # Level up?
                    if food_count > 0 and food_count % food_to_next == 0 and level < len(LEVELS):
                        level += 1
                        obstacles = build_obstacles(level, snake, walls)
                        level_data   = LEVELS[level - 1]
                        base_speed   = level_data["speed"]
                        food_to_next = level_data["food_to_next"]
                        _show_level_banner(screen, fonts, level)

                    spawn_food()
                    break

            if not ate_food:
                snake.pop()

            # Check power-up pickup
            if field_powerup and head == field_powerup["pos"]:
                ptype = field_powerup["type"]
                if ptype == PU_SHIELD:
                    shield_active = True
                    active_powerup = None
                else:
                    active_powerup = {
                        "type":       ptype,
                        "expires_at": now + PU_EFFECT_DURATION,
                    }
                field_powerup = None

        # Expire timed foods
        foods = [
            f for f in foods
            if not f["timed"] or (now - f["spawn_time"]) < FOOD_DISAPPEAR_TIME
        ]
        if not foods:
            spawn_food()

        # Expire active power-up
        if active_powerup and now >= active_powerup["expires_at"]:
            active_powerup = None

        # Spawn new field power-up
        if field_powerup is None and now >= next_pu_spawn:
            food_pos_set = [f["pos"] for f in foods]
            pos = random_free_cell(snake, walls, obstacles, extra=food_pos_set)
            if pos:
                field_powerup = {
                    "pos":      pos,
                    "type":     random.choice(pu_types),
                    "expires":  now + PU_FIELD_DURATION,
                }
            next_pu_spawn = now + random.randint(8000, 18000)

        # Expire field power-up
        if field_powerup and now >= field_powerup["expires"]:
            field_powerup = None

        # ── Draw ──────────────────────────────────────────────────────────────
        screen.fill(BLACK)
        if settings.get("grid_overlay", True):
            draw_grid(screen)
        draw_walls(screen, walls)
        draw_obstacles(screen, obstacles)
        for food in foods:
            draw_food_item(screen, food)
        draw_powerup(screen, field_powerup)
        draw_snake(screen, snake, snake_color)
        draw_hud(screen, fonts, score, level, food_count, food_to_next,
                 personal_best, active_powerup, shield_active)
        pygame.display.flip()


# ── Level banner ──────────────────────────────────────────────────────────────

def _show_level_banner(screen, fonts, level):
    overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    screen.blit(overlay, (0, 0))
    msg  = fonts["big"].render(f"LEVEL {level}!", True, YELLOW)
    msg2 = fonts["small"].render("Get ready...", True, LIGHT_GRAY)
    screen.blit(msg,  (SCREEN_W // 2 - msg.get_width()  // 2, SCREEN_H // 2 - 40))
    screen.blit(msg2, (SCREEN_W // 2 - msg2.get_width() // 2, SCREEN_H // 2 + 20))
    pygame.display.flip()
    pygame.time.wait(1500)
