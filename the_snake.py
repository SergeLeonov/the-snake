from random import choice, randint
from typing import List, Optional, Tuple

import pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH: int = 640
SCREEN_HEIGHT: int = 480
GRID_SIZE: int = 20
GRID_WIDTH: int = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT: int = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP: Tuple[int, int] = (0, -1)
DOWN: Tuple[int, int] = (0, 1)
LEFT: Tuple[int, int] = (-1, 0)
RIGHT: Tuple[int, int] = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR: Tuple[int, int, int] = (0, 0, 0)
# Цвет границы ячейки
BORDER_COLOR: Tuple[int, int, int] = (93, 216, 228)
# Цвет яблока
APPLE_COLOR: Tuple[int, int, int] = (255, 0, 0)
# Цвет змейки
SNAKE_COLOR: Tuple[int, int, int] = (0, 255, 0)
# Скорость движения змейки:
SPEED: int = 10
# Настройка игрового окна:
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')
# Настройка времени:
clock = pygame.time.Clock()
# Координаты старта змейки
snake_start: Tuple[int, int] = (
    SCREEN_WIDTH // 2,
    SCREEN_HEIGHT // 2
)

Position = Tuple[int, int]
Positions = List[Position]


class GameObject:
    """
    Базовый класс игровых объектов.

    Хранит позицию и цвет, предоставляет шаблон для отрисовки.
    Классы Apple и Snake наследуются от него.
    """

    def __init__(self,
                 position: Optional[Position] = None,
                 body_color: Optional[Tuple[int, int, int]] = None,
                 ) -> None:
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

    def draw(self) -> None:
        """
        Отрисовывает объект на экране.

        По умолчанию ничего не делает:
        переопределяется в дочерних классах
        """
        raise NotImplementedError("Переопределить в наследниках")


class Apple(GameObject):
    """
    Класс яблока — цель для змейки.

    Создаёт яблоко в случайной позиции на сетке, умеет менять позицию
    и отрисовывать себя как цветной квадрат с рамкой.
    """

    def __init__(self,
                 position: Optional[Position] = None,
                 body_color: Tuple[int, int, int] = APPLE_COLOR
                 ) -> None:
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

    def randomize_position(self, snake_position: Positions) -> Position:
        """
        Перемещает яблоко в новую случайную позицию на сетке.

        Позиция выбирается так, чтобы центр яблока совпадал с узлами сетки.
        Кроме того, яблоко не появлялось внутри змейки.

        Returns:
            tuple[int, int]: новая позиция (x, y).
        """
        while True:
            apple_position_x = randint(0, GRID_WIDTH - 1) * GRID_SIZE
            apple_position_y = randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            pre_position = (apple_position_x, apple_position_y)

            if pre_position not in snake_position[1:]:
                self.position = pre_position
                return self.position

    def draw(self) -> None:
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

    def __init__(
        self,
        direction: Position = RIGHT,
        body_color: Tuple[int, int, int] = SNAKE_COLOR,
    ) -> None:
        """Создаёт змейку.

        Args:
            direction (tuple[int, int]): текущее направление движения.
            body_color (tuple[int, int, int]): цвет змейки.
        """
        super().__init__(position=None, body_color=body_color)
        self.direction = direction
        self.body_color = body_color
        self.reset()

    def get_head_position(self) -> Position:
        """Возвращает позицию головы змейки.

        Returns:
            tuple[int, int]: координаты головы (x, y).
        """
        return self.positions[0]

    def move(self) -> None:
        """
        Вычисляет новую позицию головы и обновляет список сегментов.

        Новая голова добавляется в начало списка. Если длина списка превышает
        допустимую (self.length), удаляется последний сегмент хвоста.
        Реализует «проход сквозь стены» посредствам поиска в пространстве
        головы змеи и "телепортации" в нужную точку.
        """
        head_x, head_y = self.get_head_position()
        new_head_x = (head_x + GRID_SIZE * self.direction[0]) % SCREEN_WIDTH
        new_head_y = (head_y + GRID_SIZE * self.direction[1]) % SCREEN_HEIGHT

        self.positions.insert(0, (new_head_x, new_head_y))
        if len(self.positions) > self.length:
            self.positions.pop()

    def grow(self) -> None:
        """
        Увеличивает длину змейки на 1 сегмент.

        При обработке столкновений с яблоком,
        змейка не сохраняет свою длину, а увеличвается в размерах.
        """
        self.length += 1

    def update_direction(self) -> None:
        """
        Применяет сохранённое направление к текущему.

        Используется для корректного изменения направления при нажатии клавиш.
        После применения next_direction сбрасывается в None.
        """
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def reset(self) -> None:
        """Сбрасывает состояние змейки к начальному.

        Устанавливает длину 1, позицию в центр поля, случайное направление.
        Используется, например, после столкновения со своим хвостом.
        """
        self.length = 1
        self.positions: Positions = [snake_start]
        self.direction = choice([UP, DOWN, LEFT, RIGHT])
        self.next_direction = None

    def draw(self) -> None:
        """
        Отрисовывает все сегменты змейки
        как цветные прямоугольники с рамкой.
        """
        for position in self.positions:
            rect = (pygame.Rect(position, (GRID_SIZE, GRID_SIZE)))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


def handle_keys(game_object: Snake) -> None:
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


def main() -> None:
    """
    Основной игровой цикл.

    Инициализирует объекты, обрабатывает ввод, обновляет состояние, проверяет
    столкновения, отрисовывает кадр и контролирует частоту кадров.
    """
    snake = Snake()
    apple = Apple()

    apple.randomize_position(snake.positions)

    while True:

        handle_keys(snake)
        snake.update_direction()
        snake.move()

        head_position = snake.get_head_position()

        if head_position == apple.position:
            apple.randomize_position(snake.positions)
            snake.grow()

        if head_position in snake.positions[1:]:
            snake.reset()
            apple.randomize_position(snake.positions)

        screen.fill(BOARD_BACKGROUND_COLOR)
        apple.draw()
        snake.draw()
        pygame.display.update()
        clock.tick(SPEED)


if __name__ == '__main__':
    main()
