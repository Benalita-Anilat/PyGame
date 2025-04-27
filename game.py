import pygame
import sys
import json
from os import path
from itertools import product
from random import shuffle, choice
# ОФОРМЛЕНИЕ ИГРЫ
# размер экрана
Width, Height = 520, 660
screen_rect = (0, 0, Width, Height)
# обновление экрана
FPS = 30
# цвет текста и таблицы, цвет фона, цвет верно выбранной ячейки
textcolor = pygame.Color("white")
fon = pygame.Color(0)
good = pygame.Color("green")
# шрифт
font_name = pygame.font.match_font('arial')

# загрузка изображений
def load_image(name, colorkey=None):
    fullname = path.join('data', name)
    if not path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    return image

# загрузка музыки
def load_music(name):
    fullname = path.join('data', name)  # поменять папку на музыка
    try:
        music = pygame.mixer.music.load(fullname)
    except pygame.error as message:
        print('Не удаётся загрузить:', fullname)
        raise SystemExit(message)
    return music

# загрузка звукового сигнала
def load_sound(name):
    fullname = path.join('data', name)  # поменять папку на музыка
    try:
        sound = pygame.mixer.Sound(fullname)
    except pygame.error as message:
        print('Не удаётся загрузить:', fullname)
        raise SystemExit(message)
    return sound

# проигрывание звукового сигнала
def beep(name):
    load_sound(name).play()

# проигрывание фоновой музыки
def music(filename):
    load_music(filename)
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play()

# вывод текста на экран, по умолчанию - белого цвета
def draw_text(surface, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, textcolor)
    text_rect = text_surface.get_rect(midtop=(x, y))
    surface.blit(text_surface, text_rect)

# вывод многострочного текста на экран
def draw_multiline_text(surface, text_in_list, size, x, y):
    for i, line in enumerate(text_in_list):
        draw_text(surface, line, size, x, y + size * i)

# перемешанный список чисел от 1 до 100
def shuffled_numbers():
    start, finish = 1, 100
    numbers_list = list(range(start, finish + 1))
    shuffle(numbers_list)
    return [[numbers_list[10 * i + j] for i in range(10)] for j in range(10)]

# максимальное количество очков в уровне
def max_score(level):
    return sum(1 for i in range(1, 101) if i % level == 0)

# завершение работы программы
def terminate():
    pygame.quit()
    sys.exit()
# КЛАССЫ ОБЪЕКТОВ ИГРЫ
# текущая игра (имя игрока и результаты)
class Game:
    def __init__(self):
        self.game_is_on = True
        self.is_played = False
        self.player_name = 'Player'
        self.results = [0] * 9
        self.level_number = 1
        self.level_score = 0
        self.level_result = self.level_score / max_score(self.level_number)
        self.set_results_file()

    def set_results_file(self):
        data = {"self.player_name": self.results}
        with open(path.join('data', 'results.json'), 'w', encoding='utf-8') as f:  # type: typing.IO[str]
            json.dump(data, f, ensure_ascii=False)

    # запись результата уровня в файл
    def save_results(self):
        with open(path.join('data', 'results.json'), 'rt', encoding='utf-8') as f: # type: typing.IO[str]
            data = json.load(f)
        data[self.player_name] = self.results
        with open(path.join('data', 'results.json'), 'w', encoding='utf-8') as f:  # type: typing.IO[str]
                json.dump(data, f, ensure_ascii=False)

    # загрузка предыдущих результатов игрока из файла
    def load_results(self):
        with open(path.join('data', 'results.json'), 'rt', encoding='utf-8') as file: # type: typing.IO[str]
            data = json.load(file)
        self.results = data[self.player_name]

new_game = Game()
# Элементы управления
# Ввод текста (имя игрока)
class TextInputBox(pygame.sprite.Sprite):
    def __init__(self, x, y, w, font_name):
        super().__init__()
        self.rect = None
        self.image = None
        self.color = (180, 180, 180)
        self.pos = (x, y)
        self.width = w
        self.font = pygame.font.Font(font_name, 32)
        self.active = False
        self.text = "Player"
        self.render_text()

    def render_text(self):
        t_surf = self.font.render(self.text, True, self.color, fon)
        self.image = pygame.Surface((max(self.width, t_surf.get_width() + 10), t_surf.get_height() + 10), pygame.SRCALPHA)
        self.image.fill(fon)
        self.image.blit(t_surf, (5, 5))
        pygame.draw.rect(self.image, "#FFFFFF", self.image.get_rect().inflate(-2, -2), 2)
        self.rect = self.image.get_rect(topleft=self.pos)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and not self.active:
            self.active = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                self.active = False
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode
            self.render_text()

# Кнопка
class Button(pygame.sprite.Sprite):
    def __init__(self, x, y, text, callback):
        super().__init__()
        self.rect = None
        self.image = None
        self.textcolor = 0
        self.backcolor = '#aaaaaa'
        self.pos = (x, y)
        self.font = pygame.font.SysFont('arial', 30)
        self.text = text
        self.is_hovered = False
        self.callback = callback
        self.draw()

    def handle_event(self, event):
        color_down, color_over = '#585858', '#cccccc'
        self.backcolor = '#aaaaaa'
        if event.type ==  pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos):
            self.backcolor = color_down
        if event.type ==  pygame.MOUSEBUTTONUP and event.button == 1 and self.rect.collidepoint(event.pos):
            self.callback()
        if event.type == pygame.MOUSEMOTION and self.rect.collidepoint(event.pos):
            self.is_hovered = True
            self.backcolor = color_over
        self.draw()

    def draw(self):
        surf = self.font.render(self.text, True, self.textcolor, self.backcolor)
        self.image = pygame.Surface((surf.get_width() + 20, surf.get_height() + 10))
        self.image.fill(self.backcolor)
        self.image.blit(surf, (10, 5))
        #рамка
        pygame.draw.rect(self.image, self.textcolor, self.image.get_rect().inflate(-2, -2), 3)
        self.rect = self.image.get_rect(topleft=self.pos)
# Изображения
# Котенок на стартовом экране и экране с результатами
class Kitten(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        if not new_game.game_is_on:
            filename = "sleepy_cat.png"
        elif new_game.level_number == 0:
            filename = "cat.png"
        elif new_game.level_result >= 0.8:
            filename = "happy_cat.png"
        else:
            filename = "sad_cat.png"
        self.image = load_image(filename)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.mask = pygame.mask.from_surface(self.image)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if kitten.rect.collidepoint(event.pos):
                music('meow.mp3')

kitten = Kitten(142, 300)

# трава фоновая
class Grass(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = load_image("grass.png")
        self.rect = self.image.get_rect(topleft=(x, y))
        self.mask = pygame.mask.from_surface(self.image)

    def handle_event(self, event):
        pass

grass = Grass(0, 500)

# граница зоны рисунка
class Border(pygame.sprite.Sprite):
    def __init__(self, x1, y1, x2, y2):
        super().__init__()
        self.image = pygame.Surface((x2 - x1, y2 - y1))
        self.rect = pygame.Rect(x1, y1, x2 - x1, y2 - y1)
        self.mask = pygame.mask.from_surface(self.image)

horisont = Border(0, 590, Width, Height)
# звездный фонтан из урока PyGame8
numbers = range(-6, 6)
# Звездочки для звёздного фонтана
class Star(pygame.sprite.Sprite):
    def __init__(self, dx, dy):
        super().__init__()
        star = load_image("star.png")
        if 0.8 <= new_game.level_result < 1:
            star = pygame.transform.grayscale(star)
        self.expl = [star]
        for scale in range(5, 25, 3):
            self.expl.append(pygame.transform.scale(self.expl[0], (scale, scale)))
        self.image = choice(self.expl)
        self.rect = self.image.get_rect()
        self.velocity = [dx, dy]
        self.rect.x, self.rect.y = (260, 70)
        self.gravity = 0.1
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.velocity[1] += self.gravity
        if all(not pygame.sprite.collide_mask(self, i)
                   for i in (grass, kitten)):
            self.rect.x += self.velocity[0]
            self.rect.y += self.velocity[1]
        if not self.rect.colliderect(screen_rect):
            self.kill()

    def handle_event(self, event):
        pass

# Монетка-медаль за прохождение уровня
class Coin(pygame.sprite.Sprite):
    def __init__(self, size, x, y):
        super().__init__()
        self.width, self.height = size
        image = load_image("starcoin0.png")
        if 0.8 <= new_game.level_result < 1:
            image = pygame.transform.grayscale(image)
        self.image = image
        self.rect = self.image.get_rect(midtop=(x, y))
        self.count = 0

    def handle_event(self, event):
        pass

# Базовое игровое поле
class Board:
    def __init__(self, width, height):
        #super().__init__()
        self.width, self.height = width, height
        self.left, self.top = 10, 10
        self.cell_size = 50
        self.board = [[0] * width for _ in range(height)]
        self.image = pygame.Surface((width * self.cell_size, height * self.cell_size))
        self.rect = self.image.get_rect()
        self.is_empty = True

    def put_content(self, number, x0, y0, s, screen):
        pass

    def render(self,screen):
        s = self.cell_size
        self.image.fill(0)
        for x, y in product(range(self.width), range(self.height)):
            x0 = x * s + self.left
            y0 = y * s + self.top
            if not self.is_empty:
                self.put_content(self.board[y][x], x0, y0, s, screen)
            pygame.draw.rect(screen, textcolor, (x0, y0, s, s), 1)

    def get_cell(self, mouse_pos):
        cell_x = (mouse_pos[0] - self.left) // self.cell_size
        cell_y = (mouse_pos[1] - self.top) // self.cell_size
        if not (0 <= cell_x < self.width and 0 <= cell_y < self.height):
            return None
        return cell_x, cell_y

    def on_click(self, cell):
        pass

    def get_click(self, mouse_pos):
        cell = self.get_cell(mouse_pos)
        if cell:
            self.on_click(cell)
        else:
            return None

# Поле выбора уровня
class Menu(Board):
    def __init__(self, width, height):
        super().__init__(width, height)
        self.left = 35
        self.top = 480
        self.board[0] = list(range(2, width + 2))
        self.board[1] = new_game.results
        self.is_empty = False

    def put_content(self, number, x0, y0, s, screen):
        draw_text(screen, str(number), 28, x0 + 20, y0 + 10)

    def on_click(self, cell):
        music('click.mp3')
        new_game.level_number = self.board[cell[1]][cell[0]]
        MenuScreen.done = True
        LevelScreen().run()

# Поле уровня
class Level(Board):
    def __init__(self, width, height):
        super().__init__(width, height)
        self.board = shuffled_numbers()
        self.divider = new_game.level_number
        self.max_score = max_score(new_game.level_number)
        self.time = 2 * self.max_score
        self.score = 0
        self.found_numbers = 0
        self.is_empty = False

    def put_content(self, number, x0, y0, s, screen):
        if number < 0:
            pygame.draw.rect(screen, good, (x0, y0, s, s))
        else:
            draw_text(screen, str(number), 28, x0 + 20, y0 + 10)

    def on_click(self, cell):
        if self.board[cell[1]][cell[0]] % self.divider == 0:
            self.board[cell[1]][cell[0]] *= -1
            self.score += 1
            self.found_numbers += 1
            self.time += 1
        else:
            self.score -= 1
            beep('beep.wav')

# Экраны
class Screen:
    def __init__(self):
        self.width, self.height = Width, Height
        self.fill = fon
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.title = "Знаю,что поделится!"
        pygame.display.set_caption(self.title)
        self.clock = pygame.time.Clock()
        self.done = False
        self.board = None
        self.buttons = None

    def run(self):
        while not self.done:
            self.handle_events()
            self.run_logic()
            self.draw()
            self.clock.tick(FPS)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.done = True
                terminate()
            if self.board:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.board.get_click(event.pos)
            if self.buttons:
                for button in self.buttons:
                    button.handle_event(event)

    def run_logic(self):
        if self.buttons:
            self.buttons.update()

    def draw(self):
        if self.board:
            self.screen.fill(fon)
            self.board.render(self.screen)
        if self.buttons:
            self.buttons.draw(self.screen)
        pygame.display.flip()

    def go_to_menu(self):
        self.done = True

    def exit_button(self):
        new_game.game_is_on = False
        self.done = True

# Стартовый экран
class StartScreen(Screen):
    def __init__(self):
        super().__init__()
        draw_text(self.screen, 'Что поделится?', 60, Width / 2, 30)
        with open('data/rules.txt', encoding='utf-8') as file:
            intro_text = list(map(str.rstrip, file.readlines()))
        draw_multiline_text(self.screen, intro_text, 24, Width / 2, 130)
        self.buttons = pygame.sprite.Group(kitten, Button(200, 600, 'Старт', self.go_to_menu))

# Экран авторизации
class AuthScreen(Screen):
    def __init__(self):
        super().__init__()
        player_name = TextInputBox(35, 350, 350, font_name)
        self.player = player_name.text
        self.buttons = pygame.sprite.Group(player_name, Button(410, 350, ' Ок ', self.ok_button))

    def ok_button(self):
        new_game.player_name = self.player
        new_game.save_results()
        self.done = True
        MenuScreen().run()

    def draw(self):
        self.screen.fill(fon)
        self.buttons.draw(self.screen)
        draw_text(self.screen, 'Введи своё имя:', 32, 135, 300)
        pygame.display.flip()

# Экран меню игры
class MenuScreen(Screen):
    def __init__(self):
        super().__init__()
        self.buttons = pygame.sprite.Group(Button(220, 600, 'Выход', self.exit_button))
        self.board = Menu(9, 2)

    def draw(self):
        self.screen.fill(fon)
        self.buttons.draw(self.screen)
        self.board.render(self.screen)
        draw_text(self.screen, 'Выбери уровень:', 32, 260, 420)
        pygame.display.flip()

# Экран уровня игры
class LevelScreen(Screen):
    def __init__(self):
        super().__init__()
        self.n = new_game.level_number
        self.board = Level(10, 10)
        self.seconds = None

    def run(self):
        if new_game.level_number % 2:
            music('background_music.mp3')
        else:
            music('background_music1.mp3')
        start_ticks = pygame.time.get_ticks()
        while not self.done:
            self.handle_events()
            self.run_logic()
            self.draw()
            self.clock.tick(FPS)
            self.seconds = self.board.time - int((pygame.time.get_ticks() - start_ticks) / 1000)

    def run_logic(self):
        if self.seconds == 0 or self.board.found_numbers == self.board.max_score:
            pygame.mixer.music.stop()
            beep('win_sound.wav')
            new_game.level_score = self.board.score
            new_game.level_result = round(self.board.score / self.board.max_score, 1)
            new_game.results[self.n - 2] = new_game.level_result
            new_game.save_results()
            self.done = True
            ResultOfTheLevelScreen().run()

    def draw(self):
        self.screen.fill(fon)
        self.board.render(self.screen)
        draw_text(self.screen, f'Нужно найти {self.board.max_score} чисел', 24, 265, 530)
        draw_text(self.screen, f'Время: {self.seconds}', 30, 70, 580)
        draw_text(self.screen, f'Очки: {str(self.board.score)}', 30, 460, 580)
        draw_text(self.screen, f'Делитель: {str(self.board.divider)}', 30, 265, 580)
        pygame.display.flip()

# Экран результата прохождения уровня
class ResultOfTheLevelScreen(Screen):
    def __init__(self):
        super().__init__()
        kitten = Kitten(142, 300)
        self.buttons = pygame.sprite.Group(grass, kitten, Button(220, 600, 'Меню', self.go_to_menu))

    def run(self):
        if new_game.level_result >= 0.8:
            self.buttons.add(Coin((100, 100), Width / 2, 80))
            result_of_the_level_music = 'win.mp3'
        else:
            result_of_the_level_music = 'loose.mp3'
        music(result_of_the_level_music)
        while not self.done:
            self.screen.fill(fon)
            if new_game.level_result >= 0.8:
                self.buttons.add(Star(choice(numbers), choice(numbers)))
            draw_text(self.screen, f'Уровень: {new_game.level_number}', 28, 70, 20)
            draw_text(self.screen, f'Максимум: {str(max_score(new_game.level_number))}', 28, 440, 20)
            draw_text(self.screen, f'Твои очки: {new_game.level_score}', 28, 265, 20)
            self.handle_events()
            self.run_logic()
            self.draw()
            self.clock.tick(FPS)

# Финальный экран
class FinalScreen(Screen):
    def __init__(self):
        super().__init__()
        draw_text(self.screen, "Конец игры.", 48, Width / 2, Height / 2 - 150)
        draw_text(self.screen, "Время отдохнуть.", 48, Width / 2, Height / 2 - 80)
        music('game_over_man_voice.mp3')
        self.buttons = pygame.sprite.Group(Kitten(142, 300))

def main():
    pygame.init()
    StartScreen().run()
    AuthScreen().run()
    while new_game.game_is_on:
        MenuScreen().run()
    FinalScreen().run()

if __name__ == '__main__':
    main()