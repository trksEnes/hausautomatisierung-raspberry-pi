# Technische Erläuterungen

Diese Beschreibung bezieht sich auf die unveränderte Datei [motor_und_touchpad.py](../src/motor_und_touchpad.py). Bei Abweichungen zur ursprünglichen Projektarbeit ist für die Beschreibung des erhaltenen Programms der Code maßgeblich.

## Pinbelegung

Das Programm verwendet `GPIO.setmode(GPIO.BCM)`. Die Zahlen sind BCM-GPIO-Nummern und keine physischen Steckplatznummern.

| BCM-GPIO | Variable | Funktion im Code |
| --- | --- | --- |
| 21 | `touch_pin` | Eingang des Touchsensors; zusätzlich direkt als `GPIO.input(21)` ausgelesen |
| 20 | `led` | Ausgang für die Innenbeleuchtung |
| 5 | `sensor_pin` | Digitaler Eingang des Lichtsensors |
| 6, 13, 19, 26 | `motor_pins` | Vier Steuersignale für die Motor-Treiberplatine |
| 27 | `knopf` | Betriebsarttaster zum Pausieren und Fortsetzen der Automatik |
| 22 | `right_pin` | Manuelle Drehrichtung mit vorwärts durchlaufener Schrittfolge |
| 17 | `left_pin` | Manuelle Drehrichtung mit rückwärts durchlaufener Schrittfolge |

Die Außenbeleuchtung wird in der ursprünglichen Projektarbeit separat mit GPIO 2 für den Bewegungssensor und GPIO 3 für die LED beschrieben. Diese Pins werden in der hier vorhandenen Python-Datei nicht eingerichtet. Die Tabelle ersetzt keinen geprüften Schaltplan.

## Innenbeleuchtung

`light_thread()` liest den Touch-Eingang in einer Endlosschleife. Bei einem HIGH-Signal wird der Zustand in `Value` umgeschaltet und der LED-Ausgang entsprechend gesetzt. Zwischen den Abfragen liegt eine Pause von 0,3 Sekunden. `Value1` wird ebenfalls verändert, beeinflusst aber die Ausgänge nicht.

Das beabsichtigte Verhalten ist ein Wechsel zwischen Licht an und Licht aus bei jeder Berührung. Der vorhandene Code prüft jedoch den Signalpegel statt einer einzelnen Flanke: Bleibt der Eingang länger HIGH, kann die Beleuchtung wiederholt umschalten.

## Automatische Jalousie

`MotorThread.run()` liest den Lichtsensor und vergleicht ihn mit `last_sensor_state`. Bei einer Änderung wird die Drehrichtung gewählt: HIGH setzt `direction = -1`, LOW setzt `direction = 1`. Ob ein Modul bei Helligkeit HIGH oder LOW ausgibt, muss zum tatsächlich verwendeten Sensor und dessen Einstellung passen.

Der Motor erhält eine achtteilige Halbschrittfolge. Nach jeder Ausgabe wartet die Software 0,001 Sekunden. Eine automatische Fahrt läuft ungefähr 15 Sekunden; anschließend folgt eine Wartephase von bis zu 15 Sekunden. Der Sensor wird nicht kontinuierlich während dieser Fahrt und Wartephase ausgewertet. Beim Start zählt auch der erste gelesene Sensorwert als Änderung gegenüber `None`.

Endschalter oder eine Positionsrückmeldung sind im Code nicht enthalten. Die Zeitsteuerung liefert deshalb keine bestätigte Endposition der Jalousie.

## Manuelle Bedienung

Die Tastereingänge verwenden interne Pull-up-Widerstände. Eine fallende Flanke löst den jeweiligen Callback aus; `bouncetime=200` dient als Entprellzeit.

Der Betriebsarttaster verändert `trash` und ruft `pause()` oder `resume()` am Motor-Thread auf. Die beiden Richtungstaster werden nur ausgeführt, wenn `trash` den manuellen Betrieb anzeigt. Solange der jeweilige Eingang LOW bleibt, läuft die entsprechende Schrittfolge.

## Grenzen und mögliche Weiterentwicklung

Der Code dokumentiert den damaligen Prototyp. Bei einer Überarbeitung wären diese Punkte sinnvoll:

- **Einmalige Touch-Ereignisse:** Flankenerkennung statt wiederholten Umschaltens bei einem gehaltenen HIGH-Signal.
- **Eindeutige Betriebsarten:** `trash` wird sowohl zum Umschalten als auch zum Beenden der Automatikschleife verwendet. Je nach Zeitpunkt kann der Motor-Thread enden und durch `resume()` nicht wieder gestartet werden.
- **Ein gemeinsamer Motorzugriff:** Automatik und Richtungstaster schreiben auf dieselben Motorpins. Die Pause bestätigt nicht, dass der automatische Zugriff bereits beendet ist; eine gemeinsame Steuerlogik könnte überlappende Schreibzugriffe verhindern.
- **Reaktionszeit und Position:** Eine unterbrechbare Ablaufsteuerung und eine Rückmeldung der Endposition würden die zeitgesteuerte Bewegung ergänzen.
- **Geordnetes Beenden:** Im erhaltenen Programm fehlen ein gemeinsames Stoppsignal für die Threads und ein abschließendes `GPIO.cleanup()`.
- **Außenbeleuchtung ergänzen:** Die originale separate Quelldatei fehlt. Eine neue Implementierung müsste als spätere Ergänzung gekennzeichnet und am Aufbau geprüft werden.

## Prüfung dieses Repositorys

Die Python-Datei wurde auf Syntax geprüft und mit der bereitgestellten Originaldatei verglichen. Die Dokumentation wurde mit der Pinbelegung und der Logik im Code abgeglichen. Ein Hardwaretest wurde bei dieser Aufbereitung nicht durchgeführt, da der ursprüngliche Aufbau nicht angeschlossen ist.
