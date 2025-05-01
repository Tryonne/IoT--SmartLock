// analytics.js
// ------------------------------ //
// Função para atualizar os dados das métricas e gráficos
function atualizarDados() {
    fetch('/analytics/dados')
        .then(response => response.json())
        .then(data => {
            // Atualiza as métricas principais
            document.getElementById('totalAcessos').textContent = data.total_acessos;
            document.getElementById('taxaSucesso').textContent = data.taxa_sucesso + '%';
            document.getElementById('horarioPico').textContent = data.horario_pico;
            document.getElementById('tentativasNegadas').textContent = data.tentativas_negadas;

            // Atualiza o gráfico de linha
            console.log(data.dias, data.acessos_por_dia)
            window.lineChart.data.labels.length = 0;
            window.lineChart.data.labels.push(...data.dias);
            window.lineChart.data.datasets[0].data.length = 0;
            window.lineChart.data.datasets[0].data.push(...data.acessos_por_dia);
            window.lineChart.update();

            // Atualiza o gráfico de pizza
            window.pieChart.data.datasets[0].data = data.tipos_acesso;
            window.pieChart.update();

            // Atualiza a tabela de últimos acessos
            const tbody = document.getElementById('tabelaUltimosAcessos');
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
    window.lineChart = new Chart(ctxLine, window.lineChartConfig);

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
    setInterval(atualizarDados, 10000); // 10 segundos
    atualizarDados(); // Atualiza logo ao carregar a página
});