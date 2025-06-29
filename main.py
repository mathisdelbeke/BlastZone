#!/usr/bin/env python3

import sys
import enum
import dataclasses
import random
import pygame

@dataclasses.dataclass
class Pos:
    x : int
    y : int

class DuckHorDirection(enum.Enum):
    LEFT = 0
    RIGHT = 1

class DuckVerDirection(enum.Enum):
    UP = 0
    DOWN = 1

class Duck:
    def __init__(self):
        self.pos = Pos(0, 0)
        self.width = 120
        self.height = 90
        self.speed = 5
        self.hor_direction = DuckHorDirection.LEFT
        self.ver_direction = DuckVerDirection.UP

class DuckGame:
    def __init__(self):
        pygame.init()
        display_info = pygame.display.Info()
        self.screen_width = display_info.current_w
        self.screen_height = display_info.current_h
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.duck_count = 5
        self.ducks = [Duck() for _ in range(self.duck_count)]
        self.duck_images = []
        self.fetch_duck_images()
        for duck in self.ducks: self.init_duck_position(duck)
        self.init_ducks_directions()
        self.game_loop(pygame.time.Clock())

    def fetch_duck_images(self):
        self.duck_images.append(pygame.image.load("duckImages/duck_left_wings_down.png").convert_alpha())
        self.duck_images.append(pygame.image.load("duckImages/duck_right_wings_down.png").convert_alpha())
    
    def init_duck_position(self, duck):
        random_x = random.randint(0, (self.screen_width - duck.width))
        random_y = random.randint(0, self.screen_height - duck.height)
        is_unique = False
        while (not is_unique):
            for other_duck in self.ducks:
                if (duck == other_duck): continue

                if ((not (random_x + duck.width) < other_duck.pos.x) and (not random_x > (other_duck.pos.x + other_duck.width))):
                    random_x = random.randint(0, (self.screen_width - duck.width))
                    is_unique = False
                    break
                elif ((not (random_y + duck.height) < duck.pos.y) and (not random_y > (duck.pos.y + duck.height))):    
                    random_y = random.randint(0, self.screen_height - duck.height)
                    is_unique = False
                    break
                else:
                    is_unique = True

        duck.pos.x = random_x
        duck.pos.y = random_y

    def init_ducks_directions(self):
        for i in range(len(self.ducks)):
            if i % 2 == 0: 
                self.ducks[i].hor_direction = DuckHorDirection.LEFT
                self.ducks[i].ver_direction = DuckVerDirection.UP
            else: 
                self.ducks[i].hor_direction = DuckHorDirection.RIGHT
                self.ducks[i].ver_direction = DuckVerDirection.DOWN

    def game_loop(self, clock):
        while True:
            self.check_quit_event()
            self.move_ducks()
            self.handle_wall_collisions()
            self.draw_everything()
            clock.tick(60)

    def check_quit_event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

    def move_ducks(self):
        for duck in self.ducks:
            if (duck.hor_direction == DuckHorDirection.LEFT): duck.pos.x = duck.pos.x - duck.speed
            elif (duck.hor_direction == DuckHorDirection.RIGHT): duck.pos.x = duck.pos.x + duck.speed

            if (duck.ver_direction == DuckVerDirection.UP): duck.pos.y = duck.pos.y - duck.speed
            elif (duck.ver_direction == DuckVerDirection.DOWN): duck.pos.y = duck.pos.y + duck.speed

    def handle_wall_collisions(self):
        for duck in self.ducks:
            if (duck.pos.x < 0): duck.hor_direction = DuckHorDirection.RIGHT
            elif ((duck.pos.x + duck.width) >= self.screen_width): duck.hor_direction = DuckHorDirection.LEFT

            if (duck.pos.y < 0): duck.ver_direction = DuckVerDirection.DOWN
            elif ((duck.pos.y + duck.height) >= self.screen_height): duck.ver_direction = DuckVerDirection.UP 

    def draw_everything(self):
        self.screen.fill((150, 150, 255))   # Background
        for duck in self.ducks:
            self.screen.blit(self.duck_images[duck.hor_direction.value], (duck.pos.x, duck.pos.y)) 
        pygame.display.flip()

if __name__ == "__main__":
    duck_game = DuckGame()

