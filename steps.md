# Implementation Steps for Value Iteration Grid World

This document outlines the step-by-step plan to implement a 5x5 Grid World application using Flask and Value Iteration algorithm, as described in `ref/idea.md`.

## Phase 1: Project Setup & Basic Structure

- [ ] **Step 1.1: Initialize Project**
    - Create a project directory structure.
    - Set up a virtual environment.
    - Create `requirements.txt` with dependencies (Flask, NumPy).
    - Install dependencies.

- [ ] **Step 1.2: Flask Application Skeleton**
    - Create `app.py`.
    - Initialize the Flask app.
    - Create a basic route `/` that renders `index.html`.
    - Create `templates/index.html` and `static/style.css`.

## Phase 2: Frontend Development (Grid Interface)

- [ ] **Step 2.1: Grid UI Layout**
    - Implement a 5x5 grid in `index.html` using CSS Grid or Flexbox.
    - Style the cells to be square and visually distinct.

- [ ] **Step 2.2: User Interaction (Click Events)**
    - Add JavaScript to handle cell clicks.
    - Implement logic to toggle cell states:
        - Set Start point (Cycle states or use radio buttons/tools).
        - Set End point.
        - Toggle Obstacles (Blocks).
        - Default state is Empty.
    - Visualize these states (e.g., Green for Start, Red for End, Black for Obstacle).

- [ ] **Step 2.3: Control Panel**
    - Add buttons to "Run Value Iteration", "Reset Grid".
    - Add configuration inputs if necessary (Gamma/Discount factor, Theta/Convergence threshold).

## Phase 3: Backend Logic (Value Iteration)

- [ ] **Step 3.1: Grid World Model**
    - Define the Grid World environment in Python.
    - Represent the state space (5x5).
    - Define actions (Up, Down, Left, Right).
    - Define rewards (e.g., -1 per step, +10 for goal, penalty for obstacles?).
    - Define transition dynamics (deterministic or stochastic).

- [ ] **Step 3.2: Value Iteration Algorithm**
    - Implement the `value_iteration()` function.
    - Initialize Value table $V(s)$.
    - Iteratively update $V(s)$ using the Bellman Optimality Equation until convergence.
    - $V(s) \leftarrow \max_a \sum_{s'} P(s'|s,a) [R(s,a,s') + \gamma V(s')]$

- [ ] **Step 3.3: Policy Extraction**
    - Implement function to derive optimal policy $\pi^*(s)$ from converged $V(s)$.
    - $\pi^*(s) = \arg\max_a \sum_{s'} P(s'|s,a) [R(s,a,s') + \gamma V(s')]$

## Phase 4: Integration & Visualization

- [ ] **Step 4.1: API Endpoints**
    - Create a Flask POST endpoint `/solve`.
    - Receive grid configuration (start, end, obstacles) from frontend JSON.
    - Run the Value Iteration logic on the server.
    - Return the calculated Values and Policy (Actions) as JSON.

- [ ] **Step 4.2: Frontend Update Logic**
    - Fetch data from `/solve` using `fetch` API or `Axios`.
    - Parse the response.

- [ ] **Step 4.3: Visualizing Results**
    - Display the Value $V(s)$ in each cell (formatted number).
    - Display the Optimal Action (Arrow) in each cell.
    - Highlight the path if possible, or just show the policy map.

## Phase 5: Refinement & Polish

- [ ] **Step 5.1: Error Handling**
    - Handle cases where no path exists (though Value Iteration works regardless).
    - Ensure start/end points are valid.

- [ ] **Step 5.2: UI Polish**
    - Improve CSS styling.
    - Add legend for colors/icons.
