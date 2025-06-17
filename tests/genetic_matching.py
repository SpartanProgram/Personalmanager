import time
import pandas as pd
import numpy as np
import random
from typing import List, Dict, Tuple, Optional
from copy import deepcopy

def calculate_fitness(assignment, teilaufgaben_df, personen_df, belegungen=None):
    """
    Calculate fitness score for a given assignment
    Higher score = better assignment
    """
    if belegungen is None:
        belegungen = {}
    
    total_score = 0
    constraint_penalty = 0
    
    # Create temporary availability tracker
    temp_belegungen = deepcopy(belegungen)
    
    for task_idx, person_idx in enumerate(assignment):
        if person_idx >= len(personen_df):
            continue
            
        ta = teilaufgaben_df.iloc[task_idx]
        person = personen_df.iloc[person_idx]
        
        # Check skill match
        if ta["kompetenz"] not in person["kompetenzen_liste"]:
            constraint_penalty += 1000  # Heavy penalty for skill mismatch
            continue
        
        # Check availability
        ta_start = int(ta["start"].split("/")[0])
        ta_ende = int(ta["ende"].split("/")[0])
        ta_monate = ta_ende - ta_start + 1
        ta_monatsaufwand = ta["aufwand"] / ta_monate
        
        person_id = person["id"]
        if person_id not in temp_belegungen:
            temp_belegungen[person_id] = {}
        
        # Check monthly availability
        available_hours = 0
        for monat in range(ta_start, ta_ende + 1):
            monat_label = f"{monat:02d}/2025"
            
            # Check project conflicts
            belegung_label = f"projektbelegung_{monat_label}"
            aktuelle_belegung = person.get(belegung_label, "Frei")
            
            if aktuelle_belegung not in ["Frei", ta["projekt_id"]]:
                constraint_penalty += 500  # Penalty for project conflict
                continue
            
            # Check availability
            verfügbarkeit = person.get(f"verfuegbarkeit_{monat_label}", 0)
            belegt = temp_belegungen[person_id].get(monat_label, 0)
            rest = max(0, verfügbarkeit - belegt)
            available_hours += rest
        
        if available_hours >= ta["aufwand"]:
            # Good assignment - calculate positive score
            skill_bonus = 2.0 if ta["kompetenz"] in person["kompetenzen_liste"] else 1.0
            availability_score = available_hours * person["zeitbudget"] * skill_bonus
            total_score += availability_score
            
            # Update availability
            for monat in range(ta_start, ta_ende + 1):
                monat_label = f"{monat:02d}/2025"
                temp_belegungen[person_id][monat_label] = temp_belegungen[person_id].get(monat_label, 0) + ta_monatsaufwand
        else:
            constraint_penalty += 200  # Penalty for insufficient availability
    
    # Calculate workload coverage bonus
    assigned_workload = sum(ta["aufwand"] for i, ta in enumerate(teilaufgaben_df.iterrows()) 
                          if assignment[i] < len(personen_df) and 
                          ta[1]["kompetenz"] in personen_df.iloc[assignment[i]]["kompetenzen_liste"])
    total_workload = teilaufgaben_df["aufwand"].sum()
    coverage_bonus = (assigned_workload / total_workload) * 1000
    
    return total_score + coverage_bonus - constraint_penalty

def create_initial_population(population_size, num_tasks, num_people):
    """
    Create initial population of random assignments
    """
    population = []
    for _ in range(population_size):
        # Create random assignment: each task gets assigned to a random person
        assignment = [random.randint(0, num_people - 1) for _ in range(num_tasks)]
        population.append(assignment)
    return population

def tournament_selection(population, fitness_scores, tournament_size=3):
    """
    Select parent using tournament selection
    """
    tournament_indices = random.sample(range(len(population)), tournament_size)
    tournament_fitness = [fitness_scores[i] for i in tournament_indices]
    winner_idx = tournament_indices[tournament_fitness.index(max(tournament_fitness))]
    return population[winner_idx]

def crossover(parent1, parent2, crossover_rate=0.8):
    """
    Perform crossover between two parents
    """
    if random.random() > crossover_rate:
        return parent1, parent2
    
    # Single-point crossover
    crossover_point = random.randint(1, len(parent1) - 1)
    child1 = parent1[:crossover_point] + parent2[crossover_point:]
    child2 = parent2[:crossover_point] + parent1[crossover_point:]
    
    return child1, child2

def mutate(assignment, mutation_rate=0.1, num_people=None):
    """
    Perform mutation on an assignment
    """
    if num_people is None:
        num_people = max(assignment) + 1
    
    mutated = assignment.copy()
    for i in range(len(mutated)):
        if random.random() < mutation_rate:
            mutated[i] = random.randint(0, num_people - 1)
    
    return mutated

def genetic_algorithm_matching(teilaufgaben_df, personen_df, population_size=50, generations=100, 
                             mutation_rate=0.1, crossover_rate=0.8, tournament_size=3):
    """
    Genetic Algorithm for optimal assignment
    
    Args:
        teilaufgaben_df: DataFrame with tasks
        personen_df: DataFrame with people
        population_size: Size of the population
        generations: Number of generations to evolve
        mutation_rate: Probability of mutation
        crossover_rate: Probability of crossover
        tournament_size: Size of tournament for selection
        
    Returns:
        tuple: (list of matching results, execution time)
    """
    print("\n=== Genetic Algorithm ===")
    start_time = time.time()
    
    num_tasks = len(teilaufgaben_df)
    num_people = len(personen_df)
    
    # Create initial population
    population = create_initial_population(population_size, num_tasks, num_people)
    
    best_fitness = float('-inf')
    best_assignment = None
    
    print(f"Population size: {population_size}")
    print(f"Generations: {generations}")
    print(f"Tasks: {num_tasks}, People: {num_people}")
    
    # Evolution loop
    for generation in range(generations):
        # Calculate fitness for all individuals
        fitness_scores = []
        for assignment in population:
            fitness = calculate_fitness(assignment, teilaufgaben_df, personen_df)
            fitness_scores.append(fitness)
            
            # Track best solution
            if fitness > best_fitness:
                best_fitness = fitness
                best_assignment = assignment.copy()
        
        # Create new population
        new_population = []
        
        # Elitism: keep best individual
        best_idx = fitness_scores.index(max(fitness_scores))
        new_population.append(population[best_idx])
        
        # Generate rest of population
        while len(new_population) < population_size:
            # Selection
            parent1 = tournament_selection(population, fitness_scores, tournament_size)
            parent2 = tournament_selection(population, fitness_scores, tournament_size)
            
            # Crossover
            child1, child2 = crossover(parent1, parent2, crossover_rate)
            
            # Mutation
            child1 = mutate(child1, mutation_rate, num_people)
            child2 = mutate(child2, mutation_rate, num_people)
            
            new_population.extend([child1, child2])
        
        # Trim to population size
        population = new_population[:population_size]
        
        # Progress reporting
        if generation % 20 == 0 or generation == generations - 1:
            avg_fitness = np.mean(fitness_scores)
            print(f"Generation {generation}: Best={best_fitness:.1f}, Avg={avg_fitness:.1f}")
    
    # Convert best assignment to results format
    matching_results = []
    for task_idx, person_idx in enumerate(best_assignment):
        if person_idx < len(personen_df):
            ta = teilaufgaben_df.iloc[task_idx]
            person = personen_df.iloc[person_idx]
            
            matching_results.append({
                "teilaufgabe_id": ta["teilaufgabe_id"],
                "teilaufgabe": ta["bezeichnung"],
                "projekt_id": ta["projekt_id"],
                "kompetenz": ta["kompetenz"],
                "person_id": person["id"],
                "name": person["name"],
                "zugewiesener_aufwand": ta["aufwand"],
                "score": best_fitness
            })
    
    execution_time = time.time() - start_time
    
    print(f"Execution time: {execution_time:.3f} seconds")
    print(f"Best fitness: {best_fitness:.1f}")
    print(f"Found assignments: {len(matching_results)}")
    
    return matching_results, execution_time

def genetic_matching_with_elite(teilaufgaben_df, personen_df, population_size=100, generations=200):
    """
    Enhanced genetic algorithm with elite preservation and adaptive parameters
    """
    print("\n=== Enhanced Genetic Algorithm ===")
    start_time = time.time()
    
    # Run multiple times with different parameters and keep best result
    best_result = None
    best_fitness = float('-inf')
    
    # Parameter combinations to try
    param_combinations = [
        {"population_size": 50, "generations": 100, "mutation_rate": 0.1},
        {"population_size": 100, "generations": 150, "mutation_rate": 0.05},
        {"population_size": 75, "generations": 200, "mutation_rate": 0.15},
    ]
    
    for i, params in enumerate(param_combinations):
        print(f"\nTrying parameter set {i+1}/{len(param_combinations)}")
        results, _ = genetic_algorithm_matching(
            teilaufgaben_df, personen_df, **params
        )
        
        # Calculate fitness of this result
        assignment = []
        for result in results:
            task_idx = teilaufgaben_df[teilaufgaben_df['teilaufgabe_id'] == result['teilaufgabe_id']].index[0]
            person_idx = personen_df[personen_df['id'] == result['person_id']].index[0]
            assignment.append(person_idx)
        
        # Pad assignment if needed
        while len(assignment) < len(teilaufgaben_df):
            assignment.append(random.randint(0, len(personen_df) - 1))
        
        fitness = calculate_fitness(assignment, teilaufgaben_df, personen_df)
        
        if fitness > best_fitness:
            best_fitness = fitness
            best_result = results
    
    execution_time = time.time() - start_time
    return best_result, execution_time

if __name__ == "__main__":
    # Test the algorithm
    print("Testing Genetic Algorithm...")
    
    # Load data
    personen_df = pd.read_csv("../data/personen.csv")
    teilaufgaben_df = pd.read_csv("../data/teilaufgaben.csv")
    
    # Prepare data
    personen_df["kompetenzen_liste"] = personen_df["kompetenzen"].str.split(r",\s*")
    
    # Run algorithm
    results, time_taken = genetic_matching_with_elite(teilaufgaben_df, personen_df)
    
    print(f"\nFinal Results:")
    print(f"Total assignments: {len(results)}")
    print(f"Total workload: {sum(item['zugewiesener_aufwand'] for item in results):.1f} hours") 