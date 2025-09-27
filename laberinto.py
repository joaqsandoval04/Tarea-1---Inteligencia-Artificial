import random
import pygame
import sys

# Empezamos creando un laberinto 10x10
# 0 = Vacío
# 1 = Muralla
# 2 = Agente
# 3 = Salidas falsas
# 4 = Salida real
laberinto = [
[0,0,0,0,2,1,1,1,1,0],
[0,1,0,1,0,0,0,0,0,0],
[1,1,0,1,0,1,1,1,1,1],
[0,1,1,1,0,1,0,0,0,0],
[0,0,0,0,0,1,1,0,1,0],
[1,1,0,0,0,0,1,0,1,0],
[0,1,1,0,1,0,0,0,1,0],
[0,1,0,0,1,0,1,0,1,0],
[1,1,0,1,1,1,1,1,1,0],
[3,0,0,1,4,0,0,0,0,0]]

# Crear pantalla
pygame.init()

BLACK = (0,0,0)
WHITE = (255,255,255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0,0,255)

SIZE = (800,800)

def main():
    tamaño_laberinto = int(input("Ingresa el tamaño del laberinto, debe ser un numero natural:\n"))
    tamaño_pixeles = int(SIZE[1])/tamaño_laberinto
    print(tamaño_pixeles)
    screen = pygame.display.set_mode(SIZE)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        screen.fill(WHITE)
        ### -- Zona de dibujo
        for i in range(len(laberinto)):
            for j in range(len(laberinto[i])):
                if laberinto[i][j] == 0:
                    pygame.draw.rect(screen, WHITE, (tamaño_pixeles*j, tamaño_pixeles*i, tamaño_pixeles, tamaño_pixeles))
                elif laberinto[i][j] == 1:
                    pygame.draw.rect(screen, BLACK, (tamaño_pixeles*j, tamaño_pixeles*i, tamaño_pixeles, tamaño_pixeles))
                elif laberinto[i][j] == 2:
                    pygame.draw.rect(screen, GREEN, (tamaño_pixeles*j, tamaño_pixeles*i, tamaño_pixeles, tamaño_pixeles))
                elif laberinto[i][j] == 3:
                    pygame.draw.rect(screen, RED, (tamaño_pixeles*j, tamaño_pixeles*i, tamaño_pixeles, tamaño_pixeles))
                elif laberinto[i][j] == 4:
                    pygame.draw.rect(screen, BLUE, (tamaño_pixeles*j, tamaño_pixeles*i, tamaño_pixeles, tamaño_pixeles))



        ### -- Zona de dibujo
        # Actualizar pantalla
        pygame.display.flip()

main()