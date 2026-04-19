# DOKUMENTACJA TECHNICZNA SYSTEMU

## Moduł: assets_manager.py
```markdown
**1. Architektura**
- Moduł zarządza zasobami gry (dźwięki, w przyszłości grafiki) poprzez centralny cache w postaci słowników `SOUNDS` i `IMAGES`.
- Wykorzystuje ścieżkę bazową `ASSETS_PATH` zdefiniowaną w pliku `config.py` do budowania pełnych ścieżek do zasobów.
- Implementuje leniwe ładowanie zasobów (lazy loading) – zasoby są ładowane tylko raz, przy starcie gry, a następnie przechowywane w pamięci.
- Oddziela logikę ładowania zasobów od ich odtwarzania/użycia, co ułatwia zarządzanie pamięcią i błędami.
- Inicjalizuje mikser audio Pygame z niestandardowymi parametrami (44100 Hz, 16-bit, stereo, bufor 2048), co poprawia synchronizację dźwięku.
- Wspiera dynamiczne ustawianie głośności dla poszczególnych dźwięków oraz muzyki tła.
- Zawiera zaktualizowaną listę dźwięków z precyzyjnie skalibrowanymi poziomami głośności (np. `"hit"` z głośnością `0.3`, `"megaman"` z głośnością `0.1`).

**2. Interfejsy**
- **`load_all_assets()`**
  - **Opis**: Główna funkcja inicjalizująca, wywoływana raz na początku gry. Ładuje wszystkie zdefiniowane zasoby audio do cache'u `SOUNDS` z indywidualnie skalibrowanymi poziomami głośności.
  - **Parametry**: Brak.
  - **Zwraca**: Nic (efektem ubocznym jest wypełnienie słownika `SOUNDS`).
  - **Efekty uboczne**:
    - Inicjalizuje mikser audio Pygame z parametrami: częstotliwość 44100 Hz, 16-bit, stereo, bufor 2048 bajtów.
    - Wypisuje informacje o sukcesach/błędach ładowania do konsoli (ścieżki plików, komunikaty o błędach, poziomy głośności).
  - **Uwagi**:
    - Lista zasobów do załadowania jest zdefiniowana wewnętrznie w zmiennej `to_load`, gdzie każdy element zawiera nazwę zasobu, nazwę pliku i docelową głośność (0.0-1.0).
    - Zaktualizowane wartości głośności dla dźwięków: `"hit"` (0.3), `"golem_hit"` (0.4), `"empty_hit"` (0.6), `"golem_empty_hit"` (0.8), `"jump"` (0.1), `"landing"` (0.4), `"megaman"` (0.1).

- **`play_sound(name: str)`**
  - **Opis**: Odtwarza dźwięk o podanej nazwie z cache'u `SOUNDS`.
  - **Parametry**:
    - `name`: Klucz dźwięku w słowniku `SOUNDS` (np. `"hit"`, `"jump"`).
  - **Zwraca**: Nic.
  - **Efekty uboczne**:
    - Odtwarza dźwięk za pomocą miksera Pygame.
    - Wypisuje ostrzeżenie do konsoli, jeśli dźwięk nie istnieje.
  - **Uwagi**: Komunikat debugowy (opcjonalny) może być włączony poprzez odkomentowanie linii `print(f"DEBUG: Odtwarzam dźwięk: {name}")`.

- **`play_bg_music(filename: str, loop: int = -1, volume: float = 0.1)`**
  - **Opis**: Ładuje i odtwarza muzykę tła z pliku z możliwością ustawienia liczby powtórzeń i głośności.
  - **Parametry**:
    - `filename`: Nazwa pliku muzycznego (np. `"background.mp3"`) w katalogu `ASSETS_PATH/sound/`.
    - `loop`: Liczba powtórzeń (`-1` oznacza zapętlenie, domyślnie).
    - `volume`: Głośność muzyki (0.0-1.0, domyślnie `0.1`).
  - **Zwraca**: Nic.
  - **Efekty uboczne**:
    - Ładuje i odtwarza muzykę za pomocą `pygame.mixer.music`.
    - Ustawia głośność na podstawie przekazanego parametru.
    - Wypisuje informacje o sukcesie/błędzie do konsoli, w tym nazwę pliku i poziom głośności.

- **`stop_music()`**
  - **Opis**: Zatrzymuje odtwarzanie aktualnej muzyki tła.
  - **Parametry**: Brak.
  - **Zwraca**: Nic.
  - **Efekty uboczne**: Zatrzymuje muzykę za pomocą `pygame.mixer.music.stop()`.

**3. Logika**
- **Ładowanie zasobów**:
  - Dla każdego zasobu w liście `to_load` sprawdzana jest fizyczna obecność pliku na dysku przed próbą załadowania.
  - W przypadku błędu ładowania (np. niekompatybilny format) wypisywany jest komunikat do konsoli, ale gra kontynuuje działanie.
  - Głośność każdego dźwięku jest indywidualnie skalibrowana i zabezpieczona przed przekroczeniem zakresu 0.0-1.0 (funkcja `max(0.0, min(1.0, volume))`).
  - Mikser audio jest inicjalizowany tylko raz, przy pierwszym wywołaniu `load_all_assets()`, z parametrami poprawiającymi synchronizację dźwięku.
  - Zaktualizowane wartości głośności dla dźwięków: `"hit"` (0.3), `"golem_hit"` (0.4), `"empty_hit"` (0.6), `"golem_empty_hit"` (0.8), `"jump"` (0.1), `"landing"` (0.4), `"megaman"` (0.1).

- **Odtwarzanie dźwięków**:
  - Funkcja `play_sound` sprawdza istnienie dźwięku w cache'u przed próbą odtworzenia, co zapobiega wyjątkom.
  - Muzyka tła jest obsługiwana oddzielnie przez `pygame.mixer.music`, co pozwala na strumieniowanie dużych plików audio bez obciążania pamięci.
  - Głośność muzyki tła może być dynamicznie dostosowywana poprzez parametr `volume` w funkcji `play_bg_music`.

- **Obsługa błędów**:
  - Wszystkie operacje ładowania/odtwarzania są opakowane w bloki `try-except` z wypisywaniem błędów do konsoli.
  - Brak zasobu nie przerywa działania gry – wypisywane jest jedynie ostrzeżenie.
  - Dodatkowe komunikaty debugowe mogą być włączone dla śledzenia ładowania i odtwarzania zasobów.

**4. Modele**
- **Cache zasobów**:
  - `SOUNDS`: Słownik przechowujący załadowane dźwięki (`pygame.mixer.Sound`), gdzie kluczem jest nazwa zasobu (np. `"hit"`), a wartością obiekt dźwięku z predefiniowaną głośnością.
  - `IMAGES`: Słownik na przyszłe zasoby graficzne (obecnie pusty i niewykorzystywany).
- **Ścieżki zasobów**:
  - Pełne ścieżki do plików są budowane dynamicznie na podstawie `ASSETS_PATH` i podkatalogów (`sound/`).
  - Sprawdzanie istnienia plików odbywa się przed próbą ich załadowania, co minimalizuje ryzyko wystąpienia błędów.
- **Konfiguracja audio**:
  - Mikser audio Pygame jest inicjalizowany z parametrami: 44100 Hz, 16-bit, stereo, bufor 2048 bajtów, co zapewnia lepszą synchronizację dźwięku.
  - Głośność dźwięków i muzyki jest skalowalna w zakresie 0.0-1.0, z zabezpieczeniem przed przekroczeniem tego zakresu.
  - Zaktualizowane wartości głośności dla poszczególnych dźwięków (np. `"hit"`: 0.3, `"megaman"`: 0.1).
```

---

## Moduł: characters.py
### 1. Architektura
- **Bazowa klasa `Character`**: Abstrakcyjna klasa dziedzicząca po `pygame.sprite.Sprite`, definiująca wspólne właściwości i metody dla wszystkich postaci w grze. Zawiera logikę animacji, fizyki, ataków, sterowania CPU oraz zarządzania stanem postaci.
- **Dziedziczenie**: Klasy konkretnych postaci (`Soldier`, `Orc`, `HumanSoldier`, `Golem`) dziedziczą po `Character`, implementując specyficzne animacje, dźwięki, logikę ataków i właściwości (np. punkty życia, obrażenia, możliwość strzelania).
- **Modularność**:
  - Oddzielenie logiki animacji (`update_animation`), fizyki (`apply_gravity`, `move_and_check_walls`), ataków (`check_attack_collision`, `start_attack`, `start_attack_golem`), sterowania CPU (`update_cpu`, `apply_cpu_controls`) i zarządzania stanem od konkretnych implementacji postaci.
  - Wspólne metody dla wszystkich postaci, z możliwością nadpisania (np. `play_hit_sound`, `play_attack_impact_sound`, `start_attack` w `Golem`).
  - Metoda `screen_wrap()` do obsługi przechodzenia postaci przez krawędzie ekranu.
- **Zarządzanie zasobami**:
  - Wykorzystanie `assets_manager` do ładowania dźwięków (np. `play_sound("hit")`, `play_sound("golem_hit")`, `play_sound("golem_empty_hit")`).
  - Centralizacja ładowania grafik poprzez metodę `load_sheet`, która obsługuje sprite sheety i skalowanie, zwracając klatki dla obu kierunków (prawego i lewego).
  - Obsługa fallback dla sprite sheetów w przypadku błędu ładowania (czerwony prostokąt).
- **Nowe elementy**:
  - Obsługa przesunięcia grafiki (`image_offset_y`) dla lepszego dopasowania sprite'ów do hitboxów.
  - Wsparcie dla różnych rozmiarów sprite'ów (np. `W, H = 96, 96` dla `HumanSoldier` i `90, 64` dla `Golem`).
  - Dodanie parametru `difficulty` w logice CPU, wpływającego na agresywność i reakcje przeciwnika.
  - **Nowość**: Metoda `update_hitbox()` z przesunięciem hitboxa w górę o 5 pikseli dla lepszej precyzji kolizji.
  - **Nowość**: Metoda `jump()` zintegrowana z odtwarzaniem dźwięku skoku.

---

### 2. Interfejsy
#### Klasa `Character`
- **Konstruktor (`__init__`)**:
  - Parametry:
    - `x`, `y`: Pozycja startowa postaci.
    - `folder`: Ścieżka do katalogu z zasobami graficznymi postaci.
    - `scale`: Skala grafiki (domyślnie `2.5`).
    - `hp`: Maksymalne punkty życia (domyślnie `100`).
    - `speed`: Prędkość poruszania się (domyślnie `5`).
    - `damage`: Obrażenia zadawane przez postać (domyślnie `10`).
    - `width`, `height`: Wymiary hitboxa (domyślnie `40x60`).
  - Inicjalizuje:
    - Podstawowe właściwości (animacje, stan, kierunek, flagi stanu: `is_attacking`, `is_blocking`, `is_dead`, `is_jumping`).
    - Hitboxy (`rect` i `hitbox`).
    - Właściwości fizyki (grawitacja, skok, prędkość pionowa).
    - Timer akcji CPU (`cpu_action_timer`, `cpu_current_action`).
    - Offset grafiki (`image_offset_y`).
    - Flagi: `can_shoot` (domyślnie `False`), `arrow_shot` (dla `Soldier`).
    - Właściwość `difficulty` (domyślnie `1.0`) wpływająca na logikę CPU.

- **Metody publiczne**:
  - `load_sheet(filename, frame_count, width, height)`:
    - Ładuje sprite sheet z pliku i zwraca dwie listy klatek animacji: dla prawej (`frames_right`) i lewej (`frames_left`) strony.
    - Obsługuje skalowanie klatek (`pygame.transform.scale`) i zwraca fallback (czerwony prostokąt) w przypadku błędu.
    - Wsparcie dla różnych rozmiarów sprite'ów (np. `96x96` dla `HumanSoldier`).
  - `draw_hp_bar(surface, x, y, width=200, height=20, align_right=False)`:
    - Rysuje pasek życia na podanej powierzchni (`surface`).
    - Parametry:
      - `align_right`: Wyrównanie paska do prawej krawędzi (używane dla P2).
    - Składa się z trzech części: tło (ciemnoczerwone), zdrowie (jasnozielone), ramka (biała).
  - `update_hitbox()`: Aktualizuje pozycję `hitbox` na podstawie `rect`, z niewielkim przesunięciem w górę (`-5` pikseli) dla lepszej precyzji kolizji.
  - `play_hit_sound()`: Odtwarza dźwięk trafienia (domyślnie `"hit"`; nadpisywane w klasach dziedziczących, np. `Golem`).
  - `play_attack_impact_sound()`: Odtwarza dźwięk trafienia przeciwnika (domyślnie `"hit"`; nadpisywane w `Golem` na `"golem_hit"`).
  - `take_damage(amount)`:
    - Zadaje obrażenia postaci i aktualizuje jej stan.
    - Ignoruje obrażenia, jeśli postać jest martwa (`is_dead`) lub blokuje (`is_blocking`).
    - Ustawia stan na `death` lub `hit` w zależności od pozostałych punktów życia (`current_hp`).
    - Resetuje `frame_index` do `0`.
  - `update_animation()`:
    - Aktualizuje animację postaci na podstawie jej stanu (`state`), kierunku (`direction`) i flag (`is_attacking`, `is_blocking`, `is_dead`).
    - Obsługuje różne prędkości animacji (szybsza dla ataków i trafień: `anim_speed = 0.25`; wolniejsza dla innych stanów: `0.18`).
    - Resetuje `is_attacking` i `state` do `idle` po zakończeniu animacji ataku/trafienia.
  - `apply_gravity(platforms_list)`:
    - Aplikuje grawitację do prędkości pionowej (`vel_y`).
    - Obsługuje kolizje z platformami (lądowanie na platformie, uderzenie głową w sufit).
  - `start_attack(type='attack1')`:
    - Rozpoczyna atak określonego typu (np. `'attack1'`, `'attack2'`).
    - Odtwarza dźwięk pustego ciosu (`"empty_hit"`; nadpisywany w klasach dziedziczących, np. `Golem`).
    - Ustawia flagę `is_attacking` i resetuje `frame_index`.
  - `jump()`:
    - Inicjuje skok postaci, ustawiając `vel_y` na `jump_height` i flagę `is_jumping` na `True`.
    - Odtwarza dźwięk skoku (`"jump"`).
    - Ustawia stan na `'jump'` i resetuje `frame_index`.
  - `move_and_check_walls(dx, platforms_list)`:
    - Przesuwa postać w poziomie o `dx` i obsługuje kolizje ze ścianami (platformami).
  - `check_attack_collision(target)`:
    - Sprawdza kolizję ataku z celem (lub listą celów).
    - Zadaje obrażenia, jeśli atak trafia w hitbox celu i cel nie jest w trakcie odnowienia (`hit_cooldown == 0`).
    - Obsługuje różne typy ataków (`attack1`, `attack2`) i ich ramy czasowe (klatki `2-5`).
    - Wywołuje `play_attack_impact_sound()` atakującego (nie ofiary).
    - Obsługa listy celów (`targets_to_check`).
  - `screen_wrap()`: Obsługuje przechodzenie postaci przez krawędzie ekranu (teleportacja na przeciwną stronę).
  - `update_cpu(target, arrows_list, platforms_list)`:
    - Logika sterowania postacią przez CPU.
    - Podejmuje decyzje na podstawie:
      - Odległości od celu (`distance`).
      - Zagrożeń (strzały w zasięgu `200 * difficulty`).
      - Losowości (`random.random()`).
      - Trudności (`difficulty`, domyślnie `1.0`).
    - Ustawia akcje CPU (ruch, skok, atak, blok) i przekazuje je do `apply_cpu_controls`.
    - Martwa strefa (deadzone) dla bliskiego dystansu (`distance < 20`), gdzie CPU przestaje biegać i atakuje (`atk1`).
    - Optymalizacja dystansu w zależności od `can_shoot` (dla `Soldier` dystans `200-400`, dla pozostałych `30-65`).
  - `apply_cpu_controls(keys, target, arrows_list, platforms_list)`:
    - Aplikuje sterowanie CPU na podstawie przekazanych klawiszy (`keys`).
    - Priorytetyzuje akcje: blok > atak > ruch.
    - Obsługuje fizykę, kolizje, odnowienie (`hit_cooldown`) i aktualizację animacji.
    - Odtwarza dźwięki pustego ciosu na początku ataków (`"empty_hit"` lub `"golem_empty_hit"`).

#### Klasy dziedziczące (`Soldier`, `Orc`, `HumanSoldier`, `Golem`)
- **Konstruktory**:
  - Inicjalizują specyficzne dla postaci:
    - Animacje (za pomocą `load_sheet`).
    - Punkty życia (`hp`), prędkość (`speed`), obrażenia (`damage`).
    - Offset grafiki (`image_offset_y`).
    - Właściwości specjalne (np. `can_shoot = True` dla `Soldier`).
    - Wymiary sprite'ów (np. `W, H = 96, 96` dla `HumanSoldier` i `90, 64` dla `Golem`).
- **Metody nadpisane**:
  - `play_hit_sound()`: `Golem` odtwarza unikalny dźwięk (`"golem_hit"`).
  - `play_attack_impact_sound()`: `Golem` odtwarza unikalny dźwięk trafienia (`"golem_hit"`).
  - `start_attack(type)`: `Golem` używa `start_attack_golem`, która odtwarza unikalny dźwięk zamachu (`"golem_empty_hit"`).
- **Metoda `update(target, arrows_list, controls, platforms_list, keys)`**:
  - Parametry:
    - `target`: Cel ataku (postać lub lista postaci).
    - `arrows_list`: Lista aktywnych strzał (dla `Soldier`).
    - `controls`: Słownik mapujący akcje na klawisze (np. `{'left': pygame.K_a, 'atk1': pygame.K_j}`).
    - `platforms_list`: Lista platform do obsługi kolizji.
    - `keys`: Stan klawiszy (zastępuje `pygame.key.get_pressed()`).
  - Logika:
    - Obsługa sterowania użytkownika (ruch, skok, atak, blok).
    - Specyficzna logika dla `Soldier` (strzelanie z łuku w klatce `6` animacji `bow`).
    - Aplikacja grawitacji, aktualizacja hitboxa, sprawdzanie kolizji ataków, odnowienie (`hit_cooldown`), aktualizacja animacji.
    - `Soldier`: Wystrzeliwuje strzałę (`Arrow`) w klatce `6` animacji `bow` z precyzyjnym pozycjonowaniem (`arrow_height = self.hitbox.bottom - 11`).
    - `Orc` i `HumanSoldier`: Obsługują blokowanie (`is_blocking` ustawiane przez `keys['block']` lub CPU).
    - `Golem`: Używa `start_attack_golem` dla ataków i nie może skakać (animacja `jump` używa `idle`).

---

### 3. Logika
#### Fizyka i Kolizje
- **Grawitacja i skoki**:
  - Postacie podlegają grawitacji (`gravity = 0.8`), która zwiększa prędkość pionową (`vel_y`).
  - Skok inicjowany przez metodę `jump()`, która ustawia `vel_y` na `jump_height = -16` i flagę `is_jumping = True`, odtwarza dźwięk skoku i ustawia stan na `'jump'`.
- **Kolizje z platformami**:
  - **Pionowe**: Metoda `apply_gravity` obsługuje lądowanie (kolizja od góry) i uderzenie głową w sufit (kolizja od dołu).
  - **Poziome**: Metoda `move_and_check_walls` obsługuje kolizje ze ścianami (platformami) podczas ruchu w poziomie.
- **Hitboxy**:
  - Każda postać ma dwa prostokąty:
    - `rect`: Do rysowania grafiki (pozycja i wymiary).
    - `hitbox`: Do kolizji (aktualizowany przez `update_hitbox` z przesunięciem w górę o 5 pikseli dla lepszej precyzji).
  - Kolizje ataków sprawdzane są na podstawie `hitbox` celu.
- **Przechodzenie przez krawędzie ekranu**:
  - Metoda `screen_wrap()` umożliwia postaci przechodzenie przez lewą/prawą krawędź ekranu, pojawiając się po przeciwnej stronie.

#### Ataki i Obrażenia
- **Ataki**:
  - Postacie mogą wykonywać różne typy ataków (`attack1`, `attack2`, `bow` dla `Soldier`).
  - Ataki inicjowane przez `start_attack`, `start_attack_golem` (dla `Golem`) lub bezpośrednio w metodzie `update`.
  - Dźwięk pustego ciosu odtwarzany na początku ataku (nadpisywany w `Golem`).
- **Kolizje ataków**:
  - Metoda `check_attack_collision` sprawdza, czy atak trafia w cel, używając prostokąta ataku (`attack_rect`).
  - Obrażenia zadawane tylko w określonych klatkach animacji (np. `2-5` dla `attack1` i `attack2`).
  - Cel otrzymuje obrażenia, jeśli nie jest martwy, nie blokuje i nie jest w trakcie odnowienia (`hit_cooldown`).
  - Wywołuje `play_attack_impact_sound()` atakującego (nie ofiary).
  - Obsługa listy celów (`targets_to_check`).
- **Obrażenia**:
  - Metoda `take_damage` redukuje `current_hp` i aktualizuje stan postaci:
    - `death`, jeśli `current_hp <= 0`.
    - `hit`, jeśli postać przeżyła.
  - Ignoruje obrażenia, jeśli postać blokuje (`is_blocking`) lub jest martwa (`is_dead`).
  - Odtwarza dźwięk trafienia (nadpisywany w `Golem`).

#### Sterowanie CPU
- **Logika decyzji**:
  - Metoda `update_cpu` implementuje logikę podejmowania decyzji przez CPU na podstawie:
    - Odległości od celu (`distance`).
    - Zagrożeń (strzały w zasięgu `200 * difficulty`).
    - Losowości (`random.random()`).
    - Trudności (`difficulty`, domyślnie `1.0`).
  - **Reakcje na zagrożenia**:
    - CPU blokuje (`block`), jeśli strzała jest w zasięgu i losowość na to pozwala.
  - **Ruch i ataki**:
    - CPU porusza się w stronę celu, utrzymując optymalny dystans (zależny od `can_shoot`):
      - `Soldier` (`can_shoot = True`): Optymalny dystans `200-400`.
      - Pozostałe postacie: Optymalny dystans `30-65`.
    - Atakuje, jeśli cel jest w zasięgu (`distance <= 75` dla ataków wręcz, `distance > 220` dla strzałów).
    - Losowo wybiera między `attack1` i `attack2`.
    - Martwa strefa (deadzone) dla bliskiego dystansu (`distance < 20`), gdzie CPU przestaje biegać i atakuje (`atk1`).
  - **Timer akcji**:
    - CPU może wykonywać długie akcje (np. strzelanie z łuku) przez określony czas (`cpu_action_timer = 40` dla `special`).
- **Aplikacja sterowania**:
  - Metoda `apply_cpu_controls` aplikuje decyzje CPU, priorytetyzując:
    1. Blok (jeśli `keys['block']` i nie skacze).
    2. Atak (jeśli `is_attacking`).
    3. Ruch i reszta akcji (skok, ruch w lewo/prawo, specjalne ataki).
  - Obsługuje fizykę, kolizje, odnowienie (`hit_cooldown`) i aktualizację animacji.
  - Odtwarza dźwięki pustego ciosu na początku ataków (`"empty_hit"` lub `"golem_empty_hit"`).

#### Animacje
- **Stany animacji**:
  - Postacie mają różne stany (`idle`, `walk`, `jump`, `attack1`, `attack2`, `bow`, `hit`, `death`, `block`), które determinują aktualnie odtwarzaną animację.
  - Animacje są ładowane z sprite sheetów i przechowywane w słowniku `animations` jako dwie listy klatek (dla prawej i lewej strony).
- **Aktualizacja animacji**:
  - Metoda `update_animation` aktualizuje `frame_index` na podstawie:
    - Stanu postaci (`state`).
    - Kierunku (`direction`).
    - Flag (`is_attacking`, `is_blocking`, `is_dead`).
  - Prędkość animacji zależy od stanu (szybsza dla ataków i trafień: `anim_speed = 0.25`; wolniejsza dla innych stanów: `0.18`).
  - Po zakończeniu animacji ataku/trafienia resetuje `is_attacking` i `state` do `idle`.

#### Specjalne mechaniki
- **Strzelanie z łuku (`Soldier`)**:
  - Inicjowane przez `keys['special']` lub logikę CPU.
  - Strzała (`Arrow`) jest tworzona w klatce `6` animacji `bow` z precyzyjnym pozycjonowaniem (`arrow_height = self.hitbox.bottom - 11`).
  - Strzała ma własną logikę ruchu i kolizji (zdefiniowaną w klasie `Arrow` w `items.py`).
- **Blokowanie (`Orc`, `HumanSoldier`)**:
  - Inicjowane przez `keys['block']` lub logikę CPU.
  - Postać wchodzi w stan `block` i ignoruje obrażenia (`take_damage` sprawdza `is_blocking`).
- **Unikalne dźwięki (`Golem`)**:
  - Nadpisuje `play_hit_sound` i `play_attack_impact_sound` dla unikalnych dźwięków (`"golem_hit"`).
  - Nadpisuje `start_attack` jako `start_attack_golem` dla unikalnego dźwięku zamachu (`"golem_empty_hit"`).
- **Martwa strefa (Deadzone) w logice CPU**:
  - Jeśli CPU jest bardzo blisko celu (`distance < 20`), przestaje biegać i atakuje (`atk1`).

---

### 4. Modele
#### Klasa `Character`
- **Właściwości**:
  - **Animacje**:
    - `animations`: Słownik mapujący stany (`idle`, `walk`, itp.) na listy klatek animacji dla prawej i lewej strony.
  - **Stan**:
    - `state`: Aktualny stan postaci (np. `'idle'`, `'attack1'`).
    - `frame_index`: Indeks aktualnej klatki animacji.
    - `direction`: Kierunek postaci (`'left'` lub `'right'`).
    - `is_attacking`, `is_blocking`, `is_dead`, `is_jumping`: Flagi określające stan postaci.
    - `hit_cooldown`: Licznik odnowienia po otrzymaniu obrażeń (uniemożliwia wielokrotne trafienia w krótkim czasie).
  - **Fizyka**:
    - `rect`: Prostokąt do rysowania grafiki (pozycja i wymiary).
    - `hitbox`: Prostokąt do kolizji (aktualizowany przez `update_hitbox` z przesunięciem w górę o 5 pikseli).
    - `vel_y`: Prędkość pionowa (do obsługi grawitacji i skoków).
    - `gravity`: Wartość grawitacji (`0.8`).
    - `jump_height`: Wysokość skoku (`-16`).
  - **Statystyki**:
    - `max_hp`, `current_hp`: Maksymalne i aktualne punkty życia.
    - `vel`: Prędkość poruszania się.
    - `damage`: Obrażenia zadawane przez postać.
  - **Sterowanie CPU**:
    - `cpu_action_timer`: Licznik trwania aktualnej akcji CPU.
    - `cpu_current_action`: Aktualna akcja CPU (np. `'special'` dla strzelania).
    - `difficulty`: Współczynnik trudności (domyślnie `1.0`), wpływający na agresywność i reakcje CPU.
  - **Inne**:
    - `can_shoot`: Flaga określająca, czy postać może strzelać (domyślnie `False`; `True` dla `Soldier`).
    - `image_offset_y`: Przesunięcie grafiki w pionie (dla dopasowania sprite'ów do hitboxa).

#### Klasy dziedziczące
- **`Soldier`**:
  - **Właściwości**:
    - `can_shoot = True`: Może strzelać z łuku.
    - `arrow_shot`: Flaga określająca, czy strzała została już wystrzelona w aktualnej animacji `bow`.
  - **Animacje**:
    - Specyficzne dla łuku (`bow`).
  - **Logika**:
    - Wystrzeliwuje strzałę w klatce `6` animacji `bow` z precyzyjnym pozycjonowaniem (`arrow_height = self.hitbox.bottom - 11`).
- **`Orc`**:
  - **Właściwości**:
    - Wyższe obrażenia (`damage = 14`).
  - **Animacje**:
    - Animacja blokowania (`block`).
  - **Logika**:
    - Może blokować ataki (`is_blocking` ustawiane przez `keys['block']` lub CPU).
- **`HumanSoldier`**:
  - **Właściwości**:
    - Zrównoważone statystyki (`hp = 100`, `damage = 11`, `speed = 6`).
    - Wymiary sprite'ów (`96x96`).
  - **Animacje**:
    - Animacja blokowania (`block`).
  - **Logika**:
    - Może blokować ataki (`is_blocking` ustawiane przez `keys['block']` lub CPU).
- **`Golem`**:
  - **Właściwości**:
    - Wysokie punkty życia (`hp = 200`) i obrażenia (`damage = 20`), ale niska prędkość (`speed = 3`).
    - Większy hitbox (`width = 70`, `height = 80`).
    - Skala grafiki (`scale = 2.8`).
    - Wymiary sprite'ów (`90x64`).
    - Niższa wysokość skoku (`jump_height = -10`).
  - **Animacje**:
    - Brak animacji skoku (`jump` używa animacji `idle`).
    - `attack2` używa tej samej animacji co `attack1`.
  - **Metody nadpisane**:
    - `play_hit_sound()`: Odtwarza `"golem_hit"`.
    - `play_attack_impact_sound()`: Odtwarza `"golem_hit"`.
    - `start_attack_golem(type)`: Odtwarza `"golem_empty_hit"` i inicjuje atak.
  - **Logika**:
    - Używa tej samej animacji dla `attack1` i `attack2`.
    - Nie może skakać (animacja `jump` używa `idle`).

---

---

## Moduł: config.py
**1. Architektura**
Plik `config.py` stanowi centralny punkt konfiguracyjny aplikacji, definiujący stałe, ścieżki zasobów, parametry mechaniki gry oraz ustawienia interfejsu. Jego struktura opiera się na podejściu modularnym, gdzie każda sekcja odpowiada za określony aspekt gry, zapewniając spójność i łatwość zarządzania konfiguracją. Plik wykorzystuje moduły `pygame` (do obsługi grafiki i sterowania) oraz `pathlib` (do zarządzania ścieżkami systemowymi), co gwarantuje przenośność i elastyczność w różnych środowiskach uruchomieniowych.

Kluczowe sekcje:
- **Stany gry**: Definicje stałych reprezentujących stany interfejsu (menu, wybór postaci, wybór poziomu trudności, wybór mapy, ustawienia, rozgrywka).
- **Ustawienia ekranu**: Parametry wyświetlania (rozdzielczość, FPS, skalowanie kafelków, rozmiar cache'u).
- **Mechanika gry**: Wartości wpływające na rozgrywkę (statystyki postaci, poziomy trudności, kolizje, mechaniki przedmiotów, współczynniki trudności).
- **Ścieżki zasobów**: Dynamiczne generowanie ścieżek do plików graficznych i dźwiękowych z uwzględnieniem struktury katalogów.
- **Sterowanie**: Domyślne mapowania klawiszy dla dwóch graczy, umożliwiające personalizację kontrolek.
- **Interfejs użytkownika**: Kolory, czcionki oraz mapy znaków dla niestandardowych czcionek, w tym obsługa polskich znaków diakrytycznych.
- **Debugowanie**: Komunikaty debugowania (`print`) weryfikujące poprawność ścieżek zasobów.

---

**2. Interfejsy**
Plik udostępnia stałe i struktury danych do wykorzystania przez inne moduły gry, zapewniając jednolity dostęp do konfiguracji:

- **Stałe globalne**:
  - Stany gry: `STATE_MENU`, `STATE_CHAR_SELECT`, `STATE_MAP_SELECT`, `STATE_SETTINGS`, `STATE_PLAYING`, `STATE_DIFF_SELECT` (stan wyboru poziomu trudności).
  - Wymiary ekranu: `SCREEN_WIDTH`, `SCREEN_HEIGHT`, `FPS`, `MAX_CACHE_SIZE`.
  - Skalowanie: `TILE_SCALE`, `TILE_SIZE_ORIGINAL`, `TILE_SIZE`.
  - Kolory: `COLOR_BG`, `COLOR_TEXT`, `COLOR_GOLD`.
  - Poziomy trudności: `DIFFICULTY_EASY`, `DIFFICULTY_NORMAL`, `DIFFICULTY_HARD`, `DIFFICULTY_LABELS`, `DIFFICULTY_VALUES`.
  - Mechanika przedmiotów: `POTION_SPAWN_COOLDOWN`.

- **Słowniki i listy**:
  - `CHAR_STATS`: Statystyki postaci (HP, prędkość, obrażenia, możliwość strzelania). Zawiera postacie: "Soldier", "Orc", "Knight", "Golem" z unikalnymi wartościami.
  - `CHAR_DESCRIPTIONS`: Opisy postaci (wykorzystywane w menu wyboru), zawierające krótkie informacje o umiejętnościach i charakterystyce.
  - `COLLISION_TILES`: Identyfikatory kafelków, z którymi występują kolizje (rozszerzona lista: `[0, 1, 2, 13, 15, 34, 35, 36, 64, 65, 66]`).
  - `DEFAULT_P1_CONTROLS`, `DEFAULT_P2_CONTROLS`: Domyślne ustawienia sterowania (klawisze ruchu, ataku, blokowania, umiejętności specjalnych).
  - `FONT_CHARS_MAP`: Mapa znaków dla niestandardowej czcionki, uwzględniająca polskie znaki diakrytyczne (małe i wielkie litery, cyfry, znaki interpunkcyjne).

- **Ścieżki zasobów**:
  - `BASE_PATH`, `ASSETS_PATH`, `TILES_PATH`, `BG_PATH`: Ścieżki do katalogów z zasobami (obliczane względem lokalizacji pliku `config.py`), z weryfikacją poprzez komunikaty debugowania (`print`).

---

**3. Logika**
- **Dynamiczne ścieżki**:
  - Ścieżki do zasobów są obliczane na podstawie lokalizacji pliku `config.py` (nie katalogu uruchomienia), co zapewnia poprawne działanie niezależnie od środowiska.
  - Weryfikacja ścieżek odbywa się poprzez komunikaty debugowania (`print`), wyświetlające aktualny katalog roboczy i ścieżkę do zasobów.
- **Skalowanie kafelków**:
  - Rozmiar kafelków (`TILE_SIZE`) jest obliczany na podstawie oryginalnego rozmiaru (`TILE_SIZE_ORIGINAL`) i współczynnika skalowania (`TILE_SCALE`), co umożliwia elastyczne dostosowanie rozdzielczości gry.
- **Poziomy trudności**:
  - Stan gry `STATE_DIFF_SELECT` umożliwia wybór poziomu trudności przed rozpoczęciem rozgrywki.
  - Wartości trudności (`DIFFICULTY_VALUES`) są powiązane z etykietami (`DIFFICULTY_LABELS`) w celu wyświetlania przyjaznych nazw w interfejsie.
  - Wartości te wpływają na mechaniki gry, takie jak:
    - Modyfikatory obrażeń zadawanych przez przeciwników (np. `DIFFICULTY_HARD` zwiększa obrażenia o 50%).
    - Modyfikatory punktów życia przeciwników (np. `DIFFICULTY_HARD` zwiększa HP przeciwników o 50%).
    - Częstotliwość pojawiania się przeciwników lub przedmiotów.
- **Mechanika kolizji**:
  - Lista `COLLISION_TILES` definiuje kafelki, z którymi postacie nie mogą wchodzić w interakcję (np. ściany, przeszkody, pułapki).
- **Mechanika przedmiotów**:
  - Stała `POTION_SPAWN_COOLDOWN` określa czas odradzania się mikstur w grze (400 klatek, co odpowiada ~8 sekundom przy 50 FPS).
- **Cache**:
  - Stała `MAX_CACHE_SIZE` definiuje maksymalną liczbę elementów przechowywanych w cache'u (200), optymalizując wydajność gry.
- **Sterowanie**:
  - Domyślne mapowania klawiszy dla dwóch graczy (`DEFAULT_P1_CONTROLS`, `DEFAULT_P2_CONTROLS`) obejmują:
    - Ruch (lewo/prawo/skok).
    - Ataki podstawowe (`atk1`) i specjalne (`atk2`).
    - Blokowanie ciosów (`block`).
    - Umiejętności specjalne (`special`).

---

**4. Modele**
- **Postacie**:
  - Każda postać jest reprezentowana przez klucz w słownikach `CHAR_STATS` oraz `CHAR_DESCRIPTIONS`. Statystyki obejmują:
    - `damage`: Obrażenia zadawane przez postać.
    - `max_hp`: Maksymalna ilość punktów życia.
    - `vel`: Prędkość poruszania się.
    - `can_shoot`: Flaga określająca, czy postać może atakować na odległość.
  - Opisy postaci (`CHAR_DESCRIPTIONS`) zawierają krótkie informacje o umiejętnościach i charakterystyce.
  - Postacie i ich statystyki:
    - **Soldier**: Wysokie obrażenia (`damage: 12`), niska odporność (`max_hp: 80`), wysoka prędkość (`vel: 6`), możliwość strzelania (`can_shoot: True`).
    - **Orc**: Wysokie obrażenia (`damage: 14`), średnia odporność (`max_hp: 90`), średnia prędkość (`vel: 5`), brak możliwości strzelania (`can_shoot: False`).
    - **Knight**: Zbalansowane obrażenia (`damage: 11`), wysoka odporność (`max_hp: 100`), wysoka prędkość (`vel: 6`), brak możliwości strzelania (`can_shoot: False`).
    - **Golem**: Bardzo wysokie obrażenia (`damage: 20`), bardzo wysoka odporność (`max_hp: 200`), niska prędkość (`vel: 3`), brak możliwości strzelania (`can_shoot: False`).

- **Poziomy trudności**:
  - Wartości trudności (`DIFFICULTY_EASY = 0.6`, `DIFFICULTY_NORMAL = 1.0`, `DIFFICULTY_HARD = 1.5`) są mnożnikami wpływającymi na:
    - Punkty życia przeciwników.
    - Obrażenia zadawane przez przeciwników.
    - Częstotliwość spawnowania przeciwników lub przedmiotów.
  - Etykiety poziomów trudności (`DIFFICULTY_LABELS = ["ŁATWY", "NORMALNY", "TRUDNY"]`) są wyświetlane w interfejsie użytkownika.

- **Kafelki**:
  - Identyfikatory w `COLLISION_TILES` odpowiadają konkretnym typom kafelków w plikach graficznych (np. kafelki ścian, podłóg, przeszkód).

- **Przedmioty**:
  - Mikstury (reprezentowane przez `POTION_SPAWN_COOLDOWN`) odradzają się po określonym czasie (~8 sekund przy 50 FPS), przywracając punkty życia postaci.

- **Interfejs użytkownika**:
  - Kolory (`COLOR_BG`, `COLOR_TEXT`, `COLOR_GOLD`) są wykorzystywane do spójnego stylizowania elementów interfejsu.
  - Mapa znaków (`FONT_CHARS_MAP`) umożliwia renderowanie niestandardowych czcionek z obsługą polskich znaków diakrytycznych.

---

---

## Moduł: items.py
```markdown
1. **Architektura**
   - Plik `items.py` zawiera implementacje klas reprezentujących obiekty interaktywne w grze: pociski (`Arrow`) oraz mikstury zdrowia (`HealthPotion`).
   - Obie klasy dziedziczą po `pygame.sprite.Sprite`, co umożliwia zarządzanie nimi w grupach sprite'ów oraz obsługę kolizji.
   - Wykorzystuje globalną listę `HEART_FRAMES` do przechowywania klatek animacji serca (mikstury), co optymalizuje wydajność poprzez ładowanie zasobów tylko raz podczas pierwszego utworzenia instancji `HealthPotion`.
   - Klasa `Arrow` obsługuje kolizje z wieloma celami, przyjmując listę lub pojedynczy obiekt jako parametr `targets` w metodzie `update`.
   - Klasa `HealthPotion` implementuje animację zapętloną oraz fizykę grawitacji dla realistycznego spadania i interakcji z platformami.
   - Dodano obsługę hitboxów (`hitbox`) dla celów, co pozwala na precyzyjniejsze wykrywanie kolizji niż przy użyciu domyślnego `rect`.
   - Klasa `HealthPotion` wykorzystuje mechanizm ładowania sprite sheet (`Assets/red_heart.png`) z automatycznym skalowaniem klatek (`game_scale = 1.3`).

2. **Interfejsy**
   - **Arrow**:
     - Konstruktor: `__init__(self, x, y, direction, owner)`
       - `x`, `y`: współrzędne startowe pocisku.
       - `direction`: kierunek lotu (`'right'` dla prawej strony, w przeciwnym razie lewa).
       - `owner`: referencja do obiektu, który wystrzelił pocisk (np. gracz lub przeciwnik), używana do uniknięcia samouszkodzenia.
     - Metoda: `update(self, targets)`
       - Aktualizuje pozycję pocisku i obsługuje kolizje z celami.
       - `targets`: lista lub pojedynczy obiekt, z którym pocisk może kolidować. Jeśli `targets` nie jest listą, jest konwertowany na listę jednoparametrową.
       - Ustawia `self.active = False` po trafieniu celu (nawet jeśli cel blokuje atak) lub wyjściu poza ekran (`SCREEN_WIDTH`).
   - **HealthPotion**:
     - Konstruktor: `__init__(self, x, y)`
       - `x`, `y`: współrzędne startowe mikstury.
     - Metoda: `update(self, platforms_list, targets)`
       - Aktualizuje animację, fizykę (grawitację) oraz obsługuje kolizje z platformami i celami.
       - `platforms_list`: lista obiektów platform, z którymi mikstura może kolidować (zatrzymuje się na nich).
       - `targets`: lista lub pojedynczy obiekt, który może zebrać miksturę.
       - Zwraca `True`, jeśli mikstura została zebrana przez cel (leczenie o `self.heal_amount`), w przeciwnym razie `False`.

3. **Logika**
   - **Arrow**:
     - Pocisk porusza się poziomo z określoną prędkością (`self.speed = 12` pikseli na klatkę).
     - Zadaje obrażenia (`self.damage = 15`) celowi po kolizji, jeśli cel nie blokuje ataku (`not target.is_blocking`).
     - Pocisk jest oznaczany jako nieaktywny (`self.active = False`) po trafieniu celu (nawet jeśli cel blokuje) lub wyjściu poza ekran (`SCREEN_WIDTH`).
     - Kolizje są sprawdzane z użyciem hitboxów celów (jeśli dostępne, poprzez `getattr(target, 'hitbox', target.rect)`) lub ich prostokątów (`rect`).
     - Właściciel pocisku (`owner`) jest wykluczany z kolizji, aby uniknąć samouszkodzenia.
     - Sprawdzanie stanu celu (`not target.is_dead`) przed próbą zadania obrażeń.
   - **HealthPotion**:
     - Animacja serca jest zapętlona i odtwarzana z prędkością `self.animation_speed = 0.2`. Aktualna klatka jest wybierana na podstawie `self.frame_index`.
     - Mikstura podlega grawitacji (`self.gravity = 0.5`) i zatrzymuje się na platformach, gdy `self.vel_y > 0` (spada w dół).
     - Leczy cel o `self.heal_amount = 25` punktów zdrowia, nie przekraczając maksymalnego zdrowia celu (`target.max_hp`).
     - Mikstura jest usuwana po zebraniu przez cel (metoda `update` zwraca `True`).
     - Obsługa błędów ładowania zasobów: w przypadku niepowodzenia załadowania animacji serca, używana jest rezerwowa klatka (czerwony prostokąt).
     - Sprawdzanie stanu celu (`not target.is_dead`) przed próbą leczenia.
     - Mechanizm ładowania sprite sheet uwzględnia skalowanie klatek (`game_scale = 1.3`) oraz liczbę klatek na podstawie szerokości sprite sheet (`num_frames = sheet.get_width() // base_w`).

4. **Modele**
   - **Arrow**:
     - `owner`: Referencja do obiektu wystrzeliwującego pocisk (np. gracz lub przeciwnik), używana do uniknięcia samouszkodzenia.
     - `speed`: Stała prędkość pocisku (12 pikseli na klatkę).
     - `image`: Powierzchnia `pygame.Surface` reprezentująca grafikę pocisku (szary prostokąt o wymiarach 20x4 piksele).
     - `rect`: Prostokąt `pygame.Rect` określający pozycję i rozmiar pocisku.
     - `active`: Flaga logiczna określająca, czy pocisk jest aktywny (nie został zniszczony). Używana do zarządzania cyklem życia pocisku.
     - `vel_x`: Prędkość pozioma pocisku (zależna od kierunku: `self.speed` dla prawej, `-self.speed` dla lewej).
     - `damage`: Ilość obrażeń zadawanych przez pocisk (15 punktów zdrowia).
   - **HealthPotion**:
     - `frames`: Lista klatek animacji serca (załadowana z pliku `Assets/red_heart.png` przy pierwszym utworzeniu instancji). Klatki są skalowane o współczynnik `game_scale = 1.3`.
     - `frame_index`: Indeks aktualnej klatki animacji (typ `float` dla płynnego przejścia między klatkami).
     - `animation_speed`: Prędkość odtwarzania animacji (0.2 klatki na aktualizację).
     - `image`: Aktualna klatka animacji (`pygame.Surface`), ustawiana na podstawie `self.frames[int(self.frame_index)]`.
     - `rect`: Prostokąt `pygame.Rect` określający pozycję i rozmiar mikstury.
     - `vel_y`: Prędkość pionowa mikstury (wpływa na nią grawitacja).
     - `gravity`: Wartość przyciągania grawitacyjnego (0.5), dodawana do `vel_y` w każdej klatce.
     - `heal_amount`: Ilość punktów zdrowia przywracanych przez miksturę (25 punktów zdrowia).
     - `base_w`, `base_h`: Bazowe wymiary klatki animacji (16x16 pikseli) przed skalowaniem.
```

---

## Moduł: main.py
### 1. Architektura
- **Wzorzec aplikacji**: Gra oparta na bibliotece Pygame z asynchronicznym uruchomieniem przy użyciu `asyncio` (wymagane przez Pygbag dla wersji webowej). Implementacja wzorca **maszyny stanów** do zarządzania różnymi ekranami gry (menu, wybór postaci, rozgrywka, ustawienia, wybór trudności, wybór mapy).
- **Struktura pliku**:
  - Główny plik `main.py` zawiera pętlę gry, zarządzanie stanami oraz inicjalizację zasobów.
  - Wszystkie importy niestandardowe (poza `pygame` i modułami standardowymi) są umieszczone wewnątrz funkcji `main()` ze względu na wymagania Pygbag (ładowanie asynchroniczne).
  - Ustawienie kodowania UTF-8 dla konsoli w celu uniknięcia błędów `charmap` na systemach Windows.
  - Ustawienie katalogu roboczego na folder zawierający `main.py` (wymagane przez Pygbag).
- **Zarządzanie stanami**: Gra wykorzystuje maszynę stanów z następującymi stanami:
  - `STATE_MENU`: Ekran główny z opcjami wyboru trybu gry.
  - `STATE_DIFF_SELECT`: Wybór poziomu trudności (tylko dla trybu single player).
  - `STATE_CHAR_SELECT`: Wybór postaci dla graczy.
  - `STATE_MAP_SELECT`: Wybór mapy (tylko dla trybu multiplayer).
  - `STATE_SETTINGS`: Ustawienia sterowania.
  - `STATE_PLAYING`: Główna pętla gry.
- **Moduły zewnętrzne**:
  - `assets_manager`: Zarządzanie zasobami (grafika, dźwięk, muzyka).
  - `ui`: Obsługa interfejsu użytkownika (menu, HUD, tła, parallax background, podgląd postaci, wybór mapy/trudności).
  - `map_module`: Zarządzanie mapami, platformami, tłem oraz ładowaniem kafelków.
  - `characters`: Definicje postaci (klasy `Soldier`, `Orc`, `HumanSoldier`, `Golem`).
  - `items`: Przedmioty w grze (np. `Arrow`, `HealthPotion`).
  - `config`: Stałe konfiguracyjne (rozdzielczość, ścieżki zasobów, stany gry, sterowanie, czas odradzania mikstur).
- **Nowe funkcjonalności i aktualizacje**:
  - Obsługa przełączania trybu pełnoekranowego (`toggle_fullscreen()`) z odświeżaniem mapy po zmianie trybu.
  - Dynamiczne zarządzanie muzyką tła (włączanie/wyłączanie w zależności od stanu gry).
  - Bezpieczne resetowanie pozycji graczy przy zmianie mapy (sprawdzanie istnienia obiektów przed odwołaniem się do `rect`).
  - Obsługa przejścia do kolejnego poziomu w trybie single player po pokonaniu wszystkich przeciwników.
  - Dodano obsługę wyboru poziomu trudności (`STATE_DIFF_SELECT`) z nawigacją i potwierdzaniem wyboru.
  - Poprawiono bezpieczeństwo kodu poprzez sprawdzanie istnienia obiektów przed ich użyciem (np. `if player1 is not None`).
  - Ulepszono logikę gry w trybie single player, w tym odnawianie części HP gracza po przejściu poziomu i resetowanie timera mikstur.
  - Dodano obsługę wyboru postaci w trybie single player za pomocą strzałek (wcześniej tylko `A` i `D`).
  - Ulepszono obsługę zdarzeń w `handle_playing_events` poprzez bezpieczne sprawdzanie stanu śmierci graczy przed restartem gry.
  - **Nowe funkcje pomocnicze**:
    - `spawn_character(name, x, y)`: Tworzy instancję postaci na podstawie nazwy i współrzędnych.
    - `redraw_map()`: Odświeża powierzchnię mapy na podstawie `game_map_data`.
    - `draw_debug_info(surface, platforms_list, players, enemies)`: Rysuje hitboxy i platformy w trybie debugowania.
    - `toggle_fullscreen()`: Przełącza tryb pełnoekranowy i odświeża mapę.

---

### 2. Interfejsy
#### 2.1. Wejście (Input)
- **Sterowanie**:
  - Domyślne klawisze dla graczy są zdefiniowane w `config.py` (`DEFAULT_P1_CONTROLS`, `DEFAULT_P2_CONTROLS`).
  - Możliwość zmiany klawiszy w ustawieniach (`STATE_SETTINGS`).
  - Obsługa klawiszy:
    - **Nawigacja w menu**:
      - Strzałki (`UP`, `DOWN`): Przesuwanie kursora.
      - `ENTER`: Potwierdzenie wyboru.
      - `ESC`: Powrót do poprzedniego stanu (np. z `STATE_PLAYING` do `STATE_MENU`).
    - **Wybór trudności**:
      - Strzałki (`UP`, `DOWN`): Przesuwanie kursora między poziomami trudności.
      - `ENTER`: Potwierdzenie wyboru trudności.
      - `ESC`: Powrót do menu głównego.
    - **Wybór postaci**:
      - Gracz 1: Klawisze `A`, `D` lub strzałki (`LEFT`, `RIGHT`) w trybie single player.
      - Gracz 2: Strzałki (`LEFT`, `RIGHT`) w trybie multiplayer.
      - `ENTER`: Potwierdzenie wyboru.
      - `ESC`: Powrót do menu głównego.
    - **Wybór mapy**:
      - Strzałki (`LEFT`, `RIGHT`) lub klawisze `A`, `D`: Przesuwanie kursora między mapami.
      - `ENTER`: Potwierdzenie wyboru mapy.
      - `ESC`: Powrót do wyboru postaci.
    - **Sterowanie postaciami**:
      - Gracz 1: Klawisze ruchu (`A`, `D`), skok (`W`), ataki (`atk1`, `atk2`, `special`), blok (`block`).
      - Gracz 2: Klawisze ruchu (strzałki), skok (`UP`), ataki (`atk1`, `atk2`, `special`), blok (`block`).
    - **Inne**:
      - `F`: Przełączanie trybu pełnoekranowego (tylko na desktopie, nie działa w przeglądarce).
      - `RETURN` w `STATE_PLAYING`: Restart gry po śmierci postaci (powrót do menu).
- **Zdarzenia Pygame**: Obsługa zdarzeń `pygame.KEYDOWN` i `pygame.QUIT`.
- **Nowe funkcjonalności**:
  - Dynamiczne przypisywanie klawiszy w ustawieniach (`is_binding` i `bind_list`).
  - Obsługa wyboru trudności (`STATE_DIFF_SELECT`) z nawigacją strzałkami i potwierdzeniem `ENTER`.
  - W trybie single player, gracz może używać strzałek do wyboru postaci (wcześniej tylko `A` i `D`).
  - Ulepszona nawigacja w menu wyboru mapy (obsługa klawiszy `A`, `D` oprócz strzałek).
  - **Nowe funkcje obsługi zdarzeń**:
    - `handle_menu_events(event, current_idx)`: Obsługa nawigacji w menu głównym.
    - `handle_diff_events(event, current_diff_idx)`: Obsługa wyboru trudności.
    - `handle_char_select_events(event, p1_idx, p2_idx)`: Obsługa wyboru postaci.
    - `handle_map_select_events(event, current_map_idx)`: Obsługa wyboru mapy.
    - `handle_settings_events(event, current_idx, binding_status)`: Obsługa ustawień sterowania.
    - `handle_playing_events(event)`: Obsługa zdarzeń w trakcie gry.

#### 2.2. Wyjście (Output)
- **Rendering**:
  - Ekran gry o rozdzielczości `SCREEN_WIDTH x SCREEN_HEIGHT` (zdefiniowane w `config.py`).
  - Tryb wyświetlania: `pygame.SCALED | pygame.RESIZABLE` (skalowanie ekranu, bez pełnego ekranu w przeglądarce).
  - **Elementy wizualne**:
    - **Tło**:
      - Parallax background dla menu (`ui.ParallaxBackground`).
      - Statyczne tło dla map (ładowane z `map_module.load_background()`).
    - **Mapa**:
      - Renderowana na podstawie `game_map_data` (kafelki) i `platforms` (kolizje).
      - Powierzchnia `map_surface` jest odświeżana przy zmianie mapy (`redraw_map()`) i przełączaniu trybu pełnoekranowego.
    - **Postacie**:
      - Renderowane na podstawie animacji (atrybut `image` w klasach postaci).
      - Kierunek postaci (`direction`) wpływa na orientację sprite'a.
      - Podgląd postaci w `STATE_CHAR_SELECT` (`p1_previews`, `p2_previews`).
    - **HUD**:
      - Paski życia dla graczy i przeciwników (tylko w trybie single player).
      - Punkty obrażeń (niezrealizowane w kodzie, ale miejsce na rozbudowę).
      - Licznik FPS (tylko w trybie `DEBUG_MODE`).
    - **Debug**:
      - Wizualizacja hitboxów (`rect`) i platform (`draw_debug_info()`).
      - Wyświetlanie czasu logiki+renderingu ramki (tylko w trybie `DEBUG_MODE`).
    - **Menu i podmenu**:
      - Wybór trudności (`ui.draw_difficulty_select()`) z podświetleniem aktualnie wybranej opcji.
      - Wybór mapy (`ui.draw_map_select()`).
      - Ustawienia sterowania (`ui.draw_settings()`).
      - Efekt animacji strzałek w menu wyboru postaci (`ui.arrow_offset_L/R`).
- **Dźwięk**:
  - Muzyka tła (`megaman.wav`) odtwarzana w stanach menu (`STATE_MENU`, `STATE_CHAR_SELECT`, `STATE_MAP_SELECT`, `STATE_SETTINGS`, `STATE_DIFF_SELECT`).
  - Automatyczne włączanie/wyłączanie muzyki przy zmianie stanu gry.
- **Nowe funkcjonalności**:
  - Wizualne podświetlenie wybranych opcji w menu (efekt strzałek z przesunięciem `ui.arrow_offset_L/R`).
  - Dynamiczne renderowanie listy map i trudności na podstawie danych z `config.py` i `map_module.py`.
  - Wyświetlanie aktualnie wybranej trudności w `STATE_DIFF_SELECT`.
  - Ulepszone renderowanie menu wyboru mapy z podglądem miniatur.
  - **Nowe funkcje renderowania**:
    - `menu_parallax.update()` i `menu_parallax.draw(screen)`: Aktualizacja i rysowanie tła parallax.
    - `ui.draw_menu(screen, menu_options, menu_index)`: Rysowanie menu głównego.
    - `ui.draw_difficulty_select(screen, diff_index)`: Rysowanie menu wyboru trudności.
    - `ui.draw_char_select(screen, p1_previews, p2_previews, p1_char_index, p2_char_index, available_chars, game_mode)`: Rysowanie menu wyboru postaci.
    - `ui.draw_map_select(screen, map_module.available_maps, selected_map_index)`: Rysowanie menu wyboru mapy.
    - `ui.draw_settings(screen, bind_list, P1_CONTROLS, P2_CONTROLS, setting_selected_idx, is_binding)`: Rysowanie ustawień sterowania.
    - `ui.draw_playing_hud(screen, player1, player2, game_mode, cpu_enemies)`: Rysowanie HUD w trakcie gry.

---

### 3. Logika
#### 3.1. Inicjalizacja
- **Zasoby**:
  - Ładowanie zasobów odbywa się po inicjalizacji Pygame:
    - `assets_manager.load_all_assets()`: Grafika i dźwięk.
    - `ui.load_ui_assets()`: Elementy interfejsu (czcionki, sprite'y menu).
    - `map_module.load_tiles()`: Tekstury kafelków mapy.
- **Postacie**:
  - Inicjalizacja postaci graczy (`player1`, `player2`) i przeciwników (`cpu_enemies`) na podstawie wyboru w `STATE_CHAR_SELECT`.
  - Funkcja `spawn_character()` tworzy instancje postaci na podstawie nazwy (np. `"Soldier"` → `Soldier(x, y)`).
  - Podgląd postaci w `STATE_CHAR_SELECT` (`p1_previews`, `p2_previews`).
- **Mapa**:
  - Budowanie mapy z kafelków na podstawie danych z `map_module.build_platforms()`.
  - Losowe generowanie map w trybie single player (`random.choice(map_module.single_levels)`).
  - Odświeżanie mapy (`redraw_map()`) przy zmianie poziomu, przejściu do `STATE_PLAYING` lub przełączaniu trybu pełnoekranowego.
- **Nowe funkcjonalności**:
  - Inicjalizacja poziomu trudności (`current_difficulty`) na podstawie wyboru w `STATE_DIFF_SELECT`.
  - Bezpieczne czyszczenie list (`platforms`, `cpu_enemies`, `arrows`, `potions`) przy zmianie mapy.
  - Ustawienie domyślnego poziomu trudności na "Normalny" (`diff_index = 1`).
  - Inicjalizacja podglądu postaci z odpowiednimi kierunkami (`p1_previews` patrzą w prawo, `p2_previews` w lewo).
  - **Nowe zmienne stanu**:
    - `is_menu_music_playing`: Flaga kontrolująca odtwarzanie muzyki menu.
    - `potion_spawn_timer`: Licznik czasu do spawnu kolejnej mikstury.
    - `fps_print_timer`: Licznik ramek do wyświetlania debug info.

#### 3.2. Pętla gry
- **Aktualizacja stanu**:
  - Obsługa zdarzeń (klawiatura, wyjście z gry) w zależności od `game_state`.
  - **Menu i podmenu**:
    - Nawigacja po opcjach (`handle_menu_events`, `handle_diff_events`, `handle_char_select_events`, `handle_map_select_events`, `handle_settings_events`).
    - Zmiana stanu gry (np. `STATE_MENU` → `STATE_CHAR_SELECT` lub `STATE_DIFF_SELECT`).
    - Dynamiczne przypisywanie klawiszy w ustawieniach (`is_binding`).
  - **Gra (`STATE_PLAYING`)**:
    - **Aktualizacja logiki**:
      - Postacie graczy (`player1.update()`, `player2.update()`).
      - Przeciwnicy AI (`en.update_cpu()`) w trybie single player (z uwzględnieniem `current_difficulty`).
      - Strzały (`Arrow.update()`) i mikstury (`HealthPotion.update()`).
      - Kolizje:
        - Postacie-platformy (sprawdzane w metodach `update` postaci).
        - Strzały-postacie (sprawdzane w `Arrow.update()`).
        - Mikstury-postacie (sprawdzane w `HealthPotion.update()`).
    - **Logika gry**:
      - Spawn mikstur życia (`HealthPotion`) co `POTION_SPAWN_COOLDOWN` (maksymalnie 3 na mapie).
      - Usuwanie martwych przeciwników (`cpu_enemies.remove(en)`).
      - Przejście na kolejny poziom po pokonaniu wszystkich przeciwników (tryb single player).
      - Zawijanie ekranu (`screen_wrap()`) dla postaci wychodzących poza granice ekranu.
      - Odnawianie części HP gracza (`player1.current_hp + 20`) po przejściu poziomu.
      - Resetowanie timera mikstur (`potion_spawn_timer = 0`) po przejściu poziomu.
    - **Renderowanie**:
      - Rysowanie tła, mapy, postaci, przedmiotów i HUD.
      - Odświeżanie ekranu (`pygame.display.flip()`).
      - Kontrola FPS (`clock.tick(FPS)`) z asynchroniczną pauzą (`await asyncio.sleep(0)`) dla wersji webowej.
- **Zarządzanie stanami**:
  - Każdy stan gry ma dedykowaną funkcję obsługi zdarzeń klawiatury:
    - `handle_menu_events()`: Nawigacja w menu głównym.
    - `handle_diff_events()`: Wybór trudności.
    - `handle_char_select_events()`: Wybór postaci.
    - `handle_map_select_events()`: Wybór mapy.
    - `handle_settings_events()`: Zmiana ustawień sterowania.
    - `handle_playing_events()`: Obsługa klawiszy w trakcie gry.
  - **Muzyka**: Automatyczne włączanie/wyłączanie muzyki tła w zależności od stanu gry (lista `states_with_music`).
- **Nowe funkcjonalności**:
  - Obsługa wyboru trudności (`STATE_DIFF_SELECT`) z nawigacją i potwierdzaniem.
  - Ulepszona logika przejścia między stanami gry (np. z `STATE_DIFF_SELECT` do `STATE_CHAR_SELECT` po wyborze trudności).
  - Bezpieczne sprawdzanie stanu postaci przed restartem gry (np. `is_p1_dead = player1.is_dead if player1 is not None else False`).
  - Ulepszona obsługa zdarzeń w `handle_map_select_events` (dodano obsługę klawiszy `A`, `D`).
  - Ulepszona obsługa zdarzeń w `handle_playing_events` (sprawdzanie śmierci graczy przed restartem).
  - **Nowe mechaniki gry**:
    - Przejście na kolejny poziom w trybie single player po pokonaniu wszystkich przeciwników.
    - Odnawianie części HP gracza po przejściu poziomu.
    - Resetowanie timera mikstur po przejściu poziomu.

#### 3.3. Tryby gry
- **Single Player**:
  - Gracz (`player1`) walczy z przeciwnikami sterowanymi przez AI (`cpu_enemies`).
  - Poziom trudności (`current_difficulty`) wpływa na zachowanie przeciwników (parametr `en.difficulty`).
  - Losowe generowanie map po pokonaniu wszystkich przeciwników (z `map_module.single_levels`).
  - Odnawianie części HP gracza (`player1.current_hp + 20`) po przejściu poziomu.
  - Resetowanie timera mikstur (`potion_spawn_timer = 0`) po przejściu poziomu.
- **Multiplayer**:
  - Dwóch graczy (`player1` i `player2`) walczy ze sobą na wybranej mapie.
  - Brak przeciwników AI.
  - Wybór mapy z `map_module.available_maps`.

#### 3.4. Debugowanie
- **Tryb `DEBUG_MODE`**:
  - Wizualizacja hitboxów (`rect`) i platform (`draw_debug_info()`).
  - Wyświetlanie FPS i czasu logiki+renderingu ramki w konsoli (co 180 ramek).
  - Obsługa błędów (np. przełączanie pełnego ekranu, pomiar czasu).
  - Bezpieczne sprawdzanie istnienia obiektów przed odwołaniem się do ich atrybutów (np. `if player1 is not None`).
  - Pomiar czasu wykonania logiki i renderowania ramki (`frame_logic_time`).
- **Nowe funkcjonalności**:
  - Ulepszone debugowanie w trybie single player (wyświetlanie hitboxów przeciwników).
  - Bezpieczne sprawdzanie stanu obiektów przed ich użyciem (np. `filter(None, all_chars)`).

---

### 4. Modele
#### 4.1. Postacie
- **Klasy postaci** (dziedziczące po klasie bazowej z modułu `characters`):
  - `Soldier`: Podstawowa postać z umiejętnościami ataku i obrony.
  - `Orc`: Postać z większą siłą, ale wolniejsza.
  - `HumanSoldier` (Knight): Zbalansowana postać z umiejętnością specjalną.
  - `Golem`: Wolna, ale wytrzymała postać.
- **Wspólne atrybuty**:
  - `rect`: Pozycja i rozmiar hitboxa (używany do kolizji i renderowania).
  - `hitbox`: Hitbox dla kolizji (mniejszy niż `rect` dla precyzyjniejszych interakcji).
  - `current_hp`, `max_hp`: Punkty życia (aktualne i maksymalne).
  - `animations`: Słownik animacji (klucze: `'idle'`, `'run'`, `'attack1'`, `'attack2'`, `'special'`, `'block'`, `'death'`; wartości: listy klatek animacji).
  - `frame_index`: Indeks aktualnej klatki animacji.
  - `is_dead`: Flaga śmierci postaci.
  - `direction`: Kierunek patrzenia (`'left'`/`'right'`).
  - `image`: Aktualny sprite postaci (wybierany na podstawie animacji i kierunku).
  - `image_offset_y`: Przesunięcie sprite'a względem `rect` (dla poprawnego renderowania).
- **Wspólne metody**:
  - `update()`: Aktualizacja logiki postaci (ruch, ataki, kolizje z platformami, obsługa animacji).
    - Parametry: `opponent` (przeciwnik), `arrows` (lista strzał), `controls` (mapa klawiszy), `platforms` (lista platform), `keys_pressed` (stan klawiatury).
  - `update_cpu()`: Logika AI dla przeciwników (tylko tryb single player).
    - Parametry: `player` (gracz), `arrows` (lista strzał), `platforms` (lista platform).
    - Zachowanie zależne od `difficulty` (poziom trudności).
  - `screen_wrap()`: Zawijanie ekranu (postacie wychodzące z jednej strony pojawiają się po drugiej).
  - Metody ataku: `attack1()`, `attack2()`, `special_attack()` (tworzą obiekty `Arrow`).
- **Specyficzne zachowania**:
  - Przeciwnicy AI (`cpu_enemies`) atakują gracza na podstawie odległości i poziomu trudności.

#### 4.2. Przedmioty
- **Arrow**:
  - Strzały wystrzeliwane przez postacie (efekt ataków).
  - Atrybuty:
    - `rect`: Pozycja i rozmiar strzały.
    - `image`: Sprite strzały.
    - `speed`: Prędkość ruchu.
    - `damage`: Obrażenia zadawane postaciom.
    - `direction`: Kierunek ruchu (`'left'`/`'right'`).
    - `active`: Flaga aktywności (usuwana po trafieniu lub wyjściu poza ekran).
  - Metody:
    - `update()`: Aktualizacja pozycji i sprawdzanie kolizji z postaciami.
- **HealthPotion**:
  - Mikstury życia spawnowane na mapie.
  - Atrybuty:
    - `rect`: Pozycja i rozmiar mikstury.
    - `image`: Sprite mikstury.
    - `heal_amount`: Ilość odnawianego HP.
  - Metody:
    - `update()`: Sprawdzanie kolizji z postaciami i odnawianie HP.

#### 4.3. Mapa
- **Struktura**:
  - `game_map_data`: Dwuwymiarowa tablica (lista list) reprezentująca kafelki mapy (indeksy kafelków lub `None` dla pustych miejsc).
  - `platforms`: Lista prostokątów (`pygame.Rect`) reprezentujących platformy (kolizje).
  - `map_surface`: Powierzchnia Pygame (`pygame.Surface`) z wyrenderowaną mapą (kafelki).
- **Funkcje**:
  - `redraw_map()`: Odświeżanie `map_surface` na podstawie `game_map_data`.
    - Ustawia kolor `(0, 0, 0)` jako przezroczysty (`set_colorkey`).
    - Renderuje kafelki na podstawie indeksów w `game_map_data`.
  - `map_module.build_platforms()`: Budowanie platform i przeciwników na podstawie danych mapy.
    - Parametry: `data` (dane mapy), `platforms` (lista do uzupełnienia), `enemies` (lista przeciwników), `game_mode` (tryb gry).
    - Zwraca `game_map_data` (tablica kafelków).

#### 4.4. Konfiguracja
- **Plik `config.py`**: Zawiera stałe używane w grze:
  - **Rozdzielczość i skalowanie**:
    - `SCREEN_WIDTH`, `SCREEN_HEIGHT`: Wymiary ekranu.
    - `TILE_SIZE`, `TILE_SCALE`: Rozmiar kafelków i skala.
  - **Ścieżki zasobów**:
    - `TILES_PATH`: Ścieżka do folderu z kafelkami.
  - **Kolory**:
    - `COLOR_BG`: Kolor tła (czarny).
  - **Stany gry**:
    - `STATE_MENU`, `STATE_CHAR_SELECT`, `STATE_MAP_SELECT`, `STATE_SETTINGS`, `STATE_PLAYING`, `STATE_DIFF_SELECT`: Stałe reprezentujące stany gry.
  - **Poziomy trudności**:
    - `DIFFICULTY_LABELS`: Etykiety poziomów trudności (np. `"Łatwy"`, `"Normalny"`, `"Trudny"`).
    - `DIFFICULTY_VALUES`: Wartości trudności (wpływają na AI przeciwników).
  - **Sterowanie**:
    - `DEFAULT_P1_CONTROLS`, `DEFAULT_P2_CONTROLS`: Domyślne mapowania klawiszy dla graczy.
  - **Inne**:
    - `FPS`: Docelowa liczba klatek na sekundę.
    - `POTION_SPAWN_COOLDOWN`: Czas między spawnami mikstur życia (w klatkach).
---

---

## Moduł: map.py
```
**1. Architektura**
- Moduł `map.py` zarządza danymi map i poziomów dla trybów gry *multiplayer* oraz *single player*, a także obsługuje ładowanie zasobów graficznych (kafelków i tła).
- Wykorzystuje zewnętrzne zależności:
  - `pygame` – do renderowania grafik i obsługi powierzchni.
  - `random` – do losowania wariantów kafelków (`R`).
  - `pathlib.Path` – do obsługi ścieżek plików w sposób niezależny od systemu operacyjnego.
  - `config` – stałe konfiguracyjne (rozmiary kafelków, ścieżki zasobów, wymiary ekranu, lista kafelków z kolizjami).
  - `characters` – klasy przeciwników (importowane dynamicznie w funkcji `build_platforms` w celu uniknięcia cyklicznych zależności).
- Nowe symbole w danych map:
  - `'R'` – losowy kafelek (zastępowany w runtime przez indeks 60–62).
  - `'O'`, `'G'`, `'K'` – symbole przeciwników (Orc, Golem, HumanSoldier; aktywne tylko w trybie *single player*).

---

**2. Interfejsy**
- **Dane map i poziomów**:
  - `available_maps` – lista słowników definiujących mapy dla trybu *multiplayer* (klucze: `name`, `data`, `bg_path`).
  - `single_levels` – lista słowników definiujących poziomy dla trybu *single player* (struktura analogiczna do `available_maps`, dodatkowo zawiera symbole przeciwników w danych mapy).
  - Symbole specjalne w danych map:
    - `B` – tło (pusty kafelek, nie generuje kolizji).
    - `R` – losowy kafelek (zastępowany w runtime przez indeks 60–62).
    - `O`, `G`, `K` – symbole przeciwników (Orc, Golem, HumanSoldier; aktywne tylko w trybie *single player*).

- **Funkcje publiczne**:
  - `get_path(relative_path: str) -> str` – konwertuje ścieżkę relatywną na absolutną (bazując na `ASSETS_PATH` zdefiniowanym w `config.py`).
  - `load_background(bg_path: str) -> pygame.Surface` – ładuje i skaluje tło na podstawie ścieżki. Zwraca powierzchnię `pygame.Surface` o wymiarach `SCREEN_WIDTH` × `SCREEN_HEIGHT`.
  - `load_tiles(folder_path: str, scale: int) -> list[pygame.Surface]` – ładuje kafelki z plików `.png` (nazewnictwo: `kafelek{i}.png`, gdzie `i` ∈ [0, 59]) oraz arkuszy sprite'ów (`sprite1.png`, `sprite2.png`). Obsługuje błędy ładowania (generuje różową powierzchnię zastępczą).
  - `build_platforms(map_data: list[list], platforms_list: list, cpu_enemies_list: list, game_mode: str) -> list[list]` – przetwarza dane mapy:
    - Uzupełnia listy platform (obiekty `pygame.Rect` dla kolizji) i przeciwników (tylko dla trybu *single player*).
    - Zastępuje symbole `R` losowymi indeksami kafelków (60–62).
    - Dodaje instancje przeciwników na podstawie symboli (`O`, `G`, `K`).
    - Zwraca zmodyfikowane dane mapy (kopię oryginalnych danych z podmienionymi symbolami).

---

**3. Logika**
- **Generowanie map**:
  - Funkcja `build_platforms` iteruje po danych mapy (dwuwymiarowa lista), przetwarzając każdy kafelek:
    - Dla symbolu `R`: losuje indeks kafelka (60, 61 lub 62) i dodaje prostokąt kolizji do `platforms_list`.
    - Dla indeksów liczbowych: sprawdza, czy kafelek należy do `COLLISION_TILES` (z `config.py`), i jeśli tak, dodaje prostokąt kolizji.
    - Dla symboli przeciwników (`O`, `G`, `K`): tworzy instancje odpowiednich klas (tylko w trybie *single player*) i dodaje je do `cpu_enemies_list`.
  - Modyfikuje kopię danych mapy (aby nie zmieniać oryginału) i zwraca ją.

- **Obsługa zasobów**:
  - Kafelki są ładowane z plików o nazwach `kafelek{i}.png` (i=0–59) oraz z arkuszy sprite'ów (`sprite1.png`, `sprite2.png`). Arkusze są dzielone na kafelki o rozmiarze 16×16 pikseli (bazowy rozmiar kafelka).
  - W przypadku błędów ładowania generowana jest różowa powierzchnia zastępcza (`pygame.Surface` wypełniona kolorem RGB (255, 0, 255)).
  - Tła są skalowane do wymiarów ekranu (`SCREEN_WIDTH`, `SCREEN_HEIGHT`).

---

**4. Modele**
- **Struktura danych mapy**:
  - Dwuwymiarowa lista (wiersze × kolumny), gdzie każdy element to:
    - Liczba całkowita – indeks kafelka (np. `2`, `13`, `60`).
    - Symbol specjalny (np. `B`, `R`, `O`, `G`, `K`).
  - Wymiary mapy są ustalane na podstawie liczby kolumn i stałej `TILE_SIZE` (np. 23 kolumny × `TILE_SIZE` = szerokość ekranu `SCREEN_WIDTH`).

- **Zależności zewnętrzne**:
  - Klasy przeciwników (`Orc`, `Golem`, `HumanSoldier`) są importowane dynamicznie w funkcji `build_platforms` w celu uniknięcia cyklicznych zależności między modułami.
  - Lista `COLLISION_TILES` (z `config.py`) definiuje, które kafelki generują kolizje.

- **Reprezentacja kolizji**:
  - Platformy (kolizje) są reprezentowane jako obiekty `pygame.Rect` przechowywane w liście `platforms_list`.
  - Każdy prostokąt ma wymiary `TILE_SIZE` × `TILE_SIZE` i pozycję odpowiadającą pozycji kafelka na mapie.
```

---

---

## Moduł: ui.py
```
1. **Architektura**
   - Plik `ui.py` implementuje warstwę prezentacji gry, odpowiadając za renderowanie wszystkich elementów interfejsu użytkownika przy użyciu biblioteki **pygame**.
   - Wykorzystuje **modularne podejście** do zarządzania zasobami graficznymi, oddzielając logikę ładowania (`load_ui_assets()`) od logiki rysowania (funkcje `draw_*`).
   - Implementuje **dwupoziomowy system cache'owania** dla optymalizacji wydajności:
     - `TEXT_CACHE`: Przechowuje gotowe powierzchnie wyrenderowanych tekstów (limitowany przez `MAX_CACHE_SIZE` z `config.py`).
     - `CHAR_SURFACE_CACHE`: Przechowuje pojedyncze znaki czcionki bitmapowej z możliwością dynamicznej zmiany kolorów.
   - Wspiera **tryby gry**:
     - Single-player (solo) z wyborem poziomu trudności i przeciwników sterowanych przez CPU.
     - Multiplayer (multi) z obsługą dwóch graczy (P1/P2) na jednym urządzeniu.
   - Zawiera **klasę `ParallaxBackground`** dla efektu głębi tła, z optymalizacją ruchu sub-pikselowego i stałą liczbą operacji `blit`.
   - **Nowe elementy i aktualizacje**:
     - Dodano obsługę strzałki w lewo (`ARROW_IMG_LEFT`) jako lustrzanego odbicia `ARROW_IMG`.
     - Zmienne globalne `arrow_offset_L` i `arrow_offset_R` do płynnej animacji strzałek wyboru postaci.
     - Wprowadzono stałą `MAX_CACHE_SIZE` z `config.py` dla lepszej kontroli nad rozmiarem cache.
     - **Optymalizacja**: Dynamiczne tworzenie obiektów `pygame.Color` poza pętlą w funkcji `draw_custom_text` dla poprawy wydajności.
     - **Bezpieczeństwo zasobów**: Użycie bloku `with` w funkcji `change_color` dla zarządzania `PixelArray`.
     - **Debugowanie**: Dodano komunikaty kontrolne (`print`) w funkcji `load_ui_assets()` dla łatwiejszego śledzenia ładowania zasobów.
     - **Rozszerzenie trybu multiplayer**: Pełna obsługa wyboru postaci dla dwóch graczy z oddzielnymi ramkami i tablicami statystyk.

2. **Interfejsy**
   - **Funkcje rysowania UI**:
     - `draw_menu(screen, menu_options, menu_index)`:
       - Renderuje menu główne z tytułem "PRZYSTAN FIGHT CLUB" i opcjami gry.
       - Wykorzystuje kolorystykę fioletowo-złotą (`PURPLE_BG`, `GOLD_BORDER`).
     - `draw_difficulty_select(screen, selected_idx)`:
       - Wyświetla ekran wyboru poziomu trudności z trzema opcjami (ŁATWY/NORMALNY/TRUDNY).
       - Używa motywów kolorystycznych (zielony/żółty/czerwony) dla wizualnego odróżnienia poziomów.
     - `draw_char_select(screen, p1_previews, p2_previews, p1_idx, p2_idx, char_names, game_mode)`:
       - Obsługuje wybór postaci dla jednego lub dwóch graczy.
       - Wyświetla ramki, animacje postaci, tablice ze statystykami (`CHAR_STATS`) i opisami (`CHAR_DESCRIPTIONS`).
       - Implementuje płynne animacje strzałek wyboru (`arrow_offset_L`, `arrow_offset_R`).
       - **Rozszerzenie**: Pełna obsługa trybu multiplayer z oddzielnymi ramkami i tablicami dla P1 i P2, w tym dynamiczne etykiety ("P1: Nazwa", "P2: Nazwa").
     - `draw_map_select(screen, available_maps, selected_idx)`:
       - Pozwala na wybór areny z listy dostępnych map.
       - Wyświetla nazwę mapy w ozdobnych nawiasach (`< MAPA >`).
     - `draw_settings(screen, bind_list, p1_ctrl, p2_ctrl, selected_idx, is_binding)`:
       - Umożliwia konfigurację klawiszy sterowania dla obu graczy.
       - Obsługuje stan "bindowania" klawisza (czerwony kolor tła, komunikat `<WCISNIJ KLAWISZ>`).
       - **Aktualizacja**: Dodano marginesy tekstu w przyciskach dla lepszej czytelności.
     - `draw_playing_hud(screen, p1, p2, game_mode, cpu_enemies)`:
       - Rysuje paski życia graczy (`draw_hp_bar`).
       - Wyświetla komunikaty o wyniku walki (wygrana/przegrana) z odpowiednią kolorystyką (zielony/czerwony).
       - **Nowość**: Komunikaty dla trybu multiplayer ("GRACZ 1 WYGRAL!" / "GRACZ 2 WYGRAL!").
   - **Funkcje pomocnicze**:
     - `draw_custom_text(screen, text, x, y, font_png, scale, main_color, shadow_color, center)`:
       - Renderuje tekst z niestandardowej czcionki bitmapowej (`FONT_BITMAP`).
       - Obsługuje:
         - Skalowanie tekstu (`scale`).
         - Cienie i dynamiczne kolory (`main_color`, `shadow_color`).
         - Centrowanie tekstu (`center`).
         - Polskie znaki diakrytyczne (np. "Ś", "Ć") z korektą metryk (`get_char_metrics`).
         - Cache'owanie gotowych powierzchni tekstów (`TEXT_CACHE`).
         - **Optymalizacja**: Dynamiczne tworzenie obiektów `pygame.Color` poza pętlą znaków.
         - **Nowość**: Zapas wysokości (`t_height = 10 * scale`) dla znaków z ogonkami (np. polskie litery).
     - `draw_keyboard_button(screen, text, x, y, width, height, is_selected, bg_color, border_color)`:
       - Tworzy przyciski z zaokrąglonymi narożnikami (`border_radius=10`).
       - Obsługuje dynamiczne kolory tła i ramki w zależności od stanu (`is_selected`).
       - **Nowość**: Możliwość przekazania niestandardowego koloru tła (`bg_color`) i ramki (`border_color`).
     - `get_custom_text_width(text, scale)`:
       - Oblicza szerokość tekstu przed renderowaniem (używane do centrowania).
     - `get_char_metrics(char)`:
       - Zwraca metryki (szerokość, offset X/Y) dla pojedynczych znaków, uwzględniając:
         - Różnice między małymi a wielkimi literami.
         - Specjalne przypadki (np. "i", "l", "w", "m", polskie znaki "Ś", "Ć", "Ź", "Ż", "Ó", "Ń").
         - **Aktualizacja**: Dodano obsługę znaków "3" i "?" z korektą szerokości i offsetu.
     - `change_color(surface, old_main, new_main, old_shadow, new_shadow)`:
       - Tworzy kopię obrazka z podmienionymi kolorami (używane dla dynamicznych tekstów).
       - **Nowość**: Użycie bloku `with` dla bezpiecznego zarządzania `PixelArray`.
     - `load_ui_assets()`:
       - Ładuje obrazy UI z plików (ramki, strzałki, tablice, czcionki) i skaluje je do odpowiednich rozmiarów.
       - **Aktualizacja**: Dodano ładowanie lustrzanego odbicia strzałki (`ARROW_IMG_LEFT`) oraz komunikaty kontrolne w konsoli dla debugowania.

3. **Logika**
   - **Cache'owanie i optymalizacja**:
     - `TEXT_CACHE` i `CHAR_SURFACE_CACHE` ograniczają liczbę operacji renderowania tekstu.
     - Limit rozmiaru cache (`MAX_CACHE_SIZE=200`) zapobiega nadmiernemu zużyciu pamięci.
     - Usuwanie najstarszych elementów cache przy przekroczeniu limitu (`TEXT_CACHE.pop(next(iter(TEXT_CACHE)))`).
     - **Nowość**: Stała `MAX_CACHE_SIZE` importowana z `config.py` dla łatwiejszej konfiguracji i spójności.
   - **Animacje**:
     - Płynny ruch strzałek wyboru postaci (`arrow_offset_L`, `arrow_offset_R`) z automatycznym powrotem do pozycji spoczynkowej.
   - **Kolorystyka**:
     - Dynamiczne zmiany kolorów tekstów i przycisków w zależności od stanu (np. biały tekst na kolorowym tle dla zaznaczonych opcji).
     - Motywy kolorystyczne dla poziomów trudności (zielony/żółty/czerwony) i komunikatów (wygrana/przegrana).
     - **Nowość**: Dodano kolorystykę dla trybu multiplayer (niebieski dla P1, czerwony dla P2).
   - **Responsywność**:
     - Centrowanie elementów względem rozdzielczości ekranu (`SCREEN_WIDTH`, `SCREEN_HEIGHT`).
     - Skalowanie czcionek i obrazów dostosowane do rozmiaru ekranu.
   - **Obsługa języka polskiego**:
     - Korekta metryk dla polskich znaków diakrytycznych (np. "Ś", "Ć") w `get_char_metrics()`.
     - Zapas wysokości w powierzchni tekstu (`t_height = 10 * scale`) dla ogonków liter.
     - **Aktualizacja**: Dodano obsługę znaków "3" i "?" z korektą metryk.

4. **Modele**
   - **Zależności zewnętrzne**:
     - Importuje klasy postaci (`Soldier`, `Orc`, `HumanSoldier`, `Golem`) z `characters.py` i mapuje je w słowniku `CHAR_CLASS_MAP`.
     - Wykorzystuje stałe konfiguracyjne z `config.py`:
       - `SCREEN_WIDTH`, `SCREEN_HEIGHT`: Rozmiar ekranu.
       - `COLOR_GOLD`: Kolor złotej ramki.
       - `FONT_CHARS_MAP`: Mapa znaków czcionki bitmapowej.
       - `CHAR_STATS`: Statystyki postaci (atak, HP, szybkość).
       - `CHAR_DESCRIPTIONS`: Opisy postaci.
       - `DIFFICULTY_LABELS`: Etykiety poziomów trudności.
       - **Nowość**: `MAX_CACHE_SIZE` dla kontroli rozmiaru cache tekstów.
   - **Klasa `ParallaxBackground`**:
     - Zarządza tłem z efektem paralaksy poprzez warstwy o różnych prędkościach (`speed`).
     - Optymalizacje:
       - Ruch sub-pikselowy (`x` jako `float`) dla płynności animacji.
       - Stała liczba operacji `blit` (obliczana przy inicjalizacji) zamiast dynamicznego dodawania kopii warstw.
       - Skalowanie warstw do wysokości ekranu przy zachowaniu proporcji szerokości.
       - Obsługa błędów ładowania warstw (zastępowanie brakujących plików przez przezroczyste powierzchnie).
```

---

