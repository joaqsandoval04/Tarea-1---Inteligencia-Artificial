import random
import numpy as np
from deap import base, creator, tools
import time

from maze_generator import MazeGenerator


class GeneticAlgorithm:
    def __init__(self, max_movimientos=50):
        self.max_movimientos = max_movimientos
        self.nodos_explorados = 0

        # Movimientos que puede hacer: arriba, abajo, izquierda, derecha
        self.movimientos = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def encontrar_entrada(self, laberinto: MazeGenerator):
        return laberinto.get_agent_pos()
        #individuo_pos = np.where(laberinto == 2)
        #return (individuo_pos[0][0], individuo_pos[1][0])

    # Busca todas las salidas en la grilla  
    def encontrar_salidas(self, laberinto: MazeGenerator):
        return laberinto.get_exits_pos()
        #salidas = list(zip(*np.where(laberinto == 3))) + list(zip(*np.where(laberinto == 4)))
        #return salidas

    # Evalúa una secuencia de movimientos hacia una salida en específico
    def evaluar(self, individuo, laberinto: MazeGenerator, posicion_inicial, salida):
        grid = laberinto.get_laberinto()
        posicion_actual = posicion_inicial
        visitado = {posicion_actual}
        num_movimientos = 0
        colisiones_muros = 0
        posiciones_repetidas = 0

        for movimiento_idx in individuo:
            movimiento = self.movimientos[movimiento_idx]
            new_pos = (posicion_actual[0] + movimiento[0], posicion_actual[1] + movimiento[1])

            # Verificar límites del laberinto
            if not (0 <= new_pos[0] < grid.shape[0] and 0 <= new_pos[1] < grid.shape[1]):
                colisiones_muros += 1
                continue

            # Verificar colisión con una pared
            if grid[new_pos] == 1:
                colisiones_muros += 1
                continue

            # Movimiento válido
            posicion_actual = new_pos
            num_movimientos += 1

            # Penalizar posiciones repetidas (ciclos)
            if posicion_actual in visitado:
                posiciones_repetidas += 1
            visitado.add(posicion_actual)

            # Si llegó a la salida objetivo
            if posicion_actual == salida:
                # Fitness que penaliza por pasos innecesarios
                fitness = 1000000 - (num_movimientos * 100)
                return (fitness,)

        # No llega a la salida, fitness basado en distancia euclidiana
        distancia = ((posicion_actual[0] - salida[0]) ** 2 + (posicion_actual[1] - salida[1]) ** 2) ** 0.5

        # Fitness
        fitness = (
                10000 / (distancia + 1) # Base inversamente proporsional a la distancia
                + len(visitado) * 0.2 # Beneficio por casillas distintas visitadas
                + num_movimientos * 0.5  # Beneficio por moverse
                - colisiones_muros * 50  # Penalizar choques
                - posiciones_repetidas * 10 # Penalizar ciclos
        )
        return (max(0, fitness),)

    def reconstruir_camino(self, individuo, laberinto: MazeGenerator, posicion_inicial):
        grid = laberinto.get_laberinto()
        posicion_actual = posicion_inicial
        path = [posicion_actual]

        for movimiento_idx in individuo:
            movimiento = self.movimientos[movimiento_idx]
            new_pos = (posicion_actual[0] + movimiento[0], posicion_actual[1] + movimiento[1])

            # Verificar límites y paredes
            if not (0 <= new_pos[0] < grid.shape[0] and 0 <= new_pos[1] < grid.shape[1]) or grid[new_pos] == 1:
                continue

            posicion_actual = new_pos
            path.append(posicion_actual)

            # Si llega a alguna salida (real o falsa)
            if grid[posicion_actual] in [3, 4]:
                break
        return path

    def solve(self, laberinto: MazeGenerator, population_size=30, generations=20):
        posicion_actual = self.encontrar_entrada(laberinto)
        salidas_visitadas = set()
        all_caminos = []
        nodos_total = 0

        while True:
            # Encontrar salidas disponibles
            all_salidas = self.encontrar_salidas(laberinto)
            salidas_disponibles = []
            for s in all_salidas:
                if s not in salidas_visitadas:
                    salidas_disponibles.append(s)

            # Buscar la salida más cercana como objetivo
            distancia_minima = float('inf')
            salida_objetivo = None
            for salida in salidas_disponibles:
                distancia = ((salida[0] - posicion_actual[0]) ** 2 + (salida[1] - posicion_actual[1]) ** 2) ** 0.5
                if distancia < distancia_minima:
                    distancia_minima = distancia
                    salida_objetivo = salida

            # Resetear contador de nodos para esta iteración
            self.nodos_explorados = 0

            # ===== DEAP =====
            # Eliminar clases si ya estan creadas, evita errores
            if hasattr(creator, "Fitness"):
                del creator.Fitness
            if hasattr(creator, "individuo"):
                del creator.individuo

            # Definir clases
            creator.create("Fitness", base.Fitness, weights=(1.0,))
            creator.create("individuo", list, fitness=creator.Fitness)

            toolbox = base.Toolbox()

            # Definir genes y estructura
            toolbox.register("attr_movimiento", random.randint, 0, len(self.movimientos) - 1)   # Valor random que se usa en movimientos[]
            toolbox.register("individuo", tools.initRepeat, creator.individuo, toolbox.attr_movimiento, n=self.max_movimientos) # Crea un individuo cierta cantidad de veces
            toolbox.register("population", tools.initRepeat, list, toolbox.individuo)   # Crea una lista de individuos

            # Operadores genéticos
            toolbox.register("evaluate", lambda ind: self.evaluar(ind, laberinto, posicion_actual, salida_objetivo))    # Toma un individuo y lo evalua
            toolbox.register("mate", tools.cxTwoPoint)  # Cruce
            toolbox.register("mutate", tools.mutUniformInt, low=0, up=len(self.movimientos) - 1, indpb=0.15)    # Mutación
            toolbox.register("select", tools.selTournament, tournsize=3)    # Selecciona los mejores individuos de 3 competidores al azar

            # Población inicial
            population = toolbox.population(n=population_size)

            camino_encontrado = None
            salida_encontrada = None

            # === Ciclo evolutivo ===
            for gen in range(generations):
                self.nodos_explorados += len(population)

                # Evaluar todos los individuos de la población
                fitnesses = list(map(toolbox.evaluate, population))
                for ind, fit in zip(population, fitnesses):
                    ind.fitness.values = fit

                # Mejor individuo de esta generación
                mejor_ind = tools.selBest(population, 1)[0]
                best_path = self.reconstruir_camino(mejor_ind, laberinto, posicion_actual)

                # Verificar si llegó a la salida objetivo
                if best_path and best_path[-1] == salida_objetivo:
                    camino_encontrado = best_path
                    salida_encontrada = salida_objetivo
                    break

                # Selección y reproducción
                offspring = toolbox.select(population, len(population))
                offspring = list(map(toolbox.clone, offspring))

                # Cruce
                for child1, child2 in zip(offspring[::2], offspring[1::2]):
                    if random.random() < 0.7:
                        toolbox.mate(child1, child2)
                        del child1.fitness.values
                        del child2.fitness.values

                # Mutación
                for mutant in offspring:
                    if random.random() < 0.2:
                        toolbox.mutate(mutant)
                        del mutant.fitness.values

                # Mantener al mejor individuo de la generacion
                mejor_previo = tools.selBest(population, 1)[0]
                offspring = [mejor_previo] + offspring[:-1]

                # Nueva generación
                population[:] = offspring

            # Si no encontró camino completo, usar el mejor intento
            if camino_encontrado is None:
                mejor_ind = tools.selBest(population, 1)[0]
                camino_encontrado = self.reconstruir_camino(mejor_ind, laberinto, posicion_actual)
                if camino_encontrado:
                    salida_encontrada = camino_encontrado[-1]

            # Agregar este camino
            all_caminos.append(camino_encontrado)
            nodos_total += self.nodos_explorados
            salidas_visitadas.add(salida_encontrada)
            # Verifica la salida si es real (4) o falsa (3)
            if laberinto.get_laberinto()[salida_encontrada[0], salida_encontrada[1]] == 4:
                self.nodos_explorados = nodos_total
                return all_caminos, True
            else:
                posicion_actual = salida_encontrada

if __name__ == "__main__":
    # Laberinto de ejemplo (5x5)
    # 0 = vacío, 1 = muro, 2 = agente, 3 = salida falsa, 4 = salida real

    size = 10
    laberinto = MazeGenerator(size)
    laberinto = laberinto.get_laberinto()
    """
    laberinto = np.array([
        [1, 1, 1, 1, 1],
        [1, 2, 0, 1, 1],
        [1, 0, 1, 0, 1],
        [1, 0, 0, 4, 1],
        [1, 1, 1, 1, 1]
    ])
    """

    ga = GeneticAlgorithm(max_movimientos=20)
    caminos, exito = ga.solve(laberinto, population_size=30, generations=20)
    print("¿Encontró salida real?", exito)
    for i, camino in enumerate(caminos):
        print(f"Camino {i + 1}: {[(int(x), int(y)) for x, y in camino]}")