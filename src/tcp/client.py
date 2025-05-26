import socket
import logging
from datetime import datetime
import os
import json

# configuración del logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TCPClient:
    def __init__(self, host='localhost', port=54321):
        self.host = host
        self.port = port
        self.client_socket = None

    def connect(self):
        """establece conexión con el servidor"""
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))
            logger.info(f"conectado al servidor en {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"error al conectar: {e}")
            return False

    def send_file(self, file_path):
        """envía un archivo al servidor"""
        try:
            # lee el archivo en modo binario
            with open(file_path, 'rb') as file:
                file_content = file.read()
                file_name = os.path.basename(file_path)
                
                # crea un diccionario con la información del archivo
                message = {
                    'filename': file_name,
                    'content': file_content.hex(),  # convierte bytes a hex para json
                    'size': len(file_content)
                }
                
                # convierte el mensaje a json y luego a bytes
                message_bytes = json.dumps(message).encode('utf-8')
                
                # envía el tamaño del mensaje primero
                message_size = len(message_bytes)
                self.client_socket.send(message_size.to_bytes(4, byteorder='big'))
                
                # envía el mensaje
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.client_socket.send(message_bytes)
                logger.info(f"archivo enviado a las {timestamp}: {file_name} ({message_size} bytes)")
                
                # espera confirmación
                response = self.client_socket.recv(1024).decode('utf-8')
                logger.info(f"respuesta recibida: {response}")
                
            return True
        except Exception as e:
            logger.error(f"error al procesar el archivo {file_path}: {e}")
            return False

    def send_path(self, path):
        """envía un archivo o directorio al servidor"""
        if not os.path.exists(path):
            logger.error(f"la ruta no existe: {path}")
            return False

        try:
            if os.path.isdir(path):
                # si es un directorio, envía cada archivo
                logger.info(f"enviando archivos del directorio: {path}")
                for root, dirs, files in os.walk(path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        if not self.send_file(file_path):
                            logger.error(f"error al enviar archivo: {file_path}")
                return True
            else:
                # si es un archivo, envíalo directamente
                return self.send_file(path)
        except Exception as e:
            logger.error(f"error al procesar la ruta: {e}")
            return False
        finally:
            if self.client_socket:
                self.client_socket.close()

if __name__ == "__main__":
    # ejemplo de uso
    client = TCPClient()
    if client.connect():
        # aquí deberías proporcionar la ruta al archivo o directorio
        path = input("ingresa la ruta del archivo o directorio: ")
        client.send_path(path) 