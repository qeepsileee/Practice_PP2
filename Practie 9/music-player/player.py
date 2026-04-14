import pygame
import os

class MusicPlayer:
    def __init__(self, music_folder):
        pygame.mixer.init()

        self.music_folder = music_folder
        self.playlist = [
            f for f in os.listdir(music_folder)
            if f.endswith(('.wav', '.mp3'))
        ]

        if not self.playlist:
            raise Exception("Папка music пуста!")

        self.current_index = 0
        self.is_playing = False

    def load_track(self):
        track_path = os.path.join(
            self.music_folder,
            self.playlist[self.current_index]
        )
        pygame.mixer.music.load(track_path)

    def play(self):
        self.load_track()
        pygame.mixer.music.play()
        self.is_playing = True

    def stop(self):
        pygame.mixer.music.stop()
        self.is_playing = False

    def next_track(self):
        self.current_index = (self.current_index + 1) % len(self.playlist)
        self.play()

    def previous_track(self):
        self.current_index = (self.current_index - 1) % len(self.playlist)
        self.play()

    def get_current_track(self):
        name = self.playlist[self.current_index]
        return name.replace(".mp3", "").replace(".wav", "")

    def get_position(self):
        pos = pygame.mixer.music.get_pos()
        return max(0, pos // 1000) 