# Snips-Homematic-XML
Dies ist ein Homematic Skill für Snips.ai, der die vorhandenen Geräte und Programme via XML-API ansteuert. Die Namen der Geräte werden initial und später auf Befehl von der CCU ausgelesen.

Es gibt insgesamt sechs verschiedene Kommandos:
- Programm ausführen (z.B. "Führe Bla aus")
- Geräte/Programm-Cache aktualisieren (z.B. "Aktualisiere!")
- Geräte binär steuern (z.B. "Licht xyz an", "Rolllade abc hoch")
- Geräte prozentual steuern (z.B. "Fahre Rolllade abc auf 13%")
- Thermostate mit Grad-Zahl steuern (z.B. "Setze Heizung Wohnzimmer auf 20 Grad.")
- Den Zustand von Geräten wie Lichtaktoren, Rollladenaktoren, Bewegungsmeldern oder Türkontakten auslesen (z.B. "Zustand Türkontakt Haustür")

Der Parameter url="http://192.168.0.2/addons/xmlapi/" konfiguriert den Zugriff auf die XML-API der CCU.
