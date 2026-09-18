# Référentiel des communes françaises

Sert à `src/demo/lieux.py` : savoir quels noms sont des communes, lesquels sont des
départements, et lever les homonymes grâce au département imprimé sur la carte.
Embarqué dans l'application, donc **aucune requête réseau** n'est faite pour ça.

| Fichier | Contenu |
|---|---|
| `communes_france.csv` | 36 012 entrées : nom normalisé, nom officiel, code de département, coordonnées |
| `departements_france.csv` | 102 départements : nom normalisé, nom, code |

**Source** : jeu de données ouvert « Communes de France » (codes INSEE, codes postaux et
coordonnées, d'après INSEE et La Poste), réduit ici aux seules colonnes utiles.

1 579 noms de communes sont portés par plusieurs communes dans des départements
différents : sans département connu, `lieux.coordonnees()` refuse de trancher.
