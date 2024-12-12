from pedina import Token
import time

green_safe_zone = [(5, 7), (4, 7), (3, 7), (2, 7), (1, 7)]
red_safe_zone = [(7, 5), (7, 4), (7, 3), (7, 2), (7, 1)]
red_wins = 0
green_wins = 0

larghezza_finestra = 600
altezza_finestra = 600
colore_sfondo = (255, 255, 255)
dimensione_cella = larghezza_finestra // 15  # 15 boxes in a row
spessore_bordo = 1
phase = "red"

tokens = [Token((139, 0, 0), (2, 2), 1, dimensione_cella),
          Token((139, 0, 0), (2, 3), 2, dimensione_cella),
          Token((0, 100, 0), (2, 11), 1, dimensione_cella),
          Token((0, 100, 0), (2, 12), 2, dimensione_cella)]

turno_player_red = True
tempo_limite = 30
tempo_iniziale = time.time()

observations = {
    'into the base': 2,
    'in the path': 0,
    'into the safe zone': 0,
    'arrived at destination': 0,
    'passed 1': 0,
    'passed 2': 0
}
