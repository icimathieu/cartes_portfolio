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
Ce benchmark a ete construit sur un corpus large de 600 cartes postales, avec exclusion des seuls cas juges intrinsequement ambigus (hors de nos règles d'évaluation définies dans guide_benchmark.md). Tous les pourcentages presentes ci dessous sont calcules sur le corpus benchmarke, hors cas_ambigu.

Le resultat principal est solide : 454 cartes sur 592 benchmarkees sont justes simultanement sur les trois niveaux de precision. A chaque niveau, la couverture est tres elevee sur le lieu dit et le monument, et reste forte sur la commune. Les 31 cas bonus find_else montrent en plus que le modele sait retrouver un lieu meme quand la carte ne fournit pas de texte de localisation explicite.

Le taux d hallucination reste tres faible pour un systeme generatif : 18 hallucinations sur 1776 predictions, soit 1.01%. C est un argument fort en contexte client, car il montre que le pipeline ne remplit pas arbitrairement les champs et conserve un comportement globalement fiable.

Les confusions residuelles sont elles aussi lisibles et pilotables : 80 cas sur 1776 predictions, soit 4.50%. Elles proviennent pour l essentiel de formulations editoriales ou descriptives comme les noms d imprimeurs et les mentions du type vue depuis X. Cela ouvre des pistes d amelioration tres concretes par filtrage contextuel et regles de desambiguisation.

Une part significative des erreurs restantes correspond a des erreurs de granularite ou a des swaps entre niveaux (4.6%), plutot qu a une localisation totalement hors sujet. Le pipeline est donc souvent proche du bon resultat, avec des marges d amelioration credibles par regles de coherence, post traitement et enrichissement par bases externes.

### 1. Vue d ensemble
Le graphique ci dessous synthetise la couverture et l exactitude sur cartes couvertes pour les trois niveaux de precision. Il donne une lecture immediate de la robustesse globale du pipeline, sans ajouter une troisieme metrique redondante.

![Performance par niveau](../plots_benchmark_300/01_overview_by_level.png)

### 2. Lecture executive
Cette vue ramasse le benchmark en quelques chiffres simples : part de cartes entierement correctes, volume d erreurs, poids des cas bonus et place des erreurs croisees. C est le visuel le plus utile pour une slide de synthese ou une page de proposition.

![Lecture executive](../plots_benchmark_300/04_card_level_summary.png)

### 3. Rappel et capacite a ne pas manquer un lieu
Le rappel proxy permet d estimer a quel point le pipeline evite de passer a cote d une information de localisation quand elle est effectivement presente. Il ressort particulierement haut pour la commune et le monument, et reste le plus exigeant sur le lieu dit.

![Rappel proxy](../plots_benchmark_300/06_recall_proxy.png)

### 4. Cas a forte valeur ajoutee
Les cas bonus find_else mettent en evidence la capacite du modele a mobiliser des indices visuels et contextuels au dela du simple texte imprime. Pour un client, cela montre que la solution ne se limite pas a de l OCR, mais apporte une lecture semantique utile sur des documents patrimoniaux complexes.

![Cas bonus](../plots_benchmark_300/05_bonus_cases.png)

### 5. Nature des erreurs restantes
Le dernier visuel montre que les erreurs residuelles se concentrent sur quelques familles identifiables. Elles sont donc pilotables et peuvent etre transformees en feuille de route d amelioration.

![Types d erreurs](../plots_benchmark_300/03_error_types.png)
