from .models import Zuweisung, Person, Aufgabe, Projekt, db
import numpy as np
from scipy.optimize import linear_sum_assignment
import re

def berechne_zuweisung_pro_projekt():
    projekte = Projekt.query.all()

    if not projekte:
        print("❌ Keine Projekte in der Datenbank gefunden.")
        return

    for projekt in projekte:
        print(f"🔄 Verarbeite Projekt: {projekt.projektname}")
        
        # Alle Aufgaben und Personen für das aktuelle Projekt abrufen
        aufgaben = Aufgabe.query.filter_by(projekt_id=projekt.id).all()
        personen = Person.query.all()

        if not aufgaben or not personen:
            print(f"⚠️ Projekt {projekt.projektname} hat keine Aufgaben oder es gibt keine Personen.")
            continue

        # Kostenmatrix erstellen
        kostenmatrix = []
        for person in personen:
            kostenreihe = []
            for aufgabe in aufgaben:
                if ord(person.kompetenz) >= ord(aufgabe.minimale_kompetenz):
                    kosten = aufgabe.arbeitsaufwand / person.teilzeitfaktor
                else:
                    kosten = float('inf')  # Hohe Kosten für ungeeignete Kandidaten
                kostenreihe.append(kosten)
            kostenmatrix.append(kostenreihe)

        kostenmatrix = np.array(kostenmatrix)

        # Prüfen, ob die Kostenmatrix valide ist
        if kostenmatrix.shape[0] == 0 or kostenmatrix.shape[1] == 0:
            print(f"⚠️ Leere oder ungültige Kostenmatrix für Projekt {projekt.projektname}.")
            continue

        # Kuhn-Munkres-Algorithmus anwenden
        try:
            personen_index, aufgaben_index = linear_sum_assignment(kostenmatrix)
        except Exception as e:
            print(f"❌ Fehler beim Anwenden des Algorithmus für Projekt {projekt.projektname}: {e}")
            continue

        # Zuweisungen speichern
        for p_idx, a_idx in zip(personen_index, aufgaben_index):
            if kostenmatrix[p_idx][a_idx] < float('inf'):
                neue_zuweisung = Zuweisung(
                    person_id=personen[p_idx].id,
                    aufgabe_id=aufgaben[a_idx].id,
                    kosten=kostenmatrix[p_idx][a_idx]
                )
                db.session.add(neue_zuweisung)

        try:
            db.session.commit()
            print(f"✅ Zuweisungen für Projekt {projekt.projektname} erfolgreich berechnet und gespeichert.")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Fehler beim Speichern der Zuweisungen für Projekt {projekt.projektname}: {e}")

# -----------------------------
# ScoreMatching-Algorithmus (stundenbasiert, heuristisch)
# -----------------------------

def parse_verfuegbarkeit(verf_str):
    """
    Wandelt den Verfügbarkeitsstring aus der Datenbank (z. B. "01/2025:0.5,02/2025:1.0")
    in ein Dictionary um: {"01/2025": 0.5, "02/2025": 1.0}
    """
    monate = {}
    for eintrag in verf_str.split(","):
        match = re.match(r"(\d{2}/\d{4}):([\d.]+)", eintrag.strip())
        if match:
            monat, wert = match.groups()
            monate[monat] = float(wert)
    return monate


def berechne_zuweisungen_stundenbasiert():
    """
    Hauptfunktion für stundenbasierte Aufgabenverteilung.
    Personen mit ausreichender Kompetenz und verfügbarer Zeit
    werden heuristisch auf Aufgaben verteilt.
    """

    # Alle relevanten Daten aus der Datenbank laden
    personen = Person.query.all()
    aufgaben = Aufgabe.query.all()

    if not personen or not aufgaben:
        return {"error": "Keine Personen oder Aufgaben gefunden."}

    belegungen = {}  # Speichert pro Person und Monat die bereits belegten Stunden
    matching_ergebnisse = []  # Liste für Reporting / Export

    for ta in aufgaben:
        # Zeitraum und Aufwand der Aufgabe vorbereiten
        ta_start = int(ta.startmonat.split("/")[0])
        ta_ende = int(ta.endmonat.split("/")[0])
        aufwand_stunden = int(ta.arbeitsaufwand * 160)  # Aufwand in Stunden
        reststunden = aufwand_stunden
        kandidaten = []

        # Über alle Personen iterieren
        for p in personen:
            # Kompetenzprüfung: Person muss mindestens geforderte Kompetenz haben
            if ta.minimale_kompetenz > p.kompetenz:
                continue

            # Verfügbarkeiten der Person parsen
            verf_dict = parse_verfuegbarkeit(p.verfuegbare_monate)
            pid = p.id

            verf_stunden = 0
            monatlich = {}

            # Verfügbarkeit je Monat berechnen
            for m in range(ta_start, ta_ende + 1):
                monat_label = f"{m:02d}/2025"
                pm = verf_dict.get(monat_label, 0)  # PM aus Verfügbarkeit
                ist_stunden = pm * 160 / p.teilzeitfaktor  # Umrechnen auf reale Stunden
                belegt = belegungen.get(pid, {}).get(monat_label, 0)
                frei = max(0, ist_stunden - belegt)
                monatlich[monat_label] = frei
                verf_stunden += frei

            # Nur Personen mit verfügbarer Zeit in die Kandidatenliste aufnehmen
            if verf_stunden > 0:
                kandidaten.append((p, verf_stunden, monatlich))

        # Kandidaten sortieren: wer hat am meisten Zeit, kommt zuerst
        kandidaten.sort(key=lambda x: x[1], reverse=True)

        # Versuche, Aufgabe auf einen Kandidaten zu verteilen
        for person, verf_stunden, rest_by_month in kandidaten:
            if reststunden <= 0:
                break  # Aufgabe ist vollständig zugewiesen

            pid = person.id
            belegungen.setdefault(pid, {})
            zugewiesen = 0

            # Über Monate iterieren und Stunden zuteilen
            for monat, rest in rest_by_month.items():
                if rest <= 0 or reststunden <= 0:
                    continue
                anteil = min(reststunden, rest)
                belegungen[pid][monat] = belegungen[pid].get(monat, 0) + anteil
                zugewiesen += anteil
                reststunden -= anteil
                if reststunden <= 0:
                    break  # Aufgabe ist fertig verplant

            # Speichere die Zuweisung, wenn überhaupt Stunden zugewiesen wurden
            if zugewiesen > 0:
                z = Zuweisung(
                    person_id=pid,
                    aufgabe_id=ta.id,
                    kosten=zugewiesen  # Speichere Zuweisungskosten als Stunden
                )
                db.session.add(z)

                # Optional für Reporting oder Export
                matching_ergebnisse.append({
                    "person": f"{person.vorname} {person.nachname}",
                    "aufgabe": ta.aufgabe,
                    "projekt": ta.projekt.projektname,
                    "stunden": zugewiesen
                })

    # Versuche, die Zuweisungen in der DB zu speichern
    try:
        db.session.commit()
        return {"message": "Stundenbasierte Zuweisungen gespeichert.", "anzahl": len(matching_ergebnisse)}
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}
