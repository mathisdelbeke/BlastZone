import sys
import enum
import dataclasses
import random
import pygame
import serial
import time
import struct

@dataclasses.dataclass
class Pos:
    x : int
    y : int

class DuckHorDirection(enum.Enum):
    LEFT = 0
    RIGHT = 1
    NONE = 2

class DuckVerDirection(enum.Enum):
    UP = 0
    DOWN = 1

class Duck:
    def __init__(self):
        self.is_alive = True
        self.pos = Pos(0, 0)
        self.width = 120
        self.height = 90
        self.speed = 5
        self.hor_direction = DuckHorDirection.LEFT
        self.ver_direction = DuckVerDirection.UP

class DuckGame:
    COM_PORT = 'COM5'
    COM_BAUD_RATE = 9600
    UART_MSSG_HEADER = 0xAA
    NUM_MPU6500_BYTES = 6
    REFRESH_FREQ = 60
    GYRO_SCALE_FACTOR = 131.0
    HPF_ALPHA = 0.8

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("BlastZone")
        display_info = pygame.display.Info()
        self.error = ""
        self.screen_width = display_info.current_w
        self.screen_height = display_info.current_h
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))

        self.prev_gx_dps = 0
        self.prev_gy_dps = 0
        self.prev_gz_dps = 0
        self.gx_dps_fil = 0
        self.gy_dps_fil = 0
        self.gz_dps_fil = 0
        self.aim_point = Pos((self.screen_width / 2), self.screen_height / 2)

        self.kills = 0
        self.aim_sensitivity = 50

        self.duck_count = 5
        self.ducks = [Duck() for _ in range(self.duck_count)]
        self.duck_images = []
        self.fetch_duck_images()
        for duck in self.ducks: self.init_duck_position(duck)
        self.init_ducks_directions()
        self.draw_everything()

        self.serial = None
        self.is_com_connected = False
        self.connect_to_com()
        
        # Start game
        self.game_loop(pygame.time.Clock())

    def fetch_duck_images(self):
        self.duck_images.append(pygame.image.load("duckImages/duck_left_wings_down.png").convert_alpha())
        self.duck_images.append(pygame.image.load("duckImages/duck_right_wings_down.png").convert_alpha())
        self.duck_images.append(pygame.image.load("duckImages/duck_dead.png").convert_alpha())
    
    def init_duck_position(self, duck):
        duck.pos.x = random.randint(0, self.screen_width - duck.width)
        duck.pos.y = random.randint(0, self.screen_height - duck.height)

    def init_ducks_directions(self):
        for i in range(len(self.ducks)):
            if i % 2 == 0: 
                self.ducks[i].hor_direction = DuckHorDirection.LEFT
                self.ducks[i].ver_direction = DuckVerDirection.UP
            else: 
                self.ducks[i].hor_direction = DuckHorDirection.RIGHT
                self.ducks[i].ver_direction = DuckVerDirection.DOWN

    def connect_to_com(self):
        while (not self.is_com_connected):
            try:
                self.serial = serial.Serial(self.COM_PORT, self.COM_BAUD_RATE, timeout=1)
                self.is_com_connected = True
                self.error = ""
            except serial.SerialException as e:
                self.error = f"Error {e}"
                self.draw_everything()
                time.sleep(1)

    def game_loop(self, clock):
        while True:
            self.check_events()
            self.update_aim_pos()
            self.move_ducks()
            self.handle_wall_collisions()
            self.draw_everything()
            clock.tick(self.REFRESH_FREQ)

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                button = event.button
                if (button == 1): self.shoot_gun(pos)                                   # Needs to go

    def update_aim_pos(self):
        data = self.read_com_port()
        if (data is not None):
            gx, gy, gz = struct.unpack(">hhh", data)
            gx_dps = gx / self.GYRO_SCALE_FACTOR
            gy_dps = gy / self.GYRO_SCALE_FACTOR
            gz_dps = gz / self.GYRO_SCALE_FACTOR

            self.gx_dps_fil = self.HPF_ALPHA * (self.gx_dps_fil + gx_dps - self.prev_gx_dps)       # hpf
            self.gy_dps_fil = self.HPF_ALPHA * (self.gy_dps_fil + gy_dps - self.prev_gy_dps)
            self.gz_dps_fil = self.HPF_ALPHA * (self.gz_dps_fil + gz_dps - self.prev_gz_dps)
            self.prev_gx_dps = gx_dps
            self.prev_gy_dps = gy_dps
            self.prev_gz_dps = gz_dps
            print(f"{self.gx_dps_fil:.0f}, {self.gy_dps_fil:.0f}, {self.gz_dps_fil:.0f}")

            self.aim_point.x -= (self.gz_dps_fil * self.aim_sensitivity * (1 / self.REFRESH_FREQ))       # more precise time???
            self.aim_point.y -= (self.gx_dps_fil * self.aim_sensitivity * (1 / self.REFRESH_FREQ)) 

            self.aim_point.x = max(0, min(self.screen_width, self.aim_point.x))
            self.aim_point.y = max(0, min(self.screen_height, self.aim_point.y))

    def read_com_port(self):
        try:
            if (self.serial.in_waiting >= 1):
                byte = self.serial.read(1)
                if (byte[0] == self.UART_MSSG_HEADER):
                    if (self.serial.in_waiting >= self.NUM_MPU6500_BYTES):
                        data_bytes = self.serial.read(self.NUM_MPU6500_BYTES)
                        if (len(data_bytes) == self.NUM_MPU6500_BYTES): return data_bytes
        
        except serial.SerialException:                                               
            self.is_com_connected = False
            self.connect_to_com()

    def shoot_gun(self, shot_pos):
        shot_x, shot_y = shot_pos
        for duck in self.ducks:
            if ((duck.pos.x <= shot_x <= (duck.pos.x + duck.width)) and (duck.pos.y <= shot_y <= (duck.pos.y + duck.height))):
                if (duck.is_alive): self.kill_duck(duck)

    def kill_duck(self, duck):
        duck.is_alive = False
        duck.ver_direction = DuckVerDirection.DOWN
        duck.hor_direction = DuckHorDirection.NONE
        self.kills += 1

    def move_ducks(self):
        for duck in self.ducks:
            if (duck.hor_direction == DuckHorDirection.LEFT): duck.pos.x = duck.pos.x - duck.speed
            elif (duck.hor_direction == DuckHorDirection.RIGHT): duck.pos.x = duck.pos.x + duck.speed

            if (duck.ver_direction == DuckVerDirection.UP): duck.pos.y = duck.pos.y - duck.speed
            elif (duck.ver_direction == DuckVerDirection.DOWN): duck.pos.y = duck.pos.y + duck.speed


    def handle_wall_collisions(self):
        for duck in self.ducks:
            if (duck.is_alive):
                if (duck.pos.x < 0): duck.hor_direction = DuckHorDirection.RIGHT
                elif ((duck.pos.x + duck.width) >= self.screen_width): duck.hor_direction = DuckHorDirection.LEFT

                if (duck.pos.y < 0): duck.ver_direction = DuckVerDirection.DOWN
                elif ((duck.pos.y + duck.height) >= self.screen_height): duck.ver_direction = DuckVerDirection.UP
            else:
                if (duck.pos.y > self.screen_height): 
                    self.respawn_duck(duck)
                
    def respawn_duck(self, duck):
        self.init_duck_position(duck)
        duck.is_alive = True
        if (self.kills % 2 == 0): 
            duck.hor_direction = DuckHorDirection.LEFT
            duck.ver_direction = DuckVerDirection.UP
        else:
            duck.hor_direction = DuckHorDirection.RIGHT
            duck.ver_direction = DuckVerDirection.DOWN
    
    def draw_everything(self):
        self.screen.fill((150, 150, 255))   # Background

        for duck in self.ducks:
            if (duck.is_alive):
                self.screen.blit(self.duck_images[duck.hor_direction.value], (duck.pos.x, duck.pos.y))
            else:
                   self.screen.blit(self.duck_images[DuckHorDirection.NONE.value], (duck.pos.x, duck.pos.y))

        pygame.draw.circle(self.screen, (0, 0, 0), (self.aim_point.x, self.aim_point.y), 5, 0)  # width=0 = filled circle

        kills_font = pygame.font.SysFont(None, 48)
        kills_text_surface = kills_font.render(f"Kills: {self.kills}", True, (255, 255, 255))
        self.screen.blit(kills_text_surface, (0, 0))

        error_font = pygame.font.SysFont(None, 24)
        error_text_surface = error_font.render(f"{self.error}", True, (255, 255, 255))
        self.screen.blit(error_text_surface, (0, self.screen_height - 50))

        pygame.display.flip()

if __name__ == "__main__":
    duck_game = DuckGame()