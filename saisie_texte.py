# saisie_texte.py
# Module léger de saisie modale (boîte de dialogue rétro) pour Pygame
# Bloque le routage musical uniquement pendant la frappe de texte

import pygame

class SaisieModale:
    def __init__(self):
        self.actif = False
        self.titre = ""
        self.texte = ""
        self.mode = None  # "SAUVEGARDE_MORCEAU", "AJOUT_PAROLE", "SYLLABE_NOTE"
        self.donnees_contexte = None

    def ouvrir(self, mode, titre, texte_initial="", donnees_contexte=None):
        """Ouvre la boîte de saisie et capture le clavier."""
        self.actif = True
        self.mode = mode
        self.titre = titre
        self.texte = texte_initial
        self.donnees_contexte = donnees_contexte
        pygame.key.set_repeat(300, 40)

    def fermer(self):
        """Ferme la boîte et rend la main au moteur musical."""
        self.actif = False
        self.mode = None
        self.texte = ""
        self.donnees_contexte = None
        pygame.key.set_repeat(0)

    def traiter_evenement(self, event):
        """
        Gère la frappe clavier.
        Retourne (True, resultat_dict) si validé par Entrée,
        (True, None) si annulé par Échap,
        (False, None) si la saisie continue.
        """
        if not self.actif or event.type != pygame.KEYDOWN:
            return False, None

        if event.key == pygame.K_ESCAPE:
            self.fermer()
            return True, None

        elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            resultat = {
                "mode": self.mode,
                "texte": self.texte.strip(),
                "contexte": self.donnees_contexte
            }
            self.fermer()
            return True, resultat

        elif event.key == pygame.K_BACKSPACE:
            self.texte = self.texte[:-1]
            return False, None

        else:
            if event.unicode and event.unicode.isprintable():
                if len(self.texte) < 60:
                    self.texte += event.unicode
            return False, None

    def dessiner(self, ecran, police_titre, police_texte):
        """Affiche une boîte de dialogue rétro centrée à l'écran."""
        if not self.actif:
            return

        largeur_ecran, hauteur_ecran = ecran.get_size()
        overlay = pygame.Surface((largeur_ecran, hauteur_ecran), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        ecran.blit(overlay, (0, 0))

        boite_l, boite_h = 620, 170
        x = (largeur_ecran - boite_l) // 2
        y = (hauteur_ecran - boite_h) // 2

        pygame.draw.rect(ecran, (25, 30, 45), (x, y, boite_l, boite_h), border_radius=8)
        pygame.draw.rect(ecran, (0, 220, 180), (x, y, boite_l, boite_h), 2, border_radius=8)

        surf_titre = police_titre.render(self.titre, True, (0, 220, 180))
        ecran.blit(surf_titre, (x + 20, y + 18))

        champ_rect = pygame.Rect(x + 20, y + 65, boite_l - 40, 44)
        pygame.draw.rect(ecran, (15, 18, 28), champ_rect, border_radius=4)
        pygame.draw.rect(ecran, (100, 120, 160), champ_rect, 1, border_radius=4)

        curseur = "|" if (pygame.time.get_ticks() // 500) % 2 == 0 else ""
        surf_saisie = police_texte.render(self.texte + curseur, True, (255, 255, 255))
        ecran.blit(surf_saisie, (champ_rect.x + 12, champ_rect.y + 10))

        aide = police_texte.render("[ENTRÉE] Valider   |   [ÉCHAP] Annuler", True, (160, 170, 190))
        ecran.blit(aide, (x + 20, y + 128))
