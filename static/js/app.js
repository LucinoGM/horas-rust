/* ═══════════════════════════════════════════════
   RUST HOURS API - JavaScript
   ═══════════════════════════════════════════════ */

// Configuração
const API_URL = '/api/status';
const REFRESH_INTERVAL = 10000; // 10 segundos

// Estado
let pingCount = parseInt(localStorage.getItem('rust_pingCount') || '0');
let startTime = parseInt(localStorage.getItem('rust_startTime') || Date.now());
let checkCount = parseInt(localStorage.getItem('rust_checkCount') || '0');
let lastPingTime = parseInt(localStorage.getItem('rust_lastPing') || '0');

// Salvar startTime na primeira vez
if (!localStorage.getItem('rust_startTime')) {
    localStorage.setItem('rust_startTime', startTime);
}

// Elementos DOM
const els = {
    statusDot: document.getElementById('statusDot'),
    statusText: document.getElementById('statusText'),
    rustHours: document.getElementById('rustHours'),
    rustDate: document.getElementById('rustDate'),
    uptime: document.getElementById('uptime'),
    lastPing: document.getElementById('lastPing'),
    timeSinceLastPing: document.getElementById('timeSinceLastPing'),
    responseTime: document.getElementById('responseTime'),
    checks: document.getElementById('checks'),
    currentGame: document.getElementById('currentGame'),
    currentGameTime: document.getElementById('currentGameTime'),
    profileAvatar: document.getElementById('profileAvatar'),
    profileName: document.getElementById('profileName'),
    profileState: document.getElementById('profileState'),
    pingCount: document.getElementById('pingCount'),
    progressFill: document.getElementById('progressFill'),
    progressPercent: document.getElementById('progressPercent'),
    monitorBadge: document.getElementById('monitorBadge')
};

// ═══════════════════════════════════════════════
// FUNÇÕES UTILITÁRIAS
// ═══════════════════════════════════════════════

function formatUptime(ms) {
    const seconds = Math.floor(ms / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    const parts = [];
    if (days > 0) parts.push(`${days}d`);
    if (hours % 24 > 0) parts.push(`${hours % 24}h`);
    if (minutes % 60 > 0) parts.push(`${minutes % 60}m`);
    if (seconds % 60 > 0 && days === 0) parts.push(`${seconds % 60}s`);

    return parts.join(' ') || '0s';
}

function formatTimeAgo(timestamp) {
    if (!timestamp) return 'Nunca';
    const diff = Date.now() - timestamp;
    const seconds = Math.floor(diff / 1000);

    if (seconds < 5) return 'Agora';
    if (seconds < 60) return `${seconds}s`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h`;
    return `${Math.floor(seconds / 86400)}d`;
}

function updateProgress() {
    const maxPings = 1000;
    const progress = Math.min((pingCount / maxPings) * 100, 100);

    els.progressFill.style.width = `${progress}%`;
    els.progressPercent.textContent = `${Math.round(progress)}%`;

    // Mudar cor baseado no progresso
    if (progress < 30) {
        els.progressFill.style.background = 'linear-gradient(90deg, #ff4444, #ff6b35)';
    } else if (progress < 70) {
        els.progressFill.style.background = 'linear-gradient(90deg, #ffcc00, #ff6b35)';
    } else {
        els.progressFill.style.background = 'linear-gradient(90deg, #00ff88, #00d4ff)';
    }
}

function renderAnalytics(analytics) {
    const chart = document.getElementById('hoursChart');
    const rankingList = document.getElementById('rankingList');
    const calendarGrid = document.getElementById('calendarGrid');

    if (chart && analytics?.chart) {
        const maxValue = Math.max(...analytics.chart.values, 1);
        chart.innerHTML = analytics.chart.labels.map((label, index) => {
            const value = analytics.chart.values[index] || 0;
            const percentage = Math.max(8, (value / maxValue) * 100);
            return `
                <div class="chart-bar-group">
                    <div class="chart-bar-track">
                        <div class="chart-bar" style="height: ${percentage}%"></div>
                    </div>
                    <div class="chart-label">${label}</div>
                    <div class="chart-value">${value}h</div>
                </div>
            `;
        }).join('');
    }

    if (rankingList && analytics?.ranking) {
        rankingList.innerHTML = analytics.ranking.map((entry, index) => `
            <li class="ranking-item">
                <span class="ranking-rank">#${index + 1}</span>
                <div class="ranking-avatar" style="background-image: url('${entry.avatar || 'https://via.placeholder.com/48?text=STEAM'}')"></div>
                <div class="ranking-info">
                    <strong>${entry.name}</strong>
                    <span>${entry.hours}h · ${entry.status}</span>
                </div>
            </li>
        `).join('');
    }

    if (calendarGrid && analytics?.calendar) {
        calendarGrid.innerHTML = analytics.calendar.map((day) => `
            <div class="calendar-day">
                <div class="calendar-label">${day.label}</div>
                <div class="calendar-number">${day.day}</div>
                <div class="calendar-hours">${day.hours}h</div>
            </div>
        `).join('');
    }
}

// ═══════════════════════════════════════════════
// VERIFICAR STATUS
// ═══════════════════════════════════════════════

function setToggleButtonState(enabled) {
    const toggleBtn = document.getElementById('toggleApiBtn');
    if (!toggleBtn) return;

    toggleBtn.classList.toggle('active', enabled);
    toggleBtn.innerHTML = `<span class="toggle-icon">${enabled ? '⚡' : '🔌'}</span>${enabled ? 'Desligar API' : 'Ligar API'}`;
}

async function checkStatus() {
    // Estado de loading
    els.statusDot.className = 'status-dot loading';
    els.statusText.className = 'status-text loading';
    els.statusText.textContent = 'Verificando...';
    els.responseTime.textContent = '--';

    // Não marcar como offline só porque a página fez um refresh automático
    if (lastPingTime) {
        els.lastPing.textContent = formatTimeAgo(lastPingTime);
    }

    const start = performance.now();

    try {
        const response = await fetch(API_URL, {
            method: 'GET',
            cache: 'no-cache',
            headers: { 'Accept': 'application/json' }
        });

        const end = performance.now();
        const responseTime = Math.round(end - start);

        if (response.ok) {
            const data = await response.json();

            if (data.online) {
                setToggleButtonState(true);

                // API Online!
                els.statusDot.className = 'status-dot online';
                els.statusText.className = 'status-text online';
                els.statusText.textContent = '✅ API Online';

                // Atualizar horas do Rust
                els.rustHours.textContent = data.hours_formatted;
                els.rustDate.textContent = `Registrado em ${data.date}`;

                // Atualizar contadores
                pingCount = typeof data.ping_count === 'number' ? data.ping_count : pingCount;
                localStorage.setItem('rust_pingCount', pingCount);
                els.pingCount.textContent = pingCount;

                // Atualizar perfil Steam
                els.profileAvatar.src = data.profile_avatar || 'https://via.placeholder.com/96?text=STEAM';
                els.profileName.textContent = data.profile_name || 'Perfil Steam';
                if (data.current_game) {
                    els.profileState.textContent = `Jogando agora`;
                } else {
                    els.profileState.textContent = data.profile_state || 'Offline';
                }

                // Atualizar jogo atual
                if (data.current_game) {
                    els.currentGame.textContent = data.current_game;
                    els.currentGameTime.textContent = data.current_game_hours !== null && data.current_game_hours !== undefined ? `${data.current_game_hours}h jogadas` : 'Tempo de jogo indisponível';
                } else {
                    els.currentGame.textContent = data.profile_state ? `${data.profile_state}` : 'Offline';
                    els.currentGameTime.textContent = data.profile_state === 'Online' ? 'Não está jogando nenhum jogo' : 'Offline no Steam';
                }

                if (data.analytics) {
                    renderAnalytics(data.analytics);
                }

                // Atualizar último ping
                if (typeof data.last_ping_timestamp === 'number') {
                    lastPingTime = data.last_ping_timestamp * 1000;
                } else {
                    lastPingTime = Date.now();
                }
                localStorage.setItem('rust_lastPing', lastPingTime);
                els.lastPing.textContent = data.last_ping_at ? `Último ping: ${data.last_ping_at}` : 'Agora';
                els.timeSinceLastPing.textContent = 'agora';
                els.monitorBadge.className = 'live-badge active';
                els.monitorBadge.innerHTML = '<span class="live-pulse"></span>MONITOR ATIVO';

                // Tempo de resposta
                els.responseTime.textContent = `${responseTime}ms`;

                // Cor do tempo de resposta
                if (responseTime < 500) {
                    els.responseTime.style.color = '#00ff88';
                } else if (responseTime < 1500) {
                    els.responseTime.style.color = '#ffcc00';
                } else {
                    els.responseTime.style.color = '#ff4444';
                }

            } else {
                throw new Error(data.error || 'API retornou offline');
            }

        } else {
            throw new Error(`HTTP ${response.status}`);
        }

    } catch (error) {
        setToggleButtonState(false);

        // API Offline
        els.statusDot.className = 'status-dot offline';
        els.statusText.className = 'status-text offline';
        els.statusText.textContent = '❌ API Offline';
        els.responseTime.textContent = 'Timeout';
        els.responseTime.style.color = '#ff4444';
        els.lastPing.textContent = formatTimeAgo(lastPingTime);
        els.timeSinceLastPing.textContent = lastPingTime ? formatTimeAgo(lastPingTime) : 'nunca';
    }

    // Incrementar contador de checks
    checkCount++;
    localStorage.setItem('rust_checkCount', checkCount);
    els.checks.textContent = checkCount;

    // Atualizar progresso
    updateProgress();
}

// ═══════════════════════════════════════════════
// ATUALIZAR UPTIME (a cada segundo)
// ═══════════════════════════════════════════════

function updateUptime() {
    const uptime = Date.now() - startTime;
    els.uptime.textContent = formatUptime(uptime);
}

async function toggleApiStatus() {
    try {
        const response = await fetch('/api/toggle-status', {
            method: 'POST',
            headers: { 'Accept': 'application/json' }
        });

        if (!response.ok) {
            throw new Error('Falha ao alternar API');
        }

        const data = await response.json();
        setToggleButtonState(data.enabled);

        if (!data.enabled) {
            els.statusDot.className = 'status-dot offline';
            els.statusText.className = 'status-text offline';
            els.statusText.textContent = '🔌 API Desligada';
            els.rustHours.textContent = '--';
            els.rustDate.textContent = 'Dados reiniciados';
            els.responseTime.textContent = 'Off';
            els.responseTime.style.color = '#ffcc00';
            els.lastPing.textContent = 'Nenhum ping';
            els.timeSinceLastPing.textContent = 'desligada';
            els.pingCount.textContent = '0';
            els.checks.textContent = '0';
            els.uptime.textContent = '0s';
            els.monitorBadge.className = 'live-badge inactive';
            els.monitorBadge.innerHTML = '<span class="live-pulse"></span>MONITOR INATIVO';
            pingCount = 0;
            checkCount = 0;
            lastPingTime = 0;
            localStorage.setItem('rust_pingCount', '0');
            localStorage.setItem('rust_checkCount', '0');
            localStorage.setItem('rust_lastPing', '0');
        } else {
            checkStatus();
        }
    } catch (error) {
        console.error(error);
    }
}

// Atualizar "último ping" a cada segundo
function updateLastPing() {
    if (lastPingTime) {
        const ago = formatTimeAgo(lastPingTime);
        els.lastPing.textContent = ago;
        els.timeSinceLastPing.textContent = ago === 'Agora' ? 'agora' : ago;

        const minutesSinceLastPing = Math.floor((Date.now() - lastPingTime) / 60000);
        if (minutesSinceLastPing <= 10) {
            els.monitorBadge.className = 'live-badge active';
            els.monitorBadge.innerHTML = '<span class="live-pulse"></span>MONITOR ATIVO';
        } else {
            els.monitorBadge.className = 'live-badge inactive';
            els.monitorBadge.innerHTML = '<span class="live-pulse"></span>MONITOR INATIVO';
        }
    } else {
        els.timeSinceLastPing.textContent = 'nunca';
        els.monitorBadge.className = 'live-badge inactive';
        els.monitorBadge.innerHTML = '<span class="live-pulse"></span>MONITOR INATIVO';
    }
}

// ═══════════════════════════════════════════════
// INICIALIZAÇÃO
// ═══════════════════════════════════════════════

function init() {
    // Inicializar valores
    els.pingCount.textContent = pingCount;
    els.checks.textContent = checkCount;
    updateProgress();

    const toggleBtn = document.getElementById('toggleApiBtn');
    if (toggleBtn) {
        toggleBtn.innerHTML = '<span class="toggle-icon">⚡</span>Desligar API';
        toggleBtn.classList.add('active');
    }

    // Primeira verificação
    checkStatus();

    // Atualizar uptime a cada segundo
    setInterval(updateUptime, 1000);
    updateUptime();

    // Atualizar "último ping" a cada 5 segundos
    setInterval(updateLastPing, 5000);

    // Verificar status a cada 10 segundos
    setInterval(checkStatus, REFRESH_INTERVAL);
}

// Iniciar quando DOM estiver pronto
document.addEventListener('DOMContentLoaded', init);
