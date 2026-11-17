# -*- coding: utf-8 -*-
import pygame

COUL_FOND = (18, 22, 28)
COUL_PANNEAU = (28, 34, 44)
COUL_BORDURE = (60, 72, 90)
COUL_TEXTE = (235, 240, 245)
COUL_GRIS = (135, 145, 160)
COUL_ACCENT = (56, 189, 248)
COUL_VERT = (52, 211, 153)
COUL_ORANGE = (251, 146, 60)
COUL_ROUGE = (248, 113, 113)

INSTRUMENTS_BATTERIE = ["kick", "snare", "hihat", "rim"]
LABELS_BATTERIE = ["Grosse Caisse", "Caisse Claire", "Charleston", "Rimshot"]


class InterfaceArrangeur:
    """Gere l'affichage visuel : Step Sequencer cliquable, console multi-pistes et prompteur."""

    def __init__(self, largeur=1024, hauteur=680):
        self.largeur = largeur
        self.hauteur = hauteur
        pygame.font.init()
        self.font_titre = pygame.font.SysFont("consolas", 24, bold=True)
        self.font_moyen = pygame.font.SysFont("consolas", 18, bold=True)
        self.font_petit = pygame.font.SysFont("consolas", 14)
        self.font_karaoke = pygame.font.SysFont("consolas", 22, bold=True)

        self.zone_grille = pygame.Rect(190, 175, 790, 220)
        self._cache_paroles = {}

    def dessiner(self, surface, contexte):
        surface.fill(COUL_FOND)
        etat = contexte.get("etat", "MENU_PRINCIPAL")

        if etat == "MENU_PRINCIPAL":
            self._dessiner_menu_retro(surface, contexte)
            return

        self._dessiner_barre_superieure(surface, contexte)
        self._dessiner_prompteur(surface, contexte)

        if etat == "RYTHM_SET":
            self._dessiner_grille_batterie(surface, contexte)
        elif etat in ("BASS_SET", "MELODY_SET"):
            self._dessiner_piano_roll(surface, contexte)
        elif etat in ("CHORD_SET", "LIVE_PLAY"):
            self._dessiner_console_multipistes(surface, contexte)

        self._dessiner_barre_mixage(surface, contexte)

    def _dessiner_menu_retro(self, surface, contexte):
        cadre = pygame.Rect(140, 80, self.largeur - 280, self.hauteur - 160)
        pygame.draw.rect(surface, COUL_PANNEAU, cadre, border_radius=8)
        pygame.draw.rect(surface, COUL_ACCENT, cadre, 2, border_radius=8)

        titre = self.font_titre.render("=== MON ARRANGEUR MUSICAL v1.0 ===", True, COUL_ACCENT)
        surface.blit(titre, (cadre.centerx - titre.get_width() // 2, cadre.y + 35))

        options = contexte.get("options_menu", [
            "1. JOUER UN STYLE USINE (Valse, Tango, Rumba...)",
            "2. OUVRIR UNE CHANSON (Morceaux + Paroles)",
            "3. ATELIER CREATION (Rythmes, Basses, Melodies)",
            "4. JEU LIBRE COMPLET (Console Multi-Pistes)",
            "5. QUITTER",
        ])
        index_sel = contexte.get("index_menu", 0)

        for i, texte in enumerate(options):
            actif = (i == index_sel)
            couleur = COUL_VERT if actif else COUL_TEXTE
            prefixe = "> " if actif else "  "
            rendu = self.font_moyen.render(prefixe + texte, True, couleur)
            surface.blit(rendu, (cadre.x + 60, cadre.y + 120 + i * 52))

        aide = self.font_petit.render("Navigation : Fleches [HAUT/BAS] + [ENTREE] | Touches [F1-F5] en jeu", True, COUL_GRIS)
        surface.blit(aide, (cadre.centerx - aide.get_width() // 2, cadre.bottom - 45))

    def _dessiner_barre_superieure(self, surface, contexte):
        barre = pygame.Rect(20, 15, self.largeur - 40, 52)
        pygame.draw.rect(surface, COUL_PANNEAU, barre, border_radius=6)
        pygame.draw.rect(surface, COUL_BORDURE, barre, 1, border_radius=6)

        etat = contexte.get("etat", "LIVE_PLAY")
        bpm = contexte.get("bpm", 110)
        sig = contexte.get("signature", [4, 4])
        accord = contexte.get("accord_actif", "---")
        en_lecture = contexte.get("en_lecture", False)

        txt_etat = self.font_moyen.render(f"MODE: {etat}", True, COUL_ACCENT)
        txt_tempo = self.font_moyen.render(f"BPM: {int(bpm)} | SIG: {sig[0]}/{sig[1]}", True, COUL_TEXTE)
        txt_accord = self.font_moyen.render(f"ACCORD: {accord}", True, COUL_ORANGE)
        txt_play = self.font_moyen.render("PLAY" if en_lecture else "STOP", True, COUL_VERT if en_lecture else COUL_ROUGE)

        surface.blit(txt_etat, (35, 31))
        surface.blit(txt_tempo, (310, 31))
        surface.blit(txt_accord, (580, 31))
        surface.blit(txt_play, (880, 31))

    def _dessiner_prompteur(self, surface, contexte):
        box = pygame.Rect(20, 78, self.largeur - 40, 82)
        pygame.draw.rect(surface, COUL_PANNEAU, box, border_radius=6)
        pygame.draw.rect(surface, COUL_BORDURE, box, 1, border_radius=6)

        paroles = contexte.get("paroles", [])
        pas_global = contexte.get("pas_global", 0)

        if not paroles:
            msg = self.font_petit.render("[Prompteur Paroles : Aucune parole chargee - Appuyez sur ESPACE en mode sync]", True, COUL_GRIS)
            surface.blit(msg, (box.x + 20, box.y + 32))
            return

        idx_courant = 0
        for i, ligne in enumerate(paroles):
            if ligne.get("pas", 0) <= pas_global:
                idx_courant = i

        texte_actuel = paroles[idx_courant].get("ligne", "")
        texte_suivant = paroles[idx_courant + 1].get("ligne", "") if idx_courant + 1 < len(paroles) else "--- Fin ---"

        surf_act = self._obtenir_surface_texte(texte_actuel, COUL_VERT, self.font_karaoke)
        surf_suiv = self._obtenir_surface_texte(texte_suivant, COUL_GRIS, self.font_petit)

        surface.blit(surf_act, (box.x + 25, box.y + 14))
        surface.blit(surf_suiv, (box.x + 25, box.y + 50))

    def _obtenir_surface_texte(self, texte, couleur, police):
        cle = (texte, couleur, id(police))
        if cle not in self._cache_paroles:
            self._cache_paroles[cle] = police.render(texte, True, couleur)
        return self._cache_paroles[cle]

    def _dessiner_grille_batterie(self, surface, contexte):
        nb_pas = contexte.get("nb_pas", 16)
        pas_actuel = contexte.get("pas_actuel", 0)
        grille = contexte.get("grille_batterie", {})

        largeur_case = self.zone_grille.width // max(1, nb_pas)
        hauteur_ligne = self.zone_grille.height // len(INSTRUMENTS_BATTERIE)

        for r, inst in enumerate(INSTRUMENTS_BATTERIE):
            y = self.zone_grille.y + r * hauteur_ligne
            label = self.font_petit.render(LABELS_BATTERIE[r], True, COUL_TEXTE)
            surface.blit(label, (25, y + hauteur_ligne // 2 - 8))

            piste = grille.get(inst, [0] * nb_pas)
            for c in range(nb_pas):
                x = self.zone_grille.x + c * largeur_case
                rect = pygame.Rect(x + 2, y + 4, largeur_case - 4, hauteur_ligne - 8)
                actif = c < len(piste) and piste[c] == 1

                if c == pas_actuel:
                    couleur = COUL_ACCENT if actif else (55, 70, 92)
                else:
                    couleur = COUL_VERT if actif else COUL_PANNEAU

                pygame.draw.rect(surface, couleur, rect, border_radius=4)
                if c % 4 == 0:
                    pygame.draw.rect(surface, COUL_GRIS, rect, 1, border_radius=4)

    def _dessiner_piano_roll(self, surface, contexte):
        nb_pas = contexte.get("nb_pas", 16)
        pas_actuel = contexte.get("pas_actuel", 0)
        notes = contexte.get("notes_edition", [])

        pygame.draw.rect(surface, COUL_PANNEAU, self.zone_grille, border_radius=6)
        largeur_case = self.zone_grille.width / max(1, nb_pas)

        for c in range(nb_pas):
            x = int(self.zone_grille.x + c * largeur_case)
            if c == pas_actuel:
                pygame.draw.rect(surface, (45, 62, 85), (x, self.zone_grille.y, int(largeur_case), self.zone_grille.height))
            pygame.draw.line(surface, COUL_BORDURE, (x, self.zone_grille.y), (x, self.zone_grille.bottom))

        for item in notes:
            pas = item.get("pas", 0)
            note_midi = item.get("note", 60)
            duree = item.get("duree", 1)
            syllabe = item.get("syllabe", "")

            rel_y = max(0, min(23, 72 - note_midi))
            y = self.zone_grille.y + int((rel_y / 24.0) * (self.zone_grille.height - 16))
            x = int(self.zone_grille.x + pas * largeur_case) + 2
            w = max(12, int(duree * largeur_case) - 4)

            rect_note = pygame.Rect(x, y, w, 16)
            pygame.draw.rect(surface, COUL_ORANGE, rect_note, border_radius=3)
            if syllabe:
                txt_syl = self.font_petit.render(syllabe, True, COUL_FOND)
                surface.blit(txt_syl, (x + 3, y))

    def _dessiner_console_multipistes(self, surface, contexte):
        pistes_actives = contexte.get("pistes_actives", {})
        categories = [
            ("RYTHMES", pistes_actives.get("rythmes", set())),
            ("BASSES", pistes_actives.get("basses", set())),
            ("ACCORDS", pistes_actives.get("accords", set())),
            ("MELODIES", pistes_actives.get("melodies", set())),
        ]
        largeur_col = (self.largeur - 60) // 4
        for idx, (titre, ensemble) in enumerate(categories):
            col_rect = pygame.Rect(20 + idx * (largeur_col + 6), 175, largeur_col, 240)
            pygame.draw.rect(surface, COUL_PANNEAU, col_rect, border_radius=6)
            pygame.draw.rect(surface, COUL_BORDURE, col_rect, 1, border_radius=6)

            lbl = self.font_moyen.render(titre, True, COUL_ACCENT)
            surface.blit(lbl, (col_rect.x + 12, col_rect.y + 10))

            for j, nom_piste in enumerate(sorted(list(ensemble))[:6]):
                badge = pygame.Rect(col_rect.x + 10, col_rect.y + 45 + j * 30, col_rect.width - 20, 24)
                pygame.draw.rect(surface, COUL_VERT, badge, border_radius=4)
                txt = self.font_petit.render(nom_piste[:20], True, COUL_FOND)
                surface.blit(txt, (badge.x + 6, badge.y + 4))

    def _dessiner_barre_mixage(self, surface, contexte):
        barre = pygame.Rect(20, self.hauteur - 115, self.largeur - 40, 95)
        pygame.draw.rect(surface, COUL_PANNEAU, barre, border_radius=6)
        pygame.draw.rect(surface, COUL_BORDURE, barre, 1, border_radius=6)

        mixage = contexte.get("mixage", {"batterie": 0.85, "basse": 0.90, "accords": 0.70, "melodie": 1.00})
        pistes = ["batterie", "basse", "accords", "melodie"]

        for i, nom in enumerate(pistes):
            val = mixage.get(nom, 0.8)
            x = barre.x + 30 + i * 240
            lbl = self.font_petit.render(f"{nom.upper()}: {int(val * 100)}%", True, COUL_TEXTE)
            surface.blit(lbl, (x, barre.y + 14))

            jauge_fond = pygame.Rect(x, barre.y + 38, 180, 14)
            jauge_val = pygame.Rect(x, barre.y + 38, int(180 * val), 14)
            pygame.draw.rect(surface, COUL_FOND, jauge_fond, border_radius=4)
            pygame.draw.rect(surface, COUL_ACCENT, jauge_val, border_radius=4)

        raccourcis = self.font_petit.render(
            "[F1] Rythme | [F2] Basse | [F3] Accords | [F4] Melodie | [F5] Live | [ESC] Menu",
            True,
            COUL_GRIS,
        )
        surface.blit(raccourcis, (barre.x + 30, barre.bottom - 24))

    def gerer_clic_grille(self, pos_souris, nb_pas, grille_batterie):
        """Edition rapide a la souris dans la grille batterie (O(1) sans boucle)."""
        if not self.zone_grille.collidepoint(pos_souris):
            return False
        largeur_case = self.zone_grille.width // max(1, nb_pas)
        hauteur_ligne = self.zone_grille.height // len(INSTRUMENTS_BATTERIE)

        col = (pos_souris[0] - self.zone_grille.x) // largeur_case
        row = (pos_souris[1] - self.zone_grille.y) // hauteur_ligne

        if 0 <= row < len(INSTRUMENTS_BATTERIE) and 0 <= col < nb_pas:
            inst = INSTRUMENTS_BATTERIE[row]
            piste = grille_batterie.setdefault(inst, [0] * nb_pas)
            if col < len(piste):
                piste[col] = 0 if piste[col] == 1 else 1
                return True
        return False
