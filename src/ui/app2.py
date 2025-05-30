from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Header, Footer, Input, Static, LoadingIndicator, ListView, ListItem, Label
from textual.binding import Binding

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

    .list {
        width: 1fr;
        border: round $accent;
        padding: 1;
        background: transparent;
    }
    
    .messages {
        height: 1fr;
        width: 4fr;
        border: round $accent; # borde de los logs
        padding: 1;
        color: #ffffff;
    }

    .input {
        dock: bottom;
        margin: 1;
        border: round $accent;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "Salir", show=True),
        Binding("enter", "select_cursor", "Select", show=False),
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
                    ListItem(Label("1. Iniciar servidor TCP")),
                    ListItem(Label("2. Cerrar servidor TCP")),
                    ListItem(Label("3. Iniciar servidor UDP")),
                    ListItem(Label("4. Cerrar servidor UDP")),
                    ListItem(Label("5. Enviar mensaje TCP")),
                    ListItem(Label("6. Enviar mensaje UDP")),
                    classes="list",
                ),
                
                Static("", classes="messages"),
                classes="row", 
            ),
            Input(placeholder="Escribe un mensaje...", classes="input"),
        )
        yield Footer()

    def on_mount(self) -> None:
        """Configuración inicial"""
        self.title = "CSAT"
        self.sub_title = "Mensajería cliente-servidor y Análisis de Tráfico"
        # Buscar widgets por clase
        lista = self.query_one(".list", expect_type=ListView)
        mensajes = self.query_one(".messages", expect_type=Static)

        lista.border_title = "Funciones"
        mensajes.border_title = "Logs"  

    def LoadingIndicator(self):
        """Barrita de carga"""
        self.loading_indicator = LoadingIndicator()
        self.add(self.loading_indicator)


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