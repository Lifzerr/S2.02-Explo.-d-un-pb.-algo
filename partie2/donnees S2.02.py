import json
import pandas as pd
import numpy as np
import os


os.chdir("C:\\IUT\\Semestre 2\\S2.02 - Explo algorithmique d'un problème\\partie2")

# import dicsucc.json et dicsuccdist.json (--> dictionnaire)
with open("dicsucc.json", "r") as fichier:
    dicsucc = json.load(fichier)
with open("dicsuccdist.json", "r") as fichier:
    dicsuccdist = json.load(fichier)

# import aretes.csv (--> dataframe) et transformation de lstpoints (chaîne-->liste)
aretes = pd.read_table('aretes.csv', sep  =';', index_col= 0)

for ind in aretes.index :
    ls = aretes.loc[ind,'lstpoints'].replace(" ","").replace("]", "").replace("[", "").split(',')
    lst = []
    for val in ls :
        lst.append(int(val))
    aretes.at[ind,'lstpoints'] = lst


# import sommets.csv, matrice_poids.csv (--> dataframe)
sommets = pd.read_table('sommets.csv', sep  =';', index_col= 0)
matrice_poids = pd.read_csv('matrice_poids.csv', sep = ';', index_col = 0)

# transformation dataframe matrice des poids en tableau    
tableau_poids = np.array(matrice_poids)

# transformation matrice des poids en liste de listes
liste_poids = [[None for j in range(len(tableau_poids))] for i in range(len(tableau_poids))]
for i in range(len(tableau_poids)):
    for j in range(len(tableau_poids)):
        liste_poids[i][j]  = tableau_poids[i,j]


del fichier, i, j, val, ls, lst, ind 




def dijkstra(graphe, depart, arrivee):
    # Initialisation
    distances = {sommet: float('inf') for sommet in graphe}
    distances[depart] = 0
    predecesseurs = {}
    non_traites = set(graphe)

    while non_traites:
        # Sélectionner le sommet non traité avec la plus petite distance
        sommet_courant = min(non_traites, key=lambda sommet: distances[sommet])
        non_traites.remove(sommet_courant)

        if sommet_courant == arrivee:
            break  # On a trouvé le chemin le plus court

        for voisin in graphe[sommet_courant]:
            # Calculer la nouvelle distance
            nouvelle_distance = distances[sommet_courant] + graphe[sommet_courant][voisin]

            if nouvelle_distance < distances[voisin]:
                distances[voisin] = nouvelle_distance
                predecesseurs[voisin] = sommet_courant

    # Reconstruction du chemin le plus court
    chemin = []
    sommet = arrivee
    while sommet in predecesseurs:
        chemin.insert(0, sommet)
        sommet = predecesseurs[sommet]
    chemin.insert(0, depart)

    return chemin


def bellman_ford_dictionnaires(graphe, depart):
    # Initialisation
    distances = {sommet: float('inf') for sommet in graphe}
    distances[depart] = 0
    predecesseurs = {}
    
    # Relachement des arêtes
    for _ in range(len(graphe) - 1):
        for sommet in graphe:
            for voisin in graphe[sommet]:
                poids = graphe[sommet][voisin]
                if distances[sommet] + poids < distances[voisin]:
                    distances[voisin] = distances[sommet] + poids
                    predecesseurs[voisin] = sommet
    
    # Détection de cycle négatif
    for sommet in graphe:
        for voisin in graphe[sommet]:
            poids = graphe[sommet][voisin]
            if distances[sommet] + poids < distances[voisin]:
                return "Cycle négatif détecté"
    
    return distances, predecesseurs


def bellman_ford_liste(liste_aretes, nombre_sommets, depart):
    # Initialisation
    distances = [float('inf')] * nombre_sommets
    distances[depart] = 0
    predecesseurs = {}

    # Relaxation des arêtes
    for _ in range(nombre_sommets - 1):
        for u, v, poids in liste_aretes:
            if distances[u] + poids < distances[v]:
                distances[v] = distances[u] + poids
                predecesseurs[v] = u

    # Détection de cycle négatif
    for u, v, poids in liste_aretes:
        if distances[u] + poids < distances[v]:
            return "Cycle négatif détecté"

    return distances, predecesseurs