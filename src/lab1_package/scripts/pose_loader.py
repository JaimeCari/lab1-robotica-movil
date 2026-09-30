#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
import math
from geometry_msgs.msg import Pose, PoseArray
import time
from .parameters import PATH_POSE_LOADER


class PoseLoader(Node):
    def __init__(self):
        super().__init__('pose_loader')
        self.get_logger().info('pose_loader iniciado')
        self.publisher = self.create_publisher(PoseArray,'goal_list', 10)
        self.comandos = []


    def funcion_archivos(self):
        with open (PATH_POSE_LOADER, 'r') as f:
            for linea in f:

                fila = linea.strip()
                lista = fila.split(";") 
                lista_float = [float(lista[0]), float(lista[1]), float(lista[2])]
                self.comandos.append(lista_float)
                if not fila:
                    continue

    def mandar_mensaje(self) -> None:
        msg = PoseArray()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'map'

        for x, y, theta in self.comandos:
            pose = Pose()
            pose.position.x = x
            pose.position.y = y
            pose.orientation.z = math.sin(theta / 2)
            pose.orientation.w = math.cos(theta / 2)
            msg.poses.append(pose)

        self.publisher.publish(msg)
        self.get_logger().info('Envio de %d poses' % len(msg.poses))




def main(args=None) -> None:
    rclpy.init(args=args)
    nodo = PoseLoader()

    # Esperar a que mi nodo dead_reckoning_nav esteescuchando
    while nodo.publisher.get_subscription_count() == 0 and rclpy.ok():
        nodo.get_logger().info('Esperando al nodo')
        time.sleep(0.5) #para no pregunte a cada rato

    nodo.funcion_archivos()

    nodo.mandar_mensaje()
    nodo.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()