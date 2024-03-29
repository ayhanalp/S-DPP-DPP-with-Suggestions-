import numpy as np
from AADI_RoverDomain.parameters import Parameters as p
import random


class Ccea:

    def __init__(self):
        self.mut_prob = p.mutation_rate
        self.epsilon = p.epsilon
        self.n_populations = p.num_rovers  # One population for each rover
        self.population_size = p.pop_size * 2  # Number of policies in each pop
        n_inputs = p.num_inputs
        n_outputs = p.num_outputs
        n_nodes = p.num_nodes  # Number of nodes in hidden layer
        self.policy_size = (n_inputs + 1)*n_nodes + (n_nodes + 1) * n_outputs  # Number of weights for NN
        self.pops = np.zeros((self.n_populations, self.population_size, self.policy_size))
        self.fitness = np.zeros((self.n_populations, self.population_size))
        self.team_selection = np.ones((self.n_populations, self.population_size)) * (-1)

    def reset_populations(self):  # Re-initializes CCEA populations for new run
        self.team_selection = np.ones((self.n_populations, self.population_size)) * (-1)
        for pop_index in range(self.n_populations):
            for policy_index in range(self.population_size):
                for w in range(self.policy_size):
                    self.pops[pop_index, policy_index, w] = np.random.normal(0, 1)

    def select_policy_teams(self):  # Create policy teams for testing
        self.team_selection = np.ones((self.n_populations, self.population_size)) * (-1)

        for pop_id in range(self.n_populations):
            for j in range(self.population_size):
                rpol = random.randint(0, (self.population_size - 1))  # Select a random policy from pop
                k = 0
                while k < j:  # Check for duplicates
                    if rpol == self.team_selection[pop_id][k]:
                        rpol = random.randint(0, (self.population_size - 1))
                        k = -1
                    k += 1
                self.team_selection[pop_id][j] = rpol  # Assign policy to team

    def mutate(self):  # Mutate policy based on probability
        half_pop_length = int(self.population_size/2)

        for pop_index in range(self.n_populations):
            policy_index = half_pop_length
            while policy_index < self.population_size:
                rnum = random.uniform(0, 1)
                if rnum <= self.mut_prob:
                    target = random.randint(0, (self.policy_size - 1))  # Select random weight to mutate
                    self.pops[pop_index, policy_index, target] = np.random.normal(0, 1)
                policy_index += 1

    def mutate_percent(self):  # Mutate percentage of policy every generation
        half_pop_length = int(self.population_size / 2)

        for pop_index in range(self.n_populations):
            policy_index = half_pop_length
            mutate_n = int(p.mutation_rate * self.policy_size)
            while policy_index < self.population_size:
                for w in range(mutate_n):
                    target = random.randint(0, (self.policy_size - 1))  # Select random weight to mutate
                    self.pops[pop_index, policy_index, target] = np.random.normal(0, 1)
                policy_index += 1

    def epsilon_greedy_select(self):  # Choose K successors
        half_pop_length = int(self.population_size/2)
        for pop_id in range(self.n_populations):
            policy_id = half_pop_length
            while policy_id < self.population_size:
                rnum = random.uniform(0, 1)
                if rnum >= self.epsilon:  # Choose best policy
                    for k in range(self.policy_size):
                        self.pops[pop_id, policy_id, k] = self.pops[pop_id, 0, k]  # Best policy
                else:
                    parent = random.randint(0, (self.population_size-1))  # Choose a random parent
                    for k in range(self.policy_size):
                        self.pops[pop_id, policy_id, k] = self.pops[pop_id, parent, k]  # Random policy
                policy_id += 1

    def down_select(self):  # Create a new offspring population using parents from top 50% of policies
        # Reorder populations in terms of fitness (top half = best policies)
        for pop_id in range(self.n_populations):
            for j in range(self.population_size):
                k = j + 1
                while k < self.population_size:
                    if self.fitness[pop_id, j] < self.fitness[pop_id, k]:
                        self.fitness[pop_id, j], self.fitness[pop_id, k] = self.fitness[pop_id, k], self.fitness[pop_id, j]
                        self.pops[pop_id, j], self.pops[pop_id, k] = self.pops[pop_id, k], self.pops[pop_id, j]
                    k += 1

        self.epsilon_greedy_select()  # Select parents for offspring population
        self.mutate()  # Mutate offspring population
        self.fitness = np.zeros((self.n_populations, self.population_size))
