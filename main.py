from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from collections import deque
import ctypes
import sys

app = Ursina()

window.fps_counter.enabled = True
window.exit_button.visible = False
window.title = 'Побег из Лабиринта: Ошибка системы'

# --- НЕБО И СКРИМЕР ---
sky = Sky(texture='nebo')

screamer_image = Entity(
    parent=camera.ui,
    model='quad',
    texture='strashna',
    scale=(2, 2),
    z=-1,
    enabled=False
)

screamer_sound = Audio('scrimer', autoplay=False)

# --- ГЕНЕРАЦИЯ ЛАБИРИНТА ---
MAZE_MAP = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1],
    [1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1],
    [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1],
    [1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1],
    [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1],
    [1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1],
    [1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1],
    [1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1],
    [1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1],
    [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]

CELL_SIZE = 4
OFFSET_X = -(len(MAZE_MAP[0]) * CELL_SIZE) // 2
OFFSET_Z = -(len(MAZE_MAP) * CELL_SIZE) // 2

# Пол
ground = Entity(
    model='plane',
    scale=(len(MAZE_MAP[0]) * CELL_SIZE, 1, len(MAZE_MAP) * CELL_SIZE),
    color=color.gray,
    texture='white_cube',
    texture_scale=(40, 40),
    collider='box'
)

# Стены
walls = []
for row in range(len(MAZE_MAP)):
    for col in range(len(MAZE_MAP[row])):
        if MAZE_MAP[row][col] == 1:
            x = OFFSET_X + col * CELL_SIZE
            z = OFFSET_Z + row * CELL_SIZE
            wall = Entity(
                model='cube',
                position=(x, 2.5, z),
                scale=(CELL_SIZE, 5, CELL_SIZE),
                color=color.dark_gray,
                texture='white_cube',
                collider='box'
            )
            walls.append(wall)

# --- ФИНИШ ---
escape_x = OFFSET_X + 19 * CELL_SIZE
escape_z = OFFSET_Z + 19 * CELL_SIZE

escape_zone = Entity(
    model='cube',
    scale=(CELL_SIZE - 0.5, 0.1, CELL_SIZE - 0.5),
    position=(escape_x, 0.1, escape_z),
    color=color.green,
    collider='box'
)

Text(
    text='ВЫХОД',
    position=(escape_x, 3, escape_z),
    scale=12,
    color=color.green,
    billboard=True
)

# --- ИГРОК ---
start_x = OFFSET_X + 1 * CELL_SIZE
start_z = OFFSET_Z + 1 * CELL_SIZE
player = FirstPersonController(position=(start_x, 2, start_z), speed=6.0)

# --- МИША ---
misha_x = OFFSET_X + 10 * CELL_SIZE
misha_z = OFFSET_Z + 10 * CELL_SIZE

misha = Entity(
    model='cube',
    scale=(1.8, 3, 1.8),
    position=(misha_x, 1.5, misha_z),
    color=color.red,
    collider='box'
)

Entity(parent=misha, model='sphere', scale=0.25, position=(-0.3, 0.3, -0.51), color=color.black)
Entity(parent=misha, model='sphere', scale=0.25, position=(0.3, 0.3, -0.51), color=color.black)

normal_speed = 4.8
chase_speed = 11.5
game_over = False

status_text = Text(
    text='HARDCORE: ВЫЖИВИ И НАЙДИ ВЫХОД!',
    origin=(0, 0),
    position=(0, 0.4),
    scale=2,
    color=color.red
)


# --- ПОИСК ПУТИ (BFS) ---
def world_to_grid(pos):
    col = round((pos.x - OFFSET_X) / CELL_SIZE)
    row = round((pos.z - OFFSET_Z) / CELL_SIZE)
    return int(row), int(col)


def grid_to_world(row, col):
    x = OFFSET_X + col * CELL_SIZE
    z = OFFSET_Z + row * CELL_SIZE
    return Vec3(x, 1.5, z)


def find_path(start_grid, target_grid):
    queue = deque([[start_grid]])
    visited = {start_grid}

    while queue:
        path = queue.popleft()
        current = path[-1]
        if current == target_grid:
            return path

        r, c = current
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < len(MAZE_MAP) and 0 <= nc < len(MAZE_MAP[0]):
                if MAZE_MAP[nr][nc] == 0 and (nr, nc) not in visited:
                    visited.add((nr, nc))
                    queue.append(path + [(nr, nc)])
    return [start_grid]


path_timer = 0
current_path = []


def move_misha():
    global path_timer, current_path
    if game_over:
        return

    dir_to_player = player.position - misha.position
    dist_to_player = dir_to_player.length()
    dir_to_player = dir_to_player.normalized()
    dir_to_player.y = 0

    ray = raycast(misha.position + Vec3(0, 0.5, 0), dir_to_player, distance=dist_to_player, ignore=(misha, player))
    sees_player = not ray.hit and dist_to_player < 40

    if sees_player:
        misha.look_at(player.position)
        misha.rotation_x = 0
        misha.rotation_z = 0
        misha.position += dir_to_player * chase_speed * time.dt
        current_path = []
    else:
        path_timer += time.dt
        misha_grid = world_to_grid(misha.position)
        player_grid = world_to_grid(player.position)

        if path_timer > 0.2 or not current_path:
            path_timer = 0
            current_path = find_path(misha_grid, player_grid)

        if len(current_path) > 1:
            next_cell = current_path[1]
            target_pos = grid_to_world(next_cell[0], next_cell[1])
            target_pos.y = misha.position.y

            direction = (target_pos - misha.position).normalized()
            if direction.length() > 0:
                misha.look_at(target_pos)
                misha.rotation_x = 0
                misha.rotation_z = 0
                misha.position += direction * normal_speed * time.dt

                if distance(misha.position, target_pos) < 0.25:
                    current_path.pop(0)


# Функция фейкового вылета с ошибкой
def trigger_fake_crash():
    ctypes.windll.user32.MessageBoxW(
        0,
        "КРИТИЧЕСКАЯ СИСТЕМНАЯ ОШИБКА!\nОбнаружено вредоносное ПО.\nВаш ПК будет полностью уничтожен через 1 минуту!",
        "Критический сбой Windows",
        0x10 | 0x0  # Иконка крестика (ошибка) + кнопка OK
    )
    sys.exit()


def update():
    global game_over

    if game_over:
        return

    move_misha()

    dist_xz = Vec2(player.x - misha.x, player.z - misha.z).length()

    # Поймал
    if dist_xz < 1.8:
        game_over = True
        status_text.text = 'МИША ТЕБЯ ПОЙМАЛ!'
        status_text.color = color.red
        player.enabled = False

        screamer_image.enabled = True
        screamer_sound.play()

        # Запускаем окно с ошибкой и вылет ровно через 1.2 секунды (после скримера)
        invoke(trigger_fake_crash, delay=1.2)

    # Победа
    if distance(player.position, escape_zone.position) < 2.5:
        game_over = True
        status_text.text = 'ТЫ ВЫБРАЛСЯ ИЗ ЛАБИРИНТА!\nПОБЕДА!\n[R] - Сыграть снова'
        status_text.color = color.green
        player.enabled = False


def input(key):
    global game_over, current_path
    if key == 'r' or key == 'к':
        player.position = (start_x, 2, start_z)
        misha.position = (misha_x, 1.5, misha_z)
        player.enabled = True
        game_over = False
        current_path = []
        screamer_image.enabled = False
        status_text.text = 'HARDCORE: ВЫЖИВИ И НАЙДИ ВЫХОД!'
        status_text.color = color.red


app.run()