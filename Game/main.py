import sys
import enum
import dataclasses
import random
import pygame
import serial
import time

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
    com_port = 'COM5'
    com_baud_rate = 9600
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("BlastZone")
        display_info = pygame.display.Info()
        self.error = ""
        self.screen_width = display_info.current_w
        self.screen_height = display_info.current_h
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.kills = 0
        self.duck_count = 5
        self.ducks = [Duck() for _ in range(self.duck_count)]
        self.duck_images = []
        self.fetch_duck_images()
        for duck in self.ducks: self.init_duck_position(duck)
        self.init_ducks_directions()
        self.draw_everything()
        self.is_com_connected = False
        self.connect_com_port()
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

    def connect_com_port(self):
        while (not self.is_com_connected):
            try:
                ser = serial.Serial(self.com_port, self.com_baud_rate, timeout=10)
                self.is_com_connected = True
                self.error = ""
                        
            except serial.SerialException as e:
                self.error = f"Error {e}"
                self.draw_everything()
                time.sleep(3)

    def game_loop(self, clock):
        while True:
            self.check_events()
            self.move_ducks()
            self.handle_wall_collisions()
            self.draw_everything()
            clock.tick(60)

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                button = event.button
                if (button == 1): self.shoot_gun(pos)

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

        kills_font = pygame.font.SysFont(None, 48)
        kills_text_surface = kills_font.render(f"Kills: {self.kills}", True, (255, 255, 255))
        self.screen.blit(kills_text_surface, (0, 0))

        error_font = pygame.font.SysFont(None, 24)
        error_text_surface = error_font.render(f"{self.error}", True, (255, 255, 255))
        self.screen.blit(error_text_surface, (0, self.screen_height - 50))

        pygame.display.flip()

if __name__ == "__main__":
    duck_game = DuckGame()