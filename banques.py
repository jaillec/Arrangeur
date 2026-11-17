# -*- coding: utf-8 -*-
import os
import json
from styles_usine import STYLES_USINE

DOSSIER_DATA = "data"
DOSSIER_MORCEAUX = os.path.join(DOSSIER_DATA, "morceaux")

FICHIER_RYTHMES = os.path.join(DOSSIER_DATA, "rythmes.json")
FICHIER_BASSES = os.path.join(DOSSIER_DATA, "basses.json")
FICHIER_ACCORDS = os.path.join(DOSSIER_DATA, "accords.json")
FICHIER_MELODIES = os.path.join(DOSSIER_DATA, "melodies.json")


class GestionnaireBanques:
    """Gere la persistance JSON hybride : bibliotheques globales + morceaux complets."""

    def __init__(self):
        self._preparer_dossiers()
        self.rythmes = self._charger_json(FICHIER_RYTHMES, self._rythmes_defaut())
        self.basses = self._charger_json(FICHIER_BASSES, self._basses_defaut())
        self.accords = self._charger_json(FICHIER_ACCORDS, {})
        self.melodies = self._charger_json(FICHIER_MELODIES, {})

    def _preparer_dossiers(self):
        os.makedirs(DOSSIER_DATA, exist_ok=True)
        os.makedirs(DOSSIER_MORCEAUX, exist_ok=True)

    def _charger_json(self, chemin, defaut):
        if not os.path.exists(chemin):
            self._sauvegarder_json(chemin, defaut)
            return dict(defaut)
        try:
            with open(chemin, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return dict(defaut)

    def _sauvegarder_json(self, chemin, donnees):
        with open(chemin, "w", encoding="utf-8") as f:
            json.dump(donnees, f, indent=2, ensure_ascii=False)

    def _rythmes_defaut(self):
        banque = {}
        for nom, style in STYLES_USINE.items():
            banque[nom] = {
                "bpm": style.get("bpm", 110),
                "signature": style.get("signature", [4, 4]),
                "nb_pas": style.get("nb_pas", 16),
                "grille": style.get("batterie", {}),
            }
        return banque

    def _basses_defaut(self):
        banque = {}
        for nom, style in STYLES_USINE.items():
            if "basse" in style:
                banque[f"Basse_{nom}"] = {
                    "nb_pas": style.get("nb_pas", 16),
                    "notes": style["basse"],
                }
        return banque

    def sauvegarder_rythme(self, nom, bpm, signature, nb_pas, grille):
        self.rythmes[nom] = {
            "bpm": bpm,
            "signature": list(signature),
            "nb_pas": nb_pas,
            "grille": grille,
        }
        self._sauvegarder_json(FICHIER_RYTHMES, self.rythmes)

    def sauvegarder_basse(self, nom, nb_pas, notes):
        self.basses[nom] = {
            "nb_pas": nb_pas,
            "notes": notes,
        }
        self._sauvegarder_json(FICHIER_BASSES, self.basses)

    def sauvegarder_melodie(self, nom, nb_pas, notes):
        self.melodies[nom] = {
            "nb_pas": nb_pas,
            "notes": notes,
        }
        self._sauvegarder_json(FICHIER_MELODIES, self.melodies)

    def sauvegarder_morceau(self, titre, donnees_morceau):
        nom_propre = "".join(c if c.isalnum() or c in ("_", "-") else "_" for c in titre).strip("_")
        if not nom_propre:
            nom_propre = "Morceau_Sans_Titre"
        chemin = os.path.join(DOSSIER_MORCEAUX, f"{nom_propre}.json")
        payload = {
            "titre": titre,
            "tempo_bpm": donnees_morceau.get("tempo_bpm", 110),
            "signature": donnees_morceau.get("signature", [4, 4]),
            "mixage": donnees_morceau.get("mixage", {
                "batterie": 0.85,
                "basse": 0.90,
                "accords": 0.70,
                "melodie": 1.00,
            }),
            "pistes_chargees": donnees_morceau.get("pistes_chargees", {
                "rythmes": [],
                "basses": [],
                "accords": [],
                "melodies": [],
            }),
            "paroles": donnees_morceau.get("paroles", []),
        }
        self._sauvegarder_json(chemin, payload)
        return chemin

    def lister_morceaux(self):
        if not os.path.exists(DOSSIER_MORCEAUX):
            return []
        fichiers = [f[:-5] for f in os.listdir(DOSSIER_MORCEAUX) if f.endswith(".json")]
        return sorted(fichiers)

    def charger_morceau(self, nom_fichier):
        chemin = os.path.join(DOSSIER_MORCEAUX, f"{nom_fichier}.json")
        if not os.path.exists(chemin):
            return None
        return self._charger_json(chemin, {})
