"""
Servidor TCP para transferencia de archivos
"""
import socket
import threading
import logging
import os
from ..base.message_handler import TCPMessageHandler
from ..utils.file_handler import FileHandler

logger = logging.getLogger(__name__)

class TCPServer:
    def __init__(self, host='0.0.0.0', port=54321):
        self.host = host
        self.port = port
        self.server_socket = None
        self.running = False
        self.clients = []
        self.received_files_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'received_files'))
        os.makedirs(self.received_files_dir, exist_ok=True)
        logger.info(f"Directorio de archivos recibidos: {self.received_files_dir}")

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
                    client_thread = threading.Thread(target=self._handle_client, args=(client_socket, address))
                    client_thread.start()
                    self.clients.append(client_thread)
                except Exception as e:
                    if self.running:
                        logger.error(f"Error al aceptar conexión: {e}")

        except Exception as e:
            logger.error(f"Error al iniciar servidor TCP: {e}")
            self.stop()

    def stop(self):
        """Detiene el servidor TCP"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        for client in self.clients:
            client.join()
        logger.info("Servidor TCP detenido")

    def _send_response(self, client_socket: socket.socket, message: str) -> bool:
        """Envía una respuesta al cliente"""
        try:
            response_bytes = message.encode('utf-8')
            response_size = len(response_bytes).to_bytes(4, byteorder='big')
            logger.debug(f"Enviando respuesta: {message} ({len(response_bytes)} bytes)")
            
            # Enviar tamaño y mensaje juntos
            full_response = response_size + response_bytes
            total_sent = 0
            while total_sent < len(full_response):
                sent = client_socket.send(full_response[total_sent:])
                if sent == 0:
                    logger.error("Conexión rota al enviar respuesta")
                    return False
                total_sent += sent
            
            logger.debug("Respuesta enviada completamente")
            return True
        except Exception as e:
            logger.error(f"Error al enviar respuesta: {e}")
            return False

    def _handle_client(self, client_socket: socket.socket, address):
        """Maneja la conexión con un cliente"""
        try:
            # Recibe el tamaño del mensaje (4 bytes)
            size_data = client_socket.recv(4)
            if not size_data or len(size_data) != 4:
                logger.error("Error al recibir tamaño del mensaje")
                self._send_response(client_socket, "Error: tamaño de mensaje inválido")
                return

            message_size = int.from_bytes(size_data, byteorder='big')
            logger.debug(f"Esperando mensaje de {message_size} bytes")

            # Recibe el mensaje completo
            data = b''
            while len(data) < message_size:
                chunk = client_socket.recv(min(4096, message_size - len(data)))
                if not chunk:
                    logger.error("Conexión cerrada por el cliente durante la recepción")
                    return
                data += chunk
                logger.debug(f"Recibidos {len(data)} de {message_size} bytes")

            if len(data) != message_size:
                logger.error(f"Mensaje incompleto. Recibidos {len(data)} bytes de {message_size}")
                self._send_response(client_socket, "Error: mensaje incompleto")
                return

            logger.debug(f"Mensaje completo recibido: {len(data)} bytes")

            # Desempaqueta el archivo
            filename, content = TCPMessageHandler.parse_file_message(data)
            if filename is None or content is None:
                logger.error("Error al desempaquetar archivo")
                self._send_response(client_socket, "Error: no se pudo desempaquetar el archivo")
                return

            logger.debug(f"Archivo desempaquetado: {filename} ({len(content)} bytes)")

            # Guarda el archivo
            filepath = os.path.join(self.received_files_dir, filename)
            if FileHandler.save_file(filename, content, self.received_files_dir):
                logger.info(f"Archivo guardado: {filepath}")
                if not self._send_response(client_socket, f"Archivo {filename} recibido y guardado correctamente"):
                    logger.error("Error al enviar confirmación de éxito")
            else:
                logger.error(f"Error al guardar archivo: {filepath}")
                if not self._send_response(client_socket, f"Error al guardar archivo {filename}"):
                    logger.error("Error al enviar mensaje de error")

        except Exception as e:
            logger.error(f"Error al manejar cliente {address}: {e}")
            try:
                self._send_response(client_socket, f"Error interno del servidor: {str(e)}")
            except:
                pass
        finally:
            client_socket.close()
            logger.info(f"Conexión cerrada con {address}")

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    server = TCPServer()
    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()