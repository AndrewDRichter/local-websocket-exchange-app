import json
import flet as ft
import requests
from datetime import datetime as dt
import websockets
from utils.error_handler_decorator import error_handler_decorator
from utils.months import MONTHS

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
    username = ft.TextField(hint_text='usuario...')
    password = ft.TextField(password=True)
    conn_established = False
    # chat_messages = ft.Column(scroll=ft.ScrollMode.ALWAYS, height=200, width=page.width)
    chat_ref = ft.Ref[ft.Column]()
    chat_container = ft.Container(
        content=ft.Column(ref=chat_ref, scroll=ft.ScrollMode.ALWAYS),
        height=200,
        width=page.width,
    )

    async def receber_dados():
        uri = f'ws://192.168.1.101:8000/ws'
        async with websockets.connect(uri) as websocket:
            while True:
                mensagem = await websocket.recv()
                print(mensagem)
                if 'Cambio' in mensagem:
                    print(f'Cambio: {mensagem}')
                    # exchange_data.value = mensagem.split(": ")[1]
                if 'Combustible' in mensagem:
                    print(f'Combustible: {mensagem}')
                    # gas_data.value = mensagem.split(": ")[1]
                if 'Costo' in mensagem:
                    print(f'Costo: {mensagem}')
                    # cost_data.value = mensagem.split(": ")[1]
                if 'Chat' in mensagem:
                    # msg = mensagem.split(': ')[1]
                    # msg_txt = ft.Text(msg, expand=True)
                    # chat_messages.controls.append(msg_txt)
                    # chat_messages.scroll_to(offset=-1, duration=1000)
                    chat_ref.current.controls.append(ft.Text(mensagem))
                    chat_ref.current.update()
                
                page.update()

    # @error_handler_decorator
    def request_combustivel(e):
        response = requests.get('http://192.168.1.101:8000/get-gas-price/')
        price = response.json().get('price')
        gas_data.value = str(f'{price}')
        page.update()

    # @error_handler_decorator
    def request_cambio(e):
        headers = {
            'Authorization': f'Bearer {page.client_storage.get('session')}'
        }
        response = requests.get('http://192.168.1.101:8000/get-exchange-values/', headers=headers)
        print(response.json())
        # buy = response.json().get('buy')
        # sell = response.json().get('sell')
        # exchange_data.value = str(f'{buy}/{sell}')
        page.update()

    # @error_handler_decorator
    def request_custo(e):
        response = requests.get('http://192.168.1.101:8000/get-soybean-cost/')
        print(response.json())
        cost = response.json().get('cost')
        ref_month = response.json().get('ref_month')
        print(ref_month)
        cost_data.value = str(f'{cost}/{MONTHS[ref_month]}')
        page.update()

    def enviar(e, msg):
        URL = f'http://192.168.1.101:8000/atualizar-chat/{msg}'
        response = requests.post(url=URL)

    def login(e):
        # headers = {
        #     'Authorization': f'Bearer token123'
        # }
        data = {
            "username": username.value,
            "password": password.value
        }
        response = requests.post('http://192.168.1.101:8000/signin/', data=json.dumps(data))
        token = response.json().get('token', None)
        if token is None:
            raise Exception('Erro ao fazer login')
        page.clean()
        page.add(view)
        page.run_task(receber_dados)
        page.client_storage.set(key='session', value=token)
        page.update()

    # Login Section
    loginView = ft.Column([
        ft.Row([
            ft.Text('Nombre: '),
        ]),
        ft.Row([
            username,
        ]),
        ft.Row([
            ft.Text('Contraseña: '),
        ]),
        ft.Row([
            password,
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
            # chat_messages,
            chat_container,
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        # visible=False
    )

    # page.add(loginView, view)
    page.add(loginView)
    # page.run_task(receber_dados)


ft.app(main)
