import pygame
import sys

# Initialize pygame-ce
pygame.init()

# Screen settings
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Clicker Damage Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 0, 0)
GREEN = (0, 200, 0)

# Clock for FPS control
clock = pygame.time.Clock()

# Enemy settings
enemy_width, enemy_height = 150, 150
enemy_x = WIDTH // 2 - enemy_width // 2
enemy_y = HEIGHT // 2 - enemy_height // 2
enemy_rect = pygame.Rect(enemy_x, enemy_y, enemy_width, enemy_height)

# Game variables
base_hp = 100
enemy_max_hp = base_hp
enemy_hp = enemy_max_hp
damage_per_click = 10
enemy_count = 1  # Tracks which enemy number we are on

# Font
font = pygame.font.SysFont(None, 36)

def draw_enemy():
    """Draw the enemy and its health bar."""
    pygame.draw.rect(screen, RED, enemy_rect)  # Enemy body

    # Health bar background
    pygame.draw.rect(screen, BLACK, (enemy_x, enemy_y - 20, enemy_width, 10))
    # Health bar foreground
    hp_ratio = enemy_hp / enemy_max_hp
    pygame.draw.rect(screen, GREEN, (enemy_x, enemy_y - 20, enemy_width * hp_ratio, 10))

def draw_text(text, x, y, color=BLACK):
    """Draw text on the screen."""
    img = font.render(text, True, color)
    screen.blit(img, (x, y))

def spawn_new_enemy():
    """Increase difficulty and spawn a new enemy."""
    global enemy_hp, enemy_max_hp, enemy_count
    enemy_count += 1
    enemy_max_hp = base_hp + (enemy_count - 1) * 50  # Increase HP each round
    enemy_hp = enemy_max_hp

# Game loop
while True:
    screen.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Handle mouse clicks
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
            if enemy_rect.collidepoint(event.pos) and enemy_hp > 0:
                enemy_hp -= damage_per_click
                if enemy_hp <= 0:
                    enemy_hp = 0
                    pygame.time.delay(500)  # Small pause before next enemy
                    spawn_new_enemy()

    # Draw enemy and UI
    draw_enemy()
    draw_text(f"Enemy #{enemy_count}", 10, 10)
    draw_text(f"HP: {enemy_hp}/{enemy_max_hp}", 10, 40)

    pygame.display.flip()
    clock.tick(60)  # Limit to 60 FPS

    #Source: Using Copilot as reference