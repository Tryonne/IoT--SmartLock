// analytics.js

// Função para atualizar os dados das métricas e gráficos
function atualizarDados() {
    fetch('/analytics/dados')
        .then(response => response.json())
        .then(data => {
            // Atualiza as métricas principais
            document.querySelector('.metric-value:nth-child(1)').textContent = data.total_acessos;
            document.querySelector('.metric-value:nth-child(2)').textContent = data.taxa_sucesso + '%';
            document.querySelector('.metric-value:nth-child(3)').textContent = data.horario_pico;
            document.querySelector('.metric-value:nth-child(4)').textContent = data.tentativas_negadas;

            // Atualiza o gráfico de linha
            lineChart.data.labels = data.dias;
            lineChart.data.datasets[0].data = data.acessos_por_dia;
            lineChart.update();

            // Atualiza o gráfico de pizza
            pieChart.data.datasets[0].data = data.tipos_acesso;
            pieChart.update();

            // Atualiza a tabela de últimos acessos
            const tbody = document.querySelector('table tbody');
            tbody.innerHTML = '';
            data.ultimos_acessos.forEach(acesso => {
                tbody.innerHTML += `
                    <tr>
                        <td>${acesso.data}</td>
                        <td>${acesso.tipo}</td>
                        <td>
                            <span class="badge ${acesso.status === 'autorizado' ? 'bg-success' : 'bg-danger'}">
                                ${acesso.status}
                            </span>
                        </td>
                        <td>${acesso.metodo}</td>
                    </tr>
                `;
            });
        })
        .catch(error => console.error('Erro ao atualizar dados:', error));
}

// Inicialização dos gráficos Chart.js
document.addEventListener('DOMContentLoaded', function() {
    // Configuração do gráfico de linha
    const ctxLine = document.getElementById('acessosPorDia').getContext('2d');
    window.lineChart = new Chart(ctxLine, lineChartConfig);

    // Configuração do gráfico de pizza
    const ctxPie = document.getElementById('tiposAcesso').getContext('2d');
    window.pieChart = new Chart(ctxPie, {
        type: 'pie',
        data: {
            labels: ['PIN', 'QR Code', 'Outros'],
            datasets: [{
                data: window.tiposAcessoData, // Definido no HTML
                backgroundColor: ['#2ecc71', '#3498db', '#95a5a6'],
                borderWidth: 2,
                borderColor: '#ffffff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'bottom',
                    labels: {
                        font: {
                            family: "'Helvetica Neue', 'Helvetica', 'Arial', sans-serif",
                            size: 12
                        },
                        padding: 20
                    }
                }
            }
        }
    });

    // Atualiza os dados periodicamente
    setInterval(atualizarDados, 30000);
});