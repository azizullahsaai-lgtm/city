

import pygame
import random
import math
import sys

# ============================================================
# REALISTIC CITY SIMULATOR
# Python + Pygame
# ============================================================

pygame.init()
pygame.mixer.init()

# ============================================================
# SETTINGS
# ============================================================

WIDTH = 1280
HEIGHT = 720

FPS = 60

SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Realistic City Simulator")

CLOCK = pygame.time.Clock()

# ============================================================
# COLORS
# ============================================================

SKY_DAY = (110, 190, 235)
SKY_EVENING = (220, 145, 100)
SKY_NIGHT = (18, 25, 55)

GRASS = (70, 145, 70)
GRASS_DARK = (52, 120, 58)

ROAD = (55, 58, 62)
ROAD_DARK = (42, 45, 48)

SIDEWALK = (155, 155, 150)
SIDEWALK_DARK = (125, 125, 120)

LANE = (235, 220, 150)

WHITE = (245, 245, 245)
BLACK = (15, 15, 15)

BUILDING_COLORS = [
    (180, 190, 200),
    (205, 180, 160),
    (160, 175, 190),
    (190, 170, 145),
    (150, 160, 175),
    (200, 200, 185),
]

CAR_COLORS = [
    (190, 40, 40),
    (40, 90, 190),
    (40, 150, 80),
    (220, 180, 40),
    (170, 60, 170),
    (40, 160, 170),
    (230, 230, 230),
    (45, 45, 50),
]

# ============================================================
# FONTS
# ============================================================

FONT_SMALL = pygame.font.SysFont("arial", 14)
FONT = pygame.font.SysFont("arial", 18)
FONT_MEDIUM = pygame.font.SysFont("arial", 24)
FONT_BIG = pygame.font.SysFont("arial", 34)
FONT_TITLE = pygame.font.SysFont("arial", 42, bold=True)

# ============================================================
# WORLD
# ============================================================

WORLD_WIDTH = 3000
WORLD_HEIGHT = 2200

# Camera
camera_x = 0
camera_y = 0
camera_speed = 700

# ============================================================
# TIME SYSTEM
# ============================================================

world_time = 8.0
TIME_SPEED = 0.12

paused = False

# ============================================================
# ROAD SYSTEM
# ============================================================

ROAD_WIDTH = 130

vertical_roads = [
    300,
    850,
    1400,
    1950,
    2500,
]

horizontal_roads = [
    300,
    800,
    1300,
    1800,
]

# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def clamp(value, minimum, maximum):
    return max(minimum, min(value, maximum))


def distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def world_to_screen(x, y):
    return int(x - camera_x), int(y - camera_y)


def screen_to_world(x, y):
    return x + camera_x, y + camera_y


def draw_world_rect(surface, color, rect):
    x, y, w, h = rect
    sx, sy = world_to_screen(x, y)
    pygame.draw.rect(surface, color, (sx, sy, w, h))


def draw_world_circle(surface, color, x, y, radius):
    sx, sy = world_to_screen(x, y)
    pygame.draw.circle(surface, color, (sx, sy), radius)


# ============================================================
# BUILDING
# ============================================================

class Building:

    def __init__(self, x, y, w, h):

        self.x = x
        self.y = y
        self.w = w
        self.h = h

        self.color = random.choice(BUILDING_COLORS)

        self.windows = []

        rows = max(2, int(h / 35))
        cols = max(2, int(w / 30))

        for row in range(rows):
            for col in range(cols):

                wx = x + 10 + col * 30
                wy = y + 12 + row * 35

                if wx + 14 < x + w - 5 and wy + 18 < y + h - 5:

                    self.windows.append({
                        "x": wx,
                        "y": wy,
                        "on": random.random() < 0.25
                    })

    def draw(self, surface, night):

        sx, sy = world_to_screen(self.x, self.y)

        pygame.draw.rect(
            surface,
            self.color,
            (sx, sy, self.w, self.h)
        )

        # Shadow
        pygame.draw.rect(
            surface,
            (70, 70, 75),
            (sx, sy + self.h - 7, self.w, 7)
        )

        # Windows
        for window in self.windows:

            wx, wy = world_to_screen(
                window["x"],
                window["y"]
            )

            if night and window["on"]:

                pygame.draw.rect(
                    surface,
                    (245, 210, 100),
                    (wx, wy, 14, 18)
                )

            else:

                pygame.draw.rect(
                    surface,
                    (70, 120, 150),
                    (wx, wy, 14, 18)
                )

        # Roof
        pygame.draw.line(
            surface,
            (80, 80, 80),
            (sx, sy),
            (sx + self.w, sy),
            3
        )


# ============================================================
# TREE
# ============================================================

class Tree:

    def __init__(self, x, y):

        self.x = x
        self.y = y

        self.size = random.randint(18, 30)

        self.green = random.choice([
            (35, 120, 50),
            (45, 140, 55),
            (55, 150, 65),
            (30, 105, 45)
        ])

    def draw(self, surface):

        sx, sy = world_to_screen(self.x, self.y)

        # Shadow
        pygame.draw.ellipse(
            surface,
            (35, 90, 40),
            (
                sx - self.size,
                sy + self.size // 2,
                self.size * 2,
                self.size // 2
            )
        )

        # Trunk
        pygame.draw.rect(
            surface,
            (100, 65, 35),
            (
                sx - 5,
                sy,
                10,
                self.size
            )
        )

        # Leaves
        pygame.draw.circle(
            surface,
            self.green,
            (sx, sy - 10),
            self.size
        )

        pygame.draw.circle(
            surface,
            self.green,
            (sx - 14, sy),
            self.size // 2
        )

        pygame.draw.circle(
            surface,
            self.green,
            (sx + 14, sy),
            self.size // 2
        )


# ============================================================
# CLOUD
# ============================================================

class Cloud:

    def __init__(self):

        self.x = random.randint(0, WORLD_WIDTH)
        self.y = random.randint(50, 400)

        self.speed = random.uniform(10, 30)

        self.size = random.randint(35, 70)

    def update(self, dt):

        self.x += self.speed * dt

        if self.x > WORLD_WIDTH + 200:
            self.x = -200

    def draw(self, surface):

        sx, sy = world_to_screen(self.x, self.y)

        color = (245, 245, 245)

        pygame.draw.circle(
            surface,
            color,
            (sx, sy),
            self.size
        )

        pygame.draw.circle(
            surface,
            color,
            (sx + self.size // 2, sy + 10),
            self.size // 2
        )

        pygame.draw.circle(
            surface,
            color,
            (sx - self.size // 2, sy + 12),
            self.size // 2
        )


# ============================================================
# RAIN
# ============================================================

class RainDrop:

    def __init__(self):

        self.x = random.randint(0, WIDTH)
        self.y = random.randint(-HEIGHT, HEIGHT)

        self.speed = random.randint(500, 850)

    def update(self, dt):

        self.y += self.speed * dt

        if self.y > HEIGHT:

            self.y = random.randint(-200, 0)
            self.x = random.randint(0, WIDTH)

    def draw(self, surface):

        pygame.draw.line(
            surface,
            (170, 200, 240),
            (self.x, self.y),
            (self.x - 3, self.y + 14),
            1
        )


# ============================================================
# TRAFFIC LIGHT
# ============================================================

class TrafficLight:

    def __init__(self, x, y, orientation="vertical"):

        self.x = x
        self.y = y

        self.orientation = orientation

        self.timer = random.uniform(0, 8)

        self.state = "green"

    def update(self, dt):

        self.timer += dt

        cycle = self.timer % 12

        if cycle < 6:

            self.state = "green"

        elif cycle < 8:

            self.state = "yellow"

        else:

            self.state = "red"

    def draw(self, surface, night):

        sx, sy = world_to_screen(self.x, self.y)

        pygame.draw.rect(
            surface,
            (25, 25, 25),
            (sx - 8, sy - 25, 16, 50)
        )

        colors = {
            "red": (220, 30, 30),
            "yellow": (240, 210, 30),
            "green": (30, 220, 80)
        }

        # Red
        pygame.draw.circle(
            surface,
            colors["red"] if self.state == "red" else (70, 20, 20),
            (sx, sy - 15),
            5
        )

        # Yellow
        pygame.draw.circle(
            surface,
            colors["yellow"] if self.state == "yellow" else (70, 65, 20),
            (sx, sy),
            5
        )

        # Green
        pygame.draw.circle(
            surface,
            colors["green"] if self.state == "green" else (20, 70, 30),
            (sx, sy + 15),
            5
        )


# ============================================================
# CAR
# ============================================================

class Car:

    def __init__(self):

        self.direction = random.choice([
            "horizontal",
            "vertical"
        ])

        if self.direction == "horizontal":

            self.y = random.choice(horizontal_roads)

            if random.random() < 0.5:

                self.x = random.randint(
                    0,
                    WORLD_WIDTH
                )

                self.dx = 1

            else:

                self.x = random.randint(
                    0,
                    WORLD_WIDTH
                )

                self.dx = -1

            self.dy = 0

        else:

            self.x = random.choice(vertical_roads)

            if random.random() < 0.5:

                self.y = random.randint(
                    0,
                    WORLD_HEIGHT
                )

                self.dy = 1

            else:

                self.y = random.randint(
                    0,
                    WORLD_HEIGHT
                )

                self.dy = -1

            self.dx = 0

        self.speed = random.uniform(70, 130)

        self.base_speed = self.speed

        self.color = random.choice(CAR_COLORS)

        self.width = 38

        self.height = 20

        self.stopped = False

        self.is_emergency = False

    def check_traffic_light(self, traffic_lights):

        self.stopped = False

        for light in traffic_lights:

            d = distance(
                self.x,
                self.y,
                light.x,
                light.y
            )

            if d < 80 and light.state == "red":

                self.stopped = True

                break

    def update(self, dt, traffic_lights):

        self.check_traffic_light(
            traffic_lights
        )

        if self.stopped:

            self.speed = 0

        else:

            self.speed += (
                self.base_speed - self.speed
            ) * 0.08

        self.x += self.dx * self.speed * dt
        self.y += self.dy * self.speed * dt

        # Wrap around city

        if self.x > WORLD_WIDTH + 100:
            self.x = -100

        if self.x < -100:
            self.x = WORLD_WIDTH + 100

        if self.y > WORLD_HEIGHT + 100:
            self.y = -100

        if self.y < -100:
            self.y = WORLD_HEIGHT + 100

    def draw(self, surface, night):

        sx, sy = world_to_screen(
            self.x,
            self.y
        )

        if self.direction == "horizontal":

            rect = (
                sx - self.width // 2,
                sy - self.height // 2,
                self.width,
                self.height
            )

        else:

            rect = (
                sx - self.height // 2,
                sy - self.width // 2,
                self.height,
                self.width
            )

        pygame.draw.rect(
            surface,
            self.color,
            rect,
            border_radius=5
        )

        # Windows

        if self.direction == "horizontal":

            pygame.draw.rect(
                surface,
                (50, 80, 100),
                (sx - 8, sy - 7, 12, 14)
            )

            pygame.draw.rect(
                surface,
                (50, 80, 100),
                (sx + 4, sy - 7, 10, 14)
            )

        else:

            pygame.draw.rect(
                surface,
                (50, 80, 100),
                (sx - 7, sy - 8, 14, 10)
            )

        # Wheels

        if self.direction == "horizontal":

            pygame.draw.circle(
                surface,
                BLACK,
                (sx - 13, sy + 10),
                4
            )

            pygame.draw.circle(
                surface,
                BLACK,
                (sx + 13, sy + 10),
                4
            )

        else:

            pygame.draw.circle(
                surface,
                BLACK,
                (sx + 10, sy - 13),
                4
            )

            pygame.draw.circle(
                surface,
                BLACK,
                (sx + 10, sy + 13),
                4
            )


# ============================================================
# BUS
# ============================================================

class Bus(Car):

    def __init__(self):

        super().__init__()

        self.speed = random.uniform(45, 75)

        self.base_speed = self.speed

        self.color = (30, 100, 190)

        self.width = 65

        self.height = 25

    def draw(self, surface, night):

        sx, sy = world_to_screen(
            self.x,
            self.y
        )

        if self.direction == "horizontal":

            rect = (
                sx - self.width // 2,
                sy - self.height // 2,
                self.width,
                self.height
            )

        else:

            rect = (
                sx - self.height // 2,
                sy - self.width // 2,
                self.height,
                self.width
            )

        pygame.draw.rect(
            surface,
            self.color,
            rect,
            border_radius=5
        )

        # Windows

        if self.direction == "horizontal":

            for i in range(5):

                pygame.draw.rect(
                    surface,
                    (70, 130, 155),
                    (
                        sx - 25 + i * 11,
                        sy - 7,
                        8,
                        10
                    )
                )

        else:

            for i in range(5):

                pygame.draw.rect(
                    surface,
                    (70, 130, 155),
                    (
                        sx - 7,
                        sy - 25 + i * 11,
                        10,
                        8
                    )
                )


# ============================================================
# EMERGENCY VEHICLE
# ============================================================

class EmergencyCar(Car):

    def __init__(self):

        super().__init__()

        self.color = (235, 235, 235)

        self.speed = 170

        self.base_speed = 170

        self.is_emergency = True

    def draw(self, surface, night):

        super().draw(
            surface,
            night
        )

        sx, sy = world_to_screen(
            self.x,
            self.y
        )

        pygame.draw.rect(
            surface,
            (220, 20, 20),
            (
                sx - 7,
                sy - 3,
                14,
                5
            )
        )


# ============================================================
# PEDESTRIAN
# ============================================================

class Pedestrian:

    def __init__(self):

        self.x = random.randint(
            50,
            WORLD_WIDTH - 50
        )

        self.y = random.randint(
            50,
            WORLD_HEIGHT - 50
        )

        self.angle = random.uniform(
            0,
            math.pi * 2
        )

        self.speed = random.uniform(
            20,
            45
        )

        self.color = random.choice([
            (220, 80, 70),
            (70, 100, 200),
            (80, 170, 100),
            (220, 180, 70),
            (150, 90, 180),
        ])

    def update(self, dt):

        # Randomly change direction

        if random.random() < 0.005:

            self.angle += random.uniform(
                -1.2,
                1.2
            )

        self.x += math.cos(
            self.angle
        ) * self.speed * dt

        self.y += math.sin(
            self.angle
        ) * self.speed * dt

        self.x = clamp(
            self.x,
            20,
            WORLD_WIDTH - 20
        )

        self.y = clamp(
            self.y,
            20,
            WORLD_HEIGHT - 20
        )

    def draw(self, surface):

        sx, sy = world_to_screen(
            self.x,
            self.y
        )

        # Head
        pygame.draw.circle(
            surface,
            (235, 190, 150),
            (sx, sy - 7),
            4
        )

        # Body
        pygame.draw.line(
            surface,
            self.color,
            (sx, sy - 2),
            (sx, sy + 9),
            4
        )

        # Legs

        pygame.draw.line(
            surface,
            BLACK,
            (sx, sy + 9),
            (sx - 4, sy + 16),
            2
        )

        pygame.draw.line(
            surface,
            BLACK,
            (sx, sy + 9),
            (sx + 4, sy + 16),
            2
        )


# ============================================================
# PARK
# ============================================================

class Park:

    def __init__(self, x, y, w, h):

        self.x = x
        self.y = y
        self.w = w
        self.h = h

        self.trees = []

        for _ in range(
            random.randint(12, 25)
        ):

            tx = random.randint(
                x + 25,
                x + w - 25
            )

            ty = random.randint(
                y + 25,
                y + h - 25
            )

            self.trees.append(
                Tree(tx, ty)
            )

    def draw(self, surface):

        draw_world_rect(
            surface,
            (65, 145, 75),
            (
                self.x,
                self.y,
                self.w,
                self.h
            )
        )

        # Path

        pygame.draw.rect(
            surface,
            (190, 170, 140),
            (
                self.x - camera_x + self.w // 2 - 10,
                self.y - camera_y,
                20,
                self.h
            )
        )

        pygame.draw.rect(
            surface,
            (190, 170, 140),
            (
                self.x - camera_x,
                self.y - camera_y + self.h // 2 - 10,
                self.w,
                20
            )
        )

        for tree in self.trees:

            tree.draw(surface)


# ============================================================
# CITY
# ============================================================

buildings = []

parks = []

traffic_lights = []

cars = []

buses = []

emergency_cars = []

pedestrians = []

clouds = []

rain = []


# ============================================================
# CREATE CITY
# ============================================================

def create_city():

    global buildings
    global parks
    global traffic_lights
    global cars
    global buses
    global emergency_cars
    global pedestrians
    global clouds
    global rain

    buildings.clear()
    parks.clear()
    traffic_lights.clear()
    cars.clear()
    buses.clear()
    emergency_cars.clear()
    pedestrians.clear()
    clouds.clear()
    rain.clear()

    # --------------------------------------------------------
    # Buildings
    # --------------------------------------------------------

    for gx in range(
        len(vertical_roads) - 1
    ):

        for gy in range(
            len(horizontal_roads) - 1
        ):

            left = (
                vertical_roads[gx]
                + ROAD_WIDTH
            )

            right = (
                vertical_roads[gx + 1]
                - ROAD_WIDTH
            )

            top = (
                horizontal_roads[gy]
                + ROAD_WIDTH
            )

            bottom = (
                horizontal_roads[gy + 1]
                - ROAD_WIDTH
            )

            block_w = right - left
            block_h = bottom - top

            # Sometimes create park

            if random.random() < 0.18:

                parks.append(
                    Park(
                        left + 15,
                        top + 15,
                        block_w - 30,
                        block_h - 30
                    )
                )

                continue

            # Create multiple buildings

            cols = random.choice([1, 2, 3])
            rows = random.choice([1, 2, 3])

            bw = block_w / cols
            bh = block_h / rows

            for col in range(cols):

                for row in range(rows):

                    margin = 12

                    x = (
                        left
                        + col * bw
                        + margin
                    )

                    y = (
                        top
                        + row * bh
                        + margin
                    )

                    w = bw - 2 * margin
                    h = bh - 2 * margin

                    buildings.append(
                        Building(
                            x,
                            y,
                            int(w),
                            int(h)
                        )
                    )

    # --------------------------------------------------------
    # Traffic lights
    # --------------------------------------------------------

    for x in vertical_roads:

        for y in horizontal_roads:

            traffic_lights.append(
                TrafficLight(
                    x - ROAD_WIDTH // 2,
                    y - ROAD_WIDTH // 2
                )
            )

            traffic_lights.append(
                TrafficLight(
                    x + ROAD_WIDTH // 2,
                    y + ROAD_WIDTH // 2
                )
            )

    # --------------------------------------------------------
    # Cars
    # --------------------------------------------------------

    for _ in range(55):

        cars.append(
            Car()
        )

    # --------------------------------------------------------
    # Buses
    # --------------------------------------------------------

    for _ in range(8):

        buses.append(
            Bus()
        )

    # --------------------------------------------------------
    # Emergency vehicles
    # --------------------------------------------------------

    for _ in range(2):

        emergency_cars.append(
            EmergencyCar()
        )

    # --------------------------------------------------------
    # Pedestrians
    # --------------------------------------------------------

    for _ in range(70):

        pedestrians.append(
            Pedestrian()
        )

    # --------------------------------------------------------
    # Clouds
    # --------------------------------------------------------

    for _ in range(15):

        clouds.append(
            Cloud()
        )

    # --------------------------------------------------------
    # Rain
    # --------------------------------------------------------

    for _ in range(180):

        rain.append(
            RainDrop()
        )


# ============================================================
# DRAW SKY
# ============================================================

def get_sky_color():

    hour = world_time % 24

    if 7 <= hour < 17:

        return SKY_DAY

    if 17 <= hour < 20:

        # Evening

        t = (hour - 17) / 3

        r = int(
            SKY_DAY[0]
            + (SKY_EVENING[0] - SKY_DAY[0]) * t
        )

        g = int(
            SKY_DAY[1]
            + (SKY_EVENING[1] - SKY_DAY[1]) * t
        )

        b = int(
            SKY_DAY[2]
            + (SKY_EVENING[2] - SKY_DAY[2]) * t
        )

        return (
            r,
            g,
            b
        )

    if 20 <= hour or hour < 5:

        return SKY_NIGHT

    # Morning

    t = (hour - 5) / 2

    r = int(
        SKY_NIGHT[0]
        + (SKY_DAY[0] - SKY_NIGHT[0]) * t
    )

    g = int(
        SKY_NIGHT[1]
        + (SKY_DAY[1] - SKY_NIGHT[1]) * t
    )

    b = int(
        SKY_NIGHT[2]
        + (SKY_DAY[2] - SKY_NIGHT[2]) * t
    )

    return (
        r,
        g,
        b
    )


# ============================================================
# NIGHT CHECK
# ============================================================

def is_night():

    hour = world_time % 24

    return (
        hour >= 20
        or hour < 5
    )


# ============================================================
# DRAW WORLD
# ============================================================

def draw_ground(surface):

    # Grass

    draw_world_rect(
        surface,
        GRASS,
        (
            0,
            0,
            WORLD_WIDTH,
            WORLD_HEIGHT
        )
    )

    # Small grass patterns

    random.seed(10)

    for _ in range(700):

        x = random.randint(
            0,
            WORLD_WIDTH
        )

        y = random.randint(
            0,
            WORLD_HEIGHT
        )

        sx, sy = world_to_screen(
            x,
            y
        )

        if (
            -5 < sx < WIDTH + 5
            and -5 < sy < HEIGHT + 5
        ):

            pygame.draw.line(
                surface,
                GRASS_DARK,
                (sx, sy),
                (sx + 3, sy - 4),
                1
            )

    random.seed()


# ============================================================
# DRAW ROADS
# ============================================================

def draw_roads(surface):

    # Horizontal roads

    for y in horizontal_roads:

        draw_world_rect(
            surface,
            SIDEWALK_DARK,
            (
                0,
                y - ROAD_WIDTH // 2 - 10,
                WORLD_WIDTH,
                ROAD_WIDTH + 20
            )
        )

        draw_world_rect(
            surface,
            ROAD,
            (
                0,
                y - ROAD_WIDTH // 2,
                WORLD_WIDTH,
                ROAD_WIDTH
            )
        )

        # Center line

        for x in range(
            0,
            WORLD_WIDTH,
            70
        ):

            draw_world_rect(
                surface,
                LANE,
                (
                    x,
                    y - 2,
                    35,
                    4
                )
            )

        # Sidewalk lines

        draw_world_rect(
            surface,
            SIDEWALK,
            (
                0,
                y - ROAD_WIDTH // 2,
                WORLD_WIDTH,
                5
            )
        )

        draw_world_rect(
            surface,
            SIDEWALK,
            (
                0,
                y + ROAD_WIDTH // 2 - 5,
                WORLD_WIDTH,
                5
            )
        )

    # Vertical roads

    for x in vertical_roads:

        draw_world_rect(
            surface,
            SIDEWALK_DARK,
            (
                x - ROAD_WIDTH // 2 - 10,
                0,
                ROAD_WIDTH + 20,
                WORLD_HEIGHT
            )
        )

        draw_world_rect(
            surface,
            ROAD,
            (
                x - ROAD_WIDTH // 2,
                0,
                ROAD_WIDTH,
                WORLD_HEIGHT
            )
        )

        for y in range(
            0,
            WORLD_HEIGHT,
            70
        ):

            draw_world_rect(
                surface,
                LANE,
                (
                    x - 2,
                    y,
                    4,
                    35
                )
            )

        draw_world_rect(
            surface,
            SIDEWALK,
            (
                x - ROAD_WIDTH // 2,
                0,
                5,
                WORLD_HEIGHT
            )
        )

        draw_world_rect(
            surface,
            SIDEWALK,
            (
                x + ROAD_WIDTH // 2 - 5,
                0,
                5,
                WORLD_HEIGHT
            )
        )


# ============================================================
# SUN
# ============================================================

def draw_sun(surface):

    hour = world_time % 24

    if 5 <= hour <= 20:

        progress = (
            hour - 5
        ) / 15

        sun_x = int(
            progress * WIDTH
        )

        sun_y = int(
            430
            - math.sin(
                progress * math.pi
            ) * 330
        )

        pygame.draw.circle(
            surface,
            (255, 225, 100),
            (
                sun_x,
                sun_y
            ),
            35
        )


# ============================================================
# MOON
# ============================================================

def draw_moon(surface):

    hour = world_time % 24

    if hour >= 18 or hour < 6:

        progress = (
            (hour - 18) % 24
        ) / 12

        moon_x = int(
            progress * WIDTH
        )

        moon_y = int(
            350
            - math.sin(
                progress * math.pi
            ) * 260
        )

        pygame.draw.circle(
            surface,
            (235, 235, 210),
            (
                moon_x,
                moon_y
            ),
            28
        )


# ============================================================
# RAIN MODE
# ============================================================

rain_enabled = False


# ============================================================
# DAY/NIGHT OVERLAY
# ============================================================

def draw_night_overlay(surface):

    if not is_night():

        return

    overlay = pygame.Surface(
        (WIDTH, HEIGHT),
        pygame.SRCALPHA
    )

    overlay.fill(
        (10, 15, 45, 110)
    )

    surface.blit(
        overlay,
        (0, 0)
    )


# ============================================================
# UI
# ============================================================

def draw_ui(surface):

    panel = pygame.Surface(
        (330, 155),
        pygame.SRCALPHA
    )

    panel.fill(
        (15, 15, 20, 205)
    )

    surface.blit(
        panel,
        (15, 15)
    )

    hour = int(
        world_time
    )

    minute = int(
        (world_time - hour) * 60
    )

    time_text = FONT_BIG.render(
        f"{hour:02d}:{minute:02d}",
        True,
        WHITE
    )

    surface.blit(
        time_text,
        (30, 25)
    )

    status = "NIGHT" if is_night() else "DAY"

    status_text = FONT.render(
        f"City Time: {status}",
        True,
        WHITE
    )

    surface.blit(
        status_text,
        (30, 70)
    )

    stats = FONT_SMALL.render(
        f"Cars: {len(cars)}   Buses: {len(buses)}   "
        f"People: {len(pedestrians)}",
        True,
        WHITE
    )

    surface.blit(
        stats,
        (30, 100)
    )

    weather = "RAIN" if rain_enabled else "CLEAR"

    weather_text = FONT_SMALL.render(
        f"Weather: {weather}",
        True,
        WHITE
    )

    surface.blit(
        weather_text,
        (30, 125)
    )

    controls = FONT_SMALL.render(
        "WASD / Arrows = Camera | R = Rain | SPACE = Pause",
        True,
        WHITE
    )

    surface.blit(
        controls,
        (15, HEIGHT - 30)
    )


# ============================================================
# MINIMAP
# ============================================================

def draw_minimap(surface):

    mini_w = 220
    mini_h = 150

    mini_x = WIDTH - mini_w - 20
    mini_y = 20

    pygame.draw.rect(
        surface,
        (30, 35, 35),
        (
            mini_x,
            mini_y,
            mini_w,
            mini_h
        )
    )

    scale_x = mini_w / WORLD_WIDTH
    scale_y = mini_h / WORLD_HEIGHT

    # Roads

    for x in vertical_roads:

        mx = int(
            mini_x
            + x * scale_x
        )

        pygame.draw.line(
            surface,
            (100, 100, 100),
            (mx, mini_y),
            (mx, mini_y + mini_h),
            3
        )

    for y in horizontal_roads:

        my = int(
            mini_y
            + y * scale_y
        )

        pygame.draw.line(
            surface,
            (100, 100, 100),
            (mini_x, my),
            (mini_x + mini_w, my),
            3
        )

    # Camera rectangle

    cam_rect = pygame.Rect(
        mini_x
        + camera_x * scale_x,
        mini_y
        + camera_y * scale_y,
        WIDTH * scale_x,
        HEIGHT * scale_y
    )

    pygame.draw.rect(
        surface,
        WHITE,
        cam_rect,
        1
    )


# ============================================================
# CAMERA
# ============================================================

def update_camera(dt):

    global camera_x
    global camera_y

    keys = pygame.key.get_pressed()

    dx = 0
    dy = 0

    if keys[pygame.K_LEFT] or keys[pygame.K_a]:

        dx -= 1

    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:

        dx += 1

    if keys[pygame.K_UP] or keys[pygame.K_w]:

        dy -= 1

    if keys[pygame.K_DOWN] or keys[pygame.K_s]:

        dy += 1

    if dx != 0 or dy != 0:

        length = math.sqrt(
            dx * dx + dy * dy
        )

        dx /= length
        dy /= length

        camera_x += (
            dx
            * camera_speed
            * dt
        )

        camera_y += (
            dy
            * camera_speed
            * dt
        )

    camera_x = clamp(
        camera_x,
        0,
        WORLD_WIDTH - WIDTH
    )

    camera_y = clamp(
        camera_y,
        0,
        WORLD_HEIGHT - HEIGHT
    )


# ============================================================
# COLLISION WITH BUILDINGS
# ============================================================

def pedestrian_avoids_buildings(pedestrian):

    for building in buildings:

        rect = pygame.Rect(
            building.x,
            building.y,
            building.w,
            building.h
        )

        if rect.collidepoint(
            pedestrian.x,
            pedestrian.y
        ):

            pedestrian.angle += math.pi

            pedestrian.x += (
                math.cos(
                    pedestrian.angle
                ) * 10
            )

            pedestrian.y += (
                math.sin(
                    pedestrian.angle
                ) * 10
            )


# ============================================================
# UPDATE WORLD
# ============================================================

def update_world(dt):

    global world_time

    if paused:

        return

    # Time

    world_time += (
        TIME_SPEED * dt
    )

    if world_time >= 24:

        world_time -= 24

    # Clouds

    for cloud in clouds:

        cloud.update(dt)

    # Traffic lights

    for light in traffic_lights:

        light.update(dt)

    # Cars

    for car in cars:

        car.update(
            dt,
            traffic_lights
        )

    # Buses

    for bus in buses:

        bus.update(
            dt,
            traffic_lights
        )

    # Emergency

    for emergency in emergency_cars:

        emergency.update(
            dt,
            traffic_lights
        )

    # Pedestrians

    for person in pedestrians:

        person.update(dt)

        pedestrian_avoids_buildings(
            person
        )

    # Rain

    if rain_enabled:

        for drop in rain:

            drop.update(dt)


# ============================================================
# DRAW EVERYTHING
# ============================================================

def draw_scene(surface):

    # Sky

    surface.fill(
        get_sky_color()
    )

    # Sun/Moon

    draw_sun(surface)

    draw_moon(surface)

    # Ground

    draw_ground(surface)

    # Parks

    for park in parks:

        park.draw(surface)

    # Roads

    draw_roads(surface)

    # Buildings

    for building in buildings:

        building.draw(
            surface,
            is_night()
        )

    # Clouds

    if not is_night():

        for cloud in clouds:

            cloud.draw(surface)

    # Pedestrians

    for person in pedestrians:

        sx, sy = world_to_screen(
            person.x,
            person.y
        )

        if (
            -20 < sx < WIDTH + 20
            and -20 < sy < HEIGHT + 20
        ):

            person.draw(surface)

    # Cars

    for car in cars:

        sx, sy = world_to_screen(
            car.x,
            car.y
        )

        if (
            -100 < sx < WIDTH + 100
            and -100 < sy < HEIGHT + 100
        ):

            car.draw(
                surface,
                is_night()
            )

    # Buses

    for bus in buses:

        bus.draw(
            surface,
            is_night()
        )

    # Emergency vehicles

    for emergency in emergency_cars:

        emergency.draw(
            surface,
            is_night()
        )

    # Traffic lights

    for light in traffic_lights:

        light.draw(
            surface,
            is_night()
        )

    # Night

    draw_night_overlay(surface)

    # Rain

    if rain_enabled:

        for drop in rain:

            drop.draw(surface)

    # UI

    draw_ui(surface)

    draw_minimap(surface)


# ============================================================
# EVENT HANDLER
# ============================================================

def handle_events():

    global paused
    global rain_enabled
    global world_time

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:

            # Pause

            if event.key == pygame.K_SPACE:

                paused = not paused

            # Rain

            if event.key == pygame.K_r:

                rain_enabled = not rain_enabled

            # Reset camera

            if event.key == pygame.K_HOME:

                reset_camera()

            # Morning

            if event.key == pygame.K_1:

                world_time = 8

            # Evening

            if event.key == pygame.K_2:

                world_time = 18

            # Night

            if event.key == pygame.K_3:

                world_time = 23

            # Random time

            if event.key == pygame.K_4:

                world_time = random.uniform(
                    0,
                    24
                )


# ============================================================
# RESET CAMERA
# ============================================================

def reset_camera():

    global camera_x
    global camera_y

    camera_x = (
        WORLD_WIDTH - WIDTH
    ) / 2

    camera_y = (
        WORLD_HEIGHT - HEIGHT
    ) / 2


# ============================================================
# PERFORMANCE VISIBILITY
# ============================================================

def visible_object(x, y, margin=100):

    sx, sy = world_to_screen(
        x,
        y
    )

    return (
        -margin < sx < WIDTH + margin
        and
        -margin < sy < HEIGHT + margin
    )


# ============================================================
# MAIN
# ============================================================

def main():

    create_city()

    reset_camera()

    running = True

    while running:

        dt = CLOCK.tick(FPS) / 1000.0

        handle_events()

        update_camera(dt)

        update_world(dt)

        draw_scene(SCREEN)

        pygame.display.flip()

    pygame.quit()


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    main()


    # ============================================================
    # NATURAL SNAKE SYSTEM
    # ============================================================

    class Snake:

        def __init__(self, x, y):

            self.x = x
            self.y = y

            self.angle = random.uniform(0, math.pi * 2)

            self.target_angle = self.angle

            self.speed = random.uniform(35, 55)

            self.length = random.randint(22, 30)

            self.segment_distance = 8

            self.segments = []

            # رنگ‌های مار
            self.body_color = random.choice([
                (45, 105, 45),
                (55, 125, 50),
                (75, 135, 55),
                (90, 120, 45)
            ])

            self.dark_color = (
                max(0, self.body_color[0] - 20),
                max(0, self.body_color[1] - 20),
                max(0, self.body_color[2] - 15)
            )

            # ساخت بدن
            for i in range(self.length):
                self.segments.append([
                    self.x - i * self.segment_distance,
                    self.y
                ])

            self.wander_timer = 0

            self.blink_timer = random.uniform(2, 6)

            self.eye_blink = False

        # --------------------------------------------------------
        # Natural wandering
        # --------------------------------------------------------

        def choose_direction(self):

            self.target_angle += random.uniform(
                -0.8,
                0.8
            )

        # --------------------------------------------------------
        # Update
        # --------------------------------------------------------

        def update(self, dt):

            self.wander_timer -= dt

            if self.wander_timer <= 0:
                self.choose_direction()

                self.wander_timer = random.uniform(
                    1.0,
                    3.5
                )

            # Smooth turning
            difference = (
                    self.target_angle
                    - self.angle
            )

            while difference > math.pi:
                difference -= math.pi * 2

            while difference < -math.pi:
                difference += math.pi * 2

            self.angle += difference * dt * 1.8

            # Slight natural movement
            wave = math.sin(
                pygame.time.get_ticks() * 0.006
            ) * 0.15

            move_angle = self.angle + wave

            self.x += (
                    math.cos(move_angle)
                    * self.speed
                    * dt
            )

            self.y += (
                    math.sin(move_angle)
                    * self.speed
                    * dt
            )

            # City boundaries
            margin = 100

            if self.x < margin:

                self.target_angle = 0

            elif self.x > WORLD_WIDTH - margin:

                self.target_angle = math.pi

            if self.y < margin:

                self.target_angle = math.pi / 2

            elif self.y > WORLD_HEIGHT - margin:

                self.target_angle = -math.pi / 2

            # Head position
            self.segments[0][0] = self.x
            self.segments[0][1] = self.y

            # Follow system
            for i in range(1, len(self.segments)):

                previous = self.segments[i - 1]

                current = self.segments[i]

                dx = previous[0] - current[0]
                dy = previous[1] - current[1]

                dist = math.sqrt(
                    dx * dx + dy * dy
                )

                if dist > self.segment_distance:
                    ratio = (
                                    dist - self.segment_distance
                            ) / dist

                    current[0] += dx * ratio * 0.65
                    current[1] += dy * ratio * 0.65

            # Blink
            self.blink_timer -= dt

            if self.blink_timer <= 0:
                self.eye_blink = not self.eye_blink

                self.blink_timer = (
                    0.15
                    if self.eye_blink
                    else random.uniform(2, 5)
                )

        # --------------------------------------------------------
        # Draw shadow
        # --------------------------------------------------------

        def draw_shadow(self, surface):

            for i in range(
                    len(self.segments) - 1,
                    -1,
                    -2
            ):
                x, y = self.segments[i]

                sx, sy = world_to_screen(
                    x + 4,
                    y + 6
                )

                radius = max(
                    3,
                    int(10 - i * 0.25)
                )

                pygame.draw.circle(
                    surface,
                    (40, 80, 40),
                    (sx, sy),
                    radius
                )

        # --------------------------------------------------------
        # Draw body
        # --------------------------------------------------------

        def draw(self, surface):

            # Shadow first
            self.draw_shadow(surface)

            # Body from tail to head
            for i in range(
                    len(self.segments) - 1,
                    -1,
                    -1
            ):

                x, y = self.segments[i]

                sx, sy = world_to_screen(
                    x,
                    y
                )

                # Body gets smaller toward tail
                size = max(
                    3,
                    int(
                        10
                        - (i / self.length) * 6
                    )
                )

                # Dark underside
                pygame.draw.circle(
                    surface,
                    self.dark_color,
                    (sx + 1, sy + 2),
                    size
                )

                # Main body
                pygame.draw.circle(
                    surface,
                    self.body_color,
                    (sx, sy),
                    size
                )

                # Natural pattern
                if i % 3 == 0:
                    pygame.draw.circle(
                        surface,
                        (
                            max(
                                0,
                                self.body_color[0] - 15
                            ),
                            max(
                                0,
                                self.body_color[1] - 10
                            ),
                            max(
                                0,
                                self.body_color[2] - 5
                            )
                        ),
                        (sx, sy),
                        max(2, size // 3)
                    )

            # ----------------------------------------------------
            # Head
            # ----------------------------------------------------

            hx, hy = world_to_screen(
                self.x,
                self.y
            )

            head_size = 13

            pygame.draw.circle(
                surface,
                self.dark_color,
                (
                    hx + 2,
                    hy + 2
                ),
                head_size + 1
            )

            pygame.draw.circle(
                surface,
                self.body_color,
                (
                    hx,
                    hy
                ),
                head_size
            )

            # ----------------------------------------------------
            # Eyes
            # ----------------------------------------------------

            eye_distance = 6

            left_eye_x = (
                    hx
                    + math.cos(
                self.angle + 0.65
            ) * eye_distance
            )

            left_eye_y = (
                    hy
                    + math.sin(
                self.angle + 0.65
            ) * eye_distance
            )

            right_eye_x = (
                    hx
                    + math.cos(
                self.angle - 0.65
            ) * eye_distance
            )

            right_eye_y = (
                    hy
                    + math.sin(
                self.angle - 0.65
            ) * eye_distance
            )

            if not self.eye_blink:
                pygame.draw.circle(
                    surface,
                    (235, 235, 190),
                    (
                        int(left_eye_x),
                        int(left_eye_y)
                    ),
                    3
                )

                pygame.draw.circle(
                    surface,
                    (235, 235, 190),
                    (
                        int(right_eye_x),
                        int(right_eye_y)
                    ),
                    3
                )

                pygame.draw.circle(
                    surface,
                    BLACK,
                    (
                        int(left_eye_x),
                        int(left_eye_y)
                    ),
                    1
                )

                pygame.draw.circle(
                    surface,
                    BLACK,
                    (
                        int(right_eye_x),
                        int(right_eye_y)
                    ),
                    1
                )

            # ----------------------------------------------------
            # Tongue
            # ----------------------------------------------------

            tongue_start_x = (
                    hx
                    + math.cos(self.angle)
                    * 10
            )

            tongue_start_y = (
                    hy
                    + math.sin(self.angle)
                    * 10
            )

            tongue_end_x = (
                    hx
                    + math.cos(self.angle)
                    * 22
            )

            tongue_end_y = (
                    hy
                    + math.sin(self.angle)
                    * 22
            )

            pygame.draw.line(
                surface,
                (180, 50, 60),
                (
                    int(tongue_start_x),
                    int(tongue_start_y)
                ),
                (
                    int(tongue_end_x),
                    int(tongue_end_y)
                ),
                2
            )

            # Fork
            fork_angle = 0.35

            fork_length = 7

            pygame.draw.line(
                surface,
                (180, 50, 60),
                (
                    int(tongue_end_x),
                    int(tongue_end_y)
                ),
                (
                    int(
                        tongue_end_x
                        + math.cos(
                            self.angle + fork_angle
                        ) * fork_length
                    ),
                    int(
                        tongue_end_y
                        + math.sin(
                            self.angle + fork_angle
                        ) * fork_length
                    )
                ),
                1
            )

            pygame.draw.line(
                surface,
                (180, 50, 60),
                (
                    int(tongue_end_x),
                    int(tongue_end_y)
                ),
                (
                    int(
                        tongue_end_x
                        + math.cos(
                            self.angle - fork_angle
                        ) * fork_length
                    ),
                    int(
                        tongue_end_y
                        + math.sin(
                            self.angle - fork_angle
                        ) * fork_length
                    )
                ),
                1
            )


    # ============================================================
    # CREATE SNAKES
    # ============================================================

    snakes = []


    def create_snakes():

        snakes.clear()

        # مارها را در پارک‌های شهر قرار می‌دهیم
        if parks:

            for park in parks:

                if random.random() < 0.7:
                    x = random.randint(
                        int(park.x + 30),
                        int(
                            park.x
                            + park.w
                            - 30
                        )
                    )

                    y = random.randint(
                        int(park.y + 30),
                        int(
                            park.y
                            + park.h
                            - 30
                        )
                    )

                    snakes.append(
                        Snake(
                            x,
                            y
                        )
                    )

        # اگر پارک کم بود، چند مار اضافه
        while len(snakes) < 5:
            snakes.append(
                Snake(
                    random.randint(
                        100,
                        WORLD_WIDTH - 100
                    ),
                    random.randint(
                        100,
                        WORLD_HEIGHT - 100
                    )
                )
            )


    # ============================================================
    # UPDATE SNAKES
    # ============================================================

    def update_snakes(dt):

        if paused:
            return

        for snake in snakes:
            snake.update(dt)


    # ============================================================
    # DRAW SNAKES
    # ============================================================

    def draw_snakes(surface):

        for snake in snakes:

            if visible_object(
                    snake.x,
                    snake.y,
                    150
            ):
                snake.draw(surface)