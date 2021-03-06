"""
Alexsander Rosante's creation 2022
"""

from pygame.locals import *

import json
import math
import random
import pygame

pygame.init()
pygame.mixer.init()


# UI ###################################################################################################################
class Button(pygame.sprite.Sprite):
    def __init__(self,
                 text='Hello',
                 color='yellow',
                 bg_color=None,
                 color_hovered='blue',
                 bg_color_hovered='yellow',
                 padx=5,
                 pady=0,
                 font_name='Arimo-Medium',
                 on_click=lambda: None):
        super().__init__()

        # properties
        self.text = text
        self.font = pygame.font.Font(f'font/{font_name}.ttf', 48)
        self.on_click = on_click
        self.color = color
        self.color_hovered = color_hovered
        self.bg_color = bg_color
        self.bg_color_hovered = bg_color_hovered
        self.padx = padx
        self.pady = pady

        # surface dimensions
        text_surf = self.font.render(text, True, color)
        self.surf_w = text_surf.get_width() + 2 * padx
        self.surf_h = text_surf.get_height() + 2 * pady

        # surfaces
        self.surf = self.get_surf()
        self.surf_hovered = self.get_surf_hovered()

        # image'n'rect
        self.image = self.surf.copy()
        self.rect = self.image.get_rect()

    def get_surf(self):
        self.surf = pygame.Surface((self.surf_w, self.surf_h), SRCALPHA)
        if self.bg_color is not None:
            self.surf.fill(self.bg_color)
        self.surf.blit(self.font.render(self.text, True, self.color), (self.padx, self.pady))
        return self.surf

    def get_surf_hovered(self):
        self.surf_hovered = pygame.Surface((self.surf_w, self.surf_h), SRCALPHA)
        if self.bg_color_hovered is not None:
            self.surf_hovered.fill(self.bg_color_hovered)
        self.surf_hovered.blit(self.font.render(self.text, True, self.color_hovered), (self.padx, self.pady))
        return self.surf_hovered

    def set_as_hovered(self):
        self.image = self.surf_hovered.copy()

    def set_as_default(self):
        self.image = self.surf.copy()

    def update_text(self, new_text):
        self.text = str(new_text)
        self.get_surf()
        self.get_surf_hovered()


class ButtonPentagram(Button):
    def __init__(self):
        super().__init__('6', 'red', '#1a1a1a', '#1a1a1a', 'red', font_name='SyneMono-Regular', on_click=self.increase)

    def get_value(self):
        return int(self.text)

    def increase(self):
        cur_value = int(self.text) + 1 if int(self.text) + 1 <= 9 else 0
        self.update_text(cur_value)


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
    def __init__(self,
                 text: str,
                 text_size=48,
                 color='cyan',
                 font_name='Arimo-Medium'):
        super().__init__()
        font = pygame.font.Font(f'font/{font_name}.ttf', text_size)  # convert
        self.image = font.render(text, True, color)
        self.rect = self.image.get_rect()
        self.alpha = 255


# Scene ################################################################################################################
class Scene:
    def __init__(self, channel_num=1):

        # properties
        self.bg_color = 'blue'
        self.channel_num = channel_num
        self.interactive_buttons = True

        # overlay
        self.crt_overlay = pygame.image.load('pics/border.png').convert_alpha()

        # draw group
        self.drawables = pygame.sprite.LayeredUpdates()

        # update groups
        self.buttons = pygame.sprite.Group()
        self.caption = pygame.sprite.GroupSingle()

        # states
        self.hovered = pygame.sprite.GroupSingle()

        self.draw_crt_lines()

    def add_button(self, button: Button):
        self.buttons.add(button)
        self.sprite_show(button)

    def add_caption(self, caption: Caption):
        if self.caption.sprite:
            self.caption.sprite.kill()
        self.caption.add(caption)
        self.sprite_show(caption)

    def add_sprite(self, sprite: pygame.sprite.Sprite):
        self.sprite_show(sprite)

    def check_collisions(self):
        mouse_pos = pygame.mouse.get_pos()
        for button in self.buttons:
            if button.rect.collidepoint(mouse_pos):
                if self.interactive_buttons:
                    button.set_as_hovered()
                    self.hovered.add(button)
            else:
                button.set_as_default()
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

    def clear_all(self):
        """Clear all groups"""
        self.buttons.empty()
        self.caption.empty()
        self.drawables.empty()
        self.hovered.empty()

    def cursor_by_context(self):
        if self.hovered:
            pygame.mouse.set_cursor(SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(SYSTEM_CURSOR_ARROW)

    def draw_crt_lines(self, n_lines=140, alpha=.1):
        lines_surf = pygame.Surface((screen_w, screen_h), SRCALPHA)
        for i in range(n_lines):
            y = round(screen_h / n_lines * i)
            pygame.draw.line(lines_surf, 'black', (0, y), (screen_w, y))
        lines_surf.set_alpha(round(255 * alpha))
        self.crt_overlay.blit(lines_surf, (0, 0))

    def play(self):
        pass

    def sprite_hide(self, sprite: pygame.sprite.Sprite):
        self.drawables.remove(sprite)

    def sprite_show(self, sprite: pygame.sprite.Sprite):
        self.drawables.add(sprite)

    def stop(self):
        pass

    def update(self, events: list):
        self.check_collisions()
        self.check_events(events)
        self.cursor_by_context()
        self.buttons.update()

    def update_weak(self):
        pass

    def draw(self, surface: pygame.Surface):
        surface.fill(self.bg_color)
        self.drawables.draw(surface)
        surface.blit(self.crt_overlay, (0, 0))


class NoSignal(Scene):
    """Offline"""
    def __init__(self, channel_num: int):
        super().__init__(channel_num)
        self.bg_sound = pygame.mixer.Sound('sfxs/no_signal.mp3')
        self.bg_sound.set_volume(.1)

    def stop(self):
        self.bg_sound.stop()

    def play(self):
        self.bg_sound.play(loops=-1)

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
        self.tuto = pygame.sprite.Sprite()
        self.tuto.image = pygame.image.load('pics/tuto.png').convert()
        self.tuto.rect = self.tuto.image.get_rect()
        self.drawables.add(self.tuto)


class Channel2(NoSignal):
    def __init__(self):
        super().__init__(2)


class Channel3(Scene):
    """A woman spelling the lucky numbers. Part of pentagram puzzle"""

    def __init__(self):
        super().__init__(channel_num=3)
        lucky_nums_list = list(str(game.lucky_nums))
        self.speech_list = ['the_numbers_are', *lucky_nums_list, 'repeating', *lucky_nums_list]
        self.frame = 0.00
        self.speech_speed = .01
        self.speech_sound = pygame.mixer.Sound('sfxs/1.mp3')

    def say_the_lucky_nums(self):
        if self.frame >= len(self.speech_list):
            self.frame = 0.00
        if '{:.2f}'.format(self.frame)[-2:] == '00':
            self.speech_sound = pygame.mixer.Sound(f'sfxs/{self.speech_list[int(self.frame)]}.mp3')
            self.speech_sound.play()
            caption_text = self.speech_list[int(self.frame)]
            caption_text = 'the numbers are' if caption_text == 'the_numbers_are' else caption_text
            self.add_caption(Caption(caption_text))
        self.frame = round(self.frame + self.speech_speed, 2)

    def stop(self):
        self.speech_sound.stop()

    def update_weak(self):
        if self.frame >= len(self.speech_list):
            self.frame = 0.00
        self.frame = round(self.frame + self.speech_speed, 2)
        if self.caption.sprite:
            self.caption.sprite.kill()

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

        # properties
        self.bg_color = '#1a1a1a'
        self.lines_colors = game.lucky_colors  # always 5 elements
        self.update = self.event_1

        # set positions
        p1 = (.50 * screen_w, .20 * screen_h)
        p2 = (.20 * screen_w, .40 * screen_h)
        p3 = (.80 * screen_w, .40 * screen_h)
        p4 = (.30 * screen_w, .80 * screen_h)
        p5 = (.70 * screen_w, .80 * screen_h)

        # choose a random start point
        p0 = random.choice([p1, p2, p3, p4, p5])

        # get a path based on choosed point
        path = {p1: [p1, p4, p3, p2, p5],
                p2: [p2, p5, p1, p4, p3],
                p3: [p3, p4, p1, p5, p2],
                p4: [p4, p3, p2, p5, p1],
                p5: [p5, p1, p4, p3, p2],
                }[p0]

        # set the buttons
        for i, pos in enumerate(path):
            button = ButtonPentagram()
            button.rect.center = pos
            self.add_button(button)

    def event_1(self, events: list):
        """Check if the lucky nums match and go to event 2 if it does"""
        super().update(events)
        if game.lucky_nums == int(''.join(str(button.get_value()) for button in self.buttons)):
            self.lines_colors = 5 * ['red']
            self.interactive_buttons = False
            pygame.mixer.Sound('sfxs/my_side.mp3').play()
            self.update = self.event_2

    def event_2(self, events: list):
        super().update(events)

    def draw_lines(self, surface: pygame.Surface):
        buttons = self.buttons.sprites()
        for i in range(0, len(buttons) - 1):
            start_point, end_point = buttons[i].rect.center, buttons[i + 1].rect.center
            pygame.draw.line(surface, self.lines_colors[i], start_point, end_point, 2)
        start_point, end_point = buttons[-1].rect.center, buttons[0].rect.center
        pygame.draw.line(surface, self.lines_colors[-1], start_point, end_point, 2)

    def draw(self, surface: pygame.Surface):
        surface.fill(self.bg_color)
        self.draw_lines(surface)
        self.drawables.draw(surface)
        surface.blit(self.crt_overlay, (0, 0))


class Channel7(Scene):
    """Sun channel. Part of sun and moon puzzle"""

    def __init__(self):
        super().__init__(7)
        self.bg_color = 'white'


class Channel8(Scene):
    """No signal. Part of pentagram puzzle"""

    def __init__(self):
        super().__init__(channel_num=8)
        self.bars_colors = ['white', *game.lucky_colors[:-1], 'red', game.lucky_colors[-1], '#1a1a1a']
        self.bg_sound = pygame.mixer.Sound('sfxs/no_signal.mp3')
        self.bg_sound.set_volume(.1)

    def stop(self):
        self.bg_sound.stop()

    def play(self):
        self.bg_sound.play(loops=-1)

    def draw(self, surface: pygame.Surface):
        draw_color_bars(surface, self.bars_colors)
        self.drawables.draw(surface)
        surface.blit(self.crt_overlay, (0, 0))


class Channel9(Scene):
    """Missing people channel or game credities"""

    def __init__(self):
        super().__init__(9)
        self.set_scene()

    def set_scene(self, name='Alexsander Rosante', photo_name='me'):
        self.clear_all()
        self.set_strip()
        # photo
        photo = pygame.sprite.Sprite()
        photo.image = pygame.image.load(f'pics/{photo_name}.png').convert()
        photo.image = pygame.transform.smoothscale(photo.image, 2 * [.35 * screen_h])
        photo.rect = photo.image.get_rect(midbottom=(.5 * screen_w, .6 * screen_h))
        self.add_sprite(photo)
        # name
        name = Text(name, 28, 'orange')
        name.rect.midtop = .5 * screen_w, photo.rect.bottom + 30
        self.add_sprite(name)

    def set_strip(self):
        # strip
        strip = pygame.sprite.Sprite()
        strip.image = pygame.Surface((screen_w, .15 * screen_h), SRCALPHA)
        strip.image.fill('#1a1a1a')
        strip.rect = strip.image.get_rect()
        # text
        text = Text('Missing person', 44, 'white')
        text.rect.center = .5 * screen_w, .5 * strip.rect.h
        strip.image.blit(text.image, text.rect)
        # rotate strip
        strip.image = pygame.transform.rotozoom(strip.image, 30, 1)
        strip.rect.left -= .1 * screen_w
        strip.rect.top -= .1 * screen_h
        # add to group
        self.add_sprite(strip)
        self.drawables.change_layer(strip, 1)


class Channel10(Scene):
    """Moon channel. Part of sun and moon puzzle"""

    def __init__(self):
        super().__init__(10)
        self.bg_color = '#1a1a1a'


class SceneMenu(Scene):
    def __init__(self):
        super().__init__()
        # properties
        self.on_default = True
        self.click_cooldown = 1

        # version
        self.version = Text(version, text_size=24)
        self.version.rect.bottomright = .93 * screen_w, .93 * screen_h

        self.set_to_default()

    def check_events(self, events: list):
        for event in events:
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    for button in self.buttons:
                        if button.rect.collidepoint(event.pos):
                            button.on_click()
                elif event.button == 3:
                    if self.click_cooldown:
                        self.click_cooldown -= 1
                    else:
                        if self.on_default:
                            game.menu_close()
                        else:
                            self.set_to_default()

    def set_to_quit(self):
        self.clear_all()
        text = Text('Quit the game?'.upper())
        button_yes = Button('YES', on_click=game.quit)
        button_no = Button('NO', on_click=self.set_to_default)
        text.rect.midbottom = .5 * screen_w, .5 * screen_h - 10
        button_yes.rect.topright = .5 * screen_w - 10, .5 * screen_h + 10
        button_no.rect.topleft = .5 * screen_w + 10, button_yes.rect.top
        self.add_sprite(text)
        self.add_button(button_yes)
        self.add_button(button_no)

    def set_to_default(self):
        self.clear_all()
        button_display = Button('DISPLAY')
        button_time = Button('TIME')
        button_channels = Button('CHANNELS')
        button_reset = Button('RESET GAME')
        button_quit = Button('QUIT', on_click=self.set_to_quit)
        for i, button in enumerate((button_display, button_time, button_channels, button_reset, button_quit)):
            button.rect.midleft = .1 * screen_w, (.2 + .15 * i) * screen_h
            self.add_button(button)

    def draw(self, surface: pygame.Surface):
        surface.fill(self.bg_color)
        self.drawables.draw(surface)
        surface.blit(self.version.image, self.version.rect)
        surface.blit(self.crt_overlay, (0, 0))


# Game #################################################################################################################
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((screen_w, screen_h), NOFRAME)
        pygame.display.set_caption(f'Strange Channels v{version}')
        pygame.display.set_icon(pygame.image.load('pics/icon.png').convert())
        self.clock = pygame.time.Clock()
        self.events = pygame.event.get()
        self.loop = True
        self.scene = Scene()

        self.lucky_nums = random.randint(10000, 99999)
        self.lucky_colors = ['yellow', 'cyan', 'green', 'magenta', 'blue']
        random.shuffle(self.lucky_colors)

        # channels menagement
        self.channels = {}
        self.cur_channel = 1
        self.channel_indicator = pygame.sprite.GroupSingle()

        # states
        self.is_menu_open = False

    def change_scene(self, scene: Scene, show_channel_num=True):
        self.scene = scene
        if show_channel_num:
            self.show_channel_num(self.scene.channel_num)

    def check_events(self):
        self.events = pygame.event.get()
        for event in self.events:
            if event.type == QUIT:
                self.quit()
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 3:
                    self.menu_open()

    def menu_open(self):
        if not self.is_menu_open:
            self.channel_indicator.empty()
            self.scene.stop()
            self.scene = SceneMenu()
            self.is_menu_open = True

    def menu_close(self):
        self.scene = self.channels[self.cur_channel]
        self.scene.play()
        self.is_menu_open = False

    def next_channel(self):
        if not self.is_menu_open:
            self.scene.stop()
            self.cur_channel += 1
            if self.cur_channel > len(self.channels):
                self.cur_channel = 1
            self.scene = self.channels[self.cur_channel]
            self.show_channel_num(self.scene.channel_num)
            self.scene.play()

    def previous_channel(self):
        if not self.is_menu_open:
            self.scene.stop()
            self.cur_channel -= 1
            if self.cur_channel < 1:
                self.cur_channel = len(self.channels)
            self.scene = self.channels[self.cur_channel]
            self.show_channel_num(self.scene.channel_num)
            self.scene.play()

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

    def show_channel_num(self, number: int):
        indicator = ChannelIndicator(number)
        indicator.rect.topright = .9 * screen_w, .1 * screen_h
        self.channel_indicator.add(indicator)

    def update_weak(self):
        for channel in self.channels.values():
            if channel != self.scene:
                channel.update_weak()

    def run(self):
        self.set_channels()
        while self.loop:
            self.check_events()
            self.update_weak()
            self.scene.update(self.events)
            self.channel_indicator.update()
            self.scene.draw(self.screen)
            self.channel_indicator.draw(self.screen)
            pygame.display.update()
            self.clock.tick(fps)
        pygame.quit()


# Functions ############################################################################################################

def draw_color_bars(surface: pygame.Surface,
                    colors=('white', 'yellow', 'cyan', 'green', 'magenta', 'red', 'blue', '#1a1a1a')):
    bar_w, bar_h = math.ceil(surface.get_width() / len(colors)), surface.get_height()
    for i, color in enumerate(colors):
        pygame.draw.rect(surface, color, [bar_w * i, 0, bar_w, bar_h])


def int_to_roman(num: int):
    return {1: 'I',
            2: 'II',
            3: 'III',
            4: 'IV',
            5: 'V',
            6: 'VI',
            7: 'VII',
            8: 'VIII',
            9: 'IX'
            }[num]


########################################################################################################################
if __name__ == '__main__':
    #
    with open('settings.json', 'r') as fp:
        info = json.load(fp)

    # properties
    version = info['version']
    screen_w = info['screen_w']
    screen_h = info['screen_h']
    fps = info['fps']

    game = Game()
    game.run()
