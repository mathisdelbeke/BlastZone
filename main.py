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

class DuckDirection(enum.Enum):
    LEFT = 0
    RIGHT = 1

class Duck:
    def __init__(self):
        self.pos = Pos(0, 0)
        self.width = 120
        self.height = 90
        self.speed = 5
        self.direction = DuckDirection.LEFT

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

    def game_loop(self, clock):
        while True:
            self.check_quit_event()
            for duck in self.ducks: self.init_duck_position(duck)
            self.draw_everything()
            clock.tick(1)

    def check_quit_event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

    def update_duck_pos(self):
        x, y = self.duck.pos
        nx, ny = x, y

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            nx = x - self.duck.speed
            self.duck.direction = DuckDirection.LEFT
        if keys[pygame.K_RIGHT]:
            nx = x + self.duck.speed
            self.duck.direction = DuckDirection.RIGHT
        if keys[pygame.K_UP]:
            ny = y - self.duck.speed
        if keys[pygame.K_DOWN]:
            ny = y + self.duck.speed
        
        self.duck.pos = (nx, ny)

    def draw_everything(self):
        self.screen.fill((150, 150, 255))   # Background
        for duck in self.ducks:
            self.screen.blit(self.duck_images[duck.direction.value], (duck.pos.x, duck.pos.y)) 
        pygame.display.flip()

if __name__ == "__main__":
    duck_game = DuckGame()

