"""
Nodo registrador de trayectoria. Este nodo se suscribe a /real_pose y a /odom
y guarda las coordenadas (x, y) en un CSV al cerrar

SIN FACTOR DE CORRECION
"""

import csv
import rclpy
import os

from rclpy.node import Node
from geometry_msgs.msg import Pose
from nav_msgs.msg import Odometry
from .parameters import DATA_DIR


class PoseRecorderCSV(Node):
    def __init__(self, output_path: str) -> None:
        super().__init__('pose_recorder_csv')
        self.output_path = output_path
        self.info = [] # Se acumulan los datos a guardar
        self.t0 = None
        # Pose Recorder CSV es subscriptor de los datos de real_pose y odometria
        self.create_subscription(Pose, '/real_pose', self.real_pose_sub, 10)
        self.create_subscription(Odometry, '/odom', self.odom_sub, 10)

        self.get_logger().info(f'Registrando trayectoria en {self.output_path} (Guardar: Ctrl+C)')

    def _elapsed(self) -> float:
        # Calculo de lapsos de tiempo
        now = self.get_clock().now().nanoseconds * 1e-9
        if self.t0 is None:
            self.t0 = now
        return now - self.t0

    def real_pose_sub(self, msg: Pose) -> None:
        # Se ejecuta cuandollega un mensaje a /real_pose.
        self.info.append((self._elapsed(), 'real_pose', msg.position.x, msg.position.y))

    def odom_sub(self, msg: Odometry) -> None:
        # Se ejecuta cuando llega un mensaje a /odom.
        p = msg.pose.pose.position
        self.info.append((self._elapsed(), 'odometry', p.x, p.y))

    def save_to_csv(self) -> None:
        with open(self.output_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Time (s)', 'Source', 'x', 'y'])
            writer.writerows(self.info)
        self.get_logger().info(f'Datos guardados en {self.output_path}')

def next_free_path(prefix: str) -> str:
        # Buscar un nombre no existente de archivo
        os.makedirs(DATA_DIR, exist_ok=True)
        n = 1
        while os.path.exists(os.path.join(DATA_DIR, f'{prefix}_{n}.csv')):
            n += 1
        return os.path.join(DATA_DIR, f'{prefix}_{n}.csv')

def main(args=None) -> None:
    output_path = next_free_path('trayectoria')
    print(f'Se guardará datos en {output_path}')
    rclpy.init(args=args)
    node = PoseRecorderCSV(output_path)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass  # Ctrl+C
    finally:
        node.save_to_csv() # Se guarda el csv en output path
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()