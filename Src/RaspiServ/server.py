import asyncio

from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusDeviceContext
from pymodbus.datastore import ModbusServerContext
from pymodbus.server import StartAsyncTcpServer


async def main():
    store = ModbusDeviceContext(
        hr=ModbusSequentialDataBlock(1, [0] * 100)
    )

    context = ModbusServerContext(
        devices=store,
        single=True
    )

    print("Modbus TCP Server läuft auf Port 5020")

    await StartAsyncTcpServer(
        context=context,
        address=("0.0.0.0", 5020)
    )


asyncio.run(main())