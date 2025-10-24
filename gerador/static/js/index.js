// JavaScript específico para index.html
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Página inicial carregada');
    
    // Adicionar efeitos aos cards
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
    
    // Validação básica do formulário
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', function(e) {
            const fileInput = document.getElementById('file');
            if (fileInput && !fileInput.files[0]) {
                e.preventDefault();
                alert('Por favor, selecione um arquivo CSV.');
                return;
            }
            
            const file = fileInput.files[0];
            if (file) {
                const fileName = file.name.toLowerCase();
                if (!fileName.endsWith('.csv')) {
                    e.preventDefault();
                    alert('Por favor, selecione um arquivo CSV válido.');
                    return;
                }
            }
        });
    }
});