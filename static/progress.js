// static/js/progress.js

function initializeChart(quizHistory) {
    if (!quizHistory || quizHistory.length === 0) {
        document.getElementById('quizChart').style.display = 'none';
        return;
    }
    
    const ctx = document.getElementById('quizChart').getContext('2d');
    
    // Prepare data for chart
    const labels = quizHistory.map(quiz => quiz.date);
    const scores = quizHistory.map(quiz => quiz.score);
    const difficulties = quizHistory.map(quiz => quiz.difficulty);
    
    // Define colors by difficulty
    const colors = difficulties.map(difficulty => {
        switch(difficulty) {
            case 'easy': return 'rgba(75, 192, 192, 0.7)';
            case 'medium': return 'rgba(54, 162, 235, 0.7)';
            case 'hard': return 'rgba(153, 102, 255, 0.7)';
            default: return 'rgba(75, 192, 192, 0.7)';
        }
    });
    
    // Create chart
    const chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Quiz Scores (%)',
                data: scores,
                backgroundColor: colors,
                borderColor: colors.map(color => color.replace('0.7', '1')),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    title: {
                        display: true,
                        text: 'Score (%)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Quiz Date'
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        afterLabel: function(context) {
                            return 'Difficulty: ' + difficulties[context.dataIndex];
                        }
                    }
                },
                legend: {
                    display: false
                }
            }
        }
    });
}

document.addEventListener('DOMContentLoaded', function() {
    // Initialize a legend for difficulty colors
    const legendContainer = document.createElement('div');
    legendContainer.className = 'chart-legend';
    
    const difficulties = ['easy', 'medium', 'hard'];
    const colors = [
        'rgba(75, 192, 192, 0.7)',
        'rgba(54, 162, 235, 0.7)',
        'rgba(153, 102, 255, 0.7)'
    ];
    
    difficulties.forEach((difficulty, index) => {
        const legendItem = document.createElement('div');
        legendItem.className = 'legend-item';
        
        const colorBox = document.createElement('div');
        colorBox.className = 'legend-color';
        colorBox.style.backgroundColor = colors[index];
        
        const label = document.createElement('span');
        label.textContent = difficulty.charAt(0).toUpperCase() + difficulty.slice(1);
        
        legendItem.appendChild(colorBox);
        legendItem.appendChild(label);
        legendContainer.appendChild(legendItem);
    });
    
    // Add legend to the page
    const chartContainer = document.querySelector('.chart-container');
    if (chartContainer) {
        chartContainer.appendChild(legendContainer);
    }
});