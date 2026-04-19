# -*- coding: utf-8 -*-
import pygame
import asyncio
import os
import sys
import random
import time
import io  # Zmieniono z 'from scipy import io' na standardowe 'import io'
from pathlib import Path
import assets_manager
# Wymuszenie UTF-8 dla konsoli (naprawia błąd charmap na niektórych systemach)
if sys.stdout.encoding != 'UTF-8':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except:
        pass


# Pygbag wymaga ustawienia katalogu roboczego na folder z main.py
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# =============================================================================
# WSZYSTKIE IMPORTY NIESTANDARDOWE MUSZĄ BYĆ WEWNĄTRZ main() W PYGBAG
# Tutaj tylko moduły standardowe i pygame
# =============================================================================

DEBUG_MODE = False

async def main():
    # -------------------------------------------------------------------------
    # IMPORTY — muszą być tutaj, wewnątrz async def main(), nie na górze pliku
    # Pygbag ładuje pliki .py asynchronicznie przez sieć — import na poziomie
    # modułu kończy się cichym crashem i szarym ekranem w przeglądarce
    # -------------------------------------------------------------------------
    import ui
    import map as map_module
    import characters as chars
    from characters import Soldier, Orc, HumanSoldier, Golem
    from items import Arrow, HealthPotion
    from config import (
        SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TILE_SCALE, TILE_SIZE,
        POTION_SPAWN_COOLDOWN, DEFAULT_P1_CONTROLS, DEFAULT_P2_CONTROLS,
        TILES_PATH, COLOR_BG, STATE_MENU, STATE_CHAR_SELECT,
        STATE_MAP_SELECT, STATE_SETTINGS, STATE_PLAYING, STATE_DIFF_SELECT,
        DIFFICULTY_LABELS, DIFFICULTY_VALUES
    )

    pygame.init()
    assets_manager.load_all_assets()
    # SCALED bez FULLSCREEN — FULLSCREEN nie działa poprawnie w przeglądarce
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SCALED | pygame.RESIZABLE)
    pygame.display.set_caption("Przystan Fight Game")
    clock = pygame.time.Clock()
    
    # --- ZMIENNE STANU ---
    menu_options = ["Jeden Gracz", "Dwóch Graczy", "USTAWIENIA"]
    menu_index = 0
    game_mode = "multi"
    game_state = STATE_MENU
    is_menu_music_playing = False
    diff_index = 1
    current_difficulty = DIFFICULTY_VALUES[1]

    available_chars = ["Soldier", "Orc", "Knight", "Golem"]
    p1_char_index, p2_char_index = 0, 1
    selected_map_index = 0
    setting_selected_idx = 0
    is_binding = False

    P1_CONTROLS = DEFAULT_P1_CONTROLS.copy()
    P2_CONTROLS = DEFAULT_P2_CONTROLS.copy()

    bind_list = [
        ("P1", "Atak 1", "atk1"), ("P1", "Atak 2", "atk2"),
        ("P1", "Specjalny", "special"), ("P1", "Blok", "block"),
        ("P2", "Atak 1", "atk1"), ("P2", "Atak 2", "atk2"),
        ("P2", "Specjalny", "special"), ("P2", "Blok", "block"),
    ]

    player1, player2 = None, None
    platforms, cpu_enemies, arrows, potions = [], [], [], []
    game_map_data = []
    map_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    current_bg_img = None
    potion_spawn_timer = 0
    fps_print_timer = 0


    def handle_menu_events(event, current_idx):
            new_state, new_mode = STATE_MENU, game_mode
            if event.key == pygame.K_UP: current_idx = (current_idx - 1) % len(menu_options)
            elif event.key == pygame.K_DOWN: current_idx = (current_idx + 1) % len(menu_options)
            elif event.key == pygame.K_RETURN:
                if current_idx == 0: new_mode, new_state = "single", STATE_DIFF_SELECT
                elif current_idx == 1: new_mode, new_state = "multi", STATE_CHAR_SELECT
                elif current_idx == 2: new_state = STATE_SETTINGS
            return new_state, current_idx, new_mode

    def handle_diff_events(event, current_diff_idx):
        if event.key == pygame.K_UP: current_diff_idx = (current_diff_idx - 1) % len(DIFFICULTY_LABELS)
        elif event.key == pygame.K_DOWN: current_diff_idx = (current_diff_idx + 1) % len(DIFFICULTY_LABELS)
        elif event.key == pygame.K_ESCAPE: return STATE_MENU, current_diff_idx, DIFFICULTY_VALUES[current_diff_idx]
        elif event.key == pygame.K_RETURN:
            return STATE_CHAR_SELECT, current_diff_idx, DIFFICULTY_VALUES[current_diff_idx]
        return STATE_DIFF_SELECT, current_diff_idx, DIFFICULTY_VALUES[current_diff_idx]

    def handle_char_select_events(event, p1_idx, p2_idx):
        nonlocal player1, player2, platforms, cpu_enemies, game_map_data, current_bg_img
        
        if event.key == pygame.K_ESCAPE: return STATE_MENU, p1_idx, p2_idx
        
        # P1 wybór (A/D lub Strzałki w Single)
        if event.key == pygame.K_a or (game_mode == "single" and event.key == pygame.K_LEFT):
            p1_idx = (p1_idx - 1) % 4
            ui.arrow_offset_L = -15
        if event.key == pygame.K_d or (game_mode == "single" and event.key == pygame.K_RIGHT):
            p1_idx = (p1_idx + 1) % 4
            ui.arrow_offset_R = 15

        # P2 wybór
        if game_mode == "multi":
            if event.key == pygame.K_LEFT: p2_idx = (p2_idx - 1) % 4; ui.arrow_offset_L = -15
            if event.key == pygame.K_RIGHT: p2_idx = (p2_idx + 1) % 4; ui.arrow_offset_L = 15

        if event.key == pygame.K_RETURN:
            # Inicjalizacja walki
            player1 = spawn_character(available_chars[p1_idx], 100, 250)
            target_p2_idx = p1_idx if game_mode == "single" else p2_idx
            player2 = spawn_character(available_chars[target_p2_idx], 300, 250)
            
            if game_mode == "single":
                # Automatyczny start na losowej mapie
                level = random.choice(map_module.single_levels)
                platforms.clear()
                game_map_data = map_module.build_platforms(level["data"], platforms, cpu_enemies, "single")
                redraw_map()
                current_bg_img = map_module.load_background(level["bg_path"])
                return STATE_PLAYING, p1_idx, p2_idx
            else:
                return STATE_MAP_SELECT, p1_idx, p2_idx
                
        return STATE_CHAR_SELECT, p1_idx, p2_idx
    

    def toggle_fullscreen():
        try:
            # To jest natywna metoda Pygame, która najlepiej radzi sobie z flagą SCALED
            pygame.display.toggle_fullscreen()
            
            # WAŻNE: Po przełączeniu warto odświeżyć mapę, 
            # bo format pikseli ekranu mógł się zmienić
            if game_map_data:
                redraw_map()
        except Exception as e:
            print(f"Błąd przełączania: {e}")

    def handle_settings_events(event, current_idx, binding_status):
        nonlocal game_state, is_binding
        if binding_status:
            # Przypisanie klawisza
            p_idx, label, action = bind_list[current_idx]
            if p_idx == "P1": P1_CONTROLS[action] = event.key
            else: P2_CONTROLS[action] = event.key
            return STATE_SETTINGS, current_idx, False
        else:
            if event.key == pygame.K_UP:
                current_idx = (current_idx - 1) % len(bind_list)
            elif event.key == pygame.K_DOWN:
                current_idx = (current_idx + 1) % len(bind_list)
            elif event.key == pygame.K_RETURN:
                return STATE_SETTINGS, current_idx, True
            elif event.key == pygame.K_ESCAPE:
                return STATE_MENU, current_idx, False
        return STATE_SETTINGS, current_idx, binding_status

    def handle_map_select_events(event, current_map_idx):
        nonlocal game_state, platforms, cpu_enemies, arrows, potions, game_map_data, current_bg_img, map_surface
        
        if event.key == pygame.K_ESCAPE:
            return STATE_CHAR_SELECT, current_map_idx
        
        if event.key in (pygame.K_LEFT, pygame.K_a):
            current_map_idx = (current_map_idx - 1) % len(map_module.available_maps)
        elif event.key in (pygame.K_RIGHT, pygame.K_d):
            current_map_idx = (current_map_idx + 1) % len(map_module.available_maps)
            
        elif event.key == pygame.K_RETURN:
            info = map_module.available_maps[current_map_idx]
            platforms.clear()
            cpu_enemies.clear()
            arrows.clear()
            potions.clear()
            
            game_map_data = map_module.build_platforms(info["data"], platforms, cpu_enemies, game_mode)
            redraw_map()
            current_bg_img = map_module.load_background(info["bg_path"])
            
            # --- POPRAWKA: Bezpieczny reset pozycji ---
            # Sprawdzamy, czy obiekty istnieją, zanim odwołamy się do .rect
            if player1 is not None:
                player1.rect.topleft = (100, 250)
            
            if game_mode == "multi" and player2 is not None:
                player2.rect.topleft = (900, 250)
            elif player2 is not None:
                # W single player player2 może być technicznie None lub nieużywany
                player2.rect.topleft = (700, 250)

            return STATE_PLAYING, current_map_idx
            
        return STATE_MAP_SELECT, current_map_idx

    def handle_playing_events(event):
        nonlocal game_state
        if event.key == pygame.K_ESCAPE:
            return STATE_MENU
        
        # --- BEZPIECZNE SPRAWDZENIE ŚMIERCI ---
        # Sprawdzamy czy player1 istnieje, jeśli nie (None), zakładamy że nie żyje (False)
        is_p1_dead = player1.is_dead if player1 is not None else False
        
        # Dla P2 sprawdzamy: czy jest tryb multi ORAZ czy player2 istnieje
        is_p2_dead = False
        if game_mode == "multi" and player2 is not None:
            is_p2_dead = player2.is_dead
        
        # Restart po śmierci (powrót do menu)
        if event.key == pygame.K_RETURN and (is_p1_dead or is_p2_dead):
            return STATE_MENU
            
        return STATE_PLAYING






    def redraw_map():
        nonlocal map_surface
        map_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

        # Ustawiamy czarny kolor (0,0,0) jako przezroczysty dla tej powierzchni
        map_surface.set_colorkey((0, 0, 0))

        for r_idx, row in enumerate(game_map_data):
            for c_idx, t_idx in enumerate(row):
                if isinstance(t_idx, int):
                    map_surface.blit(tiles[t_idx], (c_idx * TILE_SIZE, r_idx * TILE_SIZE))
        map_surface = map_surface.convert()
    # --- ŁADOWANIE ZASOBÓW ---


    def spawn_character(name, x, y):
        mapping = {"Soldier": Soldier, "Orc": Orc, "Knight": HumanSoldier, "Golem": Golem}
        return mapping.get(name, Soldier)(x, y)

    def draw_debug_info(surface, platforms_list, players, enemies):
        for plat in platforms_list:
            pygame.draw.rect(surface, (255, 0, 0), plat, 2)
        for p in players + enemies:
            if not p.is_dead:
                pygame.draw.rect(surface, (0, 255, 0), p.rect, 2)
                pygame.draw.rect(surface, (0, 0, 255), p.hitbox, 1)

    # Ładujemy zasoby po inicjalizacji pygame
    ui.load_ui_assets()
    tiles = map_module.load_tiles(TILES_PATH, TILE_SCALE)
    # ------------------------------

    
    menu_parallax = ui.ParallaxBackground(SCREEN_WIDTH, SCREEN_HEIGHT)

    p1_previews = [Soldier(200, 150), Orc(200, 150), HumanSoldier(200, 150), Golem(200, 150)]
    p2_previews = [Soldier(650, 150), Orc(650, 150), HumanSoldier(650, 150), Golem(650, 150)]
    for p in p1_previews: p.direction = 'right'
    for p in p2_previews: p.direction = 'left'

    # =========================================================================
    # GŁÓWNA PĘTLA
    # =========================================================================
    while True:
        if DEBUG_MODE:
            try:
                import time
                start_time = time.perf_counter()
            except:
                start_time = None
        keys_pressed = pygame.key.get_pressed()
        if game_state != STATE_PLAYING:
            screen.fill(COLOR_BG)

        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                # 1. Globalne
                if event.key == pygame.K_f:
                    toggle_fullscreen()
                
                # 2. Specyficzne dla stanu
                if game_state == STATE_MENU:
                    game_state, menu_index, game_mode = handle_menu_events(event, menu_index)
                
                elif game_state == STATE_SETTINGS:
                    game_state, setting_selected_idx, is_binding = handle_settings_events(event, setting_selected_idx, is_binding)
                
                elif game_state == STATE_DIFF_SELECT:
                    game_state, diff_index, current_difficulty = handle_diff_events(event, diff_index)
                
                elif game_state == STATE_CHAR_SELECT:
                    game_state, p1_char_index, p2_char_index = handle_char_select_events(event, p1_char_index, p2_char_index)
                
                elif game_state == STATE_MAP_SELECT:
                    game_state, selected_map_index = handle_map_select_events(event, selected_map_index)
                
                elif game_state == STATE_PLAYING:
                    game_state = handle_playing_events(event)
                states_with_music = [STATE_MENU, STATE_CHAR_SELECT, STATE_MAP_SELECT, STATE_SETTINGS, STATE_DIFF_SELECT]
                
                if game_state in states_with_music:
                    if not is_menu_music_playing:
                        assets_manager.play_bg_music("megaman.wav", loop=-1)
                        is_menu_music_playing = True
                else:
                    # Jeśli weszliśmy do STATE_PLAYING, a muzyka menu wciąż gra -> wyłącz ją
                    if is_menu_music_playing:
                        assets_manager.stop_music()
                        is_menu_music_playing = False    
        # --- RENDERING ---
        
        if game_state in [STATE_MENU, STATE_DIFF_SELECT, STATE_CHAR_SELECT, STATE_MAP_SELECT, STATE_SETTINGS]:
            menu_parallax.update()
            menu_parallax.draw(screen)

        if game_state == STATE_MENU:
            ui.draw_menu(screen, menu_options, menu_index)
        elif game_state == STATE_DIFF_SELECT:
            ui.draw_difficulty_select(screen, diff_index)
        elif game_state == STATE_CHAR_SELECT:
            ui.draw_char_select(screen, p1_previews, p2_previews, p1_char_index, p2_char_index, available_chars, game_mode)
        elif game_state == STATE_MAP_SELECT:
            ui.draw_map_select(screen, map_module.available_maps, selected_map_index)
        elif game_state == STATE_SETTINGS:
            ui.draw_settings(screen, bind_list, P1_CONTROLS, P2_CONTROLS, setting_selected_idx, is_binding)

        elif game_state == STATE_PLAYING:
            
            all_chars = []
            if current_bg_img:
                screen.blit(current_bg_img, (0, 0))
            else:
                screen.fill(COLOR_BG)

            screen.blit(map_surface, (0, 0))

            if player1 is not None:
                if game_mode == "multi":
                    # Sprawdzamy, czy player2 istnieje w trybie multi
                    if player2 is not None:
                        player1.update(player2, arrows, P1_CONTROLS, platforms, keys_pressed) 
                        player2.update(player1, arrows, P2_CONTROLS, platforms, keys_pressed)
                        all_chars = [player1, player2]
                else:
                    # Tryb Single Player
                    player1.update(cpu_enemies, arrows, P1_CONTROLS, platforms, keys_pressed) 
                    
                    for en in cpu_enemies[:]:
                        en.update_cpu(player1, arrows, platforms) 
                        if en.is_dead and int(en.frame_index) >= len(en.animations['death'][0]) - 1:
                            cpu_enemies.remove(en)
                    all_chars = [player1] + cpu_enemies

                    # Logika przejścia na kolejny poziom (Single Player)
                    if not cpu_enemies and not player1.is_dead:
                        level = random.choice(map_module.single_levels)
                        platforms.clear()
                        game_map_data = map_module.build_platforms(level["data"], platforms, cpu_enemies, game_mode)
                        redraw_map()
                        for en in cpu_enemies:
                            en.difficulty = current_difficulty
                        current_bg_img = map_module.load_background(level["bg_path"])
                        player1.current_hp = min(player1.current_hp + 20, player1.max_hp)
                        potion_spawn_timer = 0
            else:
                # Jeśli jakimś cudem jesteśmy w STATE_PLAYING bez postaci, wróć do menu
                game_state = STATE_MENU
            for p in filter(None, all_chars):
                p.screen_wrap()
                img_rect = p.image.get_rect(midbottom=(p.rect.centerx, p.rect.bottom + p.image_offset_y))
                screen.blit(p.image, img_rect)
                if p not in (player1, player2) and not p.is_dead:
                    bx, by = p.rect.centerx - 20, p.rect.top - 15
                    pygame.draw.rect(screen, (100, 0, 0), (bx, by, 40, 5))
                    pygame.draw.rect(screen, (0, 255, 0), (bx, by, int(40 * p.current_hp / p.max_hp), 5))

            targets = [player1, player2, *cpu_enemies]

            for pot in potions[:]:
                if pot.update(platforms, targets):
                    potions.remove(pot)
                else:
                    screen.blit(pot.image, pot.rect)

            for arr in arrows[:]:
                arr.update(targets)
                if not arr.active:
                    arrows.remove(arr)
                else:
                    screen.blit(arr.image, arr.rect)

            potion_spawn_timer += 1
            if potion_spawn_timer >= POTION_SPAWN_COOLDOWN:
                if len(potions) < 3:
                    potions.append(HealthPotion(random.randint(100, SCREEN_WIDTH - 100), -50))
                potion_spawn_timer = 0

            if DEBUG_MODE:
                debug_players = [player1]
                if game_mode == "multi":
                    debug_players.append(player2)
                draw_debug_info(screen, platforms, debug_players, cpu_enemies)

            ui.draw_playing_hud(screen, player1, player2, game_mode, cpu_enemies)

        pygame.display.flip()

        if DEBUG_MODE and start_time is not None:
            try:
                
                frame_logic_time = (time.perf_counter() - start_time) * 1000
                fps_print_timer += 1
                if fps_print_timer >= 180:
                    print(f"FPS: {clock.get_fps():.1f} | Logika+Render: {frame_logic_time:.2f}ms")
                    fps_print_timer = 0
            except:
                pass
        # Zamiast sztywnego clock.tick(FPS), spróbuj:
        await asyncio.sleep(0) # Pozwól przeglądarce odetchnąć
        clock.tick(FPS) # Na desktopie zostaw stare zachowanie


# Pygbag wymaga dokładnie tego wzorca uruchomienia
asyncio.run(main())