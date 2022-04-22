from trading_app_client import TradingAppClient
from trading_app_server import *


async def run_client():
    print('inside run client')

    client = TradingAppClient()
    await client.connect_async('ws://localhost:8080')
    for i in range(100):
        place_order_request = PlaceOrderRequest()
        place_order_request.Symbol = "INFY"
        place_order_request.Market = "NSE"
        place_order_request.Quantity = i + 99
        place_order_request.Price = (i + 99) * 100
        await client.place_order_async(place_order_request)

    # Sleep for a few seconds, until the server sends back order execution status
    await asyncio.sleep(10)

    # disconnect from server
    await client.disconnect('normal client disconnect')


async def main():
    print('Hello World!')
    print('WebsocketsApp or Client (S/C): ')
    val = input()

    if val == 'S' or val == 's':
        server = TradingAppServer(8080)
        await server.initialize_async()
    else:
        for j in range(1):
            asyncio.create_task(run_client())

        print('wait for a few seconds to close the client program automatically')
        await asyncio.sleep(30)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
