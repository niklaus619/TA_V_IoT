import threading

from flask import Flask, jsonify, request

from server import RaspCtrlServer
from database import (
    initialize_database,
    get_measurements,
    get_measurements_since,
)


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
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
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

    <div class="card">
    <h2>Solltemperatur</h2>

    <div style="display:flex; align-items:center; gap:15px;">
        <button onclick="changeTemperature(-0.5)">−</button>

        <span id="targetTemperature" class="value">
            22.0 °C
        </span>

        <button onclick="changeTemperature(0.5)">+</button>
    </div>

    <br>

    <button onclick="sendTargetTemperature()">
        Übernehmen
    </button>

    <p id="commandResult"></p>
    </div>

    <div class="card">
    <h2>Totzone</h2>

    <div style="display:flex; align-items:center; gap:15px;">
        <button onclick="changeDeadband(-0.1)">−</button>

        <span id="temperatureDeadband" class="value">
            0.5 °C
        </span>

        <button onclick="changeDeadband(0.1)">+</button>
    </div>

    <br>

    <button onclick="sendDeadband()">
        Übernehmen
    </button>

    <p id="deadbandResult"></p>
</div>

<div class="card">
    <h2>Zeitraum</h2>

    <div style="display:flex; gap:10px; flex-wrap:wrap;">

        <button onclick="setHistoryRange(5)">
            5 Minuten
        </button>

        <button onclick="setHistoryRange(30)">
            30 Minuten
        </button>

        <button onclick="setHistoryRange(60)">
            1 Stunde
        </button>

    </div>
</div>

<div class="card">
    <h2>Temperaturverlauf</h2>
    <canvas id="temperatureChart"></canvas>
</div>

<div class="card">
    <h2>Luftfeuchtigkeit</h2>
    <canvas id="humidityChart"></canvas>
</div>

<div class="card">
    <h2>Lichtverlauf</h2>
    <canvas id="lightChart"></canvas>
</div>

</div>


<script>

let targetTemperature = 22.0;
let targetTemperatureDirty = false;
let temperatureDeadband = 0.5;
let temperatureDeadbandDirty = false;
let temperatureChart;
let humidityChart;
let lightChart;
let historyMinutes = 5;

function setHistoryRange(minutes) {

    historyMinutes = minutes;

    updateHistory();
}

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


        // Aktuellen Sollwert von RaspCtrl übernehmen
        if (
            status.target_temperature !== undefined &&
            !targetTemperatureDirty
        ) {

            targetTemperature =
                Number(status.target_temperature);

            document.getElementById(
                "targetTemperature"
            ).textContent =
                targetTemperature.toFixed(1) + " °C";
        }
        if (
            status.temperature_deadband !== undefined &&
            !temperatureDeadbandDirty
        ) {
            temperatureDeadband =
                Number(status.temperature_deadband);

            document.getElementById(
             "temperatureDeadband"
            ).textContent =
                temperatureDeadband.toFixed(1) + " °C";
        }

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


function changeTemperature(change) {

    targetTemperature += change;

    // Benutzer bearbeitet den Wert gerade
    targetTemperatureDirty = true;


    if (targetTemperature < 5) {
        targetTemperature = 5;
    }

    if (targetTemperature > 35) {
        targetTemperature = 35;
    }


    document.getElementById(
        "targetTemperature"
    ).textContent =
        targetTemperature.toFixed(1) + " °C";
}


async function sendTargetTemperature() {

    const result =
        document.getElementById(
            "commandResult"
        );


    try {

        const response = await fetch(
            "/api/target-temperature",
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    target_temperature:
                        targetTemperature
                })
            }
        );


        const data =
            await response.json();


        if (data.ok) {

            targetTemperature =
                Number(data.target_temperature);

            // Ab jetzt wieder echten Wert von RaspCtrl übernehmen
            targetTemperatureDirty = false;

            result.textContent =
                "Solltemperatur auf " +
                data.target_temperature +
                " °C gesetzt.";

        } else {

            result.textContent =
                data.error;
        }

    }
    catch (error) {

        result.textContent =
            "Fehler beim Senden.";

        console.error(error);
    }
}

    function changeDeadband(change) {

        temperatureDeadband += change;
        temperatureDeadbandDirty = true;

        if (temperatureDeadband < 0.1) {
            temperatureDeadband = 0.1;
        }

        temperatureDeadband =
            Math.round(temperatureDeadband * 10) / 10;

        document.getElementById(
            "temperatureDeadband"
        ).textContent =
            temperatureDeadband.toFixed(1) + " °C";
    }


    async function sendDeadband() {

        const result =
            document.getElementById(
                "deadbandResult"
            );

        try {

            const response = await fetch(
                "/api/temperature-deadband",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        temperature_deadband:
                            temperatureDeadband
                    })
                }
            );

            const data =
                await response.json();

            if (data.ok) {

                temperatureDeadband =
                    Number(data.temperature_deadband);

                temperatureDeadbandDirty = false;

                result.textContent =
                    "Totzone auf " +
                    data.temperature_deadband +
                    " °C gesetzt.";

            } else {

                result.textContent =
                    data.error;
            }

        } catch (error) {

            result.textContent =
                "Fehler beim Senden.";

            console.error(error);
        }
    }
function createCharts() {

    temperatureChart = new Chart(
        document.getElementById("temperatureChart"),
        {
            type: "line",

            data: {
                labels: [],
                datasets: [
                    {
                        label: "Temperatur °C",
                        data: [],
                        tension: 0.2
                    }
                ]
            },

            options: {
                responsive: true,
                animation: false,

                scales: {
                    x: {
                        ticks: {
                            maxTicksLimit: 8
                        }
                    }
                }
            }
        }
    );


    humidityChart = new Chart(
        document.getElementById("humidityChart"),
        {
            type: "line",

            data: {
                labels: [],
                datasets: [
                    {
                        label: "Luftfeuchtigkeit %",
                        data: [],
                        tension: 0.2
                    }
                ]
            },

            options: {
                responsive: true,
                animation: false,

                scales: {
                    x: {
                        ticks: {
                            maxTicksLimit: 8
                        }
                    }
                }
            }
        }
    );


    lightChart = new Chart(
        document.getElementById("lightChart"),
        {
            type: "line",

            data: {
                labels: [],
                datasets: [
                    {
                        label: "Licht",
                        data: [],
                        tension: 0.2
                    }
                ]
            },

            options: {
                responsive: true,
                animation: false,

                scales: {
                    x: {
                        ticks: {
                            maxTicksLimit: 8
                        }
                    }
                }
            }
        }
    );
}

async function updateHistory() {

    try {

        const response =
            await fetch(
                "/api/history?minutes=" +
                historyMinutes
        );

        const measurements =
            await response.json();


        const labels =
            measurements.map(item => {

                const date =
                    new Date(
                        item.timestamp
                            .replace(" ", "T") + "Z"
                    );

                return date.toLocaleTimeString(
                    "de-CH",
                    {
                        hour: "2-digit",
                        minute: "2-digit",
                        second: "2-digit"
                    }
                );
            });


        const temperatures =
            measurements.map(
                item => item.temperature
            );


        const humidities =
            measurements.map(
                item => item.humidity
            );


        const lights =
            measurements.map(
                item => item.light
            );


        temperatureChart.data.labels =
            labels;

        temperatureChart.data.datasets[0].data =
            temperatures;

        temperatureChart.update();


        humidityChart.data.labels =
            labels;

        humidityChart.data.datasets[0].data =
            humidities;

        humidityChart.update();


        lightChart.data.labels =
            labels;

        lightChart.data.datasets[0].data =
            lights;

        lightChart.update();

    }
    catch (error) {

        console.error(
            "Fehler beim Laden der Historie:",
            error
        );
    }
}


createCharts();

updateStatus();
updateHistory();


setInterval(
    updateStatus,
    1000
);


setInterval(
    updateHistory,
    5000
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

@app.route("/api/history")
def history():

    try:
        minutes = int(
            request.args.get(
                "minutes",
                5
            )
        )
    except ValueError:
        minutes = 5

    allowed_minutes = {
        5,
        30,
        60,
    }

    if minutes not in allowed_minutes:
        minutes = 5

    measurements = get_measurements_since(minutes)

    return jsonify(measurements)

@app.route("/api/target-temperature", methods=["POST"])
def set_target_temperature():
    data = request.get_json(silent=True) or {}
    try:
        target_temperature = float(data["target_temperature"])
    except (KeyError, TypeError, ValueError):
        return jsonify({
            "ok": False,
            "error": "Ungueltige Solltemperatur"
        }), 400

    if not 5.0 <= target_temperature <= 35.0:
        return jsonify({
            "ok": False,
            "error": "Solltemperatur muss zwischen 5 und 35 Grad liegen"
        }), 400

    try:
        raspctrl_server.send_command({
            "type": "set_parameters",
            "target_temperature": target_temperature,
        })
    except ConnectionError:
        return jsonify({
            "ok": False,
            "error": "RaspCtrl ist nicht verbunden"
        }), 503

    return jsonify({
        "ok": True,
        "target_temperature": target_temperature,
    })

@app.route("/api/temperature-deadband", methods=["POST"])
def set_temperature_deadband():
    data = request.get_json(silent=True) or {}

    try:
        temperature_deadband = float(
            data["temperature_deadband"]
        )
    except (KeyError, TypeError, ValueError):
        return jsonify({
            "ok": False,
            "error": "Ungueltige Totzone"
        }), 400

    if temperature_deadband <= 0:
        return jsonify({
            "ok": False,
            "error": "Totzone muss groesser als 0 sein"
        }), 400

    try:
        raspctrl_server.send_command({
            "type": "set_parameters",
            "temperature_deadband": temperature_deadband,
        })
    except ConnectionError:
        return jsonify({
            "ok": False,
            "error": "RaspCtrl ist nicht verbunden"
        }), 503

    return jsonify({
        "ok": True,
        "temperature_deadband": temperature_deadband,
    })   

def start_tcp_server():

    raspctrl_server.serve_forever()



if __name__ == "__main__":

    initialize_database()

    tcp_thread = threading.Thread(
        target=start_tcp_server,
        daemon=True,
    )

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