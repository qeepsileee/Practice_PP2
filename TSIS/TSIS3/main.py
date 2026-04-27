import pygame
import sys

from persistence import load_settings, save_score
from ui          import main_menu, username_screen, settings_screen, \
                        leaderboard_screen, gameover_screen
from racer       import run_game

SCREEN_W, SCREEN_H = 500, 700

pygame.init()
screen   = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Racer — Arcade Edition")
font_big   = pygame.font.SysFont("Arial", 36, bold=True)
font_small = pygame.font.SysFont("Arial", 22)

settings = load_settings()
username = "Player"

while True:
    action = main_menu(screen, font_big, font_small)

    if action == "quit":
        pygame.quit()
        sys.exit()

    elif action == "leaderboard":
        leaderboard_screen(screen, font_big, font_small)

    elif action == "settings":
        settings = settings_screen(screen, font_big, font_small, settings)

    elif action == "play":
        username = username_screen(screen, font_big, font_small)

        # inner play loop (supports retry without re-entering name)
        while True:
            score, distance, coins, reason = run_game(screen, font_big, font_small, settings)

            if reason == "quit":
                pygame.quit()
                sys.exit()

            save_score(username, score, distance, coins)

            if reason == "menu":
                break

            # "dead" → show game-over screen
            choice = gameover_screen(screen, font_big, font_small, score, distance, coins)
            if choice == "retry":
                continue        # play again
            elif choice == "menu":
                break
            else:               # quit from game-over
                pygame.quit()
                sys.exit()
