# ArUco Sheet Generator

Dieses Script erzeugt klassische OpenCV-ArUco-Marker fuer den Druck auf A4-Seiten.
Es ist fuer deinen Workflow gedacht: Marker drucken, spaeter im anderen Script per Dictionary + ID sicher wiederfinden und fuer automatische Bildaufnahme bzw. Entzerrung nutzen.

## Warum diese Auslegung?

OpenCV empfiehlt fuer Anwendungen mit wenigen benoetigten Markern eher kleinere Dictionaries, weil kleinere Dictionary-Groessen bei passender Markeranzahl eine hoehere Inter-Marker-Distanz und damit robustere Erkennung erlauben koennen. Quelle: OpenCV ArUco Detection Tutorial. [web:4]

Zugleich gilt: groessere Marker auf dem Ausdruck sind auf Distanz leichter zu erkennen, waehrend Marker mit mehr Bits schwerer auszulesen sein koennen. Quellen: OpenCV ArUco Detection Tutorial; OpenCV Doku zu Markerparametern. [web:4][web:7]

Fuer eine typische Aufnahmedistanz von etwa 90 cm nach unten ist deshalb ein guter Startpunkt:
- `DICT_4X4_50` fuer kleine Marker-Sets
- Marker-Kantenlaenge ca. 45 mm bis 60 mm
- Druck mit 300 DPI

## Voraussetzungen

Python 3.10+ empfohlen.

Pakete installieren:

```bash
pip install opencv-contrib-python numpy
```

Wichtig: Das Paket muss `opencv-contrib-python` sein, damit `cv2.aruco` verfuegbar ist.

## Script starten

```bash
python aruco_sheet_generator.py --dict DICT_4X4_50 --ids 0-11 --marker-mm 45 --dpi 300 --show
```

Das erzeugt:
- eine oder mehrere A4-Seiten mit so vielen Markern wie auf die Seite passen
- klare Dateinamen
- optional eine Vorschau pro Seite
- auf Wunsch Einzelmarker-Dateien

## Wichtige CLI-Parameter

- `--dict` -> OpenCV-Dictionary, z. B. `DICT_4X4_50`, `DICT_5X5_50`, `DICT_6X6_250`
- `--ids` -> Marker-IDs, z. B. `0-3` oder `0,1,2,7`
- `--marker-mm` -> reale Marker-Kantenlaenge in Millimetern
- `--distance-cm` -> nur fuer die automatische Groessenempfehlung, falls `--marker-mm` nicht gesetzt ist
- `--dpi` -> Druckaufloesung, Standard 300
- `--border-bits` -> schwarzer Rand des Markers, Standard 1
- `--margin-mm` -> Seitenrand auf A4
- `--gap-mm` -> Abstand zwischen Markern
- `--label-height-mm` -> Platz fuer die Beschriftung unter dem Marker
- `--outdir` -> Zielordner, Standard `ArUco-images`
- `--show` -> zeigt die Seiten nacheinander mit OpenCV an
- `--save-individual` -> speichert zusaetzlich jeden Marker einzeln als PNG
- `--start-small` -> erzeugt zusaetzlich ein kleines Testblatt mit `DICT_4X4_50` und 35 mm

## Empfohlene Startwerte

### 1) Kleiner und robust fuer wenige Marker

```bash
python aruco_sheet_generator.py --dict DICT_4X4_50 --ids 0-7 --marker-mm 45 --dpi 300 --show --save-individual
```

Gut, wenn du nur wenige Marker gleichzeitig brauchst und robuste Detection willst. OpenCV beschreibt kleinere Dictionary-Groessen fuer kleine Marker-Sets als vorteilhaft. [web:4]

### 2) Etwas konservativer, naeher an deinem aktuellen Stand

```bash
python aruco_sheet_generator.py --dict DICT_6X6_250 --ids 0-7 --marker-mm 60 --dpi 300 --show --save-individual
```

Sinnvoll, wenn du beim bisherigen 6x6-Workflow bleiben willst. Bei hoeherer Bit-Anzahl wird die Detektion anspruchsvoller als bei kleineren Markern, deshalb eher groesser drucken. [web:4][web:16]

### 3) Wenn du die Groesse automatisch empfehlen lassen willst

```bash
python aruco_sheet_generator.py --dict DICT_4X4_50 --ids 0-11 --distance-cm 90 --show
```

Das Script waehlt dann automatisch einen praxisnahen Startwert fuer `--marker-mm`.

## Was ist fuer 90 cm Distanz sinnvoll?

Als Startempfehlung fuer eine nach unten gerichtete Kamera mit Weitwinkel auf etwa 90 cm Distanz:
- `DICT_4X4_50`
- 45 mm Markerlaenge, wenn du viele auf eine Seite bekommen willst
- 60 mm Markerlaenge, wenn dir Detection-Robustheit wichtiger ist als Packdichte
- 300 DPI Druck

Das ist eine praxisnahe Empfehlung aus den OpenCV-Grundregeln: wenige Marker -> kleineres Dictionary; groessere Ausdrucke -> leichtere Erkennung auf Distanz. [web:4][web:7]

## Dateinamen

Beispiele:
- `aruco_sheet_DICT_4X4_50_p01_45mm_300dpi.png`
- `aruco_DICT_4X4_50_id003_531px.png`

Damit kannst du spaeter im Detektionsscript sauber referenzieren:
- Dictionary: `DICT_4X4_50`
- ID: `3`
- physische Kantenlaenge: z. B. `45.0 mm`

## Im Detect-Script verwenden

Fuer die Detection muessen Dictionary und ID zum Druckmarker passen. OpenCV sucht nur Marker aus dem angegebenen Dictionary. [web:15][web:4]

Beispiel:

```python
import cv2

aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
params = cv2.aruco.DetectorParameters()
detector = cv2.aruco.ArucoDetector(aruco_dict, params)

image = cv2.imread('frame.png')
corners, ids, rejected = detector.detectMarkers(image)

if ids is not None:
    print(ids.flatten().tolist())
```

Wenn du Pose oder Abstand schaetzen willst, brauchst du zusaetzlich die echte Marker-Kantenlaenge und eine kalibrierte Kamera. Die Pose-Schaetzung verwendet die Markerlaenge in realen Einheiten. [web:13]

## Empfehlung fuer deinen Fall

Ich wuerde mit diesen zwei Druckseiten testen:

### Seite A: maximale Packdichte

```bash
python aruco_sheet_generator.py --dict DICT_4X4_50 --ids 0-15 --marker-mm 45 --dpi 300 --show --save-individual
```

### Seite B: robuster fuer Distanz

```bash
python aruco_sheet_generator.py --dict DICT_6X6_250 --ids 0-7 --marker-mm 60 --dpi 300 --show --save-individual
```

Dann machst du reale Testbilder mit deiner Raspberry-Pi-Wide-Kamera in deinem Aufbau und vergleichst Detection-Stabilitaet, besonders bei Randbereichen und Perspektive.
