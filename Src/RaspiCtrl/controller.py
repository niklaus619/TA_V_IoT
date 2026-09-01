import time

from pymodbus.client import ModbusTcpClient


client = ModbusTcpClient(
    host="iot-server",
    port=5020
)

if client.connect():
    print("Verbindung zum Modbus Server erfolgreich")

    temperatur = 234  # entspricht 23.4 °C

    client.write_register(
        address=0,
        value=temperatur
    )

    print(f"Temperaturwert {temperatur} geschrieben")

    client.close()
else:
    print("Verbindung fehlgeschlagen")