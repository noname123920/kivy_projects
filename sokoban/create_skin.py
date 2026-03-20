import pygame

pygame.init()
size = 32
skin = pygame.Surface((size * 4, size * 4))

# Цвета
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
BROWN = (139, 69, 19)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GOLD = (255, 215, 0)
BLACK = (0, 0, 0)

# Заливаем фон
skin.fill(WHITE)

# Рисуем сетку
for x in range(4):
    for y in range(4):
        pygame.draw.rect(skin, GRAY, (x*size, y*size, size, size))
        pygame.draw.rect(skin, DARK_GRAY, (x*size, y*size, size, size), 1)

# Стена (0,2)
pygame.draw.rect(skin, BROWN, (0, 2*size, size, size))
for k in range(3):
    pygame.draw.rect(skin, (100, 50, 10), (k*10 + 5, 2*size + 10, 8, 5))
    pygame.draw.rect(skin, (100, 50, 10), (k*10 + 5, 2*size + 20, 8, 5))

# Игрок (1,0)
pygame.draw.circle(skin, BLUE, (size + size//2, size//2), size//3)
pygame.draw.circle(skin, WHITE, (size + size//2 - 4, size//2 - 3), 3)
pygame.draw.circle(skin, WHITE, (size + size//2 + 4, size//2 - 3), 3)
pygame.draw.circle(skin, BLACK, (size + size//2 - 4, size//2 - 3), 1)
pygame.draw.circle(skin, BLACK, (size + size//2 + 4, size//2 - 3), 1)

# Ящик (2,0)
pygame.draw.rect(skin, BROWN, (2*size, 0, size, size))
pygame.draw.rect(skin, BLACK, (2*size, 0, size, size), 2)
pygame.draw.line(skin, BLACK, (2*size + size//4, size//2), (2*size + 3*size//4, size//2), 2)
pygame.draw.line(skin, BLACK, (2*size + size//2, size//4), (2*size + size//2, 3*size//4), 2)

# Цель (0,1)
pygame.draw.circle(skin, RED, (size//2, size + size//2), size//5)
pygame.draw.circle(skin, WHITE, (size//2, size + size//2), size//8)

# Игрок на цели (1,1)
pygame.draw.circle(skin, GREEN, (size + size//2, size + size//2), size//3)
pygame.draw.circle(skin, BLUE, (size + size//2, size + size//2), size//4)

# Ящик на цели (2,1)
pygame.draw.rect(skin, GOLD, (2*size, size, size, size))
pygame.draw.rect(skin, BLACK, (2*size, size, size, size), 2)
pygame.draw.circle(skin, RED, (2*size + size//2, size + size//2), size//6)

pygame.image.save(skin, 'borgar.png')
print("Файл borgar.png создан!")