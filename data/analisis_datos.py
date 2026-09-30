'''
Analisis de la trayectoria Actividad 1.2. 
Este script lee los CSV que genera el script pose_recorder_csv,
dibuja las trayectorias, y calcula el error entre punto de partida
y llegada.
'''

import csv
import matplotlib.pyplot as plt


def upload_csv(path: str) -> dict:
    data = {'real_pose': ([], []), 'odometry': ([], [])}
    with open(path, newline='') as csv_data:
        for row in csv.DictReader(csv_data):
            x, y = data[row['Source']]   # elige las listas de 'real' u 'odom'
            x.append(float(row['x']))
            y.append(float(row['y']))
    if not data['real_pose'][0] or not data['odometry'][0]:
        raise ValueError(f'{path}: faltan datos de real u odom')
    return data

def xy_error(x: list, y: list) -> float: # Pitagoras
    return ((x[-1] - x[0]) ** 2 + (y[-1] - y[0]) ** 2) ** 0.5

def graph_trajectory(run: dict, title: str, output: str) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(11, 5))
    sources = (('real_pose', 'Real (/real_pose)'), ('odometry', 'Odometría (/odom)'))

    for ax, (source, name) in zip(axes, sources):
        x, y = run[source]
        ax.plot(x, y, linewidth=1)
        ax.plot(x[0], y[0], 'o', color='green', label='inicio')
        ax.plot(x[-1], y[-1], 'x', color='red', markersize=9, label='fin')
        ax.set_title(name)
        ax.set_xlabel('x [m]')
        ax.set_ylabel('y [m]')
        ax.set_aspect('equal', adjustable='datalim')  
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=8)

    fig.suptitle(title)
    fig.tight_layout()
    fig.savefig(f'{output}.png', dpi=150)
    plt.show()


def main() -> None:
    path = input('Nombre archivo CSV (ej: factor/test1.csv): ').strip()
    title = input('Título del gráfico: ').strip() or 'Trayectoria del robot'
    output = input('Nombre del PNG de salida (sin .png): ').strip() or 'trayectoria'

    run = upload_csv(path)

    # Se desempaqueta la tupla (x, y) en dos argumentos
    error_real = xy_error(*run['real_pose']) * 100   # m -> cm
    error_odom = xy_error(*run['odometry']) * 100s

    print(f'\nError real (inicio-fin): {error_real:.3f} cm')
    print(f'Error odometria (inicio-fin): {error_odom:.3f} cm')

    graph_trajectory(run, title, output) # Se grafica la trayectoria
    print(f'Gráfico guardado en {output}.png')


if __name__ == '__main__':
    main()
