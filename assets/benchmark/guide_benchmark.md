# Guide de benchmark - corpus de 600 cartes postales

## Objectif

Ce benchmark mesure la performance du pipeline sur 600 cartes du corpus Vaucluse a partir de trois niveaux de precision :

1. la commune
2. le lieu-dit / quartier / place
3. le monument

Le fichier a annoter manuellement est :

- `benchmark_300_cartes_vaucluse/corpus_benchmark_annotation.json`

Le fichier source filtre sur le benchmark est :

- `benchmark_300_cartes_vaucluse/metadata_output_benchmark_300.json`

## Principe general

Chaque carte est evaluee sur les trois niveaux, independamment :

- `trans_city`
- `trans_hamlet_uniformise`
- `trans_monument_uniformise`

Les colonnes a remplir manuellement sont :

- `error_city`
- `error_hamlet`
- `error_monument`
- `another_error`
- `bonus`

Regle simple :

- si la prediction est acceptable, laisser la colonne d'erreur a `null`
- si la prediction est fausse, renseigner un code d'erreur unique dans la colonne concernee
- si l'erreur touche plusieurs niveaux a la fois, renseigner aussi `another_error`
- si la carte constitue un cas de reussite notable sans texte de localisation exploitable, renseigner `bonus`

## Champ bonus

La colonne `bonus` sert a signaler les cas positifs remarquables, a valoriser dans le benchmark final.

Valeur autorisee :

- `find_else`

Utiliser `bonus = "find_else"` quand le modele trouve correctement la commune, le lieu-dit ou le monument sans s'appuyer sur un texte imprime de localisation.

Typiquement :

- il n'y a pas de nom de lieu lisible sur la carte
- ou le texte visible n'est pas le bon support de localisation
- mais le modele retrouve quand meme correctement un des niveaux grace au contenu visuel ou a d'autres indices utiles

Important :

- `bonus` ne remplace pas les colonnes d'erreur
- si la prediction est fausse, il ne faut pas mettre `find_else`
- si plusieurs niveaux sont correctement retrouves sans texte, un seul `find_else` suffit

## Regles d'acceptation

Le benchmark est semantique, pas strictement lexical.

On considere comme correct :

- les variantes mineures d'ecriture : accents, apostrophes, traits d'union, articles, pluriels, ordre legerement different des mots
- les variantes toponymiques equivalentes si elles renvoient sans ambiguite au meme lieu
- une identification correcte obtenue par lecture de l'image, meme en l'absence de texte imprime, si le lieu est suffisamment net et non ambigu
- pour le champ monument, la mention du monument principal meme si un sous-espace n'est pas restitue
- que les lieux naturels soient tour à tour identifiés comme monument ou lieu-dit ou les deux 
- que les lieux aux noms trop génériques sans précision ne soient pas identifiés ni dans lieu-dit ni dans monument (exp : "la vallée", "la source", "le lac")

On considere comme erreur :

- une mauvaise commune, un mauvais lieu-dit ou un mauvais monument
- une hallucination a partir d'un texte secondaire, d'une enseigne, d'un lieu d'impression ou d'un detail photographique
- un mauvais niveau de granularite
- un monument partiel ou incomplet quand cela change reellement l'identification
- un seul monument renseigne alors que plusieurs monuments nommes doivent etre restitues
- que les lieux naturels adjectivés et donc spécifiques ne soient pas renseignés ni dans lieu-dit ni dans monument (exp : "la vallée X", "la source de Y", "le gouffre du Z")

## Regles par niveau

### 1. Commune

Le champ `trans_city` est correct s'il designe la bonne commune representee ou citee par la carte.

Cas acceptes :

- `Pontet` pour `Le Pontet` si la commune est correcte
- une commune retrouvee visuellement sans texte imprime, si le cas est vraiment clair

Cas d'erreur :

- confusion avec la commune d'impression, d'expedition ou d'edition
- confusion avec un lieu-dit, un quartier ou un monument
- commune voisine ou homonyme

### 2. Lieu-dit / quartier / place

Le champ `trans_hamlet_uniformise` est correct s'il restitue le bon niveau intermediaire dans la commune :

- lieu-dit
- quartier
- place
- rue
- avenue
- secteur localement identifiable "le rocher X", "la source Y", etc.

`Aucun lieu-dit` est correct si aucun niveau intermediaire fiable n'est identifiable. Dans le cas de descriptions trop générales ("la vallée" ou "la place" sans plus de précision) si rien n'a été identifié nous ne considérons pas cela comme une erreur au vue du caractère trop général de l'information fournie. De même les cours d'eau ne sont pas considérés ici comme un lieu-dit ("le Rhône", "la Sorgue") ni des lieux naturels trop généraux (que l'on serait d'ailleurs bien à mal de catégoriser comme lieu-dit ou comme monument "naturel").

Cas d'erreur :

- un lieu-dit absent alors qu'il est lisible ou clairement identifiable
- un lieu-dit hallucine
- un niveau trop large ou trop fin
- confusion avec la commune ou avec le monument
- dans les cas de "prise depuis X" ou "vue depuis X" et où X est identifié comme lieu-dit

### 3. Monument

Le champ `trans_monument_uniformise` est correct s'il identifie le bon monument.

`Aucun monument` est correct si aucun monument specifique n'est identifiable de maniere fiable.

Cas acceptes :

- `Eglise` / `Eglise paroissiale` / `Eglise Saint-...` si cela renvoie au meme edifice
- le monument principal sans sous-partie tres fine

Cas d'erreur :

- monument inexistant ou faux
- mauvais monument dans la bonne commune
- sous-partie prise a tort pour le monument principal
- monument partiel lorsque l'identification devient insuffisante
- liste incomplete quand plusieurs monuments sont nommes

## Typologie d'erreurs a utiliser

Utiliser exactement les codes ci-dessous.

### `error_city`
- `mauvaise_commune` : commune incorrecte sans cas plus precis. souvent car le modèle interprète du texte sur l'image comme étant la commune.
- `commune_absente` : aucune commune restituee alors qu'elle etait identifiable
- `commune_hallucinee` : commune inventee a tort
- `commune_lieu_edition` : lieu d'impression / d'edition / d'expedition pris pour la commune representee
- `commune_mauvais_niveau` : la prediction correspond a un lieu-dit, un quartier ou un monument au lieu d'une commune
- `commune_normalisation` : ancien nom, graphie historique ou variante toponymique mal resolue

### `error_hamlet`
- `mauvais_lieudit` : lieu-dit / quartier / place incorrect. souvent car le modèle interprète du texte sur l'image comme étant le lieu-dit.
- `lieudit_absent` : aucun ou mauvais lieu-dit restitue alors qu'il etait identifiable
- `lieudit_hallucine` : lieu-dit invente a tort
- `lieudit_mauvais_niveau` : prediction trop large ou trop fine pour ce niveau
- `lieudit_normalisation` : variante locale, graphie ou forme historique mal resolue

### `error_monument`
- `mauvais_monument` : monument incorrect sans cas plus precis. souvent car le modèle interprète du texte sur l'image comme étant le monument.
- `monument_absent` : aucun monument restitue alors qu'il etait identifiable
- `monument_hallucine` : monument invente ou deduit a tort
- `monument_partiel` : seule une partie du monument est donnee alors que cela rend l'identification insuffisante
- `monument_mauvais_niveau` : prediction trop generale ou trop fine pour le niveau monument
- `monument_multiple_incomplet` : plusieurs monuments sont presents mais un seul est restitue
- `monument_multiple_excedentaire` : la prediction ajoute un monument non present
- `monument_normalisation` : variante d'intitule ou graphie historique mal resolue

### `another_error`

- `swap_commune_lieudit` : la commune et le lieu-dit sont inverses
- `swap_commune_monument` : la commune et le monument sont inverses
- `swap_lieudit_monument` : le lieu-dit et le monument sont inverses
- `decalage_general_niveaux` : les niveaux sont globalement decales
- `source_json_absente` : la carte est dans le corpus benchmark mais absente du JSON source
- `cas_ambigu` : la verite terrain reste ambigue ou discutable

Cette colonne ne remplace pas les colonnes precedentes. Elle sert a documenter les erreurs croisees et les cas structurels. On peut mettre plusieurs codes separes par `;`.

Regle de benchmark :

- si `another_error` contient `cas_ambigu`, la carte est exclue du benchmark quantitatif final
- elle peut rester documentee qualitativement, mais elle ne doit pas entrer dans les totaux, pourcentages ou rapports de performance

## Mode d'annotation recommande

Pour chaque carte :

1. ouvrir l'image dans `benchmark_300_cartes_vaucluse/corpus_benchmark/`
2. lire la prediction dans `corpus_benchmark_annotation.json`
3. juger chaque niveau separement
4. laisser `null` si correct, sinon renseigner le code d'erreur approprie
5. utiliser `another_error` si l'erreur est croisee ou structurelle
6. utiliser `bonus = "find_else"` si la carte constitue un cas de reussite notable sans texte de localisation

## Calculs et lecture des livrables

Le notebook produit :

- des tableaux CSV dans `benchmark_300_cartes_vaucluse/exports_benchmark_300/`
- des graphiques PNG dans `benchmark_300_cartes_vaucluse/plots_benchmark_300/`
- une synthese narrative dans `benchmark_300_cartes_vaucluse/exports_benchmark_300/benchmark_pitch_summary.md`

Regle structurante :

- toute carte dont `another_error` contient `cas_ambigu` est exclue du benchmark quantitatif
- elle reste documentee, mais elle n'entre dans aucun pourcentage ni aucun ratio

### Indicateurs principaux

Pour chaque niveau (`commune`, `lieu-dit`, `monument`), le notebook calcule :

- `correct` : prediction acceptee, donc colonne d'erreur vide
- `error` : prediction renseignee mais jugee fausse
- `missing_prediction` : prediction vide
- `couverture` : `(correct + error) / total_benchmark`
- `exactitude sur couvert` : `correct / (correct + error)`

Important :

- l'exactitude sur couvert est une accuracy conditionnelle : elle mesure la justesse quand le modele a effectivement propose une reponse
- l'ensemble des calculs ci-dessus se fait hors `cas_ambigu`

### Valeurs `Aucune ville`, `Aucun lieu-dit`, `Aucun monument`

Le notebook compte aussi, pour chaque niveau :

- le nombre de predictions avec la valeur speciale `Aucune...`
- parmi elles, combien sont correctes
- parmi elles, combien sont en erreur

Cela permet de distinguer :

- une vraie absence de lieu ou de monument, correctement detectee
- une non-reponse vide
- une absence annoncee a tort

### Rappel proxy

Le rappel proxy est calcule par niveau comme suit :

- `total_moins_aucun = total_benchmark - nb_predictions_Aucune`
- `rappel_proxy = total_moins_aucun / (total_moins_aucun + nb_codes_absent)`

ou :

- `nb_codes_absent` vaut respectivement `commune_absente`, `lieudit_absent` ou `monument_absent`

Ce calcul donne une estimation pratique de la capacite du pipeline a ne pas manquer une information de localisation quand elle est effectivement presente.

### Hallucinations

Le notebook isole explicitement les trois codes :

- `commune_hallucinee`
- `lieudit_hallucine`
- `monument_hallucine`

Puis calcule :

- le nombre d'hallucinations par niveau
- le total d'hallucinations sur les trois niveaux
- la proportion d'hallucinations sur l'ensemble des predictions possibles, soit `total_benchmark * 3`

Cette mesure sert a objectiver un point commercial important : meme avec un modele generatif, les hallucinations restent marginales.

### Erreurs croisees

Les codes de `another_error` sont comptes a part pour produire :

- la repartition des swaps entre niveaux
- le nombre de cartes avec erreur croisee ou cas structurel

Ces erreurs ne remplacent pas les erreurs par niveau. Elles documentent les cas ou le pipeline est proche du bon resultat mais se trompe de niveau ou de structure.

### Lecture des plots

`01_overview_by_level.png`

- compare, pour chaque niveau, la couverture et l'exactitude sur couvert

`02_status_split.png`

- montre les volumes bruts `correct / error / missing_prediction` par niveau

`03_error_types.png`

- montre les principaux types d'erreurs par niveau

`04_card_level_summary.png`

- synthetise les cartes entierement correctes, les cartes en erreur, les predictions manquantes, les erreurs croisees et les cas bonus

`05_bonus_cases.png`

- met en valeur les cas `find_else`

`06_recall_proxy.png`

- montre le rappel proxy par niveau

`07_cross_errors.png`

- detaille les swaps et erreurs croisees quand il y en a

### Lecture du `benchmark_pitch_summary.md`

Le resume final suit une logique simple :

- une section `Chiffres` pour les indicateurs structurants
- une section `Volumetrie par niveau` pour les volumes bruts
- une section `Valeurs Aucune` pour les absences explicites
- une section `Rappel proxy`
- une section `Swaps et erreurs croisees`
- une section `Hallucinations`
- une section `Erreurs par niveau`
- une section `Lecture client` pour transformer les resultats en argumentaire lisible par des non-specialistes

## Exemple d'annotation

```json
{
  "File name": "FRAD084_07FI007_0803.jpg",
  "trans_city": "Avignon",
  "trans_hamlet_uniformise": "Chevalets",
  "trans_monument_uniformise": "Le Pont de Chevalets",
  "error_city": null,
  "error_hamlet": null,
  "error_monument": "mauvais_monument",
  "another_error": null,
  "bonus": null
}
```

Exemple avec erreur croisee :

```json
{
  "File name": "exemple.jpg",
  "trans_city": "Villeneuve-les-Avignon",
  "trans_hamlet_uniformise": "Avignon",
  "trans_monument_uniformise": "Aucun monument",
  "error_city": "commune_mauvais_niveau",
  "error_hamlet": "lieudit_mauvais_niveau",
  "error_monument": null,
  "another_error": "swap_commune_lieudit",
  "bonus": null
}
```

Exemple avec bonus :

```json
{
  "File name": "exemple_bonus.jpg",
  "trans_city": "Avignon",
  "trans_hamlet_uniformise": "Aucun lieu-dit",
  "trans_monument_uniformise": "Palais des Papes",
  "error_city": null,
  "error_hamlet": null,
  "error_monument": null,
  "another_error": null,
  "bonus": "find_else"
}
```
