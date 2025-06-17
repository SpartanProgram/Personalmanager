import time
import numpy as np
from scipy.optimize import linear_sum_assignment

def calculate_person_score(person, ta):
    """
    Berechnet den Score für eine Person-Aufgabe Kombination
    """
    # Basis-Score basierend auf Kompetenz-Match
    base_score = 100 if ta["kompetenz"] in person["kompetenzen_liste"] else 0
    
    # Verfügbarkeits-Score (vereinfacht)
    availability_score = 0
    for col in person.index:
        if col.startswith("verfuegbarkeit_"):
            availability_score += person[col]
    
    return base_score + availability_score * 0.1

def hungarian_matching(teilaufgaben_df, personen_df):
    """
    Hungarian Algorithm for optimal assignment
    """
    print("\n=== Hungarian Algorithm ===")
    start_time = time.time()
    
    # Create cost matrix (negative scores for maximization)
    n_tasks = len(teilaufgaben_df)
    n_people = len(personen_df)
    cost_matrix = np.zeros((n_tasks, n_people))
    
    # Fill cost matrix
    for i, ta in teilaufgaben_df.iterrows():
        for j, person in personen_df.iterrows():
            if ta["kompetenz"] in person["kompetenzen_liste"]:
                score = calculate_person_score(person, ta)
                cost_matrix[i, j] = -score  # Negative for minimization
            else:
                cost_matrix[i, j] = -999999  # Very high cost for incompatible
    
    # Solve assignment problem
    row_indices, col_indices = linear_sum_assignment(cost_matrix)
    
    # Create results
    matching_results = []
    total_score = 0
    
    for task_idx, person_idx in zip(row_indices, col_indices):
        ta = teilaufgaben_df.iloc[task_idx]
        person = personen_df.iloc[person_idx]
        score = -cost_matrix[task_idx, person_idx]  # Back to positive
        
        if score > 0:
            matching_results.append({
                "teilaufgabe_id": ta["teilaufgabe_id"],
                "teilaufgabe": ta["bezeichnung"],
                "projekt_id": ta["projekt_id"],
                "kompetenz": ta["kompetenz"],
                "person_id": person["id"],
                "name": person["name"],
                "zugewiesener_aufwand": ta["aufwand"],
                "score": score
            })
            total_score += score
    
    execution_time = time.time() - start_time
    
    print(f"Execution time: {execution_time:.3f} seconds")
    print(f"Found assignments: {len(matching_results)}")
    print(f"Total score: {total_score:.2f}")
    
    return matching_results, execution_time