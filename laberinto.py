import pygame
import sys
from maze_generator import MazeGenerator
from a_star import AStar
from algoritmo_genetico import GeneticAlgorithm
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
ORANGE = (255, 165, 0)

SIZE = (800, 800)

# Recalcula el camino desde la posición actual del agente
def recalcular_camino(laberinto: MazeGenerator, solver, agente_pos, salidas_visitadas, algorithm_type="astar"):
    if agente_pos is None:
        agente_pos = laberinto.get_agent_pos()
    lab = copy.deepcopy(laberinto)

    lab.set_agent_pos(agente_pos)

    # "Bloquear" temporalmente las salidas (falsas) ya visitadas, para evitar que no intente ir a ellas de nuevo
    # Las salidas (3) pasan a ser un muro (1)
    for salida in salidas_visitadas:
        if lab.get_obj_in_pos(salida) == 3:
            lab.set_obj_in_pos(salida, 0)

    # Ejecutar el algoritmo correspondiente
    if algorithm_type == "astar":
        caminos, exito = solver.solve(lab)
    else:  # genetico
        caminos, exito = solver.solve(lab, population_size=10, generations=2)

    # Restaurar valores de las salidas
    for salida in salidas_visitadas:
        lab.set_obj_in_pos(salida, 3)

    # Si encuentra un camino válido
    if exito and caminos:
        return caminos[0] if caminos[0] else [], agente_pos, True
    else:
        return [], agente_pos, False

def main():
    laberinto = MazeGenerator(20)
    laberinto.create_maze()

    tamaño_laberinto = laberinto.get_size()
    tamaño_pixeles = int(SIZE[1]) / tamaño_laberinto

    # Control de tiempo
    clock = pygame.time.Clock()
    time_update_maze = pygame.time.get_ticks()
    time_move_agent = pygame.time.get_ticks()

    # Solvers Setup
    astar_solver = AStar()
    genetic_solver = GeneticAlgorithm(max_movimientos=100)

    current_solver = None
    algorithm_type = None
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
                # Tecla A para A*
                if event.key == pygame.K_a:
                    auto_solving = True
                    current_solver = astar_solver
                    algorithm_type = "astar"
                    agente_pos = laberinto.get_agent_pos()
                    salidas_visitadas = set()
                    path_index = 0
                    movimiento_agente = False

                    camino_actual, agente_pos, exito = recalcular_camino( laberinto, current_solver, agente_pos, salidas_visitadas, algorithm_type)
                    if exito:
                        movimiento_agente = True

                # Tecla G para Genético
                elif event.key == pygame.K_g:
                    auto_solving = True
                    current_solver = genetic_solver
                    algorithm_type = "genetic"
                    agente_pos = laberinto.get_agent_pos()
                    salidas_visitadas = set()
                    path_index = 0
                    movimiento_agente = False

                    camino_actual, agente_pos, exito = recalcular_camino( laberinto, current_solver, agente_pos, salidas_visitadas, algorithm_type)
                    if exito:
                        movimiento_agente = True

                # Tecla R para reiniciar
                elif event.key == pygame.K_r:
                    laberinto.create_maze()
                    auto_solving = False
                    current_solver = None
                    algorithm_type = None
                    agente_pos = None
                    salidas_visitadas = set()
                    camino_actual = []
                    path_index = 0
                    movimiento_agente = False
                    agent_moving_img = pygame.transform.scale( pygame.image.load("resources/Hornet.webp"), (int(tamaño_pixeles), int(tamaño_pixeles)))

        now = pygame.time.get_ticks()

        # Actualizar laberinto (mutar) cada 5 segundos
        if now - time_update_maze >= 5000:
            if laberinto.update_maze():
                time_update_maze = now
                print("Laberinto mutó")

                # Si se está resolviendo automáticamente, recalcular el camino
                if auto_solving and current_solver:
                    path_index = 0
                    camino_actual, agente_pos, exito = recalcular_camino( laberinto, current_solver, agente_pos, salidas_visitadas, algorithm_type)
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
                            camino_actual, agente_pos, exito = recalcular_camino( laberinto, current_solver, agente_pos, salidas_visitadas, algorithm_type)
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
                pygame.draw.rect(screen, (128, 128, 128), (tamaño_pixeles * j, tamaño_pixeles * i, tamaño_pixeles, tamaño_pixeles), 1)

        # Mostrar instrucciones
        font = pygame.font.Font(None, 28)
        instructions = ["A: Weighted A*", "G: Algoritmo Genetico", "R: Reiniciar laberinto"]

        for idx, instruction in enumerate(instructions):
            text = font.render(instruction, True, PURPLE)
            screen.blit(text, (10, 10 + idx * 30))

        # Mostrar estado del juego
        if auto_solving:
            status = "Resolviendo..." if movimiento_agente else "Calculando..."
            status_text = font.render(status, True, PURPLE)
            screen.blit(status_text, (10, 130))

            # Mostrar contador de salidas falsas encontradas
            if salidas_visitadas:
                exits_text = font.render(f"Salidas falsas: {len(salidas_visitadas)}", True, PURPLE)
                screen.blit(exits_text, (10, 90))
        # Actualizar pantalla
        pygame.display.flip()
        clock.tick(60)  # 60 FPS


if __name__ == "__main__":
    main()