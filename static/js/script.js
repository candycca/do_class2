document.addEventListener('DOMContentLoaded', () => {
    const gridEl = document.getElementById('grid');
    const runBtn = document.getElementById('runBtn');
    const resetBtn = document.getElementById('resetBtn');
    
    let currentTool = 'start';
    let startPos = {r: 0, c: 0};
    let endPos = {r: 4, c: 4};
    let blocks = new Set(['1-1', '2-2', '3-3']);
    
    function initGrid() {
        gridEl.innerHTML = '';
        for (let r = 0; r < 5; r++) {
            for (let c = 0; c < 5; c++) {
                const cell = document.createElement('div');
                cell.className = 'cell';
                cell.dataset.r = r;
                cell.dataset.c = c;
                
                // Add event listeners
                cell.addEventListener('click', handleCellClick);
                
                gridEl.appendChild(cell);
            }
        }
        updateGridDisplay();
    }
    
    function handleCellClick(e) {
        const cell = e.target.closest('.cell');
        const r = parseInt(cell.dataset.r);
        const c = parseInt(cell.dataset.c);
        const key = `${r}-${c}`;
        
        const tool = document.querySelector('input[name="tool"]:checked').value;
        
        switch(tool) {
            case 'S':
                // Clear old start
                startPos = {r, c};
                blocks.delete(key);
                break;
            case 'E':
                endPos = {r, c};
                blocks.delete(key);
                break;
            case 'B':
                if ((r !== startPos.r || c !== startPos.c) && 
                    (r !== endPos.r || c !== endPos.c)) {
                    blocks.add(key);
                }
                break;
            case 'C':
                blocks.delete(key);
                if (r === startPos.r && c === startPos.c) {
                    startPos = null;
                }
                if (r === endPos.r && c === endPos.c) {
                    endPos = null;
                }
                break;
        }
        updateGridDisplay();
    }
    
    function updateGridDisplay() {
        // Reset classes
        document.querySelectorAll('.cell').forEach(cell => {
            cell.className = 'cell';
            cell.innerHTML = ''; // clear arrows/text
            cell.style.backgroundColor = ''; // clear optimal path color
            cell.style.color = ''; // clear text color
        });
        
        if (startPos) {
            const startCell = getCell(startPos.r, startPos.c);
            if(startCell) startCell.classList.add('start');
        }
        
        if (endPos) {
            const endCell = getCell(endPos.r, endPos.c);
            if(endCell) endCell.classList.add('end');
        }
        
        blocks.forEach(key => {
            const [r, c] = key.split('-').map(Number);
            const blockCell = getCell(r, c);
            if(blockCell) blockCell.classList.add('obstacle');
        });
    }

    function getCell(r, c) {
        return document.querySelector(`.cell[data-r="${r}"][data-c="${c}"]`);
    }

    runBtn.addEventListener('click', async () => {
        if (!startPos || !endPos) {
            alert("Start and End positions are required!");
            return;
        }

        const blockArray = Array.from(blocks).map(k => {
           const [r,c] = k.split('-').map(Number);
           return [r, c]; 
        });

        const data = {
            start: [startPos.r, startPos.c],
            end: [endPos.r, endPos.c],
            blocks: blockArray,
            grid_size: 5
        };

        const res = await fetch('/solve', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });

        const result = await res.json();
        
        // Display Results
        applyResults(result);
    });

    resetBtn.addEventListener('click', () => {
        // Reset to initial state
        startPos = {r: 0, c: 0};
        endPos = {r: 4, c: 4};
        blocks = new Set(['1-1', '2-2', '3-3']);
        
        updateGridDisplay();
        document.getElementById('status').innerText = 'Ready';
    });

    function applyResults(data) {
        // Clean up previous results first
        updateGridDisplay();
        
        const { policy, values, path, iterations } = data;
        
        // Update Grid UI
        for (let r = 0; r < 5; r++) {
            for (let c = 0; c < 5; c++) {
                const cell = getCell(r, c);
                const action = policy[r][c];
                const valueStr = values[r][c].toFixed(2);
                
                // Add Value
                const valDiv = document.createElement('div');
                valDiv.className = 'val';
                valDiv.style.fontSize = '10px';
                valDiv.style.position = 'absolute';
                valDiv.style.top = '2px';
                valDiv.style.left = '2px';
                valDiv.innerText = valueStr;
                cell.appendChild(valDiv);

                // Add Arrow
                if (action && !cell.classList.contains('obstacle') && !cell.classList.contains('end')) {
                    const arrowDiv = document.createElement('div');
                    arrowDiv.className = 'arrow';
                    arrowDiv.innerText = action;
                    cell.appendChild(arrowDiv);
                }
            }
        }
        
        // Highlight Path
        path.forEach(([r, c]) => {
            const cell = getCell(r, c);
            if (!cell.classList.contains('start') && !cell.classList.contains('end')) {
                cell.style.backgroundColor = '#228B22'; // Dark Green
                cell.style.color = 'white'; // Make text white on dark background
                // Also update child elements color if needed, but css cascade might work
                Array.from(cell.children).forEach(child => child.style.color = 'white');
            }
        });
        
        document.getElementById('status').innerText = `Solved in ${iterations} iterations!`;
    }

    initGrid();
});