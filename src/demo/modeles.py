"""
Modèles proposés au visiteur de la démo.

Choisis d'après le benchmark des 84 cartes du Vaucluse (repo privé
`cartes_benchmark`, `RAPPORT.md` du 2026-09-17). Le propos de la page est la
comparaison : notre petit modèle à poids ouverts, sans aucune aide, face à un
modèle frontière parmi les plus puissants du marché.

Le coût par image n'est volontairement pas affiché : ce n'est que le prix de
calcul chez un intermédiaire, sans rapport avec la valeur de la prestation,
qui est surtout du travail humain.

Pas de repli automatique : si un modèle disparaît (les versions « preview »
peuvent être retirées), le visiteur doit le voir plutôt que recevoir en douce
les résultats d'un autre modèle. Tout modèle listé doit avoir un fournisseur
sans conservation des données (ZDR) acceptant un schéma JSON strict.
"""

MODELES = {
    "pipeline": {
        "slug": "qwen/qwen3-vl-8b-instruct",
        "titre": "Notre modèle (8 milliards de paramètres)",
        "detail": (
            "Le modèle de notre pipeline, ici sans aucune aide : ni métadonnées de "
            "votre catalogue, ni base de connaissances. Il est frugal et à poids "
            "ouverts, donc il tourne aussi bien sur nos propres serveurs que sur un "
            "hébergeur français : dans ce cas, vos images ne quittent jamais "
            "l'infrastructure choisie avec vous."
        ),
    },
    "frontiere": {
        "slug": "google/gemini-3.1-pro-preview",
        "titre": "Un modèle frontière (le haut du marché)",
        "detail": (
            "L'un des plus gros modèles commerciaux disponibles, appelé chez son "
            "fournisseur. C'est le point de comparaison : il coûte environ quinze "
            "fois plus cher par image, pour un écart de résultats bien plus faible."
        ),
    },
}

DEFAUT = "pipeline"
