import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Neon Pong")

# Colors (Neon style)
NEON_BLUE = (0, 255, 255)
NEON_PINK = (255, 0, 255)
NEON_RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Game objects
PADDLE_WIDTH = 15
PADDLE_HEIGHT = 90
BALL_SIZE = 10
PADDLE_SPEED = 5
BALL_SPEED = 7

# Powerup settings
POWERUP_SIZE = 20
POWERUP_SPAWN_RATE = 0.02  # Chance of spawning per frame
POWERUP_DURATION = 5000  # 5 seconds in milliseconds

# Initialize game objects
player_paddle = pygame.Rect(50, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
cpu_paddle = pygame.Rect(WIDTH - 50 - PADDLE_WIDTH, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
ball = pygame.Rect(WIDTH // 2 - BALL_SIZE // 2, HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE)
ball_speed_x = BALL_SPEED * random.choice((1, -1))
ball_speed_y = BALL_SPEED * random.choice((1, -1))

# Powerup states
powerups = []
fireball_active = False
fireball_timer = 0
speed_modifier = 1.0
paddle_size_modifier = 1.0
powerup_timer = 0

# Scores
player_score = 0
cpu_score = 0
font = pygame.font.Font(None, 36)

# Create a surface for glowing effect
def create_glow_surface(size, color, alpha=128):
    surf = pygame.Surface((size * 3, size * 3), pygame.SRCALPHA)
    pygame.draw.circle(surf, (*color, alpha), (size * 1.5, size * 1.5), size * 1.5)
    return surf

# Powerup class
class Powerup:
    def __init__(self, x, y, type):
        self.rect = pygame.Rect(x, y, POWERUP_SIZE, POWERUP_SIZE)
        self.type = type  # "fireball", "speed_up", "speed_down", "paddle_increase", "paddle_decrease"

def spawn_powerup():
    if random.random() < POWERUP_SPAWN_RATE:
        x = random.randint(100, WIDTH - 100)
        y = random.randint(100, HEIGHT - 100)
        types = ["fireball", "speed_up", "speed_down", "paddle_increase", "paddle_decrease"]
        powerup_type = random.choice(types)
        powerups.append(Powerup(x, y, powerup_type))

def apply_powerup(powerup):
    global fireball_active, fireball_timer, speed_modifier, paddle_size_modifier, powerup_timer
    powerup_timer = pygame.time.get_ticks()
    
    if powerup.type == "fireball":
        fireball_active = True
        fireball_timer = pygame.time.get_ticks()
    elif powerup.type == "speed_up":
        speed_modifier = 1.5
    elif powerup.type == "speed_down":
        speed_modifier = 0.5
    elif powerup.type == "paddle_increase":
        paddle_size_modifier = 1.5
        player_paddle.height = int(PADDLE_HEIGHT * paddle_size_modifier)
        player_paddle.y = max(0, min(player_paddle.y, HEIGHT - player_paddle.height))
    elif powerup.type == "paddle_decrease":
        paddle_size_modifier = 0.5
        player_paddle.height = int(PADDLE_HEIGHT * paddle_size_modifier)
        player_paddle.y = max(0, min(player_paddle.y, HEIGHT - player_paddle.height))

def reset_powerups():
    global fireball_active, speed_modifier, paddle_size_modifier
    fireball_active = False
    speed_modifier = 1.0
    paddle_size_modifier = 1.0
    player_paddle.height = PADDLE_HEIGHT
    player_paddle.y = HEIGHT // 2 - PADDLE_HEIGHT // 2

# Game loop
clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Player paddle movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP] and player_paddle.top > 0:
        player_paddle.y -= PADDLE_SPEED
    if keys[pygame.K_DOWN] and player_paddle.bottom < HEIGHT:
        player_paddle.y += PADDLE_SPEED

    # CPU paddle movement (simple AI)
    cpu_speed = PADDLE_SPEED * 0.8  # Slightly slower than player
    if cpu_paddle.centery < ball.centery and cpu_paddle.bottom < HEIGHT:
        cpu_paddle.y += cpu_speed
    if cpu_paddle.centery > ball.centery and cpu_paddle.top > 0:
        cpu_paddle.y -= cpu_speed

    # Ball movement
    current_speed_x = ball_speed_x * speed_modifier
    current_speed_y = ball_speed_y * speed_modifier
    ball.x += current_speed_x
    ball.y += current_speed_y

    # Ball collisions with top and bottom
    if ball.top <= 0 or ball.bottom >= HEIGHT:
        ball_speed_y = -ball_speed_y

    # Ball collisions with paddles
    if ball.colliderect(player_paddle) and ball_speed_x < 0:
        ball_speed_x = -ball_speed_x
    if ball.colliderect(cpu_paddle) and ball_speed_x > 0:
        ball_speed_x = -ball_speed_x

    # Ball out of bounds
    if ball.left <= 0:
        cpu_score += 1
        ball.center = (WIDTH // 2, HEIGHT // 2)
        ball_speed_x = BALL_SPEED * random.choice((1, -1))
        ball_speed_y = BALL_SPEED * random.choice((1, -1))
        reset_powerups()
    if ball.right >= WIDTH:
        player_score += 1
        ball.center = (WIDTH // 2, HEIGHT // 2)
        ball_speed_x = BALL_SPEED * random.choice((1, -1))
        ball_speed_y = BALL_SPEED * random.choice((1, -1))
        reset_powerups()

    # Spawn and collect powerups
    spawn_powerup()
    for powerup in powerups[:]:
        if player_paddle.colliderect(powerup.rect):
            apply_powerup(powerup)
            powerups.remove(powerup)

    # Powerup duration
    current_time = pygame.time.get_ticks()
    if fireball_active and current_time - fireball_timer > POWERUP_DURATION:
        fireball_active = False
    if powerup_timer and current_time - powerup_timer > POWERUP_DURATION:
        reset_powerups()

    # Drawing
    screen.fill(BLACK)

    # Draw glowing paddles
    player_glow = create_glow_surface(PADDLE_WIDTH, NEON_BLUE)
    cpu_glow = create_glow_surface(PADDLE_WIDTH, NEON_PINK)
    screen.blit(player_glow, (player_paddle.x - PADDLE_WIDTH, player_paddle.y - (PADDLE_HEIGHT * paddle_size_modifier - PADDLE_WIDTH) // 2))
    screen.blit(cpu_glow, (cpu_paddle.x - PADDLE_WIDTH, cpu_paddle.y - (PADDLE_HEIGHT - PADDLE_WIDTH) // 2))
    pygame.draw.rect(screen, NEON_BLUE, player_paddle)
    pygame.draw.rect(screen, NEON_PINK, cpu_paddle)

    # Draw ball with glow
    ball_color = NEON_RED if fireball_active else WHITE
    ball_glow = create_glow_surface(BALL_SIZE, ball_color)
    screen.blit(ball_glow, (ball.x - BALL_SIZE, ball.y - BALL_SIZE))
    pygame.draw.ellipse(screen, ball_color, ball)

    # Draw powerups
    for powerup in powerups:
        if powerup.type == "fireball":
            pygame.draw.circle(screen, NEON_RED, powerup.rect.center, POWERUP_SIZE // 2)
        elif powerup.type == "speed_up":
            pygame.draw.rect(screen, (0, 255, 0), powerup.rect)
        elif powerup.type == "speed_down":
            pygame.draw.rect(screen, (255, 165, 0), powerup.rect)
        elif powerup.type == "paddle_increase":
            pygame.draw.rect(screen, (0, 255, 255), powerup.rect)
        elif powerup.type == "paddle_decrease":
            pygame.draw.rect(screen, (255, 0, 255), powerup.rect)

    # Draw scores
    player_text = font.render(str(player_score), True, WHITE)
    cpu_text = font.render(str(cpu_score), True, WHITE)
    screen.blit(player_text, (WIDTH // 4, 20))
    screen.blit(cpu_text, (3 * WIDTH // 4, 20))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()