import json
import os

LEADERBOARD_FILE = "leaderboard.json"
SETTINGS_FILE = "settings.json"

DEFAULT_SETTINGS = {
    "sound": False,
    "car_color": "green",
    "difficulty": "normal"
}

CAR_COLORS = {
    "green":  (50,  200, 50),
    "blue":   (50,  100, 220),
    "red":    (220, 60,  60),
    "yellow": (220, 200, 30),
    "purple": (160, 60,  220),
}

DIFFICULTY = {
    "easy":   {"enemy_speed_init": 3, "spawn_time": 110, "scale_rate": 500},
    "normal": {"enemy_speed_init": 4, "spawn_time": 90,  "scale_rate": 300},
    "hard":   {"enemy_speed_init": 6, "spawn_time": 60,  "scale_rate": 200},
}


def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                data = json.load(f)
                # fill in any missing keys
                for k, v in DEFAULT_SETTINGS.items():
                    data.setdefault(k, v)
                return data
        except Exception:
            pass
    return dict(DEFAULT_SETTINGS)


def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=2)


def load_leaderboard():
    if os.path.exists(LEADERBOARD_FILE):
        try:
            with open(LEADERBOARD_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return []


def save_score(name, score, distance, coins):
    lb = load_leaderboard()
    lb.append({"name": name, "score": score, "distance": distance, "coins": coins})
    lb.sort(key=lambda x: x["score"], reverse=True)
    lb = lb[:10]
    with open(LEADERBOARD_FILE, "w") as f:
        json.dump(lb, f, indent=2)
    return lb
