# -*- coding: utf-8 -*-
import pygame
from config import SCREEN_WIDTH
HEART_FRAMES = []
# =============================================================================
# KLASA POCISKU
# =============================================================================

class Arrow(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, owner):
        super().__init__()
        self.owner = owner
        self.speed = 12
        self.image = pygame.Surface((20, 4))
        self.image.fill((200, 200, 200))
        self.rect = self.image.get_rect()
        self.active = True

        if direction == 'right':
            self.rect.left = x
            self.vel_x = self.speed
        else:
            self.rect.right = x
            self.vel_x = -self.speed

        self.rect.centery = y
        self.damage = 15

    def update(self, targets):
        self.rect.x += self.vel_x

        # Upewniamy się, że targets jest listą
        if not isinstance(targets, list):
            targets = [targets]

        for target in targets:
            # 1. Sprawdzamy czy target istnieje, nie jest właścicielem i żyje
            if target and target != self.owner and not target.is_dead:

                # 2. Pobieramy hitbox (niebieską ramkę)
                target_box = getattr(target, 'hitbox', target.rect)

                # 3. Sprawdzamy kolizję
                if self.rect.colliderect(target_box):
                    # Jeśli nie blokuje, zadaj obrażenia
                    if not target.is_blocking:
                        target.take_damage(self.damage)

                    # Strzała znika po trafieniu (nawet w blok)
                    self.active = False
                    return

        # Usuwanie poza ekranem
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.active = False


# =============================================================================
# KLASA MIKSTURY
# =============================================================================

class HealthPotion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        global HEART_FRAMES

        # Jeśli lista jest pusta, załaduj ją tylko TEN JEDEN RAZ
        if not HEART_FRAMES:
            try:
                sheet = pygame.image.load("Assets/red_heart.png").convert_alpha()
                base_w, base_h = 16, 16
                game_scale = 1.3
                num_frames = sheet.get_width() // base_w
                for i in range(num_frames):
                    rect = pygame.Rect(i * base_w, 0, base_w, base_h)
                    frame = sheet.subsurface(rect)
                    scaled = pygame.transform.scale(frame, (int(base_w*game_scale), int(base_h*game_scale)))
                    HEART_FRAMES.append(scaled)
                print("--- System: Animacja serca załadowana do pamięci RAM ---")
            except Exception as e:
                print(f"Błąd zasobów: {e}")
                # Rezerwowa klatka
                dummy = pygame.Surface((20, 20))
                dummy.fill((255, 0, 0))
                HEART_FRAMES = [dummy]

        # Teraz przypisujemy referencję do gotowej listy (bardzo szybkie!)
        self.frames = HEART_FRAMES
        self.frame_index = 0
        self.animation_speed = 0.2
        self.image = self.frames[0]
        self.rect = self.image.get_rect(topleft=(x, y))

        self.vel_y = 0
        self.gravity = 0.5
        self.heal_amount = 25

    def update(self, platforms_list, targets):
        # 1. AKTUALIZACJA ANIMACJI
        self.frame_index += self.animation_speed

        # Jeśli dojdziemy do końca paska, wracamy do początku (zaplętlenie)
        if self.frame_index >= len(self.frames):
            self.frame_index = 0

        # Ustawiamy aktualny obrazek dla Sprite'a
        self.image = self.frames[int(self.frame_index)]

        # 2. FIZYKA (Grawitacja i ruch)
        self.vel_y += self.gravity
        self.rect.y += self.vel_y

        # Kolizja z podłożem
        for platform in platforms_list:
            if self.rect.colliderect(platform):
                if self.vel_y > 0:
                    self.rect.bottom = platform.top
                    self.vel_y = 0

        # Kolizja z postaciami (leczenie)
        for target in targets:
            if target and not target.is_dead:
                target_box = getattr(target, 'hitbox', target.rect)
                if self.rect.colliderect(target_box):
                    target.current_hp = min(target.max_hp, target.current_hp + self.heal_amount)
                    return True # Mikstura zebrana
        return False