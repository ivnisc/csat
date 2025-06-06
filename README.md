# CSAT - Cliente-Servidor de Análisis de Tráfico

## Instalación / Installation

### Opción 1: Instalación Global / Option 1: Global Installation
```bash
pip install textual
```

### Opción 2: Instalación en Entorno Virtual / Option 2: Virtual Environment Installation
```bash
# Crear entorno virtual / Create virtual environment
python -m venv venv

# Activar entorno virtual / Activate virtual environment
source venv/bin/activate

# Instalar textual / Install textual
pip install textual
```

## Uso / How to use

Para ejecutar la aplicación CSAT, utiliza el siguiente comando:

To run the CSAT app, use the following command:

```bash
python src/ui/app2.py
```

## Funciones / Features

- Interfaz gráfica basada en Textual / Textual-based graphical interface
- Soporte para protocolos TCP y UDP / TCP and UDP protocol support
- Monitoreo de tráfico en tiempo real / Real-time traffic monitoring
- Análisis de paquetes y conexiones / Packet and connection analysis
  
<img width="983" alt="csat" src="https://github.com/user-attachments/assets/7f72ec88-4b5c-4473-9545-5342be432dee" />

## Próximamente / Next Features

- Soporte para interfaz de red externa (0.0.0.0) / External network interface support
- Configuración personalizada de puertos / Custom port config
- Análisis detallado de tráfico con PyShark / Detailed traffic analysis with PyShark
