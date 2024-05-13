import json
import pandas as pd
import numpy as np
import os
import graphics as g 


# os.chdir("C:\\IUT\\Semestre 2\\S2.02 - Explo algorithmique d'un problème\\partie3")
# os.chdir("E:\\Cours\\Semestre2\\S2.02\\S2.02-Explo.-d-un-pb.-algo\\partie3")
os.chdir("F:\\IUT\\1ereAnnee\\Semestre2\\S2.02\\S2.02-Explo.-d-un-pb.-algo\\partie3")

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







def affiche_graphe():
    # Création fenêtre graphique avec des dimensions adaptées à celles de l'image
    image_path = "CaptureOpenStreetMap2024.PNG"
    image = g.Image(g.Point(0, 0), image_path)  # Créez une instance de l'image pour obtenir ses dimensions
    image_width = image.getWidth()
    image_height = image.getHeight()
    

    win_width = image_width + 20  # Ajoutez une marge de 20 pixels pour plus d'espace
    win_height = image_height + 20
    
    # Calcul des coordonnées
    lat_min, lat_max = sommets['lat'].min(), sommets['lat'].max()
    lon_min, lon_max = sommets['lon'].min(), sommets['lon'].max()

    # Calculer les facteurs d'échelle pour convertir les coordonnées en x, y
    x_scale = (lon_max - lon_min) / image_width
    y_scale = (lat_max - lat_min) / image_height

    # Convertir les coordonnées de chaque sommet en x, y
    sommets['x'] = (sommets['lon'] - lon_min) / x_scale
    sommets['y'] = image_height - ((sommets['lat'] - lat_min) / y_scale)
    
    # Créer la fenetre
    win = g.GraphWin("Image Display", win_width, win_height)
    win.setCoords(0, 0, image_width, image_height)
        
    
    # Permettre le redimensionnement de la fenêtre
    win.master.resizable(True, True)

    # Chargez et affichez l'image dans la fenêtre graphique
    image.move(image_width / 2, image_height / 2)  # Déplacez l'image au centre de la fenêtre
    image.draw(win)
    
    # Afficher chaque point dans la fenêtre
    for _, row in sommets.iterrows():
        point = g.Point(row['x'], row['y'])
        point.draw(win)

    # Attendre que l'utilisateur clique pour fermer la fenêtre
    win.getMouse()

    # Fermer la fenêtre graphique lorsque l'utilisateur clique
    win.close()
    
    
affiche_graphe()