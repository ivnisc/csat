"""
Cliente TCP y UDP para prueba de concepto
"""
import socket
import logging
import time
from datetime import datetime
import sys
from pathlib import Path

# agregamos el directorio root al path
root_dir = str(Path(__file__).parent.parent.parent)
if root_dir not in sys.path:
    sys.path.append(root_dir)

from src.base.client_base import BaseClient

logger = logging.getLogger(__name__)

class TCPClient(BaseClient):
    def __init__(self, port=54321, log_callback=None):
        super().__init__()
        self.port = port
        self.log_callback = log_callback

    def _log(self, message):
        """envía el log al callback si existe, sino usa logger"""
        if self.log_callback:
            self.log_callback(message)
        else:
            logger.info(message)

    def connect(self):
        """establece conexión con el servidor"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self._log(f"Conectado al servidor en {self.host}:{self.port}")
            return True
        except Exception as e:
            self._log(f"Error al conectar: {e}")
            return False

    def send_message(self, message):
        """envía un mensaje al servidor y recibe respuesta"""
        try:
            if message.lower() == 'end':
                if self.message_count < 5:
                    self._log(f"Error: Debes enviar al menos 5 mensajes. Llevas {self.message_count}")
                    return True
                return False

            # envía mensaje
            self.socket.send(message.encode())
            self.message_count += 1
            
            # información del envío
            timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
            self._log(f"Mensaje: {message}")
            if self._get_server_info():
                self._log(f"IP de destino: {self.server_ip}")
                self._log(f"Puerto de destino: {self.server_port}")
            self._log(f"Tiempo de envío: {timestamp}")
            
            # recibe respuesta
            response = self.socket.recv(1024).decode()
            #self._log(f"Respuesta: {response}")
            return True
        except Exception as e:
            self._log(f"Error al enviar mensaje: {e}")
            return False

    def close(self):
        """cierra la conexión con el servidor"""
        if self.socket:
            try:
                self.socket.close()
                self._log("Conexión cerrada")
            except Exception as e:
                self._log(f"Error al cerrar la conexión: {e}")
            finally:
                self.socket = None

class UDPClient(BaseClient):
    def __init__(self, port=5555, log_callback=None):
        super().__init__()
        self.port = port
        self.log_callback = log_callback
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(5.0)  # timeout de 5 segundos

    def _log(self, message):
        """envía el log al callback si existe, sino usa logger"""
        if self.log_callback:
            self.log_callback(message)
        else:
            logger.info(message)

    def send_message(self, message):
        """envía un mensaje al servidor UDP"""
        try:
            if message.lower() == 'end':
                if self.message_count < 5:
                    self._log(f"Error: Debes enviar al menos 5 mensajes. Llevas {self.message_count}")
                    return True
                return False

            # envía mensaje
            self.socket.sendto(message.encode(), (self.host, self.port))
            self.message_count += 1
            
            # información del envío
            timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
            self._log(f"Mensaje: {message}")
            self._log(f"IP de destino: {self.host}")
            self._log(f"Puerto de destino: {self.port}")
            self._log(f"Tiempo de envío: {timestamp}")
            
            # recibe respuesta
            data, addr = self.socket.recvfrom(1024)
            #response = data.decode()
            #self._log(f"Respuesta: {response}")
            return True
        except socket.timeout:
            self._log("Timeout: No se recibió respuesta del servidor")
            return False
        except Exception as e:
            self._log(f"Error al enviar mensaje UDP: {e}")
            return False

    def close(self):
        """cierra el socket UDP"""
        if self.socket:
            try:
                self.socket.close()
                self._log("Socket UDP cerrado")
            except Exception as e:
                self._log(f"Error al cerrar socket UDP: {e}")
            finally:
                self.socket = None

if __name__ == "__main__":
    print("Seleccione el cliente a iniciar:")
    print("1. TCP")
    print("2. UDP")
    eleccion = input("Ingrese su elección (1 o 2): ")
    
    if eleccion == "1":
        client = TCPClient()
        if client.connect():
            try:
                print("\n=== Cliente TCP ===")
                print("Ingresa mensajes (min 5). Escribe 'end' para terminar.")
                
                while True:
                    message = input()
                    if not client.send_message(message):
                        break
            except KeyboardInterrupt:
                logger.info("Programa interrumpido por el usuario")
            finally:
                client.close()
    elif eleccion == "2":
        client = UDPClient()
        try:
            print("\n=== Cliente UDP ===")
            print("Ingresa mensajes (min 5). Escribe 'end' para terminar.")
            
            while True:
                message = input()
                if not client.send_message(message):
                    break
        except KeyboardInterrupt:
            logger.info("Programa interrumpido por el usuario")
        finally:
            client.close()
    else:
        print("Opción inválida")