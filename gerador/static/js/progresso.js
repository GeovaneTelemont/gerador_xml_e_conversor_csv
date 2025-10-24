// JavaScript específico para progresso.html

let progressBar, progressText, progressPercent, currentCount, totalCount;
let logContainer, statusMessage, statusIcon, connectionStatus, statusText;
let actionButtons, resultButton;
let reconnectAttempts = 0;
const maxReconnectAttempts = 5;
let sseConnection;

function initProgresso() {
    progressBar = document.getElementById('progressBar');
    progressText = document.getElementById('progressText');
    progressPercent = document.getElementById('progressPercent');
    currentCount = document.getElementById('currentCount');
    totalCount = document.getElementById('totalCount');
    logContainer = document.getElementById('logContainer');
    statusMessage = document.getElementById('statusMessage');
    statusIcon = document.getElementById('statusIcon');
    connectionStatus = document.getElementById('connectionStatus');
    statusText = document.getElementById('statusText');
    actionButtons = document.getElementById('actionButtons');
    resultButton = document.getElementById('resultButton');

    sseConnection = connectSSE();

    document.addEventListener('visibilitychange', handleVisibilityChange);
    window.addEventListener('beforeunload', cleanup);
}

function handleVisibilityChange() {
    if (!document.hidden && (sseConnection.readyState === EventSource.CLOSED)) {
        addLog('🔄 Reconectando...');
        sseConnection = connectSSE();
    }
}

function cleanup() {
    if (sseConnection) {
        sseConnection.close();
    }
}

function addLog(message) {
    const logEntry = document.createElement('div');
    logEntry.className = 'log-entry';
    logEntry.innerHTML = message;
    logContainer.appendChild(logEntry);
    logContainer.scrollTop = logContainer.scrollHeight;
    
    const logs = logContainer.getElementsByClassName('log-entry');
    if (logs.length > 100) {
        logContainer.removeChild(logs[0]);
    }
}

function updateConnectionStatus(connected) {
    if (connected) {
        connectionStatus.className = 'connection-status connected';
        statusText.innerHTML = '<i class="fas fa-wifi"></i> Conectado';
        reconnectAttempts = 0;
    } else {
        connectionStatus.className = 'connection-status disconnected';
        statusText.innerHTML = '<i class="fas fa-wifi-slash"></i> Desconectado';
    }
}

function connectSSE() {
    updateConnectionStatus(false);
    
    const eventSource = new EventSource('/progress');

    eventSource.onopen = function() {
        console.log('Conexão SSE aberta');
        updateConnectionStatus(true);
        addLog('✅ Conectado ao servidor');
    };

    eventSource.onmessage = function(event) {
        try {
            const data = JSON.parse(event.data);
            
            if (data.progress !== undefined) {
                progressBar.style.width = data.progress + '%';
                progressText.textContent = Math.round(data.progress) + '%';
                progressPercent.textContent = Math.round(data.progress) + '%';
            }
            
            if (data.current !== undefined) {
                currentCount.textContent = data.current.toLocaleString();
            }
            if (data.total !== undefined) {
                totalCount.textContent = data.total.toLocaleString();
            }
            
            if (data.message) {
                statusMessage.textContent = data.message;
                if (data.message !== 'Aguardando...' && data.message !== 'Conectado...') {
                    addLog(data.message);
                }
            }
            
            if (data.status === 'completed') {
                statusIcon.className = 'fas fa-check-circle text-success';
                statusMessage.innerHTML = '<span class="text-success">✅ Processamento concluído com sucesso!</span>';
                actionButtons.style.display = 'block';
                resultButton.style.display = 'inline-block';
                eventSource.close();
                
            } else if (data.status === 'error') {
                statusIcon.className = 'fas fa-exclamation-triangle text-danger';
                statusMessage.innerHTML = '<span class="text-danger">❌ Erro no processamento!</span>';
                actionButtons.style.display = 'block';
                resultButton.style.display = 'none';
                eventSource.close();
            }
            
        } catch (e) {
            console.error('Erro ao processar mensagem:', e);
        }
    };

    eventSource.onerror = function(event) {
        console.error('Erro na conexão SSE:', event);
        updateConnectionStatus(false);
        eventSource.close();
        
        if (reconnectAttempts < maxReconnectAttempts) {
            reconnectAttempts++;
            addLog(`🔁 Tentativa de reconexão ${reconnectAttempts}/${maxReconnectAttempts}...`);
            setTimeout(connectSSE, 2000);
        } else {
            addLog('❌ Falha na conexão. Por favor, recarregue a página.');
            statusIcon.className = 'fas fa-exclamation-triangle text-danger';
            actionButtons.style.display = 'block';
        }
    };

    return eventSource;
}

// Inicializar quando o DOM estiver carregado
if (document.getElementById('progressBar')) {
    document.addEventListener('DOMContentLoaded', initProgresso);
}