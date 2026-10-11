"""Игра «Змейка»: движение по сетке, яблоки и перезапуск при столкновении."""

from random import choice, randint

import pygame

# Размеры игрового поля и сетки.
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения.
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвета игрового поля, границ ячеек, яблока и змейки.
BOARD_BACKGROUND_COLOR = (0, 0, 0)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)

# Число шагов змейки в секунду.
SPEED = 20

# Настройка игрового окна и часов.
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pygame.display.set_caption('Змейка')
clock = pygame.time.Clock()


class GameObject:
    """Базовый класс объектов игрового поля."""

    def __init__(self):
        """Задаёт начальную позицию объекта и его цвет."""
        self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.body_color = None

    def draw(self):
        """Определяет интерфейс отрисовки для дочерних классов."""
        pass


class Apple(GameObject):
    """Яблоко, которое появляется в случайной свободной ячейке."""

    def __init__(self, occupied_positions=()):
        """Задаёт цвет яблока и выбирает его начальную позицию."""
        super().__init__()
        self.body_color = APPLE_COLOR
        self.randomize_position(occupied_positions)

    def randomize_position(self, occupied_positions=()):
        """Выбирает ячейку поля, исключая переданные занятые позиции."""
        occupied_positions = set(occupied_positions)
        if not occupied_positions:
            self.position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE,
            )
            return

        free_positions = [
            (x * GRID_SIZE, y * GRID_SIZE)
            for x in range(GRID_WIDTH)
            for y in range(GRID_HEIGHT)
            if (x * GRID_SIZE, y * GRID_SIZE) not in occupied_positions
        ]
        if not free_positions:
            raise ValueError('На игровом поле нет свободных ячеек.')
        self.position = choice(free_positions)

    def draw(self):
        """Рисует яблоко и границу его ячейки."""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """Змейка с головой, сегментами тела и направлением движения."""

    def __init__(self):
        """Создаёт змейку длиной в одну ячейку, движущуюся вправо."""
        super().__init__()
        self.body_color = SNAKE_COLOR
        self.length = 1
        self.positions = [self.position]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None

    def update_direction(self):
        """Применяет направление, выбранное при обработке клавиш."""
        if self.next_direction is not None:
            self.direction = self.next_direction
            self.next_direction = None

    def get_head_position(self):
        """Возвращает координаты головы змейки."""
        return self.positions[0]

    def move(self):
        """Перемещает змейку на одну ячейку с переходом через края."""
        head_x, head_y = self.get_head_position()
        direction_x, direction_y = self.direction
        new_head = (
            (head_x + direction_x * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + direction_y * GRID_SIZE) % SCREEN_HEIGHT,
        )
        self.positions.insert(0, new_head)
        self.position = new_head
        self.last = None
        if len(self.positions) > self.length:
            self.last = self.positions.pop()

    def grow(self):
        """Увеличивает длину и сохраняет хвост после съеденного яблока."""
        self.length += 1
        if self.last is not None:
            self.positions.append(self.last)
            self.last = None

    def draw(self):
        """Стирает прошлый хвост и рисует все сегменты змейки."""
        # Сначала стираем хвост: голова могла попасть в его прежнюю ячейку.
        if self.last is not None:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

        for position in self.positions:
            rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

    def reset(self):
        """Возвращает змейку в центр и выбирает случайное направление."""
        self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.length = 1
        self.positions = [self.position]
        self.direction = choice((UP, DOWN, LEFT, RIGHT))
        self.next_direction = None
        self.last = None


def handle_keys(game_object):
    """Обрабатывает закрытие окна и повороты без разворота назад."""
    key_directions = {
        pygame.K_UP: UP,
        pygame.K_DOWN: DOWN,
        pygame.K_LEFT: LEFT,
        pygame.K_RIGHT: RIGHT,
    }
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        if event.type == pygame.KEYDOWN:
            next_direction = key_directions.get(event.key)
            opposite_direction = (
                -game_object.direction[0], -game_object.direction[1]
            )
            if next_direction and next_direction != opposite_direction:
                game_object.next_direction = next_direction


def main():
    """Запускает игровой цикл до закрытия окна пользователем."""
    pygame.init()
    snake = Snake()
    apple = Apple(snake.positions)
    screen.fill(BOARD_BACKGROUND_COLOR)

    while True:
        clock.tick(SPEED)
        handle_keys(snake)
        snake.update_direction()
        snake.move()

        if snake.get_head_position() in snake.positions[1:]:
            snake.reset()
            screen.fill(BOARD_BACKGROUND_COLOR)
            apple.randomize_position(snake.positions)
        elif snake.get_head_position() == apple.position:
            snake.grow()
            # Полностью заполненное поле завершает раунд и начинает новый.
            if snake.length == GRID_WIDTH * GRID_HEIGHT:
                snake.reset()
                screen.fill(BOARD_BACKGROUND_COLOR)
            apple.randomize_position(snake.positions)

        snake.draw()
        apple.draw()
        pygame.display.update()


if __name__ == '__main__':
    main()
