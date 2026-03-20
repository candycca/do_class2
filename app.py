from flask import Flask, render_template, request, jsonify
import numpy as np

app = Flask(__name__)

# --- Value Iteration Algorithm ---
ACTION_MAP = {
    (-1, 0): '↑',
    (1, 0): '↓',
    (0, -1): '←',
    (0, 1): '→'
}
ACTIONS = list(ACTION_MAP.keys())

def is_valid(r, c, grid_size=5):
    return 0 <= r < grid_size and 0 <= c < grid_size

def run_value_iteration(grid_size, start, end, blocks):
    gamma = 0.9
    threshold = 1e-4
    step_cost = -0.04
    
    V = np.zeros((grid_size, grid_size))
    policy = np.full((grid_size, grid_size), "", dtype=object)
    
    # Simple blocks set for O(1) lookup
    block_set = set([(r, c) for r, c in blocks])
    
    iteration = 0
    while True:
        delta = 0
        new_V = np.copy(V)
        
        for r in range(grid_size):
            for c in range(grid_size):
                state = (r, c)
                
                if state == end:
                    new_V[r, c] = 0 # Absorbing state (Value 0 or huge reward?) Usually 0 if reward is on transition
                    continue
                if state in block_set:
                    new_V[r, c] = 0
                    continue
                
                # Max over actions
                q_values = []
                for action in ACTIONS:
                    nr, nc = r + action[0], c + action[1]
                    
                    if not is_valid(nr, nc, grid_size) or (nr, nc) in block_set:
                        nr, nc = r, c # Hit wall
                        
                    reward = step_cost
                    if (nr, nc) == end:
                        reward = 1.0
                    
                    q_val = reward + gamma * V[nr, nc]
                    q_values.append(q_val)
                    
                best_val = max(q_values)
                new_V[r, c] = best_val
                delta = max(delta, abs(best_val - V[r, c]))
                
        V = new_V
        if delta < threshold:
            break
        iteration += 1
        
    # Extract Policy
    for r in range(grid_size):
        for c in range(grid_size):
            state = (r, c)
            if state == end:
                policy[r, c] = "G"
                continue
            if state in block_set:
                policy[r, c] = "X"
                continue
            
            q_values = []
            best_action_idx = -1
            max_q = -float('inf')
            
            for idx, action in enumerate(ACTIONS):
                nr, nc = r + action[0], c + action[1]
                
                if not is_valid(nr, nc, grid_size) or (nr, nc) in block_set:
                    nr, nc = r, c
                
                reward = step_cost
                if (nr, nc) == end:
                    reward = 1.0
                
                q = reward + gamma * V[nr, nc]
                if q > max_q:
                    max_q = q
                    best_action_idx = idx
            
            policy[r, c] = ACTION_MAP[ACTIONS[best_action_idx]]
            
    return V, policy, iteration

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/solve', methods=['POST'])
def solve():
    data = request.json
    grid_size = data.get('grid_size', 5)
    start = tuple(data['start'])
    end = tuple(data['end'])
    blocks = [tuple(b) for b in data['blocks']]
    
    # Run Algorithm
    V, policy, iters = run_value_iteration(grid_size, start, end, blocks)
    
    # Convert numpy arrays to lists for JSON
    V_list = V.tolist()
    policy_list = policy.tolist()
    
    # Trace Path
    path = []
    curr = start
    path.append(curr)
    visited = set([curr])
    
    while curr != end:
        r, c = curr
        action_char = policy[r, c]
        
        dv = (0, 0)
        if action_char == '↑': dv = (-1, 0)
        elif action_char == '↓': dv = (1, 0)
        elif action_char == '←': dv = (0, -1)
        elif action_char == '→': dv = (0, 1)
        
        if dv == (0, 0): break
        
        next_pos = (r + dv[0], c + dv[1])
        if not is_valid(next_pos[0], next_pos[1], grid_size) or next_pos in blocks or next_pos in visited:
            break
            
        curr = next_pos
        visited.add(curr)
        path.append(curr)
        
    return jsonify({
        'values': V_list,
        'policy': policy_list,
        'iterations': iters,
        'path': path
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
