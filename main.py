import pygame
import random
import sys
import os
# --- os.environ['SDL_AUDIODRIVER'] = 'dummy' ---
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
POWERUP_SIZE = 32  # Increased from 20

fireball_trail = []  # List of (x, y, timestamp)
FIREBALL_DOT_LIFETIME = 500
FIREBALL_TRAIL_SPACING = 16

NUM_LEVELS = 10
level_unlocks = [True] + [False] * (NUM_LEVELS - 1)
current_level = None
level_score_targets = [10 + 5 * i for i in range(NUM_LEVELS)]
level_selecting = False

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
active_powerup = None  
powerup_effect_duration = 20000  
powerup_on_screen = False

cpu_miss_chance = 0.1
cpu_miss_increment = 0.01 
cpu_miss_max = 0.50  
cpu_speed_modifier = 1.0

player_score = 0
cpu_score = 0
font = pygame.font.Font(None, 36)
big_font = pygame.font.Font(None, 72)

level_select_cursor = 0  # For keyboard navigation

def create_glow_surface(size, color, alpha=128):
    surf = pygame.Surface((size * 3, size * 3), pygame.SRCALPHA)
    pygame.draw.circle(surf, (*color, alpha), (size * 1.5, size * 1.5), size * 1.5)
    return surf

class Powerup:
    def __init__(self, x, y, type):
        self.rect = pygame.Rect(x, y, POWERUP_SIZE, POWERUP_SIZE)
        self.type = type

def spawn_powerup():
    global powerup_on_screen
    if len(powerups) < 2 and random.random() < POWERUP_SPAWN_RATE:
        x = random.randint(100, WIDTH - 100)
        y = random.randint(100, HEIGHT - 100)
        types = ["fireball", "speed_modifier", "paddle_size"]
        powerup_type = random.choice(types)
        powerups.append(Powerup(x, y, powerup_type))

def apply_powerup(powerup):
    global fireball_active, fireball_timer, speed_modifier, paddle_size_modifier, powerup_timer, active_powerup
    powerup_timer = pygame.time.get_ticks()
    active_powerup = powerup.type
    if powerup.type == "fireball":
        fireball_active = True
        fireball_timer = pygame.time.get_ticks()
    elif powerup.type == "speed_modifier":
        speed_modifier = 1.2
        cpu_speed_modifier = 0.8
    elif powerup.type == "paddle_size":
        paddle_size_modifier = 1.5
        player_paddle.height = int(PADDLE_HEIGHT * paddle_size_modifier)
        cpu_paddle.height = int(PADDLE_HEIGHT * 0.7)
        player_paddle.y = max(0, min(player_paddle.y, HEIGHT - player_paddle.height))
        cpu_paddle.y = max(0, min(cpu_paddle.y, HEIGHT - cpu_paddle.height))

def reset_powerups():
    global fireball_active, speed_modifier, paddle_size_modifier
    fireball_active = False
    speed_modifier = 1.0
    paddle_size_modifier = 1.0
    player_paddle.height = PADDLE_HEIGHT
    player_paddle.y = HEIGHT // 2 - PADDLE_HEIGHT // 2

def draw_level_select():
    screen.fill(BLACK)
    title = big_font.render("Select Level", True, NEON_BLUE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 40))
    grid_margin = 60
    grid_spacing_x = (WIDTH - 2 * grid_margin) // 5
    grid_spacing_y = 80
    button_width = 110
    button_height = 60
    for i in range(NUM_LEVELS):
        col = i % 5
        row = i // 5
        x = grid_margin + col * grid_spacing_x
        y = 150 + row * grid_spacing_y
        rect = pygame.Rect(x, y, button_width, button_height)
        color = (0, 255, 0) if level_unlocks[i] else (100, 100, 100)
        pygame.draw.rect(screen, color, rect, border_radius=10)
        stage_font = pygame.font.Font(None, 28)
        level_text = stage_font.render(f"Stage {i+1}", True, BLACK if level_unlocks[i] else WHITE)
        screen.blit(level_text, (x + button_width // 2 - level_text.get_width() // 2, y + 6))
        if i == level_select_cursor:
            pygame.draw.rect(screen, NEON_PINK, rect, 3, border_radius=10)
    pygame.display.flip()
    pygame.display.flip()

def get_level_clicked(pos):
    grid_margin = 60
    grid_spacing_x = (WIDTH - 2 * grid_margin) // 5
    grid_spacing_y = 80
    button_width = 110
    button_height = 60
    for i in range(NUM_LEVELS):
        col = i % 5
        row = i // 5
        x = grid_margin + col * grid_spacing_x
        y = 150 + row * grid_spacing_y
        rect = pygame.Rect(x, y, button_width, button_height)
        if rect.collidepoint(pos):
            return i
    return None

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
                    level_selecting = True
                    in_menu = False
                if event.key == pygame.K_q:
                    running = False
        continue

    if level_selecting:
        draw_level_select()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                idx = get_level_clicked(event.pos)
                if idx is not None and level_unlocks[idx]:
                    current_level = idx
                    player_score = 0
                    cpu_score = 0
                    level_selecting = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    if level_select_cursor < NUM_LEVELS - 1:
                        level_select_cursor += 1
                if event.key == pygame.K_LEFT:
                    if level_select_cursor > 0:
                        level_select_cursor -= 1
                if event.key == pygame.K_UP:
                    if level_select_cursor - 5 >= 0:
                        level_select_cursor -= 5
                if event.key == pygame.K_DOWN:
                    if level_select_cursor + 5 < NUM_LEVELS:
                        level_select_cursor += 5
                if event.key == pygame.K_RETURN:
                    if level_unlocks[level_select_cursor]:
                        current_level = level_select_cursor
                        player_score = 0
                        cpu_score = 0
                        level_selecting = False
        if level_selecting:
            continue

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                paused = not paused
            if event.key == pygame.K_f and not active_powerup:
                apply_powerup(Powerup(ball.x, ball.y, "fireball"))
            if event.key == pygame.K_e and not active_powerup:
                apply_powerup(Powerup(ball.x, ball.y, "paddle_size"))
            if event.key == pygame.K_s and not active_powerup:
                apply_powerup(Powerup(ball.x, ball.y, "speed_modifier"))

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
        player_paddle.y -= int(PADDLE_SPEED * speed_modifier)
    if keys[pygame.K_DOWN] and player_paddle.bottom < HEIGHT:
        player_paddle.y += int(PADDLE_SPEED * speed_modifier)

    cpu_speed = PADDLE_SPEED * 0.8 * cpu_speed_modifier
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

    # Fireball trail logic: add dot after moving ball
    if fireball_active:
        if (
        len(fireball_trail) == 0 or
        (abs(ball.x + BALL_SIZE // 2 - fireball_trail[-1][0]) > FIREBALL_TRAIL_SPACING or
         abs(ball.y + BALL_SIZE // 2 - fireball_trail[-1][1]) > FIREBALL_TRAIL_SPACING)
    ):
            fireball_trail.append((ball.x + BALL_SIZE // 2, ball.y + BALL_SIZE // 2, pygame.time.get_ticks()))

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
        pygame.time.delay(600)
        ball.center = (WIDTH // 2, HEIGHT // 2)
        ball_speed_x = BALL_SPEED * random.choice((1, -1))
        ball_speed_y = BALL_SPEED * random.choice((1, -1))
        cpu_miss_chance = 0.0

    if cpu_score >= 10 and player_score < level_score_targets[current_level]:
        msg = big_font.render("Game Over", True, (255, 0, 0))
        screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2 - msg.get_height() // 2))
        pygame.display.flip()
        pygame.time.delay(1500)
        level_selecting = True
        current_level = None
        in_menu = False
        continue

    if ball.right >= WIDTH:
        player_score += 1
        pygame.display.flip()
        pygame.time.delay(600)
        if player_score >= level_score_targets[current_level]:
            if current_level + 1 < NUM_LEVELS:
                level_unlocks[current_level + 1] = True
            msg = big_font.render("Level Complete!", True, (0, 255, 0))
            screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2 - msg.get_height() // 2))
            pygame.display.flip()
            pygame.time.delay(1500)
            level_selecting = True
            current_level = None
            in_menu = False
            continue
        ball.center = (WIDTH // 2, HEIGHT // 2)
        ball_speed_x = BALL_SPEED * random.choice((1, -1))
        ball_speed_y = BALL_SPEED * random.choice((1, -1))

    spawn_powerup()
    for powerup in powerups[:]:
        if ball.colliderect(powerup.rect):
            apply_powerup(powerup)
            powerups.remove(powerup)
            powerup_on_screen = False

    current_time = pygame.time.get_ticks()
    # Reset powerups and clear fireball trail when effect ends
    if active_powerup and current_time - powerup_timer > powerup_effect_duration:
        fireball_active = False
        speed_modifier = 1.0
        cpu_speed_modifier = 1.0
        paddle_size_modifier = 1.0
        player_paddle.height = PADDLE_HEIGHT
        cpu_paddle.height = PADDLE_HEIGHT
        player_paddle.y = max(0, min(player_paddle.y, HEIGHT - player_paddle.height))
        cpu_paddle.y = max(0, min(cpu_paddle.y, HEIGHT - cpu_paddle.height))
        fireball_trail.clear()
        active_powerup = None

    screen.fill(BLACK)
    pygame.draw.rect(screen, NEON_BLUE, player_paddle)
    pygame.draw.rect(screen, NEON_PINK, cpu_paddle)
    ball_color = NEON_RED if fireball_active else WHITE
    pygame.draw.ellipse(screen, ball_color, ball)

    # Draw persistent, fading fireball trail
    now = pygame.time.get_ticks()
    for dot in fireball_trail[:]:
        age = now - dot[2]
        if age > FIREBALL_DOT_LIFETIME:
            fireball_trail.remove(dot)
        else:
            alpha = max(0, 255 - int(255 * (age / FIREBALL_DOT_LIFETIME)))
            dot_surface = pygame.Surface((BALL_SIZE, BALL_SIZE), pygame.SRCALPHA)
            pygame.draw.circle(dot_surface, (255, 69, 0, alpha), (BALL_SIZE // 2, BALL_SIZE // 2), BALL_SIZE // 2)
            screen.blit(dot_surface, (dot[0] - BALL_SIZE // 2, dot[1] - BALL_SIZE // 2))

    for powerup in powerups:
        if powerup.type == "fireball":
            pygame.draw.circle(screen, NEON_RED, powerup.rect.center, POWERUP_SIZE // 2)
        elif powerup.type == "speed_modifier":
            pygame.draw.rect(screen, (0, 255, 0), powerup.rect)
        elif powerup.type == "paddle_size":
            pygame.draw.rect(screen, (0, 255, 255), powerup.rect)

    player_text = font.render(str(player_score), True, WHITE)
    if active_powerup == "fireball":
        powerup_text = font.render("FIREBALL", True, NEON_RED)
    elif active_powerup == "speed_modifier":
        powerup_text = font.render("SPEED UP", True, (0, 255, 0))
    elif active_powerup == "paddle_size":
        powerup_text = font.render("PADDLE SIZE", True, (0, 255, 255))
    else:
        powerup_text = font.render("", True, WHITE)
    screen.blit(powerup_text, (WIDTH // 2 - powerup_text.get_width() // 2, 20))
    cpu_text = font.render(str(cpu_score), True, WHITE)
    screen.blit(player_text, (WIDTH // 4, 20))
    screen.blit(cpu_text, (3 * WIDTH // 4, 20))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()