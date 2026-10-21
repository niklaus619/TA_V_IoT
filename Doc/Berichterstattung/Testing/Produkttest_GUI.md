# Produkttest – Bedienung über das GUI

| Prüfdaten | Eintrag |
|---|---|
| Softwarestand | `main` auf GitHub, Commit `ab006e80187dece41007d8089a19b4b787b2f7ce` |
| GUI | `http://RaspServ.home:5000` |
| Prüfdatum | __________ |
| Prüfperson | __________ |
| Anfängliche Solltemperatur | __________ °C |
| Anfängliche Totzone | __________ °C |
| Checkbox | Abhaken nach erfolgreicher Prüfung von Bedienung und Wirkung |

## Voraussetzungen

- [ ] RaspServ, RaspCtrl und Bluefruit eingeschaltet; Software gestartet.
- [ ] Bluefruit mit RaspCtrl verbunden; Sense HAT vorhanden; Hardwarebetrieb ohne Simulation.
- [ ] GUI zeigt RaspCtrl als **Verbunden**; aktuelle Sensordaten vorhanden.
- [ ] Chart.js für die Darstellung der Diagramme geladen.

| Testbedingung | Vorgabe |
|---|---|
| `T` | Aktuell angezeigte Isttemperatur |
| `S` | Übernommene Solltemperatur |
| `D` | Übernommene Totzone; für Regeltests **0,5 °C** |
| Neutraler Zustand | `S − D ≤ T ≤ S + D` |
| Kühlanforderung | `T > S + D`; Solltemperatur mindestens 1 °C unter `T` wählen |
| Heizanforderung | `T < S − D`; Solltemperatur mindestens 1 °C über `T` wählen |
| Sollwerte für Regeltests | Innerhalb **5–35 °C**; Bedingungen während der Prüfung beibehalten |
| Hell / dunkel | Lichtwert **≥ 100** / **< 100**; Standardkonfiguration |
| Passive Wartezeit | Bei Helligkeit **120 s** ab Eintritt in Heiz- oder Kühlmodus; Standardkonfiguration |
| Beginn eines Wartezeittests | Zuerst neutralen Zustand einstellen und Status **Heizung: Aus / Kühlung: Aus** abwarten |
| Aktualisierung | Statusanzeige ca. **1 s**; Diagramme ca. **5 s**; Rückmeldung und Hardwarewirkung abwarten |
| Historienprüfung | Gespeicherte Messwerte aus den zu prüfenden Zeiträumen; ohne Messwerte bleibt der jeweilige Verlauf leer |

## 1. Übersicht und Messwerte

- [ ] **A01 – GUI öffnen** → Verbindungsanzeige **Verbunden**, grün.
- [ ] **A02 – Messwertkarten prüfen** → Temperatur in **°C**, Luftfeuchtigkeit in **%**, Licht als Zahlenwert.
- [ ] **A03 – Zustandsanzeigen prüfen** → Store als **open/closed**; Heizung und Kühlung als **Ein/Aus**; Storenmodus als **AUTO/MANUELL**.

## 2. Solltemperatur

- [ ] **S01 – Solltemperatur: `+` drücken** → Angezeigter Wert steigt um **0,5 °C**.
- [ ] **S02 – Solltemperatur: `−` drücken** → Angezeigter Wert sinkt um **0,5 °C**.
- [ ] **S03 – Bei 5,0 °C erneut `−` drücken** → Anzeige bleibt bei **5,0 °C**.
- [ ] **S04 – Bei 35,0 °C erneut `+` drücken** → Anzeige bleibt bei **35,0 °C**.
- [ ] **S05 – Wert ändern; ohne `Übernehmen` mindestens 3 s warten** → Entwurf bleibt angezeigt; bisheriger Sollwert bleibt für die Regelung wirksam.
- [ ] **S06 – Solltemperatur: `Übernehmen` drücken** → Meldung **Solltemperatur auf … °C gesetzt.**; Regelung übernimmt den neuen Sollwert.
- [ ] **S07 – Nach bestätigter Rückmeldung von RaspCtrl die Seite neu laden** → Übernommene Solltemperatur wird wieder angezeigt.

## 3. Totzone

- [ ] **T01 – Totzone: `+` drücken** → Angezeigter Wert steigt um **0,1 °C**.
- [ ] **T02 – Totzone: `−` drücken** → Angezeigter Wert sinkt um **0,1 °C**.
- [ ] **T03 – Bei 0,1 °C erneut `−` drücken** → Anzeige bleibt bei **0,1 °C**.
- [ ] **T04 – Wert ändern; ohne `Übernehmen` mindestens 3 s warten** → Entwurf bleibt angezeigt; bisherige Totzone bleibt für die Regelung wirksam.
- [ ] **T05 – Totzone: `Übernehmen` drücken** → Meldung **Totzone auf … °C gesetzt.**; Regelung übernimmt die neue Totzone.
- [ ] **T06 – Nach bestätigter Rückmeldung von RaspCtrl die Seite neu laden** → Übernommene Totzone wird wieder angezeigt.
- [ ] **T07 – Bei gleichbleibender Temperatur die Totzone so vergrössern und übernehmen, dass `T` im neutralen Bereich liegt** → **Heizung: Aus**, **Kühlung: Aus**; Sense-HAT-Matrix dunkel.
- [ ] **T08 – Totzone auf 0,5 °C und Solltemperatur möglichst nahe an `T` stellen; jeweils `Übernehmen` drücken** → Neutraler Ausgangszustand für die folgenden Regeltests.

## 4. Storensteuerung

- [ ] **B01 – `ÖFFNEN` drücken** → Modus **MANUELL**; Store **open**; NeoPixel am Bluefruit **grün**; Meldung **Store manuell geöffnet.**
- [ ] **B02 – `SCHLIESSEN` drücken** → Modus **MANUELL**; Store **closed**; NeoPixel am Bluefruit **aus**; Meldung **Store manuell geschlossen.**
- [ ] **B03 – Bei Helligkeit: `ÖFFNEN` drücken; Kühlanforderung über Solltemperatur einstellen und übernehmen** → Store bleibt **open**, Modus **MANUELL**, Bluefruit **grün**; Kühlung wird nach der passiven Wartezeit **Ein**.
- [ ] **B04 – Bei fortbestehender Kühlanforderung und Helligkeit: `AUTO` drücken** → Modus **AUTO**; Store **closed**; Bluefruit-NeoPixel **aus**; Meldung **Storensteuerung auf AUTO gesetzt.**
- [ ] **B05 – Bei Helligkeit und Modus AUTO: Heizanforderung über Solltemperatur einstellen und übernehmen** → Store **open**; Bluefruit-NeoPixel **grün**; Heizung wird nach der passiven Wartezeit **Ein**.

## 5. Klimaanlage / Sense-HAT-Anzeige

- [ ] **K01 – Solltemperatur in den neutralen Bereich stellen und übernehmen; `EIN` drücken** → Sense-HAT-Matrix bleibt **dunkel**; **Heizung: Aus**, **Kühlung: Aus**; Meldung **Klimaanlage eingeschaltet.**
- [ ] **K02 – Aus neutralem Zustand Kühlanforderung über Solltemperatur einstellen und übernehmen** → Bei Helligkeit zunächst **Kühlung: Aus**, Matrix **dunkel**; nach **120 s** **Kühlung: Ein**, Matrix **blau**. Bei Dunkelheit: Kühlung ohne passive Wartezeit **Ein**, Matrix **blau**.
- [ ] **K03 – Bei aktiver Kühlung: `AUS` drücken** → Sense-HAT-Matrix **dunkel**; GUI weiterhin **Kühlung: Ein**; Meldung **Klimaanlage ausgeschaltet.**
- [ ] **K04 – Bei weiterhin aktiver Kühlung: `EIN` drücken** → Sense-HAT-Matrix wieder **blau**.
- [ ] **K05 – `AUS` drücken; Heizanforderung über Solltemperatur einstellen und übernehmen** → Nach erforderlicher Wartezeit **Heizung: Ein**, **Kühlung: Aus**; Matrix bleibt **dunkel**.
- [ ] **K06 – Bei aktiver Heizung: `EIN` drücken** → Sense-HAT-Matrix **rot**.
- [ ] **K07 – Solltemperatur in den neutralen Bereich stellen und übernehmen** → **Heizung: Aus**, **Kühlung: Aus**; Matrix **dunkel** trotz freigegebener Anzeige.

## 6. Messwertverlauf

- [ ] **H01 – `5 Minuten` drücken** → Alle drei Diagramme zeigen gespeicherte Werte der letzten **5 Minuten**.
- [ ] **H02 – `1 Stunde` drücken** → Alle drei Diagramme zeigen gespeicherte Werte der letzten **60 Minuten**.
- [ ] **H03 – `1 Tag` drücken** → Alle drei Diagramme zeigen gespeicherte Werte der letzten **24 Stunden**.
- [ ] **H04 – `3 Tage` drücken** → Alle drei Diagramme zeigen gespeicherte Werte der letzten **72 Stunden**.
- [ ] **H05 – Bei laufender Messwerterfassung mindestens 10 s warten** → Temperatur-, Luftfeuchtigkeits- und Lichtdiagramm werden automatisch um neue Messpunkte ergänzt.
- [ ] **H06 – Mauszeiger über einen Messpunkt bewegen** → Tooltip zeigt den zugehörigen Messwert; Zeitangabe an der Zeitachse bzw. im Tooltip.
- [ ] **H07 – Seite neu laden** → Gespeicherte Messwerte bleiben verfügbar; ausgewählter Zeitraum steht wieder auf **5 Minuten**.

## 7. Abschluss

- [ ] **E01 – Anfängliche Solltemperatur und Totzone einstellen und jeweils `Übernehmen` drücken** → Ausgangswerte wieder wirksam.
- [ ] **E02 – Storensteuerung: `AUTO` drücken** → Modus **AUTO**.
- [ ] **E03 – Klimaanlage: `EIN` drücken** → Sense-HAT-Matrix zeigt den aktuellen Regelzustand: **rot / blau / dunkel**.

## Abweichungen

| Test-ID | Beobachtete Wirkung / Fehler | Nachprüfung |
|---|---|---|
| | | |
| | | |
| | | |
