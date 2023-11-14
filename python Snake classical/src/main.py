import pygame

pygame.init()
SIZE = W, H = 500, 500
WHITE = 255, 255, 255
BLACK = 0, 0, 0
screen = pygame.display.set_mode(SIZE)
clock = pygame.time.Clock()

screen.fill(WHITE)
for i in range(0, W, 10):
    pygame.draw.line(screen, BLACK, (i, 0), (H, 0))
pygame.display.flip()

running = True

while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False





