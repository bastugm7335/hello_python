import math
import random
import sys

import pygame
from pygame.locals import K_DOWN, K_LEFT, K_RIGHT, K_UP, K_p, K_r, QUIT


pygame.init()

FPS = 60
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
FramePerSec = pygame.time.Clock()

BLUE = (0, 0, 255)
RED = (255, 55, 55)
GREEN = (40, 180, 90)
BLACK = (20, 20, 30)
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)

DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Road Escape")

try:
    FONT = pygame.font.Font("C:\\Windows\\Fonts\\arial.ttf", 24)
    SMALL_FONT = pygame.font.Font("C:\\Windows\\Fonts\\arial.ttf", 18)
except pygame.error:
    FONT = pygame.font.Font(None, 24)
    SMALL_FONT = pygame.font.Font(None, 18)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, level):
        super().__init__()
        self.image = pygame.image.load("enemy.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.reset(level)

    def reset(self, level):
        self.rect.center = (
            random.randint(35, SCREEN_WIDTH - 35),
            random.randint(-150, -40),
        )
        self.speed = random.randint(4, 7) + level
        self.horizontal_speed = random.choice((-1, 0, 0, 0, 1)) * random.randint(1, 2)

    def update(self, level):
        self.rect.move_ip(self.horizontal_speed, self.speed)

        if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
            self.horizontal_speed *= -1

        if self.rect.top > SCREEN_HEIGHT:
            self.reset(level)
            return True
        return False

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("player.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, 530)
        self.speed = 6
        self.lives = 3
        self.invulnerable_until = 0
        self.shield_until = 0

    def update(self):
        keys = pygame.key.get_pressed()

        if keys[K_LEFT]:
            self.rect.move_ip(-self.speed, 0)
        if keys[K_RIGHT]:
            self.rect.move_ip(self.speed, 0)
        if keys[K_UP]:
            self.rect.move_ip(0, -self.speed)
        if keys[K_DOWN]:
            self.rect.move_ip(0, self.speed)

        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(SCREEN_WIDTH, self.rect.right)
        self.rect.top = max(80, self.rect.top)
        self.rect.bottom = min(SCREEN_HEIGHT, self.rect.bottom)

    def take_hit(self, now):
        if now < self.invulnerable_until:
            return False
        if now < self.shield_until:
            self.invulnerable_until = now + 500
            return False

        self.lives -= 1
        self.invulnerable_until = now + 1500
        return True

    def draw(self, surface, now):
        if now < self.invulnerable_until and (now // 100) % 2 == 0:
            return

        surface.blit(self.image, self.rect)
        if now < self.shield_until:
            pygame.draw.circle(
                surface,
                CYAN,
                self.rect.center,
                max(self.rect.width, self.rect.height) // 2 + 8,
                3,
            )


class Shield(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.radius = 12
        self.rect = pygame.Rect(0, 0, self.radius * 2, self.radius * 2)
        self.reset()

    def reset(self):
        self.rect.center = (
            random.randint(30, SCREEN_WIDTH - 30),
            random.randint(-400, -100),
        )
        self.speed = random.randint(3, 5)

    def update(self):
        self.rect.move_ip(0, self.speed)
        if self.rect.top > SCREEN_HEIGHT:
            self.reset()

    def draw(self, surface, now):
        pulse = 2 + int((now // 150) % 3)
        pygame.draw.circle(surface, CYAN, self.rect.center, self.radius)
        pygame.draw.circle(surface, WHITE, self.rect.center, self.radius - pulse, 3)


def draw_background(surface, elapsed):
    surface.fill((35, 95, 55))

    road_left = 95
    road_right = 305
    pygame.draw.polygon(
        surface,
        (105, 105, 115),
        [
            (road_left, 0),
            (road_right, 0),
            (road_right, SCREEN_HEIGHT),
            (road_left, SCREEN_HEIGHT),
        ],
    )
    pygame.draw.line(surface, WHITE, (road_left, 0), (road_left, SCREEN_HEIGHT), 4)
    pygame.draw.line(surface, WHITE, (road_right, 0), (road_right, SCREEN_HEIGHT), 4)

    road_scroll = (elapsed // 8) % 40
    for y in range(-40 + road_scroll, SCREEN_HEIGHT, 40):
        pygame.draw.line(
            surface,
            (190, 190, 200),
            (SCREEN_WIDTH // 2, y),
            (SCREEN_WIDTH // 2, y + 20),
            3,
        )

    def draw_pine(x, y, scale):
        trunk_rect = pygame.Rect(x - 4 * scale, y - 2 * scale, 8 * scale, 22 * scale)
        pygame.draw.rect(surface, (90, 55, 35), trunk_rect)

        for offset, width in ((-34, 30), (-25, 38), (-16, 46)):
            top_y = y + offset * scale
            bottom_y = top_y + 38 * scale
            pygame.draw.polygon(
                surface,
                (18, 95 + 30 * (width // 38), 55),
                [
                    (x, top_y),
                    (x - width * scale, bottom_y),
                    (x + width * scale, bottom_y),
                ],
            )

    scroll = (elapsed // 5) % 110
    left_positions = [32, 72]
    right_positions = [328, 368]
    for row in range(-1, 7):
        y = row * 110 + scroll
        offset = (row % 2) * 18
        for x in left_positions:
            draw_pine(x + offset, y, 0.65)
        for x in right_positions:
            draw_pine(x - offset, y, 0.65)

    def draw_rabbit(x, y, direction):
        body_color = (235, 225, 200)
        head_x = x + direction * 8
        pygame.draw.ellipse(surface, body_color, (x - 11, y - 9, 20, 12))
        pygame.draw.ellipse(surface, body_color, (head_x - 5, y - 16, 12, 12))
        pygame.draw.ellipse(surface, body_color, (x - 16, y - 7, 8, 8))
        pygame.draw.line(
            surface, body_color, (head_x - 2, y - 14), (head_x - 4, y - 27), 4
        )
        pygame.draw.line(
            surface,
            body_color,
            (head_x + 2, y - 14),
            (head_x + 5, y - 26),
            4,
        )
        eye_x = head_x + direction * 2
        pygame.draw.circle(surface, BLACK, (eye_x, y - 12), 1)
        pygame.draw.line(surface, body_color, (x - 5, y), (x - 9, y + 3), 2)
        pygame.draw.line(surface, body_color, (x + 5, y), (x + 9, y + 3), 2)

    rabbit_phase = (elapsed // 25) % 130
    if rabbit_phase <= 65:
        rabbit_x = 12 + rabbit_phase
        rabbit_direction = 1
    else:
        rabbit_x = 12 + 130 - rabbit_phase
        rabbit_direction = -1
    rabbit_hop = int(abs(math.sin(elapsed / 140)) * 8)
    draw_rabbit(rabbit_x, SCREEN_HEIGHT - 85 - rabbit_hop, rabbit_direction)


def draw_hud(surface, score, lives, level, shield_until, now):
    surface.blit(FONT.render(f"Score: {score}", True, WHITE), (12, 12))
    surface.blit(SMALL_FONT.render(f"Level: {level}", True, CYAN), (300, 16))
    surface.blit(SMALL_FONT.render("Lives: " + " " .join(["+"] * lives), True, RED), (12, 45))

    if now < shield_until:
        seconds = (shield_until - now) // 1000 + 1
        surface.blit(SMALL_FONT.render(f"Shield: {seconds}s", True, CYAN), (270, 45))


def show_game_over(surface, score):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 210))
    surface.blit(overlay, (0, 0))

    title = FONT.render("GAME OVER", True, RED)
    final_score = FONT.render(f"Final score: {score}", True, WHITE)
    restart = SMALL_FONT.render("Press R to restart", True, CYAN)
    surface.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 250)))
    surface.blit(final_score, final_score.get_rect(center=(SCREEN_WIDTH // 2, 300)))
    surface.blit(restart, restart.get_rect(center=(SCREEN_WIDTH // 2, 350)))


def reset_game():
    player = Player()
    enemies = [Enemy(1) for _ in range(3)]
    shield = Shield()
    return player, enemies, shield, 0, 1, pygame.time.get_ticks()


P1, enemies, shield, score, level, started_at = reset_game()
paused = False
game_over = False

spawn_timer = 0

while True:
    now = pygame.time.get_ticks()
    elapsed = now - started_at

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == K_p:
                paused = not paused
            if event.key == K_r and game_over:
                P1, enemies, shield, score, level, started_at = reset_game()
                spawn_timer = 0
                paused = False
                game_over = False

    if not paused and not game_over:
        P1.update()
        level = 1 + score // 500

        spawn_timer += 1
        target_enemy_count = min(3 + level, 8)
        if spawn_timer >= max(25, 70 - level * 5) and len(enemies) < target_enemy_count:
            enemies.append(Enemy(level))
            spawn_timer = 0

        for enemy in enemies:
            if enemy.update(level):
                score += 10

        shield.update()

        for enemy in enemies:
            if P1.rect.colliderect(enemy.rect):
                if P1.take_hit(now):
                    enemy.reset(level)
                if P1.lives <= 0:
                    game_over = True

        if P1.rect.colliderect(shield.rect):
            P1.shield_until = now + 5000
            shield.reset()

    draw_background(DISPLAYSURF, elapsed)
    for enemy in enemies:
        enemy.draw(DISPLAYSURF)
    shield.draw(DISPLAYSURF, now)
    P1.draw(DISPLAYSURF, now)
    draw_hud(DISPLAYSURF, score, P1.lives, level, P1.shield_until, now)

    if paused:
        pause_text = FONT.render("PAUSED", True, CYAN)
        DISPLAYSURF.blit(pause_text, pause_text.get_rect(center=(200, 300)))
    if game_over:
        show_game_over(DISPLAYSURF, score)

    pygame.display.update()
    FramePerSec.tick(FPS)
