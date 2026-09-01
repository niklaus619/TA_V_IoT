import streamlit as st
from pymodbus.client import ModbusTcpClient

st.set_page_config(
    page_title="IoT Raumklimasteuerung",
    layout="wide"
)

st.title("IoT Raumklimasteuerung – Modbus TCP Demo")

controller_col, server_col = st.columns(2)

with controller_col:
    st.subheader("🎛 Controller")

    temperatur = st.number_input(
        "Temperatur [°C]",
        min_value=-20.0,
        max_value=60.0,
        value=23.4,
        step=0.1
    )

    feuchtigkeit = st.number_input(
        "Feuchtigkeit [%]",
        min_value=0,
        max_value=100,
        value=48
    )

    helligkeit = st.number_input(
        "Helligkeit [lx]",
        min_value=0,
        max_value=100000,
        value=750
    )

    senden = st.button(
        "Werte über Modbus senden",
        use_container_width=True
    )


client = ModbusTcpClient(
    host="iot-server",
    port=5020
)


if senden:

    if client.connect():

        client.write_register(
            address=0,
            value=int(temperatur * 10)
        )

        client.write_register(
            address=1,
            value=int(feuchtigkeit)
        )

        client.write_register(
            address=2,
            value=int(helligkeit)
        )

        st.session_state["gesendet"] = True

    else:
        st.error("Keine Verbindung zum Modbus-Server")


with server_col:
    st.subheader("🖥 Server")

    if client.connect():

        result = client.read_holding_registers(
            address=0,
            count=3
        )

        if not result.isError():

            temperatur_server = result.registers[0] / 10
            feuchtigkeit_server = result.registers[1]
            helligkeit_server = result.registers[2]

            st.success("🟢 Modbus TCP verbunden")

            st.metric(
                "Temperatur",
                f"{temperatur_server:.1f} °C"
            )

            st.metric(
                "Feuchtigkeit",
                f"{feuchtigkeit_server} %"
            )

            st.metric(
                "Helligkeit",
                f"{helligkeit_server} lx"
            )

        else:
            st.error("Register konnten nicht gelesen werden")

    else:
        st.error("🔴 Server nicht erreichbar")


client.close()