import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 960, 512
FPS = 100
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
VOID_BLACK = (5, 0, 25)

# Setup screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("SpaceFighter")
clock = pygame.time.Clock()
bg_nebula = pygame.image.load("nebula.jpg").convert()
bg_nebula = pygame.transform.scale(bg_nebula, (SCREEN_WIDTH * 1.5, SCREEN_HEIGHT * 1.5))

scroll_speed = 0.7
score = 0
ui_font = pygame.font.SysFont("Arial", 32)


# Spaceship class
class Spaceship:
    def __init__(self):
        self.image = pygame.Surface((50, 40))
        self.image.fill((0, 0, 0))
        self.shoot_sound = pygame.mixer.Sound("laser.mp3")
        self.shoot_sound.set_volume(0.3)
        self.invulnerable = True
        self.spawnedat = pygame.time.get_ticks()
        self.everysecond = True
        self.rect = self.image.get_rect(center=(100, SCREEN_HEIGHT // 2))
        self.lives = 3
        self.energy = 100
        self.weapon_level = 1
        self.shot_delay = 500
        self.last_shot = 0
        self.spaceship_pics = []
        self.spaceship_pics.append(pygame.image.load("ship1.png").convert_alpha())
        self.spaceship_pics.append(pygame.image.load("ship2.png").convert_alpha())
        self.spaceship_pics.append(pygame.image.load("ship3.png").convert_alpha())
        self.spaceship_pics.append(pygame.image.load("ship4.png").convert_alpha())
        self.spaceship_pics.append(pygame.image.load("ship5.png").convert_alpha())
        for i in range(5):
            self.spaceship_pics[i] = pygame.transform.scale(self.spaceship_pics[i], (60, 60))

    def move(self, keys):
        if keys[pygame.K_w] and self.rect.top > 0:
            self.rect.y -= 5
        if keys[pygame.K_s] and self.rect.bottom < SCREEN_HEIGHT:
            self.rect.y += 5
        if keys[pygame.K_a] and self.rect.left > 0:
            self.rect.x -= 5
        if keys[pygame.K_d] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += 5
        if self.rect.center[0] - 5 <= pygame.mouse.get_pos()[0]:
            self.rect.x += 5
        if self.rect.center[0] + 5 >= pygame.mouse.get_pos()[0]:
            self.rect.x -= 5
        if self.rect.center[1] - 5 <= pygame.mouse.get_pos()[1]:
            self.rect.y += 5
        if self.rect.center[1] + 5 >= pygame.mouse.get_pos()[1]:
            self.rect.y -= 5

    def shoot(self, bullets):
        self.shot_delay = 800 - 60 * self.weapon_level
        if pygame.time.get_ticks() > self.last_shot + self.shot_delay:
            if not self.everysecond:
                self.last_shot = pygame.time.get_ticks()
            else:
                self.last_shot = pygame.time.get_ticks() - 500 + self.weapon_level * 40
            self.everysecond = not self.everysecond

            bullets.append(Bullet(self.rect.centerx, self.rect.centery))
            self.shoot_sound.play()
        if self.invulnerable and pygame.time.get_ticks() > self.spawnedat + 5000:
            self.invulnerable = False

    def respawn(self):
        self.rect.center = (100, SCREEN_HEIGHT // 2)
        self.weapon_level = max(1, self.weapon_level - 1)
        self.spawnedat = pygame.time.get_ticks()
        self.invulnerable = True

    def draw(self):
        i = int(pygame.time.get_ticks() / 20) % 5
        screen.blit(self.spaceship_pics[i], (self.rect.left, self.rect.top - 9))
        if self.invulnerable:
            pygame.draw.circle(screen, (70, 70, 250), self.rect.center, 40, 5)


# Bullet class
class Bullet:
    def __init__(self, x, y):
        self.image = pygame.Surface((20, 25))
        self.image.fill((255, 255, 0))
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 10
        self.image = pygame.image.load("bullet.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (25, 25))

    def update(self):
        self.rect.x += self.speed
        return self.rect.right > 0

    def draw(self):
        screen.blit(self.image, self.rect)


# Meteor class
class Meteor:
    def __init__(self, x, y):
        self.posx = x
        self.image = pygame.Surface((60, 60))
        self.image.fill((128, 128, 128))
        self.rect = self.image.get_rect(center=(x, y))
        self.maxhp = 10
        self.hitpoints = self.maxhp
        self.image = pygame.image.load("rock.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (55, 50))
        self.image = pygame.transform.rotate(self.image, random.randint(0, 359))
        self.rect = self.image.get_rect(center=(x, y))
        self.rect2 = self.image.get_rect(center=(x, y))
        self.rect.y += 10
        self.rect.width -= 30
        self.rect.height -= 20

    def update(self):
        self.posx -= scroll_speed
        self.rect.x = int(self.posx + 10)
        self.rect2.x = int(self.posx)
        return self.rect.right > 0

    def hit(self, hit):
        self.hitpoints -= hit
        alpha = int(125 + 130 * self.hitpoints / self.maxhp)
        self.image.set_alpha(alpha)

    def draw(self):
        screen.blit(self.image, self.rect2)


# Enemy class
class Enemy:
    def __init__(self, x, y, hitpoints, enemy_type, weapon, potential_drop):
        self.posx = x
        self.posy = y
        self.hitpoints = hitpoints
        self.type = enemy_type
        self.weapon = weapon
        self.potential_drop = potential_drop
        self.last_shot = pygame.time.get_ticks()
        self.explosion_sound = pygame.mixer.Sound("pop.wav")
        if enemy_type == 1:
            self.image = pygame.image.load("enemy1.png")
            self.image.convert_alpha()
            self.image = pygame.transform.scale(self.image, (60, 60))
            self.image = pygame.transform.rotate(self.image, random.randint(0, 359))
            self.rect = self.image.get_rect(center=(int(x), int(y)))
            cx, cy = 45, 56
            self.collision_rect = pygame.Rect(self.rect.centerx - cx // 2, self.rect.centery - cy // 2, cx, cy)
        elif enemy_type == 2:
            self.image = pygame.image.load("enemy2.png")
            self.image.convert_alpha()
            self.image = pygame.transform.scale(self.image, (80, 80))
            self.image = pygame.transform.rotate(self.image, random.randint(0, 359))
            self.rect = self.image.get_rect(center=(int(x), int(y)))
            cx, cy = 65, 70
            self.collision_rect = pygame.Rect(self.rect.centerx - cx // 2, self.rect.centery - cy // 2, cx, cy)
        elif enemy_type == 3:
            self.image = pygame.image.load("enemy3.png")
            self.image.convert_alpha()
            self.image = pygame.transform.scale(self.image, (75, 60))
            self.rect = self.image.get_rect(center=(int(x), int(y)))
            cx, cy = 52, 56
            self.collision_rect = pygame.Rect(self.rect.centerx - cx // 2, self.rect.centery - cy // 2, cx, cy)
        elif enemy_type == 4:
            self.image = pygame.image.load("enemy4.png")
            self.image.convert_alpha()
            self.image = pygame.transform.scale(self.image, (60, 80))
            self.rect = self.image.get_rect(center=(int(x), int(y)))
            cx, cy = 45, 76
            self.collision_rect = pygame.Rect(self.rect.centerx - cx // 2, self.rect.centery - cy // 2, cx, cy)
        else:
            self.image = pygame.image.load("enemy3.png")

    def update(self):
        self.posx -= scroll_speed
        self.rect.x = int(self.posx)
        self.rect.y = int(self.posy)
        self.collision_rect.center = self.rect.center
        return self.rect.right > 0

    def shoot(self, enemy_bullets):
        if random.randint(1, 600) == 7 and self.last_shot + 300 < pygame.time.get_ticks():
            enemy_bullets.append(EnemyBullet(self.rect.left, self.rect.centery))
            self.last_shot = pygame.time.get_ticks()

    def draw(self):
        screen.blit(self.image, self.rect)
        pygame.draw.rect(screen, (0, 255, 0), self.collision_rect, 2)

    def destroy(self):
        if self.potential_drop is not None:
            bonuses.append(Bonus(self.rect.centerx, self.rect.centery, bonus_type=self.potential_drop))
        self.explosion_sound.play()


# EnemyBullet class
class EnemyBullet:
    def __init__(self, x, y):
        self.image = pygame.Surface((20, 20))
        self.image.fill((255, 0, 255))
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 3
        self.image = pygame.image.load("enemy_bullet.png").convert_alpha()

        self.image = pygame.transform.scale(self.image, (20, 20))

    def update(self):
        self.rect.x -= self.speed
        return self.rect.left > 0

    def draw(self):
        screen.blit(self.image, self.rect)


# Bonus class
class Bonus:
    def __init__(self, x, y, bonus_type):
        self.image = pygame.Surface((40, 40))
        self.image.fill((0, 0, 255))
        self.rect = self.image.get_rect(center=(x, y))
        self.bonus_type = bonus_type
        self.spawn_time = pygame.time.get_ticks()
        self.timetolive = 10000
        self.killtime = self.spawn_time + self.timetolive
        self.posx = x
        if bonus_type == "weapon":
            self.r = 150
            self.g = 150
            self.b = 150
        elif bonus_type == "life":
            self.r = 0
            self.g = 255
            self.b = 0
        elif bonus_type == "invulnerability":
            self.r = 0
            self.g = 0
            self.b = 255
        elif bonus_type == "speedup":
            self.r = 255
            self.g = 255
            self.b = 0
        else:
            self.r = 255
            self.g = 255
            self.b = 255
        self.rtemp = self.r
        self.gtemp = self.g
        self.btemp = self.b
        self.dim = 1.0

    def update(self):
        self.posx -= scroll_speed
        self.rect.x = self.posx
        if self.rect.right < 0:
            bonuses.remove(self)

        return self.rect.right > 0

    def draw(self):
        t = 1.0
        dim = 1
        if self.killtime - pygame.time.get_ticks() < 2000:
            t = self.killtime - pygame.time.get_ticks() / 400
            dim = max((self.killtime - pygame.time.get_ticks()) / 2000, 0.3)
            self.rtemp = int(self.r * max(0.3, abs(math.sin(t))) * dim)
            self.gtemp = int(self.g * max(0.3, abs(math.sin(t))) * dim)
            self.btemp = int(self.b * max(0.3, abs(math.sin(t))) * dim)
        self.color = (self.rtemp, self.gtemp, self.btemp)
        pygame.draw.circle(screen, self.color, self.rect.center, 20)

        # screen.blit(self.image, self.rect)


# background stars class
class Star:
    def __init__(self):
        self.size = random.randint(1, 2)
        self.color = (255 - self.size * 50, 255 - self.size * 50, 255 - self.size * 50)
        self.x = random.randint(0, SCREEN_WIDTH + 3)
        self.y = random.randint(-2, SCREEN_HEIGHT + 2)
        self.image = pygame.draw.circle(screen, self.color, (self.x, self.y), self.size)

    def update(self):
        self.x -= scroll_speed / 3
        if self.x <= -4:
            self.x = SCREEN_WIDTH + 3
            self.y = random.randint(-2, SCREEN_HEIGHT + 2)
        return True

    def draw(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.size)
        return True


# Spawner class
class Spawner:
    def __init__(self, meteor_list, enemy_list):
        self.meteor_list = meteor_list
        self.enemy_list = enemy_list
        self.last_spawn_time = 0

    def spawn(self, meteors, enemies):
        current_time = pygame.time.get_ticks()
        # Spawn meteors
        for m in self.meteor_list:
            if current_time >= m["t"]:
                meteors.append(Meteor(SCREEN_WIDTH, m["y"] * SCREEN_HEIGHT / 100))
                self.meteor_list.remove(m)
        # Spawn enemies
        for e in self.enemy_list:
            if current_time >= e["t"]:
                enemies.append(
                    Enemy(SCREEN_WIDTH, e["y"] * SCREEN_HEIGHT / 100, e["hp"], e["k"], e["w"], e["b"])
                )  # Time, Y-position, HP, Kind, Weapon, Bonus

                self.enemy_list.remove(e)


# Main game loop
spaceship = Spaceship()
bullets = []
meteors = []
enemies = []
enemy_bullets = []
bonuses = []
backgroundstars = []
meteor_list = []
for i in range(555):
    meteor_list.append({"t": 2000 + i * 5000, "y": random.randint(0, 19) * 5})

enemy_list = []

# Create waves of enemies
for wave in range(500):
    start_time = 5000 + wave * 25000  # Each wave starts 10 seconds apart
    enemy_type_in_wave = random.randint(1, 4)
    for i in range(5):  # 5 enemies per wave
        if random.random() >= 0.5:
            kind = None
        else:
            kind = random.choice(["weapon", "life", "invulnerability"])
        enemy_list.append(
            {
                "t": start_time + i * 1500,  # Spawn each enemy 1 second apart
                "y": random.randint(1, 18) * 5,
                "hp": 3,
                "k": enemy_type_in_wave,
                "w": 1,
                "b": kind,
            }
        )


spawner = Spawner(meteor_list, enemy_list)

for i in range(300):
    backgroundstars.append(Star())

running = True
while running:
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_SPACE:
                if spaceship.weapon_level < 10:
                    spaceship.weapon_level += 1

    # Update spaceship
    spaceship.move(keys)
    spaceship.shoot(bullets)

    # Update bullets
    bullets = [b for b in bullets if b.update()]
    enemy_bullets = [eb for eb in enemy_bullets if eb.update()]

    # Spawn meteors and enemies
    spawner.spawn(meteors, enemies)

    # Update meteors and enemies
    meteors = [m for m in meteors if m.update()]
    enemies = [e for e in enemies if e.update()]

    # update/draw stars
    backgroundstars = [s for s in backgroundstars if s.update()]

    # update bonnuses
    bonuses = [bo for bo in bonuses if bo.update()]

    # Check collisions
    for bullet in bullets[:]:
        for enemy in enemies[:]:
            if bullet.rect.colliderect(enemy.collision_rect):
                enemy.hitpoints -= 1
                bullets.remove(bullet)
                if enemy.hitpoints <= 0:
                    enemy.destroy()
                    enemies.remove(enemy)
                    score += 100
        for meteor in meteors[:]:
            if bullet.rect.colliderect(meteor.rect):
                meteor.hit(1)
                if bullet in bullets:
                    bullets.remove(bullet)
                if meteor.hitpoints <= 0:
                    meteors.remove(meteor)

    for meteor in meteors[:]:
        if spaceship.rect.colliderect(meteor.rect) and not spaceship.invulnerable:
            spaceship.lives -= 1
            spaceship.respawn()
            meteor.hit(5)
            if meteor.hitpoints <= 0:
                meteors.remove(meteor)

    for enemy in enemies[:]:
        if spaceship.rect.colliderect(enemy.collision_rect) and not spaceship.invulnerable:
            spaceship.lives -= 1
            spaceship.respawn()
            enemies.remove(enemy)

    for enemy_bullet in enemy_bullets[:]:
        if spaceship.rect.colliderect(enemy_bullet.rect) and not spaceship.invulnerable:
            spaceship.lives -= 1
            spaceship.respawn()

    for bonus in bonuses[:]:
        if spaceship.rect.colliderect(bonus.rect):
            if bonus.bonus_type == "weapon":
                spaceship.weapon_level = min(spaceship.weapon_level + 1, 10)
            elif bonus.bonus_type == "life":
                spaceship.lives += 1
            elif bonus.bonus_type == "invulnerability":
                spaceship.invulnerable = True
                spaceship.spawnedat = pygame.time.get_ticks()

            bonuses.remove(bonus)

    # Draw everything
    screen.fill(VOID_BLACK)

    # screen.blit(bg_nebula, (0 - int(spaceship.rect.centerx / 3), 0 - int(spaceship.rect.centery / 3)))

    for bs in backgroundstars:
        bs.draw()
    spaceship.draw()
    for b in bullets:
        b.draw()
    for m in meteors:
        m.draw()
    for e in enemies:
        e.draw()
        e.shoot(enemy_bullets)
    for eb in enemy_bullets:
        eb.draw()
    for bo in bonuses:
        bo.draw()
        if pygame.time.get_ticks() > bo.killtime:
            bonuses.remove(bo)

    score_text = ui_font.render("Score: " + str(score), True, WHITE)
    screen.blit(score_text, (10, SCREEN_HEIGHT - score_text.get_height() - 2))
    lives_text = ui_font.render("Lives: " + str(spaceship.lives), True, WHITE)
    screen.blit(lives_text, (SCREEN_WIDTH - lives_text.get_width() - 10, SCREEN_HEIGHT - score_text.get_height() - 2))

    # Display update
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
