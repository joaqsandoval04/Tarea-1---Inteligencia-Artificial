import numpy as np
import random
from collections import deque


# 0 = Vacío
# 1 = Muralla
# 2 = Agente
# 3 = Salidas falsas
# 4 = Salida real

class MazeGenerator:
    def __init__(self, size: int):
        self._size = size
        self._laberinto = np.zeros((size,size), dtype = int)

    def create_maze(self, file):
        self._laberinto = np.loadtxt(file, dtype=int)

    # Devuelve True si el nuevo laberinto es posible y se actualiza, de lo contrario retorna False
    def update_maze(self):
        muros = list(zip(*np.where(self._laberinto == 1)))
        vacios = list(zip(*np.where(self._laberinto == 0)))

        # Si por alguna razón todo el laberinto está lleno
        if not vacios:
            return False

        # Elegir muro y vacio aleatorio
        muro = random.choice(muros)
        vacio = random.choice(vacios)

        for i in range(100):
            # Intercambiar posiciones
            new = self._laberinto.copy()
            new[muro] = 0
            new[vacio] = 1

            # Validar
            if self.is_a_path(new):
                self._laberinto = new
                return True



    def is_a_path(self, laberinto):
        filas, cols = laberinto.shape
        visitado = np.zeros_like(laberinto, dtype=bool)
        # Definimos posición del agente actual y la salida real
        pos_agente = tuple(map(int, np.argwhere(laberinto == 2)[0]))
        pos_salida = tuple(map(int, np.argwhere(laberinto == 4)[0]))
        # Metemos la posición  del agente en queue
        # Así compararemos si la posición es igual o no a la salida
        queue = deque([pos_agente])

        # Posibles direcciones que el agente puede tomas
        direcciones = [(1,0), (-1,0), (0,1), (0,-1)]

        # Reiteramos hasta encontrar la salida, o hasta corroborar que no hay camino existente
        # Mientras la queue no esté vacía...
        while queue:
            x, y = queue.popleft() # Sacamos la posición del agente y la asignamos a (x,y)
            if (x,y) == pos_salida:
                return True
            for dx, dy in direcciones:
                nx, ny = x + dx, y +dy  # Sea x,y = 0,5; nx,ny será la nueva posición a evaluar
                if 0 <= nx < filas and 0 <= ny < cols:
                    if not visitado[nx, ny] and laberinto[nx, ny] != 1:
                        visitado[nx,ny] = 1
                        queue.append((nx,ny))
        return False

    def get_laberinto(self):
        return self._laberinto

    def get_size(self):
        return self._size