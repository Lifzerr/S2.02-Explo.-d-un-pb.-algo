import json
import pandas as pd
import numpy as np
import os
import math
from math import acos,asin,cos,sin,pi


# os.chdir("C:\\IUT\\Semestre 2\\S2.02 - Explo algorithmique d'un problème\\partie2")
# os.chdir("E:\\Cours\\Semestre2\\S2.02\\S2.02-Explo.-d-un-pb.-algo\\partie2")

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
sommets['indice'] = [i for i in range(1884)]

# transformation dataframe matrice des poids en tableau    
tableau_poids = np.array(matrice_poids)

# transformation matrice des poids en liste de listes
liste_poids = [[None for j in range(len(tableau_poids))] for i in range(len(tableau_poids))]
for i in range(len(tableau_poids)):
    for j in range(len(tableau_poids)):
        liste_poids[i][j]  = tableau_poids[i,j]


del fichier, i, j, val, ls, lst, ind 


def distanceGPS(latA, latB, lonA, lonB):
    pi = math.pi
    sin = math.sin
    cos = math.cos
    acos = math.acos
    
    # Conversions des latitudes en radians
    ltA = latA / 180 * pi
    ltB = latB / 180 * pi
    loA = lonA / 180 * pi
    loB = lonB / 180 * pi
    
    # Rayon de la terre en mètres 
    RT = 6378137
    
    # angle en radians entre les 2 points
    S = acos(round(sin(ltA) * sin(ltB) + cos(ltA) * cos(ltB) * cos(abs(loB - loA)), 14))
    
    # distance entre les 2 points, comptée sur un arc de grand cercle
    return S * RT


def transformer_graphe(graphe):
    """ Le graphe d'origine incluait des clés en string, et nous préférons par simplicité les transformer en entier.
        De plus, les valeurs du dictionnaire d'origine étaient des listes de listes, et nous préférons, pour manipuler, des dictionnaires.
        Cette fonction transforme le dictionnaire dans la forme que nous le voulons"""
    nouveau_graphe = {}
    # On itère sur les sommet (et leurs successeurs)
    for sommet_str, voisins in graphe.items():
        sommet_int = int(sommet_str)     # Transformation de la clé
        nouveau_graphe[sommet_int] = {}  # Création du couple clé-valeur dans le nouveau dictionnaire
        for voisin, poids in voisins:
            nouveau_graphe[sommet_int][voisin] = poids  # Ajout dans le dictionnaire du voisins le poid de l'arc
    return nouveau_graphe

graphe_transforme = transformer_graphe(dicsuccdist)

def reconstituer(pred, dep, arr):
    chemin = []
    sommet = arr
    while sommet != dep:
        chemin.insert(0, sommet)
        sommet = pred[sommet]
    chemin.insert(0, dep)

    return chemin
    


def dijkstra(graphe, depart, arrivee):
    # Initialisation
    distances = {sommet: float('inf') for sommet in graphe}
    distances[depart] = 0
    predecesseurs = {}
    non_traites = set(graphe.keys())

    while non_traites:
        # Sélectionner le sommet non traité avec la plus petite distance
        sommet_courant = min(non_traites, key=lambda sommet: distances[sommet])
        non_traites.remove(sommet_courant)

        if sommet_courant == arrivee:
            break  # On a trouvé le chemin le plus court

        for voisin, poids in graphe[sommet_courant].items():  # On itère sur les voisins
            # Calculer la nouvelle distance
            nouvelle_distance = distances[sommet_courant] + poids

            # Vérifier si la nouvele distance est meilleure
            if nouvelle_distance < distances[voisin]:
                distances[voisin] = nouvelle_distance
                predecesseurs[voisin] = sommet_courant

    # Reconstruction du chemin le plus court
    return reconstituer(predecesseurs, depart, arrivee)


cheminTest = dijkstra(graphe_transforme, 1806175538, 1801848709)


def bellman(graphe, depart, arrivee):
    # Initialisation
    distances = {sommet: float('inf') for sommet in graphe}
    distances[depart] = 0
    predecesseurs = {}

    # Nombre de sommets dans le graphe
    nb_sommets = len(graphe)

    # Relachement des arêtes
    for _ in range(nb_sommets - 1):
        for sommet in graphe:
            for voisin, poids in graphe[sommet].items():
                if distances[sommet] + poids < distances[voisin]:
                    distances[voisin] = distances[sommet] + poids
                    predecesseurs[voisin] = sommet

    # Détection de cycle négatif
    for sommet in graphe:
        for voisin, poids in graphe[sommet].items():
            if distances[sommet] + poids < distances[voisin]:
                return "Cycle négatif détecté"

    # Reconstruction du chemin le plus court
    return reconstituer(predecesseurs, depart, arrivee)


chemin = bellman(graphe_transforme, 1806175538, 1801848709)



def floyd_warshall(graphe, depart, arrivee):
    # Initialisation de la matrice des distances
    nb_sommets = len(graphe)
    distances = {i: {j: float('inf') for j in range(nb_sommets)} for i in range(nb_sommets)}
    for sommet in graphe:
        distances[sommet][sommet] = 0
        for voisin, poids in graphe[sommet].items():
            distances[sommet][voisin] = poids

    # Algorithme de Floyd-Warshall
    for k in range(nb_sommets):
        for i in range(nb_sommets):
            for j in range(nb_sommets):
                distances[i][j] = min(distances[i][j], distances[i][k] + distances[k][j])

    # Retourner la distance entre le sommet de départ et le sommet d'arrivée
    return distances[depart][arrivee]

# distance = floyd_warshall(graphe_transforme, 1806175538, 1801848709)

import heapq

def a_star(graphe, depart, arrivee):
    # Calculer les distances à vol d'oiseau entre chaque sommet et l'arrivée
    distances_estimees = {sommet: distanceGPS(sommets.loc[sommet, 'lat'], sommets.loc[arrivee, 'lat'], sommets.loc[sommet, 'lon'], sommets.loc[arrivee, 'lon']) for sommet in graphe}
    
    # Initialisation
    ouverts = [(distances_estimees[depart], depart)]  # (estimation + distance réelle, sommet)
    fermes = set()
    predecesseurs = {}
    distances = {sommet: float('inf') for sommet in graphe}
    distances[depart] = 0
    
    while ouverts:
        _, sommet_courant = heapq.heappop(ouverts)
        
        if sommet_courant == arrivee:
            # Reconstruction du chemin le plus court
            chemin = []
            while sommet_courant != depart:
                chemin.append(sommet_courant)
                sommet_courant = predecesseurs[sommet_courant]
            chemin.append(depart)
            return chemin[::-1]
        
        fermes.add(sommet_courant)
        
        for voisin, poids in graphe[sommet_courant].items():
            if voisin in fermes:
                continue
            
            nouvelle_distance = distances[sommet_courant] + poids
            if nouvelle_distance < distances[voisin]:
                distances[voisin] = nouvelle_distance
                heapq.heappush(ouverts, (nouvelle_distance + distances_estimees[voisin], voisin))
                predecesseurs[voisin] = sommet_courant
    
    return None  # Pas de chemin trouvé

import time
# Lancement du chrono
startDijkstra = time.time()

a_star(graphe_transforme,1806175538, 1801848709 )

endDijkstra = time.time()
print("Temps d'exécution = ", endDijkstra - startDijkstra) 
