"""
Servidor TCP para prueba de concepto
"""
import socket
import threading
import logging
from datetime import datetime
import sys
from pathlib import Path

# agregamosel directorio root al path para que se encuentren
root_dir = str(Path(__file__).parent.parent.parent)
if root_dir not in sys.path:
    sys.path.append(root_dir)

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def used_port(port, host='0.0.0.0'):
    """verificamso si un puerto está en uso"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, port))
            return False
        except socket.error:
            return True

class TCPServer:
    def __init__(self, host='0.0.0.0', port=54321, log_callback=None):
        self.host = host
        self.port = port
        self.server_socket = None
        self.running = False
        self.log_callback = log_callback

    def _log(self, message):
        """envía el log al callback si existe, sino usa logger"""
        if self.log_callback:
            self.log_callback(message)
        else:
            logger.info(message)

    def start(self):
        """inicia el servidor TCP"""
        if used_port(self.port, self.host):
            self._log(f"El puerto {self.port} ya está en uso. El servidor ya está corriendo.")
            return

        try:
            #creamos un socket tcp sobre ipv4
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # esto permite reutilizar la dirección y puerto sin esperar TIME_WAIT.
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # quitar en la entrega final
            # asocia el socket a la ip y puerto definidos.
            self.server_socket.bind((self.host, self.port))
            #soporta hasta 2 conexioens por si acaso
            self.server_socket.listen(2)
            self.running = True
            self._log(f"Servidor TCP iniciado en {self.host}:{self.port}")

            while self.running:
                try:
                    client_socket, address = self.server_socket.accept()
                    self._log(f"Conexión aceptada de {address}")
                    client_thread = threading.Thread(
                        target=self._handle_client,
                        args=(client_socket, address)
                    )
                    client_thread.start()
                except Exception as e:
                    if self.running:
                        self._log(f"Error al aceptar conexión: {e}")

        except Exception as e:
            self._log(f"Error al iniciar servidor TCP: {e}")
            self.stop()

    def _handle_client(self, client_socket, address):
        """maneja la conexión con un cliente"""
        try:
            while True:
                # Recibe mensaje
                data = client_socket.recv(1024)
                if not data:
                    break
                    
                message = data.decode()
                client_ip, client_port = address
                timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
                self._log(f"Mensaje recibido desde la IP {client_ip} puerto {client_port}.")
                self._log(f"Tiempo de recepción: {timestamp}")
                
                # Envía respuesta
                response = f"Confirmación recibida: {message}"
                client_socket.send(response.encode())
                
        except Exception as e:
            self._log(f"Error al manejar cliente {address}: {e}")
        finally:
            client_socket.close()
            self._log(f"Conexión cerrada con {address}")

    def stop(self):
        """detiene el servidor TCP"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
            self._log("Servidor TCP detenido")

if __name__ == '__main__':
    server = TCPServer()
    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()