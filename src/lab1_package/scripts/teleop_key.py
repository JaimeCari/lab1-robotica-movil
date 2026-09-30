import tkinter as tk
import rclpy #ros2

from rclpy.node import Node
from geometry_msgs.msg import Twist
from .parameters import MOVE_BINDINGS, INSTRUCTIONS # dict para los comandos

class TeleoperationKeyTTBot(Node):
    def __init__(self) -> None:
        super().__init__('teleoperation_key')
        # se crea el nodo solo como Publisher
            # Topic : /cmd_vel
            # cola: 10
            # tipo mensaje: Twist
        self.publisher_obj = self.create_publisher(Twist, '/cmd_vel', 10)
        self.get_logger().info( 'Ventana de comando de tecla (i/j/a/s/q/w)...')

    def publish_msg(self, linear: float, angular: float):
        msg = Twist()
        msg.linear.x = linear
        msg.angular.z = angular
        self.publisher_obj.publish(msg) # Envia el mensaje al topic /cmd_vel

class TeleopWindow(tk.Tk):

    def __init__(self, node: TeleoperationKeyTTBot) -> None:
        super().__init__()
        self.node = node

        self.title('Teleoperación TurtleBot')
        self.geometry('700x250')

        tk.Label(self, text=INSTRUCTIONS, justify='left', font=('Courier', 11)).pack(pady=10)
        self.status_var = tk.StringVar(value='Esperando tecla...')
        tk.Label(self, textvariable=self.status_var, font=('Courier', 12, 'bold')).pack(pady=10)

        self.bind('<KeyPress>', self.on_key_press) # tecla presionada
        self.bind('<KeyRelease>', self.on_key_release) # tecla suelta

        self.protocol('WM_DELETE_WINDOW', self.on_close) # al cerrar ejecutar self.on_close

    def on_key_press(self, event: tk.Event) -> None:
        key = event.char

        if key in MOVE_BINDINGS:
            linear, angular = MOVE_BINDINGS[key]
            self.node.publish_msg(linear, angular)
            self.status_var.set(f'Tecla: [{key}]; v={linear} m/s, w={angular} rad/s')
            self.node.get_logger().info(f'Tecla presionada: [{key}]; v={linear}m/s, w={angular}rad/s')

    def on_key_release(self, event: tk.Event) -> None:
        self.node.publish_msg(0.0, 0.0)
        self.status_var.set('Esperando tecla...')

    def on_close(self) -> None:
        self.node.publish_msg(0.0, 0.0) # se detiene turttle bot
        self.node.destroy_node() # se elimina el nodo
        rclpy.shutdown()
        self.destroy()

def main(args=None) -> None:
    rclpy.init(args = args)         # inicia ROS 2 com
    node = TeleoperationKeyTTBot()

    window = TeleopWindow(node)
    window.mainloop()   # bucle de eventos de tkinter — reemplaza tu `while rclpy.ok()`


if __name__ == '__main__':
    main()