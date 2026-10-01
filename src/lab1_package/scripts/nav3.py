#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, PoseArray, Pose, Vector3
from .parameters import EPS

import time
import threading
import time
import math

class Dead_reckoning_nav( Node ):
    def __init__( self ):
        super().__init__( 'dead_reckoning_nav')
        self.max_v = 0# [m/s]
        self.max_w = 0 # [rad/s]
        
        # Variables de estado de percepción
        self.occupancy_state = [0.0, 0.0, 0.0] # [izq, centro, der]
        self.last_log = "" # Para evitar spam en terminal
        
        self.cmd_vel_mux_pub = self.create_publisher( Twist, '/cmd_vel', 10 )
        self.subscription = self.create_subscription(PoseArray,'goal_list', self.accion_mover_cb, 10)
        
        # Suscriptor al detector de obstáculos
        self.occ_sub = self.create_subscription(Vector3, '/occupancy_state', self.occupancy_cb, 10)

    def occupancy_cb(self, msg):
        self.occupancy_state = [msg.x, msg.y, msg.z]
        
        # Lógica para evitar spam y cumplir el requerimiento de logs
        current_log = ""
        if msg.x == 1.0:
            current_log = "obstacle left"
        elif msg.y == 1.0:
            current_log = "obstacle center"
        elif msg.z == 1.0:
            current_log = "obstacle right"
            
        if current_log != "" and current_log != self.last_log:
            self.get_logger().info(current_log)
            self.last_log = current_log
        elif current_log == "" and self.last_log != "":
            self.get_logger().info("Camino libre, reanudando...")
            self.last_log = ""

    def move( self ):
        speed = Twist()
        speed.linear.x = self.max_v
        speed.angular.z = self.max_w
        self.get_logger().info( 'publishing speed (%f, %f)' % (speed.linear.x, speed.angular.z) )
        self.cmd_vel_mux_pub.publish( speed )

    def aplicar_velocidad(self, speed_command_list):
        inicio = time.perf_counter()
        for v, w, t in speed_command_list:
            self.max_v = v
            self.max_w = w
            t_ini = time.time()
            while True:
                restante = t - (time.time() - t_ini)
                if restante <= 0:
                    break
                self.move()
                time.sleep(min(0.05, restante))
        self.max_v = 0.0
        self.max_w = 0.0
        self.move()
        self.get_logger().info('tiempo: ' + str(time.perf_counter() - inicio))


    def comando_avance(self, distancia, v=0.2):
        # El signo de la distancia define si avanza o retrocede
        if abs(distancia) < EPS : #No hay moviento en dicha direccion
            return None
        signo = 1 if distancia > 0 else -1
        return (signo * v, 0.0, abs(distancia) / v)

    def comando_giro(self, angulo, w=1.0):
        #Comando de abajao permite realizar el giro mas optimo (el de menor distancia)
        #ya que funcion restringe el rango entre -180 a 180
        #atan2 te entrega el angulo que se encuentra en cierto punto (x,y)
        angul = math.atan2(math.sin(angulo), math.cos(angulo))
        if abs(angul) < EPS:
            return None
        signo = 1 if angul > 0 else -1
        return (0.0, signo * w, abs(angul) / w)

    def mover_robot_a_destino(self, goal_pose):
        x = goal_pose[0]
        y = goal_pose[1]
        theta = goal_pose[2]
        #Para evaluar casos en donde hay un sola coordenada, en especial se crea
        #el booleano, el cual se compara con un numero muy chico
        hay_x = abs(x) > EPS
        hay_y = abs(y) > EPS
        comandos = []


        #Este es el caso en que solo se necesita rotar y no mover a ningun lado
        if not hay_x and not hay_y:
            comandos.append(self.comando_giro(theta))

        #Caso 2: solo línea recta en x
        elif hay_x and not hay_y:
            comandos.append(self.comando_avance(x))
            comandos.append(self.comando_giro(theta))

        #Caso 3: puro desplazamiento en y: girar, avanzar, girar hasta theta;
        #dado que parte orientado horizontalmente, se debe girar primero antes de
        #desplazarse
        elif hay_y and not hay_x:
            #Comando de abajo sirve para quedarse con la magnitud de 90, pero el signo
            #lo da y, de esta manera se maneja para que direccion gira
            giro = math.copysign(math.pi / 2, y)
            comandos.append(self.comando_giro(giro))
            comandos.append(self.comando_avance(abs(y)))
            #Se gira lo que "quede" por girar
            comandos.append(self.comando_giro(theta - giro))

        else:
            #Caso 4 general: avanzar en x, girar, avanzar en y, girar hasta theta
            giro = math.copysign(math.pi / 2, y)
            comandos.append(self.comando_avance(x))
            comandos.append(self.comando_giro(giro))
            comandos.append(self.comando_avance(abs(y)))
            comandos.append(self.comando_giro(theta - giro))

        # Para manejar los casos en donde es nulo el movimiento y obviamente no nos interesa
        #entonces se filtra comandos
        nueva = []
        for c in comandos:
            if c is not None:
                nueva.append(c)
        comandos = nueva

        #Toma el caso de que pasaria si es que mi nueva lista filtrada, se queda sin nada
        if not comandos:
            self.get_logger().info('Pose objetivo igual a la actual, nada que hacer')
            return

        self.aplicar_velocidad(comandos)

    def accion_mover_cb(self, msg):
        # En lugar de ejecutar el movimiento aquí y bloquear ROS, 
        # lanzamos un hilo independiente para procesar toda la lista de metas.
        hilo_movimiento = threading.Thread(target=self.procesar_metas, args=(msg,))
        hilo_movimiento.start()

    def procesar_metas(self, msg):
        for pose in msg.poses:
            x = pose.position.x
            y = pose.position.y
            theta = 2 * math.atan2(pose.orientation.z, pose.orientation.w)
            self.mover_robot_a_destino((x, y, theta))

def main( args = None ):

    rclpy.init( args = args )
    mover = Dead_reckoning_nav()
    rclpy.spin(mover)
    mover.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()  



