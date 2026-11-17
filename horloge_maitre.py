# horloge_maitre.py
"""
Horloge Maître (Master Clock) gérant le tempo, les signatures variables
et la lecture synchronisée multi-pistes.
"""
import time


class HorlogeMaitre:
    def __init__(self, bpm=120, nb_pas=16):
        self.bpm = float(bpm)
        self.nb_pas = nb_pas
        self.en_lecture = False
        self.pas_actuel = 0
        self.mesure_actuelle = 0
        self.dernier_tick = time.perf_counter()
        self.recalculer_intervalle()

    def recalculer_intervalle(self):
        # 1 temps (noire) = 4 doubles-croches (pas)
        duree_noire = 60.0 / self.bpm
        self.duree_pas = duree_noire / 4.0

    def definir_tempo(self, nouveau_bpm):
        self.bpm = max(30.0, min(240.0, float(nouveau_bpm)))
        self.recalculer_intervalle()

    def definir_signature(self, nb_pas):
        self.nb_pas = nb_pas
        if self.pas_actuel >= self.nb_pas:
            self.pas_actuel = 0

    def demarrer(self):
        self.en_lecture = True
        self.pas_actuel = 0
        self.mesure_actuelle = 0
        self.dernier_tick = time.perf_counter()

    def arreter(self):
        self.en_lecture = False
        self.pas_actuel = 0

    def mettre_a_jour(self):
        """
        Vérifie si un nouveau pas doit être déclenché.
        Retourne True lors du franchissement d'un pas, sinon False.
        """
        if not self.en_lecture:
            return False

        maintenant = time.perf_counter()
        if maintenant - self.dernier_tick >= self.duree_pas:
            # Compensation de dérive temporelle
            self.dernier_tick += self.duree_pas
            if maintenant - self.dernier_tick > self.duree_pas:
                self.dernier_tick = maintenant

            self.pas_actuel = (self.pas_actuel + 1) % self.nb_pas
            if self.pas_actuel == 0:
                self.mesure_actuelle += 1
            return True

        return False

    def quantifie_pas_proche(self):
        """
        Retourne l'index du pas le plus proche de l'instant présent
        pour caler proprement une note jouée en direct.
        """
        maintenant = time.perf_counter()
        ecoule = maintenant - self.dernier_tick
        if ecoule > (self.duree_pas / 2.0):
            return (self.pas_actuel + 1) % self.nb_pas
        return self.pas_actuel
