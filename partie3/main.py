import json
import pandas as pd
import numpy as np
import os
import graphics as g 
import time as t


# os.chdir("C:\\IUT\\Semestre 2\\S2.02 - Explo algorithmique d'un problème\\partie3")
# os.chdir("E:\\Cours\\Semestre2\\S2.02\\S2.02-Explo.-d-un-pb.-algo\\partie3")
# os.chdir("F:\\IUT\\1ereAnnee\\Semestre2\\S2.02\\S2.02-Explo.-d-un-pb.-algo\\partie3")

# import dicsucc.json et dicsuccdist.json (--> dictionnaire)
with open("dicsucc.json", "r") as fichier:
    dicsucc = json.load(fichier)
with open("dicsuccdist.json", "r") as fichier:
    dicsuccdist = json.load(fichier)

# import aretes.csv (--> dataframe) et transformation de lstpoints (chaîne-->liste)
aretes = pd.read_table('aretes.csv', sep  =';', index_col= 0)


# Remplacer les string par des listes d'entiers
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

# Nettoyage des variables
del fichier, i, j, val, ls, lst, ind 


# Données nécessaires au placement des points & aretes
dim = (1411,912)
point1 = (43.48478,-1.48768)
point2 = (43.4990,-1.45738)


# Calcul des coordonnées transformées
sommets['x'] = (sommets['lon'] - point1[1]) * dim[0] / (point2[1] - point1[1])
sommets['y'] = dim[1] - (sommets['lat'] - point1[0]) * dim[1] / (point2[0] - point1[0])



def calculLatLonPoint(point):
    """ But : Calculer les coordonnées géographique de point point fourni en paramètre,
            Ce qui nous permettra de vérifier quel est le point le plus proche pour le programme qui 
            trace le chemin en fonction des clics"""
    x = point.x
    y = point.y
    lon = (x * (point2[1] - point[1]) / dim[0]) + point[1]
    lat = (-1 * (((y - dim[1]) * (point2[0] - point1[0])) / dim[1]) - point1[0])
    return lat, lon


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

import math
from math import acos,asin,cos,sin,pi

def choisirArriverDepart():
    """ But : permettre à l'utilisateur de sélectionner sur la carte son point de départ et d'arrivée. """
    clicDep = win.getMouse()
    clicArr = win.getPoint()
    
    
    lat, lon = calculLatLonPoint(clicDep)
    sommetDep = None
    
    # Recherche du chemin le plus proche
    for row in sommets.items():
        if sommetDep == None or distanceGPS(lat, lon, row["lat"], row["lon"]) < distanceGPS(lat, lon, sommets.loc[sommetDep, "lat"], sommets.loc[sommetDep, "lon"]):
            sommetsDep = row.index()
    lat, lon = calculLatLonPoint(clicDep)
    sommetArr = None
    for row in sommets.items():
        if sommetArr == None or distanceGPS(lat, lon, row["lat"], row["lon"]) < distanceGPS(lat, lon, sommets.loc[sommetArr, "lat"], sommets.loc[sommetArr, "lon"]):
            sommetArr = row.index()
    return sommetDep, sommetArr

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

def reconstituer(pred, dep, arr):
    """ But : Reconstituer un chemin issu des algorithmes de Dijkstra ou Bellman & l'afficher """
    chemin = []
    sommet = arr
    if arr not in pred:
        print(f"Aucun chemin trouvé de {dep} à {arr}")
        return chemin
    
    # Reconstituer le chemin
    while sommet != dep:
        if sommet not in pred:
            print(f"Erreur : sommet {sommet} n'a pas de prédécesseur.")
            return []
        chemin.insert(0, sommet)
        sommet = pred[sommet]
    chemin.insert(0, dep)
    
    # Afficher le chemin
    for i in range(len(chemin)-1):
        point1 = chemin[i]
        point2 = chemin[i+1]
        # Dessiner l'arête sauvegardée en bleu
        traceArc(point1, point2, "blue", 2)

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
            
            # Dessiner l'arête visitée en rouge
            traceArc(sommet_courant, voisin, "red", 2)

            # Vérifier si la nouvele distance est meilleure
            if nouvelle_distance < distances[voisin]:
                distances[voisin] = nouvelle_distance
                predecesseurs[voisin] = sommet_courant

    # Reconstruction du chemin le plus court
    chemin = reconstituer(predecesseurs, depart, arrivee)
    poids_total = distances[arrivee]
    

def bellman(graphe, depart, arrivee):
    # Initialisation
    distances = {sommet: float('inf') for sommet in graphe}
    distances[depart] = 0
    predecesseurs = {}

    # Nombre de sommets dans le graphe
    nb_sommets = len(graphe)

    # Relachement des arêtes
    for etape in range(nb_sommets - 1):
        for sommet in graphe:
            for voisin, poids in graphe[sommet].items():
                if(etape == 1):
                    traceArc(sommet, voisin, "red", 2)
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



def aetoile(graphe, depart, arrivee):
    # Récupérer les coordonnées de la destination
    latB = sommets.loc[arrivee, 'lat']
    lonB = sommets.loc[arrivee, 'lon']

    # Déclaration de la sous-fonction interne heuristique
    def heuristique(sommet):
        return distanceGPS(sommets.loc[sommet, 'lat'], latB, sommets.loc[sommet, 'lon'], lonB)
    
    # Initialisation des distances et des prédécesseurs
    g_score = {sommet: float('inf') for sommet in graphe}
    g_score[depart] = 0
    
    f_score = {sommet: float('inf') for sommet in graphe}
    f_score[depart] = heuristique(depart)
    
    open_set = {depart}
    came_from = {}
    distanceChemin = 0
    
    while open_set:
        # Sélectionner le sommet non traité avec le plus petit f_score
        sommet_courant = min(open_set, key=lambda sommet: f_score[sommet])
        
        # Si on est arrivé au sommet de fin, reconstituer le chemin
        if sommet_courant == arrivee:
            chemin = []
            sommet = arrivee
            while sommet != depart:
                chemin.append(sommet)
                sommet = came_from.get(sommet)
                traceArc(chemin[-1], sommet, "blue", 2)
                distanceChemin += f_score[sommet]
                if sommet is None:
                    return []  # Return empty if there is no valid path
            chemin.append(depart)
            chemin.reverse()
            return (chemin, distanceChemin)
        
        open_set.remove(sommet_courant)
        
        # Vérifier quel est le point (à vol d'oiseau) le plus proche de l'arrivée
        for voisin, poids in graphe[sommet_courant].items():
            tentative_g_score = g_score[sommet_courant] + poids
            
            traceArc(sommet_courant, voisin, "red")
            
            if tentative_g_score < g_score[voisin]:
                came_from[voisin] = sommet_courant
                g_score[voisin] = tentative_g_score
                f_score[voisin] = g_score[voisin] + heuristique(voisin)
                if voisin not in open_set:
                    open_set.add(voisin)
    
    return None




def affichageArcs():    
    """ But : Afficher tous les arcs en rouge sur la carte """ 
    for arc in aretes.index:
        listePoints = aretes.loc[arc, 'lstpoints']
        point1 = listePoints[0]
        point2 = listePoints[-1]
        traceArc(point1, point2)



def traceArc(point1, point2, color = "black", width = 1):
    """ But : Afficher l'arc reliant les points point1 & point2 de la couleur color (noir par défaut) avec une ligne d'épaisseur width (par défaut égale à 1) """
    
    lat1 = sommets.loc[point1, 'y']
    lon1 = sommets.loc[point1, 'x']
    lat2 = sommets.loc[point2, 'y']
    lon2 = sommets.loc[point2,'x']
    
    pt1 = g.Point(lon1, lat1)
    pt2 = g.Point(lon2, lat2)
    
    arc = g.Line(pt1, pt2)
    arc.setFill(color)
    arc.setWidth(width)
    arc.draw(win)


def affichageBG():
    """ But : Afficher l'image en fond de la fenêtre """
    background = g.Image(g.Point(1411/2,912/2), "CaptureOpenStreetMap2024.png")
    background.draw(win)
    


def affichagePts():
    """ But : Afficher tous les points du dataframe sommets dans la fenêtre """
    for point in sommets.index:
        # récup & conversion coordonnées
        lat = sommets.loc[point, 'lat']
        lon = sommets.loc[point, 'lon']
        x = (lon - point1[1]) * dim[0] / (point2[1] - point1[1])
        y = (dim[1] - (lat - point1[0]) * dim[1] / (point2[0] - point1[0]))

        # Dessiner le points en cours
        c = g.Circle(g.Point(x,y), 2)
        c.setFill(g.color_rgb(200,200,200))
        c.draw(win)
    # Dessiner les aretes
    affichageArcs()


# Création de la fenetre
win = g.GraphWin("Carte de Bayonne", 1411, 912)

def main():
    """ 
    Description : Cette procédure affiche toutes les informations des dataframes sommets & aretes.
                Elle affiche ensuite le déroulement de l'algorithme de Dijkstra, puis attend un clic utilisateur.
                Une fois ce clic pressé, elle affiche le déroulement de l'algorithme de Bellman, et la procédure
                de clic se répète pour permettre l'affichage de l'algorithme A*
    """
    
    # Afficher l'image, les points et les aretes
    resetCarte()
    
    # Saisie à la sourie du départ et de l'arrivée
    choisirArriverDepart()
    
    # Exécuter l'algorithme de Dijkstra
    dijkstra(graphe_transforme, 1806175538, 1801848709)
    
    # Attendre le clic utilisateur
    point = win.getMouse()
    resetCarte()
    
    # Exécuter l'algorithme de bellman
    bellman(graphe_transforme, 1806175538, 1801848709)
    
    # Attendre le clic utilisateur
    point = win.getMouse()
    resetCarte()
    
    # Exécuter l'algorithme A*
    aetoile(graphe_transforme, 1806175538, 1801848709)
    
    # Attendre le clic utilisateur
    point = win.getMouse()
    
    win.close()
    


def resetCarte():
    """ But : Supprimer les trajets des algorithmes successifs & afficher la carte, les points, et les aretes  """"
    # Réafficher la fenetre d'origine
    affichageBG()
    affichagePts() 

main()








