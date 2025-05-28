"""
Clase base para clientes TCP y UDP
"""
import socket
import logging
import time
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

class BaseClient:
    def __init__(self, host='localhost'):
        self.host = host
        self.socket = None
        self.message_count = 0

    def _log_message_info(self, message, is_sending=True):
        """Registra información común de los mensajes"""
        timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
        if is_sending:
            logger.info(f"Mensaje #{self.message_count} enviado: {message}")
            logger.info(f"IP destino: {self.host}")
            logger.info(f"Puerto destino: {self.port}")
            logger.info(f"Timestamp envío: {timestamp}")
        else:
            logger.info(f"Timestamp recepción: {timestamp}")

    def _log_rtt(self, start_time, end_time):
        """Registra el tiempo de respuesta"""
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