"""
Utilidades para conversión entre bytes y hexadecimal
"""
import logging

logger = logging.getLogger(__name__)

class BinaryConverter:
    @staticmethod
    def bytes_to_hex(data: bytes) -> str:
        """Convierte bytes a string hexadecimal"""
        try:
            return data.hex()
        except Exception as e:
            logger.error(f"Error al convertir bytes a hex: {e}")
            return None

    @staticmethod
    def hex_to_bytes(hex_str: str) -> bytes:
        """Convierte string hexadecimal a bytes"""
        try:
            return bytes.fromhex(hex_str)
        except Exception as e:
            logger.error(f"Error al convertir hex a bytes: {e}")
            return None

    @staticmethod
    def int_to_bytes(value: int, size: int = 4) -> bytes:
        """Convierte un entero a bytes"""
        try:
            return value.to_bytes(size, byteorder='big')
        except Exception as e:
            logger.error(f"Error al convertir entero a bytes: {e}")
            return None

    @staticmethod
    def bytes_to_int(data: bytes) -> int:
        """Convierte bytes a entero"""
        try:
            return int.from_bytes(data, byteorder='big')
        except Exception as e:
            logger.error(f"Error al convertir bytes a entero: {e}")
            return None 