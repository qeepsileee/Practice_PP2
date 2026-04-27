import pygame

# Grid settings
CELL = 20
COLS = 30
ROWS = 30
SCREEN_W = CELL * COLS
SCREEN_H = CELL * ROWS

# Colors
BLACK      = (0,   0,   0)
WHITE      = (255, 255, 255)
GRAY       = (40,  40,  40)
LIGHT_GRAY = (180, 180, 180)
GREEN      = (50,  200, 50)
DARK_GREEN = (30,  140, 30)
RED        = (220, 50,  50)
DARK_RED   = (140, 0,   0)
YELLOW     = (255, 215, 0)
ORANGE     = (255, 140, 0)
BLUE       = (50,  100, 220)
PURPLE     = (160, 32,  240)
CYAN       = (0,   220, 220)
TEAL       = (0,   160, 160)
WALL_COLOR = (100, 100, 120)
WALL_INNER = (70,  70,  90)
OBSTACLE_COLOR = (150, 80, 30)
OBSTACLE_INNER = (110, 55, 20)

# Directions
UP    = (0,  -1)
DOWN  = (0,   1)
LEFT  = (-1,  0)
RIGHT = (1,   0)

# Level config
LEVELS = [
    {"speed": 8,  "food_to_next": 3},
    {"speed": 12, "food_to_next": 3},
    {"speed": 16, "food_to_next": 3},
    {"speed": 20, "food_to_next": 3},
    {"speed": 26, "food_to_next": 999},
]

# Food types
FOOD_NORMAL  = "normal"
FOOD_BONUS   = "bonus"
FOOD_POISON  = "poison"

FOOD_DISAPPEAR_TIME = 7000   # ms before timed food vanishes

# Power-up types
PU_SPEED_BOOST = "speed_boost"
PU_SLOW_MOTION = "slow_motion"
PU_SHIELD      = "shield"

PU_FIELD_DURATION  = 8000   # ms on field before vanishing
PU_EFFECT_DURATION = 5000   # ms effect lasts after collected

PU_COLORS = {
    PU_SPEED_BOOST: (255, 200, 0),
    PU_SLOW_MOTION: (0,   180, 255),
    PU_SHIELD:      (180, 0,   255),
}

# Snake color options for settings
SNAKE_COLOR_OPTIONS = {
    "Green":  (50,  200, 50),
    "Cyan":   (0,   220, 220),
    "Orange": (255, 140, 0),
    "Pink":   (255, 100, 180),
    "White":  (230, 230, 230),
}
