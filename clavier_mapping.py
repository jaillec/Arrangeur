# clavier_mapping.py
# Gestion des deux claviers virtuels (HAUT et BAS) et du mode Yamaha Single Finger en O(1)
import pygame

# --- TABLES DES NOTES MIDI DE BASE ---
# Clavier HAUT : Mélodie (Do4 = 60 jusqu'à Mi5 = 76)
CLAVIER_HAUT_MIDI = {
    # Touches blanches (AZERTYUIOP^)
    pygame.K_a: 60,          # Do4
    pygame.K_z: 62,          # Ré4
    pygame.K_e: 64,          # Mi4
    pygame.K_r: 65,          # Fa4
    pygame.K_t: 67,          # Sol4
    pygame.K_y: 69,          # La4
    pygame.K_u: 71,          # Si4
    pygame.K_i: 72,          # Do5
    pygame.K_o: 74,          # Ré5
    pygame.K_p: 76,          # Mi5
    # Touches noires (2, 3, 5, 6, 7, 9, 0)
    pygame.K_2: 61,          # Do#4
    pygame.K_3: 63,          # Ré#4
    pygame.K_5: 66,          # Fa#4
    pygame.K_6: 68,          # Sol#4
    pygame.K_7: 70,          # La#4
    pygame.K_9: 73,          # Do#5
    pygame.K_0: 75,          # Ré#5
}

# Clavier BAS : Accords Yamaha ou Basse grave (Do2 = 36 jusqu'à Mi3 = 52)
CLAVIER_BAS_MIDI = {
    # Touches blanches (WXCVBN,;:!)
    pygame.K_w: 36,          # Do2
    pygame.K_x: 38,          # Ré2
    pygame.K_c: 40,          # Mi2
    pygame.K_v: 41,          # Fa2
    pygame.K_b: 43,          # Sol2
    pygame.K_n: 45,          # La2
    pygame.K_COMMA: 47,      # Si2
    pygame.K_SEMICOLON: 48,  # Do3
    pygame.K_COLON: 50,      # Ré3
    pygame.K_EXCLAIM: 52,    # Mi3
    # Touches noires (S, D, G, H, J, L, M)
    pygame.K_s: 37,          # Do#2
    pygame.K_d: 39,          # Ré#2
    pygame.K_g: 42,          # Fa#2
    pygame.K_h: 44,          # Sol#2
    pygame.K_j: 46,          # La#2
    pygame.K_l: 49,          # Do#3
    pygame.K_m: 51,          # Ré#3
}

# Ensembles pré-calculés pour détection de zone en temps constant O(1)
SET_CLAVIER_HAUT = set(CLAVIER_HAUT_MIDI.keys())
SET_CLAVIER_BAS = set(CLAVIER_BAS_MIDI.keys())

NOMS_NOTES = ["Do", "Do#", "Ré", "Ré#", "Mi", "Fa", "Fa#", "Sol", "Sol#", "La", "La#", "Si"]

# Intervalles d'accords en demi-tons
INTERVALLES_ACCORDS = {
    "Majeur": [0, 4, 7],
    "Mineur": [0, 3, 7],
    "7":      [0, 4, 7, 10],
    "m7":     [0, 3, 7, 10],
}

def midi_vers_frequence(note_midi):
    """Convertit un numéro de note MIDI en fréquence (Hz)."""
    return 440.0 * (2.0 ** ((note_midi - 69) / 12.0))

def midi_vers_nom(note_midi):
    """Retourne le nom lisible d'une note (ex: Do4)."""
    nom = NOMS_NOTES[note_midi % 12]
    octave = (note_midi // 12) - 1
    return f"{nom}{octave}"

def analyser_accord_yamaha(notes_bas_actives):
    """
    Détecte l'accord selon la logique Yamaha Single Finger :
    - 1 touche : Accord Majeur sur cette note.
    - Fondamentale + touche noire à gauche (-1 demi-ton) : Accord Mineur.
    - Fondamentale + touche blanche à gauche (-2 demi-tons) : Accord 7ème.
    - Fondamentale + noire + blanche à gauche (-1 et -2) : Accord Mineur 7ème.
    """
    if not notes_bas_actives:
        return None

    notes_triees = sorted(notes_bas_actives)
    fondamentale = notes_triees[-1]  # La note la plus haute est la fondamentale

    ecarts = {n - fondamentale for n in notes_triees[:-1]}

    if -1 in ecarts and -2 in ecarts:
        type_accord = "m7"
    elif -1 in ecarts:
        type_accord = "Mineur"
    elif -2 in ecarts:
        type_accord = "7"
    else:
        type_accord = "Majeur"

    nom_fondamentale = NOMS_NOTES[fondamentale % 12]
    notes_accord = [fondamentale + intervalle for intervalle in INTERVALLES_ACCORDS[type_accord]]

    return {
        "nom": f"{nom_fondamentale} {type_accord}",
        "fondamentale": fondamentale,
        "type": type_accord,
        "notes_midi": notes_accord,
    }
