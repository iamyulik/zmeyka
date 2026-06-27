import pygame
import random
import sys
import os

# ========== ФУНКЦИЯ ДЛЯ ПУТЕЙ К РЕСУРСАМ ==========
def resource_path(relative_path):
    """Получает абсолютный путь к ресурсу, работает и для .exe, и для .py"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)
# ===================================================

pygame.init()

# ========== НАСТРОЙКИ РАЗМЕРА ==========
CELL = 48
GRID_SIZE = 13
WIDTH = CELL * GRID_SIZE
HEIGHT = CELL * GRID_SIZE
FPS = 5
# ========================================

# ========== НАСТРОЙКИ АНИМАЦИЙ ==========
EATING_DURATION = 0.1
DEATH_DURATION = 10
BAT_SPAWN_CHANCE = 2
# ========================================

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake")
clock = pygame.time.Clock()

# ========== ЗАГРУЗКА ШРИФТОВ ==========
font = pygame.font.SysFont(None, 36)

def load_custom_font(size):
    """Загружает кастомный шрифт с проверкой существования"""
    font_path = resource_path(os.path.join("assets", "Tokushupikuseru-Regular.otf"))
    
    if os.path.exists(font_path):
        try:
            return pygame.font.Font(font_path, size)
        except Exception as e:
            print(f"Ошибка загрузки шрифта: {e}")
    
    print("Использую стандартный шрифт")
    return pygame.font.SysFont("Arial", size)

gameover_font = load_custom_font(72)
small_font = load_custom_font(28)
# ========================================

# Текущая тема
current_theme = "light"  # Стартуем со светлой

# Состояния головы
HEAD_NORMAL = "normal"
HEAD_EATING = "eating"
HEAD_DEAD = "dead"

# Типы еды
FOOD_APPLE = "apple"
FOOD_SWEET = "sweet"

# Таймеры для анимаций
head_state = HEAD_NORMAL
eating_timer = 0
death_timer = 0

def load_image(path, size=None):
    """Загружает изображение и масштабирует до нужного размера"""
    full_path = resource_path(path)
    if os.path.exists(full_path):
        try:
            img = pygame.image.load(full_path).convert_alpha()
            if size:
                img = pygame.transform.scale(img, size)
            return img
        except Exception as e:
            print(f"Ошибка загрузки {full_path}: {e}")
    return None

def load_sprites():
    """Загружает все спрайты для текущей темы"""
    global current_theme
    sprites = {}
    
    print(f"Загружаю спрайты для темы: {current_theme}")  # Отладка
    
    # Загружаем спрайты для головы
    sprites['head_normal'] = load_image(f"assets/head_{current_theme}.png", (CELL, CELL))
    sprites['head_eating'] = load_image(f"assets/head_eat_{current_theme}.png", (CELL, CELL))
    sprites['head_dead'] = load_image(f"assets/head_dead_{current_theme}.png", (CELL, CELL))
    
    # Если нет тематических, пробуем общие
    if not sprites['head_normal']:
        sprites['head_normal'] = load_image("assets/head.png", (CELL, CELL))
    if not sprites['head_eating']:
        sprites['head_eating'] = load_image("assets/head_eat.png", (CELL, CELL))
    if not sprites['head_dead']:
        sprites['head_dead'] = load_image("assets/head_dead.png", (CELL, CELL))
    
    # Загружаем тело
    sprites['body'] = load_image(f"assets/body_{current_theme}.png", (CELL, CELL))
    if not sprites['body']:
        sprites['body'] = load_image("assets/body.png", (CELL, CELL))
    
    # Загружаем еду (оба вида)
    sprites['food_apple'] = load_image("assets/apple.png", (CELL, CELL))
    sprites['food_sweet'] = load_image("assets/sweet.png", (CELL, CELL))
    
    # Загружаем летучую мышь
    sprites['bat'] = load_image("assets/bat.png", (CELL, CELL))
    
    # Создаем заглушки для еды, если не загрузились
    if not sprites['food_apple']:
        sprites['food_apple'] = create_food_placeholder((255, 50, 50), CELL, "🍎")
    if not sprites['food_sweet']:
        sprites['food_sweet'] = create_food_placeholder((255, 200, 50), CELL, "🍬")
    if not sprites['bat']:
        sprites['bat'] = create_food_placeholder((100, 50, 150), CELL, "🦇")
    
    # Создаем заглушки для головы, если ничего не загрузилось
    if not sprites['head_normal']:
        sprites['head_normal'] = create_placeholder_sprite((0, 255, 0), CELL)
    if not sprites['head_eating']:
        sprites['head_eating'] = sprites['head_normal']
    if not sprites['head_dead']:
        sprites['head_dead'] = create_placeholder_sprite((255, 0, 0), CELL)
    if not sprites['body']:
        sprites['body'] = create_placeholder_sprite((0, 200, 0), CELL)
    
    return sprites

def create_placeholder_sprite(color, size):
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    padding = max(2, size // 16)
    pygame.draw.rect(surf, color, (padding, padding, size - padding*2, size - padding*2), border_radius=size//8)
    return surf

def create_food_placeholder(color, size, emoji=""):
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    if emoji:
        try:
            font_size = size // 2
            emoji_font = pygame.font.SysFont("Segoe UI Emoji", font_size)
            text = emoji_font.render(emoji, True, (255, 255, 255))
            text_rect = text.get_rect(center=(size//2, size//2))
            surf.blit(text, text_rect)
        except:
            pygame.draw.circle(surf, color, (size//2, size//2), size//2 - 4)
    else:
        pygame.draw.circle(surf, color, (size//2, size//2), size//2 - 4)
    pygame.draw.circle(surf, (255, 255, 255, 100), (size//4, size//4), size//8)
    return surf

def load_background(theme):
    """Загружает фоновое изображение"""
    bg_path = resource_path(f"assets/bg_{theme}.png")
    print(f"Загружаю фон: {bg_path}")  # Отладка
    
    if os.path.exists(bg_path):
        try:
            bg = pygame.image.load(bg_path)
            bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))
            return bg
        except Exception as e:
            print(f"Ошибка загрузки фона: {e}")
    
    # Запасной фон
    bg = pygame.Surface((WIDTH, HEIGHT))
    bg.fill((20, 20, 20) if theme == "dark" else (240, 240, 240))
    return bg

# Загружаем фоны
backgrounds = {
    "dark": load_background("dark"),
    "light": load_background("light")
}

# Загружаем спрайты
sprites = load_sprites()

# Летучая мышь
bat_active = False
bat_pos = (0, 0)

def spawn_bat():
    global bat_active, bat_pos
    attempts = 0
    while attempts < 100:
        pos = (random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1))
        if pos not in snake and pos != food_pos:
            bat_pos = pos
            bat_active = True
            return
        attempts += 1

def activate_bat_effect():
    """Активирует эффект от летучей мыши - переключает на темную тему"""
    global current_theme, sprites
    if current_theme != "dark":
        current_theme = "dark"
        sprites = load_sprites()
        print(f"Тема изменена на: {current_theme}")  # Отладка

def switch_theme():
    """Переключает тему"""
    global current_theme, sprites
    current_theme = "light" if current_theme == "dark" else "dark"
    sprites = load_sprites()
    print(f"Тема изменена на: {current_theme}")  # Отладка

def set_light_theme():
    """Принудительно устанавливает светлую тему"""
    global current_theme, sprites
    current_theme = "light"
    sprites = load_sprites()
    print(f"Тема принудительно установлена на: {current_theme}")

def set_head_state(state, duration=None):
    global head_state, eating_timer, death_timer
    if duration is None:
        if state == HEAD_EATING:
            duration = EATING_DURATION
        elif state == HEAD_DEAD:
            duration = DEATH_DURATION
        else:
            duration = 0
    head_state = state
    if state == HEAD_EATING:
        eating_timer = duration
    elif state == HEAD_DEAD:
        death_timer = duration
    else:
        eating_timer = 0
        death_timer = 0

def update_head_state():
    global head_state, eating_timer, death_timer
    if head_state == HEAD_EATING:
        eating_timer -= 1
        if eating_timer <= 0:
            head_state = HEAD_NORMAL
    if head_state == HEAD_DEAD:
        death_timer -= 1
        if death_timer <= 0:
            head_state = HEAD_NORMAL

def spawn_food():
    food_type = random.choice([FOOD_APPLE, FOOD_SWEET])
    position = (random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1))
    return position, food_type

# Змейка
start_x = GRID_SIZE // 2
start_y = GRID_SIZE // 2
snake = [(start_x, start_y), (start_x - 1, start_y), (start_x - 2, start_y)]
direction = (1, 0)

# Еда
food_pos, food_type = spawn_food()

def rotate_head(surface, direction, state=HEAD_NORMAL):
    if surface is None:
        return None
    if state == HEAD_DEAD:
        return surface
    if direction == (0, -1):
        return surface
    elif direction == (0, 1):
        return pygame.transform.rotate(surface, 180)
    elif direction == (-1, 0):
        return pygame.transform.rotate(surface, 90)
    elif direction == (1, 0):
        return pygame.transform.rotate(surface, 270)
    return surface

def draw():
    global head_state, bat_active
    
    # Отрисовываем фон
    screen.blit(backgrounds[current_theme], (0, 0))
    
    # Еда
    if food_type == FOOD_APPLE:
        food_sprite = sprites['food_apple']
    else:
        food_sprite = sprites['food_sweet']
    
    if food_sprite:
        screen.blit(food_sprite, (food_pos[0] * CELL, food_pos[1] * CELL))
    
    # Летучая мышь
    if bat_active and sprites['bat']:
        screen.blit(sprites['bat'], (bat_pos[0] * CELL, bat_pos[1] * CELL))
    
    # Змейка
    for i, segment in enumerate(snake):
        x = segment[0] * CELL
        y = segment[1] * CELL
        
        if i == 0:  # Голова
            if head_state == HEAD_EATING and sprites['head_eating']:
                head_sprite = sprites['head_eating']
            elif head_state == HEAD_DEAD and sprites['head_dead']:
                head_sprite = sprites['head_dead']
            else:
                head_sprite = sprites['head_normal']
            
            if head_state == HEAD_DEAD:
                rotated_head = head_sprite
            else:
                rotated_head = rotate_head(head_sprite, direction, head_state)
            
            if rotated_head:
                screen.blit(rotated_head, (x, y))
        else:
            if sprites['body']:
                screen.blit(sprites['body'], (x, y))
    
    pygame.display.flip()
    update_head_state()

def show_game_over(score):
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(200)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))
    
    game_over_text = gameover_font.render("GAME OVER", True, (255, 50, 50))
    game_over_rect = game_over_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 100))
    screen.blit(game_over_text, game_over_rect)
    
    score_text = gameover_font.render(f"Счет: {score}", True, (255, 255, 255))
    score_rect = score_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 20))
    screen.blit(score_text, score_rect)
    
    restart_text = small_font.render("Нажмите ENTER для рестарта", True, (200, 200, 200))
    restart_rect = restart_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 50))
    screen.blit(restart_text, restart_rect)
    
    exit_text = small_font.render("ESC - выход", True, (200, 200, 200))
    exit_rect = exit_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 90))
    screen.blit(exit_text, exit_rect)
    
    pygame.display.flip()

# Основной игровой цикл
running = True
while running:
    game_over = False
    
    # Сброс игры
    start_x = GRID_SIZE // 2
    start_y = GRID_SIZE // 2
    snake = [(start_x, start_y), (start_x - 1, start_y), (start_x - 2, start_y)]
    direction = (1, 0)
    food_pos, food_type = spawn_food()
    head_state = HEAD_NORMAL
    bat_active = False
    
    # ПРИНУДИТЕЛЬНО УСТАНАВЛИВАЕМ СВЕТЛУЮ ТЕМУ ПРИ КАЖДОМ СТАРТЕ
    set_light_theme()
    
    while not game_over:
        # Случайное появление летучей мыши
        if not bat_active and random.random() < BAT_SPAWN_CHANCE:
            spawn_bat()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and direction != (0, 1):
                    direction = (0, -1)
                elif event.key == pygame.K_DOWN and direction != (0, -1):
                    direction = (0, 1)
                elif event.key == pygame.K_LEFT and direction != (1, 0):
                    direction = (-1, 0)
                elif event.key == pygame.K_RIGHT and direction != (-1, 0):
                    direction = (1, 0)
                elif event.key == pygame.K_t:
                    switch_theme()
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
        
        head = snake[0]
        new_head = (head[0] + direction[0], head[1] + direction[1])
        
        # Проверка столкновения со стенами
        if (new_head[0] < 0 or new_head[1] < 0 or 
            new_head[0] >= GRID_SIZE or new_head[1] >= GRID_SIZE):
            set_head_state(HEAD_DEAD, DEATH_DURATION)
            draw()
            pygame.time.wait(300)
            game_over = True
            show_game_over(len(snake) - 3)
            break
        
        # Проверка столкновения с летучей мышью
        if bat_active and new_head == bat_pos:
            activate_bat_effect()
            bat_active = False
            snake.insert(0, new_head)
            snake.pop()
            draw()
            continue
        
        # Проверка столкновения с собой
        if new_head in snake:
            set_head_state(HEAD_DEAD, DEATH_DURATION)
            draw()
            pygame.time.wait(300)
            game_over = True
            show_game_over(len(snake) - 3)
            break
        
        snake.insert(0, new_head)
        
        # Проверка съедания еды
        if new_head == food_pos:
            set_head_state(HEAD_EATING, EATING_DURATION)
            food_pos, food_type = spawn_food()
            while food_pos in snake:
                food_pos, food_type = spawn_food()
        else:
            snake.pop()
        
        draw()
        clock.tick(FPS)
    
    # Ожидание рестарта
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    waiting = False
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
        clock.tick(10)