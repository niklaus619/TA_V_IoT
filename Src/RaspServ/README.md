# RaspServ mit Modbus TCP

RaspCtrl verbindet sich mit `RaspServ.home:502` (Unit-ID 1).
Die Webseite bleibt unter `http://RaspServ.home:5000` erreichbar.
Beide Pis brauchen die aktualisierten Dateien; der bisherige JSON-TCP-Client
ist nicht mit diesem Server kompatibel. Bluefruit verwendet weiterhin JSON
ueber USB. Modbus benoetigt keine zusaetzlichen Python-Pakete.

## Installation ohne virtuelle Umgebung

`main.py` ist der gemeinsame Startpunkt: Es initialisiert die Datenbank,
startet Modbus TCP auf Port 502 im Hintergrund und die Webseite auf Port
5000. Alle Komponenten laufen in einem Prozess; keine weiteren Terminals
oder separaten Starts von `server.py` und `app.py` sind notwendig.

Manueller Start auf RaspServ (mit Berechtigung fuer Port 502):

```sh
cd ~/RaspServ/Src/RaspServ
python3 main.py
```

Mit Strg+C werden Webseite und Modbus-Listener beendet. Fuer den Start mit
der benoetigten Portberechtigung und automatischen Start beim Booten den
unten beschriebenen Dienst verwenden. Nicht parallel zum Dienst starten.

Auf RaspServ:

```sh
sudo apt update
sudo apt install python3-flask
cd ~/RaspServ/Src/RaspServ
```

`database.py` muss neben `app.py` liegen. SQLite ist in Python enthalten;
`measurements.db` wird automatisch angelegt. Der Benutzer `pi` muss im
Programmordner schreiben koennen. Eine eventuell aktive venv mit `deactivate`
verlassen. Die requirements.txt ist nur fuer optionale pip-Installationen.

Port 502 benoetigt auf ueblichen Linux-Konfigurationen eine besondere
Bindeberechtigung. Der mitgelieferte systemd-Dienst gibt diese gezielt dem
Prozess, der weiterhin als Benutzer `pi` laeuft. Vor der Installation in
`raspserv.service` Benutzer, Gruppe und beide Pfade anpassen, falls abweichend.
Eine bisher manuell gestartete Instanz zuerst mit Strg+C beenden.

```sh
sudo cp raspserv.service /etc/systemd/system/raspserv.service
sudo systemctl daemon-reload
sudo systemctl enable --now raspserv
sudo systemctl status raspserv
```

Bei einem bereits installierten Dienst nach dem Wechsel auf `main.py` die
Service-Datei erneut kopieren, `sudo systemctl daemon-reload` und
`sudo systemctl restart raspserv` ausfuehren.
Nach weiteren Code-Updates: `sudo systemctl restart raspserv`.
Logs: `journalctl -u raspserv -n 50 --no-pager`.
`python3 main.py` allein hat je nach Linux-Konfiguration keine Berechtigung
fuer Port 502. `server.py` startet nur Modbus ohne Webseite und braucht
dieselbe Berechtigung; nicht gleichzeitig mit dem Dienst starten.

Auf RaspCtrl im Ordner `Src/RaspCtrl`:

```sh
getent hosts RaspServ.home
python3 main.py
```

Der erste Befehl muss die IP des Server-Pis liefern. Bei abweichendem Namen:
`python3 main.py --server-host ANDERER-HOSTNAME`.
RaspCtrl braucht wie bisher pyserial, Bluefruit und das Sense HAT bzw.
`--simulate-sense-hat`. `--serial-port` waehlt den Bluefruit-Datenport.

## Registerbelegung

Alle Adressen sind nullbasiert, alle Register 16 Bit, Big Endian.
Implementiert sind FC03 (Read Holding Registers) und FC16 (Write Multiple
Registers). Andere Funktionscodes liefern Modbus-Exception 01. Die Definition
folgt der [Modbus-Spezifikation](https://www.modbus.org/file/secure/modbusprotocolspecification.pdf).
Schaltzustaende sind Bits bzw. 0/1-Werte in Holding-Registern, keine Coils.

| Adresse | Inhalt | Kodierung |
| --- | --- | --- |
| 0 | Isttemperatur | Vorzeichenbehaftet, Grad C mal 10 |
| 1 | Luftfeuchtigkeit | Prozent mal 10, 0 bis 1000 |
| 2 | Licht | Ganzzahl, 0 bis 65535 |
| 3 | Statusbits | Bit 0: Store geschlossen, Bit 1: Heizung, Bit 2: Kuehlung, Bit 3: Storensteuerung manuell |
| 4 | Aktuelle Solltemperatur | Grad C mal 10, 50 bis 350 |
| 5 | Aktuelle Totzone | Grad C mal 10, 1 bis 65535 |
| 100 / 101 | Revision / neue Solltemperatur | Grad C mal 10 |
| 102 / 103 | Revision / neue Totzone | Grad C mal 10 |
| 104 / 105 | Revision / Storensteuerung | 0 = AUTO, 1 = MANUELL OFFEN, 2 = MANUELL GESCHLOSSEN |
| 106 / 107 | Revision / Klimaanlagenanzeige (Sense HAT) | 0 aus, 1 Regelzustand anzeigen |

RaspCtrl schreibt den gesamten Statusblock 0 bis 5 atomar mit FC16 etwa
einmal pro Sekunde, sobald Sensordaten vorliegen. Jeder akzeptierte Block
wird in SQLite gespeichert. Teilweises Schreiben ist nicht erlaubt.
FC03 kann Teilbereiche innerhalb eines der beiden Bloecke lesen.
Die Befehlsregister werden von der Webseite gesetzt und sind ueber Modbus
nur lesbar. FC16 auf andere Adressen liefert Exception 02; ungueltige Werte
liefern Exception 03, Datenbankfehler Exception 04.
Die Storensteuerung verwendet das Befehlspaar 104/105. Jede Aenderung erhoeht
die Revision, damit RaspCtrl den neuen Befehl beim naechsten Poll erkennt.
Der aktuelle Modus AUTO oder MANUELL wird von RaspCtrl ueber Bit 3 des
Statusregisters 3 an RaspServ zurueckgemeldet.

Die Storen koennen ueber die Webseite automatisch oder manuell gesteuert werden.
Im Modus AUTO bestimmt die lokale Klimaregelung auf RaspCtrl den Storenstatus
anhand von Temperatur und Lichteinfall.

Mit den Webbefehlen OEFFNEN oder SCHLIESSEN wechselt die Storensteuerung
automatisch in den Modus MANUELL. Der manuell gewaehlte Zustand hat Vorrang
vor der autonomen Storenregelung und wird nicht direkt durch diese
ueberschrieben. Heizung und Kuehlung werden auch im manuellen Storenmodus
weiterhin autonom geregelt.

Der Benutzer kann jederzeit wieder auf AUTO wechseln. Zusaetzlich wird der
manuelle Modus beim ersten Regelzyklus nach Mitternacht automatisch beendet,
wodurch die autonome Storenregelung wieder uebernimmt.

Die CPB-NeoPixel zeigen weiterhin ausschliesslich den tatsaechlichen
Storenstatus an: offen = gruen, geschlossen = aus. Sie werden nicht direkt
ueber die Webseite gesteuert, sondern vom CPB bei jedem `set_blind`-Befehl
entsprechend dem Storenstatus gesetzt.

Die Sense-HAT-Bedienung heisst in der Webseite "Klimaanlage". AUS schaltet
die LEDs aus; die Regelung berechnet ihren Zustand im Hintergrund weiter.
EIN zeigt den jeweils aktuellen Zustand: Heizen = rot, Kuehlen = blau,
Aus = dunkel. Auch nach einem Zustandswechsel waehrend AUS wird beim
Einschalten sofort der aktuelle Zustand angezeigt. Beim Programmstart ist
die Anzeige freigegeben. Die Modbus-Register 106/107 fuer die
Klimaanlagenanzeige bleiben unveraendert.

RaspCtrl fragt alle 250 ms den Befehlsblock ab. Revision 0 bedeutet kein
Befehl; neue Revisionen werden einmal angewendet, nach einer Neuverbindung
erneut. Mehrere schnelle Aenderungen desselben Parameters werden auf den
neuesten Sollwert zusammengefasst. Nach Serverneustart sind Befehle leer;
RaspCtrl behaelt seine aktuellen Einstellungen. Eine erfolgreiche Webantwort
bestaetigt die Bereitstellung, nicht die Ausfuehrung am Aktor.
Die Statusanzeige uebernimmt anschliessend die von RaspCtrl gemeldeten Werte.

Nach 5 Sekunden ohne gueltigen Befehlspoll oder Status gilt die Verbindung
als getrennt. Wiederverbindungsversuche erfolgen alle 5 Sekunden.
Netzwerkzugriffe laufen in einem Hintergrundthread und blockieren die lokale
Regelung nicht. Die Register bieten eine Aufloesung von 0.1 Grad / Prozent.

## Pruefung

Auf RaspServ: `ss -ltn | grep ':502'` muss einen Listener zeigen.
Auf RaspCtrl muessen die Logs `Mit Modbus-Server RaspServ.home:502 verbunden`
melden. Beide Geraete muessen Port 502 erreichen koennen.
Die lokalen Integrationstests laufen vom Repository-Hauptordner mit:

```sh
python3 -m unittest discover -s tests -v
```
