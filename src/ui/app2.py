from textual.app import App, ComposeResult
from textual.containers import Container, ScrollableContainer
from textual.widgets import Header, Footer, Input, Static, LoadingIndicator, ListView, ListItem, Label, Log
from textual.binding import Binding
from datetime import datetime
import sys
from pathlib import Path
import threading

# agregar el directorio raíz al path
root_dir = str(Path(__file__).parent.parent.parent)
if root_dir not in sys.path:
    sys.path.append(root_dir)

class CSATApp(App):
    """Aplicación TUI para cliente-servidor TCP/UDP"""
    
    CSS = """
    
    .banner {
        color: $accent-darken-1;
        text-align: center;
        padding: 0;
        border-bottom: solid $accent;
        overflow: hidden;
        height: 11;
    }

    .title {
        color: $accent;
        padding: 1;
        text-align: center;
        text-style: underline bold;
    }

    .row {
        layout: horizontal;
        height: 1fr;
        width: 100%;
    }

    .column {
        layout: vertical;
        width: 4fr;
    }

    .list {
        width: 1fr;
        border: round $accent;
        padding: 1;
        background: transparent;
    }
    
    .messages {
        height: 1fr;
        width: 100%;
        border: round $accent; # borde de los logs
        padding: 1;
        color: #ffffff;
        overflow-y: scroll;
        scrollbar-gutter: stable;
        scrollbar-color: $accent $background;
        background: transparent
    }

    .input {
        dock: bottom;
        margin: 1;
        border: round $accent;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "Salir", show=True),
        Binding("up", "cursor_up", "Cursor up", show=False),
        Binding("down", "cursor_down", "Cursor down", show=False),
    ]

    def compose(self) -> ComposeResult:
        """Crear los widgets de la aplicación"""
        yield Header()
        yield Container(
            Static(banner, classes="banner"),
            Static("Tarea 1 de Redes de Computadores", classes="title"),
            Container(
                ListView(
                    ListItem(Label("1. Iniciar servidor TCP"), id="start_tcp"),
                    ListItem(Label("2. Cerrar servidor TCP"), id="stop_tcp"),
                    ListItem(Label("3. Iniciar servidor UDP"), id="start_udp"),
                    ListItem(Label("4. Cerrar servidor UDP"), id="stop_udp"),
                    ListItem(Label("5. Enviar mensaje TCP"), id="send_tcp"),
                    ListItem(Label("6. Enviar mensaje UDP"), id="send_udp"),
                    classes="list",
                ),
                Container(
                    Log(classes="messages", id="client_msg"),
                    Log(classes="messages", id="server_msg"),
                    classes="column",
                ),
                classes="row", 
            ),
            Input(placeholder="Escribe un mensaje...", classes="input", id="message_input"),
        )
        yield Footer()

    def on_mount(self) -> None:
        """Configuración inicial"""
        self.title = "CSAT"
        self.sub_title = "Mensajería cliente-servidor y Análisis de Tráfico"
        # buscar widgets por clase
        lista = self.query_one(".list", expect_type=ListView)
        server_messages = self.query_one("#server_msg", Log)
        client_messages = self.query_one("#client_msg", Log)

        lista.border_title = "Funciones"
        server_messages.border_title = "Logs Servidor"
        client_messages.border_title = "Logs Cliente"

    def LoadingIndicator(self):
        """Barrita de carga"""
        self.loading_indicator = LoadingIndicator()
        self.add(self.loading_indicator)

    def add_client_log(self, message: str) -> None:
        """añade un log del cliente"""
        client_messages = self.query_one("#client_msg", Log)
        client_messages.write(f"{message}\n")

    def add_server_log(self, message: str) -> None:
        """añade un log del servidor"""
        server_messages = self.query_one("#server_msg", Log)
        server_messages.write(f"{message}\n")

    def start_tcp_server(self) -> None:
        """inicia el servidor TCP"""
        try:
            from src.tcp.server import TCPServer
            self.tcp_server = TCPServer(log_callback=self.add_server_log)
            server_thread = threading.Thread(target=self.tcp_server.start)
            server_thread.daemon = True  # El hilo se cerrará cuando la app se cierre
            server_thread.start()
        except Exception as e:
            self.add_server_log(f"Error al iniciar servidor TCP: {e}")

    def start_udp_server(self) -> None:
        """inicia el servidor UDP"""
        self.add_server_log("Servidor UDP no implementado aún")

    def stop_servers(self) -> None:
        """detiene los servidores"""
        if hasattr(self, 'tcp_server'):
            self.tcp_server.stop()
            self.add_server_log("Servidor TCP detenido")

    def close_tcp_connection(self) -> None:
        """cierra la conexión TCP"""
        if hasattr(self, 'tcp_client') and self.tcp_client is not None:
            try:
                self.tcp_client.close()
                delattr(self, 'tcp_client')
                self.add_client_log("Conexión TCP cerrada")
            except Exception as e:
                self.add_client_log(f"Error al cerrar conexión TCP: {e}")

    def close_udp_connection(self) -> None:
        """cierra la conexión UDP"""
        self.add_client_log("Conexión UDP no implementada aún")

    def send_message(self) -> None:
        """envía un mensaje TCP"""
        input = self.query_one("#message_input", Input)
        message = input.value
        if message:
            try:
                from src.tcp.client import TCPClient
                if not hasattr(self, 'tcp_client'):
                    self.tcp_client = TCPClient(log_callback=self.add_client_log)
                    if not self.tcp_client.connect():
                        self.add_client_log("Error al conectar con el servidor")
                        return
                    self.add_client_log("\n=== Cliente TCP ===")
                    self.add_client_log("Ingresa mensajes (min 5). Escribe 'end' para terminar.")
                    self.add_client_log("Cada mensaje se enviará inmediatamente al presionar Enter.")
                
                if not self.tcp_client.send_message(message):
                    self.tcp_client.close()
                    delattr(self, 'tcp_client')
                    self.add_client_log("Conexión cerrada")
                
            except Exception as e:
                self.add_client_log(f"Error al enviar mensaje: {e}")
                if hasattr(self, 'tcp_client'):
                    self.tcp_client.close()
                    delattr(self, 'tcp_client')
            input.value = ""


    def exit(self) -> None:
        """cierra la aplicación"""
        try:
            if hasattr(self, 'tcp_server') and self.tcp_server is not None:
                self.tcp_server.stop()
                self.tcp_server = None
        except Exception as e:
            self.add_server_log(f"Error al cerrar servidor: {e}")
        finally:
            super().exit()

    # esto maneja evento del binding enter
    def on_input_submitted(self, event: Input.Submitted) -> None:
        lista = self.query_one(".list", expect_type=ListView)
        for item in lista.children:
            if item.highlighted:
                if item.id == "send_tcp":
                    self.send_message()
                elif item.id == "send_udp":
                    self.send_udp_message()
                break

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """maneja la selección de items en la lista"""
        selected = event.item.id
        if selected == "start_tcp":
            try:
                from src.tcp.server import TCPServer
                import threading
                self.tcp_server = TCPServer(log_callback=self.add_server_log)
                server_thread = threading.Thread(target=self.tcp_server.start)
                server_thread.daemon = True
                server_thread.start()
            except Exception as e:
                self.add_server_log(f"Error al iniciar servidor TCP: {e}")
        elif selected == "stop_tcp":
            self.close_tcp_connection()
        elif selected == "start_udp":
            self.add_server_log("Servidor UDP no implementado aún")
        elif selected == "stop_udp":
            self.close_udp_connection()
        elif selected == "send_tcp":
            self.send_message()
        elif selected == "send_udp":
            self.add_client_log("Servidor UDP no implementado aún")

banner = """
  ▄████▄    ██████  ▄▄▄      ▄▄▄█████▓ ▐██▌
▒██▀ ▀█  ▒██    ▒ ▒████▄    ▓  ██▒ ▓▒ ▐██▌
▒▓█    ▄ ░ ▓██▄   ▒██  ▀█▄  ▒ ▓██░ ▒░ ▐██▌
▒▓▓▄ ▄██▒  ▒   ██▒░██▄▄▄▄██ ░ ▓██▓ ░  ▓██▒
▒ ▓███▀ ░▒██████▒▒ ▓█   ▓██▒  ▒██▒ ░  ▒▄▄ 
░ ░▒ ▒  ░▒ ▒▓▒ ▒ ░ ▒▒   ▓▒█░  ▒ ░░    ░▀▀▒
  ░  ▒   ░ ░▒  ░ ░  ▒   ▒▒ ░    ░     ░  ░
░        ░  ░  ░    ░   ▒     ░          ░
░ ░            ░        ░  ░          ░   
░                                  
"""

if __name__ == "__main__":
    app = CSATApp()
    app.run() 