import random
import pygame
import os
import sys
import time


# функция для загрузки изображений
def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


# функция для удобного вывода текста на экран
def print_text(screen, message="", x=0, y=0, font_color='black', font_size=30, frame_color=None, frame_indent=0, frame_width=1):
    font_type = pygame.font.Font(None, font_size)
    text = font_type.render(message, True, font_color)
    screen.blit(text, (x, y))
    if frame_color:
        pygame.draw.rect(screen, frame_color, (
            x - frame_indent, y - frame_indent, text.get_rect()[2] + frame_indent * 2,
            text.get_rect()[3] + frame_indent * 2), frame_width)
    screen.blit(text, (x, y))
    return (x - frame_indent, y - frame_indent, text.get_rect()[2] + frame_indent * 2 + x,
            text.get_rect()[3] + frame_indent * 2 + y)