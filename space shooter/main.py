import pygame
import os
import random


pygame.init()
WIDTH = 600
HEIGHT = 600

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Fighters")
MAIN_FONT = pygame.font.SysFont('comicsans', 40)
DISPLAY_FONT = pygame.font.SysFont('comicsans', 80)
ship_size = (40, 40)
laser_size = (50, 50)


# load images
REDSHIP = pygame.image.load(
    os.path.join("assets", "pixel_ship_red_small.png"))
BLUESHIP = pygame.image.load(
    os.path.join("assets", "pixel_ship_blue_small.png"))
GREENSHIP = pygame.image.load(
    os.path.join("assets", "pixel_ship_green_small.png"))
# player ship
YELLOWSHIP = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png"))

ships = [REDSHIP, BLUESHIP, GREENSHIP, YELLOWSHIP]
for i in range(4):
    ships[i] = pygame.transform.scale(ships[i], ship_size)

# Lasers
RLASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
BLASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
GLASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
YLASER = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))

lasers = [RLASER, BLASER, GLASER, YLASER]
for i in range(4):
    lasers[i] = pygame.transform.scale(lasers[i], laser_size)

# Background
BG = pygame.image.load(os.path.join("assets", "background-black.png"))
BG = pygame.transform.scale(BG, (WIDTH, HEIGHT))

FPS = 60
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)


class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, win):
        win.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(obj, self)


class Ship:
    COOLDOWN = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down = 0

    def draw(self, win):
        win.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(win)

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()

    def cooldown(self):
        if self.cool_down >= self.COOLDOWN:
            self.cool_down = 0
        elif self.cool_down > 0:
            self.cool_down += 1

    def shoot(self):
        if self.cool_down == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down = 1

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)


class Player(Ship):
    ENEMIES_KILLED = 0

    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = ships[3]
        self.laser_img = lasers[3]
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        self.ENEMIES_KILLED += 1
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def healthbar(self, win):
        y = self.y + self.ship_img.get_height() + 10
        w = self.ship_img.get_width()
        fact = self.health/self.max_health
        pygame.draw.rect(win, RED, (self.x, y, w, 10))
        pygame.draw.rect(win, GREEN, (self.x, y, int(w*fact), 10))

    def draw(self, win):
        super().draw(win)
        self.healthbar(win)


class Enemy(Ship):
    COLOR_MAP = {
        'red': (ships[0], lasers[0]),
        'blue': (ships[1], lasers[1]),
        'green': (ships[2], lasers[2])
    }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down == 0:
            laser = Laser(self.x-5, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down = 1


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) is not None


def main():
    try:
        with open('highscore.txt', 'r') as file:
            high_score = int(file.read().split()[2])
    except FileNotFoundError:
        high_score = 0

    run = True
    level = 0
    lives = 5
    clock = pygame.time.Clock()
    player_vel = 3
    laser_vel = 3

    enemies = []
    wave_length = 5
    enemy_vel = 1
    lost = False
    lost_count = 0

    player = Player(240, 500)

    def redraw_win():
        WIN.blit(BG, (0, 0))
        life = lives if lives >= 0 else 0
        level_text = MAIN_FONT.render(
            f'Lives remaining: {life}', 1, WHITE)
        WIN.blit(level_text, (WIDTH - level_text.get_width() - 10, 10))

        kill_text = MAIN_FONT.render(
            f'Enemies Killed: {player.ENEMIES_KILLED}', 1, WHITE)
        WIN.blit(kill_text,
                 (WIDTH - kill_text.get_width() - 10,
                  level_text.get_height() + 10))

        lives_text = MAIN_FONT.render(f'Level: {level}', 1, WHITE)
        WIN.blit(lives_text, (10, 10))

        score = player.ENEMIES_KILLED

        score_text = MAIN_FONT.render(
            f'High Score: {high_score}', 1, WHITE)
        WIN.blit(score_text, (10, lives_text.get_height() + 10))

        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)

        if lost:
            WIN.blit(BG, (0, 0))
            lost_message = DISPLAY_FONT.render("Game Over!!", 1, WHITE)
            WIN.blit(lost_message, (WIDTH/2 - lost_message.get_width()/2, 220))
            score_mess = DISPLAY_FONT.render(f'Score: {score}', 1, WHITE)
            WIN.blit(score_mess, (WIDTH/2 - score_mess.get_width()/2, 320))

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_win()

        if player.health <= 0 and lives >= 1:
            lives -= 1
            player.health = 100

        if lives < 0:
            lost = True
            lost_count += 1

        if lost:
            with open('highscore.txt', 'w') as file:
                file.write(f'high_score = {high_score}')
            if lost_count > FPS*3:
                break
            else:
                continue

        if len(enemies) == 0:
            level += 1
            wave_length += 5

            for i in range(wave_length):
                x = random.randrange(50, WIDTH - 100)
                y = random.randrange(-1500, -100)
                enemy = Enemy(x, y, random.choice(['red', 'blue', 'green']))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                with open('highscore.txt', 'w') as file:
                    file.write(f'high_score = {high_score}')
                quit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - player_vel > 0:
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH:
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0:
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() + 15 < HEIGHT:
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 2*60) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 20
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)

        player.move_lasers(-laser_vel, enemies)
        high_score = max(high_score, player.ENEMIES_KILLED)


def main_menu():
    run = True
    while run:
        WIN.blit(BG, (0, 0))
        title_text = MAIN_FONT.render('Press the mouse to begin..', 1, WHITE)
        WIN.blit(title_text, (WIDTH/2 - title_text.get_width()/2, 300))

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()


if __name__ == '__main__':
    main_menu()

# Ship selection
# difficulty selection
# Pause
