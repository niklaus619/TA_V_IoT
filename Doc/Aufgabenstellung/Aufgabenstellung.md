# Aufgabenstellung – Intelligente IoT-Raumklimasteuerung

Im Projekt wird eine intelligente **IoT-Raumklimasteuerung** entwickelt. Das System besteht aus einem **Adafruit Circuit Playground Bluefruit (CPB)**, einem **Raspberry Pi 1 mit Sense HAT V2** und einem **Raspberry Pi 2 als IoT-Server**.

## Circuit Playground Bluefruit

Das CPB dient als dezentrale Sensor- und Aktoreinheit und wird mit **MicroPython** programmiert.

Aufgaben:

- Raumtemperatur messen
- Lichteinstrahlung messen
- Store symbolisch ansteuern
- Storenstatus über D13-LED anzeigen
- NeoPixel ansteuern

Die Kommunikation mit Raspberry Pi 1 erfolgt bidirektional über **Bluetooth Low Energy (BLE)**.

## Raspberry Pi 1 – Steuerung

Raspberry Pi 1 übernimmt die zentrale Steuerungslogik:

- Messwerte des CPB über BLE empfangen
- Luftfeuchtigkeit über Sense HAT V2 messen
- Raumklimaregelung ausführen
- Storen-, Heiz- und Kühlbefehle berechnen
- Stellbefehle an das CPB senden
- Heiz-/Kühlzustand über die Sense-HAT-LED-Matrix darstellen
- Daten und Zustände an Raspberry Pi 2 übertragen
- Sollwerte und Bedienbefehle von Raspberry Pi 2 empfangen

Die Regelung funktioniert unabhängig von Raspberry Pi 2.

## Raumklimaregelung

Bei zu hoher Raumtemperatur und hoher Sonneneinstrahlung wird zuerst die **Store geschlossen**. Reicht diese passive Massnahme nicht aus, wird die **Kühlung aktiviert**.

Bei zu tiefer Raumtemperatur und vorhandenem Tageslicht wird zuerst die **Store geöffnet**. Reicht die solare Erwärmung nicht aus oder ist kein Tageslicht vorhanden, wird die **Heizung aktiviert**.

Die Sense-HAT-Matrix zeigt:

- **Rot:** Heizung aktiv
- **Blau:** Kühlung aktiv
- **Aus:** Normalbetrieb

## Raspberry Pi 2 – IoT-Server, SQL und Visualisierung

Raspberry Pi 2 übernimmt:

- Flask-Webserver
- SQL-Datenbank
- Historisierung der Messwerte
- Darstellung aktueller Werte und Zeitreihen
- Anzeige von Storen-, Heiz- und Kühlzustand
- Parametrierung von Sollwerten und Regelparametern
- Fernsteuerung der CPB-NeoPixel
- Fernsteuerung der Sense-HAT-LED-Matrix

Die Kommunikation mit Raspberry Pi 1 erfolgt über **TCP/IP im WLAN oder Ethernet**.

## Datenfluss

**CPB ⇄ BLE ⇄ Raspberry Pi 1 ⇄ TCP/IP ⇄ Raspberry Pi 2 ⇄ Browser**

Dabei gilt:

- **CPB:** Temperatur, Licht, Store, NeoPixel
- **Raspberry Pi 1:** Steuerung, Regelung, Sense HAT V2
- **Raspberry Pi 2:** IoT-Server, SQL-Datenbank, Historisierung und Visualisierung