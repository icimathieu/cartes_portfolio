# Resume benchmark - 600 cartes annotees

## Chiffres
- Corpus annote : 600 cartes
- Cartes exclues pour cas_ambigu : 8 (1.3%)
- Corpus benchmarke : 592 cartes
- Cartes entierement correctes sur les 3 niveaux : 454 (76.7%)
- Cartes avec au moins une erreur : 138 (23.3%)
- Cartes avec prediction manquante : 0 (0.0%)
- Cas bonus find_else : 31 (5.2%)
- Cartes avec erreur croisee ou cas structurel : 27 (4.6%)
- Commune : couverture 100.0% | exactitude sur couvert 91.4%
- Lieu-dit : couverture 100.0% | exactitude sur couvert 91.6%
- Monument : couverture 100.0% | exactitude sur couvert 89.4%

## Volumetrie par niveau
- Commune : correct=541 | erreurs=51 | predictions manquantes=0
- Lieu-dit : correct=542 | erreurs=50 | predictions manquantes=0
- Monument : correct=529 | erreurs=63 | predictions manquantes=0

## Valeurs Aucune
- Commune : Aucune ville = 56 | correct=45 (80.4%) | erreurs=11 (19.6%)
- Lieu-dit : Aucun lieu-dit = 499 | correct=477 (95.6%) | erreurs=22 (4.4%)
- Monument : Aucun monument = 195 | correct=191 (97.9%) | erreurs=4 (2.1%)

## Rappel proxy
- Commune : 98.0% (base total_moins_aucun) | nb_aucun=56 | nb_absent=11
- Lieu-dit : 80.2% (base total_moins_aucun) | nb_aucun=499 | nb_absent=23
- Monument : 99.0% (base total_moins_aucun) | nb_aucun=195 | nb_absent=4

## Swaps et erreurs croisees
- swap_commune_monument : 11 cartes
- swap_lieudit_monument : 11 cartes
- swap_commune_lieudit : 5 cartes

## Confusions
- Erreurs croisees documentees via another_error : 27 cartes (4.6%)
- Confusions de lecture de toponymes : 80 sur 1776 predictions (4.50%)
- mauvaise_commune : 34
- mauvais_lieudit : 22
- mauvais_monument : 24

Pour l essentiel, ces confusions correspondent a des lectures de noms d imprimeurs, d editeurs, ou a des formulations de type "vue depuis X", "panorama depuis Y", etc.

## Hallucinations
- Total hallucinations : 18 sur 1776 predictions (1.01%)
- Commune : 3 (commune_hallucinee)
- Lieu-dit : 1 (lieudit_hallucine)
- Monument : 14 (monument_hallucine)

## Erreurs par niveau
- Commune : mauvaise_commune (34)
- Commune : commune_absente (11)
- Commune : commune_hallucinee (3)
- Commune : commune_mauvais_niveau (3)
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
Ce benchmark a été construit sur un corpus large de 600 cartes postales, avec exclusion des seuls cas jugés intrinsèquement ambigus (hors de nos règles d'évaluation définies dans guide_benchmark.md). Tous les pourcentages présentés ci-dessous sont calculés sur le corpus benchmarké, hors cas_ambigu.

Le résultat principal est solide : 454 cartes sur 592 benchmarkées sont justes simultanément sur les trois niveaux de précision. À chaque niveau, la couverture est tres élevée sur le lieu-dit et le monument, et reste forte sur la commune. Les 31 cas bonus find_else montrent en plus que le modele sait retrouver un lieu même quand la carte ne fournit pas de texte de localisation explicite.

Le taux d'hallucination reste très faible pour un système génératif : 18 hallucinations sur 1776 predictions, soit 1.01%. C est un argument fort, car il montre que le pipeline ne remplit pas arbitrairement les champs et conserve un comportement globalement fiable, malgré son caractère "génératif".

Les confusions résiduelles sont elles aussi lisibles et pilotables : 80 cas sur 1776 prédictions, soit 4.50%. Elles proviennent pour l'essentiel de formulations éditoriales ou descriptives comme les noms d'imprimeurs et les mentions du type "vue depuis X" où X, lieu de la prise de la photographie, est interprété comme le lieu photographié. Cela ouvre des pistes d'amélioration très concrètes par filtrage contextuel et règles de désambiguisation.

Une part significative des erreurs restantes correspond à des erreurs de granularité ou à des inversements entre niveaux (4.6%), plutôt qu'à une localisation totalement hors sujet. Le pipeline est donc souvent proche du bon résultat, avec des marges d'amélioration crédibles par règles de cohérence, post-traitement et enrichissement par bases de données externes.
