import pygame
from config import *
import random
import math


class Spritesheet:
    def __init__(self, path):
        self.image = pygame.image.load(path).convert()

    def get_sprite(self, x, y, width, height):
        sprite = pygame.Surface([width, height])
        sprite.blit(self.image, (0, 0), (x, y, width, height))
        sprite.set_colorkey(BLACK)
        return sprite


class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = PLAYER_LAYER
        self.groups = self.game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.has_pickaxe = False
        self.knife_count = 0

        self.facing = "down"

        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = TILESIZE
        self.height = TILESIZE

        self.x_movement = 0
        self.y_movement = 0

        self.health=99

        self.animation_frame = 1

        self.image = self.game.character_spritesheet.get_sprite(3, 2, TILESIZE, TILESIZE)
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

    def movement(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.x_movement -= PLAYER_SPEED
            self.facing = "left"
        if keys[pygame.K_d]:
            self.x_movement += PLAYER_SPEED
            self.facing = "right"
        if keys[pygame.K_w]:
            self.y_movement -= PLAYER_SPEED
            self.facing = "up"
        if keys[pygame.K_s]:
            self.y_movement += PLAYER_SPEED
            self.facing = "down"

    def update(self):
        self.movement()
        self.animate()
        self.get_enemy_collision()
        self.get_pickaxe_collision()
        self.get_knife_collision()
        self.rect.x += self.x_movement
        self.get_obst_collision("x")
        self.rect.y += self.y_movement
        self.get_obst_collision("y")

        self.x_movement = 0
        self.y_movement = 0

    def get_obst_collision(self, direction):
        if direction == "x":
            collision = pygame.sprite.spritecollide(self, self.game.objects, False)
            if collision:
                if self.x_movement > 0:
                    self.rect.x = collision[0].rect.left - self.rect.width
                if self.x_movement < 0:
                    self.rect.x = collision[0].rect.right
        if direction == "y":
            collision = pygame.sprite.spritecollide(self, self.game.objects, False)
            if collision:
                if self.y_movement > 0:
                    self.rect.y = collision[0].rect.top - self.rect.height
                if self.y_movement < 0:
                    self.rect.y = collision[0].rect.bottom

    def get_enemy_collision(self):
        collision = pygame.sprite.spritecollide(self, self.game.enemies, True)
        if collision:
            self.health-=33
            self.game.current_enemy_count-=1
            if self.health<=0:
                self.kill()
                self.game.playing = False

        collision = pygame.sprite.spritecollide(self, self.game.boss, False)
        if collision:
            self.kill()
            self.game.playing = False

    def get_pickaxe_collision(self):
        collision = pygame.sprite.spritecollide(self, self.game.pickaxe, True)
        if collision:
            self.has_pickaxe = True

    def get_knife_collision(self):
        collision = pygame.sprite.spritecollide(self, self.game.knife, True)
        if collision:
            self.knife_count = 5

    def animate(self):
        direction = self.facing
        down_animations = [self.game.character_spritesheet.get_sprite(3, 2, self.width, self.height),
                           self.game.character_spritesheet.get_sprite(35, 2, self.width, self.height),
                           self.game.character_spritesheet.get_sprite(68, 2, self.width, self.height)]

        up_animations = [self.game.character_spritesheet.get_sprite(3, 34, self.width, self.height),
                         self.game.character_spritesheet.get_sprite(35, 34, self.width, self.height),
                         self.game.character_spritesheet.get_sprite(68, 34, self.width, self.height)]

        left_animations = [self.game.character_spritesheet.get_sprite(3, 98, self.width, self.height),
                           self.game.character_spritesheet.get_sprite(35, 98, self.width, self.height),
                           self.game.character_spritesheet.get_sprite(68, 98, self.width, self.height)]

        right_animations = [self.game.character_spritesheet.get_sprite(3, 66, self.width, self.height),
                            self.game.character_spritesheet.get_sprite(35, 66, self.width, self.height),
                            self.game.character_spritesheet.get_sprite(68, 66, self.width, self.height)]

        if direction == "down":
            if self.y_movement == 0:
                self.image = down_animations[0]
            if self.y_movement > 0:
                self.image = down_animations[math.floor(self.animation_frame)]
                self.animation_frame += 0.1
                if self.animation_frame >= 3:
                    self.animation_frame = 1
        if direction == "up":
            if self.y_movement == 0:
                self.image = up_animations[0]
            if self.y_movement < 0:
                self.image = up_animations[math.floor(self.animation_frame)]
                self.animation_frame += 0.1
                if self.animation_frame >= 3:
                    self.animation_frame = 1
        if direction == "left":
            if self.x_movement == 0:
                self.image = left_animations[0]
            if self.x_movement < 0:
                self.image = left_animations[math.floor(self.animation_frame)]
                self.animation_frame += 0.1
                if self.animation_frame >= 3:
                    self.animation_frame = 1
        if direction == "right":
            if self.x_movement == 0:
                self.image = right_animations[0]
            if self.x_movement > 0:
                self.image = right_animations[math.floor(self.animation_frame)]
                self.animation_frame += 0.1
                if self.animation_frame >= 3:
                    self.animation_frame = 1


# noinspection PyTypeChecker
class Enemy(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = ENEMY_LAYER
        self.groups = self.game.all_sprites, self.game.enemies
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.facing = "left"

        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = TILESIZE
        self.height = TILESIZE

        self.x_movement = 0
        self.y_movement = 0
        self.maxtravel = random.randint(7, 32)
        self.distancetraveled = 0

        self.animation_frame = 1

        self.image = self.game.enemy_spritesheet.get_sprite(3, 2, TILESIZE, TILESIZE)
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

    def update(self):
        self.animate()
        self.movement()
        self.rect.x += self.x_movement
        self.get_obst_collisions()

        self.x_movement = 0

    def movement(self):
        if self.facing == "left":
            self.x_movement -= ENEMY_SPEED
            self.distancetraveled -= 1
            if self.distancetraveled <= -self.maxtravel:
                self.facing = 'right'
        if self.facing == "right":
            self.x_movement += ENEMY_SPEED
            self.distancetraveled += 1
            if self.distancetraveled >= self.maxtravel:
                self.facing = 'left'

    def get_obst_collisions(self):
        collisions = pygame.sprite.spritecollide(self, self.game.objects, False)
        if collisions:
            if self.x_movement > 0:
                self.rect.x = collisions[0].rect.left - self.rect.width
            if self.x_movement < 0:
                self.rect.x = collisions[0].rect.right

    def animate(self):
        left_animations = [self.game.enemy_spritesheet.get_sprite(3, 98, self.width, self.height),
                           self.game.enemy_spritesheet.get_sprite(35, 98, self.width, self.height),
                           self.game.enemy_spritesheet.get_sprite(68, 98, self.width, self.height)]

        right_animations = [self.game.enemy_spritesheet.get_sprite(3, 66, self.width, self.height),
                            self.game.enemy_spritesheet.get_sprite(35, 66, self.width, self.height),
                            self.game.enemy_spritesheet.get_sprite(68, 66, self.width, self.height)]

        if self.facing == 'left':
            self.image = left_animations[math.floor(self.animation_frame)]
            self.animation_frame += 0.1
            if self.animation_frame >= 3:
                self.animation_frame = 1
        if self.facing == 'right':
            self.image = right_animations[math.floor(self.animation_frame)]
            self.animation_frame += 0.1
            if self.animation_frame >= 3:
                self.animation_frame = 1


# noinspection PyTypeChecker
class Boss(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = ENEMY_LAYER
        self.groups = self.game.all_sprites, self.game.boss
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = TILESIZE * 2
        self.height = TILESIZE * 2

        self.image = self.game.boss_spritesheet.get_sprite(0, 0, TILESIZE * 2, TILESIZE * 2)
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

        self.health = 2000


# noinspection PyTypeChecker
class Fireball(pygame.sprite.Sprite):
    def __init__(self, game, x, y, direction):
        self.game = game
        self._layer = ENEMY_LAYER
        self.groups = self.game.all_sprites, self.game.enemies
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = TILESIZE
        self.height = TILESIZE

        self.facing = direction
        self.distancetraveled = 0

        self.getImage()
        self.image = self.game.fireball_spritesheet.get_sprite(0, 0, TILESIZE, TILESIZE)
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

    def getImage(self):
        if self.facing == 'left':
            self.game.fireball_spritesheet = Spritesheet('img/fireball_left.png')
        elif self.facing == 'right':
            self.game.fireball_spritesheet = Spritesheet('img/fireball_right.png')

    def movement(self):
        if self.distancetraveled < 128:
            if self.facing == 'left':
                self.rect.x -= FIREBALL_SPEED
            if self.facing == 'right':
                self.rect.x += FIREBALL_SPEED
            self.distancetraveled += 1
        else:
            self.kill()

    def update(self):
        self.movement()


# noinspection PyTypeChecker
class Attack(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = PLAYER_LAYER
        self.groups = self.game.all_sprites, self.game.attacks
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.x = x
        self.y = y
        self.width = TILESIZE
        self.height = TILESIZE

        self.animation_frame = 1

        self.image = self.game.attack_spritesheet.get_sprite(0, 0, TILESIZE, TILESIZE)
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

    def update(self):
        self.get_enemy_collision()
        self.get_object_collision()
        self.animate()

    def get_enemy_collision(self):
        collision = pygame.sprite.spritecollide(self, self.game.enemies, True)
        if collision:
            self.game.current_enemy_count -= len(collision)
            if not self.game.player.has_pickaxe:
                self.spawn_pickaxe(self.game, collision[0].rect.x // 32, collision[0].rect.y // 32)

        boss_collision = pygame.sprite.spritecollide(self, self.game.boss, False)
        if boss_collision:
            boss_collision[0].health -= 10
            if boss_collision[0].health <= 0:
                boss_collision[0].kill()
                self.game.is_won=True
                self.game.playing = False

    def get_object_collision(self):
        if self.game.player.has_pickaxe:
            collision = pygame.sprite.spritecollide(self, self.game.breakable_objects, True)
            for object in collision:
                if object.contains_knife:
                    Knife(self.game, object.rect.x, object.rect.y, "right", True)

    def spawn_pickaxe(self, game, x, y):
        chance = random.randint(1, 30)
        if chance == 1:
            Pickaxe(game, x, y)

    def animate(self):
        direction = self.game.player.facing
        right_animations = [self.game.attack_spritesheet.get_sprite(0, 64, self.width, self.height),
                            self.game.attack_spritesheet.get_sprite(32, 64, self.width, self.height),
                            self.game.attack_spritesheet.get_sprite(64, 64, self.width, self.height),
                            self.game.attack_spritesheet.get_sprite(96, 64, self.width, self.height),
                            self.game.attack_spritesheet.get_sprite(128, 64, self.width, self.height)]

        down_animations = [self.game.attack_spritesheet.get_sprite(0, 32, self.width, self.height),
                           self.game.attack_spritesheet.get_sprite(32, 32, self.width, self.height),
                           self.game.attack_spritesheet.get_sprite(64, 32, self.width, self.height),
                           self.game.attack_spritesheet.get_sprite(96, 32, self.width, self.height),
                           self.game.attack_spritesheet.get_sprite(128, 32, self.width, self.height)]

        left_animations = [self.game.attack_spritesheet.get_sprite(0, 96, self.width, self.height),
                           self.game.attack_spritesheet.get_sprite(32, 96, self.width, self.height),
                           self.game.attack_spritesheet.get_sprite(64, 96, self.width, self.height),
                           self.game.attack_spritesheet.get_sprite(96, 96, self.width, self.height),
                           self.game.attack_spritesheet.get_sprite(128, 96, self.width, self.height)]

        up_animations = [self.game.attack_spritesheet.get_sprite(0, 0, self.width, self.height),
                         self.game.attack_spritesheet.get_sprite(32, 0, self.width, self.height),
                         self.game.attack_spritesheet.get_sprite(64, 0, self.width, self.height),
                         self.game.attack_spritesheet.get_sprite(96, 0, self.width, self.height),
                         self.game.attack_spritesheet.get_sprite(128, 0, self.width, self.height)]

        if direction == "up":
            self.image = up_animations[math.floor(self.animation_frame)]
            self.animation_frame += 0.5
            if self.animation_frame >= 5:
                self.kill()
        if direction == "down":
            self.image = down_animations[math.floor(self.animation_frame)]
            self.animation_frame += 0.5
            if self.animation_frame >= 5:
                self.kill()
        if direction == "left":
            self.image = left_animations[math.floor(self.animation_frame)]
            self.animation_frame += 0.5
            if self.animation_frame >= 5:
                self.kill()
        if direction == "right":
            self.image = right_animations[math.floor(self.animation_frame)]
            self.animation_frame += 0.5
            if self.animation_frame >= 5:
                self.kill()


# noinspection PyTypeChecker
class Pickaxe(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = ITEM_LAYER
        self.groups = self.game.all_sprites, self.game.pickaxe
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = TILESIZE
        self.height = TILESIZE

        self.animation_frame = 1

        self.image = self.game.pickaxe_spritesheet.get_sprite(0, 0, TILESIZE, TILESIZE)
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y


# noinspection PyTypeChecker
class Knife(pygame.sprite.Sprite):
    def __init__(self, game, x, y, direction, item):
        self.game = game
        self._layer = PLAYER_LAYER
        self.groups = self.game.all_sprites, self.game.knife
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.x = x
        self.y = y
        self.width = TILESIZE
        self.height = TILESIZE
        self.direction = direction

        self.distance_traveled = 0
        self.isItem = item

        self.getImage()
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

    def getImage(self):
        if self.direction == "down":
            self.game.knife_spritesheet = Spritesheet("img/knife_down.png")
            self.image = self.game.knife_spritesheet.get_sprite(0, 0, TILESIZE, TILESIZE)
        if self.direction == "up":
            self.game.knife_spritesheet = Spritesheet("img/knife_up.png")
            self.image = self.game.knife_spritesheet.get_sprite(0, 0, TILESIZE, TILESIZE)
        if self.direction == "right":
            self.game.knife_spritesheet = Spritesheet("img/knife_right.png")
            self.image = self.game.knife_spritesheet.get_sprite(0, 0, TILESIZE, TILESIZE)
        if self.direction == "left":
            self.game.knife_spritesheet = Spritesheet("img/knife_left.png")
            self.image = self.game.knife_spritesheet.get_sprite(0, 0, TILESIZE, TILESIZE)

    def movement(self):
        if not self.isItem:
            if self.direction == "down":
                self.rect.y += THROWABLE_SPEED
                self.distance_traveled += 1
            if self.direction == "up":
                self.rect.y -= THROWABLE_SPEED
                self.distance_traveled += 1
            if self.direction == "left":
                self.rect.x -= THROWABLE_SPEED
                self.distance_traveled += 1
            if self.direction == "right":
                self.rect.x += THROWABLE_SPEED
                self.distance_traveled += 1
            if self.distance_traveled == TILESIZE * 3:
                self.kill()

    def get_enemy_collision(self):
        collision = pygame.sprite.spritecollide(self, self.game.enemies, True)
        if collision:
            self.game.current_enemy_count -= len(collision)
        boss_collision = pygame.sprite.spritecollide(self, self.game.boss, False)
        if boss_collision:
            boss_collision[0].health -= 100
            if boss_collision[0].health <= 0:
                boss_collision[0].kill()
                self.game.is_won=True
                self.game.playing = False

    def update(self):
        self.movement()
        self.get_enemy_collision()


# noinspection PyTypeChecker
class BreakableObstacle(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = OBST_LAYER
        self.groups = self.game.all_sprites, self.game.objects, self.game.breakable_objects
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = TILESIZE
        self.height = TILESIZE

        self.contains_knife = False

        self.temp = self.get_random_texture()
        self.image = self.game.terrain_spritesheet.get_sprite(self.temp[0], self.temp[1], TILESIZE, TILESIZE)
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

    def get_random_texture(self):
        choices = [(961, 445), (990, 608), (960, 576)]
        return random.choice(choices)


# noinspection PyTypeChecker
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = OBST_LAYER
        self.groups = self.game.all_sprites, self.game.objects
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = TILESIZE
        self.height = TILESIZE

        self.temp = self.get_random_texture()
        self.image = self.game.terrain_spritesheet.get_sprite(self.temp[0], self.temp[1], TILESIZE, TILESIZE)
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

    def get_random_texture(self):
        choices = [(961, 445), (990, 608), (960, 576)]
        return random.choice(choices)


# noinspection PyTypeChecker
class Ground(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = OBST_LAYER
        self.groups = self.game.all_sprites, self.game.terrain
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = TILESIZE
        self.height = TILESIZE

        self.temp = self.get_random_texture()
        self.image = self.game.terrain_spritesheet.get_sprite(self.temp[0], self.temp[1], TILESIZE, TILESIZE)
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

    def get_random_texture(self):
        choices = [(0, 352), (98, 352)]
        return random.choice(choices)


class Button:
    def __init__(self, x, y, width, height, fg, bg, content, fontsize):
        self.font = pygame.font.Font('arial.ttf', fontsize)
        self.content = content

        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.fg = fg
        self.bg = bg

        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(self.bg)
        self.rect = self.image.get_rect()

        self.rect.x = self.x
        self.rect.y = self.y

        self.text = self.font.render(self.content, True, self.fg)
        self.text_rect=self.text.get_rect(center=(self.width/2,self.height/2))
        self.image.blit(self.text,self.text_rect)

    def is_pressed(self,pos,pressed):
        if self.rect.collidepoint(pos):
            if pressed[0]:
                return True
            return False
        return False
