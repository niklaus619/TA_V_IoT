import threading

from flask import Flask, jsonify

from server import RaspCtrlServer


app = Flask(__name__)

raspctrl_server = RaspCtrlServer(
    host="0.0.0.0",
    port=9000,
)


@app.route("/")
def index():
    return """
<!DOCTYPE html>
<html lang="de">

<head>
    <meta charset="UTF-8">
    <meta name="viewport"
          content="width=device-width, initial-scale=1.0">

    <title>RaspServ</title>

    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f2f2f2;
            margin: 0;
            padding: 20px;
        }

        .container {
            max-width: 500px;
            margin: auto;
        }

        .card {
            background: white;
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 15px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        .value {
            font-size: 26px;
            font-weight: bold;
        }

        .connected {
            color: green;
        }

        .disconnected {
            color: red;
        }
    </style>
</head>

<body>

<div class="container">

    <div class="card">
        <h1>RaspServ</h1>

        RaspCtrl:
        <strong id="connection">
            Lade...
        </strong>
    </div>

    <div class="card">
        Temperatur
        <div class="value" id="temperature">
            -
        </div>
    </div>

    <div class="card">
        Luftfeuchtigkeit
        <div class="value" id="humidity">
            -
        </div>
    </div>

    <div class="card">
        Licht
        <div class="value" id="light">
            -
        </div>
    </div>

    <div class="card">
        Store:
        <strong id="blind">-</strong>
        <br><br>

        Heizung:
        <strong id="heating">-</strong>
        <br><br>

        Kühlung:
        <strong id="cooling">-</strong>
    </div>

</div>


<script>

async function updateStatus() {

    try {

        const response =
            await fetch("/api/status");

        const data =
            await response.json();

        const connection =
            document.getElementById("connection");


        if (data.connected) {

            connection.textContent =
                "Verbunden";

            connection.className =
                "connected";

        } else {

            connection.textContent =
                "Nicht verbunden";

            connection.className =
                "disconnected";
        }


        const status = data.status;


        document.getElementById(
            "temperature"
        ).textContent =
            status.temperature !== undefined
                ? status.temperature + " °C"
                : "-";


        document.getElementById(
            "humidity"
        ).textContent =
            status.humidity !== undefined
                ? status.humidity + " %"
                : "-";


        document.getElementById(
            "light"
        ).textContent =
            status.light !== undefined
                ? status.light
                : "-";


        document.getElementById(
            "blind"
        ).textContent =
            status.blind ?? "-";


        document.getElementById(
            "heating"
        ).textContent =
            status.heating
                ? "Ein"
                : "Aus";


        document.getElementById(
            "cooling"
        ).textContent =
            status.cooling
                ? "Ein"
                : "Aus";

    }
    catch (error) {

        console.error(error);

    }

}


updateStatus();

setInterval(
    updateStatus,
    1000
);

</script>

</body>

</html>
"""


@app.route("/api/status")
def status():

    return jsonify(
        {
            "connected":
                raspctrl_server.is_connected(),

            "status":
                raspctrl_server.get_latest_status(),
        }
    )


def start_tcp_server():

    raspctrl_server.serve_forever()


if __name__ == "__main__":

    tcp_thread = threading.Thread(
        target=start_tcp_server,
        daemon=True,
    )

    tcp_thread.start()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False,
    )