import pygame
from persistence import CAR_COLORS, DIFFICULTY, save_settings, load_leaderboard

BLACK     = (0,   0,   0)
WHITE     = (255, 255, 255)
GRAY      = (100, 100, 100)
DARK_GRAY = (50,  50,  50)
YELLOW    = (255, 215, 0)
GREEN     = (50,  200, 50)
RED       = (200, 50,  50)
ACCENT    = (80,  180, 255)


def draw_button(screen, rect, text, font, hovered=False, color=None):
    c = color if color else (ACCENT if hovered else DARK_GRAY)
    pygame.draw.rect(screen, c, rect, border_radius=8)
    pygame.draw.rect(screen, WHITE, rect, 2, border_radius=8)
    label = font.render(text, True, WHITE)
    screen.blit(label, (rect.centerx - label.get_width() // 2,
                         rect.centery - label.get_height() // 2))


def main_menu(screen, font_big, font_small):
    W, H = screen.get_size()
    buttons = {
        "play":        pygame.Rect(W//2 - 110, 260, 220, 52),
        "leaderboard": pygame.Rect(W//2 - 110, 330, 220, 52),
        "settings":    pygame.Rect(W//2 - 110, 400, 220, 52),
        "quit":        pygame.Rect(W//2 - 110, 470, 220, 52),
    }
    labels = {"play": "Play", "leaderboard": "Leaderboard",
              "settings": "Settings", "quit": "Quit"}
    clock = pygame.time.Clock()
    while True:
        mouse = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.MOUSEBUTTONDOWN:
                for key, rect in buttons.items():
                    if rect.collidepoint(mouse):
                        return key

        screen.fill(BLACK)
        title = font_big.render("RACER", True, YELLOW)
        sub   = font_small.render("Arcade Edition", True, GRAY)
        screen.blit(title, (W//2 - title.get_width()//2, 150))
        screen.blit(sub,   (W//2 - sub.get_width()//2,   210))

        for key, rect in buttons.items():
            draw_button(screen, rect, labels[key], font_small, rect.collidepoint(mouse))

        pygame.display.flip()
        clock.tick(60)


def username_screen(screen, font_big, font_small):
    W, H = screen.get_size()
    name = ""
    clock = pygame.time.Clock()
    input_rect = pygame.Rect(W//2 - 130, H//2, 260, 46)
    btn = pygame.Rect(W//2 - 80, H//2 + 70, 160, 46)

    while True:
        mouse = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "Player"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name.strip():
                    return name.strip()
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif len(name) < 16 and event.unicode.isprintable():
                    name += event.unicode
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn.collidepoint(mouse) and name.strip():
                    return name.strip()

        screen.fill(BLACK)
        title = font_big.render("Enter Your Name", True, WHITE)
        screen.blit(title, (W//2 - title.get_width()//2, H//2 - 100))

        pygame.draw.rect(screen, DARK_GRAY, input_rect, border_radius=6)
        pygame.draw.rect(screen, ACCENT,    input_rect, 2, border_radius=6)
        txt = font_small.render(name + "|", True, WHITE)
        screen.blit(txt, (input_rect.x + 10, input_rect.y + 10))

        draw_button(screen, btn, "Start", font_small, btn.collidepoint(mouse),
                    color=(GREEN if name.strip() else GRAY))
        pygame.display.flip()
        clock.tick(60)


def settings_screen(screen, font_big, font_small, settings):
    W, H = screen.get_size()
    clock = pygame.time.Clock()
    color_keys  = list(CAR_COLORS.keys())
    diff_keys   = list(DIFFICULTY.keys())

    while True:
        mouse = pygame.mouse.get_pos()
        ci = color_keys.index(settings["car_color"])
        di = diff_keys.index(settings["difficulty"])

        # button rects
        sound_btn  = pygame.Rect(W//2 + 10,  220, 130, 40)
        col_left   = pygame.Rect(W//2 - 150, 290, 36, 40)
        col_right  = pygame.Rect(W//2 + 114, 290, 36, 40)
        diff_left  = pygame.Rect(W//2 - 150, 360, 36, 40)
        diff_right = pygame.Rect(W//2 + 114, 360, 36, 40)
        back_btn   = pygame.Rect(W//2 - 80,  450, 160, 46)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_settings(settings)
                return settings
            if event.type == pygame.MOUSEBUTTONDOWN:
                if sound_btn.collidepoint(mouse):
                    settings["sound"] = not settings["sound"]
                elif col_left.collidepoint(mouse):
                    settings["car_color"] = color_keys[(ci - 1) % len(color_keys)]
                elif col_right.collidepoint(mouse):
                    settings["car_color"] = color_keys[(ci + 1) % len(color_keys)]
                elif diff_left.collidepoint(mouse):
                    settings["difficulty"] = diff_keys[(di - 1) % len(diff_keys)]
                elif diff_right.collidepoint(mouse):
                    settings["difficulty"] = diff_keys[(di + 1) % len(diff_keys)]
                elif back_btn.collidepoint(mouse):
                    save_settings(settings)
                    return settings

        screen.fill(BLACK)
        title = font_big.render("Settings", True, WHITE)
        screen.blit(title, (W//2 - title.get_width()//2, 140))

        # Sound
        lbl = font_small.render("Sound:", True, GRAY)
        screen.blit(lbl, (W//2 - 140, 232))
        s_color = GREEN if settings["sound"] else RED
        draw_button(screen, sound_btn,
                    "ON" if settings["sound"] else "OFF",
                    font_small, color=s_color)

        # Car color
        lbl = font_small.render("Car Color:", True, GRAY)
        screen.blit(lbl, (W//2 - 140, 302))
        draw_button(screen, col_left,  "<", font_small, col_left.collidepoint(mouse))
        draw_button(screen, col_right, ">", font_small, col_right.collidepoint(mouse))
        cname = settings["car_color"].capitalize()
        cval  = CAR_COLORS[settings["car_color"]]
        cnlbl = font_small.render(cname, True, cval)
        screen.blit(cnlbl, (W//2 - cnlbl.get_width()//2, 302))

        # Difficulty
        lbl = font_small.render("Difficulty:", True, GRAY)
        screen.blit(lbl, (W//2 - 140, 372))
        draw_button(screen, diff_left,  "<", font_small, diff_left.collidepoint(mouse))
        draw_button(screen, diff_right, ">", font_small, diff_right.collidepoint(mouse))
        dnlbl = font_small.render(settings["difficulty"].capitalize(), True, YELLOW)
        screen.blit(dnlbl, (W//2 - dnlbl.get_width()//2, 372))

        draw_button(screen, back_btn, "Back", font_small, back_btn.collidepoint(mouse))
        pygame.display.flip()
        clock.tick(60)


def leaderboard_screen(screen, font_big, font_small):
    W, H = screen.get_size()
    clock = pygame.time.Clock()
    back_btn = pygame.Rect(W//2 - 80, H - 80, 160, 46)
    lb = load_leaderboard()

    while True:
        mouse = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_btn.collidepoint(mouse):
                    return

        screen.fill(BLACK)
        title = font_big.render("Top 10", True, YELLOW)
        screen.blit(title, (W//2 - title.get_width()//2, 40))

        headers = font_small.render("#   Name            Score   Dist   Coins", True, GRAY)
        screen.blit(headers, (30, 100))
        pygame.draw.line(screen, GRAY, (30, 125), (W - 30, 125))

        for i, entry in enumerate(lb):
            color = YELLOW if i == 0 else WHITE
            row = font_small.render(
                f"{i+1:<4}{entry['name'][:14]:<16}{entry['score']:<9}{entry['distance']:<7}{entry['coins']}",
                True, color)
            screen.blit(row, (30, 140 + i * 34))

        if not lb:
            msg = font_small.render("No scores yet!", True, GRAY)
            screen.blit(msg, (W//2 - msg.get_width()//2, 200))

        draw_button(screen, back_btn, "Back", font_small, back_btn.collidepoint(mouse))
        pygame.display.flip()
        clock.tick(60)


def gameover_screen(screen, font_big, font_small, score, distance, coins):
    W, H = screen.get_size()
    clock = pygame.time.Clock()
    retry_btn = pygame.Rect(W//2 - 170, 420, 150, 50)
    menu_btn  = pygame.Rect(W//2 + 20,  420, 150, 50)

    while True:
        mouse = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.MOUSEBUTTONDOWN:
                if retry_btn.collidepoint(mouse):
                    return "retry"
                if menu_btn.collidepoint(mouse):
                    return "menu"

        screen.fill(BLACK)
        title = font_big.render("GAME OVER", True, RED)
        screen.blit(title, (W//2 - title.get_width()//2, 180))

        for i, (label, val) in enumerate([
            ("Score",    score),
            ("Distance", f"{distance} m"),
            ("Coins",    coins),
        ]):
            row = font_small.render(f"{label}: {val}", True, WHITE)
            screen.blit(row, (W//2 - row.get_width()//2, 270 + i * 38))

        draw_button(screen, retry_btn, "Retry",     font_small, retry_btn.collidepoint(mouse), color=GREEN)
        draw_button(screen, menu_btn,  "Main Menu", font_small, menu_btn.collidepoint(mouse))
        pygame.display.flip()
        clock.tick(60)
