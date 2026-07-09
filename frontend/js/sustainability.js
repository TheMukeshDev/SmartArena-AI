document.addEventListener('DOMContentLoaded', () => {
    // Chart.js Configuration
    Chart.defaults.color = '#94a3b8'; // text-surface-400
    Chart.defaults.font.family = 'Inter, sans-serif';
    Chart.defaults.borderColor = 'rgba(255, 255, 255, 0.05)';

    const commonOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { display: false }
        },
        scales: {
            y: { beginAtZero: true }
        }
    };

    // Simulated Metrics Data
    const currentMetrics = {
        energy_kwh: [420, 480, 510, 600, 650, 720, 680],
        water_liters: [1200, 1350, 1500, 1900, 2200, 2400, 2100],
        waste_kg: [50, 65, 80, 120, 150, 180, 160]
    };

    const labels = ['12 PM', '1 PM', '2 PM', '3 PM', '4 PM', '5 PM', '6 PM'];

    // 1. Energy Chart
    const ctxEnergy = document.getElementById('energyChart').getContext('2d');
    new Chart(ctxEnergy, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Energy (kWh)',
                data: currentMetrics.energy_kwh,
                borderColor: '#eab308', // arena-400
                backgroundColor: 'rgba(234, 179, 8, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4
            }]
        },
        options: commonOptions
    });

    // 2. Water Chart
    const ctxWater = document.getElementById('waterChart').getContext('2d');
    new Chart(ctxWater, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Water (Liters)',
                data: currentMetrics.water_liters,
                backgroundColor: '#3b82f6', // neon-blue
                borderRadius: 4
            }]
        },
        options: commonOptions
    });

    // 3. Waste Chart
    const ctxWaste = document.getElementById('wasteChart').getContext('2d');
    new Chart(ctxWaste, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Waste Diverted (kg)',
                data: currentMetrics.waste_kg,
                borderColor: '#00ff88', // neon-green
                borderWidth: 2,
                borderDash: [5, 5],
                tension: 0.1
            }]
        },
        options: commonOptions
    });

    // Phase 8: AI Optimization Logic
    const optBtn = document.getElementById('ai-optimize-btn');
    const ecoPanel = document.getElementById('ai-eco-panel');
    const ecoStatus = document.getElementById('ai-eco-status');
    const ecoRecs = document.getElementById('ai-eco-recs');

    if (optBtn) {
        optBtn.addEventListener('click', async () => {
            optBtn.disabled = true;
            optBtn.textContent = '🌱 Optimizing...';
            ecoPanel.classList.add('hidden');

            try {
                // Send current totals to AI
                const reqData = {
                    metrics: {
                        current_energy: currentMetrics.energy_kwh[6],
                        current_water: currentMetrics.water_liters[6],
                        current_waste: currentMetrics.waste_kg[6]
                    }
                };

                const res = await fetch(CONFIG.apiUrl("/ai/sustainability/optimize"), {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(reqData),
                    credentials: "include"
                });
                
                const data = await res.json();
                if (res.ok) {
                    const result = data.data;
                    ecoStatus.textContent = result.status;
                    
                    ecoRecs.innerHTML = '';
                    result.recommendations.forEach(rec => {
                        const li = document.createElement('li');
                        li.textContent = rec;
                        ecoRecs.appendChild(li);
                    });
                    
                    ecoPanel.classList.remove('hidden');
                } else {
                    alert("Optimization failed.");
                }
            } catch (err) {
                console.error(err);
                alert("Error contacting AI service.");
            } finally {
                optBtn.disabled = false;
                optBtn.textContent = '🌱 Run AI Eco-Optimizer';
            }
        });
    }
});
