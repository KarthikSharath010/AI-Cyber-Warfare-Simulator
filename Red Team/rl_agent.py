import numpy as np
import pickle
import os

class QLearningAgent:
    def __init__(self, actions, learning_rate=0.1, discount_factor=0.9, epsilon=1.0, decay=0.95):
        """
        Initializes the Q-Learning Agent.
        
        :param actions: List of available actions (e.g., ['SQL', 'XSS', 'PHISHING']).
        :param learning_rate: How much new info overrides old info (alpha). 0.1 is standard.
        :param discount_factor: Importance of future rewards (gamma). 0.9 focuses on long-term.
        :param epsilon: Exploration rate. 1.0 means 100% random actions initially.
        :param decay: How fast epsilon decreases. 0.995 is a slow, steady decay.
        """
        self.actions = actions
        self.lr = learning_rate
        self.gamma = discount_factor
        self.epsilon = epsilon
        self.epsilon_decay = decay
        self.epsilon_min = 0.05  # Always keep 5% randomness for discovery
        
        # Q-Table: Maps state -> [Q-values for each action]
        # Structure: q_table["ACTIVE_CAMPAIGN"] = [10.5, -2.0, 5.0, ...]
        self.q_table = {}

    def _init_state(self, state):
        """
        Internal helper: Initializes a new state in the Q-table if it doesn't exist.
        We use small random values (0.0 to 0.1) instead of zeros to break ties 
        and encourage testing different actions early on.
        """
        if state not in self.q_table:
            self.q_table[state] = np.random.uniform(low=0, high=0.1, size=len(self.actions))

    def choose_action(self, state):
        """
        Epsilon-Greedy Action Selection.
        Decides whether to EXPLORE (Random) or EXPLOIT (Best Known Attack).
        """
        self._init_state(state)

        # EXPLORATION: Roll the dice
        if np.random.uniform(0, 1) < self.epsilon:
            return np.random.choice(len(self.actions))
        
        # EXPLOITATION: Pick the action with the highest Q-value
        return np.argmax(self.q_table[state])

    def learn(self, state, action_index, reward, next_state):
        """
        The Core Brain Update (Bellman Equation).
        Updates the Q-value for the action taken based on the reward received.
        """
        self._init_state(state)
        self._init_state(next_state)

        # Current prediction (Old Q-value)
        predict = self.q_table[state][action_index]
        
        # Target (Actual Reward + Best expected future reward)
        target = reward + self.gamma * np.max(self.q_table[next_state])
        
        # Update the Q-value towards the target
        self.q_table[state][action_index] += self.lr * (target - predict)

        # Decay epsilon: Reduce randomness slightly after every learning step
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def save_model(self, filename="q_table.pkl"):
        """
        Saves the entire brain (Q-Table and current Epsilon) to a file.
        This allows you to pause training and resume later without restarting knowledge.
        """
        with open(filename, 'wb') as f:
            pickle.dump({
                "q_table": self.q_table,
                "epsilon": self.epsilon
            }, f)

    def load_model(self, filename="q_table.pkl"):
        """
        Loads a pre-trained brain from disk.
        """
        if os.path.exists(filename):
            with open(filename, 'rb') as f:
                data = pickle.load(f)
                # Handle loading both legacy (dict only) and new (dict + epsilon) formats
                if isinstance(data, dict) and "q_table" in data:
                    self.q_table = data["q_table"]
                    self.epsilon = data.get("epsilon", self.epsilon)
                else:
                    # Fallback for older saves
                    self.q_table = data 

    def get_brain_stats(self, state):
        """
        Introspection Tool: Returns what the AI currently thinks of each attack.
        Output format: List of (Attack Name, Score), sorted by best score.
        """
        if state not in self.q_table:
            return []
        
        q_values = self.q_table[state]
        stats = []
        for idx, value in enumerate(q_values):
            stats.append((self.actions[idx], value))
        
        # Sort by Score (Descending) so best attacks are at the top
        return sorted(stats, key=lambda x: x[1], reverse=True)
