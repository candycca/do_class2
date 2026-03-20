import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import seaborn as sns

# Set page configuration
st.set_page_config(page_title="Grid World Value Iteration", layout="centered")

st.title("Grid World Value Iteration")

# Initialize Session State for Grid
if 'grid_state' not in st.session_state:
    # 5x5 Grid
    init_grid = [['' for _ in range(5)] for _ in range(5)]
    init_grid[0][0] = 'S'
    init_grid[4][4] = 'E'
    init_grid[1][1] = 'B'
    init_grid[2][2] = 'B'
    init_grid[3][3] = 'B'
    st.session_state.grid_state = init_grid

# --- Controls ---
# Radio for Drawing Mode
draw_mode = st.radio(
    "Select Tool:",
    options=["Set Start (Green)", "Set End (Red)", "Set Obstacle (Black)", "Clear Cell"],
    horizontal=True,
    label_visibility="collapsed" 
)
# Note: "label_visibility" collapsed looks closer to screenshot which just lists options

# Determine current tool action
current_tool = "clear"
if "Start" in draw_mode: current_tool = "S"
elif "End" in draw_mode: current_tool = "E"
elif "Obstacle" in draw_mode: current_tool = "B"

# Buttons for Actions
col_btn1, col_btn2, _ = st.columns([1, 1, 2])
with col_btn1:
    run_it = st.button("Run Value Iteration")
with col_btn2:
    if st.button("Reset Grid"):
        st.session_state.grid_state = [['' for _ in range(5)] for _ in range(5)]
        st.rerun()

# --- Grid Display (Interactive) ---
# We use a 5x5 grid of buttons
grid_container = st.container()

with grid_container:
    for r in range(5):
        cols = st.columns(5)
        for c in range(5):
            cell_value = st.session_state.grid_state[r][c]
            
            # Determine visual label (Emoji as color block proxy)
            # Green Square, Red Square, Black Square, White Square
            if cell_value == 'S':
                label = "🟩"
            elif cell_value == 'E':
                label = "🟥"
            elif cell_value == 'B':
                label = "⬛"
            else:
                label = "⬜"
            
            # Button Logic
            # Note: We use a key based on coordinates.
            if cols[c].button(label, key=f"cell_{r}_{c}", use_container_width=True):
                # Update State on Click
                if current_tool == 'S':
                    # Clear old Start
                    for i in range(5):
                        for j in range(5):
                            if st.session_state.grid_state[i][j] == 'S':
                                st.session_state.grid_state[i][j] = ''
                    st.session_state.grid_state[r][c] = 'S'
                elif current_tool == 'E':
                    # Clear old End
                    for i in range(5):
                        for j in range(5):
                            if st.session_state.grid_state[i][j] == 'E':
                                st.session_state.grid_state[i][j] = ''
                    st.session_state.grid_state[r][c] = 'E'
                elif current_tool == 'B':
                    st.session_state.grid_state[r][c] = 'B'
                else: # Clear
                    st.session_state.grid_state[r][c] = ''
                st.rerun()

# ---------------- Value Iteration Algorithm ----------------

actions = [(-1, 0), (1, 0), (0, -1), (0, 1)] # Up, Down, Left, Right
action_names = ['Up', 'Down', 'Left', 'Right']
action_arrows = ['↑', '↓', '←', '→']

def is_valid(r, c, grid_size=5):
    return 0 <= r < grid_size and 0 <= c < grid_size

def value_iteration(grid_size, start, end, blocks, gamma, threshold, step_cost):
    V = np.zeros((grid_size, grid_size))
    policy = np.full((grid_size, grid_size), fill_value="", dtype=object)
    
    iteration = 0
    while True:
        delta = 0
        new_V = np.copy(V)
        
        for r in range(grid_size):
            for c in range(grid_size):
                state = (r, c)
                
                if state == end:
                    new_V[r, c] = 0 
                    continue
                if state in blocks:
                    new_V[r, c] = 0 
                    continue
                
                # Calculate max value over actions
                q_values = []
                for action in actions:
                    nr, nc = r + action[0], c + action[1]
                    
                    # Boundary check
                    if not is_valid(nr, nc, grid_size) or (nr, nc) in blocks:
                        nr, nc = r, c # Stay in place
                    
                    # Reward structure
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
                policy[r, c] = "E"
                continue
            if state in blocks:
                policy[r, c] = "B"
                continue
            
            q_values = []
            for action in actions:
                nr, nc = r + action[0], c + action[1]
                if not is_valid(nr, nc, grid_size) or (nr, nc) in blocks:
                    nr, nc = r, c
                
                reward = step_cost
                if (nr, nc) == end:
                    reward = 1.0
                
                q_values.append(reward + gamma * V[nr, nc])
            
            best_action_idx = np.argmax(q_values)
            policy[r, c] = action_arrows[best_action_idx]
            
    return V, policy, iteration

# --- Algorithm Execution ---
if run_it:
    # Parse grid from session state
    grid_size = 5
    start_pos = None
    end_pos = None
    blocks = []
    
    for r in range(grid_size):
        for c in range(grid_size):
            val = st.session_state.grid_state[r][c]
            if val == 'S': start_pos = (r,c)
            elif val == 'E': end_pos = (r,c)
            elif val == 'B': blocks.append((r,c))
            
    if not start_pos:
        st.error("Please ensure Start (Green) is set.")
    elif not end_pos:
        st.error("Please ensure End (Red) is set.")
    else:
        # Parameters
        gamma = 0.9
        threshold = 1e-4
        step_cost = -0.04
        
        V_opt, policy_opt, iters = value_iteration(grid_size, start_pos, end_pos, blocks, gamma, threshold, step_cost)
        
        st.success(f"Converged in {iters} iterations.")
        
        # Calculate Optimal Path for Visualization
        path = []
        curr = start_pos
        path.append(curr)
        visited = set()
        visited.add(curr)
        
        # Simple path tracing
        while curr != end_pos:
            r, c = curr
            action_char = policy_opt[r, c]
            
            dv = (0, 0)
            if action_char == '↑': dv = (-1, 0)
            elif action_char == '↓': dv = (1, 0)
            elif action_char == '←': dv = (0, -1)
            elif action_char == '→': dv = (0, 1)
            
            if dv == (0, 0): break # No move
            
            next_pos = (r + dv[0], c + dv[1])
            if not is_valid(next_pos[0], next_pos[1], grid_size) or next_pos in blocks or next_pos in visited:
                break
            
            curr = next_pos
            visited.add(curr)
            path.append(curr)

        # Visualization
        col1, col2 = st.columns(2)
        
        with col1:
             st.subheader("Value Function")
             fig1, ax1 = plt.subplots(figsize=(5,5))
             sns.heatmap(V_opt, annot=True, fmt=".2f", cmap="viridis", ax=ax1, cbar=False)
             st.pyplot(fig1)

        with col2:
             st.subheader("Optimal Policy")
             fig2, ax2 = plt.subplots(figsize=(5,5))
             
             # Prepare Grid Colors for Matplotlib
             # 0: White (Empty), 1: Green (Path), 2: Gray (Block)
             color_grid = np.zeros((grid_size, grid_size))
             
             # Mark blocks
             for (r, c) in blocks:
                 color_grid[r, c] = 2
             
             # Mark path
             for (r, c) in path:
                 color_grid[r, c] = 1
                 
             # Custom Colormap: White, Light Green, Dark Gray
             cmap = ListedColormap(['white', '#8FBC8F', '#404040']) 
             
             ax2.imshow(color_grid, cmap=cmap, vmin=0, vmax=2)
             
             # Grid lines
             ax2.set_xticks(np.arange(grid_size+1)-0.5, minor=True)
             ax2.set_yticks(np.arange(grid_size+1)-0.5, minor=True)
             ax2.grid(which="minor", color="black", linestyle='-', linewidth=2)
             ax2.tick_params(which="minor", bottom=False, left=False)
             ax2.set_xticks([])
             ax2.set_yticks([])

             # Overlay Arrows and Text
             for r in range(grid_size):
                 for c in range(grid_size):
                     if (r, c) in blocks:
                         continue
                     
                     text = policy_opt[r, c]
                     
                     # Add START/END labels
                     if (r, c) == start_pos:
                         ax2.text(c, r - 0.35, "START", ha='center', va='center', fontsize=7, fontweight='bold')
                     if (r, c) == end_pos:
                         ax2.text(c, r + 0.35, "END", ha='center', va='center', fontsize=7, fontweight='bold')
                         text = "" # Clear arrow for End
                     
                     if text in ['↑', '↓', '←', '→']:
                         ax2.text(c, r, text, ha='center', va='center', fontsize=20, fontweight='bold', color='black')
             
             st.pyplot(fig2)

st.markdown("---")
st.markdown("### How to use:")
st.markdown("1. Edit the grid above by typing 'S', 'E', 'B', or leaving it empty.")
st.markdown("2. Adjust parameters in the sidebar if needed.")
st.markdown("3. Click 'Run Value Iteration'.")
