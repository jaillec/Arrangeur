# styles_usine.py
"""
Bibliothèque des styles rythmiques et lignes de basse prédéfinis (Usine - Lecture seule).
Chaque pas correspond à une double-croche (16 pas = 4/4, 12 pas = 3/4).
"""

STYLES_USINE = {
    "Valse Lente (Danube)": {
        "bpm": 90,
        "signature": (3, 4),
        "nb_pas": 12,
        "batterie": {
            "kick":  [1, 0, 0, 0,  0, 0, 0, 0,  0, 0, 0, 0],
            "snare": [0, 0, 0, 0,  1, 0, 0, 0,  1, 0, 0, 0],
            "hat":   [1, 0, 1, 0,  1, 0, 1, 0,  1, 0, 1, 0]
        },
        "basse_intervalles": [0, None, None, None, 7, None, None, None, 7, None, None, None]
    },
    "Valse Musette": {
        "bpm": 168,
        "signature": (3, 4),
        "nb_pas": 12,
        "batterie": {
            "kick":  [1, 0, 0, 0,  0, 0, 0, 0,  0, 0, 0, 0],
            "snare": [0, 0, 0, 0,  1, 0, 0, 0,  1, 0, 0, 0],
            "hat":   [0, 0, 0, 0,  1, 0, 0, 0,  1, 0, 0, 0]
        },
        "basse_intervalles": [0, None, None, None, 7, None, None, None, 12, None, None, None]
    },
    "Cha-Cha-Cha": {
        "bpm": 118,
        "signature": (4, 4),
        "nb_pas": 16,
        "batterie": {
            "kick":  [1, 0, 0, 0,  1, 0, 0, 0,  1, 0, 0, 0,  1, 0, 1, 0],
            "snare": [0, 0, 0, 0,  1, 0, 0, 0,  0, 0, 0, 0,  1, 0, 1, 0],
            "hat":   [1, 0, 1, 0,  1, 0, 1, 0,  1, 0, 1, 0,  1, 1, 1, 0]
        },
        "basse_intervalles": [0, None, None, 4, 7, None, None, None, 0, None, None, 4, 7, None, 7, None]
    },
    "Tango Lent": {
        "bpm": 66,
        "signature": (4, 4),
        "nb_pas": 16,
        "batterie": {
            "kick":  [1, 0, 0, 0,  1, 0, 0, 0,  1, 0, 0, 1,  1, 0, 0, 0],
            "snare": [0, 0, 0, 0,  1, 0, 0, 0,  0, 0, 0, 1,  1, 0, 0, 0],
            "hat":   [1, 0, 0, 0,  1, 0, 0, 0,  1, 0, 0, 0,  1, 0, 0, 0]
        },
        "basse_intervalles": [0, None, None, None, 7, None, None, None, 0, None, None, 7, 12, None, None, None]
    },
    "Tango Rapide (Milonga)": {
        "bpm": 124,
        "signature": (4, 4),
        "nb_pas": 16,
        "batterie": {
            "kick":  [1, 0, 0, 1,  0, 0, 1, 0,  1, 0, 0, 1,  0, 0, 1, 0],
            "snare": [0, 0, 0, 0,  1, 0, 0, 0,  0, 0, 0, 0,  1, 0, 1, 0],
            "hat":   [1, 0, 1, 0,  1, 0, 1, 0,  1, 0, 1, 0,  1, 0, 1, 0]
        },
        "basse_intervalles": [0, None, None, 7, None, None, 0, None, 0, None, None, 7, None, None, 12, None]
    },
    "Rumba Salon": {
        "bpm": 100,
        "signature": (4, 4),
        "nb_pas": 16,
        "batterie": {
            "kick":  [1, 0, 0, 1,  0, 0, 1, 0,  0, 0, 1, 0,  1, 0, 0, 0],
            "snare": [0, 0, 0, 0,  1, 0, 0, 0,  0, 0, 0, 0,  1, 0, 0, 0],
            "hat":   [1, 1, 1, 1,  1, 1, 1, 1,  1, 1, 1, 1,  1, 1, 1, 1]
        },
        "basse_intervalles": [0, None, None, 7, None, None, 12, None, 0, None, None, 7, 12, None, None, None]
    }
}
