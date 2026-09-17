"""
Modèles proposés au visiteur de la démo.

Choisis d'après le benchmark des 84 cartes du Vaucluse (repo privé
`cartes_benchmark`, `RAPPORT.md` du 2026-09-17). Le propos de la page est la
comparaison : notre petit modèle à poids ouverts, sans aucune aide, face à un
modèle frontière parmi les plus puissants du marché — et l'écart de prix.

Pas de repli automatique : si un modèle disparaît (les versions « preview »
peuvent être retirées), le visiteur doit le voir plutôt que recevoir en douce
les résultats d'un autre modèle. Tout modèle listé doit avoir un fournisseur
sans conservation des données (ZDR) acceptant un schéma JSON strict.
"""

MODELES = {
    "pipeline": {
        "slug": "qwen/qwen3-vl-8b-instruct",
        "titre": "Notre modèle (8 milliards de paramètres)",
        "prix_usd_par_image": 0.0003,
        "detail": (
            "Le petit modèle à poids ouverts de notre pipeline, sans aucune aide : "
            "ni métadonnées de votre catalogue, ni base de connaissances. "
            "Ses poids étant publics, il peut tourner sur nos machines ou sur un "
            "serveur français ou européen, et vos images ne quittent alors pas "
            "l'infrastructure choisie."
        ),
    },
    "frontiere": {
        "slug": "google/gemini-3.1-pro-preview",
        "titre": "Un modèle frontière (le haut du marché)",
        "prix_usd_par_image": 0.0045,
        "detail": (
            "L'un des plus gros modèles commerciaux disponibles, appelé chez son "
            "fournisseur. C'est le point de comparaison : il coûte environ quinze "
            "fois plus cher par image, pour un écart de résultats bien plus faible."
        ),
    },
}

DEFAUT = "pipeline"
