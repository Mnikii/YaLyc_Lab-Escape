# Уровни игры
# 0 - пусто (воздух)
# 1 - твердая стена
# 2 - платформа (можно стоять)
# 3 - ловушка (шипы)
# 4 - выход

TILE_SIZE = 32


def get_level_config(level_num):
    if level_num == 1:
        return {
            'tiles': create_level_1(),
            'player_pos': (100, 200),
            'name': 'Центральный блок Лаборатории',
            'enemy_count': 8,
            'enemy_spawns': [(800, 150), (1200, 150), (1600, 400), (2000, 150), (2500, 300), (2800, 150), (3200, 150), (3500, 400)],
        }
    elif level_num == 2:
        return {
            'tiles': create_level_2(),
            'player_pos': (100, 200),
            'name': 'Технические тоннели',
            'enemy_count': 12,
            'enemy_spawns': [(500, 150), (1000, 150), (1500, 150), (2000, 150), (2500, 150), (3000, 150), (700, 400), (1300, 400), (1900, 400), (2400, 400), (2900, 400), (3400, 400)],
        }
    elif level_num == 3:
        return {
            'tiles': create_level_3(),
            'player_pos': (100, 200),
            'name': 'Сектор Омега - Финал',
            'enemy_count': 15,
            'enemy_spawns': [(i * 250, 200) for i in range(2, 17)],
        }
    else:
        return get_level_config(1)


def create_empty_grid(w, h):
    grid = [[0 for _ in range(w)] for _ in range(h)]
    for x in range(w):
        grid[0][x] = 1
        grid[h - 1][x] = 1
    for y in range(h):
        grid[y][0] = 1
        grid[y][w - 1] = 1
    return grid


def create_level_1():
    W, H = 120, 20
    grid = create_empty_grid(W, H)

    # Основной пол
    for x in range(1, W - 1):
        grid[H - 2][x] = 1

    # Платформы
    for x in range(10, 110, 15):
        h_pos = H - 6
        for i in range(8):
            if x + i < W - 1:
                grid[h_pos][x + i] = 2

        h_pos2 = H - 10
        for i in range(6):
            if x + 5 + i < W - 1:
                grid[h_pos2][x + 5 + i] = 2

    # Шипы
    for x in range(40, 45):
        grid[H - 2][x] = 3
    for x in range(80, 85):
        grid[H - 2][x] = 3

    # Выход
    grid[H - 4][W - 3] = 4
    grid[H - 3][W - 3] = 4
    grid[H - 4][W - 2] = 4
    grid[H - 3][W - 2] = 4

    return grid


def create_level_2():
    W, H = 120, 20
    grid = create_empty_grid(W, H)

    # Сплошной пол
    for x in range(1, W - 1):
        grid[H - 2][x] = 1

    # Шипы
    for x in range(25, 28):
        grid[H - 2][x] = 3
    for x in range(55, 58):
        grid[H - 2][x] = 3
    for x in range(85, 88):
        grid[H - 2][x] = 3

    # Платформы
    for x in range(20, 30):
        grid[H - 6][x] = 2
    for x in range(50, 60):
        grid[H - 6][x] = 2
    for x in range(80, 90):
        grid[H - 6][x] = 2

    for x in range(35, 45):
        grid[H - 10][x] = 2
    for x in range(65, 75):
        grid[H - 10][x] = 2

    for x in range(W - 12, W - 6):
        grid[H - 5][x] = 2

    # Выход
    grid[H - 4][W - 3] = 4
    grid[H - 3][W - 3] = 4
    grid[H - 4][W - 2] = 4
    grid[H - 3][W - 2] = 4

    return grid



def create_level_3():
    """Уровень 3: Сектор Омега - Сбалансированный финальный этап"""
    W, H = 120, 20
    grid = create_empty_grid(W, H)

    # 1. Проработка пола: Опасные зоны чередуются с островками безопасности
    for x in range(1, W - 1):
        if (x // 15) % 2 == 0:
            grid[H - 2][x] = 1  # Безопасный пол
        else:
            grid[H - 2][x] = 3  # Зона с шипами

    # 2. Основной путь: Платформы на разной высоте, образующие четкий маршрут
    # Нижний ярус платформ (над шипами)
    for x in range(15, W - 15, 15):
        # Каждая платформа длиной в 5 тайлов
        for i in range(5):
            if x + i < W - 1:
                grid[H - 6][x + i] = 2

    # Средний ярус (чередуется с нижним)
    for x in range(22, W - 20, 15):
        for i in range(4):
            if x + i < W - 1:
                grid[H - 10][x + i] = 2

    # 3. Вертикальные препятствия (колонны), которые нужно обходить
    for x in range(30, W - 20, 30):
        # Колонны сверху вниз, оставляющие проход посередине
        for y in range(1, 6):
            grid[y][x] = 1
        for y in range(H - 10, H - 2):
            grid[y][x] = 1

    # 4. Финальный подъем перед выходом
    for i in range(3):
        step_x = W - 15 + (i * 3)
        step_y = H - 5 - (i * 2)
        for j in range(3):
            if step_x + j < W - 1:
                grid[step_y][step_x + j] = 2

    # 5. Выход (дверь 2x2)
    exit_x, exit_y = W - 4, H - 5
    grid[exit_y][exit_x] = 4
    grid[exit_y][exit_x + 1] = 4
    grid[exit_y + 1][exit_x] = 4
    grid[exit_y + 1][exit_x + 1] = 4

    return grid
