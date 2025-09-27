from mutant_maze import MutantMaze
from a_star import AStarWeightedSolver


def simulate_escape(maze_size: int = 8, wall_move_prob: float = 0.15,
                    max_steps: int = 200, show_maze: bool = True):


    print(f"=== Simulación Laberinto Mutante {maze_size}x{maze_size} ===")
    print(f"Probabilidad de movimiento de paredes: {wall_move_prob}")
    print(f"Peso A*: 1.5")

    maze = MutantMaze(maze_size, wall_move_prob, num_exits=3)
    solver = AStarWeightedSolver(weight=1.5)

    current_pos = maze.start
    total_moves = 0
    total_nodes_explored = 0
    replanning_events = 0
    false_exits = 0

    if show_maze:
        maze.print_maze(current_pos)  # Mostrar posición inicial del agente

    for step in range(max_steps):
        # El laberinto puede mutar
        if maze.mutate_walls():
            replanning_events += 1
            print(f"Step {step}: ¡Laberinto mutó! (Generación {maze.generation})")
            if show_maze:
                maze.print_maze(current_pos)

        # Cambiar el start del maze temporalmente
        original_start = maze.start
        maze.start = current_pos

        path, stats = solver.solve(maze)

        # Restaurar start original
        maze.start = original_start

        if not path or len(path) <= 1:
            print(f"Step {step}: ¡Sin camino válido desde posición actual!")
            if show_maze:
                maze.print_maze(current_pos)
            break

        total_nodes_explored += stats['nodes_explored']

        # Moverse un paso hacia el objetivo
        next_pos = path[1]
        current_pos = next_pos
        total_moves += 1

        print(f"Step {step}: Moviendo a ({current_pos.x}, {current_pos.y}) - "
              f"Nodos explorados: {stats['nodes_explored']}")

        # Mostrar maze después del movimiento
        if show_maze:
            maze.print_maze(current_pos)

        # ¿Llegamos a una salida? Verificar si es la real
        if current_pos in maze.get_all_exits():
            if maze.is_real_exit(current_pos):
                print(f"\n¡ÉXITO! Encontró la salida REAL en {step + 1} steps")
                print(f"Posición: ({current_pos.x}, {current_pos.y})")
                print(f"Movimientos totales: {total_moves}")
                print(f"Nodos explorados totales: {total_nodes_explored}")
                print(f"Replanning events: {replanning_events}")
                print(f"Salidas falsas visitadas: {false_exits}")

                if total_moves > 0:
                    efficiency = total_moves / (step + 1)
                    print(f"Eficiencia de movimiento: {efficiency:.2f}")

                return True
            else:
                false_exits += 1
                print(f"Step {step}: ¡Salida FALSA en ({current_pos.x}, {current_pos.y})! Continuando búsqueda...")

                maze.mark_exit_as_visited(current_pos)
                maze.exits = [exit_pos for exit_pos in maze.exits if exit_pos != current_pos]

                if len(maze.exits) == 0:
                    print("¡No quedan más salidas!")
                    break

    print(f"\n¡FALLO! No se pudo escapar en {max_steps} steps")
    return False