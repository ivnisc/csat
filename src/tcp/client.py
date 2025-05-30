"""
Cliente TCP para prueba de concepto
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

            # Envía mensaje
            self.socket.send(message.encode())
            self.message_count += 1
            
            # información del envío
            timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
            self._log(f"Mensaje: {message}")
            if self._get_server_info():
                self._log(f"IP de destino: {self.server_ip}")
                self._log(f"Puerto de destino: {self.server_port}")
            self._log(f"Tiempo de envío: {timestamp}")
            
            # Recibe respuesta
            self.socket.recv(1024).decode()
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
# por si se ejecuta en terminal python3 o por modulo python3 -m ruta.
if __name__ == "__main__":
    client = TCPClient()
    if client.connect():
        try:
            print("\n=== Cliente TCP ===")
            print("Ingresa mensajes (min 5). Escribe 'end' para terminar.")
            print("Cada mensaje se enviará inmediatamente al presionar Enter.")
            
            while True:
                message = input()
                if not client.send_message(message):
                    break
        except KeyboardInterrupt:
            logger.info("Programa interrumpido por el usuario")
        finally:
            client.close()
