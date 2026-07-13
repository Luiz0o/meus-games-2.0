document.addEventListener("DOMContentLoaded", function() {
    // Recupera o elemento invisível que transporta os dados do Flask
    const bridge = document.getElementById('data-bridge');
    if (!bridge) return;

    // Converte com segurança as strings JSON vindo do HTML em arrays do JavaScript
    const plataformasLabels = JSON.parse(bridge.getAttribute('data-plataformas-labels') || '[]');
    const plataformasValores = JSON.parse(bridge.getAttribute('data-plataformas-valores') || '[]');
    const notasValores = JSON.parse(bridge.getAttribute('data-notas-valores') || '[0,0,0,0,0]');
    const mesesLabels = JSON.parse(bridge.getAttribute('data-meses-labels') || '[]');
    const mesesValores = JSON.parse(bridge.getAttribute('data-meses-valores') || '[]');

    // Configurações globais de estilo do Chart.js para o tema Dark
    Chart.defaults.color = '#9ca3af';
    Chart.defaults.font.family = 'Arial, sans-serif';

    // 1. Gráfico de Rosca: Distribuição por Plataforma
    const ctxPlat = document.getElementById('chartPlataformas');
    if (ctxPlat) {
        new Chart(ctxPlat.getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: plataformasLabels,
                datasets: [{
                    data: plataformasValores,
                    backgroundColor: ['#2563eb', '#3b82f6', '#60a5fa', '#93c5fd', '#1d4ed8'],
                    borderWidth: 2,
                    borderColor: '#0b0f19',
                    cutout: '60%'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom', labels: { boxWidth: 12, padding: 15 } }
                }
            }
        });
    }

    // 2. Gráfico de Barras: Jogos por Avaliação
    const ctxEval = document.getElementById('chartAvaliacoes');
    if (ctxEval) {
        new Chart(ctxEval.getContext('2d'), {
            type: 'bar',
            data: {
                labels: ['1★', '2★', '3★', '4★', '5★'],
                datasets: [{
                    data: notasValores,
                    backgroundColor: '#8b5cf6',
                    borderRadius: 8,
                    barThickness: 32
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { grid: { display: false } },
                    y: { 
                        beginAtZero: true,
                        ticks: { stepSize: 1 },
                        grid: { color: 'rgba(255, 255, 255, 0.05)' }
                    }
                }
            }
        });
    }

    // 3. Gráfico de Linha: Evolução por Mês
    const ctxEvol = document.getElementById('chartEvolucao');
    if (ctxEvol) {
        new Chart(ctxEvol.getContext('2d'), {
            type: 'line',
            data: {
                labels: mesesLabels,
                datasets: [{
                    data: mesesValores,
                    borderColor: '#2563eb',
                    backgroundColor: '#2563eb',
                    borderWidth: 2,
                    pointRadius: 6,
                    pointHoverRadius: 8,
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { grid: { display: false } },
                    y: {
                        beginAtZero: true,
                        ticks: { stepSize: 1 },
                        grid: { color: 'rgba(255, 255, 255, 0.05)' }
                    }
                }
            }
        });
    }
});