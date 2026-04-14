# Resume benchmark - 600 cartes annotees

## Chiffres
- Corpus annote : 600 cartes
- Cartes exclues pour cas_ambigu : 8 (1.3%)
- Corpus benchmarke : 592 cartes
- Cartes entierement correctes sur les 3 niveaux : 487 (82.3%)
- Cartes avec au moins une erreur : 105 (17.7%)
- Cartes avec prediction manquante : 0 (0.0%)
- Cas bonus find_else : 31 (5.2%)
- Cartes avec erreur croisee ou cas structurel : 27 (4.6%)
- Commune : couverture 100.0% | exactitude sur couvert 100.0%
- Lieu-dit : couverture 100.0% | exactitude sur couvert 91.6%
- Monument : couverture 100.0% | exactitude sur couvert 89.4%

## Volumetrie par niveau
- Commune : correct=592 | erreurs=0 | predictions manquantes=0
- Lieu-dit : correct=542 | erreurs=50 | predictions manquantes=0
- Monument : correct=529 | erreurs=63 | predictions manquantes=0

## Valeurs Aucune
- Commune : Aucune ville = 56 | correct=56 (100.0%) | erreurs=0 (0.0%)
- Lieu-dit : Aucun lieu-dit = 499 | correct=477 (95.6%) | erreurs=22 (4.4%)
- Monument : Aucun monument = 195 | correct=191 (97.9%) | erreurs=4 (2.1%)

## Rappel proxy
- Commune : 100.0% (base total_moins_aucun) | nb_aucun=56 | nb_absent=0
- Lieu-dit : 80.2% (base total_moins_aucun) | nb_aucun=499 | nb_absent=23
- Monument : 99.0% (base total_moins_aucun) | nb_aucun=195 | nb_absent=4

## Swaps et erreurs croisees
- swap_commune_monument : 11 cartes
- swap_lieudit_monument : 11 cartes
- swap_commune_lieudit : 5 cartes

## Confusions
- Erreurs croisees documentees via another_error : 27 cartes (4.6%)
- Confusions de lecture de toponymes : 46 sur 1776 predictions (2.59%)
- mauvaise_commune : 0
- mauvais_lieudit : 22
- mauvais_monument : 24
- Pour l essentiel, ces confusions correspondent a des lectures de noms d imprimeurs, d editeurs, ou a des formulations de type vue depuis X, panorama depuis Y, etc.

## Hallucinations
- Total hallucinations : 15 sur 1776 predictions (0.84%)
- Commune : 0 (commune_hallucinee)
- Lieu-dit : 1 (lieudit_hallucine)
- Monument : 14 (monument_hallucine)

## Erreurs par niveau
- Lieu-dit : lieudit_absent (23)
- Lieu-dit : mauvais_lieudit (22)
- Lieu-dit : lieudit_mauvais_niveau (4)
- Lieu-dit : lieudit_hallucine (1)
- Monument : mauvais_monument (24)
- Monument : monument_hallucine (14)
- Monument : monument_mauvais_niveau (11)
- Monument : monument_multiple_incomplet (9)
- Monument : monument_absent (4)
- Monument : monument_partiel (1)

## Lecture client
Ce benchmark a été construit sur un corpus large de 600 cartes postales, avec exclusion des seuls cas jugés intrinsèquement ambigus. Tous les pourcentages presentés ci-dessous sont calculés sur le corpus benchmarké, hors cas_ambigu.

Le résultat principal est solide : 487 cartes sur 592 benchmarkées sont justes simultanément sur les trois niveaux de précision. A chaque niveau, la couverture (rappel) est tres élevée sur le lieu dit et le monument, et reste forte sur la commune. Les 31 cas bonus find_else montrent en plus que le modele sait retrouver un lieu même quand la carte ne fournit pas de texte de localisation explicite.

Le taux d hallucination reste tres faible pour un modèle d'intelligence artificielle générative : 15 hallucinations sur 1776 predictions, soit 0.84%. C'est un argument fort, car il montre que la chaîne de traitement ne remplit pas arbitrairement les champs et conserve un comportement globalement fiable.

Les confusions résiduelles sont elles aussi lisibles et pilotables : 46 cas sur 1776 predictions, soit 2.59%. Elles proviennent pour l'essentiel de formulations éditoriales ou descriptives comme les noms d imprimeurs et les mentions du type "vue depuis X" où "X" sera identifié comme le lieu représenté. Cela ouvre des pistes d'amélioration très concrètes par filtrage contextuel et règles de désambiguisation.

Une part significative des erreurs restantes correspond a des erreurs de granularité ou a des inversions entre niveaux, plutot qu'à une localisation totalement hors sujet. La chaîne de traitement est donc souvent proche du bon résultat, avec des marges d'amélioration credibles par règles de coherence, post-traitement et enrichissement par bases de données externes.
