import pygame
import random
from pathlib import Path
from config import (
    TILE_SIZE, COLLISION_TILES, SCREEN_WIDTH, SCREEN_HEIGHT, ASSETS_PATH
)
import characters as chars # Potrzebne do aktualizacji listy platform

# Symbol tła
B = 'B'

# --- DANE MAP MULTIPLAYER ---
map_forest = [
    [B]*21, [B]*21,
    [34, 35, 36] + [B]*15 + [34, 35, 36],
    [B]*21,
    [B]*7 + [34, 35, 35, 35, 35, 36] + [B]*8,
    [B]*21, [B]*21, ['R']*4 + [64] + [B]*17,
    [B]*4 + [65] + [66] + ['R']*17, [B]*21

    ]

map_arena = [
    [B]*23, [B]*23,
    [13, 2, 15] + [B]*15 + [13, 2, 15],
    [B]*23,
    [B]*7 + [34, 35, 35, 35, 35, 36] + [B]*10,
    [B]*23, [B]*13 + [34, 36] + [B]*8, [B]*23, [B]*23,
    [2]*23,
    ]

available_maps = [
    {"name": "Gęsty Las", "data": map_forest, "bg_path": "Assets/Backgrounds/mount.png"},
    {"name": "Podniebna Arena", "data": map_arena, "bg_path": "Assets/Backgrounds/forest.png"},
]

# --- DANE POZIOMÓW SINGLE PLAYER ---
single_levels = [
    {
        "name": "Poziom 1: Przedpole",
        "data": [
            [B]*23, [B]*23,
            [B]*5 + ['O'] + [B]*10 + ['O'] + [B]*6,
            [B]*23, [B]*23, [B]*23, [B]*23, [B]*23, [B]*23,
            [2]*23,
            ],
        "bg_path": "Assets/Backgrounds/forest.png"
    },
    {
        "name": "Poziom 2: Strażnik",
        "data": [



            [B]*21, [B]*21,
            [34, 35, 36] + [B]*15 + [34, 35, 36],
            [B]*21, [B]*9 + ['G'] + [B]*9,
            [B]*21, [B]*21,
            ['R']*4 + [64] + [B]*17,
            [B]*4 + [65] + [66] + ['R']*17, [B]*21
            ],
        "bg_path": "Assets/Backgrounds/mount.png"
    }
]

# --- FUNKCJE POMOCNICZE ---

def get_path(relative_path):
    """Konwertuje ścieżkę relatywną na absolutną na podstawie ASSETS_PATH."""
    full_path = ASSETS_PATH.parent / relative_path
    return str(full_path.absolute())

def load_background(bg_path):
    """Ładuje i skaluje tło."""
    try:
        raw = pygame.image.load(get_path(bg_path)).convert()
        return pygame.transform.scale(raw, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except Exception as e:
        print(f"Błąd ładowania tła '{bg_path}': {e}")
        return None
def load_tiles(folder_path, scale):
    tiles_list = []
    path_obj = Path(folder_path)
    tile_size = 16
    for i in range(60):
        file_path = path_obj / f"kafelek{i}.png"
        try:
            tile = pygame.image.load(str(file_path)).convert_alpha()
            tile = pygame.transform.scale(tile, (tile_size * scale, tile_size * scale))
            tiles_list.append(tile)
        except:
            err_surf = pygame.Surface((tile_size * scale, tile_size * scale))
            err_surf.fill((255, 0, 255))
            tiles_list.append(err_surf)

    spritesheet_files = ["sprite1.png", "sprite2.png"]
    for filename in spritesheet_files:
        file_path = path_obj / filename
        if file_path.exists():
            try:
                sheet = pygame.image.load(str(file_path)).convert_alpha()
                sheet_rect = sheet.get_rect()
                rows = sheet_rect.height // tile_size
                cols = sheet_rect.width // tile_size
                for row in range(rows):
                    for col in range(cols):
                        rect = pygame.Rect(col * tile_size, row * tile_size, tile_size, tile_size)
                        tile = sheet.subsurface(rect)
                        tile = pygame.transform.scale(tile, (tile_size * scale, tile_size * scale))
                        tiles_list.append(tile)
                print(f"Załadowano arkusz {filename}: {len(tiles_list)} kafelków łącznie")
            except Exception as e:
                print(f"Błąd arkusza {filename}: {e}")
    return tiles_list
def build_platforms(map_data, platforms_list, cpu_enemies_list, game_mode):
    platforms_list.clear()
    cpu_enemies_list.clear()


    # Tworzymy kopię danych mapy, aby móc ją modyfikować (podmienić 'R' na wylosowany numer)
    new_map_data = [list(row) for row in map_data]

    for row_idx, row in enumerate(new_map_data):
        for col_idx, tile_idx in enumerate(row):
            pixel_x = col_idx * TILE_SIZE
            pixel_y = row_idx * TILE_SIZE

            # LOGIKA DLA LOSOWEGO KAFELKA
            if tile_idx == 'R':
                # Losujemy indeks z Twoich nowych kafelków (60, 61, 62)
                variant = random.choice([60, 61, 62])
                new_map_data[row_idx][col_idx] = variant

                # Dodajemy prostokąt kolizji
                platforms_list.append(pygame.Rect(pixel_x, pixel_y, TILE_SIZE, TILE_SIZE))

            # LOGIKA DLA ZWYKŁYCH KAFELKÓW LICZBOWYCH
            elif isinstance(tile_idx, int):
                if tile_idx in COLLISION_TILES:
                    platforms_list.append(pygame.Rect(pixel_x, pixel_y, TILE_SIZE, TILE_SIZE))

            # LOGIKA DLA PRZECIWNIKÓW (Tryb Single Player)
            elif game_mode == "single":
                from characters import Orc, Golem, HumanSoldier
                if tile_idx == 'O':
                    cpu_enemies_list.append(Orc(pixel_x, pixel_y))
                elif tile_idx == 'G':
                    cpu_enemies_list.append(Golem(pixel_x, pixel_y))
                elif tile_idx == 'K':
                    cpu_enemies_list.append(HumanSoldier(pixel_x, pixel_y))

    return new_map_data