import json
import pandas as pd
import numpy as np
import os
import graphics as g 


os.chdir("C:\\IUT\\Semestre 2\\S2.02 - Explo algorithmique d'un problème\\partie3")
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



def affichageBG():
    win = g.GraphWin("Carte de Bayonne", 1411, 912)

    background = g.Image(g.Point(1411/2,912/2), "CaptureOpenStreetMap2024.png")
    background.draw(win)
    return win

#fenetre = affichageBG()




def affichagePts(win):
    for point in sommets.index:
        lat = sommets.loc[point, 'lat']
        lon = sommets.loc[point, 'lon']
        x = (lon - point1[1]) * dim[0] / (point2[1] - point1[1])
        y = (dim[1] - (lat - point1[0]) * dim[1] / (point2[0] - point1[0]))

        c = g.Circle(g.Point(x,y), 2)
        c.setFill(g.color_rgb(200,200,200))
        c.draw(win)
    return win
win = affichagePts(affichageBG())