import pygame
import os
import sys
import random
pygame.mixer.init()

pygame.mixer.music.load("fon.mp3")
pygame.mixer.music.set_volume(0.2)

def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Не удаётся загрузить:', name)
        raise SystemExit(message)
    image = image.convert_alpha()
    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    return image


pygame.init()
screen_size = (600, 600)
screen = pygame.display.set_mode(screen_size)
FPS = 50
ball = 10
gravity = 0.25
screen_rect = (0, 0, 100, 100)

tile_images = {
    'wall': load_image('derevo.png'),
    'empty': load_image('ground.jpg'),
    'door': load_image('door.png')
}
player_image = load_image('mar.png')
rat_image = load_image('rat.png', -1)
star_image = load_image('star.png', -1)
tile_width = tile_height = 50

class SpriteGroup(pygame.sprite.Group):

    def __init__(self):
        super().__init__()

    def get_event(self, event):
        for sprite in self:
            sprite.get_event(event)


class Sprite(pygame.sprite.Sprite):

    def __init__(self, group):
        super().__init__(group)
        self.rect = None

    def get_event(self, event):
        pass


class Tile(Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(sprite_group)
        if tile_type == 'door':
            self.add(door_group)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.abs_pos = [self.rect.x, self.rect.y]


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(all_sprites)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)
        #  self.last_update = pygame.time.get_ticks()


    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]
        if pygame.sprite.spritecollideany(self, hero_group):
            #  Sprite.kill(self)
            self.kill()


class Particle(pygame.sprite.Sprite):
    # сгенерируем частицы разного размера
    fire = [load_image("star.png")]
    for scale in (5, 10, 20):
        fire.append(pygame.transform.scale(fire[0], (scale, scale)))

    def __init__(self, pos, dx, dy):
        super().__init__(all_sprites)
        self.image = random.choice(self.fire)
        self.rect = self.image.get_rect()

        # у каждой частицы своя скорость - это вектор
        self.velocity = [dx, dy]
        # и свои координаты
        self.rect.x, self.rect.y = pos

        # гравитация будет одинаковой
        self.gravity = gravity

    def update(self):
        # применяем гравитационный эффект:
        # движение с ускорением под действием гравитации
        self.velocity[1] += self.gravity
        # перемещаем частицу
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        # убиваем, если частица ушла за экран
        if not self.rect.colliderect(screen_rect):
            self.kill()


def create_particles(position):
    # количество создаваемых частиц
    particle_count = 20
    # возможные скорости
    numbers = range(-5, 6)
    for _ in range(particle_count):
        Particle(position, random.choice(numbers), random.choice(numbers))


class Player(Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(hero_group)
        self.image = player_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 15, tile_height * pos_y + 5)
        self.pos = (pos_x, pos_y)
        self.abs_pos = (pos_x, pos_y)

    def move(self, x, y):
        camera.dx -= tile_width * (x - self.pos[0])
        camera.dy -= tile_width * (y - self.pos[1])
        self.pos = (x, y)
        for sprite in sprite_group:
            camera.apply(sprite)

    def update(self):
        global running
        global ball
        if pygame.sprite.spritecollideany(self, enemeis_group):
            if ball < 0:
                end_screen_lose()
                running = False
            else:
                if pygame.time.get_ticks() % 20 == 0:
                    ball -= 1
        if pygame.sprite.spritecollideany(self, freinds_group):
            if pygame.time.get_ticks() % 20 == 0:
                    ball += 1
        if pygame.sprite.spritecollideany(self, door_group):
            end_screen_win()
            running = False


class Rat(Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__([sprite_group, enemeis_group])
        self.image = rat_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 5, tile_height * pos_y + 5)
        self.pos = (pos_x, pos_y)
        self.abs_pos = (self.rect.x, self.rect.y)

    def update(self):
        pass


class Star(Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__([sprite_group, freinds_group])
        self.image = star_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 5, tile_height * pos_y + 5)
        self.pos = (pos_x, pos_y)
        self.abs_pos = (self.rect.x, self.rect.y)

    def update(self):
        pass

running = True
clock = pygame.time.Clock()
sprite_group = SpriteGroup()
hero_group = SpriteGroup()
enemeis_group = SpriteGroup()
freinds_group = SpriteGroup()
all_sprites = SpriteGroup()
door_group = SpriteGroup()


def terminate():
    pygame.quit()
    pygame.mixer.music.pause()
    sys.exit()


def end_screen_lose():
    intro_text = []

    fon = pygame.transform.scale(load_image('lose.jpg'), screen_size)
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return
        pygame.display.flip()
        clock.tick(FPS)


def end_screen_win():
    intro_text = []

    fon = pygame.transform.scale(load_image('win.jpg'), screen_size)
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return
        pygame.display.flip()
        clock.tick(FPS)


def start_screen():
    is_fine_name = False
    user = 'Введите имя:'
    instr = 'Hot keys:  left, right, up, down, ctrl + left, ctrl + right, ctl + up, ctrl + down'
    while not is_fine_name:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.unicode.isalpha():
                    user += event.unicode
                elif event.key == pygame.K_BACKSPACE:
                    user = user[:-1]
                elif event.key == pygame.K_RETURN:
                    if len(user) > 2:
                        global USERNAME
                        USERNAME = user
                        is_fine_name = True
                        break

        screen.fill((0, 0, 0))
        fon = pygame.transform.scale(load_image('zast.jpg'), [600, 600])
        screen.blit(fon, (10, 10))

        font = pygame.font.Font(None, 70)
        text_welcome = font.render("Welcome!", True, (255, 255, 255))
        screen.blit(text_welcome, (250, 70))

        font = pygame.font.Font(None, 50)
        text_user = font.render(user, True, (255, 255, 255))
        rect_user = text_user.get_rect()
        rect_user.center = screen.get_rect().center
        screen.blit(text_user, (150, 350))

        font = pygame.font.Font(None, 20)
        text_instr = font.render(instr, True, (255, 255, 255))
        screen.blit(text_instr, (40, 490))
        #  rect_instr.center = screen.get_rect().center
        #  screen.blit(text_instr, (550, 150))

        pygame.display.flip()
        clock.tick(FPS)


#  def start_screen():
    #  intro_text = []

    #  fon = pygame.transform.scale(load_image('zast.jpg'), screen_size)
    #  screen.blit(fon, (0, 0))
    #  font = pygame.font.Font(None, 30)
    #  text_coord = 50
    #  for line in intro_text:
        #  string_rendered = font.render(line, 1, pygame.Color('black'))
        #  intro_rect = string_rendered.get_rect()
        #  text_coord += 10
        #  ntro_rect.top = text_coord
        #  intro_rect.x = 10
        #  text_coord += intro_rect.height
        #  screen.blit(string_rendered, intro_rect)

    #  while True:
        #  for event in pygame.event.get():
            #  if event.type == pygame.QUIT:
                #  terminate()
            #  elif event.type == pygame.KEYDOWN or \
                    #  event.type == pygame.MOUSEBUTTONDOWN:
                #  return
        #  pygame.display.flip()
        #  clock.tick(FPS)


def load_level(filename):
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    return list(map(lambda x: list(x.ljust(max_width, '.')), level_map))


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '$':
                Tile('empty', x, y)
                Rat(x, y)
                level[y][x] = "."
            elif level[y][x] == '?':
                Tile('empty', x, y)
                Star(x, y)
                level[y][x] = "."
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)
                level[y][x] = "."
            elif level[y][x] == '!':
                Tile('door', x, y)
                level[y][x] = "."
    return new_player, x, y


def move(hero, movement):
    x, y = hero.pos
    global ball
    if movement == "up":
        if y > 0 and level_map[y - 1][x] == ".":
            hero.move(x, y - 1)
    elif movement == "dup":
        if y > 0 and level_map[y - 2][x] == ".":
            hero.move(x, y - 2)
            create_particles((x, y))
            ball -= 1

    elif movement == "down":
        if y < max_y - 1 and level_map[y + 1][x] == ".":
            hero.move(x, y + 1)
    elif movement == "ddown":
        if y < max_y - 2 and level_map[y + 2][x] == ".":
            hero.move(x, y + 2)
            create_particles((x, y))
            ball -= 1

    elif movement == "left":
        if x > 0 and level_map[y][x - 1] == ".":
            hero.move(x - 1, y)
    elif movement == "dleft":
        if x > 0 and level_map[y][x - 2] == ".":
            hero.move(x - 2, y)
            create_particles((x, y))
            ball -= 1
    elif movement == "right":
        if x < max_x - 1 and level_map[y][x + 1] == ".":
            hero.move(x + 1, y)
    elif movement == "dright":
        if x < max_x - 2 and level_map[y][x + 2] == ".":
            hero.move(x + 2, y)
            create_particles((x, y))
            ball -= 1

class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0

    def apply(self, obj):
        obj.rect.x = obj.abs_pos[0] + self.dx
        obj.rect.y = obj.abs_pos[1] + self.dy


start_screen()
pygame.mixer.music.play(-1)
camera = Camera()
level_map = load_level("map3.map")
last_update = pygame.time.get_ticks()    #  начало отсчета
hero, max_x, max_y = generate_level(level_map)
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
               move(hero, "up")
            elif event.key == pygame.K_DOWN:
                if pygame.key.get_mods() & pygame.KMOD_CTRL:
                    move(hero, "ddown")
                else:
                    move(hero, "down")
            elif event.key == pygame.K_LEFT:
                if pygame.key.get_mods() & pygame.KMOD_CTRL:
                    move(hero, "dleft")
                else:
                    move(hero, "left")
            elif event.key == pygame.K_RIGHT:
                if pygame.key.get_mods() & pygame.KMOD_CTRL:
                    move(hero, "dright")
                else:
                    move(hero, "right")

    screen.fill(pygame.Color("black"))
    sprite_group.draw(screen)
    enemeis_group.draw(screen)
    freinds_group.draw(screen)
    font = pygame.font.Font(None, 40)
    text_ball = font.render("Score:" + str(ball), True, (255, 255, 255))
    screen.blit(text_ball, (150, 570))


    sprite_group.update()
    hero_group.draw(screen)
    hero_group.update()

    fakel = AnimatedSprite(load_image("fire.png", -1), 5, 1, 60, 20)
    now = pygame.time.get_ticks()  # текущее время
    if now - last_update > 30:
        last_update = now
        all_sprites.draw(screen)  # анимация огня с задержкой относительно игрового цикла
        all_sprites.update()
    if now - last_update > 100:

        font = pygame.font.Font(None, 70)
        text_all = font.render("Time out", True, (255, 255, 255))
        screen.blit(text_ball, (150, 500))
        ball -= 1

    clock.tick(FPS)
    pygame.display.flip()
pygame.mixer.music.pause()
pygame.quit()