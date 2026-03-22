const API_URL = 'http://localhost:8000';

// Elementy DOM
const urlPanel = document.getElementById('urlPanel');
const controlsPanel = document.getElementById('controlsPanel');
const mainContent = document.getElementById('mainContent');

const videoUrlInput = document.getElementById('videoUrl');
const btnConfirm = document.getElementById('btnConfirm');
const btnStart = document.getElementById('btnStart');
const btnStop = document.getElementById('btnStop');
const btnDraw = document.getElementById('btnDraw');
const btnClear = document.getElementById('btnClear');

const authorList = document.getElementById('authorList');
const authorCount = document.getElementById('authorCount');
const statusMessage = document.getElementById('statusMessage');

const manualAuthorName = document.getElementById('manualAuthorName');
const btnAddManual = document.getElementById('btnAddManual');

const winnerModal = document.getElementById('winnerModal');
const winnerName = document.getElementById('winnerName');
const btnDeleteWinner = document.getElementById('btnDeleteWinner');
const btnKeepWinner = document.getElementById('btnKeepWinner');
const btnDrawAgain = document.getElementById('btnDrawAgain');

// Nowe elementy dla modala potwierdzenia usunięcia
const deleteConfirmModal = document.getElementById('deleteConfirmModal');
const authorToDeleteName = document.getElementById('authorToDeleteName');
const btnConfirmDelete = document.getElementById('btnConfirmDelete');
const btnCancelDelete = document.getElementById('btnCancelDelete');

let pollingInterval = null;
let currentWinner = null;
let displayedAuthors = new Set();
let deleteConfirmCallback = null; // Zapisujemy callback do wykonania po potwierdzeniu

// Funkcja pomocnicza do zapytań API
async function apiPost(endpoint, data = {}) {
    try {
        const response = await fetch(`${API_URL}${endpoint}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        return { success: false, message: 'Błąd połączenia z serwerem' };
    }
}

// Zarządzanie widocznością zgodnie z Twoimi krokami
function updateUIState(state) {
    // state: 'init', 'validated', 'running', 'stopped'
    
    switch(state) {
        case 'init':
            urlPanel.classList.remove('hidden');
            controlsPanel.classList.add('hidden');
            mainContent.classList.add('hidden');
            break;
            
        case 'validated':
            urlPanel.classList.remove('hidden');
            controlsPanel.classList.remove('hidden');
            mainContent.classList.remove('hidden');
            
            btnStart.classList.remove('hidden');
            btnStop.classList.add('hidden');
            btnDraw.classList.add('hidden');
            btnClear.classList.add('hidden');
            break;
            
        case 'running':
            btnStart.classList.add('hidden');
            btnStop.classList.remove('hidden');
            btnDraw.classList.add('hidden');
            btnClear.classList.add('hidden');
            break;
            
        case 'stopped':
            btnStart.classList.remove('hidden');
            btnStop.classList.add('hidden');
            // Pokazujemy Losuj i Wyczyść tylko jeśli są autorzy
            const hasAuthors = displayedAuthors.size > 0;
            btnDraw.classList.toggle('hidden', !hasAuthors);
            btnClear.classList.toggle('hidden', !hasAuthors);
            break;
    }
}

// Funkcja do wyświetlania modala potwierdzenia usunięcia
function showDeleteConfirmModal(message, callback) {
    authorToDeleteName.innerText = message;
    deleteConfirmCallback = callback;
    deleteConfirmModal.style.display = 'flex';
}

// Obsługa przycisków modala potwierdzenia
btnConfirmDelete.addEventListener('click', () => {
    if (deleteConfirmCallback) {
        deleteConfirmCallback();
    }
    deleteConfirmModal.style.display = 'none';
    deleteConfirmCallback = null;
});

btnCancelDelete.addEventListener('click', () => {
    deleteConfirmModal.style.display = 'none';
    deleteConfirmCallback = null;
});

// Potwierdź URL
btnConfirm.addEventListener('click', async () => {
    const url = videoUrlInput.value.trim();
    if (!url) return;

    statusMessage.innerText = 'Walidacja linku...';
    const result = await apiPost('/apply-url', { url });

    if (result.success) {
        statusMessage.innerText = 'Link zatwierdzony!';
        statusMessage.style.color = 'var(--success)';
        updateUIState('validated');
    } else {
        statusMessage.innerText = `Błąd: ${result.message}`;
        statusMessage.style.color = 'var(--danger)';
    }
});

// Start pobierania
btnStart.addEventListener('click', async () => {
    const result = await apiPost('/start');
    if (result.success) {
        updateUIState('running');
        startPolling();
    }
});

// Stop pobierania
btnStop.addEventListener('click', async () => {
    const result = await apiPost('/stop');
    if (result.success) {
        updateUIState('stopped');
        stopPolling();
    }
});

// Ręczne dodawanie autora
btnAddManual.addEventListener('click', async () => {
    const name = manualAuthorName.value.trim();
    if (!name) return;

    const result = await apiPost('/add-author', { name });
    if (result.success) {
        manualAuthorName.value = '';
        const response = await fetch(`${API_URL}/authors`);
        const data = await response.json();
        updateAuthorsList(data.message);
        
        // Jeśli dodaliśmy pierwszego autora po stopie, pokaż przyciski
        if (!pollingInterval) updateUIState('stopped');
    }
});

// Wyczyść listę
btnClear.addEventListener('click', () => {
    showDeleteConfirmModal('całą listę autorów', async () => {
        await apiPost('/clear');
        updateAuthorsList([]);
        updateUIState('validated');
    });
});

// Losowanie
btnDraw.addEventListener('click', async () => {
    const result = await apiPost('/draw');
    if (result.success) {
        currentWinner = result.winner;
        showWinner(currentWinner);
    }
});

// Polling
function startPolling() {
    if (pollingInterval) return;
    pollingInterval = setInterval(async () => {
        try {
            const response = await fetch(`${API_URL}/authors`);
            const result = await response.json();
            if (result.success) {
                updateAuthorsList(result.message);
            }
        } catch (e) { console.error('Polling error:', e); }
    }, 2000);
}

function stopPolling() {
    clearInterval(pollingInterval);
    pollingInterval = null;
}

function updateAuthorsList(authors) {
    authorCount.innerText = authors.length;
    
    if (authors.length === 0) {
        authorList.innerHTML = '<div class="empty-state">Brak autorów na liście.</div>';
        displayedAuthors.clear();
        return;
    }

    const emptyState = authorList.querySelector('.empty-state');
    if (emptyState) emptyState.remove();

    // Dodaj nowych
    authors.forEach(author => {
        if (!displayedAuthors.has(author)) {
            const div = document.createElement('div');
            div.className = 'author-item';
            div.innerHTML = `
                <span>${author}</span>
                <button class="btn-delete-small" title="Usuń autora"><i class="fas fa-trash-alt"></i></button>
            `;
            div.querySelector('.btn-delete-small').addEventListener('click', () => {
                deleteSpecificAuthor(author);
            });
            authorList.insertBefore(div, authorList.firstChild);
            displayedAuthors.add(author);
        }
    });

    // Usuń z ekranu tych, których nie ma w danych
    const currentOnScreen = Array.from(authorList.querySelectorAll('.author-item'));
    currentOnScreen.forEach(item => {
        const name = item.querySelector('span').innerText;
        if (!authors.includes(name)) {
            item.remove();
            displayedAuthors.delete(name);
        }
    });
}

async function deleteSpecificAuthor(name) {
    showDeleteConfirmModal(`"${name}"`, async () => {
        const result = await apiPost('/delete', { name });
        if (result.success) {
            const response = await fetch(`${API_URL}/authors`);
            const data = await response.json();
            updateAuthorsList(data.message);
            if (!pollingInterval) updateUIState('stopped');
        }
    });
}

// Modal
function showWinner(name) {
    winnerName.innerText = name;
    winnerModal.style.display = 'flex';
}

btnKeepWinner.addEventListener('click', () => {
    winnerModal.style.display = 'none';
});

btnDeleteWinner.addEventListener('click', async () => {
    // Tutaj również można użyć showDeleteConfirmModal, ale dla spójności z oryginalnym zachowaniem
    // winnerModal, który ma swój własny przycisk "Usuń z listy", pozostawię to bez dodatkowego potwierdzenia.
    const result = await apiPost('/delete', { name: currentWinner });
    if (result.success) {
        winnerModal.style.display = 'none';
        const response = await fetch(`${API_URL}/authors`);
        const data = await response.json();
        updateAuthorsList(data.message);
        if (!pollingInterval) updateUIState('stopped');
    }
});

btnDrawAgain.addEventListener('click', () => {
    winnerModal.style.display = 'none';
    btnDraw.click();
});

// Start
updateUIState('init');
