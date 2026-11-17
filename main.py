# main.py
# Point d'entrée principal de l'Arrangeur Musical (avec Saisie Modale intégrée)

import sys
import pygame
from horloge_maitre import HorlogeMaitre
from moteur_audio import MoteurAudio
from machine_etats import MachineEtats
from banques import GestionnaireBanques
from interface import InterfaceArrangeur
from saisie_texte import SaisieModale

def main():
    pygame.init()
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.mixer.set_num_channels(32)

    LARGEUR, HAUTEUR = 1100, 720
    ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
    pygame.display.set_caption("🎹 Mon Arrangeur Musical - Multi-Pistes & Machine à États")
    clock_fps = pygame.time.Clock()

    police_titre = pygame.font.SysFont("consolas", 22, bold=True)
    police_texte = pygame.font.SysFont("consolas", 18)

    banques = GestionnaireBanques()
    audio = MoteurAudio()
    horloge = HorlogeMaitre(bpm=120, signature=(4, 4))
    fsm = MachineEtats(banques, audio, horloge)
    interface = InterfaceArrangeur(ecran, banques, fsm, horloge)
    saisie = SaisieModale()

    def on_nouveau_pas(pas_global, pas_mesure, total_pas_mesure):
        # 1. Lecture des rythmes actifs
        for nom_rythme in fsm.pistes_actives["rythmes"]:
            grille = banques.obtenir_rythme(nom_rythme)
            if grille:
                idx = pas_mesure % len(grille["kick"])
                if grille["kick"][idx]:
                    audio.jouer_percussion("kick", fsm.mixage["batterie"])
                if grille["snare"][idx]:
                    audio.jouer_percussion("snare", fsm.mixage["batterie"])
                if grille["hihat"][idx]:
                    audio.jouer_percussion("hihat", fsm.mixage["batterie"])
                if grille.get("rim") and grille["rim"][idx]:
                    audio.jouer_percussion("rim", fsm.mixage["batterie"])

        # 2. Accompagnement basse auto sur accord Yamaha actif
        if fsm.accord_yamaha_actif and pas_mesure % 4 == 0:
            fondamentale = fsm.accord_yamaha_actif[0]
            audio.jouer_note("basse", fondamentale - 12, duree=0.25, volume=fsm.mixage["basse"])

        # 3. Lecture des mélodies actives
        for nom_melodie in fsm.pistes_actives["melodies"]:
            notes = banques.obtenir_melodie(nom_melodie)
            for item in notes:
                if item["pas"] == pas_mesure:
                    audio.jouer_note("orgue", item["note"], duree=0.3, volume=fsm.mixage["melodie"])

    horloge.definir_callback_pas(on_nouveau_pas)

    en_cours = True
    while en_cours:
        temps_actuel = pygame.time.get_ticks() / 1000.0
        horloge.mettre_a_jour(temps_actuel)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                en_cours = False

            # Priorité absolue à la boîte de saisie modale si ouverte
            if saisie.actif:
                termine, resultat = saisie.traiter_evenement(event)
                if termine and resultat and resultat["texte"]:
                    mode = resultat["mode"]
                    txt = resultat["texte"]
                    if mode == "SAUVEGARDE_MORCEAU":
                        fsm.titre_morceau = txt
                        banques.sauvegarder_morceau(
                            txt, horloge.bpm, horloge.signature,
                            fsm.mixage, fsm.pistes_actives, fsm.paroles_morceau
                        )
                    elif mode == "AJOUT_PAROLE":
                        pas_cible = resultat["contexte"]
                        fsm.paroles_morceau.append({"pas": pas_cible, "ligne": txt})
                        fsm.paroles_morceau.sort(key=lambda x: x["pas"])
                        interface.invalider_cache_paroles()
                continue

            # Raccourcis globaux (hors saisie)
            if event.type == pygame.KEYDOWN:
                mods = pygame.key.get_mods()
                if event.key == pygame.K_s and (mods & pygame.KMOD_CTRL):
                    saisie.ouvrir("SAUVEGARDE_MORCEAU", "Nom du morceau à sauvegarder :", fsm.titre_morceau)
                    continue
                elif event.key == pygame.K_t and (mods & pygame.KMOD_CTRL):
                    pas_courant = horloge.pas_global
                    saisie.ouvrir("AJOUT_PAROLE", f"Ajouter une phrase au pas {pas_courant} :", "", pas_courant)
                    continue

            # Molette souris : réglage BPM
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    horloge.changer_bpm(horloge.bpm + 2)
                    continue
                elif event.button == 5:
                    horloge.changer_bpm(horloge.bpm - 2)
                    continue
                elif event.button == 1:
                    interface.gerer_clic_souris(event.pos)
                    continue

            # Routage normal Machine à États O(1)
            fsm.traiter_evenement(event)

        interface.dessiner()
        saisie.dessiner(ecran, police_titre, police_texte)
        pygame.display.flip()
        clock_fps.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
