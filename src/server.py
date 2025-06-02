"""
Servidores TCP y UDP para prueba de concepto
"""
import socket
import threading
import logging
from datetime import datetime
import sys
from pathlib import Path

# agregamos el directorio root al path
root_dir = str(Path(__file__).parent.parent.parent)
if root_dir not in sys.path:
    sys.path.append(root_dir)

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def used_port(port, host='localhost'):
    """verificamos si un puerto está en uso"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, port))
            return False
        except socket.error:
            return True

def used_port_udp(port, host='localhost'):
    """verificamos si un puerto UDP está en uso"""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        try:
            s.bind((host, port))
            return False
        except socket.error:
            return True

class BaseServer:
    def __init__(self, host='localhost', port=None, log_callback=None):
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

    def stop(self):
        """detiene el servidor"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
            self._log(f"Servidor {self.__class__.__name__} detenido")

class TCPServer(BaseServer):
    def __init__(self, host='localhost', port=54321, log_callback=None):
        super().__init__(host, port, log_callback)

    def start(self):
        """inicia el servidor TCP"""
        if used_port(self.port, self.host):
            self._log(f"El puerto {self.port} ya está en uso. El servidor ya está corriendo.")
            return

        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
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
        """maneja la conexión con un cliente TCP"""
        try:
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break
                    
                message = data.decode()
                client_ip, client_port = address
                timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
                self._log(f"Mensaje recibido desde la IP {client_ip} puerto {client_port}.")
                self._log(f"Tiempo de recepción: {timestamp}")
                
                response = f"Confirmación recibida: {message}"
                client_socket.send(response.encode())
                
        except Exception as e:
            self._log(f"Error al manejar cliente {address}: {e}")
        finally:
            client_socket.close()
            self._log(f"Conexión cerrada con {address}")

class UDPServer(BaseServer):
    def __init__(self, host='localhost', port=5555, log_callback=None):
        super().__init__(host, port, log_callback)

    def start(self):
        """inicia el servidor UDP"""
        if used_port_udp(self.port, self.host):
            self._log(f"El puerto UDP {self.port} ya está en uso. El servidor ya está corriendo.")
            return

        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.settimeout(1.0)  # timeout para poder detener el servidor
            self.server_socket.bind((self.host, self.port))
            self.running = True
            self._log(f"Servidor UDP iniciado en {self.host}:{self.port}")

            while self.running:
                try:
                    data, address = self.server_socket.recvfrom(1024)
                    message = data.decode()
                    client_ip, client_port = address
                    timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
                    
                    self._log(f"Mensaje recibido desde la IP {client_ip} puerto {client_port}: {message}")
                    self._log(f"Tiempo de recepción: {timestamp}")
                    
                    response = f"Confirmación recibida: {message}"
                    self.server_socket.sendto(response.encode(), address)
                    self._log(f"Respuesta enviada a {address}")
                    
                except socket.timeout:
                    # timeout normal, continuar el bucle para verificar self.running
                    continue
                except Exception as e:
                    if self.running:
                        self._log(f"Error al recibir mensaje UDP: {e}")
        except Exception as e:
            self._log(f"Error al iniciar servidor UDP: {e}")
            self.stop()
        finally:
            self._log("Servidor UDP terminado")

if __name__ == '__main__':
    print("Seleccione el servidor a iniciar:")
    print("1. TCP")
    print("2. UDP")
    eleccion = input("Ingrese su elección (1 o 2): ")
    
    if eleccion == "1":
        server = TCPServer()
    elif eleccion == "2":
        server = UDPServer()
    else:
        print("Opcion invalida")
        exit(1)
        
    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()