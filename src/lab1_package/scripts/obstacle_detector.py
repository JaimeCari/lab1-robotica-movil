#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Vector3
import numpy as np
# Se recomienda usar cv_bridge para convertir fácilmente el mensaje de ROS a un array de NumPy
from cv_bridge import CvBridge

class ObstacleDetector(Node):
    def __init__(self):
        super().__init__('obstacle_detector')
        
        # Suscripción a la imagen de profundidad del Kinect
        self.subscription = self.create_subscription(
            Image,
            '/camera/depth/image_raw',
            self.depth_callback,
            10
        )
        
        # Publicador del estado de ocupación
        self.publisher = self.create_publisher(
            Vector3,
            '/occupancy_state',
            10
        )
        
        self.bridge = CvBridge()
        self.get_logger().info("Nodo obstacle_detector iniciado correctamente.")

    def depth_callback(self, msg):
        # 1. Convertir el mensaje ROS (sensor_msgs/Image) a un array de NumPy
        # Las imágenes de profundidad de simuladores suelen venir en 32FC1 (metros, float32)
        try:
            depth_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='passthrough')
        except Exception as e:
            self.get_logger().error(f"Error al convertir imagen: {e}")
            return
        
        # En caso de que el array contenga NaNs (valores no definidos por estar muy cerca/lejos), los ignoramos
        depth_image = np.nan_to_num(depth_image, nan=10.0)

        # 2. Dividir la imagen en 3 regiones (Izquierda, Centro, Derecha)
        height, width = depth_image.shape
        third = width // 3
        
        left_region = depth_image[:, :third]
        center_region = depth_image[:, third:2*third]
        right_region = depth_image[:, 2*third:]
        
        # 3. Detectar obstáculos a 50 cm o menos (0.5 metros)
        # Se asume que los valores > 0.0 son lecturas válidas
        threshold = 0.5 
        
        # np.any() es eficiente para comprobar si AL MENOS UN píxel cumple la condición
        obs_left = 1.0 if np.any((left_region > 0.0) & (left_region <= threshold)) else 0.0
        obs_center = 1.0 if np.any((center_region > 0.0) & (center_region <= threshold)) else 0.0
        obs_right = 1.0 if np.any((right_region > 0.0) & (right_region <= threshold)) else 0.0
        
        # 4. Publicar el estado de ocupación en formato Vector3 (x=Izquierda, y=Centro, z=Derecha)
        occupancy_msg = Vector3()
        occupancy_msg.x = obs_left
        occupancy_msg.y = obs_center
        occupancy_msg.z = obs_right
        
        self.publisher.publish(occupancy_msg)
        
        # self.get_logger().debug(f"Occupancy State: ({obs_left}, {obs_center}, {obs_right})")

def main(args=None):
    rclpy.init(args=args)
    node = ObstacleDetector()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()