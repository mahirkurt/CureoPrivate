# examples/showcase/monte-carlo-widget.md — Monte Carlo NPV Simulator Widget

Bu dokuman, pharmapatent skill ekosistemine eklenmiş ikinci showcase artifact'i tanımlar: **Monte Carlo NPV Simulator**. `royalty-calculator.py --montecarlo` modunu web tarayıcısında etkileşimli olarak simüle eder.

## Kullanım Senaryosu

Mod 7 (DD) + Mod 10 (Licensing) raporları hazırlanırken, müvekkil + BD ekibi + yönetici ile canlı NPV dağılımı tartışılırken kullanılır. Parametreler değiştirildikçe dağılım güncellenir — slider'lar ile peak sales, PTRS, discount rate, launch gecikme, patent challenge olasılığı canlı değiştirilir.

## Çağrı akışı

Claude, bir M&A veya licensing raporu yazarken bu widget'ı aşağıdaki gibi çağırır:

```
1. visualize:read_me(modules=["interactive"])
2. Aşağıdaki HTML kodunu doldur (parametrelerle)
3. visualize:show_widget(title=..., widget_code=HTML, loading_messages=...)
```

## HTML Widget Kodu

```html
<style>
.mc-row { display: flex; align-items: center; gap: 12px; margin: 0 0 12px; }
.mc-row label { font-size: 13px; color: var(--color-text-secondary); min-width: 140px; }
.mc-row input[type=range] { flex: 1; }
.mc-row .val { font-family: var(--font-mono); font-size: 13px; font-weight: 500; min-width: 60px; text-align: right; }
.mc-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 1rem; }
.mc-stat { background: var(--color-background-secondary); border-radius: var(--border-radius-md); padding: 12px; }
.mc-stat-label { font-size: 12px; color: var(--color-text-secondary); margin-bottom: 4px; }
.mc-stat-value { font-size: 20px; font-weight: 500; font-family: var(--font-mono); }
.mc-chart { height: 240px; background: var(--color-background-secondary); border-radius: var(--border-radius-md); margin-bottom: 1rem; position: relative; }
</style>

<div style="padding: 1rem 0;">
  <h2 class="sr-only">Monte Carlo NPV Simulator for M&A due diligence</h2>
  
  <div style="display: flex; align-items: baseline; gap: 8px; margin-bottom: 1rem;">
    <h2 style="margin: 0; font-size: 18px; font-weight: 500;">Monte Carlo NPV Simulator</h2>
    <span style="font-size: 12px; color: var(--color-text-secondary);">10,000 simülasyon</span>
  </div>
  
  <div class="mc-row">
    <label>Peak sales ($M)</label>
    <input type="range" id="mc-peak" min="500" max="5000" value="2000" step="50" />
    <span class="val" id="mc-peak-val">$2,000M</span>
  </div>
  <div class="mc-row">
    <label>Faz II PTRS (%)</label>
    <input type="range" id="mc-ptrs2" min="20" max="90" value="65" step="1" />
    <span class="val" id="mc-ptrs2-val">65%</span>
  </div>
  <div class="mc-row">
    <label>Faz III PTRS (%)</label>
    <input type="range" id="mc-ptrs3" min="30" max="95" value="70" step="1" />
    <span class="val" id="mc-ptrs3-val">70%</span>
  </div>
  <div class="mc-row">
    <label>Discount rate (%)</label>
    <input type="range" id="mc-discount" min="8" max="20" value="12" step="1" />
    <span class="val" id="mc-discount-val">12%</span>
  </div>
  <div class="mc-row">
    <label>Launch gecikme (yıl)</label>
    <input type="range" id="mc-delay" min="0" max="4" value="1" step="1" />
    <span class="val" id="mc-delay-val">1 yıl</span>
  </div>
  <div class="mc-row">
    <label>Patent challenge (%)</label>
    <input type="range" id="mc-patent" min="0" max="50" value="20" step="1" />
    <span class="val" id="mc-patent-val">20%</span>
  </div>
  
  <div class="mc-grid">
    <div class="mc-stat">
      <div class="mc-stat-label">P10 (worst 10%)</div>
      <div class="mc-stat-value" id="mc-p10" style="color: var(--color-text-danger);">-$80M</div>
    </div>
    <div class="mc-stat">
      <div class="mc-stat-label">P50 (median)</div>
      <div class="mc-stat-value" id="mc-p50" style="color: var(--color-text-info);">$450M</div>
    </div>
    <div class="mc-stat">
      <div class="mc-stat-label">P90 (best 10%)</div>
      <div class="mc-stat-value" id="mc-p90" style="color: var(--color-text-success);">$1,050M</div>
    </div>
  </div>
  
  <div class="mc-chart">
    <canvas id="mc-canvas" style="width: 100%; height: 100%;"></canvas>
  </div>
  
  <div style="font-size: 12px; color: var(--color-text-secondary); text-align: center;">
    Pozitif NPV: <span id="mc-positive-pct">82%</span> · 
    Beklenen NPV: <span id="mc-expected">$420M</span>
  </div>
</div>

<script>
(function() {
  const canvas = document.getElementById('mc-canvas');
  const ctx = canvas.getContext('2d');
  
  function resizeCanvas() {
    const rect = canvas.parentElement.getBoundingClientRect();
    canvas.width = rect.width * 2;
    canvas.height = rect.height * 2;
    canvas.style.width = rect.width + 'px';
    canvas.style.height = rect.height + 'px';
    ctx.scale(2, 2);
  }
  resizeCanvas();
  window.addEventListener('resize', resizeCanvas);
  
  function randomNormal(mean, std) {
    const u1 = Math.random();
    const u2 = Math.random();
    return mean + std * Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2);
  }
  
  function runSimulation(peak, ptrs2, ptrs3, discount, delay, patentChallenge) {
    const N = 10000;
    const results = [];
    
    for (let i = 0; i < N; i++) {
      // Peak sales: log-normal
      const peakSim = Math.max(0, randomNormal(peak, peak * 0.3));
      
      // PTRS gates
      const phase2Pass = Math.random() < (ptrs2 / 100);
      const phase3Pass = phase2Pass && Math.random() < (ptrs3 / 100);
      
      // Patent challenge
      const patentLost = Math.random() < (patentChallenge / 100);
      
      // Launch delay (triangular 0-delay)
      const launchDelay = delay * Math.random();
      
      let npv = 0;
      if (phase3Pass && !patentLost) {
        // Revenue over 10 years after launch (year 5 + delay)
        const peakYear = 5 + launchDelay + 5;
        for (let y = 5 + launchDelay; y <= 20; y++) {
          let revYear = 0;
          if (y < peakYear) {
            revYear = peakSim * (y - (5 + launchDelay)) / 5;
          } else if (y < peakYear + 5) {
            revYear = peakSim;
          } else {
            revYear = peakSim * Math.max(0, 1 - (y - peakYear - 5) * 0.15);
          }
          npv += revYear / Math.pow(1 + discount / 100, y);
        }
        // Costs
        npv -= 400; // Upfront + dev costs
      } else if (phase2Pass) {
        // Phase II pass but Phase III fail
        npv = -250;
      } else {
        // Phase II fail
        npv = -120;
      }
      
      results.push(npv);
    }
    
    results.sort((a, b) => a - b);
    return results;
  }
  
  function percentile(arr, p) {
    const idx = Math.floor(arr.length * p);
    return arr[idx];
  }
  
  function update() {
    const peak = Number(document.getElementById('mc-peak').value);
    const ptrs2 = Number(document.getElementById('mc-ptrs2').value);
    const ptrs3 = Number(document.getElementById('mc-ptrs3').value);
    const discount = Number(document.getElementById('mc-discount').value);
    const delay = Number(document.getElementById('mc-delay').value);
    const patentChallenge = Number(document.getElementById('mc-patent').value);
    
    // Update labels
    document.getElementById('mc-peak-val').textContent = '$' + peak.toLocaleString() + 'M';
    document.getElementById('mc-ptrs2-val').textContent = ptrs2 + '%';
    document.getElementById('mc-ptrs3-val').textContent = ptrs3 + '%';
    document.getElementById('mc-discount-val').textContent = discount + '%';
    document.getElementById('mc-delay-val').textContent = delay + ' yıl';
    document.getElementById('mc-patent-val').textContent = patentChallenge + '%';
    
    // Simulate
    const results = runSimulation(peak, ptrs2, ptrs3, discount, delay, patentChallenge);
    const p10 = percentile(results, 0.10);
    const p50 = percentile(results, 0.50);
    const p90 = percentile(results, 0.90);
    const expected = results.reduce((a, b) => a + b, 0) / results.length;
    const positive = results.filter(x => x > 0).length / results.length;
    
    document.getElementById('mc-p10').textContent = formatMoney(p10);
    document.getElementById('mc-p50').textContent = formatMoney(p50);
    document.getElementById('mc-p90').textContent = formatMoney(p90);
    document.getElementById('mc-expected').textContent = formatMoney(expected);
    document.getElementById('mc-positive-pct').textContent = Math.round(positive * 100) + '%';
    
    drawHistogram(results);
  }
  
  function formatMoney(v) {
    if (v < 0) return '-$' + Math.round(Math.abs(v)) + 'M';
    return '$' + Math.round(v) + 'M';
  }
  
  function drawHistogram(results) {
    const rect = canvas.parentElement.getBoundingClientRect();
    const W = rect.width;
    const H = rect.height;
    
    ctx.clearRect(0, 0, W, H);
    
    // Histogram bins
    const nBins = 40;
    const minVal = results[0];
    const maxVal = results[results.length - 1];
    const binWidth = (maxVal - minVal) / nBins;
    const bins = new Array(nBins).fill(0);
    
    results.forEach(v => {
      const idx = Math.min(nBins - 1, Math.floor((v - minVal) / binWidth));
      if (idx >= 0) bins[idx]++;
    });
    
    const maxCount = Math.max(...bins);
    const barW = (W - 40) / nBins;
    const chartH = H - 30;
    
    // Zero line
    const zeroX = 20 + ((-minVal) / (maxVal - minVal)) * (W - 40);
    ctx.strokeStyle = 'rgba(100,100,100,0.3)';
    ctx.setLineDash([4, 4]);
    ctx.beginPath();
    ctx.moveTo(zeroX, 10);
    ctx.lineTo(zeroX, H - 20);
    ctx.stroke();
    ctx.setLineDash([]);
    
    // Bars
    for (let i = 0; i < nBins; i++) {
      const binCenter = minVal + (i + 0.5) * binWidth;
      const barH = (bins[i] / maxCount) * chartH;
      const x = 20 + i * barW;
      const y = H - 20 - barH;
      
      // Color: red for negative, blue for positive
      ctx.fillStyle = binCenter < 0 ? 'rgba(218,30,40,0.75)' : 'rgba(15,98,254,0.75)';
      ctx.fillRect(x + 1, y, barW - 2, barH);
    }
    
    // X-axis labels
    ctx.fillStyle = 'rgba(100,100,100,1)';
    ctx.font = '10px sans-serif';
    ctx.textAlign = 'left';
    ctx.fillText(formatMoney(minVal), 20, H - 5);
    ctx.textAlign = 'center';
    ctx.fillText('0', zeroX, H - 5);
    ctx.textAlign = 'right';
    ctx.fillText(formatMoney(maxVal), W - 20, H - 5);
  }
  
  // Attach listeners
  ['mc-peak', 'mc-ptrs2', 'mc-ptrs3', 'mc-discount', 'mc-delay', 'mc-patent'].forEach(id => {
    document.getElementById(id).addEventListener('input', update);
  });
  
  // Initial
  setTimeout(update, 100);
})();
</script>
```

## Parametreler

| Parametre | Aralık | Default | Etki |
|---|---|---|---|
| Peak sales | $500M-$5B | $2B | Maksimum yıllık satış potansiyeli |
| Faz II PTRS | 20-90% | 65% | Faz II başarı olasılığı |
| Faz III PTRS | 30-95% | 70% | Faz III başarı olasılığı (conditional) |
| Discount rate | 8-20% | 12% | NPV hesabı için |
| Launch gecikme | 0-4 yıl | 1 yıl | Maksimum gecikme; triangular dağılım |
| Patent challenge | 0-50% | 20% | Temel patentin kaybedilmesi olasılığı |

## Sonuç metrikleri

- **P10** (worst case): 10. persentil NPV
- **P50** (median): 50. persentil NPV  
- **P90** (best case): 90. persentil NPV
- **Pozitif NPV %**: NPV > 0 olan simülasyon yüzdesi
- **Expected NPV**: Ortalama NPV

## Histogram

- Kırmızı barlar: negatif NPV simülasyonları
- Mavi barlar: pozitif NPV simülasyonları
- Sıfır dikey çizgi ile işaretli
