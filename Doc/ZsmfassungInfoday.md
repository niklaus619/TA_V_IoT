# Infoabend: Technische Arbeit IoT

## Projektidee

Im Rahmen dieser technischen Arbeit entwickeln die Studierenden des ersten Schuljahres ein praxisorientiertes IoT-System. Als technische Grundlage dienen **MicroPython**, ein geeigneter Mikrocontroller und elektronische Komponenten von **Adafruit**.

Die Studierenden planen und realisieren das System, erfassen und verarbeiten Sensordaten, steuern elektronische Bauteile an und prüfen die korrekte Zusammenarbeit von Hard- und Software. Neben der technischen Umsetzung gehören eine nachvollziehbare Dokumentation und eine adressatengerechte Präsentation der Ergebnisse zur Arbeit.

Die Studierenden werden durch eine **Losziehung** in Teams eingeteilt. Grundsätzlich bestehen die Teams aus zehn Personen; **Team 4 besteht aus neun Personen**.

### Team 4

- Michael Santos Nunes
- Joel Germann
- Luis Elsensohn
- Lodmila Kalbara
- Yowaldy Keller
- Noah Muro
- Erwin Reiterer
- Niklaus Janett
- Ebru Demirtay

## Lern- und Projektziele

Die Studierenden sollen:

- Grundlagen von MicroPython und IoT anwenden,
- Mikrocontroller, Sensoren und Aktoren korrekt verbinden und ansteuern,
- ein technisches Problem analysieren und eine geeignete Lösung entwickeln,
- Anforderungen formulieren und die Lösung systematisch testen,
- Fehler strukturiert suchen, dokumentieren und beheben,
- im Team planen, umsetzen und Aufgaben verteilen,
- Ergebnisse sachlich dokumentieren und verständlich präsentieren.

Am Ende soll ein funktionsfähiger Prototyp vorliegen. Die Studierenden sollen erklären können, wie die eingesetzten Komponenten und Programme zusammenarbeiten und wie die Zielerreichung überprüft wurde.

## Ablauf der Arbeit

Die Bearbeitung lässt sich in drei Phasen gliedern:

1. **Analyse und Planung**
   - Ausgangslage und Problemstellung klären
   - überprüfbare Ziele, Anforderungen und Abgrenzungen festlegen
   - mögliche Lösungsvarianten untersuchen und begründet auswählen
   - Aufgaben, Risiken, Termine und Zuständigkeiten planen

2. **Umsetzung**
   - Schaltung und Systemarchitektur entwerfen
   - Adafruit-Komponenten aufbauen und verbinden
   - Software mit MicroPython entwickeln
   - Sensorwerte erfassen und Aktoren ansteuern
   - Zwischenstände und technische Entscheidungen dokumentieren

3. **Überprüfung und Abschluss**
   - Prüfverfahren und Testfälle festlegen
   - Funktionen und Anforderungen systematisch testen
   - Messwerte und Fehler auswerten
   - Ziele überprüfen und Abweichungen begründen
   - Erkenntnisse, Nutzen und mögliche Weiterentwicklungen festhalten

# Vorgesehene Dokumentation und Präsentation

Die Leitfäden im Ordner `Doc/Leitfäden` behandeln drei mögliche Ergebnisse beziehungsweise Abgabeformen:

- projektbasierter technischer Bericht,
- Ausstellungsplakat,
- Screencast.

## Technischer Bericht

Der technische Bericht dokumentiert die ausgeführten Arbeiten, Ergebnisse und Schlussfolgerungen so, dass aussenstehende Personen das Projekt verstehen und nachvollziehen können. Er folgt einem fachlichen roten Faden und nicht einer chronologischen Erzählung des Projektverlaufs.

### Empfohlener Aufbau

#### Vorspann

- Titelblatt
- Management Summary
- KI-Hilfsmittelverzeichnis
- Inhaltsverzeichnis

#### Einleitung

- Ausgangslage und Problemstellung
- Ziele, Anforderungen und Abgrenzungen
- Vorgehensweise und eingesetzte Methoden
- kurze Zusammenfassung der Projektorganisation

#### Hauptteil

Der Hauptteil enthält die fachliche Bearbeitung des Problems. Für das IoT-Projekt bietet sich folgende Struktur an:

- Erhebung und Gewichtung der Anforderungen
- Lösungsvarianten und begründete Auswahl
- Systemkonzept und Architektur
- Auswahl und Aufbau der Hardware
- Entwurf und Implementierung der MicroPython-Software
- Zusammenspiel von Sensoren, Aktoren und Kommunikation
- Tests und Überprüfung der Funktionsweise
- unerwartete technische Probleme und erarbeitete Lösungen
- Zwischenresultate, Messwerte und Erkenntnisse

Detaillierte Berechnungen, vollständiger Programmcode, Datenblätter und umfangreiche Pläne gehören in der Regel in den Anhang. Informationen, die für das Verständnis notwendig sind, müssen im Hauptteil stehen.

#### Schlussteil

- wichtigste Resultate und Erkenntnisse zusammenfassen
- Resultate interpretieren und kritisch diskutieren
- Zielerreichung und Anforderungen überprüfen
- Abweichungen und nicht erreichte Ziele begründen
- Nutzen und Schlussfolgerungen erläutern
- nächste Schritte und mögliche Folgearbeiten nennen
- persönliche Reflexion verfassen

Die persönliche Reflexion beantwortet insbesondere:

- Was ist gut gelungen?
- Wo lagen die grössten Herausforderungen?
- Was wurde gelernt?
- Was würde mit dem heutigen Wissen anders gemacht?
- Wie haben KI-Hilfsmittel die Bearbeitung unterstützt?

#### Ergänzungsteil

- Selbständigkeitserklärung und gegebenenfalls Haftungsausschluss
- Quellenverzeichnis
- Tabellen- und Abbildungsverzeichnisse
- Anhang und Verzeichnis digitaler Anhänge

### Ziele, Anforderungen und Abgrenzungen

Ziele beschreiben den angestrebten Endzustand. Sie müssen projektbezogen, spezifisch, überprüfbar, lösungsneutral und wirkungsorientiert sein. Muss-Ziele entscheiden über den Projekterfolg; Kann-Ziele schaffen zusätzlichen Nutzen, falls Zeit und Rahmenbedingungen dies erlauben.

Technologien wie MicroPython oder vorgegebene Adafruit-Komponenten sind keine Ziele, sondern **Anforderungen**, weil sie den Lösungsweg und die Rahmenbedingungen festlegen.

Mögliche Formulierungen für dieses Projekt:

- **Ziel:** Ein funktionsfähiger Prototyp bestätigt die korrekte Zusammenarbeit der Komponenten.
- **Ziel:** Die erfassten Sensordaten werden innerhalb einer festgelegten Messabweichung verarbeitet und angezeigt.
- **Anforderung:** Die Software wird mit MicroPython implementiert.
- **Anforderung:** Für den Aufbau werden die festgelegten Adafruit-Komponenten eingesetzt.
- **Abgrenzung:** Eine Serienfertigung oder Zertifizierung ist nicht Bestandteil der Arbeit.

Das konkrete System, die Messgrössen, Toleranzen und Abgrenzungen müssen vor Projektbeginn festgelegt werden.

### Management Summary

Das Management Summary steht vor dem Inhaltsverzeichnis und fasst die gesamte Arbeit auf ungefähr einer Seite zusammen. Es wird erst am Ende der Arbeit geschrieben und muss ohne Kenntnis des Berichts verständlich sein. Es enthält:

- Ausgangslage und Problemstellung,
- Ziele und Anforderungen,
- wesentliche Ergebnisse und Erkenntnisse,
- Zielerreichung,
- Schlussfolgerung, Nutzen und weiteres Vorgehen.

Ungeeignet sind eine reine Tätigkeitsliste, Verweise auf spätere Kapitel, persönliche Danksagungen oder Aussagen ohne konkrete Resultate.

### Quellen, KI und Selbständigkeit

- Fremde Texte, Ideen, Grafiken, Datenblätter, technische Anleitungen und fremder Programmcode müssen gekennzeichnet werden.
- Zitate und sinngemässe Übernahmen werden nach der vorgegebenen, an IEEE angelehnten Zitierweise mit Nummern in eckigen Klammern angegeben.
- Das Quellenverzeichnis enthält nur Quellen, die im Bericht tatsächlich verwendet und zitiert werden.
- Jede Quelle behält bei mehrfacher Verwendung dieselbe Nummer.
- KI-Werkzeuge werden in einem eigenen KI-Hilfsmittelverzeichnis transparent aufgeführt. Die Tabelle enthält **KI-Tool**, **Funktion** und **Einsatz im Bericht**.
- Auch KI-generierte Texte, Grafiken und Programmcodes sind in der Selbständigkeitserklärung beziehungsweise im Hilfsmittelverzeichnis offenzulegen.
- Ein nicht gekennzeichnetes Übernehmen fremder oder KI-generierter Inhalte gilt als Plagiat. Laut Leitfaden führt ein Plagiat zur Note 1.

### Abbildungen, Tabellen und Anhang

- Abbildungen, Diagramme, Formeln und Tabellen werden fortlaufend nummeriert und beschriftet.
- Jede Darstellung erhält eine Quellenangabe; eigene Inhalte werden mit «eigene Darstellung» bezeichnet.
- Für die verschiedenen Darstellungsarten werden separate Verzeichnisse geführt.
- Verweise in den Anhang erfolgen über Fussnoten und müssen ein schnelles Auffinden ermöglichen.
- Der digitale Anhang wird als ZIP-Archiv abgegeben und in einem separaten Verzeichnis im Bericht aufgelistet.
- In den digitalen Anhang gehören beispielsweise Quellcode, Konfigurationen, Datenblätter, Messreihen, grosse Pläne und weitere Projektdateien.

### Sprache und Gestaltung

- klar, sachlich, präzise und leicht verständlich schreiben,
- kurze, aussagekräftige Sätze und korrekte Fachbegriffe verwenden,
- aktive Formulierungen bevorzugen,
- im Hauptteil keine Ich-, Wir- oder Erlebnisberichte verwenden,
- Tatsachen, konkrete Arbeiten und messbare Ergebnisse beschreiben,
- vage, subjektive oder übertriebene Wörter wie «einfach», «natürlich», «sehr», «super», «ein bisschen» oder «Dinge» vermeiden,
- aussagekräftige, nummerierte Überschriften verwenden,
- das Inhaltsverzeichnis auf höchstens drei Gliederungsebenen beschränken,
- ein einheitliches Layout, gut lesbare Schrift und fortlaufende Seitenzahlen verwenden,
- hochwertige Grafiken und Tabellen gezielt am passenden Ort einsetzen.

## Ausstellungsplakat

Das Plakat vermittelt die Kernaussage der Arbeit auf einen Blick. Es richtet sich an Fachpersonen, Berufskolleginnen und -kollegen, Angehörige und weitere Interessierte. Es ist kein textreiches wissenschaftliches Poster, sondern zeigt Aufgabe, Ziele, Resultate, Nutzen und Erkenntnisse kompakt und praxisorientiert.

### Inhaltliche Struktur

1. **Ausgangslage und Zielsetzung:** Was war das Problem und was sollte erreicht werden?
2. **Vorgehen und Umsetzung:** Was wurde gemacht, wie wurde entschieden und umgesetzt?
3. **Ergebnis, Erkenntnisse und Nutzen:** Was wurde erreicht und welchen Mehrwert bietet das Ergebnis?

Das Resultat soll in der Regel am prominentesten dargestellt werden. Fotos, Messwerte, Diagramme und technische Grafiken sollen konkrete Aussagen unterstützen. Rein dekorative oder nichtssagende KI-Bilder sind zu vermeiden.

### Formale Vorgaben

- vorgegebene Vorlage `HF_T_WI_Vorlage_Plakat` verwenden,
- Kopf- und Fusszeile möglichst nicht verändern,
- Format: **DIN A1, Hochformat**,
- Schriftart: **Arial**,
- Schriftgrösse: ungefähr **40–48 pt**,
- Bilder: mindestens **150 dpi**, besser **300 dpi**,
- wenig Text und klare Aussagen,
- prägnante, nicht überladene und nicht zu bunte Grafiken,
- klare Leserichtung und genügend Weissraum.

Leitfrage für die Planung: **Was soll eine Person nach einer Minute vor dem Plakat über das Projekt wissen und denken?**

## Screencast

Ein Screencast vermittelt Bildschirminhalte als Video mit gesprochenem Kommentar, optional mit Systemton und Webcam. Für das IoT-Projekt kann er beispielsweise den Programmcode, die Messwertdarstellung und die Funktion des Prototyps erklären.

### Planung und Vorbereitung

- Zielgruppe, Ziel, Kernaussage, Inhalt und Einsatzkontext festlegen,
- Dauer auf **drei bis fünf Minuten** begrenzen,
- längere Inhalte auf mehrere Videos verteilen oder mit Zwischentiteln und Sprungmarken gliedern,
- ein Drehbuch mit Sequenzen, Bildschirminhalten, Sprechertext und Zeitangaben erstellen,
- Aufnahmebereich bestimmen: ganzer Bildschirm, Fenster oder definierter Ausschnitt,
- Desktop aufräumen, Benachrichtigungen deaktivieren und private Daten ausblenden,
- neutralen Hintergrund verwenden,
- Mikrofon, Kamera und Zugriffsberechtigungen vorab testen.

Ein externes Mikrofon oder gutes Headset verbessert die Sprachqualität. Ein Mikrofon mit Nierencharakteristik reduziert seitliche und rückwärtige Umgebungsgeräusche. Ein gleichbleibender Abstand zum Mikrofon sorgt für eine konstante Aufnahme.

### Aufnahme und Bearbeitung

- ruhig und in gleichmässigem Tempo sprechen,
- Kommentar und gezeigten Inhalt aufeinander abstimmen,
- Mausbewegungen und Klicks langsam und gezielt ausführen,
- Fachbegriffe und zentrale Inhalte klar betonen,
- Markierungen, Pfeile oder Zooms nur gezielt einsetzen,
- Aufnahme vollständig prüfen,
- Versprecher, Pausen und unnötige Szenen entfernen,
- bei Bedarf Untertitel oder kurze Texteinblendungen ergänzen,
- Lautstärke ausgleichen und Störgeräusche reduzieren.

Als Werkzeuge nennt der Leitfaden unter anderem OBS Studio, Camtasia, Loom und Microsoft PowerPoint. Die Wahl richtet sich nach Aufnahme-, Audio-, Webcam-, Bearbeitungs- und Exportfunktionen sowie Betriebssystem und Bedienbarkeit.

### Export

- bevorzugtes Format: **MP4**,
- empfohlene Auflösung: **1080p (Full HD)**,
- Bildrate: meist **30 Bilder pro Sekunde**, bei viel Bewegung gegebenenfalls 60,
- Audio-Bitrate für Sprache: ungefähr **128–192 kbit/s**,
- Veröffentlichung je nach Zielgruppe über Lernplattform, internen Server, Videoportal, Cloud-Speicher oder direkte Dateiübertragung.

# Kernbotschaft für den Infoabend

Die technische Arbeit verbindet Programmierung, Elektronik und IoT mit einer systematischen Projektbearbeitung. Die Studierenden entwickeln nicht nur einen funktionierenden Prototyp mit MicroPython und Adafruit-Komponenten, sondern lernen auch, technische Entscheidungen zu begründen, Ergebnisse zu testen, Quellen und KI-Hilfsmittel korrekt offenzulegen und ihre Arbeit in Bericht, Plakat und Screencast professionell zu präsentieren.

# Grundlage

Diese Zusammenfassung basiert auf allen Dokumenten im Ordner `Doc/Leitfäden`:

- *Leitfaden zur Erstellung von Ausstellungsplakaten*, April 2026
- *Leitfaden zur Erstellung von Screencasts*, August 2025
- *Leitfaden zur Erstellung projektbasierter technischer Berichte*, Juli 2026
- die Variante des Berichtsleitfadens mit dem Zusatz «Änderungen»; sie enthält gegenüber der regulären Fassung keine abweichenden fachlichen Inhalte
