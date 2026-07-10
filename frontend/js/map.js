/**
 * SmartArena AI — Map Interactivity Logic
 */

document.addEventListener('DOMContentLoaded', () => {
    const zones = document.querySelectorAll('path[data-zone]');
    
    // Panel Elements
    const emptyState = document.getElementById('zone-info-empty');
    const infoCard = document.getElementById('zone-info-card');
    const zoneNameEl = document.getElementById('panel-zone-name');
    const statusIndEl = document.getElementById('panel-status-indicator');
    const statusTextEl = document.getElementById('panel-status-text');
    const occupancyEl = document.getElementById('panel-occupancy');
    const headcountEl = document.getElementById('panel-headcount');
    const capacityEl = document.getElementById('panel-capacity');
    const progressEl = document.getElementById('panel-progress-bar');
    const insightEl = document.getElementById('panel-ai-insight');

    // Fake simulation data generator
    const generateSimData = (zoneName) => {
        const capacity = zoneName === 'North Stand' || zoneName === 'South Stand' ? 15000 : 10000;
        const occupancyPct = Math.floor(Math.random() * 80) + 15; // 15% to 95%
        const headcount = Math.floor(capacity * (occupancyPct / 100));
        
        let status = 'Optimal';
        let color = '#00ff88'; // neon-green
        let aiInsight = 'Crowd flow is stable. All concession stands operating normally.';
        let tailwindColor = 'bg-neon-green text-neon-green';

        if (occupancyPct >= 90) {
            status = 'Critical';
            color = '#ef4444'; // red-500
            aiInsight = 'Zone at max capacity! Redirecting incoming fans to alternative entrances. Dispatching extra security.';
            tailwindColor = 'bg-red-500 text-red-500';
        } else if (occupancyPct >= 75) {
            status = 'Congested';
            color = '#ff6b2b'; // neon-orange
            aiInsight = 'High density detected. Wait times for restrooms are exceeding 10 minutes.';
            tailwindColor = 'bg-neon-orange text-neon-orange';
        } else if (occupancyPct >= 50) {
            status = 'Moderate';
            color = '#eab308'; // yellow-500
            aiInsight = 'Filling up steadily. Pre-order kiosks seeing increased traffic.';
            tailwindColor = 'bg-yellow-500 text-yellow-500';
        }

        return { capacity, occupancyPct, headcount, status, color, aiInsight, tailwindColor };
    };

    // Live Map Simulation Interval
    setInterval(() => {
        zones.forEach(zone => {
            const data = generateSimData(zone.dataset.zone);
            // Add a slight transparency to the hex color for the SVG fill
            zone.setAttribute('fill', data.color + '80'); 
            zone.dataset.currentData = JSON.stringify(data);
        });
    }, 5000); // Update every 5 seconds

    // Select a zone and update panel
    const selectZone = (zone) => {
        const data = JSON.parse(zone.dataset.currentData);
        
        // UI Updates
        emptyState.classList.add('hidden');
        infoCard.classList.remove('hidden');
        
        zoneNameEl.textContent = zone.dataset.zone;
        occupancyEl.textContent = `${data.occupancyPct}%`;
        occupancyEl.setAttribute('aria-label', `Occupancy ${data.occupancyPct} percent`);
        headcountEl.textContent = data.headcount.toLocaleString();
        headcountEl.setAttribute('aria-label', `Headcount ${data.headcount.toLocaleString()}`);
        capacityEl.textContent = data.capacity.toLocaleString();
        progressEl.style.width = `${data.occupancyPct}%`;
        progressEl.setAttribute('aria-valuenow', data.occupancyPct);
        insightEl.textContent = data.aiInsight;
        
        // Status Updates
        statusTextEl.textContent = data.status;
        
        // Reset classes
        statusIndEl.className = 'w-2 h-2 rounded-full animate-pulse ' + data.tailwindColor.split(' ')[0];
        statusTextEl.className = 'text-sm font-medium ' + data.tailwindColor.split(' ')[1];
        progressEl.className = 'h-full rounded-full transition-all duration-500 ' + data.tailwindColor.split(' ')[0];
        
        // Highlight selected zone and update ARIA
        zones.forEach(z => {
            z.setAttribute('stroke-width', '2');
            z.setAttribute('aria-selected', 'false');
        });
        zone.setAttribute('stroke-width', '4');
        zone.setAttribute('stroke', '#ffffff');
        zone.setAttribute('aria-selected', 'true');
    };

    // Click and keyboard handler for zones
    zones.forEach(zone => {
        // Initialize with data
        zone.dataset.currentData = JSON.stringify(generateSimData(zone.dataset.zone));
        zone.setAttribute('aria-selected', 'false');

        zone.addEventListener('click', () => selectZone(zone));
        zone.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                selectZone(zone);
            }
        });
    });

    // Phase 5: AI Crowd Analysis
    const analyzeBtn = document.getElementById('ai-analyze-btn');
    const insightsBanner = document.getElementById('ai-global-insights');
    const globalStatus = document.getElementById('ai-global-status');
    const insightsList = document.getElementById('ai-insights-list');
    const routingAdvice = document.getElementById('ai-routing-advice');

    if(analyzeBtn) {
        analyzeBtn.addEventListener('click', async () => {
            analyzeBtn.disabled = true;
            analyzeBtn.innerHTML = '<span aria-hidden="true">🧠</span> Analyzing...';
            analyzeBtn.setAttribute('aria-busy', 'true');
            insightsBanner.classList.add('hidden');

            // Gather current zone data
            const zonesData = Array.from(zones).map(z => {
                const d = JSON.parse(z.dataset.currentData);
                return {
                    zone: z.dataset.zone,
                    occupancy: d.occupancyPct,
                    headcount: d.headcount
                };
            });

            try {
                const res = await fetch(CONFIG.apiUrl("/ai/crowd/analyze"), {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ zones: zonesData }),
                    credentials: "include"
                });
                
                const data = await res.json();
                if (res.ok) {
                    const analysis = data.data;
                    globalStatus.textContent = analysis.global_status;
                    
                    insightsList.innerHTML = '';
                    analysis.insights.forEach(insight => {
                        const li = document.createElement('li');
                        li.textContent = insight;
                        insightsList.appendChild(li);
                    });
                    
                    routingAdvice.textContent = "Routing Advice: " + analysis.routing_advice;
                    insightsBanner.classList.remove('hidden');
                } else {
                    alert("AI failed to analyze crowd data.");
                }
            } catch (err) {
                console.error(err);
                alert("Error contacting AI service.");
            } finally {
                analyzeBtn.disabled = false;
                analyzeBtn.innerHTML = '<span aria-hidden="true">🧠</span> Run AI Crowd Analysis';
                analyzeBtn.removeAttribute('aria-busy');
            }
        });
    }
});
