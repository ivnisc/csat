import socket
import logging
from datetime import datetime
import json
import os

# Configuración del logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TCPServer:
    def __init__(self, host='localhost', port=54321):
        self.host = host
        self.port = port
        self.server_socket = None
        # crea directorio para archivos recibidos si no existe
        self.received_dir = "received_files"
        os.makedirs(self.received_dir, exist_ok=True)

    def start(self):
        """Inicia el servidor TCP"""
        try:
            # Crear socket TCP
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Permitir reuso del puerto
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # Vincular socket a la dirección
            self.server_socket.bind((self.host, self.port))
            # Escuchar conexiones entrantes
            self.server_socket.listen(5)
            
            logger.info(f"Servidor TCP iniciado en {self.host}:{self.port}")
            
            while True:
                # Aceptar conexión entrante
                client_socket, client_address = self.server_socket.accept()
                logger.info(f"Conexión establecida desde {client_address[0]}:{client_address[1]}")
                
                try:
                    # Manejar la conexión del cliente
                    self._handle_client(client_socket, client_address)
                except Exception as e:
                    logger.error(f"Error al manejar cliente: {e}")
                finally:
                    client_socket.close()
                    
        except Exception as e:
            logger.error(f"Error en el servidor: {e}")
        finally:
            if self.server_socket:
                self.server_socket.close()

    def _handle_client(self, client_socket, client_address):
        """Maneja la comunicación con un cliente"""
        while True:
            try:
                # Recibir el tamaño del mensaje (4 bytes)
                size_data = client_socket.recv(4)
                if not size_data:
                    break
                
                message_size = int.from_bytes(size_data, byteorder='big')
                
                # Recibir el mensaje completo
                received_data = b''
                while len(received_data) < message_size:
                    chunk = client_socket.recv(min(4096, message_size - len(received_data)))
                    if not chunk:
                        break
                    received_data += chunk
                
                if not received_data:
                    break
                
                # Decodificar y procesar el mensaje
                message = json.loads(received_data.decode('utf-8'))
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Convertir el contenido de hex a bytes
                file_content = bytes.fromhex(message['content'])
                
                # Guardar el archivo
                file_path = os.path.join(self.received_dir, message['filename'])
                with open(file_path, 'wb') as f:
                    f.write(file_content)
                
                logger.info(f"Archivo recibido de {client_address[0]}:{client_address[1]} "
                          f"a las {timestamp}: {message['filename']} ({message['size']} bytes)")
                
                # Enviar confirmación
                response = f"ACK: archivo {message['filename']} recibido a las {timestamp}"
                client_socket.send(response.encode('utf-8'))
                
            except Exception as e:
                logger.error(f"Error en la comunicación con el cliente: {e}")
                break

if __name__ == "__main__":
    server = TCPServer()
    server.start()