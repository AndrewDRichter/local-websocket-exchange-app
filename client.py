import asyncio
import threading
import websockets
from pystray import Icon, MenuItem, Menu
from PIL import Image, ImageDraw
import sys
from config import get_config_value

cambio_atual = "Aguardando..."  # Valor inicial do câmbio
combustivel_atual = "Aguardando..."  # Valor inicial do combustível
icone_global = None  # Referência ao ícone da bandeja
log = "..."  # Referência ao ícone da bandeja
client_version = get_config_value("CLIENT_VERSION", default="0.0.0.1")


def criar_icone():
    imagem = Image.new('RGB', (64, 64), color='green')
    draw = ImageDraw.Draw(imagem)
    draw.rectangle((16, 16, 48, 48), fill='white')
    return imagem

async def receber_dados():
    global cambio_atual
    global combustivel_atual
    global log
    uri = f"ws://{get_config_value("SERVER_IP", default="192.168.1.140")}:8000/ws"
    async with websockets.connect(uri) as websocket:
        while True:
            mensagem = await websocket.recv()
            if "Câmbio" in mensagem:
                cambio_atual = mensagem.split(":")[1]
            if "Combustível" in mensagem:
                combustivel_atual = mensagem.split(":")[1]
            log = mensagem
            atualizar_menu()

def iniciar_websocket():
    asyncio.run(receber_dados())

def atualizar_menu():
    if icone_global:
        icone_global.menu = Menu(
            MenuItem(f"💱 Câmbio atual: {cambio_atual}", None, enabled=False),
            MenuItem(f"💱 Combustível atual: {combustivel_atual}", None, enabled=False),
            MenuItem(f"Logger: {log}", None, enabled=False),
            # MenuItem(f"Version: {client_version}", None, enabled=False),
            MenuItem("Sair", lambda icon, item: sair(icon))
        )
        icone_global.update_menu()

def iniciar_bandeja():
    global icone_global
    icone = Icon("Cambio Monitor")
    icone.icon = criar_icone()
    icone.title = "Monitor de Câmbio"

    icone.menu = Menu(
        MenuItem(f"💱 Câmbio atual: {cambio_atual}", None, enabled=False),
        MenuItem(f"💱 Combustível atual: {combustivel_atual}", None, enabled=False),
        MenuItem(f"Version: {client_version}", None, enabled=False),
        MenuItem("Sair", lambda icon, item: sair(icon))
    )

    icone_global = icone

    threading.Thread(target=iniciar_websocket, daemon=True).start()
    icone.run()

def sair(icon):
    icon.stop()
    sys.exit()

if __name__ == "__main__":
    iniciar_bandeja()
