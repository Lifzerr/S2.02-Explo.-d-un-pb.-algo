import json
import pandas as pd
import numpy as np
import os
import graphics as g 


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



dim = (1411,912)
point1 = (43.48478,-1.48768)
point2 = (43.4990,-1.45738)


# Calcul des coordonnées transformées
sommets['x'] = (sommets['lon'] - point1[1]) * dim[0] / (point2[1] - point1[1])
sommets['y'] = dim[1] - (sommets['lat'] - point1[0]) * dim[1] / (point2[0] - point1[0])


"""

for ind in aretes.index:
    tempoList = []
    tempoString = aretes.loc[ind]['lstpoints'].replace('[','')
    tempoString = tempoString.replace(']','')
    tempoString = tempoString.replace(' ','')
    tempoList = tempoString.split(',')
    aretes.at[ind,'listePoints'] = tempoList
    tempoList = []
    for pt in  aretes.at[ind,'listePoints'] :
        tempoList.append(int(pt))
    aretes.at[ind,'listePoints'] = tempoList
    aretes.at[ind,'sommetDepart'] = int(aretes.loc[ind,'listePoints'][0])
    aretes.at[ind,'sommetArrivee'] = int(aretes.loc[ind,'listePoints'][-1])

""
# Changement de type
arcs = arcs.astype({'sommetDepart': 'int64', 'sommetArrivee': 'int64'})
"""



def calculCoordPoint(point): 
     lat = sommets.loc[point, 'lat']
     lon = sommets.loc[point, 'lon']
     x = (lon - point1[1]) * dim[0] / (point2[1] - point1[1])
     y = (dim[1] - (lat - point1[0]) * dim[1] / (point2[0] - point1[0]))
     return x, y


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
    chemin = []
    sommet = arr
    while sommet != dep:
        chemin.insert(0, sommet)
        sommet = pred[sommet]
    chemin.insert(0, dep)

    return chemin


def dessinerArrete(dep, arr, win, color):

    x1, y1 = calculCoordPoint(dep)
    x2, y2 = calculCoordPoint(arr)
    
    arrete = g.Line(g.Point(x1, y1), g.Point(x2, y2))
    arrete.setFill(color)
    arrete.draw(win)
        

def dijkstraGraphique(graphe, depart, arrivee, win):
    # Initialisation
    distances = {sommet: float('inf') for sommet in graphe}
    distances[depart] = 0
    predecesseurs = {}
    non_traites = set(graphe.keys())
    saveSom = int()

    while non_traites:
        # Sélectionner le sommet non traité avec la plus petite distance
        sommet_courant = min(non_traites, key=lambda sommet: distances[sommet])
        non_traites.remove(sommet_courant)

        if sommet_courant == arrivee:
            break  # On a trouvé le chemin le plus court

        for voisin, poids in graphe[sommet_courant].items():  # On itère sur les voisins
            # Calculer la nouvelle distance
            nouvelle_distance = distances[sommet_courant] + poids
            
            # Dessiner le segment en noir pour montrer qu'on l'a testé
            dessinerArrete(sommet_courant, voisin, win, "red")

            # Vérifier si la nouvele distance est meilleure
            if nouvelle_distance < distances[voisin]:
                distances[voisin] = nouvelle_distance
                predecesseurs[voisin] = sommet_courant
                saveSom = voisin
                
         
        # Redessiner le segment le plus cours en rouge une fois car c'est le segment que nous gardons
        dessinerArrete(predecesseurs[saveSom], saveSom, win, "black")

    # Reconstruction du chemin le plus court
    chemin = reconstituer(predecesseurs, depart, arrivee)
    poids_total = distances[arrivee]
    
    return (chemin, poids_total)
"""
cheminDijkstra = dijkstraGraphique(graphe_transforme, 1806175538, 1801848709)
print("Chemin trouvé par l'algorithme de Dijkstra : ", cheminDijkstra[0], "\n",
      "\n",
      "Poid du chemin : ", cheminDijkstra[1],"\n")
"""


def affichageArcs():    
    for arc in aretes.index:
        
        listePoints = aretes.loc[arc, 'lstpoints']
        point1 = listePoints[0]
        point2 = listePoints[-1]
        traceArc(point1, point2)



def traceArc(point1, point2):
    lat1 = sommets.loc[point1, 'y']
    lon1 = sommets.loc[point1, 'x']
    lat2 = sommets.loc[point2, 'y']
    lon2 = sommets.loc[point2,'x']
    
    pt1 = g.Point(lon1, lat1)
    pt2 = g.Point(lon2, lat2)
    
    arc = g.Line(pt1, pt2)
    arc.draw(win)


def affichageBG():

    background = g.Image(g.Point(1411/2,912/2), "CaptureOpenStreetMap2024.png")
    background.draw(win)
    

#fenetre = affichageBG()




def affichagePts():
    for point in sommets.index:
        lat = sommets.loc[point, 'lat']
        lon = sommets.loc[point, 'lon']
        x = (lon - point1[1]) * dim[0] / (point2[1] - point1[1])
        y = (dim[1] - (lat - point1[0]) * dim[1] / (point2[0] - point1[0]))

        c = g.Circle(g.Point(x,y), 2)
        c.setFill(g.color_rgb(200,200,200))
        c.draw(win)
        
    affichageArcs()


win = g.GraphWin("Carte de Bayonne", 1411, 912)
affichageBG()
affichagePts()
# affichagePts(affichageBG())
