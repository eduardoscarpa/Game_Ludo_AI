from environment import *
from costanti import *
import sys
import pygame
import numpy as np
import random
import ludo_env
import costanti
import matplotlib.pyplot as plt
import pickle


def table(finestra):
    # Clean window
    finestra.fill(colore_sfondo)
    # Draw the table
    disegna_tabella(finestra, dimensione_cella, spessore_bordo)


def draw_dice(dado, finestra, turno_player_red):
    # Draw the dice
    pygame.draw.rect(finestra, dado.color, (
        dado.position[1] * dimensione_cella, dado.position[0] * dimensione_cella, dimensione_cella, dimensione_cella),
                     0)
    pygame.draw.rect(finestra, (0, 0, 0), (
        dado.position[1] * dimensione_cella, dado.position[0] * dimensione_cella, dimensione_cella, dimensione_cella),
                     spessore_bordo)

    # Draw the number of the dice
    number_color = (255, 0, 0) if turno_player_red else (0, 255, 0)
    number = pygame.font.SysFont(None, 30).render(str(dado.value), True, number_color)
    number_rect = number.get_rect(center=(dado.position[1] * dimensione_cella + dimensione_cella // 2,
                                          dado.position[0] * dimensione_cella + dimensione_cella // 2))
    finestra.blit(number, number_rect)


def draw_tokens(finestra, framerate):
    # Draw tokens
    for token in tokens:
        x, y = token.position
        center_x = y * dimensione_cella + dimensione_cella // 2
        center_y = x * dimensione_cella + dimensione_cella // 2
        pygame.draw.circle(finestra, token.color, (center_x, center_y), token.size)
        number = pygame.font.SysFont(None, 30).render(str(token.number), True, (0, 0, 0))
        number_rect = number.get_rect(center=(center_x, center_y))
        finestra.blit(number, number_rect)

    # Update window
    pygame.display.flip()
    framerate.tick(120)


def update_observation(observ):
    if (tokens[0].count < tokens[2].count) or (tokens[0].count < tokens[3].count):
        observ['passed 1'] = 1
    elif (tokens[1].count < tokens[2].count) or (tokens[1].count < tokens[3].count):
        observ['passed 2'] = 1
    value = tuple(observ.values())
    return lista_stati.index(value)


def game(num):
    global new_state, current_state
    pygame.init()
    framerate = pygame.time.Clock()
    env = ludo_env.ludo_env()
    dado = Dice((0, 0, 0), (7, 7), 30)
    # Initialize window
    finestra = pygame.display.set_mode((larghezza_finestra, altezza_finestra))
    pygame.display.set_caption("Tabella Ludo")

    agent_wins = []
    cpu_wins = []

    plt.ion()
    fig, ax = plt.subplots()

    for episode in range(num):
        end = False
        current_state = 30
        dado.roll

        while not end:

            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            table(finestra)
            turno_player_red = True
            draw_dice(dado, finestra, turno_player_red)
            # Agent's turn
            action = np.argmax(Q[current_state][:])
            dado, observ, consecutive_sixes, end = env.step(action, dado, 0, 'red')
            draw_tokens(finestra, framerate)

            # New agent's turn if 6 comes out
            if consecutive_sixes > 0 and end is False:
                for consecutive_sixes in range(4):
                    current_state = update_observation(observ)
                    table(finestra)
                    draw_dice(dado, finestra, turno_player_red)

                    action = np.argmax(Q[current_state][:])
                    dado, observ, consecutive_sixes, end = env.step(action, dado, consecutive_sixes, 'red')

                    current_state = update_observation(observ)
                    draw_tokens(finestra, framerate)

                    if consecutive_sixes == 0 or end is True:
                        break

            if not end:
                # Random cpu turn
                turno_player_red = False
                draw_dice(dado, finestra, turno_player_red)
                dado, observ_cpu, consecutive_sixes, end = env.step(random.randint(0, 1), dado, 0, 'green')
                draw_tokens(finestra, framerate)

                # New cpu turn if 6 comes out
                if consecutive_sixes > 0 and end is False:
                    for consecutive_sixes in range(3):
                        current_state = update_observation(observ)
                        table(finestra)
                        draw_dice(dado, finestra, turno_player_red)
                        dado, observ_cpu, consecutive_sixes, end = env.step(random.randint(0, 1), dado, consecutive_sixes, 'green')
                        new_state = update_observation(observ)
                        draw_tokens(finestra, framerate)
                        if consecutive_sixes == 0 or end is True:
                            break
                else:
                    current_state = update_observation(observ)


        print(f"Vittorie agente: {costanti.red_wins} - Vittorie cpu: {costanti.green_wins}")
        agent_wins.append(costanti.red_wins)
        cpu_wins.append(costanti.green_wins)

        # Update the plots
        ax.clear()
        ax.plot(agent_wins, label='Agent Wins', color='red')
        ax.plot(cpu_wins, label='CPU Wins', color='green')
        ax.set_title('Wins Over Episodes')
        ax.set_xlabel('Episode')
        ax.set_ylabel('Total Wins')
        ax.legend()

        # Pause to allow the plot to update
        plt.pause(0.1)
        env.reset()

    plt.ioff()
    plt.show()



lista_stati = [
    (0, 0, 0, 2, 0, 0), (0, 0, 1, 1, 0, 0), (0, 0, 1, 1, 0, 1), (0, 0, 1, 1, 1, 0),
    (0, 0, 2, 0, 0, 0), (0, 0, 2, 0, 0, 1), (0, 0, 2, 0, 1, 0), (0, 0, 2, 0, 1, 1),
    (0, 1, 0, 1, 0, 0), (0, 1, 0, 1, 1, 0), (0, 1, 0, 1, 0, 1), (0, 1, 1, 0, 0, 0),
    (0, 1, 1, 0, 0, 1), (0, 1, 1, 0, 1, 0), (0, 1, 1, 0, 1, 1), (0, 2, 0, 0, 0, 0),
    (0, 2, 0, 0, 1, 0), (0, 2, 0, 0, 0, 1), (0, 2, 0, 0, 1, 1), (1, 0, 0, 1, 0, 0),
    (1, 0, 0, 1, 0, 1), (1, 0, 0, 1, 1, 0), (1, 0, 1, 0, 0, 0), (1, 0, 1, 0, 0, 1),
    (1, 0, 1, 0, 1, 0), (1, 0, 1, 0, 1, 1), (1, 1, 0, 0, 0, 0), (1, 1, 0, 0, 0, 1),
    (1, 1, 0, 0, 1, 0), (1, 1, 0, 0, 1, 1), (2, 0, 0, 0, 0, 0), (2, 0, 0, 0, 0, 1),
    (2, 0, 0, 0, 1, 0), (2, 0, 0, 0, 1, 1)
]


# Sarsa model
with open('models/modello_sarsa.pkl', 'rb') as file:
    Q = pickle.load(file)

if __name__ == '__main__':
    game(30)
