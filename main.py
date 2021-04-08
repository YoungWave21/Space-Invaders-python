import pygame
import random
import time

# the mask in this is used to remove all non colored area of an image to provide accurate collisions

# initializing, must always add this
pygame.init()
pygame.font.init()
main_font = pygame.font.SysFont("comicsans", 50)
lost_font = pygame.font.SysFont("comicsans", 70)
start = True
WIDTH = 800
HEIGHT = 600
bull_vel = 7
NUM_ENEMY = 0
score = 0
stars = []

for i in range(150):
    stars.append({"x": random.randrange(0, WIDTH), "y": random.randrange(0, HEIGHT), "r": random.randrange(2, 5)})

# drawing the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# title
pygame.display.set_caption("Space Invaders")
pygame.display.set_icon(pygame.image.load("images/spaceship.png"))

# loading all images
enemyIMG = pygame.image.load("images/enemy.png")
red_enemy_img = pygame.image.load("images/pixel_ship_red_small.png")
green_enemy_img = pygame.image.load("images/pixel_ship_green_small.png")
blue_enemy_img = pygame.image.load("images/pixel_ship_blue_small.png")
red_pixel_img = pygame.image.load("images/pixel_laser_red.png")
green_pixel_img = pygame.image.load("images/pixel_laser_green.png")
blue_pixel_img = pygame.image.load("images/pixel_laser_blue.png")
playerIMG = pygame.image.load("images/player.png")
enemy = []
ENEMY_VELOCITY = 2
color_index = {"red": (red_enemy_img, red_pixel_img, 3), "blue": (blue_enemy_img, blue_pixel_img, 7),
               "green": (green_enemy_img, green_pixel_img, 5)}
clock = pygame.time.Clock()


# generate the enemies
def spawnEnemies():
    for q in range(NUM_ENEMY):
        enemy.append(Enemy(random.randrange(50, WIDTH - 100), random.randrange(-500, -100),
                           random.choice(["red", "green", "blue"])))


class Lasers:
    def __init__(self, x, y, img):
        self.position = {"x": x, "y": y}
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.position["x"], self.position["y"]))

    def move(self, vel):
        self.position["y"] += vel

    def off_screen(self):
        if self.position["y"] < HEIGHT / 2:
            return not (HEIGHT > self.position["y"] + self.get_height() >= 0)
        else:
            return not (HEIGHT > self.position["y"] >= 0)

    def get_height(self):
        return self.img.get_height()

    def collision(self, obj):
        return colided(self, obj)


def colided(obj1, obj2):
    offset_x = obj2.position["x"] - obj1.position["x"]
    offset_y = obj2.position["y"] - obj1.position["y"]
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y))


class Ship:
    def __init__(self, x, y, yv, xv, img):
        self.velocity = {"x": xv, "y": yv}
        self.position = {"x": x, "y": y}
        self.img = img
        self.shot = True
        self.points = 0
        self.delay = 0.3
        self.lasers = []
        self.startTime = 0
        self.endTime = 0
        self.laserIMG = red_pixel_img
        self.cool_down = 0
        self.mask = pygame.mask.from_surface(self.img)
        self.health = 100

    def cooled(self):
        self.endTime = time.time()
        if self.endTime - self.startTime > self.delay:
            self.shot = True

    def shoot(self):
        if self.cool_down == 0:
            self.lasers.append(
                Lasers(round(self.position["x"] - (self.img.get_height() / 4)),
                       round(self.position["y"] - (self.img.get_height() / 2)), self.laserIMG))

    def get_width(self):
        return self.img.get_width()

    def drawHealthBar(self):
        pygame.draw.rect(screen, (255, 255, 255), (
            self.position["x"] - (self.get_width() / 4), (self.position["y"] + self.get_height()), 100, 7))
        pygame.draw.rect(screen, (0, 255, 0), (
            self.position["x"] - (self.get_width() / 4), (self.position["y"] + self.get_height()), self.health, 7))

    def get_height(self):
        return self.img.get_height()

    def Draw(self, window, vel, objs):
        for laser in self.lasers:
            laser.draw(screen)
            laser.move(-vel)
            if laser.off_screen():
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        self.points += obj.value
                        objs.remove(obj)
                        self.lasers.remove(laser)
        window.blit(self.img, (self.position["x"], self.position["y"]))


class Enemy:
    def __init__(self, x, y, color):
        self.img, self.laserImg, self.value = color_index[color]
        self.position = {"x": x, "y": y}
        self.lasers = []
        self.cooldown = 0
        self.shoot = True
        self.startTime = 0
        self.endTime = 0
        self.mask = pygame.mask.from_surface(self.img)

    def cooled(self):
        # cooling mechanism, can shoot after 2s
        self.endTime = time.time()
        if self.endTime - self.startTime > 2:
            self.shoot = True

    def Draw(self, window, vel, obj):
        for laser in self.lasers:
            laser.draw(screen)
            laser.move(vel)
            if laser.off_screen():
                self.lasers.remove(laser)
            elif laser.collision(obj):
                self.lasers.remove(laser)
                player.health -= 10
        window.blit(self.img, (self.position["x"], self.position["y"]))

    def get_height(self):
        return self.img.get_height()


# Infinite game loop
player = Ship(370, 500, 7, 7, playerIMG)


def main():
    level = 0
    global NUM_ENEMY
    lives = 5
    running = True
    while running:
        clock.tick(60)
        screen.fill((0, 0, 26))
        if len(enemy) == 0:
            level += 1
            NUM_ENEMY += 2
            spawnEnemies()

        for q in range(len(stars)):
            pygame.draw.circle(screen, (255, 255, 255), (stars[q]["x"], stars[q]["y"]), stars[q]["r"], 1)

        # key event handlers
        for ent in pygame.event.get():
            if ent.type == pygame.QUIT:
                quit()

        keys = pygame.key.get_pressed()  # return an array of key pressed, it can detect multiple key presses together
        if keys[pygame.K_LEFT] and player.position["x"] > 0:
            player.position["x"] -= player.velocity["x"]
        if keys[pygame.K_RIGHT] and player.position["x"] < WIDTH - 64:
            player.position["x"] += player.velocity["x"]
        if keys[pygame.K_UP] and player.position["y"] > 0:
            player.position["y"] -= player.velocity["y"]
        if keys[pygame.K_DOWN] and player.position["y"] < HEIGHT - 64:
            player.position["y"] += player.velocity["y"]
        if keys[pygame.K_SPACE] and player.shot:
            player.shoot()
            player.shot = False
            player.startTime = time.time()

        # making a copy of the enemies because if hte enemies are killed then it will affect the loop
        for en in enemy[:]:
            en.Draw(screen, bull_vel, player)
            en.position["y"] += ENEMY_VELOCITY
            if random.random() <= 0.05 and en.shoot:
                en.lasers.append(Lasers(round(en.position["x"] - (en.img.get_height() / 4)),
                                        round(en.position["y"] - (en.img.get_height() / 2)), en.laserImg))
                en.shoot = False
                en.startTime = time.time()
            if en.position["y"] + en.get_height() > HEIGHT:
                lives -= 1
                enemy.remove(en)
            if not en.shoot:
                en.cooled()
            if colided(en, player):
                player.health -= 10
                enemy.remove(en)

        # player loses a life if their health drops below a hundred
        if player.health <= 0:
            player.health = 100
            lives -= 1

        # displaying the score and lives on screen
        level_label = main_font.render(f"Level: {level}", 1, (255, 255, 255))
        lives_label = main_font.render(f"Lives: {lives}", 1, (255, 255, 255))
        points_label = main_font.render(f"Points: {player.points}", 1, (255, 255, 255))
        screen.blit(lives_label, (10, 10))
        screen.blit(points_label, ((WIDTH / 2) - (points_label.get_width() / 2), 10))
        screen.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        player.Draw(screen, bull_vel, enemy)
        player.drawHealthBar()
        player.cooled()
        if lives <= 0:
            print("Game over!")
            lost_label = lost_font.render("You Lost!!", 1, (255, 255, 255))
            screen.blit(lost_label,
                        ((WIDTH / 2) - (lost_label.get_width() / 2), (HEIGHT / 2) - (lost_label.get_height() / 2)))
            pygame.display.update()
            time.sleep(3)
            running = False
        elif player.points >= 1000:
            print("You Win!")
            win_label = lost_font.render("You Win!!", 1, (255, 255, 255))
            screen.blit(win_label,
                        ((WIDTH / 2) - (win_label.get_width() / 2), (HEIGHT / 2) - (win_label.get_height() / 2)))
            pygame.display.update()
            time.sleep(3)
            running = False
        pygame.display.update()


while start:
    screen.fill((0, 0, 0))
    click_label = main_font.render("Click to start game!", 1, (255, 255, 255))
    screen.blit(click_label, (WIDTH / 2 - click_label.get_width() / 2, HEIGHT / 2 - click_label.get_height() / 2))

    screen.blit(red_enemy_img, (200, HEIGHT / 10))
    screen.blit(main_font.render("= 3 points", 1, (255, 255, 255)), (270, HEIGHT / 10))
    screen.blit(main_font.render("= 5 points", 1, (255, 255, 255)), (270, 2 * HEIGHT / 10))
    screen.blit(main_font.render("= 7 points", 1, (255, 255, 255)), (270, 3 * HEIGHT / 10))
    screen.blit(main_font.render("Get 1000 points to win!", 1, (255, 255, 255)), (200, 7 * HEIGHT / 10))
    screen.blit(green_enemy_img, (200, 2 * HEIGHT / 10))
    screen.blit(blue_enemy_img, (200, 3 * HEIGHT / 10))

    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONUP:
            start = False
            main()
        if event.type == pygame.QUIT:
            quit()

    pygame.display.update()
