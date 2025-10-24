// JavaScript específico para conversor_csv.html

// Elementos da página
let fileInput, fileInfo, submitBtn, validationResult, validationContent, loadingSpinner;
let validationTimer;
let seconds = 0;

function initConversor() {
    fileInput = document.getElementById('file');
    fileInfo = document.getElementById('fileInfo');
    submitBtn = document.getElementById('submitBtn');
    validationResult = document.getElementById('validationResult');
    validationContent = document.getElementById('validationContent');
    
    createLoadingSpinner();
    setupEventListeners();
}

function createLoadingSpinner() {
    loadingSpinner = document.createElement('div');
    loadingSpinner.id = 'loadingSpinner';
    loadingSpinner.className = 'loading-spinner';
    
    const spinnerHTML = `
        <div class="spinner"></div>
        <span style="margin-left: 10px; color: #3498db;">Validando arquivo...</span>
        <div style="font-size: 12px; color: #666; margin-top: 5px;" id="loadingTime">Tempo: 0s</div>
    `;
    
    loadingSpinner.innerHTML = spinnerHTML;
    fileInfo.parentNode.insertBefore(loadingSpinner, fileInfo.nextSibling);
}

function setupEventListeners() {
    fileInput.addEventListener('change', handleFileChange);
    
    const uploadForm = document.getElementById('uploadForm');
    if (uploadForm) {
        uploadForm.addEventListener('submit', handleFormSubmit);
    }
    
    window.addEventListener('beforeunload', stopTimer);
}

async function handleFileChange(e) {
    validationResult.style.display = 'none';
    submitBtn.disabled = true;
    stopTimer();
    
    if (this.files && this.files[0]) {
        const file = this.files[0];
        startTimer();
        atualizarFileInfo('🔍 Validando estrutura do arquivo CSV...', 'text-warning');
        
        try {
            const resultadoEstrutura = await validarEstruturaArquivo(file);
            stopTimer();
            
            if (!resultadoEstrutura.valido) {
                showValidationResult(resultadoEstrutura.dados);
                atualizarFileInfo(`📁 ${file.name} - Estrutura inválida`, 'text-danger');
                return;
            }
            
            const resultadoTamanho = validarTamanhoArquivo(file);
            showValidationResult(resultadoEstrutura.dados);
            
            const infoBase = `📁 Arquivo: ${file.name}`;
            if (resultadoTamanho.valido) {
                atualizarFileInfo(`${infoBase} | ${resultadoTamanho.mensagem}`, 
                               resultadoTamanho.mensagem.includes('⚠️') ? 'text-warning' : 'text-success');
            } else {
                atualizarFileInfo(`${infoBase} | ${resultadoTamanho.mensagem}`, 'text-danger');
                submitBtn.disabled = true;
            }
            
        } catch (error) {
            stopTimer();
            console.error('Erro no processo de validação:', error);
            atualizarFileInfo('❌ Erro durante a validação do arquivo', 'text-danger');
            showValidationResult({
                valido: false,
                erro: 'Falha no processo de validação'
            });
        }
        
    } else {
        atualizarFileInfo('📁 Tamanho máximo: 2GB | Formato: CSV com separador |');
        submitBtn.disabled = true;
    }
}

function handleFormSubmit(e) {
    if (submitBtn.disabled) {
        e.preventDefault();
        alert('Por favor, selecione um arquivo CSV válido antes de converter.');
    }
}

function startTimer() {
    seconds = 0;
    const timeElement = document.getElementById('loadingTime');
    timeElement.textContent = `Tempo: 0s`;
    
    validationTimer = setInterval(() => {
        seconds++;
        timeElement.textContent = `Tempo: ${seconds}s`;
    }, 1000);
    
    loadingSpinner.style.display = 'block';
}

function stopTimer() {
    if (validationTimer) {
        clearInterval(validationTimer);
        validationTimer = null;
    }
    loadingSpinner.style.display = 'none';
}

function showValidationResult(result) {
    validationResult.style.display = 'block';
    
    if (result.valido) {
        validationResult.className = 'validation-result validation-success';
        let html = `<strong>✅ Arquivo válido!</strong><br>`;
        html += `${result.total_colunas} - Colunas encontradas<br>`;
        if (result.colunas_extras && result.colunas_extras.length > 0) {
            html += `<small>Colunas extras: ${result.colunas_extras.join(', ')}</small>`;
        }
        validationContent.innerHTML = html;
        submitBtn.disabled = false;
    } else {
        validationResult.className = 'validation-result validation-error';
        let html = `<strong>❌ Arquivo inválido!</strong><br>`;
        if (result.erro) {
            html += `Erro: ${result.erro}`;
        } else {
            html += `Colunas faltantes: ${result.colunas_faltantes.join(', ')}<br>`;
            html += `Total de colunas no arquivo: ${result.total_colunas}`;
        }
        validationContent.innerHTML = html;
        submitBtn.disabled = true;
    }
}

function validarTamanhoArquivo(file) {
    const fileSizeMB = (file.size / (1024 * 1024)).toFixed(2);
    const fileSizeGB = (file.size / (1024 * 1024 * 1024)).toFixed(2);
    
    const LIMITE_PEQUENO = 5;
    const LIMITE_GRANDE = 100;
    const LIMITE_MAXIMO = 2 * 1024;
    
    if (file.size > LIMITE_MAXIMO * 1024 * 1024) {
        return {
            valido: false,
            tipo: 'tamanho',
            mensagem: `❌ Arquivo muito grande! Tamanho: ${fileSizeGB} GB (Máximo: 2GB)`
        };
    } else if (file.size > LIMITE_GRANDE * 1024 * 1024) {
        return {
            valido: true,
            tipo: 'tamanho',
            mensagem: `⚠️ Arquivo grande: ${fileSizeMB} MB. A conversão pode demorar.`
        };
    } else if (file.size < LIMITE_PEQUENO * 1024 * 1024) {
        return {
            valido: true,
            tipo: 'tamanho',
            mensagem: `📄 Arquivo pequeno: ${fileSizeMB} MB. Processamento rápido.`
        };
    } else {
        return {
            valido: true,
            tipo: 'tamanho',
            mensagem: `📊 Arquivo de tamanho moderado: ${fileSizeMB} MB.`
        };
    }
}

function validarEstruturaArquivo(file) {
    const formData = new FormData();
    formData.append('file', file);

    return fetch('/validar-csv', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        return {
            valido: data.valido,
            tipo: 'estrutura',
            dados: data
        };
    })
    .catch(error => {
        console.error('Erro na validação:', error);
        return {
            valido: false,
            tipo: 'estrutura',
            dados: {
                valido: false,
                erro: 'Erro ao validar estrutura do arquivo'
            }
        };
    });
}

function atualizarFileInfo(mensagem, classe = '') {
    if (classe) {
        fileInfo.innerHTML = `<span class="${classe}">${mensagem}</span>`;
    } else {
        fileInfo.innerHTML = mensagem;
    }
}

// Inicializar quando o DOM estiver carregado
if (document.getElementById('file')) {
    document.addEventListener('DOMContentLoaded', initConversor);
}