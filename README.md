# Lab 1 — Robótica Móvil (IIC-2685)

Paquete ROS2 (`lab1`) para el Laboratorio 1: navegación por estima (dead reckoning), teleoperación por teclado y percepción/evitación de obstáculos con un TurtleBot simulado. GRUPO N°1.

---

## Tabla de contenidos

1. [Requisitos y dependencias](#1-requisitos-y-dependencias)
2. [Instalación desde cero](#2-instalación-desde-cero)
3. [Organización de carpetas](#3-organización-de-carpetas)
4. [Configuración por máquina (leer antes de correr nada)](#4-configuración-por-máquina-leer-antes-de-correr-nada)
5. [Cómo correr cada actividad](#5-cómo-correr-cada-actividad)
6. [Nodos, tópicos y mensajes](#6-nodos-tópicos-y-mensajes)
7. [Formato de `poses.txt`](#7-formato-de-posestxt)
8. [Problemas conocidos / pendientes](#8-problemas-conocidos--pendientes)
9. [Troubleshooting](#9-troubleshooting)
10. [Referencias](#10-referencias)

---

## 1. Requisitos y dependencias

- Ubuntu 22.04.5 LTS + **ROS2 Humble**
- Python 3.10+
- El simulador [`very_simple_robot_simulator`](https://github.com/gasevi/very_simple_robot_simulator) — **rama `master`**.
Dependencias de sistema (apt), según el propio README del simulador:

```bash
sudo apt update
sudo apt install -y ros-humble-image-transport ros-humble-tf-transformations \
  ros-humble-cv-bridge libcv-bridge-dev python3-pil.imagetk python3-opencv
```
---

## 2. Instalación desde cero

```bash

# Clona la carpeta lab1_ws)
git clone https://github.com/jaimecari/....

# Clona el simulador en ~{your_path}/lab1_ws/src para obtener la última versión 
git clone https://github.com/gasevi/very_simple_robot_simulator.git

cd ~{your path}/lab01_ws
sudo apt update
sudo apt install -y ros-humble-image-transport ros-humble-tf-transformations \
  ros-humble-cv-bridge libcv-bridge-dev python3-pil.imagetk python3-opencv

colcon build --symlink-install
source install/setup.bash
```

`--symlink-install` evita tener que recompilar cada vez que editas un `.py` (los cambios se reflejan al instante). **Sí** hay que recompilar cuando se toca `setup.py`, `package.xml`, o se agregan archivos nuevos en `launch/`/`config/`.

Para no repetir el `source` en cada terminal nueva:
```bash
echo "source ~{your_path}/lab01_ws/install/setup.bash" >> ~/.bashrc
```

---

## 3. Organización de carpetas

```
lab01_ws/                              ← el workspace (acá se corre colcon build)
├── src/
│   ├── lab1_package/                  ← nuestro paquete (el nombre ROS2 real es "lab1", ver nota abajo)
│   │   ├── scripts/                   ← código Python de los nodos
│   │   │   ├── __init__.py
│   │   │   ├── parameters.py          ← constantes compartidas entre scripts .py (teclas, EPS, rutas)
│   │   │   ├── teleop_key.py
│   │   │   ├── pose_loader.py
│   │   │   ├── dead_reckoning_nav.py
│   │   │   ├── obstacle_detector.py
│   │   │   └── pose_recorder_csv.py
│   │   ├── launch/
│   │   │   ├── teleop.xml
│   │   │   ├── avanzar_y_rotar.xml
│   │   │   └── accion_y_percepcion.xml
│   │   ├── config/
│   │   │   └── poses.txt              ← lista de poses a ejecutar A1.1, A1.2
│   │   ├── package.xml
│   │   └── setup.py
│   └── very_simple_robot_simulator/   ← dependencia externa, no se modifica
└── data/                              ← CSV de trayectorias (Actividad 1.2)
```

> **Nota sobre nombres:** la carpeta se llama `lab1_package` y la carpeta interna de código se llama `scripts`, pero el **nombre real del paquete ROS2** (el que se usa en terminal `ros2 run lab1 ...` y `ros2 launch lab1 ...`) sigue siendo `lab1` — Este se define en `package.xml` (`<name>`) y `setup.py` (`package_name`). 

---

## 4. Configuración por máquina (leer antes de correr nada)

Dos archivos tienen **rutas absolutas hardcodeadas**, específicas de una computadora. Si clonas este proyecto en otro computador (wsl, ubuntu), edítalas antes de correr:

**`scripts/parameters.py`**
```python
PATH_POSE_LOADER = {your_path_of_poses.txt}
```
Ajusta la ruta si tu workspace está en otro lugar. 

**`scripts/parameters.py`**
```python
DATA_DIR = {your_path_of_/data}
```
Ajusta la ruta si tu carpeta /data está en otro lugar. 

---

## 5. Cómo correr cada actividad

En **cada terminal nueva**, primero:
```bash
cd ~{your_path}/lab01_ws
source install/setup.bash
```

### Actividad 1.1 — Prueba funcional

1. Modificar la lista de poses de `src/lab1_package/config/poses.txt` (según formato mas abajo).
2. Ejecutar:
   ```bash
   ros2 launch lab1 avanzar_y_rotar.xml
   ```

### Actividad 1.2 — Cuadrado de 1 m, 3 vueltas, con y sin factor de corrección

1. En `poses.txt`, repetir 12 veces la línea `1.0;0.0;1.5708` (avanzar 1 m + girar 90°, ×4 vértices ×3 vueltas).
2. En una terminal nueva:
   ```bash
   ros2 run lab1 pose_recorder_csv
   ```
3. En otra terminal:
   ```bash
   ros2 launch lab1 avanzar_y_rotar.xml
   ```
4. Repetir 5 veces sin factor, y 5 veces con factor
5. Se puede analizar cada CSV:
   ```bash
   cd data
   python3 ~{your_path}/lab1_ws/data/analisis_datos.py   
   ```

### Teleoperación

```bash
ros2 launch lab1 teleop.xml
```
Se abre el simulador + una ventana `tkinter` para capturar las teclas: `i`/`j` avanzar-retroceder, `a`/`s` rotar, `q`/`w` avanzar+rotar.

### Percepción + detección de obstáculos (Sección 3 / Actividad 3.1)

```bash
ros2 launch lab1 accion_y_percepcion.xml
```

**Importante:** El `run_all.xml` del simulador trae **comentado** el `include` de `openni_simulator.xml` (el que levanta `kinect_simulator`). Sin ese nodo, nunca llega nada a `/camera/depth/image_raw` y `obstacle_detector` nunca detecta nada, aunque todo lo demás esté bien. Por eso `accion_y_percepcion.xml` se incluye además del `run_all.xml` para SOLO tenerlo en accion_y_percepcion.xml Revisar que este esto en accion_y_percepcion.xml:
```xml
<include file="$(find-pkg-share very_simple_robot_simulator)/launch/run_all.xml" />
<include file="$(find-pkg-share very_simple_robot_simulator)/launch/openni_simulator.xml" />
```

Durante la demo se pueden dibujar/borrar paredes con `w`/`d` en la ventana del simulador mientras el robot ejecuta el cuadrado, y observar en la terminal los logs `obstacle left/center/right` y `Camino libre, reanudando...`.

---

## 6. Nodos, tópicos y mensajes

| Nodo | Rol | Publica | Se suscribe a |
|---|---|---|---|
| `pose_loader` | Lee `poses.txt` y las envía | `goal_list` (`PoseArray`) | — |
| `dead_reckoning_nav` | Ejecuta la navegación; se detiene ante obstáculos | `/cmd_vel` (`Twist`) | `goal_list`, `/occupancy_state` (`Vector3`) |
| `teleop_key` | Teleoperación por teclado (ventana `tkinter`) | `/cmd_vel` (`Twist`) | — |
| `obstacle_detector` | Detecta obstáculos ≤ 0.5 m en 3 regiones | `/occupancy_state` (`Vector3`: x=izq, y=centro, z=der; 1=ocupado) | `/camera/depth/image_raw` (`Image`) |
| `pose_recorder_csv` | Registra trayectoria para la Actividad 1.2 | — (escribe CSV) | `/real_pose` (`Pose`), `/odom` (`Odometry`) |

`teleop_key` y `dead_reckoning_nav` publican al mismo `/cmd_vel`.

---

## 7. Formato de `poses.txt`

Una pose por línea, separados por `;`: `x;y;theta`, en metros y radianes, **relativos a la pose alcanzada por la línea anterior** (no son coordenadas absolutas).

```
0.5;0.0;0.0
0.0;0.5;1.5708
```

`dead_reckoning_nav` calcula la trayectoria en L: avanza en x, gira 90° hacia donde esté y, avanza en y, y gira lo que falte para llegar a `theta`.

---


## 8. Referencias

- [1] `very_simple_robot_simulator` — https://github.com/gasevi/very_simple_robot_simulator (rama `master`)
