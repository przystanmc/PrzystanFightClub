# -*- coding: utf-8 -*-
import pygame
from pathlib import Path
STATE_MENU = 0
STATE_CHAR_SELECT = 1
STATE_MAP_SELECT = 2
STATE_SETTINGS = 3
STATE_PLAYING = 4
STATE_DIFF_SELECT = 5 # Nowy stan
# --- USTAWIENIA EKRANU ---
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 500
FPS = 50
MAX_CACHE_SIZE = 200
# --- SKALOWANIE I MAPA ---
TILE_SCALE = 3
TILE_SIZE_ORIGINAL = 16
TILE_SIZE = TILE_SIZE_ORIGINAL * TILE_SCALE
COLLISION_TILES = [0, 1, 2, 13, 15, 34, 35, 36, 64, 65, 66]

# --- MECHANIKA ---
POTION_SPAWN_COOLDOWN = 400  # ~8 s przy 50 FPS
DIFFICULTY_EASY = 0.6
DIFFICULTY_NORMAL = 1.0
DIFFICULTY_HARD = 1.5
DIFFICULTY_LABELS = ["ŁATWY", "NORMALNY", "TRUDNY"]

DIFFICULTY_VALUES = [DIFFICULTY_EASY, DIFFICULTY_NORMAL, DIFFICULTY_HARD]



CHAR_STATS = {
    "Soldier": {"damage": 12, "max_hp": 80, "vel": 6, "can_shoot": True},
    "Orc":     {"damage": 14, "max_hp": 90, "vel": 5, "can_shoot": False},
    "Knight":  {"damage": 11, "max_hp": 100, "vel": 6, "can_shoot": False},
    "Golem":   {"damage": 20, "max_hp": 200, "vel": 3, "can_shoot": False},
}

# --- OPISY POSTACI ---
CHAR_DESCRIPTIONS = {
    "Soldier": ["Wyszkolony strzelec.", "Atakuje z dystansu", "uzywajac luku.", "Szybki, ale kruchy."],
    "Orc":     ["Brutalny wojownik.", "Duza sila ataku,", "potrafi blokowac", "ciosy tarcza."],
    "Knight":  ["Honorowy rycerz.", "Zbalansowany.", "Mistrz miecza", "i obrony."],
    "Golem":   ["Magiczny konstrukt.", "Ogromna ilosc HP.", "Powolny, ale", "uderza jak mlot."]
}

# --- ŚCIEŻKI DO ZASOBÓW ---
# Baza projektu liczona od lokalizacji pliku config.py, a nie od katalogu uruchomienia
BASE_PATH = Path(".")

ASSETS_PATH = BASE_PATH / "Assets"
TILES_PATH = ASSETS_PATH / "kafelki"
BG_PATH = ASSETS_PATH / "Backgrounds"

print(f"DEBUG: Katalog roboczy to: {Path.cwd()}")
print(f"DEBUG: Szukam zasobów w: {ASSETS_PATH.absolute()}")

# --- STEROWANIE DOMYŚLNE ---
DEFAULT_P1_CONTROLS = {
    'left': pygame.K_a, 'right': pygame.K_d, 'jump': pygame.K_w,
    'atk1': pygame.K_r, 'atk2': pygame.K_t,
    'special': pygame.K_y, 'block': pygame.K_u
}

DEFAULT_P2_CONTROLS = {
    'left': pygame.K_LEFT, 'right': pygame.K_RIGHT, 'jump': pygame.K_UP,
    'atk1': pygame.K_m, 'atk2': pygame.K_COMMA,
    'special': pygame.K_PERIOD, 'block': pygame.K_l
}

# --- KOLORY ---
COLOR_BG = (30, 30, 30)
COLOR_TEXT = (255, 255, 255)
COLOR_GOLD = (255, 215, 0)

FONT_CHARS_MAP = [
    "abcdefghijklmnop", "qrstuvwxyząćęłńó",
    "śżź.,!?:01234567", "89/\;              ",
    "ABCDEFGHIJKLMNOP", "QRSTUVWXYZĄĆĘŁŃÓ",
    "ŚŻŹ             "
]



