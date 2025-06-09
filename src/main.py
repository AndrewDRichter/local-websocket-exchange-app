import flet as ft
import requests
from datetime import datetime as dt
import websockets
from utils.error_handler_decorator import error_handler_decorator

async def main(page: ft.Page):
    page.window.width = 300
    page.window.height = 600
    page.window.resizable = False
    exchange_data = ft.Text("0.0",)
    gas_data = ft.Text("0.0",)
    status_bar = ft.Text(dt.now().strftime("%d/%m/%y %H:%M:%S"))
    conn_established = False

    async def receber_dados():
        uri = f'ws://192.168.1.140:8000/ws'
        async with websockets.connect(uri) as websocket:
            while True:
                mensagem = await websocket.recv()
                print(mensagem)
                if 'Câmbio' in mensagem:
                    exchange_data.value = mensagem.split(": ")[1]
                if 'Combustível' in mensagem:
                    gas_data.value = mensagem.split(": ")[1]
                
                page.update()

    @error_handler_decorator
    def request_combustivel(e):
        response = requests.get('http://192.168.1.140:8000/get-combustivel')
        values = response.json().get('mensagem')
        gas_data.value = str(values).split(": ")[1]
        page.update()

    @error_handler_decorator
    def request_cambio(e):
        response = requests.get('http://192.168.1.140:8000/get-cambio')
        values = response.json().get('mensagem')
        exchange_data.value = str(values).split(": ")[1]
        page.update()


    view = ft.Column([
            ft.Row([status_bar]),
            ft.Row([
                    ft.Column([
                        ft.ElevatedButton(text="Câmbio", icon=ft.Icons.ATTACH_MONEY_SHARP, on_click=request_cambio),
                        ft.Row([
                            ft.Text("Câmbio: "),
                            exchange_data,
                        ])
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    height=100
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
                    height=100
                ),

            ],
            alignment=ft.MainAxisAlignment.CENTER,
            ),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
    )

    page.add(view)
    page.run_task(receber_dados)


ft.app(main)
