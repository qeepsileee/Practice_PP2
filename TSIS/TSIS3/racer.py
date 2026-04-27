import pygame
import random
from persistence import CAR_COLORS, DIFFICULTY

# ── colours ──────────────────────────────────────────────────────────────────
BLACK      = (0,   0,   0)
WHITE      = (255, 255, 255)
GRAY       = (100, 100, 100)
DARK_GRAY  = (50,  50,  50)
RED        = (200, 50,  50)
YELLOW     = (255, 215, 0)
GREEN      = (50,  200, 50)
ORANGE     = (255, 165, 0)
CYAN       = (0,   220, 220)
PURPLE     = (180, 60,  220)
BROWN      = (120, 80,  30)

# ── road layout ──────────────────────────────────────────────────────────────
SCREEN_W, SCREEN_H = 500, 700
ROAD_LEFT  = 80
ROAD_RIGHT = 420
ROAD_W     = ROAD_RIGHT - ROAD_LEFT
LANE_COUNT = 4
LANE_W     = ROAD_W // LANE_COUNT
LANES      = [ROAD_LEFT + i * LANE_W + LANE_W // 2 for i in range(LANE_COUNT)]

# ── car ───────────────────────────────────────────────────────────────────────
CAR_W, CAR_H = 40, 70
CAR_SPEED     = 5
NITRO_SPEED   = 9

# ── enemy ─────────────────────────────────────────────────────────────────────
ENEMY_W, ENEMY_H = 40, 70

# ── coin ─────────────────────────────────────────────────────────────────────
COIN_R     = 12
COIN_SPEED = 4

# ── obstacle ──────────────────────────────────────────────────────────────────
OBS_W, OBS_H = 40, 30

# ── power-up ──────────────────────────────────────────────────────────────────
PU_R         = 16
PU_DURATION  = 240   # frames (~4 s at 60 fps)
PU_TIMEOUT   = 360   # frames on road before disappearing

# ── road marks ───────────────────────────────────────────────────────────────
MARK_H = 60
MARK_W = 8
MARK_GAP = 40


# ─────────────────────────────────────────────────────────────────────────────
#  Drawing helpers
# ─────────────────────────────────────────────────────────────────────────────

def draw_road(screen, offset):
    pygame.draw.rect(screen, GRAY,      (ROAD_LEFT, 0, ROAD_W, SCREEN_H))
    pygame.draw.rect(screen, DARK_GRAY, (0, 0, ROAD_LEFT, SCREEN_H))
    pygame.draw.rect(screen, DARK_GRAY, (ROAD_RIGHT, 0, SCREEN_W - ROAD_RIGHT, SCREEN_H))
    step = MARK_H + MARK_GAP
    for i in range(1, LANE_COUNT):
        x = ROAD_LEFT + i * LANE_W
        y = (offset % step) - step
        while y < SCREEN_H:
            pygame.draw.rect(screen, WHITE, (x - MARK_W // 2, y, MARK_W, MARK_H))
            y += step


def draw_car(screen, x, y, color, w=CAR_W, h=CAR_H):
    pygame.draw.rect(screen, color, (x, y, w, h), border_radius=6)
    pygame.draw.rect(screen, (180, 220, 255), (x + 5, y + 8,  w - 10, 16), border_radius=3)
    pygame.draw.rect(screen, RED,             (x + 4, y + h - 12, 10, 6), border_radius=2)
    pygame.draw.rect(screen, RED,             (x + w - 14, y + h - 12, 10, 6), border_radius=2)


def draw_coin(screen, font_small, x, y):
    pygame.draw.circle(screen, YELLOW, (x, y), COIN_R)
    pygame.draw.circle(screen, ORANGE, (x, y), COIN_R, 2)
    lbl = font_small.render("$", True, DARK_GRAY)
    screen.blit(lbl, (x - lbl.get_width() // 2, y - lbl.get_height() // 2))


def draw_powerup(screen, font_small, x, y, kind):
    colors = {"nitro": ORANGE, "shield": CYAN, "repair": GREEN}
    labels = {"nitro": "N",    "shield": "S",  "repair": "R"}
    pygame.draw.circle(screen, colors[kind], (x, y), PU_R)
    pygame.draw.circle(screen, WHITE,        (x, y), PU_R, 2)
    lbl = font_small.render(labels[kind], True, BLACK)
    screen.blit(lbl, (x - lbl.get_width() // 2, y - lbl.get_height() // 2))


def draw_obstacle(screen, x, y, kind):
    if kind == "oil":
        pygame.draw.ellipse(screen, (20, 20, 60), (x, y + 8, OBS_W, 16))
        pygame.draw.ellipse(screen, (60, 60, 160), (x + 4, y + 10, OBS_W - 8, 10))
    elif kind == "pothole":
        pygame.draw.ellipse(screen, (30, 20, 10), (x, y + 4, OBS_W, 22))
        pygame.draw.ellipse(screen, BROWN,        (x + 4, y + 8, OBS_W - 8, 14))
    elif kind == "barrier":
        pygame.draw.rect(screen, (200, 100, 0), (x, y, OBS_W, OBS_H), border_radius=4)
        pygame.draw.rect(screen, WHITE,         (x, y, OBS_W, OBS_H), 2, border_radius=4)


def draw_hud(screen, font_small, score, coins, distance, powerup, pu_timer, shield_active):
    # left: score + distance
    screen.blit(font_small.render(f"Score: {score}",    True, WHITE),  (10, 10))
    screen.blit(font_small.render(f"Dist:  {distance}m", True, GRAY), (10, 36))

    # right: coins
    cs = font_small.render(f"Coins: {coins}", True, YELLOW)
    screen.blit(cs, (SCREEN_W - cs.get_width() - 10, 10))

    # shield indicator
    if shield_active:
        sh = font_small.render("🛡 SHIELD", True, CYAN)
        screen.blit(sh, (SCREEN_W - sh.get_width() - 10, 36))

    # active power-up bar
    if powerup and pu_timer > 0:
        label = {"nitro": "NITRO", "shield": "SHIELD", "repair": "REPAIR"}[powerup]
        color = {"nitro": ORANGE,  "shield": CYAN,     "repair": GREEN}[powerup]
        bar_w = int((pu_timer / PU_DURATION) * 140)
        pygame.draw.rect(screen, DARK_GRAY, (SCREEN_W // 2 - 70, 10, 140, 20), border_radius=4)
        pygame.draw.rect(screen, color,     (SCREEN_W // 2 - 70, 10, bar_w, 20), border_radius=4)
        lbl = font_small.render(label, True, WHITE)
        screen.blit(lbl, (SCREEN_W // 2 - lbl.get_width() // 2, 32))


# ─────────────────────────────────────────────────────────────────────────────
#  Game objects
# ─────────────────────────────────────────────────────────────────────────────

class Player:
    def __init__(self, car_color_name):
        self.color = CAR_COLORS[car_color_name]
        self.x = ROAD_LEFT + ROAD_W // 2 - CAR_W // 2
        self.y = SCREEN_H - CAR_H - 20
        self.rect = pygame.Rect(self.x, self.y, CAR_W, CAR_H)

    def update(self, keys, speed):
        if keys[pygame.K_LEFT] and self.x > ROAD_LEFT + 5:
            self.x -= speed
        if keys[pygame.K_RIGHT] and self.x < ROAD_RIGHT - CAR_W - 5:
            self.x += speed
        self.rect.x = self.x

    def draw(self, screen, nitro_active, shield_active):
        c = self.color
        if nitro_active:
            # draw flame below car
            pygame.draw.polygon(screen, ORANGE, [
                (self.x + 8, self.y + CAR_H),
                (self.x + CAR_W - 8, self.y + CAR_H),
                (self.x + CAR_W // 2, self.y + CAR_H + 18),
            ])
        draw_car(screen, self.x, self.y, c)
        if shield_active:
            pygame.draw.ellipse(screen, CYAN,
                                (self.x - 6, self.y - 6, CAR_W + 12, CAR_H + 12), 3)


class Enemy:
    COLORS = [(200, 50, 50), (50, 50, 200), (200, 100, 50), (150, 50, 200)]

    def __init__(self, speed, player_x):
        while True:
            lane = random.randint(0, LANE_COUNT - 1)
            x    = ROAD_LEFT + lane * LANE_W + (LANE_W - ENEMY_W) // 2
            # safe spawn: not within 150px horizontally of player start
            if abs(x - player_x) > 40:
                break
        self.x = x
        self.y = -ENEMY_H - random.randint(0, 60)
        self.speed = speed
        self.color = random.choice(self.COLORS)
        self.rect  = pygame.Rect(self.x, self.y, ENEMY_W, ENEMY_H)

    def update(self):
        self.y += self.speed
        self.rect.y = self.y

    def draw(self, screen):
        draw_car(screen, self.x, self.y, self.color, ENEMY_W, ENEMY_H)

    def off_screen(self):
        return self.y > SCREEN_H


class Coin:
    def __init__(self):
        lane = random.randint(0, LANE_COUNT - 1)
        self.x = ROAD_LEFT + lane * LANE_W + LANE_W // 2
        self.y = -COIN_R
        self.rect = pygame.Rect(self.x - COIN_R, self.y - COIN_R, COIN_R * 2, COIN_R * 2)

    def update(self):
        self.y += COIN_SPEED
        self.rect.y = self.y - COIN_R

    def draw(self, screen, font_small):
        draw_coin(screen, font_small, self.x, self.y)

    def off_screen(self):
        return self.y > SCREEN_H + COIN_R


class Obstacle:
    KINDS = ["oil", "pothole", "barrier"]

    def __init__(self, scroll_speed, player_x):
        while True:
            lane = random.randint(0, LANE_COUNT - 1)
            x    = ROAD_LEFT + lane * LANE_W + (LANE_W - OBS_W) // 2
            if abs(x - player_x) > 40:
                break
        self.x     = x
        self.y     = -OBS_H - random.randint(0, 80)
        self.speed = scroll_speed
        self.kind  = random.choice(self.KINDS)
        self.rect  = pygame.Rect(self.x, self.y, OBS_W, OBS_H)

    def update(self):
        self.y += self.speed
        self.rect.y = self.y

    def draw(self, screen):
        draw_obstacle(screen, self.x, self.y, self.kind)

    def off_screen(self):
        return self.y > SCREEN_H


class PowerUp:
    KINDS = ["nitro", "shield", "repair"]

    def __init__(self, scroll_speed):
        lane = random.randint(0, LANE_COUNT - 1)
        self.x     = ROAD_LEFT + lane * LANE_W + LANE_W // 2
        self.y     = -PU_R
        self.speed = scroll_speed
        self.kind  = random.choice(self.KINDS)
        self.age   = 0
        self.rect  = pygame.Rect(self.x - PU_R, self.y - PU_R, PU_R * 2, PU_R * 2)

    def update(self):
        self.y   += self.speed
        self.age += 1
        self.rect.y = self.y - PU_R

    def draw(self, screen, font_small):
        draw_powerup(screen, font_small, self.x, self.y, self.kind)

    def off_screen(self):
        return self.y > SCREEN_H + PU_R or self.age > PU_TIMEOUT


class NitroStrip:
    """A glowing strip across the road that gives a brief speed surge."""
    def __init__(self, scroll_speed):
        self.y     = -20
        self.speed = scroll_speed
        self.rect  = pygame.Rect(ROAD_LEFT, self.y, ROAD_W, 16)

    def update(self):
        self.y      += self.speed
        self.rect.y  = self.y

    def draw(self, screen):
        alpha_surf = pygame.Surface((ROAD_W, 16), pygame.SRCALPHA)
        alpha_surf.fill((255, 165, 0, 140))
        screen.blit(alpha_surf, (ROAD_LEFT, self.y))
        pygame.draw.rect(screen, ORANGE, (ROAD_LEFT, self.y, ROAD_W, 16), 2)

    def off_screen(self):
        return self.y > SCREEN_H


# ─────────────────────────────────────────────────────────────────────────────
#  Main game loop
# ─────────────────────────────────────────────────────────────────────────────

def run_game(screen, font_big, font_small, settings):
    diff     = DIFFICULTY[settings["difficulty"]]
    car_col  = settings["car_color"]

    player      = Player(car_col)
    enemies     = []
    coins       = []
    obstacles   = []
    powerups    = []
    nitro_strips = []

    road_offset  = 0
    score        = 0
    coin_count   = 0
    distance     = 0
    enemy_speed  = diff["enemy_speed_init"]

    enemy_timer  = 0
    coin_timer   = 0
    obs_timer    = 0
    pu_timer_spawn = 0
    strip_timer  = 0

    # power-up state
    active_pu    = None   # "nitro" | "shield" | "repair" | None
    pu_frames    = 0
    shield_active = False

    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return score, distance, coin_count, "quit"
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return score, distance, coin_count, "menu"

        keys   = pygame.key.get_pressed()
        cur_speed = NITRO_SPEED if active_pu == "nitro" else CAR_SPEED
        player.update(keys, cur_speed)

        # scroll speed scales with difficulty + progress
        scale_rate  = diff["scale_rate"]
        enemy_speed = diff["enemy_speed_init"] + score // scale_rate
        road_offset += enemy_speed
        distance     = score // 10

        # ── spawn logic ───────────────────────────────────────────────────────
        spawn_time = max(30, diff["spawn_time"] - score // 200)

        enemy_timer += 1
        if enemy_timer >= spawn_time:
            enemies.append(Enemy(enemy_speed, player.x))
            if score > 500 and random.random() < 0.3:   # double spawn at high score
                enemies.append(Enemy(enemy_speed, player.x))
            enemy_timer = 0

        coin_timer += 1
        if coin_timer >= 120:
            coins.append(Coin())
            coin_timer = 0

        obs_timer += 1
        obs_interval = max(100, 200 - score // 100)
        if obs_timer >= obs_interval:
            obstacles.append(Obstacle(enemy_speed, player.x))
            obs_timer = 0

        pu_timer_spawn += 1
        if pu_timer_spawn >= 300:
            if not any(isinstance(o, PowerUp) for o in powerups):
                powerups.append(PowerUp(enemy_speed))
            pu_timer_spawn = 0

        strip_timer += 1
        if strip_timer >= 400:
            nitro_strips.append(NitroStrip(enemy_speed))
            strip_timer = 0

        # ── update ────────────────────────────────────────────────────────────
        for lst in (enemies, coins, obstacles, powerups, nitro_strips):
            for obj in lst:
                obj.update()

        enemies      = [e for e in enemies      if not e.off_screen()]
        coins        = [c for c in coins        if not c.off_screen()]
        obstacles    = [o for o in obstacles    if not o.off_screen()]
        powerups     = [p for p in powerups     if not p.off_screen()]
        nitro_strips = [s for s in nitro_strips if not s.off_screen()]

        # ── collision: enemy ──────────────────────────────────────────────────
        for e in enemies:
            if player.rect.colliderect(e.rect):
                if shield_active:
                    shield_active = False
                    active_pu     = None
                    enemies.remove(e)
                    break
                else:
                    return score, distance, coin_count, "dead"

        # ── collision: obstacles ──────────────────────────────────────────────
        for o in list(obstacles):
            if player.rect.colliderect(o.rect):
                if active_pu == "repair":
                    obstacles.remove(o)
                    active_pu = None
                    pu_frames = 0
                elif shield_active:
                    shield_active = False
                    active_pu     = None
                    obstacles.remove(o)
                elif o.kind == "oil":
                    # slow down briefly (handled below)
                    obstacles.remove(o)
                else:
                    return score, distance, coin_count, "dead"

        # ── collision: nitro strips ───────────────────────────────────────────
        for s in list(nitro_strips):
            if player.rect.colliderect(s.rect):
                if active_pu is None:
                    active_pu = "nitro"
                    pu_frames = PU_DURATION
                nitro_strips.remove(s)
                break

        # ── collision: coins ──────────────────────────────────────────────────
        new_coins = []
        for c in coins:
            if player.rect.colliderect(c.rect):
                coin_count += 1
                score       += 50
            else:
                new_coins.append(c)
        coins = new_coins

        # ── collision: power-ups ──────────────────────────────────────────────
        new_pu = []
        for p in powerups:
            if player.rect.colliderect(p.rect):
                if active_pu != "shield" and active_pu != "nitro":
                    active_pu = p.kind
                    pu_frames = PU_DURATION
                    if p.kind == "shield":
                        shield_active = True
                    elif p.kind == "repair":
                        # instant: clear one obstacle ahead
                        if obstacles:
                            obstacles.pop(0)
                        active_pu = None
                        pu_frames = 0
            else:
                new_pu.append(p)
        powerups = new_pu

        # ── power-up timer ────────────────────────────────────────────────────
        if active_pu in ("nitro",):
            pu_frames -= 1
            if pu_frames <= 0:
                active_pu = None

        # ── score tick ────────────────────────────────────────────────────────
        score += 1

        # ── draw ──────────────────────────────────────────────────────────────
        screen.fill(BLACK)
        draw_road(screen, road_offset)

        for s in nitro_strips: s.draw(screen)
        for o in obstacles:    o.draw(screen)
        for e in enemies:      e.draw(screen)
        for c in coins:        c.draw(screen, font_small)
        for p in powerups:     p.draw(screen, font_small)
        player.draw(screen, active_pu == "nitro", shield_active)
        draw_hud(screen, font_small, score, coin_count, distance,
                 active_pu, pu_frames, shield_active)

        pygame.display.flip()
        clock.tick(60)
