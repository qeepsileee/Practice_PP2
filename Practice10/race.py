import pygame
import random
import sys

pygame.init()

SCREEN_W, SCREEN_H = 500, 700
FPS = 60

BLACK      = (0,   0,   0)
WHITE      = (255, 255, 255)
GRAY       = (100, 100, 100)
DARK_GRAY  = (50,  50,  50)
RED        = (200, 50,  50)
YELLOW     = (255, 215, 0)
GREEN      = (50,  200, 50)
ORANGE     = (255, 165, 0)

ROAD_LEFT  = 80
ROAD_RIGHT = 420
ROAD_W     = ROAD_RIGHT - ROAD_LEFT

CAR_W, CAR_H = 40, 70
CAR_SPEED     = 5

ENEMY_W, ENEMY_H = 40, 70
ENEMY_SPEED_INIT  = 4
ENEMY_SPAWN_TIME  = 90

COIN_R          = 12
COIN_SPEED      = 4
COIN_SPAWN_TIME = 120

MARK_H   = 60
MARK_W   = 8
MARK_GAP = 40
LANES    = [160, 240, 320, 400]

screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Racer")
clock = pygame.time.Clock()

font_big   = pygame.font.SysFont("Arial", 36, bold=True)
font_small = pygame.font.SysFont("Arial", 22)


def draw_road(offset):
    pygame.draw.rect(screen, GRAY, (ROAD_LEFT, 0, ROAD_W, SCREEN_H))
    pygame.draw.rect(screen, DARK_GRAY, (0, 0, ROAD_LEFT, SCREEN_H))
    pygame.draw.rect(screen, DARK_GRAY, (ROAD_RIGHT, 0, SCREEN_W - ROAD_RIGHT, SCREEN_H))
    step = MARK_H + MARK_GAP
    for x in LANES:
        y = (offset % step) - step
        while y < SCREEN_H:
            pygame.draw.rect(screen, WHITE, (x - MARK_W // 2, y, MARK_W, MARK_H))
            y += step


def draw_car(x, y, color, w=CAR_W, h=CAR_H):
    pygame.draw.rect(screen, color, (x, y, w, h), border_radius=6)
    pygame.draw.rect(screen, (180, 220, 255), (x + 5, y + 8, w - 10, 16), border_radius=3)
    pygame.draw.rect(screen, RED, (x + 4, y + h - 12, 10, 6), border_radius=2)
    pygame.draw.rect(screen, RED, (x + w - 14, y + h - 12, 10, 6), border_radius=2)


def draw_coin(x, y):
    pygame.draw.circle(screen, YELLOW, (x, y), COIN_R)
    pygame.draw.circle(screen, ORANGE, (x, y), COIN_R, 2)
    label = font_small.render("$", True, DARK_GRAY)
    screen.blit(label, (x - label.get_width() // 2, y - label.get_height() // 2))


def draw_hud(score, coins):
    screen.blit(font_small.render(f"Score: {score}", True, WHITE), (10, 10))
    coin_surf = font_small.render(f"Coins: {coins}", True, YELLOW)
    screen.blit(coin_surf, (SCREEN_W - coin_surf.get_width() - 10, 10))


def show_message(text, sub=""):
    screen.fill(BLACK)
    msg = font_big.render(text, True, WHITE)
    screen.blit(msg, (SCREEN_W // 2 - msg.get_width() // 2, SCREEN_H // 2 - 60))
    if sub:
        sub_msg = font_small.render(sub, True, GRAY)
        screen.blit(sub_msg, (SCREEN_W // 2 - sub_msg.get_width() // 2, SCREEN_H // 2))
    pygame.display.flip()


class Player:
    def __init__(self):
        self.x = ROAD_LEFT + ROAD_W // 2 - CAR_W // 2
        self.y = SCREEN_H - CAR_H - 20
        self.rect = pygame.Rect(self.x, self.y, CAR_W, CAR_H)

    def update(self, keys):
        if keys[pygame.K_LEFT] and self.x > ROAD_LEFT + 5:
            self.x -= CAR_SPEED
        if keys[pygame.K_RIGHT] and self.x < ROAD_RIGHT - CAR_W - 5:
            self.x += CAR_SPEED
        self.rect.x = self.x

    def draw(self):
        draw_car(self.x, self.y, GREEN)


class Enemy:
    COLORS = [(200, 50, 50), (50, 50, 200), (200, 100, 50), (150, 50, 200)]

    def __init__(self, speed):
        lane = random.randint(0, 3)
        lane_w = ROAD_W // 4
        self.x = ROAD_LEFT + lane * lane_w + (lane_w - ENEMY_W) // 2
        self.y = -ENEMY_H
        self.speed = speed
        self.color = random.choice(self.COLORS)
        self.rect = pygame.Rect(self.x, self.y, ENEMY_W, ENEMY_H)

    def update(self):
        self.y += self.speed
        self.rect.y = self.y

    def draw(self):
        draw_car(self.x, self.y, self.color, ENEMY_W, ENEMY_H)

    def off_screen(self):
        return self.y > SCREEN_H


class Coin:
    def __init__(self):
        self.x = random.randint(ROAD_LEFT + COIN_R + 5, ROAD_RIGHT - COIN_R - 5)
        self.y = -COIN_R
        self.speed = COIN_SPEED
        self.rect = pygame.Rect(self.x - COIN_R, self.y - COIN_R, COIN_R * 2, COIN_R * 2)

    def update(self):
        self.y += self.speed
        self.rect.y = self.y - COIN_R

    def draw(self):
        draw_coin(self.x, self.y)

    def off_screen(self):
        return self.y > SCREEN_H + COIN_R


def game_loop():
    player      = Player()
    enemies     = []
    coins       = []
    road_offset = 0
    score       = 0
    coin_count  = 0
    enemy_speed = ENEMY_SPEED_INIT
    enemy_timer = 0
    coin_timer  = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return score, coin_count

        keys = pygame.key.get_pressed()
        player.update(keys)

        road_offset += enemy_speed

        enemy_timer += 1
        if enemy_timer >= ENEMY_SPAWN_TIME:
            enemies.append(Enemy(enemy_speed))
            enemy_timer = 0

        coin_timer += 1
        if coin_timer >= COIN_SPAWN_TIME:
            coins.append(Coin())
            coin_timer = 0

        for e in enemies:
            e.update()
        for c in coins:
            c.update()

        enemies = [e for e in enemies if not e.off_screen()]
        coins   = [c for c in coins   if not c.off_screen()]

        for e in enemies:
            if player.rect.colliderect(e.rect):
                return score, coin_count

        collected = []
        for c in coins:
            if player.rect.colliderect(c.rect):
                coin_count += 1
                score += 50
            else:
                collected.append(c)
        coins = collected

        score += 1
        enemy_speed = ENEMY_SPEED_INIT + score // 300

        screen.fill(BLACK)
        draw_road(road_offset)
        for e in enemies:
            e.draw()
        for c in coins:
            c.draw()
        player.draw()
        draw_hud(score, coin_count)

        pygame.display.flip()
        clock.tick(FPS)


def main():
    while True:
        show_message("RACER", "Press SPACE to start")
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    waiting = False

        final_score, final_coins = game_loop()

        show_message("GAME OVER", f"Score: {final_score}   Coins: {final_coins}  |  SPACE to restart")
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