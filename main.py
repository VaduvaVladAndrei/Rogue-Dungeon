from sprites import *
from config import *

import time
import sys


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.is_won = False
        self.level = 1
        self.breakables = []
        self.font = pygame.font.Font('arial.ttf', 32)
        pygame.display.set_caption('Rogue Dungeon')

        self.icon = pygame.image.load('img/boss.png')
        pygame.display.set_icon(self.icon)

        self.current_enemy_count = 1

        self.elapsed = time.time()

        self.character_spritesheet = Spritesheet("img/character.png")
        self.enemy_spritesheet = Spritesheet("img/enemy.png")
        self.boss_spritesheet = Spritesheet("img/boss.png")
        self.terrain_spritesheet = Spritesheet("img/terrain.png")
        self.attack_spritesheet = Spritesheet("img/attack.png")
        self.pickaxe_spritesheet = Spritesheet("img/pickaxe.png")
        self.knife_spritesheet = Spritesheet("img/knife_right.png")
        self.fireball_spritesheet = Spritesheet("img/fireball_left.png")

        self.intro_background = pygame.image.load('./img/introbackground.png')
        self.gameover_bg = pygame.image.load('./img/gameover.png')

    def new(self):
        self.playing = True
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.objects = pygame.sprite.LayeredUpdates()
        self.breakable_objects = pygame.sprite.LayeredUpdates()
        self.enemies = pygame.sprite.LayeredUpdates()
        self.terrain = pygame.sprite.LayeredUpdates()
        self.attacks = pygame.sprite.LayeredUpdates()
        self.pickaxe = pygame.sprite.LayeredUpdates()
        self.knife = pygame.sprite.LayeredUpdates()
        self.boss = pygame.sprite.LayeredUpdates()

        self.build_tilemap()

    def build_tilemap(self):
        for i in range(len(tilemap)):
            for j in range(len(tilemap[i])):
                Ground(self, j, i)
                if tilemap[i][j] == "O":
                    Obstacle(self, j, i)
                elif tilemap[i][j] == "P":
                    self.player = Player(self, j, i)
                elif tilemap[i][j] == "E":
                    Enemy(self, j, i)
                elif tilemap[i][j] == "B":
                    self.breakables.append(BreakableObstacle(self, j, i))
                elif tilemap[i][j] == "F":
                    Fireball(self, j, i, 'left')
        self.place_knife()

    def place_knife(self):
        num = random.randint(0, len(self.breakables) - 1)
        self.breakables[num].contains_knife = True

    def random_spawn(self, count):
        for i in range(count):
            y = random.randint(2, 12)
            x = random.randint(2, 17)

            # inamicii nu trebuie sa poata aparea peste jucator sau la mai putin de 2 tile-uri la stanga sau dreapta de el
            if abs(self.player.rect.x - x * TILESIZE) > TILESIZE * 2:
                Enemy(self, x, y)
                self.current_enemy_count += 1
            elif abs(self.player.rect.y - y * TILESIZE) > TILESIZE * 2:
                Enemy(self, x, y)
                self.current_enemy_count += 1
            else:
                for j in range(5):
                    y = random.randint(2, 12)
                    x = random.randint(2, 17)
                    if abs(self.player.rect.x - x * TILESIZE) > TILESIZE * 2:
                        Enemy(self, x, y)
                        self.current_enemy_count += 1
                        break

    def spawn_enemies(self):
        if self.current_enemy_count == 0 and self.level != BOSS_LEVEL:
            self.level += 1
            self.random_spawn(self.level)

    def spawn_boss(self):
        if self.level == BOSS_LEVEL:
            Boss(self, 9, 1)
            Obstacle(self, 8, 1)
            Obstacle(self, 8, 2)
            Obstacle(self, 11, 1)
            Obstacle(self, 11, 2)
            self.level += 1

    def spawn_fireballs(self):
        if time.time() > self.elapsed + FIREBALL_FREQ:
            Fireball(self, 1, 3, 'right')
            Fireball(self, 18, 4, 'left')
            self.elapsed = time.time()

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.playing = False
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.player.facing == "up":
                        Attack(self, self.player.rect.x, self.player.rect.y - TILESIZE)
                    if self.player.facing == "down":
                        Attack(self, self.player.rect.x, self.player.rect.y + TILESIZE)
                    if self.player.facing == "left":
                        Attack(self, self.player.rect.x - TILESIZE, self.player.rect.y)
                    if self.player.facing == "right":
                        Attack(self, self.player.rect.x + TILESIZE, self.player.rect.y)
                if event.key == pygame.K_LSHIFT:
                    if self.player.knife_count > 0:
                        self.player.knife_count -= 1
                        if self.player.facing == "up":
                            Knife(self, self.player.rect.x, self.player.rect.y - TILESIZE, "up", False)
                        if self.player.facing == "down":
                            Knife(self, self.player.rect.x, self.player.rect.y + TILESIZE, "down", False)
                        if self.player.facing == "left":
                            Knife(self, self.player.rect.x - TILESIZE, self.player.rect.y, "left", False)
                        if self.player.facing == "right":
                            Knife(self, self.player.rect.x + TILESIZE, self.player.rect.y, "right", False)

    def update(self):
        self.all_sprites.update()

    def draw(self):
        self.screen.fill(BLACK)
        self.all_sprites.draw(self.screen)
        self.clock.tick(FPS)
        pygame.display.update()

    def game_over(self):
        text = self.font.render('Game Over', True, WHITE)
        text_rect = text.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))

        exit_button = Button(WINDOW_WIDTH / 2 - 60, WINDOW_HEIGHT / 2 + 20, 120, 50, WHITE, BLACK, 'Exit', 32)

        for sprite in self.all_sprites:
            sprite.kill()

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()

            if exit_button.is_pressed(mouse_pos, mouse_pressed):
                self.running = False

            self.screen.blit(self.gameover_bg, (0, 0))
            self.screen.blit(text, text_rect)
            self.screen.blit(exit_button.image, exit_button.rect)
            self.clock.tick(FPS)
            pygame.display.update()

    def victory(self):
        text = self.font.render('Victory!', True, WHITE)
        text_rect = text.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))

        exit_button = Button(WINDOW_WIDTH / 2 - 60, WINDOW_HEIGHT / 2 + 20, 120, 50, WHITE, BLACK, 'Exit', 32)
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()

            if exit_button.is_pressed(mouse_pos, mouse_pressed):
                self.running = False
            self.screen.blit(self.intro_background, (0, 0))
            self.screen.blit(text, text_rect)
            self.screen.blit(exit_button.image, exit_button.rect)
            self.clock.tick(FPS)
            pygame.display.update()

    def main_menu(self):
        intro = True

        title = self.font.render('Rogue Dungeon', True, WHITE)
        title_rect = title.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))

        play_button = Button(WINDOW_WIDTH / 2 - 60, WINDOW_HEIGHT / 2 + 20, 120, 50, WHITE, BLACK, 'Play', 32)
        while intro:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    intro = False
                    self.running = False
            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()
            if play_button.is_pressed(mouse_pos, mouse_pressed):
                intro = False
            self.screen.blit(self.intro_background, (0, 0))
            self.screen.blit(title, title_rect)
            self.screen.blit(play_button.image, play_button.rect)
            self.clock.tick(FPS)
            pygame.display.update()

    def main(self):
        while self.playing:
            if self.level < BOSS_LEVEL:
                self.spawn_enemies()
            elif self.level >= BOSS_LEVEL:
                self.spawn_boss()
                self.spawn_fireballs()
            self.events()
            self.update()
            self.draw()


g = Game()
g.new()
g.main_menu()
while g.running:
    g.main()
    if not g.is_won:
        g.game_over()
    else:
        g.victory()
pygame.quit()
sys.exit()
