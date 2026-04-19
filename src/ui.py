# -*- coding: utf-8 -*-
# W pliku z logiką rysowania/gry:
import pygame
from characters import Soldier, Orc, HumanSoldier, Golem
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_GOLD, ASSETS_PATH,
    DIFFICULTY_LABELS, FONT_CHARS_MAP,
    CHAR_STATS, CHAR_DESCRIPTIONS, MAX_CACHE_SIZE  # <--- DODAJ TO
)

# Definiujesz tylko to, co musi być dynamicznie powiązane z klasami:
CHAR_CLASS_MAP = {
    "Soldier": Soldier,
    "Orc": Orc,
    "Knight": HumanSoldier,
    "Golem": Golem
}

# --- GLOBALNE ZASOBY (Ładowane raz) ---
FRAME_IMG  = None
SCROLL_IMG = None
FONT_MAIN  = None
FONT_SUB   = None
ARROW_IMG  = None
ARROW_IMG_LEFT = None    # ← DODAĆ TĘ LINIĘ
BOARD_IMG  = None

# Cache wyrenderowanych napisów — zapobiega font.render() 60x/s
# Uwaga: dynamiczne teksty (liczniki) renderowane są bezpośrednio, z pominięciem cache
TEXT_CACHE = {}
MAX_CACHE_SIZE = 200  # OPTYMALIZACJA: limit rozmiaru cache
arrow_offset_L = 0
arrow_offset_R = 0

# Cache dla pojedynczych przeskalowanych liter z PNG
CHAR_SURFACE_CACHE = {}

def get_char_metrics(char):
    small_w = 6
    large_w = 7
    metrics = {"width": small_w, "x_offset": 0, "y_offset": 0}

    # Test wielkiej litery
    if char.isupper() and char != char.lower() and not char.isdigit():
        metrics["width"] = large_w

    # TWOJE SPECJALNE USTAWIENIA PIKSELOWE
    if char == "i":
        metrics.update({"width": small_w - 4, "x_offset": -2})
    elif char == "I":
        metrics.update({"width": large_w - 4, "x_offset": -2})
    elif char in ("l", "L"):
        base = small_w if char == "l" else large_w
        metrics.update({"width": base - 1, "x_offset": 0})
    elif char == "1":
        metrics.update({"width": small_w - 2, "x_offset": -1})
    elif char in ("?", "3"):
        metrics.update({"width": small_w - 1, "x_offset": -1})
    elif char == "!":
        metrics.update({"width": small_w - 3, "x_offset": -2})
    elif char in (":", ".", " "):
        if char == " ":
            metrics.update({"width": 3, "x_offset": 0})
        else:
            metrics.update({"width": small_w - 4, "x_offset": -2})
    elif char == ",":
        metrics.update({"width": small_w - 3, "x_offset": -2})
    
    # Poprawka dla w i m (odstępy lewo/prawo)
    elif char in ("w", "m"):
        metrics.update({"width": small_w + 2, "x_offset": 1})
    elif char in ("W", "M"):
        metrics.update({"width": large_w + 1, "x_offset": 1})
    # Obsługa polskich dużych znaków
    elif char in ("Ś", "Ć", "Ź", "Ż", "Ó", "Ń"):
        metrics.update({"width": large_w, "y_offset": -1}) # -1 zazwyczaj wystarczy, -4 to bardzo wysoko

    return metrics
def draw_custom_text(screen, text, x, y, font_png, scale=2, main_color="#c42525", shadow_color="#333941", center=False):
    global TEXT_CACHE, CHAR_SURFACE_CACHE, MAX_CACHE_SIZE
    
    # 1. Sprawdzamy czy MAMY JUŻ GOTOWY CAŁY NAPIS
    cache_key = (text, scale, main_color, shadow_color)
    
    if cache_key not in TEXT_CACHE:
        # --- TWORZENIE NOWEGO NAPISU ---
        t_width = get_custom_text_width(text, scale)
        # Zapas w pionie (10 * scale) żeby zmieścić wystające do góry polskie ogonki
        t_height = 10 * scale 
        
        # Tworzymy przezroczystą powierzchnię dla całego tekstu
        text_surf = pygame.Surface((t_width, t_height), pygame.SRCALPHA)
        
        cursor_x = 0
        base_y = 2 * scale # Rysujemy odrobinę niżej na naszej "kartce", żeby zrobić miejsce na polskie znaki (-y_offset)

        # Tworzymy obiekty Color tylko raz dla całego słowa, nie w pętli
        c_main = pygame.Color(main_color)
        c_shadow = pygame.Color(shadow_color)
        ORIGINAL_MAIN = pygame.Color("#c42525")
        ORIGINAL_SHADOW = pygame.Color("#333941")

        for char in text:
            if char == " ":
                cursor_x += 3 * scale
                continue

            metrics = get_char_metrics(char)
            char_key = (char, scale, main_color, shadow_color)

            # Pobieranie/tworzenie pojedynczej litery (to zostaje tak samo)
            if char_key not in CHAR_SURFACE_CACHE:
                coords = None
                for r_idx, row in enumerate(FONT_CHARS_MAP):
                    c_idx = row.find(char)
                    if c_idx != -1:
                        coords = (c_idx * 8, r_idx * 8)
                        break

                if coords:
                    char_img = font_png.subsurface(pygame.Rect(coords[0], coords[1], 8, 8))
                    if main_color != "#c42525" or shadow_color != "#333941":
                        char_img = change_color(char_img, ORIGINAL_MAIN, c_main, ORIGINAL_SHADOW, c_shadow)
                    CHAR_SURFACE_CACHE[char_key] = pygame.transform.scale(char_img, (8 * scale, 8 * scale))
                else:
                    continue

            # Rysujemy znak na NASZEJ "KARTCE" (text_surf), a nie od razu na ekranie
            cached_char = CHAR_SURFACE_CACHE[char_key]
            final_x = cursor_x + (metrics["x_offset"] * scale)
            final_y = base_y + (metrics["y_offset"] * scale)
            
            text_surf.blit(cached_char, (final_x, final_y))
            
            cursor_x += (metrics["width"] + 1) * scale

        # Zapisujemy gotowy napis do cache
        TEXT_CACHE[cache_key] = text_surf
        
        # PROSTE ZARZĄDZANIE PAMIĘCIĄ (żeby gra nie pożarła całego RAMu przy zmiennych tekstach np. licznikach)
        if len(TEXT_CACHE) > MAX_CACHE_SIZE:
            # Usuwamy najstarszy element słownika (Python 3.7+ zachowuje kolejność)
            TEXT_CACHE.pop(next(iter(TEXT_CACHE)))


    # --- RYSOWANIE GOTOWEGO NAPISU NA EKRANIE ---
    # Wyciągamy gotowy obrazek z pamięci (to dzieje się w 99% klatek)
    final_render = TEXT_CACHE[cache_key]
    
    # Obliczamy centrowanie i korygujemy Y (bo wewnątrz text_surf obniżyliśmy rysowanie o 2*scale)
    draw_x = x - final_render.get_width() // 2 if center else x
    draw_y = y - (2 * scale)
    
    # JEDNO wywołanie blit dla całego słowa!
    screen.blit(final_render, (draw_x, draw_y))
def load_ui_assets():
    global FRAME_IMG, SCROLL_IMG, FONT_MAIN, FONT_SUB, ARROW_IMG, ARROW_IMG_LEFT, BOARD_IMG, FONT_BITMAP
    try:
        FRAME_IMG = pygame.image.load("Assets/ui/frame.png").convert_alpha()
        FRAME_IMG = pygame.transform.scale(FRAME_IMG, (300, 400))
        
        SCROLL_IMG = pygame.image.load("Assets/ui/scroll.png").convert_alpha()
        SCROLL_IMG = pygame.transform.scale(SCROLL_IMG, (300, 380))

        # Dodajemy printy kontrolne
        ARROW_IMG = pygame.image.load("Assets/ui/strzalka1.png").convert_alpha()
        ARROW_IMG = pygame.transform.scale(ARROW_IMG, (96, 96))
        ARROW_IMG_LEFT = pygame.transform.flip(ARROW_IMG, True, False)
        print("Plik strzalka.png załadowany pomyślnie.")

        BOARD_IMG = pygame.image.load("Assets/ui/tablica.png").convert_alpha()
        BOARD_IMG = pygame.transform.scale(BOARD_IMG, (300, 76))
        print("Plik tablica.png załadowany pomyślnie.")

        FONT_BITMAP = pygame.image.load("Assets/ui/font.png").convert_alpha()

        print("Wszystkie zasoby UI załadowane.")
    except Exception as e:
        print(f"BŁĄD ŁADOWANIA UI: {e}")



def draw_keyboard_button(screen, text, x, y, width, height, is_selected, bg_color=None, border_color=(255, 255, 255)):
    rect = pygame.Rect(x, y, width, height)
    
    # 1. Określamy kolor wypełnienia
    if bg_color is None:
        # Jeśli nie podano koloru w argumencie, używamy domyślnych
        color = (100, 100, 255) if is_selected else (50, 50, 50)
    else:
        color = bg_color

    # 2. Rysujemy tło przycisku
    pygame.draw.rect(screen, color, rect, border_radius=10)
    
    # 3. Rysujemy ramkę (zawsze lub tylko gdy zaznaczony)
    # border_color to teraz ten Twój GOLD_BORDER
    if is_selected:
        pygame.draw.rect(screen, border_color, rect, 3, border_radius=10)



def change_color(surface, old_main, new_main, old_shadow, new_shadow):
    """Tworzy kopię obrazka z podmienionymi kolorami głównego tekstu i cienia."""
    img_copy = surface.copy()
    # PixelArray blokuje Surface, więc używamy 'with' lub usuwamy obiekt potem
    with pygame.PixelArray(img_copy) as pixels:
        pixels.replace(old_main, new_main)
        pixels.replace(old_shadow, new_shadow)
    return img_copy

def get_custom_text_width(text, scale=2):
    width = 0
    for char in text:
        if char == " ":
            width += 3 * scale
            continue
        metrics = get_char_metrics(char)
        width += (metrics["width"] + 1) * scale
    return width
def draw_menu(screen, menu_options, menu_index):
    text_str = "PRZYSTAN FIGHT CLUB"
    
    # Obliczamy szerokość dla skali 4
    text_width = get_custom_text_width(text_str, scale=4)
    x_pos = SCREEN_WIDTH // 2 - text_width // 2
    
    if FONT_BITMAP:
        draw_custom_text(
            screen, 
            text_str, 
            x_pos, 60, 
            FONT_BITMAP, 
            scale=4, 
            main_color="#77183c",  # Poprawione na 6 znaków
            shadow_color="#a54e4e"
        )

    # DEFINICJE KOLORÓW (Poza pętlą - LEPIEJ DLA WYDAJNOŚCI)
    PURPLE_BG   = pygame.Color("#77183c")
    GOLD_BORDER = pygame.Color("#e0821f")
    DARK_BG     = (40, 40, 40)
    WHITE_TEXT  = "#ffffff"
    GRAY_TEXT   = "#9ca3af"

    for i, opt in enumerate(menu_options):
        is_selected = (i == menu_index)
        bx, by = 350, 180 + i * 80
        bw, bh = 300, 60

        current_bg = PURPLE_BG if is_selected else DARK_BG
        
        # 1. Przycisk
        draw_keyboard_button(
            screen, "", bx, by, bw, bh, 
            is_selected, 
            bg_color=current_bg, 
            border_color=GOLD_BORDER
        )

        # 2. Tekst na przycisku
        text_w = get_custom_text_width(opt, scale=2)
        main_c = WHITE_TEXT if is_selected else GRAY_TEXT
        
        # Centrowanie w pionie: by + bh//2 - (8 * scale)//2 -> czyli 8 dla scale=2
        draw_custom_text(
            screen, opt, 
            bx + bw//2 - text_w//2, 
            by + bh//2 - 8, 
            FONT_BITMAP, scale=2, 
            main_color=main_c, 
            shadow_color="#000000"
        )

def draw_difficulty_select(screen, selected_idx):
    # 1. Tytuł (taki sam jak w Menu dla spójności)
    title_text = "WYBIERZ POZIOM TRUDNOŚCI"
    tw = get_custom_text_width(title_text, scale=3)
    draw_custom_text(
        screen, title_text, 
        SCREEN_WIDTH // 2 - tw // 2, 50, 
        FONT_BITMAP, scale=3, 
        main_color="#77183c", shadow_color="#a54e4e"
    )

    # Konfiguracja kolorów: (Kolor tła RGB, Kolor ramki RGB)
    # Używamy RGB, bo draw_keyboard_button tego oczekuje
    button_themes = [
        ((22, 101, 52), (74, 222, 128)),  # ŁATWY: Ciemnozielony / Jasnozielona ramka
        ((133, 77, 14), (250, 204, 21)),  # NORMALNY: Brąz / Złota ramka
        ((127, 29, 29), (239, 68, 68))    # TRUDNY: Ciemnoczerwony / Jasnoczerwona ramka
    ]
    
    # Kolory tekstów (HEX dla draw_custom_text)
    diff_text_colors = [
        ("#4ade80", "#166534"), # Zielony
        ("#facc15", "#854d0e"), # Żółty
        ("#ef4444", "#7f1d1d")  # Czerwony
    ]

    for i, label in enumerate(DIFFICULTY_LABELS):
        is_sel = (i == selected_idx)
        bx, by = 350, 180 + i * 80
        bw, bh = 300, 60
        
        # Logika kolorów przycisku
        if is_sel:
            bg_col, brd_col = button_themes[i]
            m_col, s_col = "#ffffff", "#000000" # Biały tekst na kolorowym tle
        else:
            bg_col, brd_col = (40, 40, 40), (80, 80, 80) # Szary dla niewybranych
            m_col, s_col = "#9ca3af", "#374151" # Szary tekst

        # 2. Rysujemy prostokąt przycisku
        draw_keyboard_button(
            screen, "", bx, by, bw, bh, 
            is_sel, 
            bg_color=bg_col, 
            border_color=brd_col
        )
        
        # 3. Tekst na przycisku
        lw = get_custom_text_width(label, scale=2)
        draw_custom_text(
            screen, label, 
            bx + bw//2 - lw//2, by + bh//2 - 8, 
            FONT_BITMAP, scale=2, 
            main_color=m_col, shadow_color=s_col
        )

    # 4. Podpowiedź na dole
    hint = "Gora/Dol - Zmiana | ENTER - Rozpocznij"
    hw = get_custom_text_width(hint, scale=1) # mniejsza skala dla hintu
    draw_custom_text(
        screen, hint, 
        SCREEN_WIDTH // 2 - hw // 2, 450, 
        FONT_BITMAP, scale=1, 
        main_color="#9ca3af", shadow_color="#000000"
    )

def draw_char_select(screen, p1_previews, p2_previews, p1_idx, p2_idx, char_names, game_mode):
    global arrow_offset_L, arrow_offset_R
    
    # Płynny powrót strzałek
    if arrow_offset_L < 0: arrow_offset_L += 1
    elif arrow_offset_L > 0: arrow_offset_L -= 1
    if arrow_offset_R < 0: arrow_offset_R += 1
    elif arrow_offset_R > 0: arrow_offset_R -= 1

    if game_mode == "multi":
        # --- KONFIGURACJA POZYCJI DLA MULTI ---
        # Centra ramek dla P1 i P2
        positions = [250, 750] 
        indices = [p1_idx, p2_idx]
        previews = [p1_previews[p1_idx], p2_previews[p2_idx]]
        player_labels = ["P1", "P2"]
        colors = ["#6464ff", "#ff6464"] # Niebieski dla P1, Czerwony dla P2

        for i in range(2):
            cx = positions[i]
            idx = indices[i]
            p_v = previews[i]
            
            # 1. Rysowanie ramki
            if FRAME_IMG:
                # Ramka ma szerokość 300 (z load_ui_assets), więc centrujemy ją odejmując 150
                rect = FRAME_IMG.get_rect(topleft=(cx - 150, 30))
                screen.blit(FRAME_IMG, rect)



                # 3. Tablica pod ramką
                if BOARD_IMG:
                    b_rect = BOARD_IMG.get_rect(midtop=(rect.centerx, rect.bottom - 30))
                    screen.blit(BOARD_IMG, b_rect)
                    
                    # Napis na tablicy: P1: Nazwa / P2: Nazwa
                    draw_custom_text(
                        screen, f"{player_labels[i]}: {char_names[idx]}", 
                        b_rect.centerx, b_rect.centery - 8, 
                        FONT_BITMAP, scale=2, 
                        main_color="#503214", shadow_color="#000000", 
                        center=True
                    )

                # 4. Rysowanie postaci wewnątrz ramki
                # Korekta wysokości dla Golema (idx 3) lub innych
                cy = rect.bottom - (130 if idx == 3 else 60 if idx == 2 else 50)
                p_v.update_animation()
                screen.blit(p_v.image, p_v.image.get_rect(midbottom=(cx, cy)))

    else:
        # --- TRYB SOLO (Kod bez zmian, który już miałeś) ---
        # --- TRYB SOLO ---
        frame_x, frame_y = 350, 30 
        
        if FRAME_IMG:
            rect = FRAME_IMG.get_rect(topleft=(frame_x - 150, frame_y))
            screen.blit(FRAME_IMG, rect)

            # Strzałki
            if ARROW_IMG:
                screen.blit(ARROW_IMG_LEFT, (rect.left - 60 + arrow_offset_L, rect.centery - 20))
                screen.blit(ARROW_IMG, (rect.right - 30 + arrow_offset_R, rect.centery - 20))

            # Tablica pod ramką
            if BOARD_IMG:
                b_rect = BOARD_IMG.get_rect(midtop=(rect.centerx, rect.bottom - 30))
                screen.blit(BOARD_IMG, b_rect)
                
                # NAZWA POSTACI NA TABLICY (Bitmapowa)
                draw_custom_text(
                    screen, char_names[p1_idx], 
                    b_rect.centerx, b_rect.centery - 8, 
                    FONT_BITMAP, scale=2, 
                    main_color="#503214", shadow_color="#977B617A", 
                    center=True
                )

            # Pozycja postaci
            cy = rect.bottom - (130 if p1_idx == 3 else 60 if p1_idx == 2 else 50)
            cx = rect.centerx
        else:
            cx, cy = frame_x, 300

        p_v = p1_previews[p1_idx]
        p_v.update_animation()
        screen.blit(p_v.image, p_v.image.get_rect(midbottom=(cx, cy)))

        # --- ZWÓJ ZE STATYSTYKAMI ---
        if SCROLL_IMG:
            s_rect = SCROLL_IMG.get_rect(topleft=(550, 30)) 
            screen.blit(SCROLL_IMG, s_rect)

            curr_name = char_names[p1_idx]
            stats = CHAR_STATS.get(curr_name, {})

            if stats:
                start_x = s_rect.x + 60
                start_y = s_rect.y + 70 
                
          
                
                # RYSOWANIE STATYSTYK (Bitmapowe)
                # Używamy brązowego koloru pasującego do zwoju
                scroll_text_color = "#643214"
                
                draw_custom_text(screen, f"Atak: {stats['damage']}", start_x, start_y, FONT_BITMAP, scale=2, main_color=scroll_text_color)
                draw_custom_text(screen, f"Hp: {stats['max_hp']}", start_x, start_y + 30, FONT_BITMAP, scale=2, main_color=scroll_text_color)
                draw_custom_text(screen, f"Szybkość: {stats['vel']}", start_x, start_y + 60, FONT_BITMAP, scale=2, main_color=scroll_text_color)
                
                # OPIS (Bitmapowy)
                desc_start_y = start_y + 105
                for i, line in enumerate(CHAR_DESCRIPTIONS.get(curr_name, ["Brak opisu."])):
                    draw_custom_text(screen, line, start_x, desc_start_y + i * 25, FONT_BITMAP, scale=1.5, main_color="#503214")
def draw_map_select(screen, available_maps, selected_idx):
    # 1. Tytuł (Skala 4 dla dużej widoczności)
    draw_custom_text(
        screen, "WYBIERZ ARENE", 
        SCREEN_WIDTH // 2, 80, 
        FONT_BITMAP, scale=4, 
        main_color="#ffffff", shadow_color="#444444", 
        center=True
    )

    # 2. Nazwa wybranej mapy z ozdobnymi nawiasami
    map_name = available_maps[selected_idx]["name"].upper()
    draw_custom_text(
        screen, f"<  {map_name}  >", 
        SCREEN_WIDTH // 2, 220, 
        FONT_BITMAP, scale=3, 
        main_color="#e0821f", shadow_color="#000000", 
        center=True
    )

    # 3. Podpowiedź sterowania (Skala 1, aby nie przytłaczała)
    hint_text = "A/D lub STRZALKI - Zmiana | ENTER - Walcz!"
    draw_custom_text(
        screen, hint_text, 
        SCREEN_WIDTH // 2, 350, 
        FONT_BITMAP, scale=1, 
        main_color="#9ca3af", shadow_color="#000000", 
        center=True
    )

def draw_settings(screen, bind_list, p1_ctrl, p2_ctrl, selected_idx, is_binding):
    # 1. Nagłówek PNG
    header_text = "USTAWIENIA KLAWISZY"
    hw = get_custom_text_width(header_text, scale=3)
    draw_custom_text(
        screen, header_text, 
        SCREEN_WIDTH // 2 - hw // 2, 20, 
        FONT_BITMAP, scale=3, 
        main_color="#77183c", shadow_color="#a54e4e"
    )

    # Kolory motywu
    PURPLE_BG = pygame.Color("#77183c")
    GOLD_BRD  = pygame.Color("#e0821f")
    BIND_BG   = pygame.Color("#a54e4e") # Czerwonawy kolor podczas bindowania
    DARK_BG   = (40, 40, 40)

    for i, (p_idx, label, action) in enumerate(bind_list):
        is_sel = (i == selected_idx)
        ctrl = p1_ctrl if p_idx == "P1" else p2_ctrl
        
        # Pobieramy nazwę klawisza
        key_val = ctrl[action]
        key_name = pygame.key.name(key_val).upper()
        
        # Formatowanie tekstu
        if is_binding and is_sel:
            display_text = f"{p_idx} {label}: <WCISNIJ KLAWISZ>"
            current_bg = BIND_BG # Zmiana koloru tła przy bindowaniu
        else:
            display_text = f"{p_idx} {label}: {key_name}"
            current_bg = PURPLE_BG if is_sel else DARK_BG

        # Pozycjonowanie (przyciski są cieńsze: height=35)
        bx, by = 250, 85 + i * 42
        bw, bh = 500, 35

        # 2. Rysowanie przycisku
        draw_keyboard_button(
            screen, "", bx, by, bw, bh, 
            is_sel, 
            bg_color=current_bg, 
            border_color=GOLD_BRD
        )

        # 3. Tekst PNG na przycisku
        # Używamy skali 1.5 lub 2, żeby tekst nie był za wielki w chudym przycisku
        tw = get_custom_text_width(display_text, scale=2)
        m_col = "#ffffff" if is_sel else "#9ca3af"
        
        # Centrowanie tekstu wewnątrz przycisku
        draw_custom_text(
            screen, display_text, 
            bx + 15, # Lekki margines od lewej zamiast pełnego centrowania (lepiej czytać listę)
            by + bh // 2 - 8, 
            FONT_BITMAP, scale=2, 
            main_color=m_col, shadow_color="#000000"
        )

    # 4. Stopka z instrukcją
    footer = "ESC - Powrot | ENTER - Zmien"
    fw = get_custom_text_width(footer, scale=1)
    draw_custom_text(
        screen, footer, 
        SCREEN_WIDTH // 2 - fw // 2, 530, 
        FONT_BITMAP, scale=1, 
        main_color="#e0821f", shadow_color="#000000"
    )

def draw_playing_hud(screen, p1, p2, game_mode, cpu_enemies):
    # 1. Paski HP (zakładam, że draw_hp_bar używa własnej logiki rysowania prostokątów)
    p1.draw_hp_bar(screen, 20, 20)

    if game_mode == "multi":
        p2.draw_hp_bar(screen, SCREEN_WIDTH - 20, 20, align_right=True)
        
        # Komunikat o końcu walki w trybie Multi
        if p1.is_dead or p2.is_dead:
            msg = "GRACZ 1 WYGRAL!" if p2.is_dead else "GRACZ 2 WYGRAL!"
            draw_custom_text(
                screen, msg, 
                SCREEN_WIDTH // 2, 200, 
                FONT_BITMAP, scale=4, 
                main_color="#ffffff", shadow_color="#000000", 
                center=True
            )
    else:
        # HUD dla trybu Single Player
        if not cpu_enemies:
            # Komunikat o wygranej (Zielony)
            draw_custom_text(
                screen, "POZIOM UKONCZONY!", 
                SCREEN_WIDTH // 2, 200, 
                FONT_BITMAP, scale=4, 
                main_color="#4ade80", shadow_color="#166534", 
                center=True
            )
        elif p1.is_dead:
            # Komunikat o przegranej (Czerwony)
            draw_custom_text(
                screen, "ZGINALES!", 
                SCREEN_WIDTH // 2, 200, 
                FONT_BITMAP, scale=4, 
                main_color="#ef4444", shadow_color="#7f1d1d", 
                center=True
            )
class ParallaxBackground:
    def __init__(self, screen_width, screen_height):
        self.sw = screen_width
        self.sh = screen_height

        self.layers_config = [
            ("sky.png", 0),
            ("far-mountains.png", 0.4),
            ("clouds.png", 0.7),
            ("canyon.png", 0.6),
            ("front.png", 1.0)
        ]

        self.layers = []
        for filename, speed in self.layers_config:
            try:
                img = pygame.image.load(f"Assets/layers/{filename}").convert_alpha()
            except Exception as e:
                print(f"Brak warstwy parallax '{filename}': {e}")
                img = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)

            ratio = self.sh / img.get_height()
            new_w = int(img.get_width() * ratio)
            img = pygame.transform.scale(img, (new_w, self.sh))

            # OPTYMALIZACJA: liczba kopii obliczana raz przy inicjalizacji
            # zamiast while-loop co klatkę
            copies = max(2, (screen_width // new_w) + 2)

            self.layers.append({
                'img': img,
                'speed': speed,
                'x': 0.0,   # float dla płynniejszego ruchu sub-pikselowego
                'w': new_w,
                'copies': copies
            })

    def update(self):
        for layer in self.layers:
            layer['x'] -= layer['speed']
            if layer['x'] <= -layer['w']:
                layer['x'] = 0.0

    def draw(self, screen):
        for layer in self.layers:
            # OPTYMALIZACJA: stała liczba blit'ów z copies, bez while-loop
            for i in range(layer['copies']):
                screen.blit(layer['img'], (int(layer['x'] + i * layer['w']), 0))