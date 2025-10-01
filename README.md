# Tarea-1---Inteligencia-Artificial
Escape del Laberinto Mutante
## Configuración del proyecto

Sigue estos pasos para configurar y ejecutar la aplicación:

### 1. Clonar el repositorio
```bash
git clone https://github.com/joaqsandoval04/Tarea-1---Inteligencia-Artificial
```

### 2. Crear y activar un entorno virtual
```bash
python -m venv venv
.\venv\Scripts\Activate  # En Windows
# source venv/bin/activate  # En Linux/Mac
```

### 3. Instalar dependencias
Instala las dependencias listadas en `requirements.txt`:
```bash
pip install -r requirements.txt
```


### 4. Ejecutar la aplicación
Inicia la aplicación con:
```bash
python laberinto.py
```
Luego de eso, puedes usar los siguientes botones del teclado:
- A - Para usar el algoritmo de búsqueda `Weighted A*`
- G - Para usar el `algoritmo genético (cromosomas)`
- R - Para reiniciar el laberinto

## Políticas de Comportamiento
- El agente puede desplazarse en 8 direcciones (incluyendo diagonales).
- El camino se recalcula cuando el laberinto muta o cuando se alcanza una salida falsa.
- Las salidas falsas ya visitadas son marcadas y excluidas de búsquedas posteriores.
- El agente desconoce cuál es la salida verdadera; debe explorar hasta encontrarla.
- El agente siempre inicia en una posición predeterminada del laberinto.
## Representación Visual
La interfaz gráfica utiliza el siguiente código de colores:
- Verde: Posición inicial del agente
- Rojo: Salidas falsas
- Azul: Salida real (solo visible para el usuario)
- Negro: Muros
- Blanco: Camino transitable
## Notas adicionales
- **Entorno virtual**: Siempre activa el entorno virtual (`.\venv\Scripts\Activate`) antes de ejecutar `python laberinto.py`.
- Para cambiar el tamaño del laberinto, se nesecita cambiar el numero de `laberinto = MazeGenerator(20)` en el `main()` de `laberinto.py`
- **Para tamaños muy grandes del laberinto:** `Wheighted A*` puede demorarse en crearse mientras que el `algoritmo genético` puede llegar a consumir demasiada memoria y 
dejar de responder
- **Recomendación:** Considerar laberinto de tamaño mínimo 10 y, para `Weighted A*` un máximo de 50, mientras que para el `Algoritmo Genetico`
un máximo de 20
- Código hecho y testeado en Windows