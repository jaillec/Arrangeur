# moteur_audio.py
# Synthétiseur léger avec mise en cache mémoire (Pygame + NumPy)
import pygame
import numpy as np
from clavier_mapping import midi_vers_frequence

class MoteurAudio:
    def __init__(self, frequence_echantillonnage=44100):
        self.sr = frequence_echantillonnage
        self.cache_sons = {}
        self.sons_percussions = {}
        self._generer_percussions_usine()

    def _creer_sound(self, onde_mono):
        """Convertit un tableau float NumPy (-1.0 à 1.0) en objet pygame.mixer.Sound stéréo."""
        onde_clip = np.clip(onde_mono, -1.0, 1.0)
        samples_16bit = (onde_clip * 32767).astype(np.int16)
        stereo = np.column_stack((samples_16bit, samples_16bit))
        return pygame.sndarray.make_sound(stereo)

    def _generer_percussions_usine(self):
        """Génère les 4 percussions de base une seule fois au démarrage."""
        # 1. Grosse caisse (Kick) : balayage de fréquence grave + décroissance rapide
        t_kick = np.linspace(0, 0.25, int(self.sr * 0.25), endpoint=False)
        freq_kick = 130 * np.exp(-18 * t_kick) + 42
        env_kick = np.exp(-12 * t_kick)
        onde_kick = np.sin(2 * np.pi * freq_kick * t_kick) * env_kick * 0.85
        self.sons_percussions["kick"] = self._creer_sound(onde_kick)

        # 2. Caisse claire (Snare) : bruit blanc filtré + corps tonal
        t_snare = np.linspace(0, 0.20, int(self.sr * 0.20), endpoint=False)
        bruit = np.random.uniform(-1, 1, len(t_snare))
        corps = np.sin(2 * np.pi * 185 * t_snare) * np.exp(-20 * t_snare)
        env_snare = np.exp(-18 * t_snare)
        onde_snare = (bruit * 0.6 + corps * 0.4) * env_snare * 0.65
        self.sons_percussions["snare"] = self._creer_sound(onde_snare)

        # 3. Charleston (Hi-hat fermé) : bruit très court et sec
        t_hat = np.linspace(0, 0.06, int(self.sr * 0.06), endpoint=False)
        bruit_hat = np.random.uniform(-1, 1, len(t_hat))
        env_hat = np.exp(-55 * t_hat)
        onde_hat = bruit_hat * env_hat * 0.35
        self.sons_percussions["hihat"] = self._creer_sound(onde_hat)

        # 4. Rimshot / Clave : impulsion boisée aiguë
        t_rim = np.linspace(0, 0.08, int(self.sr * 0.08), endpoint=False)
        env_rim = np.exp(-40 * t_rim)
        onde_rim = (np.sin(2 * np.pi * 820 * t_rim) + 0.5 * np.sin(2 * np.pi * 1240 * t_rim)) * env_rim * 0.5
        self.sons_percussions["rim"] = self._creer_sound(onde_rim)

    def jouer_percussion(self, nom, volume=0.8):
        """Joue instantanément une percussion pré-calculée."""
        son = self.sons_percussions.get(nom)
        if son:
            son.set_volume(volume)
            son.play()

    def obtenir_note(self, note_midi, timbre="orgue", duree=0.8):
        """Génère ou récupère depuis le cache le son d'une note donnée."""
        cle = (note_midi, timbre, round(duree, 2))
        if cle in self.cache_sons:
            return self.cache_sons[cle]

        freq = midi_vers_frequence(note_midi)
        t = np.linspace(0, duree, int(self.sr * duree), endpoint=False)

        # Enveloppe ADSR douce pour éviter les clics audio
        attaque = min(0.015, duree * 0.1)
        relachement = min(0.08, duree * 0.3)
        env = np.ones_like(t)
        nb_att = int(attaque * self.sr)
        nb_rel = int(relachement * self.sr)
        if nb_att > 0:
            env[:nb_att] = np.linspace(0, 1, nb_att)
        if nb_rel > 0:
            env[-nb_rel:] = np.linspace(1, 0, nb_rel)

        if timbre == "basse":
            # Basse ronde avec fondamentale + légère harmonique 2
            onde = (0.8 * np.sin(2 * np.pi * freq * t) +
                    0.2 * np.sin(2 * np.pi * (freq * 2) * t)) * np.exp(-2.5 * t)
        elif timbre == "nappe":
            # Accord doux (orgue chaud)
            onde = (0.6 * np.sin(2 * np.pi * freq * t) +
                    0.25 * np.sin(2 * np.pi * (freq * 2) * t) +
                    0.15 * np.sin(2 * np.pi * (freq * 3) * t))
        else:
            # Orgue Leslie léger (mélodie)
            vibrato = 1.0 + 0.004 * np.sin(2 * np.pi * 5.5 * t)
            phase = 2 * np.pi * freq * vibrato * t
            onde = (0.65 * np.sin(phase) +
                    0.25 * np.sin(2 * phase) +
                    0.10 * np.sin(4 * phase))

        son = self._creer_sound(onde * env * 0.45)
        self.cache_sons[cle] = son
        return son

    def jouer_note(self, note_midi, timbre="orgue", duree=0.8, volume=0.75):
        """Joue une note et retourne le canal Pygame utilisé (pour pouvoir la couper au KEYUP)."""
        son = self.obtenir_note(note_midi, timbre, duree)
        son.set_volume(volume)
        return son.play()
