import streamlit as st
import numpy as np
import pandas as pd

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

def main():
    st.set_page_config(page_title="Grid World Value Iteration", layout="wide")
    st.title('Grid World Value Iteration')

    st.markdown("""
        <style>
        .stButton>button {
            width: 100%;
            height: 60px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    col_control, col_grid = st.columns([1, 2])
    
    with col_control:
        st.subheader('Grid Setup')
        
        # Init session state for Grid Configuration
        if 'grid_labels' not in st.session_state:
            st.session_state.grid_labels = np.full((GRID_SIZE, GRID_SIZE), '', dtype=object)
            st.session_state.grid_labels[0, 0] = 'S'
            st.session_state.grid_labels[4, 4] = 'E'
            st.session_state.grid_labels[1, 1] = 'O'
            st.session_state.grid_labels[2, 2] = 'O'
            st.session_state.grid_labels[3, 3] = 'O'
            
        # Init session state for Results (Values and Policy)
        # Initialize with Random Policy and Zero Values as per requirements
        if 'values' not in st.session_state:
            st.session_state.values = np.zeros((GRID_SIZE, GRID_SIZE))
        
        if 'policy' not in st.session_state:
            # Generate random policy initially
            st.session_state.policy = np.random.choice(ACTIONS, size=(GRID_SIZE, GRID_SIZE))
            
        
        # Interaction Mode Selector
        mode = st.radio("Click Mode:", ["Set Start (Green)", "Set End (Red)", "Set Obstacle (Grey)", "Clear Cell"])

        if st.button('Reset Grid / Randomize Policy'):
            st.session_state.grid_labels = np.full((GRID_SIZE, GRID_SIZE), '', dtype=object)
            st.session_state.grid_labels[0, 0] = 'S'
            st.session_state.grid_labels[4, 4] = 'E'
            st.session_state.grid_labels[1, 1] = 'O'
            st.session_state.grid_labels[2, 2] = 'O'
            st.session_state.grid_labels[3, 3] = 'O'
            
            # Reset results to random
            st.session_state.values = np.zeros((GRID_SIZE, GRID_SIZE))
            st.session_state.policy = np.random.choice(ACTIONS, size=(GRID_SIZE, GRID_SIZE))
            st.rerun()

    start_pos = None
    end_pos = None
    obstacles = []

    # Update logic and state collection from grid_labels
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            label = st.session_state.grid_labels[r, c]
            if label == 'S': start_pos = [r, c]
            elif label == 'E': end_pos = [r, c]
            elif label == 'O': obstacles.append([r, c])

    with col_grid:
        st.subheader("Interactive Grid Map")

        # Container for grid buttons
        grid_placeholder = st.empty()
        
        with grid_placeholder.container():
            for r in range(GRID_SIZE):
                cols = st.columns(GRID_SIZE)
                for c in range(GRID_SIZE):
                    label = st.session_state.grid_labels[r, c]
                    
                    def on_click(row=r, col=c):
                        if mode == "Set Start (Green)":
                            st.session_state.grid_labels[st.session_state.grid_labels == 'S'] = ''
                            st.session_state.grid_labels[row, col] = 'S'
                        elif mode == "Set End (Red)":
                            st.session_state.grid_labels[st.session_state.grid_labels == 'E'] = ''
                            st.session_state.grid_labels[row, col] = 'E'
                        elif mode == "Set Obstacle (Grey)":
                            if st.session_state.grid_labels[row, col] not in ['S', 'E']:
                                 st.session_state.grid_labels[row, col] = 'O'
                        elif mode == "Clear Cell":
                             if st.session_state.grid_labels[row, col] not in ['S', 'E']:
                                st.session_state.grid_labels[row, col] = ''
                        # Reset results on edit? Optional. Let's keep them to compare or reset manually.

                    if label == 'S': btn_emoji = "🟩 S"
                    elif label == 'E': btn_emoji = "🟥 E"
                    elif label == 'O': btn_emoji = "⬛"
                    else: btn_emoji = "⬜" # Interactable buttons

                    cols[c].button(btn_emoji, key=f"btn_{r}_{c}", on_click=on_click)

    # Calculation Section
    st.divider()
    
    if st.button('Run Value Iteration (Calculate Optimal Policy)', type="primary", use_container_width=True):
        if not start_pos:
            st.error("Start position 'S' not found!")
        elif not end_pos:
            st.error("End position 'E' not found!")
        else:
            data = {
                'start': start_pos,
                'end': end_pos,
                'obstacles': obstacles
            }
            
            # Run Algorithm
            values, policy = value_iteration(data)
            
            # Update Session State
            st.session_state.values = np.array(values)
            st.session_state.policy = np.array(policy)
            
            st.success("Value Iteration Converged! Policy updated.")

    st.subheader("Visualization: Value Function & Policy")
    st.info("Initial state shows random policy. Click 'Run Value Iteration' to see the optimal policy.")
    
    # Visualization Logic using Session State Data
    values = st.session_state.values
    policy = st.session_state.policy
    
    grid_html = """
    <style>
        .grid-container {
            display: grid;
            grid-template-columns: repeat(5, 80px);
            gap: 5px;
            justify-content: center;
            font-family: sans-serif;
            margin-top: 20px;
        }
        .grid-cell {
            width: 80px;
            height: 80px;
            border: 1px solid #ccc;
            border-radius: 8px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
            position: relative;
        }
        .cell-value { font-size: 11px; margin-bottom: 2px; color: #555; }
        .cell-arrow { font-size: 24px; font-weight: bold; color: #000; }
        .cell-label { position: absolute; top: 2px; left: 4px; font-size: 10px; font-weight: bold; color: #333; }
    </style>
    <div class="grid-container">
    """
    
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            val = values[r][c]
            pol = policy[r][c]
            label = st.session_state.grid_labels[r, c]
            
            # Check Type for styling
            is_start = (label == 'S')
            is_end = (label == 'E')
            is_obs = (label == 'O')
            
            bg_color = '#ffffff'
            text_color = '#333'
            
            content_val = f"V={val:.2f}"
            content_arrow = ""
            
            if is_start:
                bg_color = '#90ee90' # Light Green
                # Show policy at start as well
            elif is_end:
                bg_color = '#ffcccb' # Light Red
                content_arrow = "★" # Goal
            elif is_obs:
                bg_color = '#555555' # Grey
                text_color = '#fff'
                content_val = ""
            
            # Determine Arrow if not obstacle or goal
            if not is_obs and not is_end:
                 if pol == 'UP': content_arrow = '↑'
                 elif pol == 'DOWN': content_arrow = '↓'
                 elif pol == 'LEFT': content_arrow = '←'
                 elif pol == 'RIGHT': content_arrow = '→'
            
            grid_html += f"""
            <div class="grid-cell" style="background-color: {bg_color}; color: {text_color};">
                <div class="cell-label">({r},{c})</div>
                <div class="cell-value">{content_val}</div>
                <div class="cell-arrow">{content_arrow}</div>
            </div>
            """
    grid_html += '</div>'
    st.markdown(grid_html, unsafe_allow_html=True)

if __name__ == '__main__':
    main()
