// JavaScript específico para sobre.html

document.addEventListener('DOMContentLoaded', function() {
    console.log('ℹ️ Página sobre carregada');
    
    // Adicionar animações simples
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            card.style.transition = 'all 0.5s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 200);
    });
});