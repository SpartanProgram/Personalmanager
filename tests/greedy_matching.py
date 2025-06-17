import time
import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional

def berechne_verfuegbarkeit(person, ta_start, ta_ende, belegungen, ta_projekt_id):
    """
    Improved availability calculation with project assignment check
    """
    person_id = person["id"]
    verfügbar = True
    verfügbarkeit_summe = 0
    monatliche_restwerte = {}

    for monat in range(ta_start, ta_ende + 1):
        monat_label = f"{monat:02d}/2025"
        
        # Check existing project assignment
        belegung_label = f"projektbelegung_{monat_label}"
        aktuelle_belegung = person.get(belegung_label, "Frei")
        
        if aktuelle_belegung not in ["Frei", ta_projekt_id]:
            rest = 0  # Person already assigned to other project
        else:
            verfügbarkeit = person.get(f"verfuegbarkeit_{monat_label}", 0)
            belegt = belegungen.get(person_id, {}).get(monat_label, 0)
            rest = max(0, verfügbarkeit - belegt)

        monatliche_restwerte[monat_label] = rest

        if rest <= 0:
            verfügbar = False
            break
        verfügbarkeit_summe += rest

    return verfügbar, verfügbarkeit_summe, monatliche_restwerte

def calculate_person_score(person, ta, belegungen=None):
    """
    Calculate person score for a task
    """
    if belegungen is None:
        belegungen = {}
        
    ta_start = int(ta["start"].split("/")[0])
    ta_ende = int(ta["ende"].split("/")[0])
    
    verfügbar, verf_summe, _ = berechne_verfuegbarkeit(person, ta_start, ta_ende, belegungen, ta["projekt_id"])
    
    if verfügbar and verf_summe > 0:
        # Score based on availability, time budget and skill match
        kompetenz_bonus = 1.0
        if ta["kompetenz"] in person["kompetenzen_liste"]:
            kompetenz_bonus = 1.5  # Bonus for exact skill match
            
        score = verf_summe * person["zeitbudget"] * kompetenz_bonus
        return round(score, 2)
    
    return 0

def calculate_lookahead_score(person, ta, remaining_tasks, personen_df, belegungen, lookahead_depth=2):
    """
    Calculate lookahead score by considering future task assignments
    """
    if lookahead_depth <= 0:
        return 0
    
    # Simulate assigning this person to current task
    temp_belegungen = {k: v.copy() for k, v in belegungen.items()}
    person_id = person["id"]
    
    if person_id not in temp_belegungen:
        temp_belegungen[person_id] = {}
    
    ta_start = int(ta["start"].split("/")[0])
    ta_ende = int(ta["ende"].split("/")[0])
    ta_monate = ta_ende - ta_start + 1
    ta_monatsaufwand = ta["aufwand"] / ta_monate
    
    # Update availability for this assignment
    for monat in range(ta_start, ta_ende + 1):
        monat_label = f"{monat:02d}/2025"
        verfügbarkeit = person.get(f"verfuegbarkeit_{monat_label}", 0)
        current_belegt = temp_belegungen[person_id].get(monat_label, 0)
        temp_belegungen[person_id][monat_label] = current_belegt + ta_monatsaufwand
    
    # Calculate potential future assignments
    future_score = 0
    for future_ta in remaining_tasks[:lookahead_depth]:
        if future_ta["kompetenz"] in person["kompetenzen_liste"]:
            future_score += calculate_person_score(person, future_ta, temp_belegungen)
    
    return future_score * 0.3  # Weight for lookahead score

def improved_greedy_matching(teilaufgaben_df, personen_df, lookahead_depth=2):
    """
    Improved Greedy Algorithm with Lookahead for optimal assignment
    
    Args:
        teilaufgaben_df: DataFrame with tasks
        personen_df: DataFrame with people
        lookahead_depth: How many future tasks to consider in scoring
        
    Returns:
        tuple: (list of matching results, execution time)
    """
    print("\n=== Improved Greedy Algorithm with Lookahead ===")
    start_time = time.time()
    
    # Initialize
    belegungen = {}
    matching_ergebnisse = []
    remaining_tasks = teilaufgaben_df.copy()
    
    # Sort tasks by priority (you can modify this based on your needs)
    # For now, sort by workload (higher workload first)
    remaining_tasks = remaining_tasks.sort_values('aufwand', ascending=False).reset_index(drop=True)
    
    while len(remaining_tasks) > 0:
        ta = remaining_tasks.iloc[0]
        ta_start = int(ta["start"].split("/")[0])
        ta_ende = int(ta["ende"].split("/")[0])
        ta_monate = ta_ende - ta_start + 1
        ta_monatsaufwand = ta["aufwand"] / ta_monate
        restaufwand = ta["aufwand"]
        
        # Find all candidates for this task
        kandidaten = []
        for _, person in personen_df.iterrows():
            if ta["kompetenz"] not in person["kompetenzen_liste"]:
                continue
                
            verfügbar, verf_summe, monatliche_restwerte = berechne_verfuegbarkeit(
                person, ta_start, ta_ende, belegungen, ta["projekt_id"]
            )
            
            if verfügbar and verf_summe > 0:
                # Calculate base score
                base_score = round(verf_summe * person["zeitbudget"], 2)
                
                # Calculate lookahead score
                lookahead_score = calculate_lookahead_score(
                    person, ta, remaining_tasks.iloc[1:].to_dict('records'), 
                    personen_df, belegungen, lookahead_depth
                )
                
                # Combined score
                total_score = base_score + lookahead_score
                
                kandidaten.append((person, total_score, verf_summe, monatliche_restwerte))
        
        # Sort candidates by total score (descending)
        kandidaten = sorted(kandidaten, key=lambda x: x[1], reverse=True)
        
        if len(kandidaten) == 0:
            print(f"Warnung: Keine Kandidaten für Aufgabe '{ta['bezeichnung']}' gefunden")
            # Remove task and continue
            remaining_tasks = remaining_tasks.iloc[1:].reset_index(drop=True)
            continue
        
        # Assign the best candidate
        best_person, best_score, verf_summe, eintrag_monate = kandidaten[0]
        pid = best_person["id"]
        
        if pid not in belegungen:
            belegungen[pid] = {}
        
        verfügbarkeit_gesamt = sum(eintrag_monate.values())
        anteil = min(restaufwand, verfügbarkeit_gesamt)
        monatsanteil = anteil / ta_monate
        
        # Create assignment
        matching_ergebnisse.append({
            "teilaufgabe_id": ta["teilaufgabe_id"],
            "teilaufgabe": ta["bezeichnung"],
            "projekt_id": ta["projekt_id"],
            "kompetenz": ta["kompetenz"],
            "person_id": pid,
            "name": best_person["name"],
            "zugewiesener_aufwand": round(anteil, 2),
            "score": best_score
        })
        
        # Update availability
        for monat_label in eintrag_monate:
            verbrauch = min(monatsanteil, eintrag_monate[monat_label])
            belegungen[pid][monat_label] = belegungen[pid].get(monat_label, 0) + verbrauch
        
        print(f"Zugewiesen: {ta['bezeichnung']} → {best_person['name']} (Score: {best_score:.2f})")
        
        # Remove assigned task
        remaining_tasks = remaining_tasks.iloc[1:].reset_index(drop=True)
    
    execution_time = time.time() - start_time
    
    print(f"Execution time: {execution_time:.3f} seconds")
    print(f"Found assignments: {len(matching_ergebnisse)}")
    print(f"Total workload assigned: {sum(item['zugewiesener_aufwand'] for item in matching_ergebnisse):.1f} hours")
    
    return matching_ergebnisse, execution_time

def greedy_matching_with_fallback(teilaufgaben_df, personen_df, lookahead_depth=2):
    """
    Greedy matching with fallback to simple assignment if no candidates found
    """
    print("\n=== Greedy Matching with Fallback ===")
    start_time = time.time()
    
    # Try improved greedy first
    matching_ergebnisse, execution_time = improved_greedy_matching(
        teilaufgaben_df, personen_df, lookahead_depth
    )
    
    # Check if all tasks were assigned
    total_assigned = sum(item["zugewiesener_aufwand"] for item in matching_ergebnisse)
    total_needed = teilaufgaben_df["aufwand"].sum()
    
    if total_assigned < total_needed:
        print(f"Greedy algorithm only assigned {total_assigned:.1f}/{total_needed:.1f} hours")
        print("Applying fallback simple assignment...")
        
        # Simple fallback: assign remaining tasks to anyone with matching skills
        remaining_tasks = []
        for _, ta in teilaufgaben_df.iterrows():
            task_assignments = [item for item in matching_ergebnisse if item['teilaufgabe_id'] == ta['teilaufgabe_id']]
            assigned_workload = sum(item['zugewiesener_aufwand'] for item in task_assignments)
            if assigned_workload < ta['aufwand']:
                remaining_tasks.append(ta)
        
        for ta in remaining_tasks:
            for _, person in personen_df.iterrows():
                if ta["kompetenz"] in person["kompetenzen_liste"]:
                    # Simple assignment without availability check
                    matching_ergebnisse.append({
                        "teilaufgabe_id": ta["teilaufgabe_id"],
                        "teilaufgabe": ta["bezeichnung"],
                        "projekt_id": ta["projekt_id"],
                        "kompetenz": ta["kompetenz"],
                        "person_id": person["id"],
                        "name": person["name"],
                        "zugewiesener_aufwand": ta["aufwand"],
                        "score": 0  # Fallback assignment
                    })
                    print(f"Fallback: {ta['bezeichnung']} → {person['name']}")
                    break
    
    execution_time = time.time() - start_time
    return matching_ergebnisse, execution_time

if __name__ == "__main__":
    # Test the algorithm
    print("Testing Improved Greedy Algorithm...")
    
    # Load data
    personen_df = pd.read_csv("../data/personen.csv")
    teilaufgaben_df = pd.read_csv("../data/teilaufgaben.csv")
    
    # Prepare data
    personen_df["kompetenzen_liste"] = personen_df["kompetenzen"].str.split(r",\s*")
    
    # Run algorithm
    results, time_taken = greedy_matching_with_fallback(teilaufgaben_df, personen_df)
    
    print(f"\nFinal Results:")
    print(f"Total assignments: {len(results)}")
    print(f"Total workload: {sum(item['zugewiesener_aufwand'] for item in results):.1f} hours")
