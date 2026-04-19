# assets_manager.py
import pygame
import os
from config import ASSETS_PATH

# Słowniki na zasoby (Cache)
SOUNDS = {}
IMAGES = {}

def load_all_assets():
    if not pygame.mixer.get_init():
        # Ustawienie bufora na mniejszy (2048) pomaga w synchronizacji dźwięku
        pygame.mixer.pre_init(44100, -16, 2, 2048)
        pygame.init()
    
    print(f"\n--- ŁADOWANIE ZASOBÓW AUDIO ---")
    
    # Skalibrowane wartości (0.0 - 1.0)
    to_load = [
        ("hit",             "hit.wav",            0.3), # Zmienione z 1.4 na 0.5
        ("golem_hit",       "golem_hit.wav",      0.4), 
        ("empty_hit",       "empty_hit.wav",      0.6),
        ("golem_empty_hit", "golem_empty_hit.wav",0.8),
        ("jump",            "jump.wav",           0.1),
        ("landing",         "landing.wav",        0.4),
        ("megaman",         "megaman.wav",        0.1), # Teraz na pewno będzie cisza
    ]

    for key, filename, volume in to_load:
        full_path = os.path.join(ASSETS_PATH, "sound", filename)
        
        if os.path.exists(full_path):
            try:
                sound = pygame.mixer.Sound(full_path)
                
                # Zabezpieczenie: upewnij się, że volume jest między 0.0 a 1.0
                safe_volume = max(0.0, min(1.0, volume))
                sound.set_volume(safe_volume) 
                
                SOUNDS[key] = sound
                print(f"SUKCES: {key} (vol: {safe_volume}) -> {filename}")
            except Exception as e:
                print(f"BŁĄD przy wczytywaniu {key}: {e}")
        else:
            print(f"BŁĄD: Brak pliku {full_path}")
def play_sound(name):
    """Bezpieczne odtwarzanie dźwięku z informacją w konsoli."""
    sound = SOUNDS.get(name)
    if sound:
        # print(f"DEBUG: Odtwarzam dźwięk: {name}") # Opcjonalne, może spamować konsolę
        sound.play()
    else:
        print(f"OSTRZEŻENIE: Próba odtworzenia nieistniejącego dźwięku: {name}")


def play_bg_music(filename, loop=-1, volume=0.1): # Dodajemy argument volume
    full_path = os.path.join(ASSETS_PATH, "sound", filename)
    try:
        pygame.mixer.music.load(full_path)
        pygame.mixer.music.set_volume(volume) # To ustawienie steruje muzyką tła
        pygame.mixer.music.play(loop)
        print(f"Muzyka gra: {filename} z głośnością {volume}")
    except Exception as e:
        print(f"Błąd muzyki ({filename}): {e}")
def stop_music():
    pygame.mixer.music.stop()        