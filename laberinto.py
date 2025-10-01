import pygame
import sys
from maze_generator import MazeGenerator
from a_star import AStar
import numpy as np
import copy

# Crear pantalla
pygame.init()

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)

SIZE = (800, 800)

# Recalcula el camino desde la posición actual del agente
# (Se usa cuando el laberinto muta o llega a una salida falsa)
def recalcular_camino(laberinto: MazeGenerator, solver, agente_pos, salidas_visitadas):
    if agente_pos is None:
        agente_pos = laberinto.get_agent_pos()
    lab = copy.deepcopy(laberinto)

    # Crear copia del laberinto para no modificar el original
    #laberinto = laberinto.get_laberinto().copy()
    
    # Mover al agente de la posicion inicial a su nueva posicion
    #pos_inicial = laberinto.get_initial_pos()
    #pos_inicial = list(zip(*np.where(laberinto == 2)))[0]
    lab.set_agent_pos(agente_pos)
    #laberinto[pos_inicial] = 0
    #laberinto[agente_pos] = 2

    # "Bloquear" temporalmente las salidas (falsas) ya visitadas, para evitar que no intente ir a ellas de nuevo
    # Las salidas (3) pasan a ser un muro (1)
    print(f"SALIDAS VISITADAS = ")
    for salida in salidas_visitadas:
        print(f"{salida}")
        if lab.get_obj_in_pos(salida) == 3:
            lab.set_obj_in_pos(salida, 0)
        """
        if laberinto[salida] == 3:
            laberinto[salida] = 0
        """

    # Ejecutar A* desde la posición actual
    print(lab)
    caminos, exito = solver.solve(lab)    # Necesita objeto laberinto

    # Restaurar valores las salidas
    for salida in salidas_visitadas:
        lab.set_obj_in_pos(salida, 3)
        #laberinto[salida] = 3
    #print(f"Posición agente = {laberinto.get_agent_pos()}")
    # Si encuentra un camino valido
    if exito and caminos:
        return caminos[0], agente_pos, True  # camino, posicion, exito
    else:
        return [], agente_pos, False

def main():
    laberinto = MazeGenerator(10)
    laberinto.create_maze()

    tamaño_laberinto = laberinto.get_size()
    tamaño_pixeles = int(SIZE[1]) / tamaño_laberinto

    # Control de tiempo
    clock = pygame.time.Clock()
    time_update_maze = pygame.time.get_ticks()
    time_move_agent = pygame.time.get_ticks()

    # A* Setup
    solver = AStar()
    camino_actual = []
    path_index = 0
    movimiento_agente = False
    agente_pos = None
    auto_solving = False
    salidas_visitadas = set()

    screen = pygame.display.set_mode(SIZE)
    agent_moving_img = pygame.image.load("resources/Hornet.webp")
    agent_moving_img = pygame.transform.scale(agent_moving_img, (int(tamaño_pixeles), int(tamaño_pixeles)))


    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    auto_solving = True
                    agente_pos = laberinto.get_agent_pos()
                    salidas_visitadas = set()
                    path_index = 0
                    movimiento_agente = False

                    camino_actual, agente_pos, exito = recalcular_camino(laberinto, solver, agente_pos, salidas_visitadas)
                    if exito:
                        movimiento_agente = True
                elif event.key == pygame.K_r:
                    laberinto.create_maze()
                    auto_solving = False
                    agente_pos = None
                    salidas_visitadas = set()
                    camino_actual = []
                    path_index = 0
                    movimiento_agente = False
                    agent_moving_img = pygame.transform.scale(pygame.image.load("resources/Hornet.webp"),
                                                              (int(tamaño_pixeles), int(tamaño_pixeles)))

        now = pygame.time.get_ticks()

        ### -- Actualizar laberinto (mutar) cada 5 segundos
        if now - time_update_maze >= 5000:
            if laberinto.update_maze():
                time_update_maze = now
                print("Laberinto mutó")

                # Si se está resolviendo automáticamente, recalcular el camino
                if auto_solving:
                    path_index = 0
                    camino_actual, agente_pos, exito = recalcular_camino(laberinto, solver, agente_pos, salidas_visitadas)
                    #print("MURO ACTUALIZADO, RECALCULANDO CAMINO ACTUAL\n")
                    #print(f"camino_actual = {camino_actual}, Agente_pos = {agente_pos}, exito = {exito}")
                    if exito:
                        movimiento_agente = True
                        time_move_agent = now

        # Mover al agente por el camino
        if movimiento_agente and camino_actual and now - time_move_agent >= 200:
            if path_index < len(camino_actual):
                agente_pos = camino_actual[path_index]
                path_index += 1
                time_move_agent = now

                # Verifica si el camino se acabó
                if path_index >= len(camino_actual):
                    movimiento_agente = False

                    # Verifica si la salida es real (4) o falsa (3)
                    maze_data = laberinto.get_laberinto()
                    if agente_pos and maze_data[agente_pos] in [3, 4]:
                        if maze_data[agente_pos] == 4:
                            print("Agente llegó a la salida real")
                            auto_solving = False
                        else:
                            print("Salida falsa, buscando siguiente salida...")
                            salidas_visitadas.add(agente_pos)
                            path_index = 0

                            # Recalcular desde esta posición
                            camino_actual, agente_pos, exito = recalcular_camino( laberinto, solver, agente_pos, salidas_visitadas)
                            if exito:
                                movimiento_agente = True
                                time_move_agent = now
                            else:
                                print("No hay más caminos disponibles")
                                auto_solving = False

        # Zona de dibujo
        screen.fill(WHITE)
        maze_data = laberinto.get_laberinto()

        # Dibujar cada celda del laberinto
        for i in range(len(maze_data)):
            for j in range(len(maze_data[i])):
                color = WHITE

                # Asignar color según el tipo de celda
                if maze_data[i][j] == 0:
                    color = WHITE   # vacío
                elif maze_data[i][j] == 1:
                    color = BLACK   # muro
                elif maze_data[i][j] == 2:
                    color = GREEN  # posicion original del agente
                elif maze_data[i][j] == 3:
                    if (i, j) in salidas_visitadas:
                        color = (100, 0, 0)  # Rojo más oscuro para las salidas falsas visitadas
                    else:
                        color = RED  # Salidas falsas
                elif maze_data[i][j] == 4:
                    color = BLUE  # Salida real

                # Mostrar camino planeado en amarillo
                if camino_actual and (i, j) in camino_actual and maze_data[i][j] == 0:
                    color = YELLOW

                # Mostrar agente en movimiento
                if agente_pos and (i, j) == agente_pos:
                    screen.blit(agent_moving_img, (tamaño_pixeles * j, tamaño_pixeles * i))
                    continue
                pygame.draw.rect(screen, color, (tamaño_pixeles * j, tamaño_pixeles * i, tamaño_pixeles, tamaño_pixeles))

                # Borde para las celdas
                pygame.draw.rect(screen, (128, 128, 128), (tamaño_pixeles * j, tamaño_pixeles * i, tamaño_pixeles, tamaño_pixeles), 1)

        # Mostrar instrucciones y estado
        font = pygame.font.Font(None, 36)
        text = font.render("ESPACIO: Resolver laberinto", True, PURPLE)
        screen.blit(text, (10, 10))

        # Mostrar estado del juego
        if auto_solving:
            status = "Resolviendo..." if movimiento_agente else "Calculando..."
            status_text = font.render(status, True, PURPLE)
            screen.blit(status_text, (10, 50))

            # Mostrar contador de salidas falsas encontradas
            if salidas_visitadas:
                exits_text = font.render(f"Salidas falsas: {len(salidas_visitadas)}", True, PURPLE)
                screen.blit(exits_text, (10, 90))
        # Actualizar pantalla
        pygame.display.flip()
        clock.tick(60)  # 60 FPS


if __name__ == "__main__":
    main()