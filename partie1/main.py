

import pandas as pd
import matplotlib.pyplot as plt
from math import pi, cos, acos, sin, asin
import numpy as np
import time


#########################################################
# calcul de la distance entre deux points A et B dont  #
# on connait la lattitude et la longitude               #
#########################################################
def distanceGPS(latA,latB,longA,longB):
    # Conversions des latitudes en radians
    ltA=latA/180*pi
    ltB=latB/180*pi
    loA=longA/180*pi
    loB=longB/180*pi
    # Rayon de la terre en mètres 
    RT = 6378137
    # angle en radians entre les 2 points
    S = acos(round(sin(ltA)*sin(ltB) + cos(ltA)*cos(ltB)*cos(abs(loB-loA)),20)) # 4 poids à 0 si on arrondi à 14
    # distance entre les 2 points, comptée sur un arc de grand cercle
    return S*RT

# Import des arcs dans un dataframe
arcs = pd.read_csv("arcs.csv", encoding="ANSI", sep=";", index_col='id_arc')


# Ajout des nouvelles colonnes
arcs['listePoints'] = None
arcs['sommetDepart'] = None
arcs['sommetArrivee'] = None
arcs['numeroSommetDepart'] = None
arcs['numeroSommetArrivee'] = None
arcs['poid'] = None


# Création des variables temporaires
tempoInt = ''
tempoString = 0
tempoList = []

compteur = 0


# Transformation de la chaine de caractère en liste réelle,
# Puis sélection des sommets de départs etr d'arrivée dans tous les arcs
for ind in arcs.index:
    tempoList = []
    tempoString = arcs.loc[ind]['lstpoints'].replace('[','')
    tempoString = tempoString.replace(']','')
    tempoString = tempoString.replace(' ','')
    tempoList = tempoString.split(',')
    arcs.at[ind,'listePoints'] = tempoList
    tempoList = []
    for pt in  arcs.at[ind,'listePoints'] :
        tempoList.append(int(pt))
    arcs.at[ind,'listePoints'] = tempoList
    arcs.at[ind,'sommetDepart'] = int(arcs.loc[ind,'listePoints'][0])
    arcs.at[ind,'sommetArrivee'] = int(arcs.loc[ind,'listePoints'][-1])


# Changement de type
arcs = arcs.astype({'sommetDepart': 'int64', 'sommetArrivee': 'int64'})


# Création de la liste des sommets distincts
listeSommets = []

for ind in arcs.index:    
    if arcs.loc[ind, 'sommetDepart'] not in listeSommets:
        listeSommets.append(arcs.loc[ind, 'sommetDepart'])
    if arcs.loc[ind, 'sommetArrivee'] not in listeSommets:
        listeSommets.append(arcs.loc[ind, 'sommetArrivee'])

# Import dans dataframe sommets
sommets = pd.DataFrame(listeSommets, columns=['Sommet'])


# Matrice d'adjacense

NB_SOMMETS = len(listeSommets)

numeroSommet = [i for i in range(NB_SOMMETS)]

sommets['numeroSommet'] = numeroSommet

sommets = sommets.set_index('Sommet')

matrice = [[0] * NB_SOMMETS for _ in range(NB_SOMMETS)]

for ind in arcs.index:
    arcs.loc[ind, 'numeroSommetDepart'] = sommets.loc[arcs.loc[ind, 'sommetDepart'], 'numeroSommet']
    arcs.loc[ind, 'numeroSommetArrivee'] = sommets.loc[arcs.loc[ind, 'sommetArrivee'], 'numeroSommet']

arcs = arcs.astype({'numeroSommetDepart': 'int64', 'numeroSommetArrivee': 'int64'})

for ind in arcs.index:
    matrice[arcs.loc[ind, 'numeroSommetDepart']][arcs.loc[ind, 'numeroSommetArrivee']] = 1
    matrice[arcs.loc[ind, 'numeroSommetArrivee']][arcs.loc[ind, 'numeroSommetDepart']] = 1


# Import des arcs dans un dataframe
points = pd.read_csv("points.csv", encoding="ANSI", sep=";", index_col='id_point')

# Ajout de lat et long à sommets
sommets['lat'] = points['lat']
sommets['lon'] = points['lon']

# Calculer le poid
for ind in arcs.index:
    poid = 0
    for i in range(len(arcs.loc[ind, 'listePoints']) - 1):
        latA = points.loc[arcs.loc[ind, 'listePoints'][i], 'lat']
        latB = points.loc[arcs.loc[ind, 'listePoints'][i + 1], 'lat']
        lonA = points.loc[arcs.loc[ind, 'listePoints'][i], 'lon']
        lonB = points.loc[arcs.loc[ind, 'listePoints'][i + 1], 'lon']
        poid = poid + distanceGPS(latA, latB, lonA, lonB)
    arcs.loc[ind, 'poid'] = poid

arcs = arcs.astype({'poid': 'float64'})

# Matrice pondérée

start = time.time()
matricePonderee = [[0] * NB_SOMMETS for _ in range(NB_SOMMETS)]

for ind in arcs.index:
    matricePonderee[arcs.loc[ind, 'numeroSommetDepart']][arcs.loc[ind, 'numeroSommetArrivee']] = arcs.loc[ind, 'poid']
    matricePonderee[arcs.loc[ind, 'numeroSommetArrivee']][arcs.loc[ind, 'numeroSommetDepart']] = arcs.loc[ind, 'poid']
end = time.time()

dureematrice =  end - start 
print('Exécution matrice pondérée : ', dureematrice)

# Dico pondéré par id

dicoPondId = {}

for ind in arcs.index:
    if arcs.loc[ind, 'sommetDepart'] not in dicoPondId.keys():
        dicoPondId[arcs.loc[ind, 'sommetDepart']] = {}
    if arcs.loc[ind, 'sommetArrivee'] not in dicoPondId.keys():
        dicoPondId[arcs.loc[ind, 'sommetArrivee']] = {}
    dicoPondId[arcs.loc[ind, 'sommetDepart']][arcs.loc[ind, 'sommetArrivee']] = arcs.loc[ind, 'poid']
    dicoPondId[arcs.loc[ind, 'sommetArrivee']][arcs.loc[ind, 'sommetDepart']] = arcs.loc[ind, 'poid']


# Dico pondéré par num

dicoPondNum = {}

for ind in arcs.index:
    if arcs.loc[ind, 'numeroSommetDepart'] not in dicoPondNum.keys():
        dicoPondNum[arcs.loc[ind, 'numeroSommetDepart']] = {}
    if arcs.loc[ind, 'numeroSommetArrivee'] not in dicoPondNum.keys():
        dicoPondNum[arcs.loc[ind, 'numeroSommetArrivee']] = {}
    dicoPondNum[arcs.loc[ind, 'numeroSommetDepart']][arcs.loc[ind, 'numeroSommetArrivee']] = arcs.loc[ind, 'poid']
    dicoPondNum[arcs.loc[ind, 'numeroSommetArrivee']][arcs.loc[ind, 'numeroSommetDepart']] = arcs.loc[ind, 'poid']


# Nettoyer le code
del compteur
del i
del ind
del latA
del latB
del lonA
del lonB
del poid
del pt
del tempoInt
del tempoList
del tempoString


debut = time.time()

rows = len(matrice)
cols = len(matrice)

arr = np.empty((rows, cols))

for ind in arcs.index:
    arr[arcs.loc[ind, 'numeroSommetDepart']][arcs.loc[ind, 'numeroSommetArrivee']] = arcs.loc[ind, 'poid']
    arr[arcs.loc[ind, 'numeroSommetArrivee']][arcs.loc[ind, 'numeroSommetDepart']] = arcs.loc[ind, 'poid']

fin = time.time()

dureeArray = fin - debut 

print('Duree Array : ', dureeArray)

deb = time.time()

# Définir la taille du DataFrame
rows = len(matrice)
cols = len(matrice)

# Créer un DataFrame vide avec la taille prédéfinie
df = pd.DataFrame(index=range(rows), columns=range(cols))

# Remplir le DataFrame avec float('inf')
df = df.fillna(float('inf'))

for ind in arcs.index:
    df[arcs.loc[ind, 'numeroSommetDepart']][arcs.loc[ind, 'numeroSommetArrivee']] = arcs.loc[ind, 'poid']
    df[arcs.loc[ind, 'numeroSommetArrivee']][arcs.loc[ind, 'numeroSommetDepart']] = arcs.loc[ind, 'poid']

df.index = sommets.index
df.columns = sommets.index
term = time.time()

dureeDf = term - deb 

print ('Duree génération Dataframe : ', dureeDf)



 






