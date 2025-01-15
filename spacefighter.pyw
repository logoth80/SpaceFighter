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
        self.last_shot, self.last_spin, self.lastudown = 0, 0, 0
        self.spaceship_pics = []
        for i in range(5):
            self.spaceship_pics.append(pygame.image.load(f"ship{i + 1}.png").convert_alpha())
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
            bullets.append(Bullet(self.rect.right, self.rect.centery, 10, 0, False))
            self.shoot_sound.play()
        if self.invulnerable and pygame.time.get_ticks() > self.spawnedat + 5000:
            self.invulnerable = False
        if pygame.time.get_ticks() > self.last_spin + 3750 and self.weapon_level >= 8:
            bullets.append(Bullet(self.rect.centerx, self.rect.centery, 10, 0, True))
            self.last_spin = pygame.time.get_ticks()
        if pygame.time.get_ticks() > self.lastudown + 2000 and self.weapon_level >= 10:
            bullets.append(Bullet(self.rect.centerx, self.rect.top, 0, -5, False))
            bullets.append(Bullet(self.rect.centerx, self.rect.bottom, 0, 5, False))
            self.lastudown = pygame.time.get_ticks()

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
    def __init__(self, x, y, dx, dy, rotating=False):
        self.image = pygame.Surface((20, 25))
        self.image.fill((255, 255, 0))
        self.rect = self.image.get_rect(center=(x, y))
        self.x, self.y = x, y
        self.dx, self.dy = dx, dy
        self.rotating = rotating
        self.spawntime = pygame.time.get_ticks()
        self.todestroy = False
        self.image = pygame.image.load("bullet.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (20, 20))

    def update(self):
        if self.rotating:
            t = pygame.time.get_ticks() - self.spawntime
            offsetx = 0.1 * min(600, 600) * math.sin(t / 200)
            offsety = 0.1 * min(600, 600) * math.cos(t / 200)
            self.x = spaceship.rect.centerx + offsetx
            self.y = spaceship.rect.centery + offsety
            self.rect.centerx, self.rect.centery = self.x, self.y
            if pygame.time.get_ticks() - self.spawntime >= 3900:
                self.todestroy = True
        else:
            self.x += self.dx
            self.y += self.dy
            self.rect.centerx, self.rect.centery = self.x, self.y
            if self.x > 4000 or self.y > 2500 or self.x < -300 or self.y < -300:
                # print("Removing bullet")
                self.todestroy = True
        return self.rect.right > 0

    def draw(self):
        screen.blit(self.image, self.rect)


# Meteor class
class Meteor:
    def __init__(self, x, y):
        self.posx, self.posy = x, y
        cx, cy = 53, 55
        self.maxhp = 10
        self.hitpoints = self.maxhp
        self.image = pygame.image.load("rock.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (70, 63))
        self.image = pygame.transform.rotate(self.image, random.randint(0, 359))
        self.rect = self.image.get_rect(center=(x, y))
        self.collision_rect = pygame.Rect(self.rect.centerx - cx // 2, self.rect.centery - cy // 2, cx, cy)

    def update(self):
        self.posx -= scroll_speed
        self.rect.centerx = int(self.posx)
        self.collision_rect.centerx = int(self.posx)
        return self.rect.right > 0

    def hit(self, hit):
        self.hitpoints -= hit
        alpha = int(125 + 130 * self.hitpoints / self.maxhp)
        self.image.set_alpha(alpha)

    def draw(self):
        screen.blit(self.image, self.rect)
        # pygame.draw.rect(screen, (0, 255, 0), self.collision_rect, 2)


# Enemy class
class Enemy:
    def __init__(self, x, y, maxhitpoints, enemy_type, weapon, potential_drop):
        self.posx, self.posy = x, y
        self.hitpoints = maxhitpoints
        self.speed = scroll_speed + 0.2
        self.type = enemy_type
        self.weapon = weapon
        self.potential_drop = potential_drop
        self.last_shot = pygame.time.get_ticks()
        self.explosion_sound = pygame.mixer.Sound("pop.wav")
        self.image = pygame.image.load(f"enemy{self.type}.png")
        self.image.convert_alpha()
        if enemy_type == 1:
            self.image = pygame.transform.rotate(self.image, random.randint(0, 359))
            self.image = pygame.transform.scale(self.image, (60, 60))
            cx, cy = 45, 56
        elif enemy_type == 2:
            self.image = pygame.transform.rotate(self.image, random.randint(0, 359))
            self.image = pygame.transform.scale(self.image, (80, 80))
            cx, cy = 65, 70
        elif enemy_type == 3:
            self.image = pygame.transform.scale(self.image, (75, 60))
            cx, cy = 52, 56
        elif enemy_type == 4:
            self.image = pygame.transform.scale(self.image, (60, 80))
            cx, cy = 45, 76
        else:
            cx, cy = 50, 50
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        self.collision_rect = pygame.Rect(self.rect.centerx - cx // 2, self.rect.centery - cy // 2, cx, cy)

    def update(self):
        self.posx -= self.speed
        self.rect.x = int(self.posx)
        self.rect.y = int(self.posy)
        self.collision_rect.center = self.rect.center
        return self.rect.right > 0

    def shoot(self, enemy_bullets):
        shoot_roll = random.randint(0, 600)
        if self.type == 3:
            if shoot_roll == 600 and self.last_shot + 300 < pygame.time.get_ticks():
                enemy_bullets.append(EnemyBullet(self.rect.left, self.rect.centery, -3, 0))
                enemy_bullets.append(EnemyBullet(self.rect.left, self.rect.centery, -2, -2))
                enemy_bullets.append(EnemyBullet(self.rect.left, self.rect.centery, -2, 2))
                self.last_shot = pygame.time.get_ticks()
        elif self.type == 4:
            if shoot_roll == 600 and self.last_shot + 300 < pygame.time.get_ticks():
                enemy_bullets.append(EnemyBullet(self.rect.left, self.rect.centery, -3, 0))
                enemy_bullets.append(EnemyBullet(self.rect.centerx, self.rect.top, -scroll_speed, -3))
                enemy_bullets.append(EnemyBullet(self.rect.centerx, self.rect.bottom, -scroll_speed, 3))
                self.last_shot = pygame.time.get_ticks()
        elif self.type == 2:
            if shoot_roll >= 600 and self.last_shot + 300 < pygame.time.get_ticks():
                enemy_bullets.append(EnemyBullet(self.rect.left, self.rect.centery, -3, 0, True))
                self.last_shot = pygame.time.get_ticks()
        else:
            if shoot_roll >= 598 and self.last_shot + 300 < pygame.time.get_ticks():
                enemy_bullets.append(EnemyBullet(self.rect.left, self.rect.centery, -3, 0))
                self.last_shot = pygame.time.get_ticks()

    def draw(self):
        screen.blit(self.image, self.rect)
        # pygame.draw.rect(screen, (0, 255, 0), self.collision_rect, 2)

    def destroy(self):
        if self.potential_drop is not None:
            bonuses.append(Bonus(self.rect.centerx, self.rect.centery, bonus_type=self.potential_drop))
        self.explosion_sound.play()


# EnemyBullet class
class EnemyBullet:
    def __init__(self, x, y, dx, dy, spin=False):
        self.image = pygame.Surface((20, 20))
        self.image.fill((255, 0, 255))
        self.rect = self.image.get_rect(center=(x, y))
        self.x, self.y = x, y
        self.dx, self.dy = dx, dy
        self.image = pygame.image.load("enemy_bullet.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (20, 20))
        self.spinning = spin
        self.spawn_time = pygame.time.get_ticks()

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        if self.spinning:
            t = pygame.time.get_ticks() - self.spawn_time
            offsetx = 0.02 * t * math.sin(t / 150)
            offsety = 0.02 * t * math.cos(t / 150)
            self.rect.x = self.x + offsetx
            self.rect.y = self.y + offsety
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
        self.size = random.randint(1, 5)
        self.color = (255 - self.size * 35, 255 - self.size * 35, 255 - self.size * 35)
        self.x = random.randint(0, SCREEN_WIDTH + 3)
        self.y = random.randint(-2, SCREEN_HEIGHT + 2)
        self.image = pygame.draw.circle(screen, self.color, (self.x, self.y), self.size // 2)

    def update(self):
        self.x -= scroll_speed / 3
        if self.x <= -4:
            self.x = SCREEN_WIDTH + 3
            self.y = random.randint(-2, SCREEN_HEIGHT + 2)
        return True

    def draw(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.size // 2)
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
    meteor_list.append({"t": 2000 + i * 4000, "y": random.randint(0, 20) * 5})

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
                "y": random.randint(2, 18) * 5,
                "hp": 3,
                "k": enemy_type_in_wave,
                "w": 1,
                "b": kind,
            }
        )


spawner = Spawner(meteor_list, enemy_list)

for i in range(400):
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
                print(len(bullets))

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
            if bullet.rect.colliderect(meteor.collision_rect):
                meteor.hit(1)
                if bullet in bullets:
                    bullets.remove(bullet)
                if meteor.hitpoints <= 0:
                    meteors.remove(meteor)
        if bullet.todestroy and bullet in bullets:
            bullets.remove(bullet)

    for meteor in meteors[:]:
        if spaceship.rect.colliderect(meteor.collision_rect) and not spaceship.invulnerable:
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
