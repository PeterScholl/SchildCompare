# Anleitung

Wähle zuerst ein Verzeichnis, in dem die Dateien der verschiedenen Datenbanken abgelegt werden sollen. Danach werden export-Verzeichnisse für jedes System angelegt

Nun können in diese Export-Ordner von jeder Datenquelle die Leistungsdaten exportiert werden. Dabei soll das UTF-8-Format gewählt werden. Hilfe erhält man, wenn man mit der Maus über das Status-Feld der entsprechenden Datenbank fährt.

Wenn alle Export-Dateien generiert worden sind, können noch Einstellungen im Datei-Menü angepasst werden. Dann kann auf Report geklickt werden.

# Export aus den verschiedenen Programmen

* Schild: Zunächst Stufe auswäheln (AKTIVE und Externe) -> dann in das Menü Datenaustausch, Schild-NRW-Schnittstelle, Export -> alle Haken aus, bis auf Schüler: Leistungsdaten, auf der rechten Seite: nur aktuellen Abschnitt auswählen -> Dateiordner für den Export auswählen -> Export starten
* Untis: Menü Datei -> Import/Export -> Deutschland -> NRW-SchildNRW, Reiter Exportieren auswählen - Klasse auswählen - Ordner auswählen - exportieren
* LuPO: Datenaustausch -> SchildNRW -> Exportieren

# Exe-Datei wird erstellt mit
pyinstaller --onefile checkStufenDaten_GUI.py
