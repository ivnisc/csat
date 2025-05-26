"""
Manejo de archivos y transferencia directa
"""
import os
import logging

logger = logging.getLogger(__name__)

class FileHandler:
    @staticmethod
    def read_file(file_path):
        """Lee un archivo y retorna (nombre, contenido en bytes)"""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            filename = os.path.basename(file_path)
            logger.info(f"Archivo leído exitosamente: {file_path} ({len(content)} bytes)")
            return filename, content
        except Exception as e:
            logger.error(f"Error al leer el archivo {file_path}: {e}")
            return None, None

    @staticmethod
    def save_file(filename, content, save_dir):
        """Guarda el archivo en el directorio indicado"""
        try:
            os.makedirs(save_dir, exist_ok=True)
            save_path = os.path.join(save_dir, filename)
            with open(save_path, 'wb') as f:
                f.write(content)
            logger.info(f"Archivo guardado en: {save_path} ({len(content)} bytes)")
            return True
        except Exception as e:
            logger.error(f"Error al escribir el archivo {save_dir}: {e}")
            return False

    @staticmethod
    def prepare_file_message(file_path):
        """Prepara el contenido del archivo para enviar"""
        try:
            # Leemos el archivo
            filename, content = FileHandler.read_file(file_path)
            if filename is None or content is None:
                return None

            logger.info(f"Archivo preparado para envío: {file_path} ({len(content)} bytes)")
            return filename, content
        except Exception as e:
            logger.error(f"Error al preparar archivo {file_path}: {e}")
            return None

    @staticmethod
    def process_file_message(content, save_path):
        """Procesa y guarda el contenido recibido"""
        try:
            if content is None:
                logger.error("Contenido inválido")
                return False

            return FileHandler.save_file(content[0], content[1], save_path)
        except Exception as e:
            logger.error(f"Error al procesar archivo: {e}")
            return False 