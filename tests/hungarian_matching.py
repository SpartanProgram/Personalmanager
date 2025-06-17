import pandas as pd
import numpy as np
from scipy.optimize import linear_sum_assignment
import random
import math
import time

def calculate_person_score(person, ta, belegungen=None):
    """
    Calculate person score for a task
    """
    if belegungen is None:
        belegungen = {}
        
    ta_start = int(ta["start"].split("/")[0])
    ta_ende = int(ta["ende"].split("/")[0])
    
    # You'll need to implement this function or import it
    # For now, let's use a simple score calculation
    if ta["kompetenz"] in person["kompetenzen_liste"]:
        score = person["zeitbudget"] * 10  # Simple scoring
        return round(score, 2)
    
    return 0

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

# Only run test if file is run directly
if __name__ == "__main__":
    # Test code here
    personen_df = pd.read_csv("../data/personen.csv")
    teilaufgaben_df = pd.read_csv("../data/teilaufgaben.csv")
    personen_df["kompetenzen_liste"] = personen_df["kompetenzen"].str.split(r",\s*")
    
    # Test Hungarian Algorithm
    hungarian_results, hungarian_time = hungarian_matching(teilaufgaben_df, personen_df)
    print("Test completed!")