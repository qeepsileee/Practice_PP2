"""
main.py – Snake TSIS 4
Screens: Main Menu → Game → Game Over → Leaderboard / Settings
"""

import pygame
import sys

from config import *
import db as database
from game import game_loop
import settings as smod


# ── Pygame init ───────────────────────────────────────────────────────────────

pygame.init()
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Snake – TSIS 4")
clock = pygame.time.Clock()

fonts = {
    "big":   pygame.font.SysFont("Arial", 42, bold=True),
    "med":   pygame.font.SysFont("Arial", 28, bold=True),
    "small": pygame.font.SysFont("Arial", 20),
    "tiny":  pygame.font.SysFont("Arial", 16),
}


# ── Shared UI helpers ─────────────────────────────────────────────────────────

def draw_bg():
    screen.fill(BLACK)
    for x in range(0, SCREEN_W, CELL):
        pygame.draw.line(screen, GRAY, (x, 0), (x, SCREEN_H))
    for y in range(0, SCREEN_H, CELL):
        pygame.draw.line(screen, GRAY, (0, y), (SCREEN_W, y))


class Button:
    PAD_X = 24
    PAD_Y = 10
    RADIUS = 8

    def __init__(self, label, cx, cy, width=None, color=GREEN, text_color=BLACK):
        self.label = label
        surf = fonts["med"].render(label, True, text_color)
        w = (width or surf.get_width() + self.PAD_X * 2)
        h = surf.get_height() + self.PAD_Y * 2
        self.rect = pygame.Rect(0, 0, w, h)
        self.rect.center = (cx, cy)
        self.color       = color
        self.hover_color = tuple(min(255, c + 40) for c in color)
        self.text_color  = text_color

    def draw(self, surface):
        mx, my = pygame.mouse.get_pos()
        col = self.hover_color if self.rect.collidepoint(mx, my) else self.color
        pygame.draw.rect(surface, col, self.rect, border_radius=self.RADIUS)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=self.RADIUS)
        surf = fonts["med"].render(self.label, True, self.text_color)
        surface.blit(surf, (self.rect.centerx - surf.get_width() // 2,
                             self.rect.centery - surf.get_height() // 2))

    def clicked(self, event):
        return (event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and self.rect.collidepoint(event.pos))


def text_center(text, color, y, font_key="small"):
    surf = fonts[font_key].render(text, True, color)
    screen.blit(surf, (SCREEN_W // 2 - surf.get_width() // 2, y))


def text_left(text, color, x, y, font_key="small"):
    surf = fonts[font_key].render(text, True, color)
    screen.blit(surf, (x, y))


# ── Username entry ────────────────────────────────────────────────────────────

def screen_username_entry():
    """Typed username entry. Returns the entered username string."""
    username = ""
    cursor_visible = True
    cursor_timer   = 0

    input_rect = pygame.Rect(SCREEN_W // 2 - 140, SCREEN_H // 2 - 20, 280, 44)

    while True:
        dt = clock.tick(30)
        cursor_timer += dt
        if cursor_timer >= 500:
            cursor_visible = not cursor_visible
            cursor_timer   = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and username.strip():
                    return username.strip()
                elif event.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                elif len(username) < 20 and event.unicode.isprintable():
                    username += event.unicode

        draw_bg()
        text_center("ENTER USERNAME", WHITE, SCREEN_H // 2 - 110, "big")
        text_center("Type your name then press Enter", LIGHT_GRAY, SCREEN_H // 2 - 55, "small")

        # Input box
        pygame.draw.rect(screen, (30, 30, 30),  input_rect, border_radius=6)
        pygame.draw.rect(screen, GREEN,          input_rect, 2, border_radius=6)
        display = username + ("|" if cursor_visible else " ")
        uname_surf = fonts["med"].render(display, True, WHITE)
        screen.blit(uname_surf, (input_rect.x + 10,
                                  input_rect.centery - uname_surf.get_height() // 2))

        pygame.display.flip()


# ── Main Menu ─────────────────────────────────────────────────────────────────

def screen_main_menu(username):
    btn_play  = Button("▶  PLAY",        SCREEN_W // 2, 260, width=240, color=GREEN)
    btn_lb    = Button("🏆  LEADERBOARD", SCREEN_W // 2, 330, width=240, color=(40, 80, 160))
    btn_set   = Button("⚙  SETTINGS",    SCREEN_W // 2, 400, width=240, color=(80, 60, 140))
    btn_quit  = Button("✕  QUIT",         SCREEN_W // 2, 470, width=240, color=(140, 40, 40))
    buttons   = [btn_play, btn_lb, btn_set, btn_quit]

    while True:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            for btn in buttons:
                if btn.clicked(event):
                    if btn is btn_play:  return "play"
                    if btn is btn_lb:    return "leaderboard"
                    if btn is btn_set:   return "settings"
                    if btn is btn_quit:
                        pygame.quit()
                        sys.exit()

        draw_bg()
        text_center("S N A K E",      GREEN,      100, "big")
        text_center(f"Player: {username}", CYAN,  155, "small")
        text_center("Arrow keys to move", LIGHT_GRAY, 185, "tiny")

        hint_texts = [
            ("🍎 Normal food = points",          WHITE),
            ("⭐ Bonus food = more points (timed)", YELLOW),
            ("☠  Poison = shorten snake",          DARK_RED),
            ("⚡ Power-ups appear on field",        CYAN),
        ]
        for i, (t, c) in enumerate(hint_texts):
            text_center(t, c, 210 + i * 20, "tiny")

        for btn in buttons:
            btn.draw(screen)
        pygame.display.flip()


# ── Game Over ─────────────────────────────────────────────────────────────────

def screen_game_over(score, level, personal_best):
    btn_retry = Button("↺  RETRY",     SCREEN_W // 2, 370, width=220, color=(40, 140, 40))
    btn_menu  = Button("⌂  MAIN MENU", SCREEN_W // 2, 440, width=220, color=(60, 60, 160))
    buttons   = [btn_retry, btn_menu]

    new_best = score >= personal_best and score > 0

    while True:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            for btn in buttons:
                if btn.clicked(event):
                    if btn is btn_retry: return "retry"
                    if btn is btn_menu:  return "menu"

        draw_bg()
        text_center("GAME OVER", RED, 120, "big")
        text_center(f"Score : {score}",         WHITE,  210, "med")
        text_center(f"Level : {level}",         YELLOW, 248, "med")
        if new_best:
            text_center("★ NEW PERSONAL BEST! ★", YELLOW, 286, "small")
        else:
            text_center(f"Best  : {personal_best}", CYAN, 286, "small")

        for btn in buttons:
            btn.draw(screen)
        pygame.display.flip()


# ── Leaderboard ───────────────────────────────────────────────────────────────

def screen_leaderboard():
    btn_back = Button("← BACK", SCREEN_W // 2, SCREEN_H - 50, width=180, color=(60, 60, 60))
    rows = database.get_leaderboard(10)

    while True:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if btn_back.clicked(event):
                return

        draw_bg()
        text_center("LEADERBOARD", YELLOW, 30, "big")

        # Table header
        cols_x = [50, 110, 250, 360, 460]
        headers = ["#", "Player", "Score", "Level", "Date"]
        h_colors = [LIGHT_GRAY] * 5
        for i, (hdr, hcol) in enumerate(zip(headers, h_colors)):
            text_left(hdr, hcol, cols_x[i], 90, "small")
        pygame.draw.line(screen, GRAY, (40, 112), (SCREEN_W - 40, 112))

        if not rows:
            text_center("No records yet — play a game!", LIGHT_GRAY, 200, "small")
        else:
            for rank, row in enumerate(rows, 1):
                y = 120 + (rank - 1) * 28
                date_str = row["played_at"].strftime("%m/%d") if row.get("played_at") else "-"
                values = [
                    str(rank),
                    row.get("username", "?")[:12],
                    str(row.get("score", 0)),
                    str(row.get("level_reached", 1)),
                    date_str,
                ]
                row_color = YELLOW if rank == 1 else (CYAN if rank <= 3 else WHITE)
                for i, val in enumerate(values):
                    text_left(val, row_color, cols_x[i], y, "small")

        btn_back.draw(screen)
        pygame.display.flip()


# ── Settings ──────────────────────────────────────────────────────────────────

def screen_settings(settings):
    """Mutates and saves settings dict. Returns updated dict."""
    color_names = list(SNAKE_COLOR_OPTIONS.keys())

    def next_color(current):
        idx = color_names.index(current) if current in color_names else 0
        return color_names[(idx + 1) % len(color_names)]

    btn_grid  = Button("", SCREEN_W // 2, 200, width=260)
    btn_sound = Button("", SCREEN_W // 2, 270, width=260)
    btn_color = Button("", SCREEN_W // 2, 340, width=260)
    btn_save  = Button("💾  SAVE & BACK", SCREEN_W // 2, 440, width=260, color=GREEN)
    buttons   = [btn_grid, btn_sound, btn_color, btn_save]

    def update_labels():
        btn_grid.label  = f"Grid:  {'ON' if settings['grid_overlay'] else 'OFF'}"
        btn_sound.label = f"Sound: {'ON' if settings['sound'] else 'OFF'}"
        btn_color.label = f"Color: {settings['snake_color']}"

    update_labels()

    while True:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if btn_grid.clicked(event):
                settings["grid_overlay"] = not settings["grid_overlay"]
                update_labels()
            elif btn_sound.clicked(event):
                settings["sound"] = not settings["sound"]
                update_labels()
            elif btn_color.clicked(event):
                settings["snake_color"] = next_color(settings["snake_color"])
                update_labels()
            elif btn_save.clicked(event):
                smod.save_settings(settings)
                return settings

        draw_bg()
        text_center("SETTINGS", WHITE, 80, "big")
        text_center("Click a button to toggle / cycle", LIGHT_GRAY, 145, "tiny")

        for btn in buttons:
            btn.draw(screen)

        # Color preview swatch
        swatch_color = SNAKE_COLOR_OPTIONS.get(settings["snake_color"], GREEN)
        swatch_rect  = pygame.Rect(SCREEN_W // 2 + 80, 326, 24, 24)
        pygame.draw.rect(screen, swatch_color, swatch_rect, border_radius=4)

        pygame.display.flip()


# ── Main orchestrator ─────────────────────────────────────────────────────────

def main():
    # Init DB (non-fatal if unavailable)
    database.init_db()

    # Load settings
    settings = smod.load_settings()

    # Username entry once per session
    username = screen_username_entry()
    personal_best = database.get_personal_best(username)

    action = screen_main_menu(username)

    while True:
        if action == "play":
            final_score, level_reached = game_loop(
                screen, clock, fonts, settings, username, personal_best
            )
            # Save to DB
            database.save_session(username, final_score, level_reached)
            # Update personal best in memory
            if final_score > personal_best:
                personal_best = final_score

            action = screen_game_over(final_score, level_reached, personal_best)

            if action == "retry":
                action = "play"
            else:  # "menu"
                action = screen_main_menu(username)

        elif action == "leaderboard":
            screen_leaderboard()
            action = screen_main_menu(username)

        elif action == "settings":
            settings = screen_settings(settings)
            action = screen_main_menu(username)

        else:
            action = screen_main_menu(username)


if __name__ == "__main__":
    main()
