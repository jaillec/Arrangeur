# machine_etats.py
# Routeur d'événements clavier O(1) basé sur la Machine à États (FSM)
import sys
import pygame
from clavier_mapping import (
    CLAVIER_HAUT_MIDI, CLAVIER_BAS_MIDI,
    SET_CLAVIER_HAUT, SET_CLAVIER_BAS,
    analyser_accord_yamaha
)

class MachineEtats:
    def __init__(self, horloge, audio, styles_usine):
        self.horloge = horloge
        self.audio = audio
        self.styles_usine = styles_usine
        self.noms_styles = list(styles_usine.keys())

        # États disponibles : MENU_PRINCIPAL, CHOIX_STYLE, LIVE_PLAY, RYTHM_SET, BASS_SET, MELODY_SET
        self.etat = "MENU_PRINCIPAL"
        self.index_menu = 0
        self.options_menu = [
            "1. JOUER UN STYLE USINE (Valse, Tango, Rumba...)",
            "2. ATELIER CREATION (Grilles & Enregistrement)",
            "3. JEU LIBRE COMPLET (Console Multi-Pistes)",
            "4. QUITTER"
        ]

        # État musical en cours
        self.style_actif_nom = self.noms_styles[0]
        self.style_actif = self.styles_usine[self.style_actif_nom]
        self.accord_courant = {"nom": "Do Majeur", "fondamentale": 48, "type": "Majeur", "notes_midi": [48, 52, 55]}

        # Suivi des touches maintenues (pour le jeu polyphonique et Yamaha Single Finger)
        self.touches_bas_maintenues = set()
        self.canaux_melodie = {}
        self.canaux_accords = []

        # Mixage par défaut
        self.mixage = {
            "batterie": 0.85,
            "basse": 0.85,
            "accords": 0.55,
            "melodie": 0.80,
        }

    def changer_etat(self, nouvel_etat):
        """Bascule proprement d'un état à l'autre et coupe les notes tenues."""
        self.arreter_tous_sons()
        self.etat = nouvel_etat
        self.index_menu = 0

    def arreter_tous_sons(self):
        for canal in self.canaux_melodie.values():
            if canal:
                canal.stop()
        self.canaux_melodie.clear()
        for canal in self.canaux_accords:
            if canal:
                canal.stop()
        self.canaux_accords.clear()
        self.touches_bas_maintenues.clear()

    def charger_style(self, nom_style):
        self.style_actif_nom = nom_style
        self.style_actif = self.styles_usine[nom_style]
        self.horloge.definir_signature(
            self.style_actif["signature"][0],
            self.style_actif["signature"][1]
        )
        self.horloge.definir_tempo(self.style_actif["bpm"])

    def traiter_evenements(self):
        """Aiguillage O(1) des événements selon l'état actif."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Raccourcis globaux de navigation (F1 à F5 et Échap)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.etat == "MENU_PRINCIPAL":
                        pygame.quit()
                        sys.exit()
                    else:
                        self.horloge.arreter()
                        self.changer_etat("MENU_PRINCIPAL")
                        continue
                elif event.key == pygame.K_F1:
                    self.changer_etat("RYTHM_SET")
                    continue
                elif event.key == pygame.K_F2:
                    self.changer_etat("BASS_SET")
                    continue
                elif event.key == pygame.K_F4:
                    self.changer_etat("MELODY_SET")
                    continue
                elif event.key == pygame.K_F5:
                    self.changer_etat("LIVE_PLAY")
                    continue

            # Molette souris : réglage instantané du tempo BPM
            if event.type == pygame.MOUSEBUTTONDOWN and self.etat != "MENU_PRINCIPAL":
                if event.button == 4:
                    self.horloge.definir_tempo(self.horloge.bpm + 2)
                elif event.button == 5:
                    self.horloge.definir_tempo(self.horloge.bpm - 2)
                continue

            # Routage dédié par état
            if self.etat == "MENU_PRINCIPAL":
                self._gerer_menu_principal(event)
            elif self.etat == "CHOIX_STYLE":
                self._gerer_choix_style(event)
            elif self.etat in ("LIVE_PLAY", "MELODY_SET", "BASS_SET", "RYTHM_SET"):
                self._gerer_jeu_musical(event)

    def _gerer_menu_principal(self, event):
        if event.type != pygame.KEYDOWN:
            return
        if event.key == pygame.K_UP:
            self.index_menu = (self.index_menu - 1) % len(self.options_menu)
        elif event.key == pygame.K_DOWN:
            self.index_menu = (self.index_menu + 1) % len(self.options_menu)
        elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            if self.index_menu == 0:
                self.changer_etat("CHOIX_STYLE")
            elif self.index_menu == 1:
                self.changer_etat("RYTHM_SET")
            elif self.index_menu == 2:
                self.changer_etat("LIVE_PLAY")
                self.horloge.demarrer()
            elif self.index_menu == 3:
                pygame.quit()
                sys.exit()

    def _gerer_choix_style(self, event):
        if event.type != pygame.KEYDOWN:
            return
        if event.key == pygame.K_UP:
            self.index_menu = (self.index_menu - 1) % len(self.noms_styles)
        elif event.key == pygame.K_DOWN:
            self.index_menu = (self.index_menu + 1) % len(self.noms_styles)
        elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            self.charger_style(self.noms_styles[self.index_menu])
            self.changer_etat("LIVE_PLAY")
            self.horloge.demarrer()

    def _gerer_jeu_musical(self, event):
        if event.type == pygame.KEYDOWN:
            # Barre espace : Lecture / Pause de l'horloge maître
            if event.key == pygame.K_SPACE:
                if self.horloge.en_lecture:
                    self.horloge.arreter()
                    self.arreter_tous_sons()
                else:
                    self.horloge.demarrer()
                return

            # --- CLAVIER HAUT : Mélodie ---
            if event.key in SET_CLAVIER_HAUT:
                note = CLAVIER_HAUT_MIDI[event.key]
                # En mode BASS_SET, le clavier haut prolonge la basse d'une octave au-dessus
                if self.etat == "BASS_SET":
                    note_basse = note - 12
                    canal = self.audio.jouer_note(note_basse, timbre="basse", duree=1.2, volume=self.mixage["basse"])
                else:
                    canal = self.audio.jouer_note(note, timbre="orgue", duree=2.5, volume=self.mixage["melodie"])
                self.canaux_melodie[event.key] = canal
                return

            # --- CLAVIER BAS : Mode Yamaha Single Finger ou Basse grave ---
            if event.key in SET_CLAVIER_BAS:
                note_basse = CLAVIER_BAS_MIDI[event.key]
                if self.etat == "BASS_SET":
                    canal = self.audio.jouer_note(note_basse, timbre="basse", duree=1.2, volume=self.mixage["basse"])
                    self.canaux_melodie[event.key] = canal
                else:
                    self.touches_bas_maintenues.add(note_basse)
                    nouvel_accord = analyser_accord_yamaha(self.touches_bas_maintenues)
                    if nouvel_accord:
                        self.accord_courant = nouvel_accord
                        self._plaquer_nappe_accord(nouvel_accord["notes_midi"])

        elif event.type == pygame.KEYUP:
            if event.key in self.canaux_melodie:
                canal = self.canaux_melodie.pop(event.key)
                if canal:
                    canal.fadeout(80)
            elif event.key in SET_CLAVIER_BAS and self.etat != "BASS_SET":
                note_basse = CLAVIER_BAS_MIDI[event.key]
                self.touches_bas_maintenues.discard(note_basse)

    def _plaquer_nappe_accord(self, notes_midi):
        """Joue doucement les notes de l'accord détecté en mode Yamaha."""
        for canal in self.canaux_accords:
            if canal:
                canal.fadeout(60)
        self.canaux_accords.clear()
        for n in notes_midi:
            c = self.audio.jouer_note(n + 12, timbre="nappe", duree=2.0, volume=self.mixage["accords"] * 0.5)
            self.canaux_accords.append(c)
