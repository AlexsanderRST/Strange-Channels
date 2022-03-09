"""
Alexsander Rosante's creation 2022
"""

from random import randint
from pygame.locals import *

import pygame

pygame.init()
pygame.mixer.init()


# UI ###################################################################################################################
class Button(pygame.sprite.Sprite):
    def __init__(self, text='Hello', color='yellow', bg_color='blue', padx=5, pady=0, on_click=lambda: None):
        super().__init__()

        # properties
        font = pygame.font.Font('font/VT323.ttf', 75)
        self.on_click = on_click

        # surface
        text_surf = font.render(text, False, color)
        surf_w = text_surf.get_width() + 2 * padx
        surf_h = text_surf.get_height() + 2 * pady

        # idle surfcae
        self.surf_idle = pygame.Surface((surf_w, surf_h), SRCALPHA)
        self.surf_idle.blit(text_surf, (padx, pady))

        # hovered idle
        self.surf_hovered = pygame.Surface((surf_w, surf_h))
        self.surf_hovered.fill(color)
        text_surf = font.render(text, False, bg_color)
        self.surf_hovered.blit(text_surf, (padx, pady))

        # image'n'rect
        self.image = self.surf_idle.copy()
        self.rect = self.image.get_rect()

    def set_as_hovered(self):
        self.image = self.surf_hovered.copy()

    def set_as_idle(self):
        self.image = self.surf_idle.copy()


class Text(pygame.sprite.Sprite):
    def __init__(self, text, color='yellow'):
        super().__init__()
        font = pygame.font.Font('font/VT323.ttf', 75)
        self.image = font.render(text, True, color)
        self.rect = self.image.get_rect()


# Scene ################################################################################################################
class Scene:
    def __init__(self):
        self.bg_color = 'blue'
        self.crt_overlay = pygame.image.load('pics/border.png').convert_alpha()
        self.buttons = pygame.sprite.Group()
        self.hovered = pygame.sprite.GroupSingle()
        self.drawables = pygame.sprite.LayeredUpdates()

        self.draw_crt_lines()

    def add_button(self, button: Button):
        self.buttons.add(button)
        self.show(button)

    def add_text(self, text: Text):
        self.show(text)

    def check_collisions(self):
        mouse_pos = pygame.mouse.get_pos()
        for button in self.buttons:
            if button.rect.collidepoint(mouse_pos):
                button.set_as_hovered()
                self.hovered.add(button)
            else:
                button.set_as_idle()
                self.hovered.remove(button)

    def check_events(self, events: list):
        for event in events:
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    for button in self.buttons:
                        if button.rect.collidepoint(event.pos):
                            button.on_click()

    def cursor_by_context(self):
        if self.hovered:
            pygame.mouse.set_cursor(SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(SYSTEM_CURSOR_ARROW)

    def draw_crt_lines(self, n_lines=140, alpha=.3):
        lines_surf = pygame.Surface((screen_w, screen_h), SRCALPHA)
        for i in range(n_lines):
            y = round(screen_h / n_lines * i)
            pygame.draw.line(lines_surf, 'black', (0, y), (screen_w, y))
        lines_surf.set_alpha(round(255 * alpha))
        self.crt_overlay.blit(lines_surf, (0, 0))

    def hide(self, sprite: pygame.sprite.Sprite):
        self.drawables.remove(sprite)

    def show(self, sprite: pygame.sprite.Sprite):
        self.drawables.add(sprite)

    def update(self, events: list):
        self.check_collisions()
        self.check_events(events)
        self.cursor_by_context()
        self.buttons.update()

    def draw(self, surface: pygame.Surface):
        surface.fill(self.bg_color)
        self.drawables.draw(surface)
        surface.blit(self.crt_overlay, (0, 0))


class SceneMenu(Scene):
    def __init__(self):
        super().__init__()

        # add buttons
        for i in range(1, 5):
            button = Button(f'Tape {i}')
            button.rect.center = screen_w / 2, i / 5 * screen_h
            self.add_button(button)


class SceneWomanCode(Scene):
    def __init__(self):
        super().__init__()



class SceneQuit(Scene):
    def __init__(self, previous_scene: Scene):
        super().__init__()

        # text
        text = Text('Quit the game?')
        text.rect.midbottom = screen_w / 2, screen_h / 2 - 10
        self.add_text(text)

        # buttons
        no_button = Button('No', on_click=lambda: game.change_scene(previous_scene))
        no_button.rect.topleft = screen_w / 2 + 10, screen_h / 2 + 10
        self.add_button(no_button)
        yes_button = Button('Yes', on_click=game.quit)
        yes_button.rect.topright = screen_w / 2 - 10, screen_h / 2 + 10
        self.add_button(yes_button)


# Game #################################################################################################################
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((screen_w, screen_h), NOFRAME)
        pygame.display.set_caption(f'My Program ({version})')
        self.clock = pygame.time.Clock()
        self.events = pygame.event.get()
        self.loop = True
        self.scene = SceneMenu()

        self.lucky_number = randint(10000, 99999)

    def change_scene(self, scene: Scene):
        self.scene = scene

    def check_events(self):
        self.events = pygame.event.get()
        for event in self.events:
            if event.type == QUIT:
                self.quit()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.scene = SceneQuit(self.scene)

    def quit(self):
        self.loop = False

    def run(self):
        while self.loop:
            self.check_events()
            self.scene.update(self.events)
            self.scene.draw(self.screen)
            pygame.display.update()
            self.clock.tick(fps)
        pygame.quit()


# Functions ############################################################################################################


if __name__ == '__main__':
    # properties
    version = '0.1'
    screen_w = 648
    screen_h = 648
    fps = 60

    game = Game()
    game.run()
