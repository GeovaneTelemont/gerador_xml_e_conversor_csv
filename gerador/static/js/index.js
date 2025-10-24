// Colunas obrigatórias - nomes exatos das colunas
const COLUNAS_OBRIGATORIAS = [
    'CHAVE LOG',
    'CELULA',
    'ESTACAO_ABASTECEDORA',
    'UF',
    'MUNICIPIO',
    'LOCALIDADE',
    'COD_LOCALIDADE',
    'LOCALIDADE_ABREV',
    'LOGRADOURO',
    'COD_LOGRADOURO',
    'NUM_FACHADA',
    'COMPLEMENTO',
    'COMPLEMENTO2',
    'COMPLEMENTO3',
    'CEP',
    'BAIRRO',
    'COD_SURVEY',
    'QUANTIDADE_UMS',
    'COD_VIABILIDADE',
    'TIPO_VIABILIDADE',
    'TIPO_REDE',
    'UCS_RESIDENCIAIS',
    'UCS_COMERCIAIS',
    'NOME_CDO',
    'ID_ENDERECO',
    'LATITUDE',
    'LONGITUDE',
    'TIPO_SURVEY',
    'REDE_INTERNA',
    'UMS_CERTIFICADAS',
    'REDE_EDIF_CERT',
    'DISP_COMERCIAL',
    'ESTADO_CONTROLE',
    'DATA_ESTADO_CONTROLE',
    'ID_CELULA',
    'QUANTIDADE_HCS',
    'ID_ROTEIRO',
    'ID_LOCALIDADE',
    'COD_ZONA',
    'ORDEM',
    'RESULTADO',
    'COMPARATIVO',
    'NUM_ARGUMENTO3_COMPLEMENTO3',
    'VALIDACAO'
];

let validationTimeout = null;

// JavaScript específico para index.html
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Página inicial carregada');
    
    // Adicionar efeitos aos cards
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.transition = 'transform 0.3s ease';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
    
    // Inicializar a lista de colunas obrigatórias na página
    displayRequiredColumns();
    
    // Configurar validação do arquivo CSV
    const fileInput = document.getElementById('file');
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                validateCSV(file);
            } else {
                resetValidation();
            }
        });
    }
    
    // Validação do formulário
    const form = document.getElementById('uploadForm');
    if (form) {
        form.addEventListener('submit', function(e) {
            const fileInput = document.getElementById('file');
            const processButton = document.getElementById('processButton');
            
            // Validação básica do arquivo
            if (!fileInput || !fileInput.files[0]) {
                e.preventDefault();
                showBootstrapAlert('danger', '❌ Por favor, selecione um arquivo CSV.');
                return;
            }
            
            const file = fileInput.files[0];
            if (file) {
                const fileName = file.name.toLowerCase();
                if (!fileName.endsWith('.csv')) {
                    e.preventDefault();
                    showBootstrapAlert('danger', '❌ Por favor, selecione um arquivo CSV válido.');
                    return;
                }
            }
            
            // REMOVIDO: Verificação que bloqueava o envio por validação de colunas
            // A validação detalhada será feita pelo Flask
            
            // Mostrar loading no submit
            const originalText = processButton.innerHTML;
            processButton.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processando...';
            processButton.disabled = true;
            
            // Restaurar botão se o formulário falhar
            setTimeout(() => {
                processButton.innerHTML = originalText;
                processButton.disabled = false;
            }, 5000);
        });
    }
});

function displayRequiredColumns() {
    const container = document.getElementById('requiredColumnsList');
    if (!container) {
        console.warn('❌ Elemento #requiredColumnsList não encontrado');
        return;
    }
    
    const groups = [];
    
    // Dividir colunas em grupos de 4 para melhor visualização (são muitas colunas)
    for (let i = 0; i < COLUNAS_OBRIGATORIAS.length; i += 4) {
        groups.push(COLUNAS_OBRIGATORIAS.slice(i, i + 4));
    }
    
    container.innerHTML = ''; // Limpar conteúdo anterior
    
    groups.forEach(group => {
        const groupDiv = document.createElement('div');
        groupDiv.className = 'd-flex flex-wrap mb-2';
        group.forEach(col => {
            const badge = document.createElement('span');
            badge.className = 'badge bg-primary required-columns-badge me-1 mb-1';
            badge.style.fontSize = '0.7rem';
            badge.textContent = col;
            groupDiv.appendChild(badge);
        });
        container.appendChild(groupDiv);
    });
}

function validateCSV(file) {
    // Limpar timeout anterior
    if (validationTimeout) {
        clearTimeout(validationTimeout);
    }

    // Mostrar status de validação
    showValidationStatus('Lendo arquivo...', true);
    hideValidationResult();

    // Desabilitar botão durante a validação
    const processButton = document.getElementById('processButton');
    if (processButton) {
        processButton.disabled = true;
    }

    // Usar timeout para dar feedback visual
    validationTimeout = setTimeout(() => {
        const reader = new FileReader();
        
        reader.onload = function(e) {
            try {
                showValidationStatus('Validando colunas...', true);
                
                const csvContent = e.target.result;
                const lines = csvContent.split('\n');
                const firstLine = lines[0];
                
                if (!firstLine || firstLine.trim() === '') {
                    throw new Error('Arquivo CSV vazio ou primeira linha inválida');
                }
                
                // Detectar separador (ponto e vírgula ou vírgula)
                const separator = firstLine.includes(';') ? ';' : ',';
                const headers = firstLine.split(separator).map(header => header.trim());
                
                // Normalizar headers para comparação (case insensitive e remove espaços extras)
                const normalizedHeaders = headers.map(header => 
                    header.toLowerCase().replace(/\s+/g, ' ').trim()
                );
                const normalizedRequired = COLUNAS_OBRIGATORIAS.map(col => 
                    col.toLowerCase().replace(/\s+/g, ' ').trim()
                );
                
                // Encontrar colunas faltantes e colunas válidas
                const missingColumns = [];
                const validColumns = [];
                const extraColumns = [];
                
                // Verificar colunas obrigatórias
                normalizedRequired.forEach((requiredCol, index) => {
                    if (normalizedHeaders.includes(requiredCol)) {
                        validColumns.push(COLUNAS_OBRIGATORIAS[index]);
                    } else {
                        missingColumns.push(COLUNAS_OBRIGATORIAS[index]);
                    }
                });
                
                // Verificar colunas extras
                normalizedHeaders.forEach((header, index) => {
                    if (!normalizedRequired.includes(header)) {
                        extraColumns.push(headers[index]);
                    }
                });
                
                // Mostrar resultado com alerts Bootstrap
                showValidationResult(missingColumns, validColumns, extraColumns, headers.length);
                
            } catch (error) {
                console.error('Erro na validação:', error);
                showValidationStatus('❌ Erro ao validar o arquivo', false);
                showBootstrapAlert('danger', `❌ Erro na validação: ${error.message}`);
                const processButton = document.getElementById('processButton');
                if (processButton) {
                    processButton.disabled = true;
                }
            }
        };
        
        reader.onerror = function() {
            showValidationStatus('❌ Erro ao ler o arquivo', false);
            showBootstrapAlert('danger', '❌ Não foi possível ler o arquivo. Verifique se o arquivo não está corrompido.');
            const processButton = document.getElementById('processButton');
            if (processButton) {
                processButton.disabled = true;
            }
        };
        
        reader.readAsText(file, 'UTF-8');
        
    }, 300);
}

function showValidationStatus(message, showSpinner) {
    const statusElement = document.getElementById('validationStatus');
    const messageElement = document.getElementById('validationMessage');
    const spinnerElement = document.getElementById('validationSpinner');
    
    if (statusElement && messageElement && spinnerElement) {
        statusElement.style.display = 'block';
        messageElement.textContent = message;
        spinnerElement.style.display = showSpinner ? 'inline-block' : 'none';
    }
}

function hideValidationResult() {
    // Esconder elementos se existirem, senão não faz nada
    const elements = [
        'validationResult', 'missingColumnsAlert', 'extraColumnsAlert', 'successAlert'
    ];
    
    elements.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.style.display = 'none';
        }
    });
}

function showValidationResult(missingColumns, validColumns, extraColumns, totalColumns) {
    const processButton = document.getElementById('processButton');
    
    if (!processButton) {
        console.error('❌ Elemento processButton não encontrado');
        return;
    }
    
    // SEMPRE habilitar o botão - a validação detalhada será feita no Flask
    processButton.disabled = false;
    
    // Criar ou obter o container de resultados
    let validationResult = document.getElementById('validationResult');
    if (!validationResult) {
        validationResult = document.createElement('div');
        validationResult.id = 'validationResult';
        validationResult.className = 'mb-3';
        
        // Inserir após o status de validação
        const validationStatus = document.getElementById('validationStatus');
        if (validationStatus) {
            validationStatus.parentNode.insertBefore(validationResult, validationStatus.nextSibling);
        } else {
            // Inserir antes do botão como fallback
            processButton.parentNode.insertBefore(validationResult, processButton);
        }
    }
    
    validationResult.style.display = 'block';
    validationResult.innerHTML = ''; // Limpar conteúdo anterior
    
    if (missingColumns.length > 0) {
        // Verificar se há alguma coluna válida
        if (validColumns.length > 0) {
            // MOSTRAR COLUNAS FALTANTES - há colunas válidas (apenas informativo)
            const missingColumnsText = missingColumns.join(', ');
            
            const warningAlert = `
                <div class="alert alert-warning">
                    <h6 class="alert-heading"><i class="fas fa-exclamation-triangle me-2"></i>Colunas Faltantes Detectadas</h6>
                    <div class="mb-2">
                        <strong>Colunas faltantes:</strong> ${missingColumnsText}
                    </div>
                    <div class="mt-2">
                        ${missingColumns.map(col => `<span class="badge bg-warning text-dark me-1 mb-1">${col}</span>`).join('')}
                    </div>
                    <small class="text-muted">A validação detalhada será feita no servidor. Você pode prosseguir com o envio.</small>
                </div>
            `;
            
            validationResult.innerHTML = warningAlert;
            showValidationStatus(`⚠️ ${missingColumns.length} colunas faltantes detectadas`, false);
            
        } else {
            // ARQUIVO INVÁLIDO - nenhuma coluna válida encontrada
            const dangerAlert = `
                <div class="alert alert-danger">
                    <h6 class="alert-heading"><i class="fas fa-exclamation-triangle me-2"></i>Arquivo inválido</h6>
                    <p class="mb-0">O arquivo não contém nenhuma coluna obrigatória válida.</p>
                </div>
            `;
            
            validationResult.innerHTML = dangerAlert;
            showValidationStatus('❌ Arquivo inválido', false);
            processButton.disabled = true;
        }
        
    } else {
        if (extraColumns.length > 0) {
            // ALERT BOOTSTRAP DE SUCCESS - Tudo certo (ignora colunas extras)
            const successAlert = `
                <div class="alert alert-success">
                    <h6 class="alert-heading"><i class="fas fa-check-circle me-2"></i>Validação Básica Concluída</h6>
                    <p class="mb-0">Todas as colunas obrigatórias estão presentes. A validação detalhada será feita no servidor.</p>
                </div>
            `;
            
            validationResult.innerHTML = successAlert;
            showValidationStatus(`✅ Validação básica concluída - ${totalColumns} colunas detectadas`, false);
            
        } else {
            // ALERT BOOTSTRAP DE SUCCESS - Tudo certo
            const successAlert = `
                <div class="alert alert-success">
                    <h6 class="alert-heading"><i class="fas fa-check-circle me-2"></i>Validação Básica Concluída</h6>
                    <p class="mb-0">Todas as colunas obrigatórias estão presentes. A validação detalhada será feita no servidor.</p>
                </div>
            `;
            
            validationResult.innerHTML = successAlert;
            showValidationStatus(`✅ Validação básica concluída - ${totalColumns} colunas detectadas`, false);
        }
    }
}

function showBootstrapAlert(type, message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Adicionar no início do container de mensagens
    const flashMessages = document.getElementById('flash-messages');
    if (flashMessages) {
        flashMessages.prepend(alertDiv);
        
        // Auto-remover após 8 segundos
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 8000);
    }
}

function resetValidation() {
    hideValidationResult();
    const statusElement = document.getElementById('validationStatus');
    const processButton = document.getElementById('processButton');
    
    if (statusElement) statusElement.style.display = 'none';
    if (processButton) processButton.disabled = true;
}