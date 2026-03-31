from pygame import *
from pygame.sprite import *

screen = display.set_mode((300,450))
display.set_caption('test caption')

class Figure(Sprite):
    def __init__(self):
        super().__init__()
        self.image = image.load('/Users/zamanbek/Downloads/images.png').convert_alpha()
        initialrect = self.image.get_rect()
        otherrect =  Rect(10,10,100,50)
        self.rect = initialrect.clip(otherrect)
        self.image = self.image.subsurface(otherrect)

f1 = Figure()

while True:
    e = event.wait()
    if e.type == QUIT:
        quit()
        break
    screen.fill((255,255,255))
    screen.blit(f1.image,(130,210))
    display.update()