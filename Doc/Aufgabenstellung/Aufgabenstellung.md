# Aufgabenstellung – Intelligente IoT-Raumklimasteuerung

Im Projekt soll eine intelligente **IoT-Raumklimasteuerung** entwickelt werden. Das System besteht aus einem **Adafruit Circuit Playground Bluefruit**, einem **Raspberry Pi 1 mit Sense HAT V2** sowie einem **Raspberry Pi 2** zur Visualisierung.

## Adafruit Circuit Playground Bluefruit

Das **Adafruit Circuit Playground Bluefruit** dient als dezentrale Sensor- und Aktoreinheit und wird mit **MicroPython** programmiert.

Es übernimmt folgende Aufgaben:

- Erfassung der **Raumtemperatur**
- Erfassung der **Lichteinstrahlung**
- symbolische Ansteuerung der **Store**
- Darstellung des Storen-Ausgangs über die integrierte **D13-LED**

Das Adafruit kommuniziert bidirektional über **Bluetooth Low Energy (BLE)** mit Raspberry Pi 1. Dabei werden Messwerte an Raspberry Pi 1 übertragen und Stellbefehle für die Store zurück an das Adafruit gesendet.

## Raspberry Pi 1 – Zentrale Steuerung und Datenspeicherung

**Raspberry Pi 1** bildet die zentrale Steuerungs- und Servereinheit des Systems.

Auf Raspberry Pi 1 werden:

- die Messwerte des Adafruit über Bluetooth empfangen,
- die Raumklima-Regellogik ausgeführt,
- Mess- und Betriebsdaten in einer **SQL-Datenbank** gespeichert,
- Stellbefehle über Bluetooth an das Adafruit zurückgesendet.

Zusätzlich ist Raspberry Pi 1 mit einem **Sense HAT V2** ausgestattet. Dieses übernimmt:

- die Messung der **Luftfeuchtigkeit**
- die Visualisierung des Heiz- und Kühlzustands über die **8×8-LED-Matrix**

Die LED-Matrix zeigt den aktuellen Betriebszustand an:

- **Rot:** Heizung aktiv
- **Blau:** Kühlung aktiv

## Raumklimaregelung

Die Regelung berücksichtigt die **Raumtemperatur**, die **Lichteinstrahlung** und die **Luftfeuchtigkeit**.

Ist der Raum zu warm und gleichzeitig genügend Sonneneinstrahlung vorhanden, wird zuerst die **Store geschlossen**, um eine weitere Erwärmung durch die Sonne zu reduzieren. Reicht diese passive Massnahme nicht aus, wird die **Kühlung aktiviert**.

Ist der Raum zu kalt und Tageslicht vorhanden, wird zuerst die **Store geöffnet**, damit die Sonneneinstrahlung zur Erwärmung des Raumes genutzt werden kann. Erst wenn diese Massnahme nicht ausreicht oder kein nutzbares Tageslicht vorhanden ist, wird die **Heizung aktiviert**.

Damit werden passive Massnahmen priorisiert und aktives Heizen oder Kühlen erst eingesetzt, wenn diese nicht ausreichen.

## Raspberry Pi 2 – Visualisierung

**Raspberry Pi 2** dient als Bedien- und Visualisierungseinheit. Er kommuniziert über **TCP/IP im WLAN** mit Raspberry Pi 1.

Die Visualisierung wird mit **Flask** umgesetzt und zeigt:

- aktuelle Temperatur
- aktuelle Lichteinstrahlung
- aktuelle Luftfeuchtigkeit
- aktuellen Heiz- und Kühlzustand
- aktuellen Storenstatus
- historische Messwerte aus der SQL-Datenbank
- einstellbare Sollwerte und Regelparameter

Über die Visualisierung können Daten von Raspberry Pi 1 abgerufen und Bedien- beziehungsweise Parametrierbefehle zurück an Raspberry Pi 1 übertragen werden.

## Datenfluss

Der grundlegende Datenfluss des Systems lautet:

**Adafruit Circuit Playground Bluefruit ⇄ Bluetooth Low Energy ⇄ Raspberry Pi 1 ⇄ TCP/IP / WLAN ⇄ Raspberry Pi 2**

Dabei übernimmt:

- **Adafruit:** Temperatur, Licht und Storen-Ausgang
- **Raspberry Pi 1:** Regelung, SQL-Datenbank, Feuchtigkeitsmessung sowie Heiz-/Kühlanzeige über Sense HAT V2
- **Raspberry Pi 2:** Flask-Visualisierung, aktuelle Werte, Historisierung und Bedienung
