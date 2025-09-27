import random
import pygame
import sys
import maze_generator
from maze_generator import MazeGenerator

# Crear pantalla
pygame.init()

BLACK = (0,0,0)
WHITE = (255,255,255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0,0,255)

SIZE = (800,800)

def main():
    laberinto = MazeGenerator(50)
    #laberinto.create_maze_file("laberinto10x10.txt")
    laberinto.create_maze()

    tamaño_laberinto = laberinto.get_size()
    tamaño_pixeles = int(SIZE[1])/tamaño_laberinto
    print(tamaño_pixeles)

    ### -- Control de tiempo
    clock = pygame.time.Clock()
    time_update_maze = pygame.time.get_ticks()

    print(laberinto.is_a_path(laberinto.get_laberinto()))

    screen = pygame.display.set_mode(SIZE)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        now = pygame.time.get_ticks()
        ### -- Actualizar laberinto
        if now - time_update_maze >= 5000:
            laberinto.update_maze()
            time_update_maze = now
            print("Maze updated")

        ### -- Zona de dibujo
        screen.fill(WHITE)
        for i in range(len(laberinto.get_laberinto())):
            for j in range(len(laberinto.get_laberinto()[i])):
                if laberinto.get_laberinto()[i][j] == 0:
                    pygame.draw.rect(screen, WHITE, (tamaño_pixeles*j, tamaño_pixeles*i, tamaño_pixeles, tamaño_pixeles))
                elif laberinto.get_laberinto()[i][j] == 1:
                    pygame.draw.rect(screen, BLACK, (tamaño_pixeles*j, tamaño_pixeles*i, tamaño_pixeles, tamaño_pixeles))
                elif laberinto.get_laberinto()[i][j] == 2:
                    pygame.draw.rect(screen, GREEN, (tamaño_pixeles*j, tamaño_pixeles*i, tamaño_pixeles, tamaño_pixeles))
                elif laberinto.get_laberinto()[i][j] == 3:
                    pygame.draw.rect(screen, RED, (tamaño_pixeles*j, tamaño_pixeles*i, tamaño_pixeles, tamaño_pixeles))
                elif laberinto.get_laberinto()[i][j] == 4:
                    pygame.draw.rect(screen, BLUE, (tamaño_pixeles*j, tamaño_pixeles*i, tamaño_pixeles, tamaño_pixeles))

        ### -- Zona de dibujo
        # Actualizar pantalla
        pygame.display.flip()

main()