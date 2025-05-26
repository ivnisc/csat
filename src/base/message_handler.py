"""
Manejo de mensajes para transferencia de archivos
"""
import logging

logger = logging.getLogger(__name__)

class MessageHandler:
    @staticmethod
    def prepare_message(content: bytes) -> bytes:
        """
        Prepara un mensaje para enviar
        Retorna: bytes del mensaje
        """
        try:
            return content
        except Exception as e:
            logger.error(f"Error al preparar mensaje: {e}")
            return None

    @staticmethod
    def parse_message(data: bytes) -> bytes:
        """
        Parsea un mensaje recibido
        """
        try:
            return data
        except Exception as e:
            logger.error(f"Error al parsear mensaje: {e}")
            return None

    @staticmethod
    def prepare_file_message(filename: str, content: bytes):
        """
        Empaqueta el nombre y el contenido del archivo:
        - 2 bytes: longitud del nombre (big-endian)
        - N bytes: nombre (UTF-8)
        - Resto: contenido
        """
        try:
            name_bytes = filename.encode('utf-8')
            name_len = len(name_bytes)
            name_len_bytes = name_len.to_bytes(2, byteorder='big')
            return name_len_bytes + name_bytes + content
        except Exception as e:
            logger.error(f"Error al empaquetar archivo: {e}")
            return None

    @staticmethod
    def parse_file_message(data: bytes):
        """
        Desempaqueta el mensaje recibido:
        - 2 bytes: longitud del nombre
        - N bytes: nombre
        - Resto: contenido
        Devuelve (nombre, contenido)
        """
        try:
            if len(data) < 2:
                logger.error("Mensaje demasiado corto para contener longitud de nombre")
                return None, None
            name_len = int.from_bytes(data[:2], byteorder='big')
            if len(data) < 2 + name_len:
                logger.error("Mensaje demasiado corto para contener el nombre completo")
                return None, None
            name_bytes = data[2:2+name_len]
            filename = name_bytes.decode('utf-8')
            content = data[2+name_len:]
            return filename, content
        except Exception as e:
            logger.error(f"Error al desempaquetar archivo: {e}")
            return None, None

class TCPMessageHandler(MessageHandler):
    @staticmethod
    def prepare_message(content: bytes) -> tuple:
        """
        Prepara un mensaje para enviar por TCP
        Retorna: (size_bytes, message_bytes)
        """
        try:
            # Prepara el tamaño del mensaje (4 bytes en big-endian)
            message_size = len(content)
            size_bytes = message_size.to_bytes(4, byteorder='big')
            return size_bytes, content
        except Exception as e:
            logger.error(f"Error al preparar mensaje TCP: {e}")
            return None, None

    @staticmethod
    def parse_message(data: bytes) -> bytes:
        """
        Parsea un mensaje TCP recibido
        Retorna: bytes del mensaje sin el tamaño
        """
        try:
            if len(data) < 4:
                logger.error("Mensaje TCP demasiado corto para contener tamaño")
                return None
            message_size = int.from_bytes(data[:4], byteorder='big')
            if len(data) < 4 + message_size:
                logger.error("Mensaje TCP incompleto")
                return None
            return data[4:]
        except Exception as e:
            logger.error(f"Error al parsear mensaje TCP: {e}")
            return None