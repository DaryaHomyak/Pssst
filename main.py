import random
import pygame
import sys
import time
from useful_functions import load_image, print_text, load_data

# размеры экрана
WIDTH, HEIGHT = DISPLAY_SIZE = (1280, 1024)
# координаты полок по х
BAREERS = (170, 1115)
# кадров в секунду
FPS_BAREER = 5
pygame.init()
screen = pygame.display.set_mode(DISPLAY_SIZE)
pygame.display.set_caption("Pssst!")
clock = pygame.time.Clock()
# возможные позиции для предметов
BCG_STAND_POSITIONS = [[120, i * 200 + 90] for i in range(4)] + [[1110, i * 200 + 90] for i in range(4)]
flower_hp = 0
# счёт
totalizer = 0
time_count = 0
time_for_cd = 0


# спец класс для анимации спрайтов
class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y, fps_bareer, *groups):
        super().__init__(*groups)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)
        self.iteration = 0
        self._fps_bareer = fps_bareer

    # нарезка на спрайты
    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    # смена кадров
    def update(self):
        if self.iteration % self._fps_bareer == 0:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]
        self.iteration += 1


# класс жуков
class Bug(AnimatedSprite):
    # подготовка изображений
    image_l = load_image('bug.png')
    image_r = pygame.transform.flip(image_l, True, False)
    image_tofl_l = pygame.transform.scale(load_image('bugtoflower.png'), (99, 79))
    image_tofl_r = pygame.transform.flip(image_tofl_l, True, False)
    # места появления жуков
    position = [[100, i * 200 + 90] for i in range(4)] + [[1120, i * 200 + 90] for i in range(4)]
    # картинка при уничтожении
    image_destruction = load_image('destruction.png')

    def __init__(self, pos, *groups):
        self._groups = groups
        # ориентация в пространстве
        self.direction_right = True if pos < 4 else False
        self.image = Bug.image_r if self.direction_right else Bug.image_l
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x, self.rect.y = self.position[pos]
        super().__init__(self.image, 3, 1, self.rect.x, self.rect.y, FPS_BAREER, *groups)
        self.cols = 3
        self.stop = False
        self.iteration = 0
        self.small_move = False

    def update_(self):
        self.cols = 3
        self.mask = pygame.mask.from_surface(self.image)
        # убийство жука
        for p in patron_sprites_bs1:
            if pygame.sprite.collide_mask(self, p):
                self.kill()
                # анимация уничтожения
                Destruction(self.direction_right, self.rect.x, self.rect.y, all_sprites)
                global totalizer
                totalizer += 35
                return
        self.mask = pygame.mask.from_surface(Bug.image_tofl_r if self.direction_right else Bug.image_tofl_l)
        # уничтожение цветка
        if pygame.sprite.collide_mask(self, st) and self.rect.y < 860:
            global flower_hp
            flower_hp -= 1
            if flower_hp < 0:
                return start_screen()
            if not self.stop:
                if self.direction_right:
                    self.image = Bug.image_tofl_r
                    self.rect.x = 550
                else:
                    self.image = Bug.image_tofl_l
                    self.rect.x = 645
                if not self.small_move:
                    self.small_move = True
                    # небольшой сдвиг, т.к. изображение в полете и у цветка различаются по у
                    self.rect.y += 60 + random.randint(-5, 5)
            self.stop = True
            super().__init__(self.image, 1, 1, self.rect.x, self.rect.y, FPS_BAREER, *self._groups)
        # движение между барьерами
        else:
            if self.rect.x == BAREERS[0]:
                self.direction_right = True
                self.image = Bug.image_r
                self.rect.x += 5
                super().__init__(self.image, 3, 1, self.rect.x, self.rect.y, FPS_BAREER, *self._groups)

            elif self.rect.x == BAREERS[1]:
                self.direction_right = False
                self.image = Bug.image_l
                self.rect.x -= 5
                super().__init__(self.image, 3, 1, self.rect.x, self.rect.y, FPS_BAREER, *self._groups)
            else:
                if self.direction_right:
                    self.rect.x += 5
                    self.rect.y += 1
                else:
                    self.rect.x -= 5
                    self.rect.y += 1
            # если перед этим он косался цветка
            if self.stop:
                super().__init__(Bug.image_r if self.direction_right else Bug.image_l, 3, 1, self.rect.x, self.rect.y,
                                 FPS_BAREER, *self._groups)
                self.stop = False

        # пересечение барьера
        if self.rect.y == HEIGHT:
            self.kill()

    def move_to_start_pos(self):
        self.kill()


# класс мотылька
class Moth(AnimatedSprite):
    # подготовка изображений
    image_l = load_image('moth.png')
    image_r = pygame.transform.flip(image_l, True, False)
    image_tofl_l = pygame.transform.scale(load_image('mothtoflower.png'), (141, 174))
    image_tofl_r = pygame.transform.flip(image_tofl_l, True, False)
    # места появления
    position = [[100, i * 200 + 90] for i in range(4)] + [[1120, i * 200 + 90] for i in range(4)]
    y_move = 0
    stop = False

    def __init__(self, pos, *groups):
        self._groups = groups
        # ориентация в пространстве
        self.direction_right = True if pos < 4 else False
        self.image = self.image_r if self.direction_right else self.image_l
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x, self.rect.y = self.position[pos]
        super().__init__(self.image, 4, 1, self.rect.x, self.rect.y, FPS_BAREER, *groups)
        self.cols = 3
        self.small_move = False
        self.stop = False

    def update_(self):
        self.cols = 3
        self.mask = pygame.mask.from_surface(self.image)
        # убийство
        for p in patron_sprites_bs2:
            if pygame.sprite.collide_mask(self, p):
                self.kill()
                # анимация уничтожения
                Destruction(self.direction_right, self.rect.x, self.rect.y, all_sprites)
                global totalizer
                totalizer += 35  # уничтожение цветка
                return
        self.mask = pygame.mask.from_surface(Bug.image_tofl_r if self.direction_right else Bug.image_tofl_l)
        # уничтожение цветка
        if pygame.sprite.collide_mask(self, st) and self.rect.y < 860:
            global flower_hp
            flower_hp -= 1
            if not self.stop:
                if self.direction_right:
                    self.image = self.image_tofl_r
                    self.rect.x += 40
                else:
                    self.image = self.image_tofl_l
                    self.rect.x += 2
                self.rect.y += 60 + random.randint(-5, 5)
                if not self.small_move:
                    self.small_move = True
                    # небольшой сдвиг, т.к. изображение в полете и у цветка различаются по у
                    self.rect.y += 60 + random.randint(-5, 5)
            self.stop = True
            super().__init__(self.image, 1, 1, self.rect.x, self.rect.y, FPS_BAREER, *self._groups)
        # движение между барьерами
        else:
            if self.rect.x <= BAREERS[0]:
                self.direction_right = True
                self.image = self.image_r
                self.rect.x += 5
                self.y_move = random.randint(-3, 3)
                super().__init__(self.image, 4, 1, self.rect.x, self.rect.y, FPS_BAREER, *self._groups)

            elif self.rect.x + 50 >= BAREERS[1]:
                self.direction_right = False
                self.image = self.image_l
                self.rect.x -= 5
                self.y_move = random.randint(-3, 3)
                super().__init__(self.image, 4, 1, self.rect.x, self.rect.y, FPS_BAREER, *self._groups)
            else:
                if self.direction_right:
                    self.rect.x += 8
                else:
                    self.rect.x -= 8
                self.rect.y += self.y_move
            # если перед этим он косался цветка
            if self.stop:
                super().__init__(Bug.image_r if self.direction_right else Bug.image_l, 3, 1, self.rect.x, self.rect.y,
                                 FPS_BAREER, *self._groups)
                self.stop = False
        if self.rect.y == HEIGHT:
            self.kill()
        elif self.rect.y <= 0:
            self.y_move = 3

    def move_to_start_pos(self):
        self.kill()


# класс облака уничтожения
class Destruction(AnimatedSprite):
    # подготовка изображений
    image_l = load_image('destruction.png')
    image_r = pygame.transform.flip(image_l, True, False)

    def __init__(self, dir_right, pos_x, pos_y, *groups):
        self._groups = groups
        # ориентация в пространстве
        self.image = self.image_r if dir_right else self.image_l
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos_x, pos_y
        super().__init__(self.image, 6, 1, self.rect.x, self.rect.y, FPS_BAREER, *groups)
        self.iteration = 0
        self.dir_right = dir_right

    def update_(self):
        # ограничение кадров
        if self.iteration > 35:
            self.kill()
        self.iteration += 1
        self.rect.x = self.rect.x - 2 if self.dir_right else self.rect.x + 2

    def move_to_start_pos(self):
        self.kill()


# класс персонажа игрока
class Mainch(AnimatedSprite):
    # подготовка изображений
    image = load_image('mainch_rest.png')
    image_l = load_image('mainch_move.png')
    image_r = pygame.transform.flip(image_l, True, False)
    image_bs1_l = load_image('mainch_moveBS1.png')
    image_bs1_r = pygame.transform.flip(image_bs1_l, True, False)
    image_bs2_l = load_image('mainch_moveBS2.png')
    image_bs2_r = pygame.transform.flip(image_bs2_l, True, False)

    def __init__(self, *groups):
        self._groups = groups
        self.image = Mainch.image
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        # взятые баночки по умолчанию
        self.bs1, self.bs2 = False, False
        # позиция по умолчанию
        self.rect.x = WIDTH // 2 - 100
        self.rect.y = HEIGHT // 2 - 150
        self.direction_right = True
        self.last_timer = 0
        super().__init__(self.image, 1, 1, self.rect.x, self.rect.y, FPS_BAREER, *groups)

    def move(self, pressed_keys, timer):
        cols = 3
        # движение вверх/вниз/вправо/влево
        if pressed_keys[pygame.K_UP]:
            if self.rect.y > 0:
                self.rect.y -= 5
        if pressed_keys[pygame.K_DOWN]:
            if self.rect.y < HEIGHT - self.rect.size[1]:
                self.rect.y += 5
        if pressed_keys[pygame.K_LEFT]:
            self.direction_right = False
            if self.rect.x > BAREERS[0] - 50:
                self.rect.x -= 5
            if self.bs1:
                self.image = Mainch.image_bs1_l
            elif self.bs2:
                self.image = Mainch.image_bs2_l
            else:
                self.image = Mainch.image_l
            super().__init__(self.image, cols, 1, self.rect.x, self.rect.y, FPS_BAREER, *self._groups)
        if pressed_keys[pygame.K_RIGHT]:
            self.direction_right = True
            if self.rect.x < BAREERS[1] - self.rect.size[0] + 50:
                self.rect.x += 5
            if self.bs1:
                self.image = Mainch.image_bs1_r
            elif self.bs2:
                self.image = Mainch.image_bs2_r
            else:
                self.image = Mainch.image_r
            super().__init__(self.image, cols, 1, self.rect.x, self.rect.y, FPS_BAREER, *self._groups)
        # выстрел
        if pressed_keys[pygame.K_SPACE] and timer - self.last_timer >= 1:
            self.shoot()
        # возвращение спрея на полку
        if pressed_keys[pygame.K_RETURN]:
            self.busket_pass()
        self.last_timer = timer
        self.mask = pygame.mask.from_surface(self.image)

    # поднятие банки
    def busket_take(self, bs1, bs2):
        global free_shelves
        self.bs1 = bs1
        self.bs2 = bs2
        pos = self.shelf_info()
        if pos != -1:
            free_shelves.add(pos)

    # взятые банки
    def busket_info(self):
        return self.bs1, self.bs2

    # определение полки у персонажа
    def shelf_info(self):
        if (180 >= self.rect.x or 800 <= self.rect.x) and (self.bs1 or self.bs2):
            past_pos = [-50, -50]
            # перебор всех возможных позиций
            for pos in BCG_STAND_POSITIONS:
                # если полка рядом с персонажем
                if past_pos[1] <= self.rect.y <= pos[1] and (abs(self.rect.x - pos[0]) < 300):
                    return BCG_STAND_POSITIONS.index(pos)
                past_pos[0] = pos[0]
                past_pos[1] = pos[1] if pos[1] != 690 else -50
        else:
            return -1

    # функция для возвращения спрея на полку
    def busket_pass(self):
        global free_shelves
        pos = self.shelf_info()
        if pos != -1 and pos in free_shelves:
            # спавним спрей на этой позиции
            Busket(pos, self.bs1, self.bs2, busket_sprites, all_sprites)
            global time_count, time_for_cd
            time_for_cd = int(time.strftime("%S", time.gmtime(time_count)))
            free_shelves.remove(pos)

            self.bs1, self.bs2 = False, False

    # возвращение на старт
    def move_to_start_pos(self):
        self.rect.x = WIDTH // 2 - 100
        self.rect.y = HEIGHT // 2 - 150
        self.image = Mainch.image
        self.bs1, self.bs2 = False, False
        super().__init__(self.image, 1, 1, self.rect.x, self.rect.y, FPS_BAREER, *self._groups)

    # выстрел
    def shoot(self):
        if self.bs1:
            Patron(self.rect.x + 50, self.rect.y + 80, True, False, self.direction_right, all_sprites,
                   patron_sprites_bs1)
        elif self.bs2:
            Patron(self.rect.x + 50, self.rect.y + 80, False, True, self.direction_right, all_sprites,
                   patron_sprites_bs2)

    def update_(self):
        pass


# класс баночек
class Busket(pygame.sprite.Sprite):
    # подготовка изображений
    image_bs2 = pygame.transform.scale(load_image('busket2.png'), (78, 107))
    image_bs1 = pygame.transform.scale(load_image('busket1.png'), (62, 106))
    position = [[100, i * 200 + 90] for i in range(4)] + [[1120, i * 200 + 90] for i in range(4)]

    def __init__(self, pos, bs1, bs2, *groups):
        super().__init__(*groups)
        self.bs1, self.bs2 = bs1, bs2
        self.image = load_image('water_can.png')
        if bs1:
            self.image = Busket.image_bs1
        if bs2:
            self.image = Busket.image_bs2
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = BCG_STAND_POSITIONS[pos]
        self.mask = pygame.mask.from_surface(self.image)

    def update_(self):
        global time_for_cd
        if pygame.sprite.collide_mask(self, ch) and ch.busket_info() == (False, False) and time_for_cd + 1 < int(
                time.strftime("%S", time.gmtime(time_count))):
            self.kill()
            ch.busket_take(self.bs1, self.bs2)

    def move_to_start_pos(self):
        global free_shelves
        if ch.busket_info()[0]:
            print(1, self.bs1, ch.busket_info())
            b_place = random.sample(free_shelves, 1)[0]
            free_shelves.remove(b_place)
            Busket(b_place, True, False, busket_sprites, all_sprites)
            self.bs1 = False
        elif ch.busket_info()[1]:
            print(2, self.bs2, ch.busket_info())
            b_place = random.sample(free_shelves, 1)[0]
            free_shelves.remove(b_place)
            Busket(b_place, False, True, busket_sprites, all_sprites)
            self.bs2 = False


# класс бонусов
class Bonus(pygame.sprite.Sprite):
    images = [load_image('fertilizer.png'), load_image('fly_swatter.png'), load_image('water_can.png')]
    position = [[100, i * 200 + 90] for i in range(4)] + [[1120, i * 200 + 90] for i in range(4)]

    def __init__(self, pos, *groups):
        super().__init__(*groups)
        self.image = self.images[random.randint(0, 2)]
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = BCG_STAND_POSITIONS[pos]
        self.mask = pygame.mask.from_surface(self.image)

    def move_to_start_pos(self):
        self.kill()

    def update_(self):
        if pygame.sprite.collide_mask(self, ch):
            self.kill()
            # возвращение свободного места на полках
            pos = ch.shelf_info()
            if pos != -1:
                free_shelves.add(pos)
            # обновление счета
            global totalizer
            totalizer += 1000


# класс патронов
class Patron(pygame.sprite.Sprite):
    image_bs1_l = pygame.transform.scale(load_image('patron1.png'), (49, 44))
    image_bs1_r = pygame.transform.flip(image_bs1_l, True, False)
    image_bs2_l = pygame.transform.scale(load_image('patron2.png'), (44, 30))
    image_bs2_r = pygame.transform.flip(image_bs2_l, True, False)

    def __init__(self, x, y, bs1, bs2, direction_right, *groups):
        super().__init__(*groups)
        self.drct_r = direction_right
        if bs1:
            if self.drct_r:
                self.image = Patron.image_bs1_r
            else:
                self.image = Patron.image_bs1_l
        if bs2:
            if self.drct_r:
                self.image = Patron.image_bs2_r
            else:
                self.image = Patron.image_bs2_l
        self.bs1, self.bs2 = bs1, bs2
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.mask = pygame.mask.from_surface(self.image)

    def move_to_start_pos(self):
        self.kill()

    def update_(self):
        if self.drct_r:
            self.rect.x += 10
        else:
            self.rect.x -= 10
        if self.rect.x == 0 or self.rect.x == 1280:
            self.kill()


class Stalk(pygame.sprite.Sprite):
    image_stalk = load_image('stalk.png')
    frames = []
    frames_y = []
    cur_frame = 0
    # создание 7 фреймов стеблей разного размера
    for i in range(1, 8):
        frames.append(pygame.transform.scale(image_stalk, (7 * i, 79 * i)))
        frames_y.append(79 * i)

    def __init__(self, *groups):
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = WIDTH // 2, HEIGHT - self.frames_y[0]
        self.mask = pygame.mask.from_surface(self.image)
        self.stop = False
        super().__init__(*groups)

    def move_to_start_pos(self):
        global flower_hp
        flower_hp = 0

    def grow(self):
        pass

    def update_(self):
        global flower_hp
        self.cur_frame = flower_hp // 300
        if flower_hp < 1900:
            self.image = self.frames[self.cur_frame]
            self.mask = pygame.mask.from_surface(self.image)
            self.rect.y = HEIGHT - self.frames_y[self.cur_frame]
        elif not self.stop:
            Flower(flower_sprites, all_sprites)
            self.stop = True


class Flower(pygame.sprite.Sprite):
    frames = []
    cur_frame = 0
    fl_iteration = 0

    def __init__(self, *groups):
        sheet = load_image('flower.png')
        self.rect = pygame.Rect(0, 0, sheet.get_width() // 4,
                                sheet.get_height() // 1)
        for j in range(1):
            for i in range(4):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = 430, 300
        super().__init__(*groups)

    def move_to_start_pos(self):
        self.kill()

    def grow(self):
        self.fl_iteration += 1
        if self.fl_iteration >= 10:
            if self.cur_frame < 4:
                self.image = self.frames[self.cur_frame]
                self.rect.y = 300
                self.rect.x = 430
            self.cur_frame += 1
            self.fl_iteration = 0

    def update_(self):
        pass


# создание объектов
all_sprites = pygame.sprite.Group()
busket_sprites = pygame.sprite.Group()
ch_sprites = pygame.sprite.Group()
ch = Mainch(ch_sprites, all_sprites)
patron_sprites_bs1 = pygame.sprite.Group()
patron_sprites_bs2 = pygame.sprite.Group()
bugs_sprites = pygame.sprite.Group()
moths_sprites = pygame.sprite.Group()
flower_sprites = pygame.sprite.Group()
st = Stalk(flower_sprites, all_sprites)
free_shelves = set(range(8))
b_place = random.sample(free_shelves, 1)[0]
free_shelves.remove(b_place)
busket1 = Busket(b_place, True, False, busket_sprites, all_sprites)
b_place = random.sample(free_shelves, 1)[0]
free_shelves.remove(b_place)
busket2 = Busket(b_place, False, True, busket_sprites, all_sprites)
player_lives = 1


# начальный экран
def start_screen():
    work = True
    while work:
        screen.blit(load_image('startscreen.jpg'), (0, 0))
        play_btn = print_text(screen, 'Play', 200, 755, 'white', 190, 'white', 20, 5)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                #  проверка на клик по кнопкам
                if play_btn[0] < event.pos[0] < play_btn[2] and play_btn[1] < event.pos[1] < play_btn[3]:
                    return level_1()
        pygame.display.flip()


def level_1():
    global flower_hp
    global player_lives
    global time_count
    global free_shelves
    global totalizer
    # очистка
    for s in all_sprites:
        if ch_sprites not in s.groups():
            s.move_to_start_pos()
    ch.move_to_start_pos()

    player_lives = 4
    time_count = 0
    totalizer = 0
    clear_timer = 0
    running = True
    iter_stage = 0

    FLOWER_GROW = pygame.USEREVENT + 1
    TIMEREVENT = pygame.USEREVENT + 2
    ENEMYSPAWN = pygame.USEREVENT + 3
    CH_MOVING = pygame.USEREVENT + 4
    CLEAR_TIMER = pygame.USEREVENT + 5
    BONUS_SPAWN = pygame.USEREVENT + 6

    moving, keys_list = False, []

    pygame.time.set_timer(CH_MOVING, 10)
    pygame.time.set_timer(FLOWER_GROW, 1000)
    pygame.time.set_timer(TIMEREVENT, 1000)
    pygame.time.set_timer(ENEMYSPAWN, 5000)
    pygame.time.set_timer(CLEAR_TIMER, 500)
    pygame.time.set_timer(BONUS_SPAWN, 30000)

    while running:
        # отрисовка фона
        screen.blit(load_image('background.jpg'), (0, 0))
        # отрисовка кол-ва жизней игрока
        print_text(screen, str(player_lives), 500, 10, 'white', 100)
        screen.blit(pygame.transform.scale(load_image('mainch_rest.png'), (45, 56)), (560, 20))
        # убийство персонажа
        for b in bugs_sprites:
            if pygame.sprite.collide_mask(ch, b):
                player_lives -= 1
                if player_lives > 0:
                    # очистка уровня
                    for s in all_sprites:
                        if ch_sprites not in s.groups():
                            s.move_to_start_pos()
                    ch.move_to_start_pos()
                else:
                    return start_screen()
        for event in pygame.event.get():
            # выход из игры
            if event.type == pygame.QUIT:
                running = False
            # удержание клавиш
            if event.type == pygame.KEYDOWN:
                moving, keys_list = True, pygame.key.get_pressed()
                if keys_list[pygame.K_ESCAPE]:
                    running = False
            if moving and event.type == CH_MOVING:
                ch.move(keys_list, clear_timer)
            if event.type == pygame.KEYUP:
                moving = False
            if event.type == FLOWER_GROW:
                flower_hp += 30
                if flower_hp >= 2000:
                    for fl in flower_sprites:
                        fl.grow()
                    iter_stage += 1
                if iter_stage // 10 >= 5:
                    return level_2()
            if event.type == TIMEREVENT:
                time_count += 1
            if event.type == CLEAR_TIMER:
                clear_timer += 1
            if event.type == ENEMYSPAWN:
                Bug(random.randint(0, 7), bugs_sprites, all_sprites)
            if event.type == BONUS_SPAWN and len(free_shelves) > 0:
                b_place = random.sample(free_shelves, 1)[0]
                free_shelves.remove(b_place)
                Bonus(b_place, all_sprites)
        for a in all_sprites:
            a.update_()
        all_sprites.update()
        # отрисовка гг
        all_sprites.draw(screen)
        # отрисовка  таймера
        print_text(screen, time.strftime("%M:%S", time.gmtime(time_count)), 10, 10, 'white', 100)
        print_text(screen, str(totalizer), 300, 10, 'white', 100)
        print_text(screen, "LEVEL 1", 800, 10, 'white', 100)
        pygame.display.flip()


def level_2():
    global flower_hp
    global player_lives
    global time_count
    global free_shelves

    # очистка
    for s in all_sprites:
        if ch_sprites not in s.groups():
            s.move_to_start_pos()
    ch.move_to_start_pos()

    player_lives = 4
    time_count = 0
    clear_timer = 0
    running = True
    iter_stage = 0

    FLOWER_GROW = pygame.USEREVENT + 1
    TIMEREVENT = pygame.USEREVENT + 2
    ENEMYSPAWN = pygame.USEREVENT + 3
    CH_MOVING = pygame.USEREVENT + 4
    CLEAR_TIMER = pygame.USEREVENT + 5
    BONUS_SPAWN = pygame.USEREVENT + 6

    moving, keys_list = False, []

    pygame.time.set_timer(CH_MOVING, 10)
    pygame.time.set_timer(FLOWER_GROW, 1000)
    pygame.time.set_timer(TIMEREVENT, 1000)
    pygame.time.set_timer(ENEMYSPAWN, 5000)
    pygame.time.set_timer(CLEAR_TIMER, 500)
    pygame.time.set_timer(BONUS_SPAWN, 30000)

    while running:
        # отрисовка фона
        screen.blit(load_image('background.jpg'), (0, 0))
        # отрисовка кол-ва жизней игрока
        print_text(screen, str(player_lives), 500, 10, 'white', 100)
        screen.blit(pygame.transform.scale(load_image('mainch_rest.png'), (45, 56)), (560, 20))
        # убийство персонажа
        for b in bugs_sprites:
            if pygame.sprite.collide_mask(ch, b):
                player_lives -= 1
                if player_lives > 0:
                    # очистка уровня
                    for s in all_sprites:
                        if ch_sprites not in s.groups():
                            s.move_to_start_pos()
                    ch.move_to_start_pos()
                else:
                    return start_screen()

        for event in pygame.event.get():
            # выход из игры
            if event.type == pygame.QUIT:
                running = False
            # удержание клавиш
            if event.type == pygame.KEYDOWN:
                moving, keys_list = True, pygame.key.get_pressed()
                if keys_list[pygame.K_ESCAPE]:
                    running = False
            if moving and event.type == CH_MOVING:
                ch.move(keys_list, clear_timer)
            if event.type == pygame.KEYUP:
                moving = False
            if event.type == FLOWER_GROW:
                flower_hp += 30
                if flower_hp >= 2000:
                    for fl in flower_sprites:
                        fl.grow()
                    iter_stage += 1
                if iter_stage // 10 >= 5:
                    # победа игрока, запись результатов
                    load_data('res.dat', totalizer, time.strftime("%M:%S", time.gmtime(time_count)))
                    return start_screen()
            if event.type == TIMEREVENT:
                time_count += 1
            if event.type == CLEAR_TIMER:
                clear_timer += 1
            if event.type == ENEMYSPAWN:
                if random.randint(0, 1) == 0:
                    Bug(random.randint(0, 7), bugs_sprites, all_sprites)
                else:
                    Moth(random.randint(0, 7), bugs_sprites, all_sprites)
            if event.type == BONUS_SPAWN and len(free_shelves) > 0:
                b_place = random.sample(free_shelves, 1)[0]
                free_shelves.remove(b_place)
                Bonus(b_place, all_sprites)
        for a in all_sprites:
            a.update_()
        all_sprites.update()
        # отрисовка гг
        all_sprites.draw(screen)
        # отрисовка  таймера
        print_text(screen, time.strftime("%M:%S", time.gmtime(time_count)), 10, 10, 'white', 100)
        print_text(screen, str(totalizer), 300, 10, 'white', 100)
        print_text(screen, "LEVEL 2", 800, 10, 'white', 100)
        pygame.display.flip()


# запуск начального экрана
start_screen()
pygame.quit()
