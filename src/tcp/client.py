"""
Cliente TCP para transferencia de archivos
"""
import socket
import logging
import os
from src.base.message_handler import TCPMessageHandler, MessageHandler
from src.utils.file_handler import FileHandler

# configuración del logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TCPClient:
    def __init__(self, host='localhost', port=54321):
        self.host = host
        self.port = port
        self.socket = None
        self.message_handler = TCPMessageHandler()

    def connect(self):
        """establece conexión con el servidor"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            logger.info(f"conectado al servidor en {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"error al conectar: {e}")
            return False

    def _receive_response(self):
        """Recibe la respuesta completa del servidor"""
        try:
            # Recibir tamaño de la respuesta
            size_data = b''
            while len(size_data) < 4:
                chunk = self.socket.recv(4 - len(size_data))
                if not chunk:
                    logger.error("Conexión cerrada por el servidor al recibir tamaño")
                    return None
                size_data += chunk

            if len(size_data) != 4:
                logger.error(f"Tamaño de respuesta incompleto: {len(size_data)} bytes")
                return None

            response_size = int.from_bytes(size_data, byteorder='big')
            logger.debug(f"Tamaño de la respuesta: {response_size} bytes")

            # Recibir respuesta completa
            response_data = b''
            while len(response_data) < response_size:
                chunk = self.socket.recv(min(4096, response_size - len(response_data)))
                if not chunk:
                    logger.error("Conexión cerrada por el servidor durante la recepción")
                    return None
                response_data += chunk

            if len(response_data) != response_size:
                logger.error(f"Respuesta incompleta. Recibidos {len(response_data)} bytes de {response_size}")
                return None

            return response_data.decode('utf-8')

        except Exception as e:
            logger.error(f"Error al recibir respuesta: {e}")
            return None

    def send_file(self, file_path):
        """envía un archivo al servidor"""
        try:
            filename, content = FileHandler.read_file(file_path)
            if filename is None or content is None:
                logger.error(f"error al preparar archivo {file_path}")
                return False

            logger.debug(f"Archivo leído: {filename} ({len(content)} bytes)")
            
            # Empaquetar nombre y contenido
            message_bytes = MessageHandler.prepare_file_message(filename, content)
            if not message_bytes:
                logger.error("Error al empaquetar el archivo")
                return False

            # Preparar tamaño para TCP
            size_bytes, tcp_message = self.message_handler.prepare_message(message_bytes)
            if not size_bytes or not tcp_message:
                logger.error("Error al preparar mensaje TCP")
                return False
            
            # Enviar datos
            total_sent = 0
            while total_sent < len(size_bytes):
                sent = self.socket.send(size_bytes[total_sent:])
                if sent == 0:
                    logger.error("Conexión rota al enviar tamaño")
                    return False
                total_sent += sent

            total_sent = 0
            while total_sent < len(tcp_message):
                sent = self.socket.send(tcp_message[total_sent:])
                if sent == 0:
                    logger.error("Conexión rota al enviar mensaje")
                    return False
                total_sent += sent

            logger.info(f"Archivo enviado: {filename} ({len(content)} bytes)")
            
            # espera confirmación
            response = self._receive_response()
            if response:
                logger.info(f"respuesta recibida: {response}")
            else:
                logger.warning("No se recibió respuesta del servidor")
            return True
        except Exception as e:
            logger.error(f"error al enviar archivo: {e}")
            self.close()
            return False

    def send_path(self, path):
        """envía un archivo o directorio al servidor"""
        if not os.path.exists(path):
            logger.error(f"la ruta no existe: {path}")
            return False

        try:
            if os.path.isdir(path):
                logger.info(f"enviando archivos del directorio: {path}")
                for root, dirs, files in os.walk(path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        if not self.send_file(file_path):
                            logger.error(f"error al enviar archivo: {file_path}")
                return True
            else:
                return self.send_file(path)
        except Exception as e:
            logger.error(f"error al procesar la ruta: {e}")
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
            path = input("Ingresa la ruta del archivo o directorio: ")
            client.send_path(path)
        except KeyboardInterrupt:
            logger.info("Programa interrumpido por el usuario")
        finally:
            client.close() 