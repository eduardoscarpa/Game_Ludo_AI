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
    finestra.fill(colore_sfondo)
    disegna_tabella(finestra, dimensione_cella, spessore_bordo)


def draw_dice(dado, finestra, turno_player_red):
    pygame.draw.rect(finestra, dado.color, (
        dado.position[1] * dimensione_cella, dado.position[0] * dimensione_cella, dimensione_cella, dimensione_cella),
                     0)
    pygame.draw.rect(finestra, (0, 0, 0), (
        dado.position[1] * dimensione_cella, dado.position[0] * dimensione_cella, dimensione_cella, dimensione_cella),
                     spessore_bordo)
    number_color = (255, 0, 0) if turno_player_red else (0, 255, 0)
    number = pygame.font.SysFont(None, 30).render(str(dado.value), True, number_color)
    number_rect = number.get_rect(center=(dado.position[1] * dimensione_cella + dimensione_cella // 2,
                                          dado.position[0] * dimensione_cella + dimensione_cella // 2))
    finestra.blit(number, number_rect)


def draw_tokens(finestra, framerate):
    for token in tokens:
        x, y = token.position
        center_x = y * dimensione_cella + dimensione_cella // 2
        center_y = x * dimensione_cella + dimensione_cella // 2
        pygame.draw.circle(finestra, token.color, (center_x, center_y), token.size)
        number = pygame.font.SysFont(None, 30).render(str(token.number), True, (0, 0, 0))
        number_rect = number.get_rect(center=(center_x, center_y))
        finestra.blit(number, number_rect)
    pygame.display.flip()
    framerate.tick(120)


def choose_action(state, exploration_prob):
    if np.random.rand() < exploration_prob:
        return np.random.randint(0, 2)  # Esplorazione casuale
    else:
        return np.argmax(Q[state, :])  # Sfruttamento della conoscenza


def token_near_enemy(position):
    enemy_tokens = [token for token in tokens if token.color != 'red']
    for enemy_token in enemy_tokens:
        if manhattan_distance(position, enemy_token.position) == 1:
            return True
    return False


def manhattan_distance(pos1, pos2):
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])


def update_observation(observ):
    if (tokens[0].count < tokens[2].count) or (tokens[0].count < tokens[3].count):
        observ['passed 1'] = 1
    elif (tokens[1].count < tokens[2].count) or (tokens[1].count < tokens[3].count):
        observ['passed 2'] = 1
    value = tuple(observ.values())
    return lista_stati.index(value)


def episode_train(num):
    global Q, exploration_prob
    pygame.init()
    framerate = pygame.time.Clock()
    env = ludo_env.ludo_env()
    dado = Dice((0, 0, 0), (7, 7), 30)
    finestra = pygame.display.set_mode((larghezza_finestra, altezza_finestra))
    pygame.display.set_caption("Tabella Ludo")

    agent_wins = []
    cpu_wins = []
    total_rewards = []

    exploration_prob = 0.2

    plt.ion()
    fig, ax = plt.subplots()

    for episode in range(num):
        end = False
        current_state = 30
        dado.roll
        total_reward = 0  # Reset reward totale per episodio

        while not end:
            new_state = current_state

            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            table(finestra)
            turno_player_red = True
            draw_dice(dado, finestra, turno_player_red)

            if current_state in range(1, 4) or current_state in range(8, 11) or current_state in range(19, 22):
                if tokens[0].position == (7, 6):
                    action = 1
                else:
                    action = 0
            else:
                action = choose_action(current_state, exploration_prob)

            dado, observ, consecutive_sixes, end = env.step(action, dado, 0, 'red')
            reward = rewards[current_state, action]

            if token_near_enemy(tokens[0].position):
                reward -= 10

            if tokens[0].position == goal_position:
                reward += 50

            total_reward += reward

            draw_tokens(finestra, framerate)

            if consecutive_sixes > 0 and not end:
                for _ in range(4):
                    new_state = update_observation(observ)
                    updateQ(current_state, action, reward, new_state)
                    table(finestra)
                    draw_dice(dado, finestra, turno_player_red)
                    action = choose_action(new_state, exploration_prob)
                    dado, observ, consecutive_sixes, end = env.step(action, dado, consecutive_sixes, 'red')
                    reward = rewards[new_state, action]
                    total_reward += reward
                    if end or consecutive_sixes == 0:
                        break

            if not end:
                turno_player_red = False
                draw_dice(dado, finestra, turno_player_red)
                dado, observ_cpu, consecutive_sixes, end = env.step(random.randint(0, 1), dado, 0, 'green')
                draw_tokens(finestra, framerate)

            new_state = update_observation(observ)
            updateQ(current_state, action, reward, new_state)
            current_state = new_state

        exploration_prob = max(0.01, exploration_prob * 0.995)

        agent_wins.append(costanti.red_wins)
        cpu_wins.append(costanti.green_wins)
        total_rewards.append(total_reward)

        print(f"episodio {episode + 1}: {total_reward}")
        print(f"Vittorie agente: {costanti.red_wins} - Vittorie cpu: {costanti.green_wins}")

        ax.clear()
        ax.plot(agent_wins, label='Agent Wins', color='red')
        ax.plot(cpu_wins, label='CPU Wins', color='green')
        ax.set_title('Wins Over Episodes')
        ax.set_xlabel('Episode')
        ax.set_ylabel('Total Wins')
        ax.legend()
        plt.pause(0.1)

        env.reset()

    plt.savefig('wins_plot_q_learning.png')
    plt.ioff()
    plt.show()


def updateQ(current_state, action, reward, new_state):
    global Q
    Q[current_state, action] = (1 - learning_rate) * Q[current_state, action] + \
                               learning_rate * (reward + discount_factor * np.max(Q[new_state, :]))


# Parametri globali
learning_rate = 0.4
discount_factor = 0.97
exploration_prob = 0.2
goal_position = (7, 6)

rewards = np.array([
    [7, 7],
    [0.5, 0.5], [0, 0.7], [0.7, 0],
    [0.5, 0.5], [-2.0, 0.7], [0.7, -2.0], [0.5, 0.5],
    [0, 0], [0.5, 0], [0, 0.5],
    [0.5, 0.5], [-2.0, 0.9], [0.9, -0.9], [0.5, 0.5],
    [0.7, 0.7], [0.9, -2.0], [-2.0, 0.7], [0.5, 0.5],
    [0, 0], [-2.0, 0.9], [0.9, -2.0],
    [0, 0], [-2.0, 0.9], [0.9, -2.0], [0.5, 0.5],
    [0.5, 0.5], [-1.5, 0.6], [0.6, -1.5], [0.5, 0.5],
    [0.7, 0.7], [-0.9, 1.0], [1.0, -0.9], [0.7, 0.7]
])

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

Q = np.random.rand(34, 2)

if __name__ == '__main__':
    num_episodes = 5000
    episode_train(num_episodes)
    with open('models/modello_q_learning.pkl', 'wb') as file:
        pickle.dump(Q, file)

    print("Modello Q salvato con successo.")