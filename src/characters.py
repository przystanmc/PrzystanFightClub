# -*- coding: utf-8 -*-
import pygame
import random
from config import SCREEN_WIDTH
from items import Arrow
import assets_manager
class Character(pygame.sprite.Sprite):
    def __init__(self, x, y, folder, scale=2.5, hp=100, speed=5, damage=10, width=40, height=60):
        super().__init__()
        self.folder = folder
        self.scale = scale
        self.max_hp = hp
        self.current_hp = hp
        self.vel = speed
        self.damage = damage
        self.can_shoot = False
        self.animations = {}
        self.state = 'idle'
        self.frame_index = 0
        self.direction = 'right'
        self.is_attacking = False
        self.is_blocking = False
        self.is_dead = False
        self.hit_cooldown = 0
        self.rect = pygame.Rect(x, y, width, height)
        self.hitbox = pygame.Rect(x, y, width, height)
        self.vel_y = 0
        self.gravity = 0.8
        self.jump_height = -16
        self.is_jumping = False
        self.image = pygame.Surface((100, 100))
        self.cpu_action_timer = 0
        self.cpu_current_action = None
        self.image_offset_y = 0

    def load_sheet(self, filename, frame_count, width, height):
        path = f"{self.folder}/{filename}"
        try:
            sheet = pygame.image.load(path).convert_alpha()
            frames_right = []
            frames_left  = []
            for i in range(frame_count):
                frame = sheet.subsurface((i * width, 0, width, height))
                frame = pygame.transform.scale(frame, (int(width * self.scale), int(height * self.scale)))
                frames_right.append(frame)
                frames_left.append(pygame.transform.flip(frame, True, False))  # ← raz przy starcie
            return frames_right, frames_left   # zwracamy dwie listy
        except Exception as e:
            surf = pygame.Surface((50, 50))
            surf.fill((100, 0, 0))
            fallback = [surf] * frame_count
            return fallback, fallback  
    def draw_hp_bar(self, surface, x, y, width=200, height=20, align_right=False):
        # Obliczanie szerokości zielonego paska
        ratio = self.current_hp / self.max_hp
        current_width = int(width * ratio)

        # Jeśli pasek ma być wyrównany do prawej (dla P2)
        draw_x = x - width if align_right else x

        # 1. Tło paska (ciemnoczerwone)
        pygame.draw.rect(surface, (100, 0, 0), (draw_x, y, width, height))

        # 2. Zdrowie (jasnozielone)
        # Jeśli wyrównujemy do prawej, zielony pasek musi się "cofać" od prawej krawędzi
        fill_x = draw_x + (width - current_width) if align_right else draw_x
        pygame.draw.rect(surface, (0, 255, 0), (fill_x, y, current_width, height))

        # 3. Ramka (biała)
        pygame.draw.rect(surface, (255, 255, 255), (draw_x, y, width, height), 2)
    def update_hitbox(self):
        self.hitbox.centerx = self.rect.centerx
        self.hitbox.centery = self.rect.centery - 5



    def take_damage(self, amount):
        if self.is_dead or self.is_blocking: return
        self.current_hp -= amount
        if self.current_hp <= 0:
            self.current_hp = 0
            self.is_dead = True
            self.state = 'death'
        else:
            self.state = 'hit'
        self.frame_index = 0

    def update_animation(self):
        side = 1 if self.direction == 'left' else 0   # 0=right, 1=left
        if self.is_dead:
            frames = self.animations['death'][side]
            self.frame_index = min(self.frame_index + 0.15, len(frames) - 1)
        elif self.state == 'block' and self.is_blocking:
            frames = self.animations.get('block', self.animations['idle'])[side]
            self.frame_index = min(self.frame_index + 0.15, len(frames) - 1)
        else:
            frames = self.animations.get(self.state, self.animations['idle'])[side]
            anim_speed = 0.25 if (self.is_attacking or self.state == 'hit') else 0.18
            self.frame_index += anim_speed
            if self.frame_index >= len(frames):
                if self.is_attacking or self.state == 'hit':
                    self.is_attacking = False
                    self.state = 'idle'
                self.frame_index = 0
        self.image = frames[int(self.frame_index)]

    def apply_gravity(self, platforms_list):
        # 1. Zastosuj grawitację do prędkości
        self.vel_y += self.gravity

        # 2. Ruch w pionie (oś Y)
        self.rect.y += self.vel_y

        # 3. Sprawdzanie kolizji po ruchu w pionie
        for platform in platforms_list:
            if self.rect.colliderect(platform):
                if self.vel_y > 0: # SPADANIE
                    # Jeśli uderzyliśmy w górną krawędź platformy
                    self.rect.bottom = platform.top
                    self.vel_y = 0
                    self.is_jumping = False
                elif self.vel_y < 0: # SKOK (uderzenie głową w sufit)
                    # Jeśli uderzyliśmy w dolną krawędź platformy
                    self.rect.top = platform.bottom
                    self.vel_y = 0
    def start_attack(self, type='attack1'):
        if not self.is_attacking:
            assets_manager.play_sound("empty_hit")
            self.state = type
            self.is_attacking = True
            self.frame_index = 0
     
    def play_hit_sound(self):
        assets_manager.play_sound("hit")       
    def jump(self):
        if not self.is_jumping:
            assets_manager.play_sound("jump")
            self.vel_y = self.jump_height
            self.is_jumping = True
            self.state = 'jump'
            self.frame_index = 0


    def play_attack_impact_sound(self):
        """Domyślny dźwięk trafienia przeciwnika (np. mieczem)"""
        assets_manager.play_sound("hit")

    def check_attack_collision(self, target):
        # Sprawdzamy czy klatka animacji to moment zadania ciosu (np. klatki 2-5)
        if self.is_attacking and self.state in ['attack1', 'attack2'] and 2 <= int(self.frame_index) <= 5:
            attack_rect = pygame.Rect(0, 0, 40, 60)
            if self.direction == 'right': attack_rect.left = self.hitbox.right
            else: attack_rect.right = self.hitbox.left
            attack_rect.centery = self.hitbox.centery

            targets_to_check = target if isinstance(target, list) else [target]
            for t in targets_to_check:
                if t and t != self and not t.is_dead:
                    target_box = getattr(t, 'hitbox', t.rect)
                    if attack_rect.colliderect(target_box):
                        if t.hit_cooldown == 0:
                            # --- KLUCZOWA ZMIANA ---
                            # Wywołujemy dźwięk ATAKUJĄCEGO, a nie ofiary
                            self.play_attack_impact_sound() 
                            
                            t.take_damage(self.damage)
                            t.hit_cooldown = 20

    
    def move_and_check_walls(self, dx, platforms_list):
        # 1. Przesuwamy się w poziomie
        self.rect.x += dx

        # 2. Sprawdzamy, czy weszliśmy w jakąś platformę
        for platform in platforms_list:
            if self.rect.colliderect(platform):
                # Jeśli idziemy w prawo i uderzyliśmy w ścianę
                if dx > 0:
                    self.rect.right = platform.left
                # Jeśli idziemy w lewo i uderzyliśmy w ścianę
                elif dx < 0:
                    self.rect.left = platform.right                        

    def screen_wrap(self):
        if self.rect.centerx > SCREEN_WIDTH: self.rect.centerx = 0
        elif self.rect.centerx < 0: self.rect.centerx = SCREEN_WIDTH

    def update_cpu(self, target, arrows_list, platforms_list):
        if self.is_dead:
            self.update_animation()
            return

        dx = target.rect.centerx - self.rect.centerx
        distance = abs(dx)
        diff = getattr(self, 'difficulty', 1.0)
        cpu_keys = {k: False for k in ['left', 'right', 'jump', 'atk1', 'atk2', 'special', 'block']}
        check_dist = 20
        check_rect = pygame.Rect(0, 0, check_dist, self.rect.height)
        if dx > 0: check_rect.left = self.rect.right
        else: check_rect.right = self.rect.left
        check_rect.y = self.rect.y
        for platform in platforms_list:
            if check_rect.colliderect(platform):
                cpu_keys['jump'] = True  # Widzi ścianę -> skacze
                break

        # --- 1. REAKCJA NA ZAGROŻENIA ---
        for arrow in arrows_list:
            if arrow.owner != self and abs(arrow.rect.centerx - self.rect.centerx) < (200 * diff):
                if random.random() < (0.2 * diff):
                    cpu_keys['block'] = True
                    self.apply_cpu_controls(cpu_keys, target, arrows_list, platforms_list)
                    return # Jeśli blokuje, niech nie robi nic innego w tej klatce

        # --- 2. DECYZJA O RUCHU ---
        if self.cpu_action_timer > 0:
            if self.cpu_current_action: cpu_keys[self.cpu_current_action] = True
            self.cpu_action_timer -= 1
        else:
            # MARTWA STREFA (Deadzone): Jeśli jesteś bardzo blisko, przestań biegać w kółko
            if distance < 20:
                cpu_keys['left'] = False
                cpu_keys['right'] = False
                # Ustaw kierunek na gracza, by wiedział gdzie uderzyć
                self.direction = 'right' if dx > 0 else 'left'

                # Skoro jesteś blisko, po prostu atakuj
                if random.random() < (0.1 * diff):
                    cpu_keys['atk1'] = True

            elif not self.is_attacking:
                # Ustalanie dystansu
                desired_min = 200 if self.can_shoot else 30
                desired_max = 400 if self.can_shoot else 65

                if distance > desired_max:
                    if dx > 0: cpu_keys['right'] = True
                    else: cpu_keys['left'] = True
                elif distance < desired_min:
                    if self.can_shoot: # Soldier ucieka (kiting)
                        if dx > 0: cpu_keys['left'] = True
                        else: cpu_keys['right'] = True
                    # Wojownik/Golem (brak can_shoot) NIE cofa się, jeśli dystans jest mały (30-65)

                # --- 3. LOGIKA ATAKU ---
                if distance <= 75:
                    if random.random() < (0.05 * diff):
                        if random.random() > 0.3:
                            cpu_keys['atk1'] = True
                        else:
                            cpu_keys['atk2'] = True
                elif self.can_shoot and distance > 220:
                    if random.random() < (0.01 * diff):
                        cpu_keys['special'] = True
                        self.cpu_action_timer = 40
                        self.cpu_current_action = 'special'

        self.apply_cpu_controls(cpu_keys, target, arrows_list, platforms_list)
    def apply_cpu_controls(self, keys, target, arrows_list, platforms_list):
        if self.is_dead: return

        # Priorytet 1: Atak (blokuje możliwość zmiany ruchu)
        if self.is_attacking:
            pass

            # Priorytet 2: Blok
        elif keys['block'] and not self.is_jumping:
            self.is_blocking = True
            self.state = 'block'

        # Priorytet 3: Ruch i reszta
        else:
            self.is_blocking = False

            if keys['jump'] and not self.is_jumping:
                self.jump() # Używamy nowej metody z dźwiękiem0

            if keys['left']:
                self.move_and_check_walls(-self.vel, platforms_list)
                self.direction = 'left'
                if not self.is_jumping: self.state = 'walk'
            elif keys['right']:
                self.move_and_check_walls(self.vel, platforms_list)
                self.direction = 'right'
                if not self.is_jumping: self.state = 'walk'
            else:
                if not self.is_jumping and not self.is_attacking:
                    self.state = 'idle'

            # Sprawdzanie nowych ataków
            if keys['atk1']:
                if not self.is_attacking: assets_manager.play_sound("empty_hit") # <--- DODAJ
                self.state = 'attack1'
                self.is_attacking = True
                self.frame_index = 0
            elif keys['atk2']:
                if not self.is_attacking: assets_manager.play_sound("empty_hit") # <--- DODAJ
                self.state = 'attack2'
                self.is_attacking = True
                self.frame_index = 0
            elif keys['special'] and self.can_shoot:
                self.state = 'bow'
                self.is_attacking = True
                self.frame_index = 0
                self.arrow_shot = False

        # FIZYKA (Musi być wcięte tak samo jak "if self.is_attacking")
        self.apply_gravity(platforms_list)
        self.update_hitbox()
        self.check_attack_collision(target)
        if self.hit_cooldown > 0:
            self.hit_cooldown -= 1
        self.update_animation()


    # =============================================================================
# KONKRETNE POSTACIE
# =============================================================================

class Soldier(Character):
    def __init__(self, x, y):
        super().__init__(x, y, "Assets/Soldier", hp=80, speed=6, damage=12, width=40, height=45)
        self.image_offset_y = 110
        self.arrow_shot = False
        self.can_shoot = True  # domyślnie żadna postać nie strzela
        self.animations = {
            'idle':    self.load_sheet('Soldier_Idle.png', 6, 100, 100),
            'walk':    self.load_sheet('Soldier_Walk.png', 8, 100, 100),
            'jump':    self.load_sheet('Soldier_Jump.png', 7, 100, 100),
            'attack1': self.load_sheet('Soldier_Attack01.png', 6, 100, 100),
            'attack2': self.load_sheet('Soldier_Attack02.png', 6, 100, 100),
            'bow':     self.load_sheet('Soldier_Attack03_No_Special_Effects.png', 9, 100, 100),
            'hit':     self.load_sheet('Soldier_Hit.png', 5, 100, 100),
            'death':   self.load_sheet('Soldier_Death.png', 4, 100, 100),
        }

    def update(self, target, arrows_list, controls, platforms_list, keys):
    # używaj zmiennej 'keys', usuń pygame.key.get_pressed()
        if self.is_dead:
            self.update_animation()
            return
        # keys = pygame.key.get_pressed()
        if not self.is_attacking and self.state != 'hit':
            if keys[controls['left']]:
                self.direction = 'left'
                self.move_and_check_walls(-self.vel, platforms_list) # POPRAWIONE
                if not self.is_jumping: self.state = 'walk'
            elif keys[controls['right']]:
                self.direction = 'right'
                self.move_and_check_walls(self.vel, platforms_list)  # POPRAWIONE
                if not self.is_jumping: self.state = 'walk'
            else:
                if not self.is_jumping: self.state = 'idle'
            if keys[controls['jump']] and not self.is_jumping:
                self.jump() # To wywoła dźwięk i ustawi fizykę skoku
            if keys[controls['atk1']]: 
                self.start_attack('attack1')
            elif keys[controls['atk2']]: 
                self.start_attack('attack2')
            elif keys[controls['special']]:
                # Łuk zostawiamy ręcznie, bo ma specyficzną logikę arrow_shot
                if not self.is_attacking:
                    self.state = 'bow'; self.is_attacking = True; self.frame_index = 0; self.arrow_shot = False

        if self.state == 'bow' and int(self.frame_index) == 6 and not self.arrow_shot:
            sp_x = self.hitbox.right if self.direction == 'right' else self.hitbox.left

            # Przesunięcie: bierzemy dół hitboxa i odejmujemy np. 15-20 pikseli w górę
            # Dostosuj tę wartość (18), aż strzała pokryje się z łukiem
            arrow_height = self.hitbox.bottom - 11

            arrows_list.append(Arrow(sp_x, arrow_height, self.direction, self))
            self.arrow_shot = True

        self.apply_gravity(platforms_list)
        self.update_hitbox()
        self.check_attack_collision(target)
        if self.hit_cooldown > 0:
            self.hit_cooldown -= 1
        self.update_animation()

class Orc(Character):
    def __init__(self, x, y):
        super().__init__(x, y, "Assets/Orc", hp=90, speed=5, damage=14, width=40, height=45)
        self.image_offset_y = 110
        self.animations = {
            'idle':    self.load_sheet('Orc_Idle.png', 6, 100, 100),
            'walk':    self.load_sheet('Orc_Walk.png', 8, 100, 100),
            'jump':    self.load_sheet('Orc_Jump.png', 7, 100, 100),
            'attack1': self.load_sheet('Orc_Attack01.png', 6, 100, 100),
            'attack2': self.load_sheet('Orc_Attack02.png', 6, 100, 100),
            'block':   self.load_sheet('Orc_Defense.png', 3, 100, 100),
            'hit':     self.load_sheet('Orc_Hit.png', 5, 100, 100),
            'death':   self.load_sheet('Orc_Death.png', 4, 100, 100),
        }

    def update(self, target, arrows_list, controls, platforms_list, keys):
        if self.is_dead:
            self.update_animation()
            return

        self.is_blocking = keys[controls['block']] and not self.is_jumping
        if self.is_blocking:
            self.state = 'block'
        elif not self.is_attacking and self.state != 'hit':
            if keys[controls['left']]:
                self.direction = 'left'
                self.move_and_check_walls(-self.vel, platforms_list) # POPRAWIONE
                if not self.is_jumping: self.state = 'walk'
            elif keys[controls['right']]:
                self.direction = 'right'
                self.move_and_check_walls(self.vel, platforms_list)  # POPRAWIONE
                if not self.is_jumping: self.state = 'walk'
            else:
                if not self.is_jumping: self.state = 'idle'
            if keys[controls['jump']] and not self.is_jumping:
                self.jump() # To wywoła dźwięk i ustawi fizykę skoku
            if keys[controls['atk1']]: 
                self.start_attack('attack1')
            elif keys[controls['atk2']]: 
                self.start_attack('attack2')

        self.apply_gravity(platforms_list)
        self.update_hitbox()
        self.check_attack_collision(target)
        if self.hit_cooldown > 0:
            self.hit_cooldown -= 1
        self.update_animation()

class HumanSoldier(Character):
    def __init__(self, x, y):
        super().__init__(x, y, "Assets/Human_Soldier_Sword_Shield", scale=2.5, hp=100, speed=6, damage=11, width=40, height=45)
        self.image_offset_y = 95
        W, H = 96, 96
        self.animations = {
            'idle':    self.load_sheet('Human_Soldier_Sword_Shield_Idle-Sheet.png', 6, W, H),
            'walk':    self.load_sheet('Human_Soldier_Sword_Shield_Walk-Sheet.png', 8, W, H),
            'jump':    self.load_sheet('Human_Soldier_Sword_Shield_Jump_Fall-Sheet.png', 5, W, H),
            'attack1': self.load_sheet('Human_Soldier_Sword_Shield_Attack1-Sheet.png', 8, W, H),
            'attack2': self.load_sheet('Human_Soldier_Sword_Shield_Attack2-Sheet.png', 8, W, H),
            'block':   self.load_sheet('Human_Soldier_Sword_Shield_Block-Sheet.png', 6, W, H),
            'hit':     self.load_sheet('Human_Soldier_Sword_Shield_Hurt-Sheet.png', 4, W, H),
            'death':   self.load_sheet('Human_Soldier_Sword_Shield_Death-Sheet.png', 10, W, H),
        }

    def update(self, target, arrows_list, controls, platforms_list, keys):
        if self.is_dead:
            self.update_animation()
            return
        
        self.is_blocking = keys[controls['block']] and not self.is_jumping and not self.is_attacking
        if self.is_blocking:
            self.state = 'block'
        elif not self.is_attacking and self.state != 'hit':
            if keys[controls['left']]:
                self.direction = 'left'
                self.move_and_check_walls(-self.vel, platforms_list) # POPRAWIONE
                if not self.is_jumping: self.state = 'walk'
            elif keys[controls['right']]:
                self.direction = 'right'
                self.move_and_check_walls(self.vel, platforms_list)  # POPRAWIONE
                if not self.is_jumping: self.state = 'walk'
            else:
                if not self.is_jumping: self.state = 'idle'
            if keys[controls['jump']] and not self.is_jumping:
                self.jump() # To wywoła dźwięk i ustawi fizykę skoku
            if keys[controls['atk1']]: 
                self.start_attack('attack1')
            elif keys[controls['atk2']]: 
                self.start_attack('attack2')

        self.apply_gravity(platforms_list)
        self.update_hitbox()
        self.check_attack_collision(target)
        if self.hit_cooldown > 0:
            self.hit_cooldown -= 1
        self.update_animation()
class Golem(Character):
    def __init__(self, x, y):
        super().__init__(x, y, "Assets/Golem", scale=2.8, hp=200, speed=3, damage=20, width=70, height=80)
        self.image_offset_y = 0
        self.image_offset_y = 0
        self.jump_height = -10
        W, H = 90, 64
        self.animations = {
            'idle':    self.load_sheet('Golem_1_idle.png', 8, W, H),
            'walk':    self.load_sheet('Golem_1_walk.png', 10, W, H),
            'attack1': self.load_sheet('Golem_1_attack.png', 11, W, H),
            'hit':     self.load_sheet('Golem_1_hurt.png', 4, W, H),
            'death':   self.load_sheet('Golem_1_die.png', 11, W, H),
        }
        self.animations['attack2'] = self.animations['attack1']   # ta sama referencja, zero kosztu
        self.animations['jump']    = self.animations['idle']  

    def play_attack_impact_sound(self):
        """Gdy Golem kogoś trafi, usłyszymy golem_hit"""
        assets_manager.play_sound("golem_hit")
    
    def play_hit_sound(self):
        """Gdy Golem sam zostanie uderzony, usłyszymy zwykły hit"""
        assets_manager.play_sound("hit")  
    def start_attack_golem(self, type='attack1'):
        """Wywoływane, gdy Golem zaczyna machać łapą (pusty cios)"""
        if not self.is_attacking:
            assets_manager.play_sound("golem_empty_hit") # Unikalny dźwięk zamachu
            self.state = type
            self.is_attacking = True
            self.frame_index = 0    
    def update(self, target, arrows_list, controls, platforms_list, keys):
        if self.is_dead:
            self.update_animation()
            return
        
        if not self.is_attacking and self.state != 'hit':
            if keys[controls['left']]:
                self.direction = 'left'
                self.move_and_check_walls(-self.vel, platforms_list)
                if not self.is_jumping: self.state = 'walk'
            elif keys[controls['right']]:
                self.direction = 'right'
                self.move_and_check_walls(self.vel, platforms_list)
                if not self.is_jumping: self.state = 'walk'
            else:
                if not self.is_jumping: self.state = 'idle'

            if keys[controls['jump']] and not self.is_jumping:
                self.vel_y = self.jump_height
                self.is_jumping = True
                self.state = 'jump'
                self.frame_index = 0

            # --- POPRAWIONE WYWOŁANIE ATAKU ---
            if keys[controls['atk1']] or keys[controls['atk2']]:
                self.start_attack_golem('attack1')

        self.apply_gravity(platforms_list)
        self.update_hitbox()
        self.check_attack_collision(target)
        if self.hit_cooldown > 0:
            self.hit_cooldown -= 1
        self.update_animation()