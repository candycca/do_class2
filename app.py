from flask import Flask, render_template, jsonify, request
import numpy as np

app = Flask(__name__)

# Constants
GRID_SIZE = 5
ACTIONS = ['UP', 'DOWN', 'LEFT', 'RIGHT']

def get_next_state(state, action):
    row, col = state
    if action == 'UP':
        next_row = max(0, row - 1)
        next_col = col
    elif action == 'DOWN':
        next_row = min(GRID_SIZE - 1, row + 1)
        next_col = col
    elif action == 'LEFT':
        next_row = row
        next_col = max(0, col - 1)
    elif action == 'RIGHT':
        next_row = row
        next_col = min(GRID_SIZE - 1, col + 1)
    return (next_row, next_col)

def value_iteration(grid_config, gamma=0.9, theta=1e-4):
    start_pos = tuple(grid_config['start'])
    end_pos = tuple(grid_config['end'])
    obstacles = set(tuple(obs) for obs in grid_config['obstacles'])
    
    # Initialize V(s)
    V = np.zeros((GRID_SIZE, GRID_SIZE))
    
    # Policy: Store best action index for each state
    policy = np.full((GRID_SIZE, GRID_SIZE), '', dtype=object)

    while True:
        delta = 0
        new_V = np.copy(V)
        
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                s = (r, c)
                
                # Terminal state (Goal) or Obstacle
                if s == end_pos:
                    new_V[s] = 0 
                    continue
                
                if s in obstacles:
                    new_V[s] = 0 
                    continue

                # Calculate max value over all actions
                action_values = []
                for action in ACTIONS:
                    next_s = get_next_state(s, action)
                    
                    if next_s in obstacles:
                        next_s = s
                    
                    # Reward structure
                    reward = -1 # Step cost
                    if next_s == end_pos:
                        reward = 10 # Goal reward
                    
                    v = reward + gamma * V[next_s]
                    action_values.append(v)
                
                best_value = max(action_values)
                new_V[s] = best_value
                delta = max(delta, abs(best_value - V[s]))
        
        V = new_V
        if delta < theta:
            break
            
    # Derive Policy
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            s = (r, c)
            if s == end_pos or s in obstacles:
                continue
                
            best_action = None
            max_val = -float('inf')
            
            for action in ACTIONS:
                next_s = get_next_state(s, action)
                if next_s in obstacles:
                    next_s = s
                
                reward = -1
                if next_s == end_pos:
                    reward = 10
                    
                val = reward + gamma * V[next_s]
                if val > max_val:
                    max_val = val
                    best_action = action
            
            policy[r, c] = best_action

    return V.tolist(), policy.tolist()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/solve', methods=['POST'])
def solve():
    data = request.json
    values, policy = value_iteration(data)
    return jsonify({
        'values': values,
        'policy': policy
    })

if __name__ == '__main__':
    app.run(debug=True)
