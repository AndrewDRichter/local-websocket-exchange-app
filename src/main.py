import json
import flet as ft
import requests
import time
from requests.exceptions import HTTPError
from datetime import datetime as dt
import websockets
from websockets.exceptions import ConnectionClosedError
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
    auth_token = None
    conn_established = False
    chat_ref = ft.Ref[ft.Column]()
    chat_container = ft.Container(
        content=ft.Column(ref=chat_ref, scroll=ft.ScrollMode.ALWAYS),
        height=200,
        width=page.width,
    )

    async def get_token():
        return await page.client_storage.get("session")

    async def receber_dados():
        uri = f'ws://192.168.1.101:8000/ws'

        headers = {'Authorization': f'Bearer {auth_token}'}

        retry_delay = 2
        max_delay = 30

        while True:
            try:
                print("🔌 Tentando conectar ao WebSocket...")
                async with websockets.connect(uri, additional_headers=headers) as websocket:
                    print("✅ Conectado ao WebSocket!")

                    retry_delay = 2

                    while True:
                        mensagem = await websocket.recv()
                        print(mensagem)
                        if 'Cambio' in mensagem:
                            exchange_data.value = mensagem.split(": ")[1]
                        if 'Combustible' in mensagem:
                            gas_data.value = mensagem.split(": ")[1]
                        if 'Costo' in mensagem:
                            cost, ref_month = mensagem.split(': ')[1].split('/')
                            cost_data.value = str(f'{cost}/{MONTHS[int(ref_month)]}')
                        # if 'Chat' in mensagem:
                            # msg = mensagem.split(': ')[1]
                            # msg_txt = ft.Text(msg, expand=True)
                            # chat_messages.controls.append(msg_txt)
                            # chat_messages.scroll_to(offset=-1, duration=1000)
                        chat_ref.current.controls.append(ft.Text(mensagem))
                        chat_ref.current.update()
                        
                        page.update()
            except (ConnectionClosedError, ConnectionRefusedError) as e:
                print(f'Error: {e}. Retrying connection in 2 seconds')
                time.sleep(2)
                page.run_task(receber_dados)
            # except ConnectionRefusedError as e:
            #     print(f'Error: {e}. Retrying connection in 2 seconds')
            #     time.sleep(2)
            #     page.run_task(receber_dados)
            finally:
                print('Error')
        

    # @error_handler_decorator
    async def request_gas(e):
        headers = {'Authorization': f'Bearer {auth_token}'}
        response = requests.get('http://192.168.1.101:8000/gas-price/', headers=headers)
        gas_data.value = str(response.json().get('price'))
        page.update()

    # @error_handler_decorator
    async def request_exchange(e):
        headers = {'Authorization': f'Bearer {auth_token}'}
        response = requests.get('http://192.168.1.101:8000/exchange-values/', headers=headers)
        buy = response.json().get('buy')
        sell = response.json().get('sell')
        exchange_data.value = str(f'{buy}/{sell}')
        page.update()

    # @error_handler_decorator
    async def request_cost(e):
        headers = {'Authorization': f'Bearer {auth_token}'}
        response = requests.get('http://192.168.1.101:8000/soybean-cost/', headers=headers)
        cost = response.json().get('cost')
        ref_month = response.json().get('ref_month')
        cost_data.value = str(f'{cost}/{MONTHS[ref_month]}')
        page.update()

    def enviar(e, msg):
        URL = f'http://192.168.1.101:8000/message/{msg}'
        response = requests.post(url=URL)

    def login(e):
        nonlocal auth_token
        data = {
            "username": username.value,
            "password": password.value
        }
        try:
            response = requests.post('http://192.168.1.101:8000/signin', data=json.dumps(data))
            token = response.json().get('token', None)
            if not token:
                raise HTTPError('Invalid token')
            auth_token = token

            page.clean()
            page.add(view)
            page.update()
            page.run_task(receber_dados)
        except Exception as e:
            print(f'Login error: {e}')

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
                        ft.ElevatedButton(text="Cambio", icon=ft.Icons.ATTACH_MONEY_SHARP, on_click=request_exchange),
                        ft.Row([
                            ft.Text("Cambio: "),
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
                        ft.ElevatedButton(text="Combustible", icon=ft.Icons.LOCAL_GAS_STATION_SHARP, on_click=request_gas),
                        ft.Row([
                            ft.Text("Combustible: "),
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
                        ft.ElevatedButton(text="Costo", icon=ft.Icons.TRENDING_UP, on_click=request_cost),
                        ft.Row([
                            ft.Text("Costo: "),
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
