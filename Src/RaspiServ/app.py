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
        * {
            box-sizing: border-box;
        }

        body {
            font-family: Arial, sans-serif;
            background: #0f172a;
            color: #e2e8f0;
            margin: 0;
            padding: 20px;
        }

        .container {
            max-width: 1400px;
            margin: auto;

            display: grid;
            grid-template-columns:
                repeat(auto-fit, minmax(260px, 1fr));

            gap: 16px;
        }

        .card {
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 14px;
            padding: 20px;
            box-shadow: 0 4px 14px rgba(0, 0, 0, 0.25);
        }

        .card h1,
        .card h2 {
            margin-top: 0;
        }

        .value {
            font-size: 26px;
            font-weight: bold;
            color: #f8fafc;
            margin-top: 8px;
        }

        button {
            background: #334155;
            color: #f8fafc;
            border: 1px solid #475569;
            border-radius: 8px;
            padding: 10px 16px;
            font-size: 15px;
            cursor: pointer;
            transition: 0.2s;
        }

        button:hover {
            background: #475569;
            transform: translateY(-1px);
        }

        button:active {
            transform: translateY(0);
        }

        .connected {
            color: #4ade80;
        }

        .disconnected {
            color: #f87171;
        }

        @media (max-width: 600px) {
            body {
                padding: 10px;
            }

            .container {
                grid-template-columns: 1fr;
            }

            .card {
                padding: 16px;
            }
        }
        .charts-section {
    grid-column: 1 / -1;
    margin-top: 5px;
}

        .charts-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 20px;
            margin-bottom: 16px;
        }

        .charts-header h2 {
            margin: 0;
            font-size: 26px;
        }

        .subtitle {
            margin: 5px 0 0 0;
            color: #94a3b8;
        }

        .range-selector {
            display: flex;
            align-items: center;
            gap: 10px;
            flex-wrap: wrap;
        }

        .range-selector span {
            color: #94a3b8;
            font-weight: bold;
        }

        .charts-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 16px;
        }

        .chart-card {
            min-width: 0;
        }

        .chart-container {
            position: relative;
            height: 300px;
            width: 100%;
        }


        /* Tablet */
        @media (max-width: 1100px) {
            .charts-grid {
                grid-template-columns: 1fr;
            }
        }


        /* Smartphone */
        @media (max-width: 600px) {
            .charts-header {
                flex-direction: column;
                align-items: flex-start;
            }

            .chart-container {
                height: 250px;
            }
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
    <h2>CPB NeoPixel</h2>

    <div style="display:flex; gap:10px;">
        <button onclick="setCpbNeopixel(true)">
            EIN
        </button>

        <button onclick="setCpbNeopixel(false)">
            AUS
        </button>
    </div>

    <p id="cpbNeopixelResult"></p>
</div>

<div class="card">
    <h2>Sense HAT NeoPixel</h2>

    <div style="display:flex; gap:10px;">
        <button onclick="setSenseNeopixel(true)">
            EIN
        </button>

        <button onclick="setSenseNeopixel(false)">
            AUS
        </button>
    </div>

    <p id="senseNeopixelResult"></p>
</div>

<div class="charts-section">

    <div class="charts-header">
        <div>
            <h2>Messwertverlauf</h2>
            <p class="subtitle">
                Historische Sensordaten
            </p>
        </div>

        <div class="range-selector">
            <span>Zeitraum:</span>

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


    <div class="charts-grid">

        <div class="card chart-card">
            <h2>Temperatur</h2>

            <div class="chart-container">
                <canvas id="temperatureChart"></canvas>
            </div>
        </div>


        <div class="card chart-card">
            <h2>Luftfeuchtigkeit</h2>

            <div class="chart-container">
                <canvas id="humidityChart"></canvas>
            </div>
        </div>


        <div class="card chart-card">
            <h2>Licht</h2>

            <div class="chart-container">
                <canvas id="lightChart"></canvas>
            </div>
        </div>

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

async function setCpbNeopixel(on) {

    const result =
        document.getElementById(
            "cpbNeopixelResult"
        );

    try {

        const response = await fetch(
            "/api/cpb-neopixel",
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    on: on
                })
            }
        );

        const data =
            await response.json();

        if (response.ok && data.ok) {

            result.textContent =
                on
                    ? "NeoPixel eingeschaltet."
                    : "NeoPixel ausgeschaltet.";

        } else {

            result.textContent =
                data.error ||
                "Fehler beim Schalten.";

        }

    }
    catch (error) {

        result.textContent =
            "Fehler bei der Verbindung.";

        console.error(error);

    }
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
                        tension: 0.2,
                        pointRadius: 0,
                        pointHoverRadius: 4,
                        borderWidth: 2
                    }
                ]
            },

            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: false,

                interaction: {
                    mode: "index",
                    intersect: false
                },

                plugins: {
                    tooltip: {
                        enabled: true
                    }
                },

                scales: {
                    x: {
                        ticks: {
                            autoSkip: true,
                            maxTicksLimit: 6,
                            maxRotation: 0,
                            minRotation: 0
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
                        tension: 0.2,
                        pointRadius: 0,
                        pointHoverRadius: 4,
                        borderWidth: 2
                    }
                ]
            },

            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: false,

                interaction: {
                    mode: "index",
                    intersect: false
                },

                plugins: {
                    tooltip: {
                        enabled: true
                    }
                },

                scales: {
                    x: {
                        ticks: {
                            autoSkip: true,
                            maxTicksLimit: 6,
                            maxRotation: 0,
                            minRotation: 0
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
                        tension: 0.2,
                        pointRadius: 0,
                        pointHoverRadius: 4,
                        borderWidth: 2

                    }
                ]
            },

            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: false,

                interaction: {
                    mode: "index",
                    intersect: false
             },

            plugins: {
                tooltip: {
                    enabled: true
                }
            },

            scales: {
                x: {
                    ticks: {
                        autoSkip: true,
                        maxTicksLimit: 6,
                        maxRotation: 0,
                        minRotation: 0
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

async function setSenseNeopixel(on) {

    const result =
        document.getElementById(
            "senseNeopixelResult"
        );

    try {

        const response = await fetch(
            "/api/sense-neopixel",
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    on: on
                })
            }
        );

        const data =
            await response.json();

        if (response.ok && data.ok) {

            result.textContent =
                on
                    ? "Sense HAT eingeschaltet."
                    : "Sense HAT ausgeschaltet.";

        } else {

            result.textContent =
                data.error ||
                "Fehler beim Schalten.";

        }

    }
    catch (error) {

        result.textContent =
            "Fehler bei der Verbindung.";

        console.error(error);

    }
}

Chart.defaults.color = "#cbd5e1";
Chart.defaults.borderColor = "#334155";

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

@app.route("/api/cpb-neopixel", methods=["POST"])
def set_cpb_neopixel():
    data = request.get_json(silent=True) or {}

    on = data.get("on")

    # Der Zustand muss eindeutig als true oder false uebertragen werden.
    if not isinstance(on, bool):
        return jsonify({
            "ok": False,
            "error": "on muss true oder false sein"
        }), 400

    try:
        raspctrl_server.send_command({
            "type": "set_cpb_neopixel",
            "on": on,
        })

    except ConnectionError:
        return jsonify({
            "ok": False,
            "error": "RaspCtrl ist nicht verbunden"
        }), 503

    return jsonify({
        "ok": True,
        "on": on,
    })

@app.route("/api/sense-neopixel", methods=["POST"])
def set_sense_neopixel():
    data = request.get_json(silent=True) or {}

    on = data.get("on")

    # Der Zustand muss eindeutig als true oder false uebertragen werden.
    if not isinstance(on, bool):
        return jsonify({
            "ok": False,
            "error": "on muss true oder false sein"
        }), 400

    try:
        raspctrl_server.send_command({
            "type": "set_sense_neopixel",
            "on": on,
        })

    except ConnectionError:
        return jsonify({
            "ok": False,
            "error": "RaspCtrl ist nicht verbunden"
        }), 503

    return jsonify({
        "ok": True,
        "on": on,
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