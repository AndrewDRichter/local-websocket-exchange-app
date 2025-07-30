import flet as ft
import requests
from datetime import datetime as dt
import websockets
from utils.error_handler_decorator import error_handler_decorator


class ChatCustomInput(ft.Row):
    def __init__(self, text, on_send):
        super().__init__()
        self.message_input = ft.TextField(hint_text=text, width=200)
        self.message_send_button = ft.IconButton(icon=ft.Icons.SEND, on_click=self.send, visible=True)
        self.controls = [
            self.message_input,
            self.message_send_button
        ]
        self.on_send = on_send
        self.alignment = ft.MainAxisAlignment.CENTER

    def send(self, e):
        msg = str(self.message_input.value).strip()
        self.message_input.value = ''
        self.on_send(e, msg)
        self.update()


async def main(page: ft.Page):
    page.window.width = 400
    page.window.height = 600
    page.window.resizable = False
    page.scroll = ft.ScrollMode.ALWAYS
    exchange_data = ft.Text("0.0",)
    cost_data = ft.Text("0.0",)
    gas_data = ft.Text("0.0",)
    conn_established = False
    chat_messages = ft.Column(scroll=ft.ScrollMode.ALWAYS, height=200, width=page.width)

    async def receber_dados():
        uri = f'ws://192.168.1.123:8000/ws'
        async with websockets.connect(uri) as websocket:
            while True:
                mensagem = await websocket.recv()
                print(mensagem)
                if 'Câmbio' in mensagem:
                    exchange_data.value = mensagem.split(": ")[1]
                if 'Combustível' in mensagem:
                    gas_data.value = mensagem.split(": ")[1]
                if 'Custo' in mensagem:
                    cost_data.value = mensagem.split(": ")[1]
                if 'Chat' in mensagem:
                    msg = mensagem.split(': ')[1]
                    msg_txt = ft.Text(msg, expand=True)
                    chat_messages.controls.append(msg_txt)
                    chat_messages.scroll_to(offset=-1, duration=1000)
                
                page.update()

    @error_handler_decorator
    def request_combustivel(e):
        response = requests.get('http://192.168.1.123:8000/get-combustivel')
        values = response.json().get('mensagem')
        gas_data.value = str(values).split(": ")[1]
        page.update()

    @error_handler_decorator
    def request_cambio(e):
        response = requests.get('http://192.168.1.123:8000/get-cambio')
        values = response.json().get('mensagem')
        exchange_data.value = str(values).split(": ")[1]
        page.update()

    @error_handler_decorator
    def request_custo(e):
        response = requests.get('http://192.168.1.123:8000/get-custo')
        values = response.json().get('mensagem')
        cost_data.value = str(values).split(": ")[1]
        page.update()

    def enviar(e, msg):
        URL = f'http://192.168.1.123:8000/atualizar-chat/{msg}'
        response = requests.post(url=URL)

    def login(e,):
        print('login')
        loginView.visible = False
        view.visible = True
        page.update()

    # Login Section
    loginView = ft.Column([
        ft.Row([
            ft.Text('Nombre: '),
        ]),
        ft.Row([
            ft.TextField(hint_text='usuario...'),
        ]),
        ft.Row([
            ft.Text('Contraseña: '),
        ]),
        ft.Row([
            ft.TextField(password=True),
        ]),
        ft.Row([
            ft.ElevatedButton(text='Entrar', on_click=login)
        ])
    ], alignment=ft.MainAxisAlignment.CENTER, )

    # View Section
    view = ft.Column([
            ft.Row([
                    ft.Column([
                        ft.ElevatedButton(text="Câmbio", icon=ft.Icons.ATTACH_MONEY_SHARP, on_click=request_cambio),
                        ft.Row([
                            ft.Text("Câmbio: "),
                            exchange_data,
                        ])
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    height=75
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            ),
            ft.Row([
                ft.Column([
                        ft.ElevatedButton(text="Combustível", icon=ft.Icons.LOCAL_GAS_STATION_SHARP, on_click=request_combustivel),
                        ft.Row([
                            ft.Text("Combustível: "),
                            gas_data,
                        ]),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    height=75
                ),

            ],
            alignment=ft.MainAxisAlignment.CENTER,
            ),
            ft.Row([
                ft.Column([
                        ft.ElevatedButton(text="Custo", icon=ft.Icons.TRENDING_UP, on_click=request_custo),
                        ft.Row([
                            ft.Text("Custo: "),
                            cost_data,
                        ]),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    height=75
                ),

            ],
            alignment=ft.MainAxisAlignment.CENTER,
            ),
            ChatCustomInput(text='...', on_send=enviar),
            chat_messages,
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        visible=False
    )

    page.add(loginView, view)
    page.run_task(receber_dados)


ft.app(main)
