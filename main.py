import pygame
import random
import sys
import os
os.environ['SDL_AUDIODRIVER'] = 'dummy'
pygame.init()

WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Neon Pong")

NEON_BLUE = (0, 255, 255)
NEON_PINK = (255, 0, 255)
NEON_RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

PADDLE_WIDTH = 15
PADDLE_HEIGHT = 90
BALL_SIZE = 10
PADDLE_SPEED = 7
BALL_SPEED = 4

POWERUP_SIZE = 20
POWERUP_SPAWN_RATE = 0.001  # Much less frequent
POWERUP_DURATION = 5000

player_paddle = pygame.Rect(50, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
cpu_paddle = pygame.Rect(WIDTH - 50 - PADDLE_WIDTH, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
ball = pygame.Rect(WIDTH // 2 - BALL_SIZE // 2, HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE)
ball_speed_x = BALL_SPEED * random.choice((1, -1))
ball_speed_y = BALL_SPEED * random.choice((1, -1))

powerups = []
fireball_active = False
fireball_timer = 0
speed_modifier = 1.0
paddle_size_modifier = 1.0
powerup_timer = 0

cpu_miss_chance = 0.1
cpu_miss_increment = 0.01 
cpu_miss_max = 0.50  

player_score = 0
cpu_score = 0
font = pygame.font.Font(None, 36)
big_font = pygame.font.Font(None, 72)

def create_glow_surface(size, color, alpha=128):
    surf = pygame.Surface((size * 3, size * 3), pygame.SRCALPHA)
    pygame.draw.circle(surf, (*color, alpha), (size * 1.5, size * 1.5), size * 1.5)
    return surf

class Powerup:
    def __init__(self, x, y, type):
        self.rect = pygame.Rect(x, y, POWERUP_SIZE, POWERUP_SIZE)
        self.type = type

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

def draw_main_menu():
    screen.fill(BLACK)
    title = big_font.render("Neon Pong", True, NEON_BLUE)
    start_text = font.render("Press ENTER to Start", True, WHITE)
    quit_text = font.render("Press Q to Quit", True, WHITE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 3))
    screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, HEIGHT // 2))
    screen.blit(quit_text, (WIDTH // 2 - quit_text.get_width() // 2, HEIGHT // 2 + 50))
    pygame.display.flip()

def draw_pause():
    pause_text = big_font.render("Paused", True, NEON_PINK)
    screen.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT // 2 - pause_text.get_height() // 2))
    pygame.display.flip()

clock = pygame.time.Clock()
running = True
paused = False
in_menu = True

while running:
    if in_menu:
        draw_main_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    in_menu = False
                if event.key == pygame.K_q:
                    running = False
        continue

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                paused = not paused

    if paused:
        draw_pause()
        while paused:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    paused = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        paused = False
            clock.tick(10)
        continue

    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP] and player_paddle.top > 0:
        player_paddle.y -= PADDLE_SPEED
    if keys[pygame.K_DOWN] and player_paddle.bottom < HEIGHT:
        player_paddle.y += PADDLE_SPEED

    cpu_speed = PADDLE_SPEED * 0.8
    if cpu_paddle.centery < ball.centery and cpu_paddle.bottom < HEIGHT:
        if ball_speed_x > 0 and random.random() < cpu_miss_chance:
            pass  
        else:
            cpu_paddle.y += cpu_speed
    if cpu_paddle.centery > ball.centery and cpu_paddle.top > 0:
        if ball_speed_x > 0 and random.random() < cpu_miss_chance:
            pass
        else:
            cpu_paddle.y -= cpu_speed

    current_speed_x = ball_speed_x * speed_modifier
    current_speed_y = ball_speed_y * speed_modifier
    ball.x += current_speed_x
    ball.y += current_speed_y

    if ball_speed_x > 0:
        cpu_miss_chance = min(cpu_miss_max, cpu_miss_chance + cpu_miss_increment)
    else:
        cpu_miss_chance = max(0.0, cpu_miss_chance - cpu_miss_increment)

    if ball.top <= 0 or ball.bottom >= HEIGHT:
        ball_speed_y = -ball_speed_y

    if ball.colliderect(player_paddle) and ball_speed_x < 0:
        ball_speed_x = -ball_speed_x
    if ball.colliderect(cpu_paddle) and ball_speed_x > 0:
        ball_speed_x = -ball_speed_x

    if ball.left <= 0:
        cpu_score += 1
        pygame.display.flip()
        pygame.time.delay(600)  # Pause to show score
        ball.center = (WIDTH // 2, HEIGHT // 2)
        ball_speed_x = BALL_SPEED * random.choice((1, -1))
        ball_speed_y = BALL_SPEED * random.choice((1, -1))
        cpu_miss_chance = 0.0

    if ball.right >= WIDTH:
        player_score += 1
        pygame.display.flip()
        pygame.time.delay(600)
        ball.center = (WIDTH // 2, HEIGHT // 2)
        ball_speed_x = BALL_SPEED * random.choice((1, -1))
        ball_speed_y = BALL_SPEED * random.choice((1, -1))

    spawn_powerup()
    for powerup in powerups[:]:
        if player_paddle.colliderect(powerup.rect):
            apply_powerup(powerup)
            powerups.remove(powerup)

    current_time = pygame.time.get_ticks()
    if fireball_active and current_time - fireball_timer > POWERUP_DURATION:
        fireball_active = False
    if powerup_timer and current_time - powerup_timer > POWERUP_DURATION:
        reset_powerups()

    screen.fill(BLACK)
    pygame.draw.rect(screen, NEON_BLUE, player_paddle)
    pygame.draw.rect(screen, NEON_PINK, cpu_paddle)
    ball_color = NEON_RED if fireball_active else WHITE
    pygame.draw.ellipse(screen, ball_color, ball)

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

    player_text = font.render(str(player_score), True, WHITE)
    cpu_text = font.render(str(cpu_score), True, WHITE)
    screen.blit(player_text, (WIDTH // 4, 20))
    screen.blit(cpu_text, (3 * WIDTH // 4, 20))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()