"""
Alexsander Rosante's creation 2022
"""

from pygame.locals import *

import math
import random
import pygame

pygame.init()
pygame.mixer.init()


# UI ###################################################################################################################
class Button(pygame.sprite.Sprite):
    def __init__(self, text='Hello', color='yellow', bg_color='blue', padx=5, pady=0, on_click=lambda: None):
        super().__init__()

        # properties
        font = pygame.font.Font('font/ArchivoBlack.ttf', 48)
        self.on_click = on_click

        # surface
        text_surf = font.render(text, True, color)
        surf_w = text_surf.get_width() + 2 * padx
        surf_h = text_surf.get_height() + 2 * pady

        # idle surfcae
        self.surf_idle = pygame.Surface((surf_w, surf_h), SRCALPHA)
        self.surf_idle.blit(text_surf, (padx, pady))

        # hovered idle
        self.surf_hovered = pygame.Surface((surf_w, surf_h))
        self.surf_hovered.fill(color)
        text_surf = font.render(text, True, bg_color)
        self.surf_hovered.blit(text_surf, (padx, pady))

        # image'n'rect
        self.image = self.surf_idle.copy()
        self.rect = self.image.get_rect()

    def set_as_hovered(self):
        self.image = self.surf_hovered.copy()

    def set_as_idle(self):
        self.image = self.surf_idle.copy()


class Caption(pygame.sprite.Sprite):
    def __init__(self, text):
        super().__init__()
        font = pygame.font.Font('font/SourceSansPro-Italic.ttf', 28)
        self.image = font.render(text, True, 'orange', 'black')
        self.rect = self.image.get_rect(midbottom=(screen_w / 2, screen_h * .9))


class ChannelIndicator(pygame.sprite.Sprite):
    def __init__(self, number: int, pady=5):
        super().__init__()
        font = pygame.font.Font('font/ArchivoBlack.ttf', 32)
        number_surf = font.render(str(number), True, 'white')
        self.image = pygame.Surface((round(0.12 * screen_w), number_surf.get_height() + 2 * pady))
        self.image.fill('darkblue')
        self.rect = self.image.get_rect()
        number_rect = number_surf.get_rect(midright=(self.rect.w - 5, self.rect.h / 2))
        self.image.blit(number_surf, number_rect)
        self.dur = 60

    def update(self):
        if not self.dur:
            self.kill()
            return
        self.dur -= 1


class Text(pygame.sprite.Sprite):
    def __init__(self, text, color='yellow'):
        super().__init__()
        font = pygame.font.Font('font/ArchivoBlack.ttf', 48)
        font.set_italic(True)
        self.image = font.render(text, True, color)
        self.rect = self.image.get_rect()
        self.alpha = 255


# Scene ################################################################################################################
class Scene:
    def __init__(self, channel_num=1):

        # properties
        self.bg_color = 'blue'
        self.channel_num = channel_num

        # overlay
        self.crt_overlay = pygame.image.load('pics/border.png').convert_alpha()

        # draw group
        self.drawables = pygame.sprite.LayeredUpdates()

        # update groups
        self.buttons = pygame.sprite.Group()
        self.caption = pygame.sprite.GroupSingle()
        self.channel_indicator = pygame.sprite.GroupSingle()

        # states
        self.hovered = pygame.sprite.GroupSingle()

        self.draw_crt_lines()
        self.show_channel_num()

    def add_button(self, button: Button):
        self.buttons.add(button)
        self.show(button)

    def add_caption(self, caption: Caption):
        if self.caption.sprite:
            self.caption.sprite.kill()
        self.caption.add(caption)
        self.show(caption)

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
                elif event.button == 4:
                    game.previous_channel()
                elif event.button == 5:
                    game.next_channel()

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

    def show_channel_num(self):
        indicator = ChannelIndicator(self.channel_num)
        indicator.rect.topright = .9 * screen_w, .1 * screen_h
        self.channel_indicator.add(indicator)
        self.show(indicator)

    def update(self, events: list):
        self.check_collisions()
        self.check_events(events)
        self.cursor_by_context()
        self.buttons.update()
        self.channel_indicator.update()

    def update_weak(self):
        pass

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


class NoSignal(Scene):
    """Offline"""
    def __init__(self, channel_num: int):
        super().__init__(channel_num)

    def update(self, events: list):
        super().update(events)

    def draw(self, surface: pygame.Surface):
        draw_color_bars(surface)
        self.drawables.draw(surface)
        surface.blit(self.crt_overlay, (0, 0))


class Channel1(Scene):
    """Tutorial"""

    def __init__(self):
        super().__init__(channel_num=1)


class Channel2(NoSignal):
    def __init__(self):
        super().__init__(2)


class Channel3(Scene):
    """A woman says the lucky numbers indefinitely"""

    def __init__(self):
        super().__init__(channel_num=3)
        lucky_nums_list = list(str(game.lucky_nums))
        self.speech_list = ['the_numbers_are', *lucky_nums_list, 'repeating', *lucky_nums_list]
        self.frame = 0.00
        self.speech_speed = .01

    def say_the_lucky_nums(self):
        if self.frame >= len(self.speech_list):
            self.frame = 0.00
        if '{:.2f}'.format(self.frame)[-2:] == '00':
            pygame.mixer.Sound(f'sfxs/{self.speech_list[int(self.frame)]}.mp3').play()
            caption_text = self.speech_list[int(self.frame)]
            caption_text = 'the numbers are' if caption_text == 'the_numbers_are' else caption_text
            self.add_caption(Caption(caption_text))
        self.frame = round(self.frame + self.speech_speed, 2)

    def update_weak(self):
        if self.frame >= len(self.speech_list):
            self.frame = 0.00
        self.frame = round(self.frame + self.speech_speed, 2)

    def update(self, events: list):
        super().update(events)
        self.say_the_lucky_nums()


class Channel4(NoSignal):
    def __init__(self):
        super().__init__(4)


class Channel5(NoSignal):
    def __init__(self):
        super().__init__(5)


class Channel6(Scene):
    """Pentagram"""

    def __init__(self):
        super().__init__(channel_num=6)
        self.bg_color = (20, 20, 20)


class Channel7(NoSignal):
    def __init__(self):
        super().__init__(7)


class Channel8(Scene):
    """Offline, but with puzzle instruction"""

    def __init__(self):
        super().__init__(channel_num=8)

    def draw(self, surface: pygame.Surface):
        draw_color_bars(surface, game.lucky_colors)
        self.drawables.draw(surface)
        surface.blit(self.crt_overlay, (0, 0))


class Channel9(NoSignal):
    def __init__(self):
        super().__init__(9)


class Channel10(NoSignal):
    def __init__(self):
        super().__init__(10)


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
        self.scene = Scene()

        self.lucky_nums = random.randint(10000, 99999)
        self.lucky_colors = ['yellow', 'cyan', 'green', 'magenta', 'blue']
        random.shuffle(self.lucky_colors)

        self.channels = {}
        self.cur_channel = 3

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

    def next_channel(self):
        self.cur_channel += 1
        if self.cur_channel > len(self.channels):
            self.cur_channel = 1
        self.scene = self.channels[self.cur_channel]
        self.scene.show_channel_num()

    def previous_channel(self):
        self.cur_channel -= 1
        if self.cur_channel < 1:
            self.cur_channel = len(self.channels)
        self.scene = self.channels[self.cur_channel]
        self.scene.show_channel_num()

    def quit(self):
        self.loop = False

    def set_channels(self):
        self.channels = {1: Channel1(),
                         2: Channel2(),
                         3: Channel3(),
                         4: Channel4(),
                         5: Channel5(),
                         6: Channel6(),
                         7: Channel7(),
                         8: Channel8(),
                         9: Channel9(),
                         10: Channel10()}
        self.scene = self.channels[self.cur_channel]

    def update_weak(self):
        for channel in self.channels.values():
            if not channel == self.scene:
                channel.update_weak()

    def run(self):
        self.set_channels()
        while self.loop:
            self.check_events()
            self.scene.update(self.events)
            self.update_weak()
            self.scene.draw(self.screen)
            pygame.display.update()
            self.clock.tick(fps)
        pygame.quit()


# Functions ############################################################################################################

def draw_color_bars(surface: pygame.Surface,
                    colors=('white', 'yellow', 'cyan', 'green', 'magenta', 'red', 'blue', (20, 20, 20))):
    bar_w, bar_h = math.ceil(surface.get_width() / len(colors)), surface.get_height()
    for i, color in enumerate(colors):
        pygame.draw.rect(surface, color, [bar_w * i, 0, bar_w, bar_h])


if __name__ == '__main__':
    # properties
    version = '0.1.3a'
    screen_w = 648
    screen_h = 648
    fps = 60

    game = Game()
    game.run()
