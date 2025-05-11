import pygame
import random

# Ініціалізація Pygame
pygame.init()

# Налаштування екрану
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dark Abyss")
clock = pygame.time.Clock()

# Кольори
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (200, 0, 0)
BLUE = (50, 50, 200)
GREEN = (0, 200, 50)

# Стани гри
MENU = "menu"
GAME = "game"
VICTORY = "victory"
game_state = MENU
 
background = pygame.image.load("background.png")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

# Шкала проходження
progress = 0
progress_max = 100
progress_timer = 0

# Клас гравця
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.speed = 5
        self.health = 100
        self.max_health = 100
        self.direction = 1

    def update(self, keys):
        if keys[pygame.K_a]:
            self.rect.x -= self.speed
            self.direction = -1
        if keys[pygame.K_d]:
            self.rect.x += self.speed
            self.direction = 1
        if keys[pygame.K_w]:
            self.rect.y -= self.speed
        if keys[pygame.K_s]:
            self.rect.y += self.speed

        self.rect.x = max(0, min(WIDTH - self.rect.width, self.rect.x))
        self.rect.y = max(0, min(HEIGHT - self.rect.height, self.rect.y))

    def attack(self):
        attack_rect = pygame.Rect(self.rect.x + (self.direction * 40), self.rect.y - 10, 50, 30)
        for enemy in enemies:
            if attack_rect.colliderect(enemy.rect):
                enemy.take_damage(30)

    def draw(self, surface):
        pygame.draw.rect(surface, BLUE, self.rect, border_radius=5)
        health_bar = pygame.Rect(10, 10, 200 * (self.health / self.max_health), 20)
        pygame.draw.rect(surface, GREEN, health_bar)

# Клас ворога
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, is_boss=False):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(RED)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = random.uniform(1.5, 2.5)
        self.health = 50 if not is_boss else 150
        self.is_boss = is_boss

    def update(self, player):
        dx = player.rect.x - self.rect.x
        dy = player.rect.y - self.rect.y
        dist = max(1, (dx**2 + dy**2) ** 0.5)
        self.rect.x += dx / dist * self.speed
        self.rect.y += dy / dist * self.speed
        if self.rect.colliderect(player.rect):
            player.health -= 0.3

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            if self.is_boss:
                global game_state
                game_state = VICTORY
            enemies.remove(self)

    def draw(self, surface):
        pygame.draw.rect(surface, RED, self.rect)

# Створення ворогів
def spawn_enemy():
    x = random.randint(50, WIDTH - 50)
    y = random.randint(50, HEIGHT - 50)
    enemies.append(Enemy(x, y))

# Клас меню
class Button:
    def __init__(self, text, x, y, width, height, callback):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.callback = callback

    def draw(self, surface):
        pygame.draw.rect(surface, WHITE, self.rect, border_radius=5)
        text_surf = pygame.font.Font(None, 36).render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.callback()

def start_game():
    global game_state, player, enemies, progress
    game_state = GAME
    progress = 0
    player = Player()
    enemies = [Enemy(random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 50)) for _ in range(3)]
    enemies.append(Enemy(WIDTH // 2, 50, is_boss=True))  # Додаємо бос-файт

buttons = [
    Button("Почати Гру", WIDTH // 2 - 100, 300, 200, 50, start_game),
]

# Основний цикл
running = True
while running:
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if game_state == MENU:
            for button in buttons:
                button.handle_event(event)
        if game_state == GAME and event.type == pygame.KEYDOWN and event.key == pygame.K_e:
            player.attack()

    if game_state == MENU:
        for button in buttons:
            button.draw(screen)
    elif game_state == GAME:
        keys = pygame.key.get_pressed()
        player.update(keys)
        for enemy in enemies:
            enemy.update(player)

        player.draw(screen)
        for enemy in enemies:
            enemy.draw(screen)

        # Шкала проходження
        progress_timer += clock.get_time()
        if progress_timer >= 5000:
            progress_timer = 0
            progress = min(progress + 10, progress_max)
        pygame.draw.rect(screen, WHITE, (WIDTH // 2 - 100, 10, 200, 20))
        pygame.draw.rect(screen, GREEN, (WIDTH // 2 - 100, 10, 200 * (progress / progress_max), 20))

        if progress >= progress_max:
            game_state = VICTORY

    elif game_state == VICTORY:
        screen.fill(BLACK)
        screen.blit(background, (0, 0))
        text = pygame.font.Font(None, 48).render("Перемога!", True, WHITE)
        screen.blit(text, (WIDTH // 2 - 100, HEIGHT // 2))
        pygame.time.delay(2000)
        game_state = MENU

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
