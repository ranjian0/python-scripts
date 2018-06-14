import pygame
from PIL import Image
from io import BytesIO

surf = pygame.Surface((100,200))
surf.fill((100, 100, 100))

data = pygame.image.tostring(surf, 'RGBA')
img = Image.frombytes('RGBA', (100,200), data)

zdata = BytesIO()
img.save(zdata, 'PNG')

img = zdata.getvalue()
_file = open("image.png", 'wb')
_file.write(img)
