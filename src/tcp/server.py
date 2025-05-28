"""
Servidor TCP para prueba de concepto
"""
import socket
import threading
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

class TCPServer:
    def __init__(self, host='0.0.0.0', port=54321):
        self.host = host
        self.port = port
        self.server_socket = None
        self.running = False

    def start(self):
        """Inicia el servidor TCP"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.running = True
            logger.info(f"Servidor TCP iniciado en {self.host}:{self.port}")

            while self.running:
                try:
                    client_socket, address = self.server_socket.accept()
                    logger.info(f"Conexión aceptada de {address}")
                    client_thread = threading.Thread(
                        target=self._handle_client,
                        args=(client_socket, address)
                    )
                    client_thread.start()
                except Exception as e:
                    if self.running:
                        logger.error(f"Error al aceptar conexión: {e}")

        except Exception as e:
            logger.error(f"Error al iniciar servidor TCP: {e}")
            self.stop()

    def _handle_client(self, client_socket, address):
        """Maneja la conexión con un cliente"""
        try:
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break
                    
                message = data.decode()
                logger.info(f"Mensaje recibido de {address}: {message}")
                
                response = f"Confirmación recibida: {message}"
                client_socket.sendall(response.encode())
                logger.info(f"Respuesta enviada a {address}")
                
        except Exception as e:
            logger.error(f"Error al manejar cliente {address}: {e}")
        finally:
            client_socket.close()
            logger.info(f"Conexión cerrada con {address}")

    def stop(self):
        """Detiene el servidor TCP"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        logger.info("Servidor TCP detenido")

if __name__ == '__main__':
    server = TCPServer()
    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()