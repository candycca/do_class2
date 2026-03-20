# Grid World Value Iteration Visualizer

A web-based interactive tool to visualize the **Value Iteration** algorithm for solving a Grid World pathfinding problem.

## Demo
👉 **Live Demo:** [https://do-class2.onrender.com](https://do-class2.onrender.com)

![Grid World Value Iteration](https://via.placeholder.com/600x400?text=Grid+World+Screenshot+Placeholder)

## Features

*   **Interactive Grid**: Click to set Start (Green), End (Red), and Obstacles (Black).
*   **Value Iteration Algorithm**: Computes the optimal policy $\pi^*(s)$ and value function $V^*(s)$.
*   **Visualization**:
    *   **Optimal Policy**: Arrows showing the best action for each cell (↑, ↓, ←, →).
    *   **Value Function**: Numerical values representing expected rewards.
    *   **Optimal Path**: Highlights the best route from Start to End in **Dark Green**.
*   **Responsive UI**: Built with Flask, HTML5, CSS3, and JavaScript.

## How to Run Locally

1.  **Clone the repository**
    ```bash
    git clone https://github.com/candycca/do_class2.git
    cd do_class2
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the Application**
    ```bash
    python app.py
    ```

4.  **Open in Browser**
    Visit `http://127.0.0.1:5000`

## Algorithm Details

*   **State Space**: 5x5 Grid
*   **Actions**: Up, Down, Left, Right
*   **Rewards**:
    *   Reaching Goal: +1.0
    *   Step Cost: -0.04
*   **Discount Factor ($\gamma$)**: 0.9
*   **Transition Model**: Deterministic (probability 1.0 for intended action).

## Technologies
*   **Backend**: Python, Flask, NumPy
*   **Frontend**: HTML, CSS, JavaScript (Vanilla)
*   **Deployment**: Render (Gunicorn)
