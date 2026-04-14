import pygame
import os
from player import MusicPlayer

pygame.init()

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Music Player")

font = pygame.font.SysFont(None, 36)
small_font = pygame.font.SysFont(None, 26)


music_path = os.path.join(os.path.dirname(__file__), "music")
player = MusicPlayer(music_path)

clock = pygame.time.Clock()
running = True


def draw():
    screen.fill((20, 20, 20))


    track_text = font.render(
        f"Now playing: {player.get_current_track()}",
        True,
        (255, 255, 255)
    )
    screen.blit(track_text, (20, 50))

    
    time_text = small_font.render(
        f"Time: {player.get_position()} sec",
        True,
        (180, 180, 180)
    )
    screen.blit(time_text, (20, 100))

    
    controls = [
        "P - Play",
        "S - Stop",
        "N - Next",
        "B - Back",
        "Q - Quit"
    ]

    for i, text in enumerate(controls):
        txt = small_font.render(text, True, (150, 150, 150))
        screen.blit(txt, (20, 160 + i * 25))

    pygame.display.flip()


while running:
    draw()


    if player.is_playing and not pygame.mixer.music.get_busy():
        player.next_track()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                player.play()

            elif event.key == pygame.K_s:
                player.stop()

            elif event.key == pygame.K_n:
                player.next_track()

            elif event.key == pygame.K_b:
                player.previous_track()

            elif event.key == pygame.K_q:
                running = False

    clock.tick(30)

pygame.quit()