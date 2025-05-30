"""
Cliente TCP para prueba de concepto
"""
from src.base.client_base import BaseClient
import socket
import logging
import time

logger = logging.getLogger(__name__)

class TCPClient(BaseClient):
    def __init__(self, port=54321):
        super().__init__()
        self.port = port

    def connect(self):
        """establece conexión con el servidor"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            logger.info(f"Conectado al servidor en {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Error al conectar: {e}")
            return False

    def send_message(self, message):
        """envía un mensaje al servidor y recibe respuesta"""
        try:
            self.socket.sendall(message.encode())
            self.message_count += 1
            
            # información del envío
            self._log_message_info(message, is_sending=True)
            
            # recibir respuesta (solo para mantener la conexión)
            self.socket.recv(1024).decode()
            return True
        except Exception as e:
            logger.error(f"Error al enviar mensaje: {e}")
            return False

    def close(self):
        """cierra la conexión con el servidor"""
        if self.socket:
            try:
                self.socket.close()
                logger.info("Conexión cerrada")
            except Exception as e:
                logger.error(f"Error al cerrar la conexión: {e}")
            finally:
                self.socket = None

if __name__ == "__main__":
    client = TCPClient()
    if client.connect():
        try:
            print("\n=== Cliente TCP ===")
            print("Ingresa mensajes (min 5). Escribe 'end' para terminar.")
            print("Cada mensaje se enviará inmediatamente al presionar Enter.")
            
            while True:
                message = input()  # Quitamos el prompt
                if message.lower() == 'end':
                    if client.message_count < 5:
                        print(f"Error: Debes enviar al menos 5 mensajes. Llevas {client.message_count}")
                        continue
                    break
                
                client.send_message(message)
                
        except KeyboardInterrupt:
            logger.info("Programa interrumpido por el usuario")
        finally:
            client.close()