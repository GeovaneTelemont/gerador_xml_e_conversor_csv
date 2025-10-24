// JavaScript específico para resultado.html e resultado_conversor.html

document.addEventListener('DOMContentLoaded', function() {
    console.log('🎉 Página de resultados carregada');
    
    // Adicionar funcionalidade para copiar log
    const logPre = document.querySelector('pre');
    if (logPre) {
        logPre.addEventListener('click', function() {
            const textArea = document.createElement('textarea');
            textArea.value = logPre.textContent;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            
            // Feedback visual
            const originalText = logPre.textContent;
            logPre.textContent = '✅ Log copiado para a área de transferência!';
            setTimeout(() => {
                logPre.textContent = originalText;
            }, 2000);
        });
        
        logPre.title = "Clique para copiar o log";
        logPre.style.cursor = "pointer";
    }
    
    // Verificar se há alerta de erro
    const downloadBtn = document.querySelector('.btn-primary');
    if (downloadBtn && downloadBtn.classList.contains('disabled')) {
        console.warn('⚠️ Download desabilitado devido a erros no processamento');
    }
});