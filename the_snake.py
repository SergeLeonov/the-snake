from random import choice, randint

import pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)
# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)
# Цвет яблока
APPLE_COLOR = (255, 0, 0)
# Цвет змейки
SNAKE_COLOR = (0, 255, 0)
# Скорость движения змейки:
SPEED = 10
# Настройка игрового окна:
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')
# Настройка времени:
clock = pygame.time.Clock()
# Координаты старта змейки
snake_start_x, snake_start_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
snake_start = (snake_start_x, snake_start_y)
# Начальные координаты яблока
apple_start_random = randint(0, GRID_WIDTH - 1) * GRID_SIZE
apple_start_xy = (apple_start_random, apple_start_random)


class GameObject:
    """
    Базовый класс игровых объектов.

    Хранит позицию и цвет, предоставляет шаблон для отрисовки.
    Классы Apple и Snake наследуются от него.
    """

    def __init__(self, position=None, body_color=None):
        """
        Инициализирует объект позицией и цветом.

        Args:
            position (tuple[int, int] | None): координаты (x, y).
            Если None — остаётся None.
            body_color (tuple[int, int, int] | None): цвет в формате RGB.
            Если None — остаётся None.
        """
        self.position = position
        self.body_color = body_color

    def draw(self):
        """
        Отрисовывает объект на экране.

        По умолчанию ничего не делает:
        переопределяется в дочерних классах
        """
        pass


class Apple(GameObject):
    """
    Класс яблока — цель для змейки.

    Создаёт яблоко в случайной позиции на сетке, умеет менять позицию
    и отрисовывать себя как цветной квадрат с рамкой.
    """

    def __init__(self, position=apple_start_xy, body_color=APPLE_COLOR):
        """
        Создаёт яблоко.

        Если позиция не передана, генерируется случайная позиция на сетке.

        Args:
            position (tuple[int, int] | None): начальная позиция (x, y).
            body_color (tuple[int, int, int]): цвет яблока (красный).
        """
        super().__init__(position, body_color)
        self.position = position
        self.body_color = body_color

    def randomize_position(self):
        """
        Перемещает яблоко в новую случайную позицию на сетке.

        Позиция выбирается так, чтобы центр яблока совпадал с узлами сетки.

        Returns:
            tuple[int, int]: новая позиция (x, y).
        """
        apple_position_x = randint(0, GRID_WIDTH - 1) * GRID_SIZE
        apple_position_y = randint(0, GRID_HEIGHT - 1) * GRID_SIZE
        self.position = (apple_position_x, apple_position_y)
        return self.position

    def draw(self):
        """Отрисовывает яблоко как цветной прямоугольник с рамкой."""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """
    Класс змейки — основной управляемый объект игры.

    Управляет списком позиций сегментов, направлением движения, ростом,
    проверкой столкновений и отрисовкой.
    """

    def __init__(self,
                 length=1,
                 positions=[snake_start],
                 direction=RIGHT,
                 body_color=SNAKE_COLOR,
                 next_direction=None
                 ):
        """Создаёт змейку.

        Args:
            length (int): начальная длина змейки (количество сегментов).
            positions (list[tuple[int, int]] | None): список позиций сегментов.
                Если None — создаётся список из одной стартовой позиции.
            direction (tuple[int, int]): текущее направление движения.
            body_color (tuple[int, int, int]): цвет змейки.
            next_direction (tuple[int, int] | None): направление, которое будет
                применено на следующем кадре (для обработки нажатий клавиш).
        """
        super().__init__(positions[0], body_color)
        self.length = length
        self.positions = positions
        self.direction = direction
        self.body_color = body_color
        self.next_direction = next_direction

    def get_head_position(self):
        """Возвращает позицию головы змейки.

        Returns:
            tuple[int, int]: координаты головы (x, y).
        """
        return self.positions[0]

    def move(self):
        """
        Вычисляет новую позицию головы и обновляет список сегментов.

        Новая голова добавляется в начало списка. Если длина списка превышает
        допустимую (self.length), удаляется последний сегмент хвоста.
        Реализует «проход сквозь стены» посредствам поиска в пространстве
        головы змеи и "телепортации" в нужную точку.
        """
        head_position = self.get_head_position()
        new_head_position_x = head_position[0] + GRID_SIZE * self.direction[0]
        new_head_position_y = head_position[1] + GRID_SIZE * self.direction[1]

        if new_head_position_x % SCREEN_WIDTH == SCREEN_WIDTH - GRID_SIZE:
            new_head_position_x = SCREEN_WIDTH - GRID_SIZE
        elif new_head_position_x % SCREEN_WIDTH == 0:
            new_head_position_x = 0

        if new_head_position_y % SCREEN_HEIGHT == SCREEN_HEIGHT - GRID_SIZE:
            new_head_position_y = SCREEN_HEIGHT - GRID_SIZE
        elif new_head_position_y % SCREEN_HEIGHT == 0:
            new_head_position_y = 0

        self.positions.insert(0, (new_head_position_x, new_head_position_y))
        if len(self.positions) > self.length:
            self.positions.pop()

    def grow(self):
        """
        Увеличивает длину змейки на 1 сегмент.

        При обработке столкновений с яблоком,
        змейка не сохраняет свою длину, а увеличвается в размерах.
        """
        self.length += 1

    def update_direction(self):
        """
        Применяет сохранённое направление к текущему.

        Используется для корректного изменения направления при нажатии клавиш.
        После применения next_direction сбрасывается в None.
        """
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def reset(self):
        """Сбрасывает состояние змейки к начальному.

        Устанавливает длину 1, позицию в центр поля, случайное направление.
        Используется, например, после столкновения со своим хвостом.
        """
        self.length = 1
        self.positions = [snake_start]
        self.direction = choice([UP, DOWN, LEFT, RIGHT])

    def draw(self):
        """
        Отрисовывает все сегменты змейки
        как цветные прямоугольники с рамкой.
        """
        for position in self.positions:
            rect = (pygame.Rect(position, (GRID_SIZE, GRID_SIZE)))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


def handle_keys(game_object):
    """
    Обрабатывает события клавиатуры (клавиши управления курсором)
    и устанавливает новое направление.

    Запрещает разворот на 180 градусов.

    Args:
        game_object (Snake): объект змейки,
        которому нужно установить направление.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def main():
    """
    Основной игровой цикл.

    Инициализирует объекты, обрабатывает ввод, обновляет состояние, проверяет
    столкновения, отрисовывает кадр и контролирует частоту кадров.
    """
    apple = Apple()
    snake = Snake()

    running = True
    while running:

        handle_keys(snake)
        snake.update_direction()
        snake.move()

        if snake.get_head_position() == apple.position:
            apple.randomize_position()
            snake.grow()

        if snake.get_head_position() in snake.positions[1:]:
            snake.reset()

        screen.fill(BOARD_BACKGROUND_COLOR)
        apple.draw()
        snake.draw()
        pygame.display.update()
        clock.tick(SPEED)


if __name__ == '__main__':
    main()
