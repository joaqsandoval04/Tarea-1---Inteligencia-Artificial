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

    def create_maze(self):
        size = self._size
        self._laberinto = np.zeros((size, size), dtype=int)

        # ============== POSICIONAR AL AGENTE ==============
        if size%2 == 0:
            self._laberinto[0][self._size//2] = 2
        else:
            self._laberinto[0][(self._size + 1) // 2] = 2
        pos_agente = tuple(map(int, np.argwhere(self._laberinto == 2)[0]))

        # Posicionar la salida real en uno de los bordes
        x,y,v = random.randint(0,self._size - 1), random.randint(0,self._size - 1), random.randint(0,1)
        if x == 0 and y == pos_agente[1] - 1:
            y = y - 1
        elif x == 0 and y == pos_agente[1] + 1:
            y = y + 1
        if v == 0:
            if x <= size//2:
                x = 0
            else:
                x = size - 1
        else:
            if y <= size//2:
                y = 0
            else:
                y = size - 1
        self._laberinto[x][y] = 4

        # ============== POSICIONAR AL AGENTE ==============

        # ============== CREAR SALIDAS FALSAS ==============
        c_salidas = random.randint(0,(self._size // 2) - self._size // 4)

        bordes = ['arriba', 'abajo', 'izquierda', 'derecha']

        for i in range(c_salidas):
            borde = random.choice(bordes)

            if borde == 'arriba':
                x = 0
                y = random.randint(0, size - 1)
            elif borde == 'abajo':
                x = size - 1
                y = random.randint(0, size - 1)
            elif borde == 'izquierda':
                x = random.randint(0, size - 1)
                y = 0
            else:  # derecha
                x = random.randint(0, size - 1)
                y = size - 1

            # Solo colocar si está vacío y no colisiona con agente o salida real
            if self._laberinto[x][y] == 0:
                self._laberinto[x][y] = 3

        # ============== CREAR SALIDAS FALSAS ==============

        # ============== CREAR MUROS ==============

        vacios = list(zip(*np.where(self._laberinto == 0)))
        for i in range((size*size)//2):
            if vacios:
                vacio = random.choice(vacios)
                new = self._laberinto.copy()
                new[vacio] = 1

                # Validar
                if self.is_a_path(new):
                    self._laberinto = new
            vacios = list(zip(*np.where(self._laberinto == 0)))

        # ============== CREAR MUROS ==============

    def create_maze_file(self, file):
        self._laberinto = np.loadtxt(file, dtype=int)

    # Devuelve True si el nuevo laberinto es posible y se actualiza, de lo contrario retorna False
    def update_maze(self):
        muros = list(zip(*np.where(self._laberinto == 1)))
        vacios = list(zip(*np.where(self._laberinto == 0)))
        # Si por alguna razón todo el laberinto está lleno o vacío
        if not vacios or not muros:
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

        # Metemos la posición del agente en queue

        # Así compararemos si la posición es igual o no a la salida
        queue = deque([pos_agente])
        # Posibles direcciones que el agente puede tomar
        direcciones = [(1,0), (-1,0), (0,1), (0,-1)]
        # Reiteramos hasta encontrar la salida, o hasta corroborar que no hay camino existente

        # Mientras la queue no esté vacía...
        while queue:
            x, y = queue.popleft()
            # Sacamos la posición del agente y la asignamos a (x,y)
            if (x,y) == pos_salida:
                return True
            for dx, dy in direcciones:
                nx, ny = x + dx, y +dy # Sea x,y = 0,5; nx,ny será la nueva posición a evaluar
                if 0 <= nx < filas and 0 <= ny < cols:
                    if not visitado[nx, ny] and laberinto[nx, ny] != 1:
                        visitado[nx,ny] = 1
                        queue.append((nx,ny))
        return False

    def get_laberinto(self):
        return self._laberinto

    def get_size(self):
        return self._size