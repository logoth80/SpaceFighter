import pygame
import random
import math
import json

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 960, 540
# SCREEN_WIDTH, SCREEN_HEIGHT = 1920, 1080

FPS = 100
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
VOID_BLACK = (5, 0, 25)

# Setup screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("SpaceFighter")
clock = pygame.time.Clock()

scroll_speed = 0.7
score = 0
ui_font = pygame.font.SysFont("Arial", 32)


# Spaceship class
class Spaceship:
    def __init__(self):
        self.image = pygame.Surface((50, 40))
        self.shoot_sound = pygame.mixer.Sound("assets\\laser.mp3")
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
            self.spaceship_pics.append(pygame.image.load(f"assets\\ship{i + 1}.png").convert_alpha())
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
    bullet_image = pygame.image.load("assets\\bullet.png").convert_alpha()
    bullet_image = pygame.transform.scale(bullet_image, (20, 20))

    def __init__(self, x, y, dx, dy, rotating=False):
        self.rect = Bullet.bullet_image.get_rect(center=(x, y))
        self.x, self.y, self.dx, self.dy = x, y, dx, dy
        self.rotating = rotating
        self.spawntime = pygame.time.get_ticks()
        self.todestroy = False

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
        screen.blit(Bullet.bullet_image, self.rect)


# Meteor class
class Meteor:
    def __init__(self, x, y):
        self.posx, self.posy = x, y
        cx, cy = 53, 55
        self.maxhp = 10
        self.hitpoints = self.maxhp
        self.image = pygame.image.load("assets\\rock.png").convert_alpha()
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
    enemy1_image = pygame.image.load("assets\\enemy1.png").convert_alpha()
    enemy1_image = pygame.transform.scale(enemy1_image, (60, 60))

    enemy2_image = pygame.image.load("assets\\enemy2.png").convert_alpha()
    enemy2_image = pygame.transform.scale(enemy2_image, (80, 80))

    enemy3_image = []
    enemy3_image.append(pygame.image.load("assets\\enemy_3_1.png").convert_alpha())
    enemy3_image[0] = pygame.transform.scale(enemy3_image[0], (75, 75))
    enemy3_image.append(pygame.image.load("assets\\enemy_3_9.png").convert_alpha())
    enemy3_image[1] = pygame.transform.scale(enemy3_image[1], (75, 75))
    enemy3_image[1].set_alpha(255)

    enemy4_image = []
    for i in range(12):
        enemy4_image.append(pygame.image.load(f"assets\\enemy_4_{i + 1}.png").convert_alpha())
        enemy4_image[i] = pygame.transform.scale(enemy4_image[i], (90, 90))

    def __init__(self, x, y, maxhitpoints, enemy_type, weapon, potential_drop):
        self.posx, self.posy = x, y
        self.maxhp = maxhitpoints
        self.hitpoints = maxhitpoints
        self.speed = scroll_speed + 0.2
        self.type = enemy_type
        self.weapon = weapon
        self.potential_drop = potential_drop
        self.last_shot = pygame.time.get_ticks()
        self.explosion_sound = pygame.mixer.Sound("assets\\pop.wav")
        self.frame = 0
        if enemy_type == 1:
            self.rect = Enemy.enemy1_image.get_rect(center=(int(x), int(y)))
            cx, cy = 45, 56
        elif enemy_type == 2:
            self.rect = Enemy.enemy2_image.get_rect(center=(int(x), int(y)))
            cx, cy = 65, 70
        elif enemy_type == 3:
            self.imageoverlay = Enemy.enemy3_image[1]
            self.rect = Enemy.enemy3_image[0].get_rect(center=(int(x), int(y)))
            cx, cy = 65, 70
        elif enemy_type == 4:
            self.rect = Enemy.enemy4_image[0].get_rect(center=(int(x), int(y)))
            cx, cy = 60, 60
        else:
            cx, cy = 50, 50
        # self.rect = self.image.get_rect(center=(int(x), int(y)))
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
        if self.type == 1:
            screen.blit(Enemy.enemy1_image, self.rect)
        elif self.type == 2:
            screen.blit(Enemy.enemy2_image, self.rect)
        elif self.type == 3:
            screen.blit(Enemy.enemy3_image[0], self.rect)
            self.imageoverlay.set_alpha(255 - int(255 * self.hitpoints / self.maxhp))
            screen.blit(self.imageoverlay, self.rect)
        elif self.type == 4:
            self.frame += 0.2
            screen.blit(Enemy.enemy4_image[int(self.frame) % 12], self.rect)
        # pygame.draw.rect(screen, (0, 255, 0), self.collision_rect, 2)

    def destroy(self):
        if self.potential_drop is not None:
            bonuses.append(Bonus(self.rect.centerx, self.rect.centery, bonus_type=self.potential_drop))
        self.explosion_sound.play()


# EnemyBullet class
class EnemyBullet:
    eb_image = pygame.image.load("assets/enemy_bullet.png").convert_alpha()
    eb_image = pygame.transform.scale(eb_image, (20, 20))

    def __init__(self, x, y, dx, dy, spin=False):
        self.x, self.y = x, y
        self.dx, self.dy = dx, dy
        self.spinning = spin
        self.spawn_time = pygame.time.get_ticks()
        self.rect = EnemyBullet.eb_image.get_rect(center=(x, y))

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
        screen.blit(EnemyBullet.eb_image, self.rect)


# Bonus class
class Bonus:
    def __init__(self, x, y, bonus_type):
        self.rect = pygame.Rect(x - 20, y - 20, 40, 40)
        self.bonus_type = bonus_type
        self.spawn_time = pygame.time.get_ticks()
        self.timetolive = 10000
        self.killtime = self.spawn_time + self.timetolive
        self.posx, self.posy = x, y
        if bonus_type == "weapon":
            self.r, self.g, self.b = 150, 150, 150
        elif bonus_type == "life":
            self.r, self.g, self.b = 0, 255, 0
        elif bonus_type == "invulnerability":
            self.r, self.g, self.b = 0, 0, 255
        elif bonus_type == "speedup":
            self.r, self.g, self.b = 0, 255, 255
        else:
            self.r, self.g, self.b = 255, 255, 255
        self.dim = 1.0

    def update(self):
        self.posx -= scroll_speed / 2
        self.rect.centerx = self.posx
        if self.rect.right < 0:
            bonuses.remove(self)
        return self.rect.right > 0

    def draw(self):
        t, dim, a = 1.0, 1, 1
        if self.killtime - pygame.time.get_ticks() < 2000:
            t = self.killtime - pygame.time.get_ticks() / 400
            dim = max((self.killtime - pygame.time.get_ticks()) / 2000, 0.3)
            a = max(0.3, abs(math.sin(t))) * dim
        self.color = (int(self.r * a), int(self.g * a), int(self.b * a))
        pygame.draw.circle(screen, self.color, self.rect.center, 20)


# background stars class (unused)
class Star:
    def __init__(self):
        self.size = random.randint(1, 5)
        self.halfsize = self.size // 2
        self.color = (255 - self.size * 35, 255 - self.size * 35, 255 - self.size * 35)
        self.x = random.randint(0, SCREEN_WIDTH + 3)
        self.y = random.randint(-2, SCREEN_HEIGHT + 2)
        self.image = pygame.draw.circle(screen, self.color, (self.x, self.y), self.size // 2)
        self.shift = scroll_speed / 3

    def update(self):
        self.x -= self.shift
        if self.x <= -4:
            self.x = SCREEN_WIDTH + 3
            self.y = random.randint(-2, SCREEN_HEIGHT + 2)
        return True

    def draw(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.halfsize)
        return True


# Spawner class
class Spawner:
    def __init__(self, meteor_list, enemy_list):
        self.meteor_list = meteor_list
        self.enemy_list = enemy_list

    def spawn(self, meteors, enemies):
        current_time = pygame.time.get_ticks()
        # Spawn meteors
        for m in self.meteor_list:
            if current_time >= m["t"]:
                meteors.append(Meteor(SCREEN_WIDTH + 70, m["y"] * SCREEN_HEIGHT / 100))
                self.meteor_list.remove(m)
        # Spawn enemies
        for e in self.enemy_list:
            if current_time >= e["t"]:
                enemies.append(
                    Enemy(SCREEN_WIDTH + 70, e["y"] * SCREEN_HEIGHT / 100, e["hp"], e["k"], e["w"], e["b"])
                )  # Time, Y-position, HP, Kind, Weapon, Bonus
                self.enemy_list.remove(e)


spaceship = Spaceship()
bullets, meteors, meteor_list, enemies, enemy_bullets, bonuses, backgroundstars, enemy_list = [], [], [], [], [], [], [], []


# load level
with open("l1.json", "r") as f:
    for line in f:
        enemy_list.append(json.loads(line.strip()))
with open("l1m.json", "r") as f:
    for line in f:
        meteor_list.append(json.loads(line.strip()))

spawner = Spawner(meteor_list, enemy_list)

# for i in range(800):       #unused
#     backgroundstars.append(Star())

frame_number = 0  # Frame counter
last_test = pygame.time.get_ticks()

running = True
bg_image = pygame.image.load("stars_5407.png")
bg_image2 = pygame.image.load("stars_8484.png")
bg_shift = 0
reorder = False

while running:
    frame_number += 1
    bg_shift += scroll_speed / 3
    if bg_shift >= 1920:
        bg_shift -= 1920
        reorder = not reorder

    if pygame.time.get_ticks() >= last_test + 2000:
        print(frame_number / 2)
        last_test = pygame.time.get_ticks()
        frame_number = 0

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
                print(f"bu: {len(bullets)}, eb: {len(enemy_bullets)}, en: {len(enemies)}, meteors: {len(meteors)}")

    # Update spaceship
    spaceship.move(keys)
    spaceship.shoot(bullets)

    # Spawn meteors and enemies
    spawner.spawn(meteors, enemies)

    # Update meteors and enemies
    for meteor in meteors[:]:
        meteor.update()
    for enemy in enemies[:]:
        enemy.update()
    for bonus in bonuses[:]:
        bonus.update()
    for bullet in bullets[:]:
        bullet.update()
    for enemy_bullet in enemy_bullets[:]:
        enemy_bullet.update()

    # Check collisions
    for bullet in bullets[:]:
        for enemy in enemies[:]:
            if bullet.rect.colliderect(enemy.collision_rect):
                enemy.hitpoints -= 1
                if bullet in bullets:
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
        if meteor.rect.x < -100 and meteor in meteors:
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
    # screen.fill(VOID_BLACK)
    if not reorder:
        screen.blit(bg_image, (0 - int(bg_shift), 0))
        screen.blit(bg_image2, (1920 - int(bg_shift), 0))
    else:
        screen.blit(bg_image2, (0 - int(bg_shift), 0))
        screen.blit(bg_image, (1920 - int(bg_shift), 0))

    # for bs in backgroundstars:
    #     bs.draw()
    # if pygame.time.get_ticks() % 5000 == 0:
    #     pygame.image.save(screen, f"stars_{random.randint(1000, 9999)}.png")

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

    # Display update-
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
