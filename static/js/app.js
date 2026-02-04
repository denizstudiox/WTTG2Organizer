const socket = io();

// State
let appData = {
    keys: [],
    sites: {},
    wifi: [],
    notes: "",
    mode1337: false,
    key_markers: []
};

// DOM Elements
const statusEl = document.getElementById('status');
const keysContainer = document.getElementById('keys-container');
const generatedKeyEl = document.getElementById('generated-key');
const notesEl = document.getElementById('notes-input');
const siteRows = document.querySelectorAll('.site-row');
const modeToggle = document.getElementById('mode-toggle');
const wifiList = document.getElementById('wifi-list');

// Internal State for Filtering
let currentMarkerFilter = 'all';

// Socket Events
socket.on('connect', () => {
    statusEl.textContent = "CONNECTED_";
    statusEl.classList.add('connected');
});

socket.on('disconnect', () => {
    statusEl.textContent = "DISCONNECTED_";
    statusEl.classList.remove('connected');
});

socket.on('init_data', (data) => {
    appData = data;
    renderAll();

    // Update Mobile Link if IP is present
    if (data.server_ip) {
        const linkEl = document.getElementById('mobile-link');
        if (linkEl) {
            const url = `http://${data.server_ip}:1337`;
            linkEl.textContent = url;
            linkEl.href = url;
        }
    }
});

socket.on('data_update', (data) => {
    appData = data;
    renderAll();
    filterSites();
});

// Event Delegation Setup
document.addEventListener('DOMContentLoaded', () => {
    // Key inputs
    document.querySelectorAll('.key-input').forEach(input => {
        input.addEventListener('input', function () {
            const idx = parseInt(this.dataset.keyIndex);
            window.handleKeyInput(idx, this);
        });
    });

    // Wiki buttons
    document.querySelectorAll('.wiki-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            const kIdx = parseInt(this.dataset.keyIndex);
            const mIdx = parseInt(this.dataset.markerIndex);
            window.toggleWikiMarker(kIdx, mIdx);
        });
    });

    // Site marker buttons
    document.querySelectorAll('.marker-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            const siteName = this.dataset.siteName;
            const color = this.dataset.color;
            window.toggleSiteMarker(siteName, color);
        });
    });

    // Notes textarea
    const notesInput = document.getElementById('notes-input');
    if (notesInput) {
        notesInput.addEventListener('input', function () {
            window.handleNotesInput(this);
        });
    }

    // Filter Buttons
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            currentMarkerFilter = this.dataset.filter;
            window.filterSites();
        });
    });
});


// Rendering Functions
function renderAll() {
    renderKeys();
    renderNotes();
    renderSites();
    renderWifi();
    renderMode();
}

function renderKeys() {
    appData.keys.forEach((val, idx) => {
        const input = document.getElementById(`key-${idx}`);
        // Only update if not focused (or if empty) to prevent fighting user input
        if (input && input !== document.activeElement) {
            input.value = val;
        }
    });

    // Update wiki buttons
    if (appData.key_markers) {
        appData.key_markers.forEach((markers, kIdx) => {
            markers.forEach((state, mIdx) => {
                const btn = document.getElementById(`wiki-btn-${kIdx}-${mIdx}`);
                if (btn) {
                    if (state === 1) btn.classList.add('active');
                    else btn.classList.remove('active');
                }
            });
        });
    }

    generateFinalKey();
}

function renderNotes() {
    if (notesEl && notesEl !== document.activeElement) {
        notesEl.value = appData.notes;
    }
}

function renderSites() {
    // Update markers
    for (const [name, info] of Object.entries(appData.sites)) {
        const row = document.querySelector(`tr[data-site="${name}"]`);
        if (row && info) {
            const greenBtn = row.querySelector('.marker-btn.green');
            const redBtn = row.querySelector('.marker-btn.red');
            const yellowBtn = row.querySelector('.marker-btn.yellow');

            if (greenBtn) {
                if (info.green) greenBtn.classList.add('active');
                else greenBtn.classList.remove('active');
            }
            if (redBtn) {
                if (info.red) redBtn.classList.add('active');
                else redBtn.classList.remove('active');
            }
            if (yellowBtn) {
                if (info.yellow) yellowBtn.classList.add('active');
                else yellowBtn.classList.remove('active');
            }
        }
    }
}

function renderWifi() {
    wifiList.innerHTML = '';
    appData.wifi.forEach((w, idx) => {
        const div = document.createElement('div');
        div.className = 'wifi-item';
        div.innerHTML = `
            <div>
                <strong>${w.ssid}</strong> (${w.loc})<br>
                <span class="status">${w.pass}</span>
            </div>
            <button class="btn" style="padding: 2px 5px; font-size: 0.7em;" onclick="deleteWifi(${idx})">X</button>
        `;
        wifiList.appendChild(div);
    });
}

function renderMode() {
    if (appData.mode1337) {
        document.body.classList.add('mode-1337-active');
        modeToggle.checked = true;
    } else {
        document.body.classList.remove('mode-1337-active');
        modeToggle.checked = false;
    }
}

function generateFinalKey() {
    const final = appData.keys.join('');
    generatedKeyEl.textContent = final;
}

// User Interactions

window.handleKeyInput = (idx, el) => {
    let val = el.value;

    // Auto-parse "Index - Hash" logic
    // Regex: Start with number, optional space, dash, optional space. capture rest.
    const match = val.match(/^(\d+)\s*-\s*(.+)$/);
    if (match) {
        const targetIdx = parseInt(match[1]) - 1; // 1-based to 0-based
        const hash = match[2].trim(); // trim whitespace

        if (targetIdx >= 0 && targetIdx < 8) {
            // Clear current input if it was a paste into the wrong box
            if (targetIdx !== idx) {
                el.value = "";
                socket.emit('update_key', { index: idx, value: "" });
            }

            // Send to correct box
            socket.emit('update_key', { index: targetIdx, value: hash });
            return;
        }
    }

    socket.emit('update_key', { index: idx, value: val });
}

window.toggleWikiMarker = (kIdx, mIdx) => {
    socket.emit('update_key_marker', { key_index: kIdx, marker_index: mIdx });
}

window.handleNotesInput = (el) => {
    socket.emit('update_notes', { text: el.value });
}

window.toggleSiteMarker = (siteName, color) => {
    socket.emit('update_site_marker', { site_name: siteName, color: color });
}

window.toggle1337 = (el) => {
    socket.emit('toggle_1337', { enabled: el.checked });
}

window.copyKey = () => {
    const text = generatedKeyEl.textContent;
    navigator.clipboard.writeText(text).then(() => {
        alert("COPIED TO CLIPBOARD_");
    });
}

window.addWifi = () => {
    const ssid = document.getElementById('wifi-ssid').value;
    const pass = document.getElementById('wifi-pass').value;
    const loc = document.getElementById('wifi-loc').value;

    if (ssid && pass) {
        socket.emit('add_wifi', { ssid, pass, loc });
        // Clear inputs
        document.getElementById('wifi-ssid').value = '';
        document.getElementById('wifi-pass').value = '';
    }
}

window.deleteWifi = (idx) => {
    socket.emit('delete_wifi', { index: idx });
}

window.shutdownSystem = () => {
    if (confirm("TERMINATE SYSTEM?")) {
        // Send shutdown signal without waiting
        fetch('/shutdown', { method: 'POST', mode: 'no-cors' }).catch(() => { });
        // Immediate UI feedback and closure
        document.body.innerHTML = "<h1 style='color:red; text-align:center; margin-top:20%;'>SYSTEM_TERMINATED</h1>";
        setTimeout(() => { if (window.close) window.close(); }, 100);
    }
}

window.resetSystem = () => {
    if (confirm("WARNING: RESET ALL DATA? This cannot be undone.")) {
        socket.emit('reset_data');
    }
}

window.filterSites = () => {
    const query = document.getElementById('site-search').value.toLowerCase();
    const rows = document.querySelectorAll('.site-row');

    rows.forEach(row => {
        const siteName = row.dataset.site.toLowerCase();
        const siteInfo = appData.sites[row.dataset.site] || { green: false, red: false, yellow: false };

        const matchesSearch = siteName.includes(query);
        let matchesMarker = true;

        if (currentMarkerFilter !== 'all') {
            matchesMarker = siteInfo[currentMarkerFilter] === true;
        }

        if (matchesSearch && matchesMarker) {
            row.classList.remove('filtered-out');
        } else {
            row.classList.add('filtered-out');
        }
    });
}

window.sortSites = () => {
    const criteria = document.getElementById('site-sort').value;
    const tbody = document.querySelector('#site-table-body');
    const rows = Array.from(tbody.querySelectorAll('.site-row'));

    rows.sort((a, b) => {
        const siteA = a.dataset.site.toLowerCase();
        const siteB = b.dataset.site.toLowerCase();

        if (criteria === 'alpha') {
            return siteA.localeCompare(siteB);
        } else if (criteria === 'time') {
            const timeA = a.dataset.time || "";
            const timeB = b.dataset.time || "";

            if (timeA.includes('Always') && !timeB.includes('Always')) return -1;
            if (!timeA.includes('Always') && timeB.includes('Always')) return 1;

            return timeA.localeCompare(timeB) || siteA.localeCompare(siteB);
        } else if (criteria === 'always') {
            const isAlwaysA = a.dataset.time.includes('Always');
            const isAlwaysB = b.dataset.time.includes('Always');

            if (isAlwaysA && !isAlwaysB) return -1;
            if (!isAlwaysA && isAlwaysB) return 1;
            return siteA.localeCompare(siteB);
        } else {
            return parseInt(a.dataset.index) - parseInt(b.dataset.index);
        }
    });

    rows.forEach(row => tbody.appendChild(row));
}
window.toggleHelp = () => {
    const modal = document.getElementById('help-modal');
    modal.style.display = (modal.style.display === 'none') ? 'flex' : 'none';
}
