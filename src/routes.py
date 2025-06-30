from flask import Blueprint, jsonify, request
from app.models import Person, Aufgabe, Projekt, Zuweisung, db
from sqlalchemy import text
from scipy.optimize import linear_sum_assignment
import numpy as np
from app.algorithm import berechne_zuweisungen_stundenbasiert
import csv
from flask import Response

bp = Blueprint('routes', __name__)

# -------------------- Test der Datenbankverbindung --------------------
@bp.route('/test_db', methods=['GET'])
def test_db():
    try:
        db.session.execute(text("SELECT 1"))
        return jsonify({"message": "Verbindung zur Datenbank erfolgreich!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -------------------- Neue Person hinzufügen --------------------
@bp.route('/personen', methods=['POST'])
def add_person():
    try:
        data = request.get_json()
        new_person = Person(
            vorname=data['vorname'],
            nachname=data['nachname'],
            kompetenz=data['kompetenz'],
            teilzeitfaktor=float(data['teilzeitfaktor']),
            verfuegbare_monate=data['verfuegbare_monate']
        )
        db.session.add(new_person)
        db.session.commit()
        return jsonify({"message": "Person hinzugefügt"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# -------------------- Alle Personen abrufen --------------------
@bp.route('/personen', methods=['GET'])
def get_personen():
    try:
        personen = Person.query.all()
        result = [
            {
                "id": p.id,
                "vorname": p.vorname,
                "nachname": p.nachname,
                "kompetenz": p.kompetenz,
                "teilzeitfaktor": p.teilzeitfaktor,
                "verfuegbare_monate": p.verfuegbare_monate
            } for p in personen
        ]
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -------------------- Neues Projekt hinzufügen --------------------
@bp.route('/projekte', methods=['POST'])
def add_projekt():
    try:
        data = request.get_json()
        new_project = Projekt(
            projektname=data['projektname'],
            projektstart=data['projektstart'],
            projektende=data['projektende'],
            anzahl_aufgaben=data['anzahl_aufgaben'],
            kompetenz=data['kompetenz']
        )
        db.session.add(new_project)
        db.session.commit()
        return jsonify({"message": "Projekt hinzugefügt"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# -------------------- Alle Projekte abrufen --------------------
@bp.route('/projekte', methods=['GET'])
def get_projekte():
    try:
        projekte = Projekt.query.all()
        result = [
            {
                "id": p.id,
                "projektname": p.projektname,
                "projektstart": p.projektstart,
                "projektende": p.projektende,
                "anzahl_aufgaben": p.anzahl_aufgaben,
                "kompetenz": p.kompetenz
            } for p in projekte
        ]
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -------------------- Neue Aufgabe hinzufügen --------------------
@bp.route('/aufgaben', methods=['POST'])
def add_aufgabe():
    try:
        data = request.get_json()
        projekt = Projekt.query.filter_by(projektname=data['projekt']).first()
        if not projekt:
            return jsonify({"error": f"Projekt '{data['projekt']}' nicht gefunden"}), 404

        new_task = Aufgabe(
            projekt_id=projekt.id,
            aufgabe=data['aufgabe'],
            startmonat=data['startmonat'],
            endmonat=data['endmonat'],
            minimale_kompetenz=data['minimale_kompetenz'],
            arbeitsaufwand=float(data['arbeitsaufwand'])
        )
        db.session.add(new_task)
        db.session.commit()
        return jsonify({"message": "Aufgabe hinzugefügt"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# -------------------- Alle Aufgaben abrufen --------------------
@bp.route('/aufgaben', methods=['GET'])
def get_aufgaben():
    try:
        aufgaben = Aufgabe.query.all()
        result = [
            {
                "id": a.id,
                "projekt_id": a.projekt_id,
                "projekt_name": a.projekt.projektname,
                "aufgabe": a.aufgabe,
                "startmonat": a.startmonat,
                "endmonat": a.endmonat,
                "minimale_kompetenz": a.minimale_kompetenz,
                "arbeitsaufwand": a.arbeitsaufwand
            } for a in aufgaben
        ]
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -------------------- Automatische Zuweisung --------------------
@bp.route('/zuweisungen/automatisch', methods=['POST'])
def berechne_zuweisungen():
    try:
        personen = Person.query.all()
        aufgaben = Aufgabe.query.all()

        if not personen or not aufgaben:
            return jsonify({"error": "Keine Personen oder Aufgaben in der Datenbank gefunden."}), 400

        kostenmatrix = []
        for person in personen:
            kostenreihe = []
            for aufgabe in aufgaben:
                kompetenz_map = {'A': 1, 'B': 2, 'C': 3}
                person_kompetenz = kompetenz_map.get(person.kompetenz.upper(), float('inf'))
                aufgabe_kompetenz = kompetenz_map.get(aufgabe.minimale_kompetenz.upper(), float('inf'))

                if person_kompetenz <= aufgabe_kompetenz:
                    kosten = aufgabe.arbeitsaufwand / person.teilzeitfaktor
                else:
                    kosten = float('inf')
                kostenreihe.append(kosten)
            kostenmatrix.append(kostenreihe)

        kostenmatrix = np.array(kostenmatrix)

        personen_index, aufgaben_index = linear_sum_assignment(kostenmatrix)

        Zuweisung.query.delete()

        for p_idx, a_idx in zip(personen_index, aufgaben_index):
            if kostenmatrix[p_idx][a_idx] < float('inf'):
                neue_zuweisung = Zuweisung(
                    person_id=personen[p_idx].id,
                    aufgabe_id=aufgaben[a_idx].id,
                    kosten=kostenmatrix[p_idx][a_idx]
                )
                db.session.add(neue_zuweisung)

        db.session.commit()
        return jsonify({"message": "Optimale Zuweisungen erfolgreich berechnet und gespeichert."}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# -------------------- Alle Zuweisungen abrufen --------------------
@bp.route('/zuweisungen', methods=['GET'])
def get_zuweisungen():
    try:
        zuweisungen = Zuweisung.query.all()
        result = [
            {
                "person": f"{z.person.vorname} {z.person.nachname}",
                "aufgabe": z.aufgabe.aufgabe,
                "projekt": z.aufgabe.projekt.projektname,
                "startmonat": z.aufgabe.startmonat,
                "endmonat": z.aufgabe.endmonat,
                "kosten": z.kosten
            } for z in zuweisungen
        ]
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -------------------- Zuweisungen aktualisieren --------------------
@bp.route('/zuweisungen', methods=['PUT'])
def update_zuweisung():
    try:
        data = request.get_json()
        zuweisung = Zuweisung.query.get(data['id'])
        if not zuweisung:
            return jsonify({"error": "Zuweisung nicht gefunden"}), 404

        zuweisung.person_id = data.get('person_id', zuweisung.person_id)
        zuweisung.aufgabe_id = data.get('aufgabe_id', zuweisung.aufgabe_id)
        zuweisung.kosten = data.get('kosten', zuweisung.kosten)
        db.session.commit()
        return jsonify({"message": "Zuweisung aktualisiert"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# -------------------- Zuweisungen stundenbasiert --------------------
@bp.route('/zuweisungen/stundenbasiert', methods=['POST'])
def route_zuweisungen_stundenbasiert():
    result = berechne_zuweisungen_stundenbasiert()
    return jsonify(result)

# -------------------- Zuweisungen als CSV ausgeben --------------------
@bp.route('/zuweisungen/export', methods=['GET'])
def export_zuweisungen_csv():
    zuweisungen = Zuweisung.query.all()

    def generate():
        header = ['Projekt', 'Aufgabe', 'Startmonat', 'Endmonat', 'Person', 'Kosten (Stunden)']
        yield ','.join(header) + '\n'
        for z in zuweisungen:
            row = [
                z.aufgabe.projekt.projektname,
                z.aufgabe.aufgabe,
                z.aufgabe.startmonat,
                z.aufgabe.endmonat,
                f"{z.person.vorname} {z.person.nachname}",
                f"{z.kosten:.2f}"
            ]
            yield ','.join(row) + '\n'

    return Response(generate(), mimetype='text/csv',
                    headers={"Content-Disposition": "attachment;filename=zuweisungen.csv"})
