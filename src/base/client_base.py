"""
Clase base para clientes TCP y UDP
"""
import socket
import logging
import time
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

class BaseClient:
    def __init__(self, host='localhost'):
        self.host = host
        self.socket = None
        self.message_count = 0
        self.server_ip = None
        self.server_port = None

    def _get_server_info(self):
        """Obtiene la información del servidor después de la conexión"""
        if self.socket:
            self.server_ip, self.server_port = self.socket.getpeername()
            return True
        return False

    def _log_message_info(self, message, is_sending=True):
        """registra info"""
        timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
        if is_sending:
            logger.info(f"Mensaje: {message}")
            if self._get_server_info():
                logger.info(f"IP de destino: {self.server_ip}")
                logger.info(f"Puerto de destino: {self.server_port}")
            logger.info(f"Tiempo de envío: {timestamp}")

    def _log_rtt(self, start_time, end_time):
        """registra el tiempo de respuesta"""
        rtt = (end_time - start_time)*1000
        logger.info(f"RTT: {rtt:.2f}ms")

    def close(self):
        """cierra la conexión"""
        if self.socket:
            try:
                self.socket.close()
                logger.info("Conexión cerrada")
            except Exception as e:
                logger.error(f"Error al cerrar la conexión: {e}")
            finally:
                self.socket = None