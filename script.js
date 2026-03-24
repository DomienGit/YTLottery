const API_URL = '';

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

const btnToggleKeyword = document.getElementById('btnToggleKeyword');
const keywordSection = document.getElementById('keywordSection');
const keywordInput = document.getElementById('keywordInput');

const authorList = document.getElementById('authorList');
const authorCount = document.getElementById('authorCount');
const statusMessage = document.getElementById('statusMessage');

const manualAuthorName = document.getElementById('manualAuthorName');
const btnAddManual = document.getElementById('btnAddManual');

const winnerModal = document.getElementById('winnerModal');
const winnerModalTitle = document.getElementById('winnerModalTitle');
const winnerModalActions = document.getElementById('winnerModalActions');
const slotMachineContainer = document.getElementById('slotMachineContainer');
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
let displayedAuthors = new Map(); // Zmieniamy na Map do przechowywania obiektów autora {name, img}
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
    if (!url) {
        gsap.to(videoUrlInput, { x: 10, duration: 0.1, repeat: 3, yoyo: true });
        return;
    }

    statusMessage.innerText = 'Walidacja linku...';
    gsap.to(statusMessage, { opacity: 0.5, duration: 0.5, repeat: -1, yoyo: true });
    
    const result = await apiPost('/apply-url', { url });

    gsap.killTweensOf(statusMessage);
    gsap.set(statusMessage, { opacity: 1 });

    if (result.success) {
        // Efekt sukcesu na przycisku
        btnConfirm.classList.add('btn-confirm-success');
        btnConfirm.innerHTML = '<i class="fas fa-check"></i>';
        
        statusMessage.innerText = 'Link zatwierdzony!';
        statusMessage.style.color = 'var(--success)';
        
        // Animacja przejścia interfejsu
        const tl = gsap.timeline();
        tl.to(btnConfirm, { scale: 1.2, duration: 0.2 })
          .to(btnConfirm, { scale: 1, duration: 0.2 })
          .fromTo([controlsPanel, mainContent], 
            { opacity: 0, y: 20 }, 
            { opacity: 1, y: 0, duration: 0.5, stagger: 0.2, delay: 0.3, onStart: () => {
                updateUIState('validated');
            }});

        // Po udanej walidacji, pobierz i zaktualizuj listę autorów
        await fetchAuthorsAndUpdateList();
    } else {
        statusMessage.innerText = `Błąd: ${result.message}`;
        statusMessage.style.color = 'var(--danger)';
        gsap.to(urlPanel, { x: 10, duration: 0.1, repeat: 3, yoyo: true });
    }
});

// Resetowanie przycisku przy edycji linku
videoUrlInput.addEventListener('input', () => {
    if (btnConfirm.classList.contains('btn-confirm-success')) {
        btnConfirm.classList.remove('btn-confirm-success');
        btnConfirm.innerHTML = 'Potwierdź';
        statusMessage.innerText = '';
        
        // Czyścimy ewentualne style inline, aby przycisk wrócił do 100% pierwotnego wyglądu
        gsap.set(btnConfirm, { clearProps: "all" });
    }
});

// Przełączanie sekcji słowa kluczowego - przycisk zamienia się w pole tekstowe
btnToggleKeyword.addEventListener('click', () => {
    keywordSection.classList.remove('hidden');
    btnToggleKeyword.classList.add('hidden');
    keywordInput.focus();
});

// Start pobierania - ukrywa opcje słowa kluczowego
btnStart.addEventListener('click', async () => {
    const keyword = keywordInput.value.trim();
    const result = await apiPost('/start', { keyword: keyword });
    if (result.success) {
        updateUIState('running');
        startPolling();
        
        // Ukrywamy wszystko co związane ze słowem kluczowym na czas pobierania
        keywordSection.classList.add('hidden');
        btnToggleKeyword.classList.add('hidden');
    }
});

// Stop pobierajnia
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
        // Po dodaniu ręcznym, pobierz i zaktualizuj listę autorów
        await fetchAuthorsAndUpdateList();
        
        // Jeśli dodaliśmy pierwszego autora po stopie, pokaż przyciski
        if (!pollingInterval) updateUIState('stopped');
    }
});

// Wyczyść listę - przywraca możliwość ustawienia słowa kluczowego
btnClear.addEventListener('click', () => {
    showDeleteConfirmModal('całą listę autorów', async () => {
        await apiPost('/clear');
        updateAuthorsList([]); // Przekazujemy pustą tablicę, aby wyczyścić widok
        updateUIState('validated');
        
        // Przywracamy przycisk słowa kluczowego i czyścimy input
        btnToggleKeyword.classList.remove('hidden');
        keywordSection.classList.add('hidden');
        keywordInput.value = '';
    });
});

// Losowanie
btnDraw.addEventListener('click', async () => {
    const result = await apiPost('/draw');
    if (result.success) {
        currentWinner = { name: result.winner, img: result.img }; // Obiekt zwycięzcy
        showWinner(currentWinner);
    }
});

// Polling
async function fetchAuthorsAndUpdateList() {
    try {
        const response = await fetch(`${API_URL}/authors`);
        const result = await response.json();
        if (result.success) {
            updateAuthorsList(result.message);
        }
    } catch (e) { console.error('Polling error:', e); }
}

function startPolling() {
    if (pollingInterval) return;
    pollingInterval = setInterval(fetchAuthorsAndUpdateList, 2000);
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
        // Po wyczyszczeniu, sprawdź stan przycisków
        if (!pollingInterval) updateUIState('stopped');
        return;
    }

    const emptyState = authorList.querySelector('.empty-state');
    if (emptyState) emptyState.remove();

    const newAuthorsMap = new Map(authors.map(author => [author.author, author]));
    
    // Usuń z ekranu tych, których nie ma w nowych danych
    for (const [authorName, authorItemDiv] of displayedAuthors.entries()) {
        if (!newAuthorsMap.has(authorName)) {
            authorItemDiv.remove();
            displayedAuthors.delete(authorName);
        }
    }

    // Dodaj nowych i zaktualizuj istniejących
    authors.forEach(authorData => {
        if (!displayedAuthors.has(authorData.author)) {
            const div = document.createElement('div');
            div.className = 'author-item';
            div.dataset.authorName = authorData.author; // Używamy dataset do przechowywania nazwy
            div.innerHTML = `
                <img src="${authorData.img || 'img/logomini.png'}" alt="${authorData.author}" class="author-avatar">
                <span>${authorData.author}</span>
                <button class="btn-delete-small" title="Usuń autora"><i class="fas fa-trash-alt"></i></button>
            `;
            div.querySelector('.btn-delete-small').addEventListener('click', () => {
                deleteSpecificAuthor(authorData.author);
            });
            authorList.insertBefore(div, authorList.firstChild);
            displayedAuthors.set(authorData.author, div); // Przechowujemy referencję do elementu DOM
        }
    });

    // Po aktualizacji, sprawdź stan przycisków
    if (!pollingInterval) updateUIState('stopped');
}

async function deleteSpecificAuthor(name) {
    showDeleteConfirmModal(`"${name}"`, async () => {
        const result = await apiPost('/delete', { name });
        if (result.success) {
            await fetchAuthorsAndUpdateList(); // Odśwież listę po usunięciu
            if (!pollingInterval) updateUIState('stopped');
        }
    });
}

// Modal
async function showWinner({ name, img }) {
    slotMachineContainer.innerHTML = ''; // Wyczyść poprzednie wyniki
    winnerModalTitle.innerText = '🎉 Losowanie... 🎉';
    winnerModalActions.classList.add('hidden'); // Schowaj przyciski
    winnerModal.style.display = 'flex';

    const allAuthors = Array.from(displayedAuthors.values()).map(div => {
        return {
            name: div.dataset.authorName,
            img: div.querySelector('.author-avatar').src
        };
    });

    if (allAuthors.length === 0) {
        const noAuthorsMessage = document.createElement('div');
        noAuthorsMessage.className = 'winner-display';
        noAuthorsMessage.innerHTML = `<div>Brak autorów do losowania!</div>`;
        slotMachineContainer.appendChild(noAuthorsMessage);
        winnerModalActions.classList.remove('hidden');
        return;
    }

    // Shuffle authors and add winner at the end for smooth animation stop
    let shuffledAuthors = [...allAuthors];
    // Ensure the winner is in the list of available authors
    const winnerExists = shuffledAuthors.some(author => author.name === name);
    if (!winnerExists) {
        shuffledAuthors.push({ name: name, img: img || 'img/logomini.png' });
    }
    
    // Create a long track for spinning
    const trackLength = 50; // How many items in the spinning track
    let slotItemsData = [];
    for (let i = 0; i < trackLength - 1; i++) {
        slotItemsData.push(shuffledAuthors[i % shuffledAuthors.length]);
    }
    // Add the actual winner as the last item to stop on
    slotItemsData.push({ name: name, img: img || 'img/logomini.png' });

    const slotTrack = document.createElement('div');
    slotTrack.className = 'slot-track';
    slotMachineContainer.appendChild(slotTrack);

    const ITEM_HEIGHT = 200; // Wysokość pojedynczego slotu, musi zgadzać się z CSS
    
    slotItemsData.forEach(authorData => {
        const item = document.createElement('div');
        item.className = 'slot-item';
        item.innerHTML = `
            <img src="${authorData.img || 'img/logomini.png'}" alt="${authorData.name}" class="author-avatar winner-avatar-small">
            <span>${authorData.name}</span>
        `;
        slotTrack.appendChild(item);
    });

    // Calculate the position for the winner
    const winnerIndex = slotItemsData.length - 1; // The winner is the last item
    const targetY = -(winnerIndex * ITEM_HEIGHT); // Target position to show the winner

    // GSAP animation
    gsap.fromTo(slotTrack, 
        { y: 0 }, 
        {
            y: targetY,
            duration: 5, // Longer duration for more spins
            ease: "power3.out", // Easing for a smooth stop
            onComplete: () => {
                // After animation, replace the slot machine with the final winner display
                slotMachineContainer.innerHTML = '';
                const finalWinnerDisplay = document.createElement('div');
                finalWinnerDisplay.className = 'winner-display';
                finalWinnerDisplay.innerHTML = `
                    <img src="${img || 'img/logomini.png'}" alt="${name}" class="winner-avatar">
                    <div>${name}</div>
                `;
                slotMachineContainer.appendChild(finalWinnerDisplay);
                
                // Zaktualizuj UI po zakończeniu
                winnerModalTitle.innerText = '✨ Gratulacje! ✨';
                winnerModalActions.classList.remove('hidden'); // Pokaż przyciski
                
                // Konfetti!
                confetti({
                    particleCount: 150,
                    spread: 70,
                    origin: { y: 0.6 },
                    zIndex: 2000
                });
            }
        }
    );
}

btnKeepWinner.addEventListener('click', () => {
    winnerModal.style.display = 'none';
});

btnDeleteWinner.addEventListener('click', async () => {
    const result = await apiPost('/delete', { name: currentWinner.name }); // Używamy currentWinner.name
    if (result.success) {
        winnerModal.style.display = 'none';
        await fetchAuthorsAndUpdateList(); // Odśwież listę po usunięciu
        if (!pollingInterval) updateUIState('stopped');
    }
});

btnDrawAgain.addEventListener('click', () => {
    winnerModal.style.display = 'none';
    btnDraw.click();
});

// Start
updateUIState('init');
