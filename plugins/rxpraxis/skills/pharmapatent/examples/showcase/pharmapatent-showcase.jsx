import React, { useState } from 'react';
import { 
  Briefcase, FileText, Code, Palette, Layers, TrendingUp, 
  Activity, Shield, FlaskConical, Scale, Globe, Cpu,
  ChevronRight, Search, Database, Users, BookOpen,
  BarChart3, PieChart, Map, GitBranch, Calendar, Target,
  CheckCircle2, AlertCircle, XCircle, ArrowRight, X
} from 'lucide-react';

// IBM Carbon renk tokenleri
const carbon = {
  bg: '#f4f4f4',           // Gray 10
  layer: '#ffffff',         // Layer 01
  textPrimary: '#161616',   // Gray 100
  textSecondary: '#525252', // Gray 70
  border: '#c6c6c6',        // Gray 30
  borderSubtle: '#e0e0e0',  // Gray 20
  blue: '#0f62fe',          // Blue 60 — interactive
  blueHover: '#0043ce',     // Blue 70
  purple: '#8a3ffc',        // Purple 60
  teal: '#007d79',          // Teal 60
  orange: '#ff832b',        // Orange 40
  red: '#da1e28',           // Red 60 — error
  green: '#24a148',         // Green 60 — success
  yellow: '#f1c21b',        // Yellow 30 — warning
};

// Skill ecosystem data
const ECOSYSTEM = {
  version: '1.6.0',
  releaseDate: '2026-04-24',
  modes: [
    { id: 1, name: 'FTO', fullName: 'Faaliyet Serbestisi Analizi', icon: Search, color: 'blue' },
    { id: 2, name: 'Invalidity', fullName: 'Hükümsüzlük Briefing', icon: Shield, color: 'red' },
    { id: 3, name: 'Landscape', fullName: 'Patent Peyzaj Raporu', icon: Map, color: 'teal' },
    { id: 4, name: 'Lifecycle', fullName: 'Yaşam Döngüsü Yönetimi', icon: TrendingUp, color: 'purple' },
    { id: 5, name: 'Regulatory', fullName: 'Pazara Giriş Takvimi', icon: Calendar, color: 'orange' },
    { id: 6, name: 'Litigation', fullName: 'Dava Briefing', icon: Scale, color: 'red' },
    { id: 7, name: 'Due Diligence', fullName: 'M&A Due Diligence', icon: Briefcase, color: 'blue' },
    { id: 8, name: 'Opposition', fullName: 'EPO Opposition', icon: AlertCircle, color: 'orange' },
    { id: 9, name: 'Biosimilar', fullName: 'Biyobenzer Yol', icon: GitBranch, color: 'teal' },
    { id: 10, name: 'Licensing', fullName: 'Lisans Müzakere', icon: FileText, color: 'purple' },
    { id: 11, name: 'Forecast', fullName: 'Landscape Forecast', icon: BarChart3, color: 'blue' },
    { id: 12, name: 'Expert Witness', fullName: 'FSHHM Bilirkişi Raporu', icon: Users, color: 'red' },
  ],
  domains: [
    { id: 'onkoloji', name: 'Onkoloji', ip: 'ICI, ADC, CAR-T, bispecific' },
    { id: 'hematoloji', name: 'Hematoloji', ip: 'CAR-T heme, bispecific, hemofili, SCD' },
    { id: 'immunoloji', name: 'İmmunoloji', ip: 'TNF-α, IL-17/23, JAK/TYK2, B-cell' },
    { id: 'noroloji', name: 'Nöroloji', ip: 'MS, Alzheimer, CGRP, gene therapy CNS' },
    { id: 'enfeksiyon', name: 'Enfeksiyon', ip: 'Antibiyotik, HIV, HCV, mRNA aşı' },
    { id: 'kardiyoloji', name: 'Kardiyoloji', ip: 'PCSK9, Factor XI, SGLT-2, Lp(a)' },
    { id: 'metabolik', name: 'Metabolik', ip: 'GLP-1, SGLT-2, obezite, MASH, KOAH' },
    { id: 'oftalmoloji', name: 'Oftalmoloji', ip: 'Anti-VEGF, gene therapy retinal, kuru göz' },
    { id: 'dermatoloji', name: 'Dermatoloji', ip: 'Psöriazis, AD, alopesi, vitiligo' },
  ],
  scripts: [
    { file: 'loe-calculator.py', desc: 'Loss of Exclusivity MAX formülü + TR 20 yıl patent + 6 yıl veri imtiyazı' },
    { file: 'claim-parser.py', desc: 'İstem yapı ayrıştırma — preamble, transition, body, özellik F1-Fn' },
    { file: 'royalty-calculator.py', desc: 'Royalty + NPV + IRR + Monte Carlo (10K simülasyon)' },
    { file: 'family-tracer.py', desc: 'INPADOC patent aile izleme + ülke coverage matrix' },
    { file: 'patent-expiry-monitor.py', desc: 'Patent expiry uyarısı — 12/24/36 ay ufuk' },
    { file: 'cpc-recommender.py', desc: 'CPC kod önerisi — hedef molekül + terapötik alan' },
    { file: 'priority-date-matrix.py', desc: 'Paris Convention + PCT priority date validasyonu' },
    { file: 'spc-calculator.py', desc: 'AB SPC hesaplayıcı — Reg. EC 469/2009 Art.13 + TR karşılaştırma' },
    { file: 'biosimilar-comparator.py', desc: 'CQA benzerlik skorlama — ICH Q5E + FDA/EMA guidance' },
    { file: 'report-builder.py', desc: 'Rapor iskeleti orkestratör — 11 rapor tipi + visualize + carbon-html' },
  ],
  references: [
    { file: 'fto-invalidity-protokol.md', weight: 12 },
    { file: 'ictihat-emsal.md', weight: 11 },
    { file: 'biyobenzer-yol.md', weight: 10 },
    { file: 'ruhsat-veri-imtiyazi.md', weight: 10 },
    { file: 'patent-degerleme.md', weight: 9 },
    { file: 'yeni-modaliteler.md', weight: 8 },
    { file: 'rapor-sablonlari.md', weight: 6 },
    { file: 'markush-analiz.md', weight: 5 },
    { file: 'tibbi-cihaz-uts.md', weight: 4 },
    { file: 'gorsel-standartlari.md', weight: 4 },
    { file: 'compliance-beyanlari.md', weight: 4 },
    { file: 'visualize-widget-kutuphanesi.md', weight: 3 },
  ],
  stats: {
    files: 42,
    references: 15,
    domains: 9,
    scripts: 10,
    modes: 12,
    reportTemplates: 10,
    filledExamples: 7,
    visualTemplates: 33,
    graphEdges: 145,
  },
};

// Main component
export default function PharmapatentShowcase() {
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedMode, setSelectedMode] = useState(null);
  const [selectedDomain, setSelectedDomain] = useState(null);

  const colorMap = {
    blue: { bg: '#edf5ff', border: carbon.blue, text: carbon.blue },
    red: { bg: '#fff1f1', border: carbon.red, text: carbon.red },
    teal: { bg: '#d9fbfb', border: carbon.teal, text: carbon.teal },
    purple: { bg: '#f6f2ff', border: carbon.purple, text: carbon.purple },
    orange: { bg: '#fff2e8', border: carbon.orange, text: '#8a3800' },
    green: { bg: '#defbe6', border: carbon.green, text: carbon.green },
  };

  return (
    <div style={{ 
      minHeight: '100vh', 
      backgroundColor: carbon.bg, 
      fontFamily: "'IBM Plex Sans', -apple-system, system-ui, sans-serif",
      color: carbon.textPrimary,
    }}>
      {/* Header */}
      <header style={{ 
        backgroundColor: carbon.textPrimary, 
        color: '#ffffff',
        padding: '20px 32px',
        borderBottom: `1px solid ${carbon.border}`,
      }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', maxWidth: '1400px', margin: '0 auto' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
            <FlaskConical size={28} style={{ color: carbon.blue }} />
            <div>
              <h1 style={{ fontSize: 22, fontWeight: 600, margin: 0, letterSpacing: '-0.02em' }}>
                pharmapatent
              </h1>
              <p style={{ fontSize: 12, margin: 0, color: '#a8a8a8', marginTop: 2 }}>
                Farmasötik Patent Uzmanlık Ekosistemi — v{ECOSYSTEM.version}
              </p>
            </div>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 24, fontSize: 12 }}>
            <div>
              <span style={{ color: '#a8a8a8' }}>Release: </span>
              <span style={{ fontFamily: "'IBM Plex Mono', monospace" }}>{ECOSYSTEM.releaseDate}</span>
            </div>
            <div style={{ 
              padding: '4px 10px', 
              backgroundColor: carbon.blue, 
              borderRadius: 0,
              fontSize: 11,
              fontWeight: 600,
              letterSpacing: '0.02em',
            }}>
              SMP v1.0 COMPLIANT
            </div>
          </div>
        </div>
      </header>

      {/* Tab Navigation */}
      <nav style={{ 
        backgroundColor: carbon.layer,
        borderBottom: `1px solid ${carbon.border}`,
        padding: '0 32px',
      }}>
        <div style={{ maxWidth: '1400px', margin: '0 auto', display: 'flex', gap: 0 }}>
          {[
            { id: 'overview', label: 'Genel Bakış', icon: Activity },
            { id: 'modes', label: 'Operasyonel Modlar', icon: Target },
            { id: 'domains', label: 'Terapötik Alanlar', icon: Layers },
            { id: 'scripts', label: 'Scriptler', icon: Code },
            { id: 'visuals', label: 'Görsel Kütüphane', icon: Palette },
            { id: 'graph', label: 'Bilgi Grafiği', icon: Database },
          ].map(tab => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                style={{
                  padding: '16px 20px',
                  border: 'none',
                  borderBottom: isActive ? `3px solid ${carbon.blue}` : '3px solid transparent',
                  backgroundColor: 'transparent',
                  color: isActive ? carbon.textPrimary : carbon.textSecondary,
                  fontSize: 14,
                  fontWeight: isActive ? 600 : 400,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8,
                  fontFamily: 'inherit',
                  transition: 'all 120ms',
                }}
              >
                <Icon size={16} />
                {tab.label}
              </button>
            );
          })}
        </div>
      </nav>

      {/* Main Content */}
      <main style={{ maxWidth: '1400px', margin: '0 auto', padding: '32px' }}>
        
        {/* OVERVIEW TAB */}
        {activeTab === 'overview' && (
          <div>
            <div style={{ marginBottom: 32 }}>
              <h2 style={{ fontSize: 32, fontWeight: 300, margin: '0 0 8px 0', letterSpacing: '-0.02em' }}>
                Türkiye + Global Farmasötik Patent Uzmanlığı
              </h2>
              <p style={{ fontSize: 16, color: carbon.textSecondary, margin: 0, maxWidth: 800, lineHeight: 1.5 }}>
                SMK 6769, TRIPS, Beşeri Tıbbi Ürünler Ruhsatlandırma Yönetmeliği, TİTCK, ÜTS/CE/ISO 13485, 
                Yargıtay 11. HD + FSHHM + EPO G-kararları ekseninde 12 operasyonel mod, 9 terapötik alan, 
                10 çalıştırılabilir Python script'i.
              </p>
            </div>

            {/* Stat cards */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 16, marginBottom: 32 }}>
              {[
                { label: 'Operasyonel Mod', value: ECOSYSTEM.stats.modes, icon: Target },
                { label: 'Terapötik Domain', value: ECOSYSTEM.stats.domains, icon: Layers },
                { label: 'Python Script', value: ECOSYSTEM.stats.scripts, icon: Code },
                { label: 'Rapor Şablonu', value: ECOSYSTEM.stats.reportTemplates, icon: FileText },
                { label: 'Görsel Şablonu', value: ECOSYSTEM.stats.visualTemplates, icon: Palette },
                { label: 'Filled Example', value: ECOSYSTEM.stats.filledExamples, icon: BookOpen },
                { label: 'Referans Protokol', value: ECOSYSTEM.stats.references, icon: Shield },
                { label: 'Graph Kenarı', value: ECOSYSTEM.stats.graphEdges, icon: GitBranch },
              ].map(stat => {
                const Icon = stat.icon;
                return (
                  <div key={stat.label} style={{ 
                    backgroundColor: carbon.layer, 
                    padding: 20,
                    border: `1px solid ${carbon.borderSubtle}`,
                    borderLeft: `4px solid ${carbon.blue}`,
                  }}>
                    <Icon size={20} style={{ color: carbon.blue, marginBottom: 8 }} />
                    <div style={{ fontSize: 28, fontWeight: 300, lineHeight: 1, letterSpacing: '-0.02em' }}>
                      {stat.value}
                    </div>
                    <div style={{ fontSize: 12, color: carbon.textSecondary, marginTop: 4 }}>
                      {stat.label}
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Architecture */}
            <div style={{ 
              backgroundColor: carbon.layer, 
              padding: 32,
              border: `1px solid ${carbon.borderSubtle}`,
            }}>
              <h3 style={{ fontSize: 18, fontWeight: 600, margin: '0 0 20px 0' }}>Ekosistem Mimarisi</h3>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16, fontSize: 12 }}>
                {[
                  { layer: 'L1 — Girdi', items: ['Hukuki vaka', 'Ürün spec', 'Patent aile', 'Klinik veri'], color: carbon.blue },
                  { layer: 'L2 — İşlem', items: ['12 Operasyonel mod', 'Script hesaplamaları', 'Prior art analizi', 'Finansal model'], color: carbon.purple },
                  { layer: 'L3 — Görsel', items: ['33 visualize şablon', 'IBM Carbon Design', 'Mermaid diyagram', 'SVG + HTML'], color: carbon.teal },
                  { layer: 'L4 — Çıktı', items: ['Markdown rapor', 'Carbon HTML', 'Carbon pptx deck', 'Compliance paket'], color: carbon.orange },
                ].map(l => (
                  <div key={l.layer} style={{ 
                    padding: 16, 
                    backgroundColor: carbon.bg,
                    borderTop: `3px solid ${l.color}`,
                  }}>
                    <div style={{ fontSize: 11, fontWeight: 600, color: l.color, marginBottom: 12, letterSpacing: '0.02em' }}>
                      {l.layer}
                    </div>
                    {l.items.map(i => (
                      <div key={i} style={{ padding: '4px 0', color: carbon.textPrimary }}>
                        {i}
                      </div>
                    ))}
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* MODES TAB */}
        {activeTab === 'modes' && (
          <div>
            <h2 style={{ fontSize: 28, fontWeight: 300, margin: '0 0 24px 0' }}>12 Operasyonel Mod</h2>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 12 }}>
              {ECOSYSTEM.modes.map(mode => {
                const Icon = mode.icon;
                const c = colorMap[mode.color];
                const isSelected = selectedMode?.id === mode.id;
                return (
                  <button
                    key={mode.id}
                    onClick={() => setSelectedMode(isSelected ? null : mode)}
                    style={{
                      textAlign: 'left',
                      padding: 20,
                      backgroundColor: isSelected ? c.bg : carbon.layer,
                      border: `1px solid ${isSelected ? c.border : carbon.borderSubtle}`,
                      borderLeft: `4px solid ${c.border}`,
                      cursor: 'pointer',
                      fontFamily: 'inherit',
                      transition: 'all 150ms',
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                        <Icon size={18} style={{ color: c.text }} />
                        <span style={{ fontSize: 11, fontFamily: "'IBM Plex Mono', monospace", color: carbon.textSecondary }}>
                          MOD {String(mode.id).padStart(2, '0')}
                        </span>
                      </div>
                      <ChevronRight size={14} style={{ color: carbon.textSecondary }} />
                    </div>
                    <div style={{ fontSize: 16, fontWeight: 600, marginBottom: 4 }}>
                      {mode.name}
                    </div>
                    <div style={{ fontSize: 12, color: carbon.textSecondary }}>
                      {mode.fullName}
                    </div>
                  </button>
                );
              })}
            </div>

            {/* Mode detail panel */}
            {selectedMode && (
              <div style={{ 
                marginTop: 24, 
                padding: 24, 
                backgroundColor: carbon.layer,
                border: `1px solid ${carbon.borderSubtle}`,
                borderLeft: `4px solid ${colorMap[selectedMode.color].border}`,
              }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
                  <h3 style={{ fontSize: 20, fontWeight: 600, margin: 0 }}>
                    {selectedMode.fullName}
                  </h3>
                  <button 
                    onClick={() => setSelectedMode(null)}
                    style={{ background: 'none', border: 'none', cursor: 'pointer', padding: 4 }}
                  >
                    <X size={18} style={{ color: carbon.textSecondary }} />
                  </button>
                </div>
                <p style={{ fontSize: 13, color: carbon.textSecondary, margin: '0 0 16px 0' }}>
                  Bu modun rapor iskeleti, zorunlu görsel şablonları ve ilgili scriptleri <code style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: 12, backgroundColor: carbon.bg, padding: '1px 6px' }}>report-builder.py --type {selectedMode.name.toLowerCase().replace(/ /g, '_')}</code> komutuyla üretilebilir.
                </p>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 16, fontSize: 12 }}>
                  <div>
                    <div style={{ fontSize: 11, fontWeight: 600, color: carbon.textSecondary, textTransform: 'uppercase', letterSpacing: '0.04em', marginBottom: 8 }}>
                      Bölüm Sayısı
                    </div>
                    <div style={{ fontSize: 24, fontWeight: 300 }}>
                      {[10, 10, 11, 11, 10, 10, 12, 11, 11, 10, 11, 12][selectedMode.id - 1]}
                    </div>
                  </div>
                  <div>
                    <div style={{ fontSize: 11, fontWeight: 600, color: carbon.textSecondary, textTransform: 'uppercase', letterSpacing: '0.04em', marginBottom: 8 }}>
                      Zorunlu Görsel
                    </div>
                    <div style={{ fontSize: 24, fontWeight: 300 }}>
                      {[4, 4, 4, 3, 2, 3, 4, 3, 4, 3, 4, 2][selectedMode.id - 1]}
                    </div>
                  </div>
                  <div>
                    <div style={{ fontSize: 11, fontWeight: 600, color: carbon.textSecondary, textTransform: 'uppercase', letterSpacing: '0.04em', marginBottom: 8 }}>
                      Hedef Kitle
                    </div>
                    <div style={{ fontSize: 14, marginTop: 4 }}>
                      {['Legal', 'Legal', 'Executive', 'Executive', 'Executive', 'Legal', 'Executive', 'Legal', 'Executive', 'Executive', 'Executive', 'Legal'][selectedMode.id - 1]}
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* DOMAINS TAB */}
        {activeTab === 'domains' && (
          <div>
            <h2 style={{ fontSize: 28, fontWeight: 300, margin: '0 0 24px 0' }}>9 Terapötik Alan Derinliği</h2>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 12 }}>
              {ECOSYSTEM.domains.map(domain => {
                const isSelected = selectedDomain?.id === domain.id;
                return (
                  <button
                    key={domain.id}
                    onClick={() => setSelectedDomain(isSelected ? null : domain)}
                    style={{
                      textAlign: 'left',
                      padding: 20,
                      backgroundColor: isSelected ? '#edf5ff' : carbon.layer,
                      border: `1px solid ${isSelected ? carbon.blue : carbon.borderSubtle}`,
                      cursor: 'pointer',
                      fontFamily: 'inherit',
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 12 }}>
                      <div style={{ 
                        width: 40, height: 40, 
                        backgroundColor: carbon.bg,
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        fontFamily: "'IBM Plex Mono', monospace",
                        fontSize: 11,
                        color: carbon.blue,
                      }}>
                        IP
                      </div>
                      <div style={{ flex: 1 }}>
                        <div style={{ fontSize: 16, fontWeight: 600 }}>{domain.name}</div>
                        <code style={{ fontSize: 10, fontFamily: "'IBM Plex Mono', monospace", color: carbon.textSecondary }}>
                          domains/{domain.id}-ip.md
                        </code>
                      </div>
                    </div>
                    <div style={{ fontSize: 12, color: carbon.textSecondary, lineHeight: 1.5 }}>
                      {domain.ip}
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
        )}

        {/* SCRIPTS TAB */}
        {activeTab === 'scripts' && (
          <div>
            <h2 style={{ fontSize: 28, fontWeight: 300, margin: '0 0 24px 0' }}>10 Çalıştırılabilir Python Script</h2>
            <div style={{ backgroundColor: carbon.layer, border: `1px solid ${carbon.borderSubtle}` }}>
              {ECOSYSTEM.scripts.map((script, idx) => (
                <div 
                  key={script.file} 
                  style={{ 
                    padding: 16, 
                    borderBottom: idx < ECOSYSTEM.scripts.length - 1 ? `1px solid ${carbon.borderSubtle}` : 'none',
                    display: 'grid',
                    gridTemplateColumns: '280px 1fr auto',
                    gap: 20,
                    alignItems: 'center',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                    <Code size={16} style={{ color: carbon.teal }} />
                    <code style={{ fontSize: 13, fontFamily: "'IBM Plex Mono', monospace", fontWeight: 500 }}>
                      {script.file}
                    </code>
                  </div>
                  <div style={{ fontSize: 13, color: carbon.textSecondary }}>
                    {script.desc}
                  </div>
                  <div style={{ 
                    fontSize: 10, 
                    fontFamily: "'IBM Plex Mono', monospace",
                    color: carbon.green,
                    backgroundColor: '#defbe6',
                    padding: '4px 8px',
                  }}>
                    --example
                  </div>
                </div>
              ))}
            </div>
            <div style={{ marginTop: 24, padding: 16, backgroundColor: '#edf5ff', borderLeft: `4px solid ${carbon.blue}` }}>
              <div style={{ fontSize: 12, color: carbon.textPrimary, lineHeight: 1.5 }}>
                Tüm script'ler <code style={{ fontFamily: "'IBM Plex Mono', monospace", backgroundColor: carbon.layer, padding: '1px 6px' }}>--example</code> flag'i ile 
                demo modunda çalışır. Production kullanım için <code style={{ fontFamily: "'IBM Plex Mono', monospace", backgroundColor: carbon.layer, padding: '1px 6px' }}>--import &lt;json-file&gt;</code> 
                ile JSON veri girişi veya interactive mode mevcuttur.
              </div>
            </div>
          </div>
        )}

        {/* VISUALS TAB */}
        {activeTab === 'visuals' && (
          <div>
            <h2 style={{ fontSize: 28, fontWeight: 300, margin: '0 0 24px 0' }}>33 Görsel Şablonu</h2>
            <p style={{ fontSize: 14, color: carbon.textSecondary, maxWidth: 800, marginBottom: 24 }}>
              IBM Carbon Design System renk paleti + IBM Plex typography uyumlu, tüm 10 rapor tipinin zorunlu görsellerini kapsayan SVG/Mermaid/HTML şablonları.
              Claude <code style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: 12, backgroundColor: carbon.bg, padding: '2px 6px' }}>visualize:show_widget</code> tool'u ile bu şablonları inline render eder.
            </p>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 8 }}>
              {[
                { cat: '§1 FTO', visuals: ['patent-country-heatmap', 'feature-matrix', 'design-around-tree', 'loe-gantt'], color: 'blue' },
                { cat: '§2 Invalidity', visuals: ['mosaic', 'radar', 'citation-network', 'forum-tree'], color: 'red' },
                { cat: '§3 Landscape', visuals: ['filing-trend', 'assignee-bar', 'geo-choropleth', 'evergreening-timeline'], color: 'teal' },
                { cat: '§4 Lifecycle', visuals: ['gantt', 'erosion', 'quadrant'], color: 'purple' },
                { cat: '§5 Launch', visuals: ['loe-gantt', 'max-formula'], color: 'orange' },
                { cat: '§6 Litigation', visuals: ['decision-tree', 'cost-curve', 'forum-matrix'], color: 'red' },
                { cat: '§7 DD', visuals: ['coverage', 'radar', 'montecarlo', 'tornado'], color: 'blue' },
                { cat: '§8 Opposition', visuals: ['art100-map', 'problem-solution', 'timeline'], color: 'orange' },
                { cat: '§9 Biosimilar', visuals: ['multi-gantt', 'sankey', 'market-share', 'launch-calendar'], color: 'teal' },
                { cat: '§10 Expert', visuals: ['feature-matrix', 'verdict-summary'], color: 'red' },
              ].map(section => {
                const c = colorMap[section.color];
                return (
                  <div key={section.cat} style={{
                    backgroundColor: carbon.layer,
                    border: `1px solid ${carbon.borderSubtle}`,
                    borderTop: `3px solid ${c.border}`,
                    padding: 16,
                  }}>
                    <div style={{ fontSize: 11, fontWeight: 600, color: c.text, marginBottom: 10, letterSpacing: '0.02em' }}>
                      {section.cat}
                    </div>
                    {section.visuals.map(v => (
                      <div key={v} style={{
                        fontSize: 10,
                        fontFamily: "'IBM Plex Mono', monospace",
                        padding: '4px 0',
                        color: carbon.textPrimary,
                      }}>
                        {v}
                      </div>
                    ))}
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* GRAPH TAB */}
        {activeTab === 'graph' && (
          <div>
            <h2 style={{ fontSize: 28, fontWeight: 300, margin: '0 0 24px 0' }}>Bilgi Grafı — Centrality</h2>
            <p style={{ fontSize: 14, color: carbon.textSecondary, maxWidth: 800, marginBottom: 24 }}>
              Referanslar + terapötik domain'ler arasındaki çapraz-atıf kenarları. In-degree centrality yüksek olan düğümler ekosistemin temel taşlarıdır.
            </p>
            
            <div style={{ backgroundColor: carbon.layer, border: `1px solid ${carbon.borderSubtle}`, padding: 24 }}>
              {ECOSYSTEM.references.map(ref => {
                const maxWeight = Math.max(...ECOSYSTEM.references.map(r => r.weight));
                const pct = (ref.weight / maxWeight) * 100;
                return (
                  <div key={ref.file} style={{ marginBottom: 12, display: 'grid', gridTemplateColumns: '340px 1fr 40px', gap: 16, alignItems: 'center' }}>
                    <code style={{ fontSize: 12, fontFamily: "'IBM Plex Mono', monospace" }}>
                      {ref.file}
                    </code>
                    <div style={{ 
                      height: 20, 
                      backgroundColor: carbon.bg,
                      position: 'relative',
                    }}>
                      <div style={{
                        height: '100%',
                        width: `${pct}%`,
                        backgroundColor: ref.weight >= 10 ? carbon.blue : ref.weight >= 7 ? carbon.purple : ref.weight >= 5 ? carbon.teal : carbon.textSecondary,
                        transition: 'width 400ms',
                      }} />
                    </div>
                    <div style={{ fontSize: 13, fontFamily: "'IBM Plex Mono', monospace", textAlign: 'right', fontWeight: 600 }}>
                      {ref.weight}
                    </div>
                  </div>
                );
              })}
            </div>

            <div style={{ marginTop: 24, display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16 }}>
              <div style={{ backgroundColor: carbon.layer, padding: 20, border: `1px solid ${carbon.borderSubtle}` }}>
                <div style={{ fontSize: 36, fontWeight: 300, color: carbon.blue, lineHeight: 1 }}>
                  {ECOSYSTEM.stats.graphEdges}
                </div>
                <div style={{ fontSize: 12, color: carbon.textSecondary, marginTop: 4 }}>
                  Toplam kenar
                </div>
              </div>
              <div style={{ backgroundColor: carbon.layer, padding: 20, border: `1px solid ${carbon.borderSubtle}` }}>
                <div style={{ fontSize: 36, fontWeight: 300, color: carbon.teal, lineHeight: 1 }}>
                  24
                </div>
                <div style={{ fontSize: 12, color: carbon.textSecondary, marginTop: 4 }}>
                  Düğüm (refs + domains)
                </div>
              </div>
              <div style={{ backgroundColor: carbon.layer, padding: 20, border: `1px solid ${carbon.borderSubtle}` }}>
                <div style={{ fontSize: 36, fontWeight: 300, color: carbon.purple, lineHeight: 1 }}>
                  {(ECOSYSTEM.stats.graphEdges / 24).toFixed(1)}
                </div>
                <div style={{ fontSize: 12, color: carbon.textSecondary, marginTop: 4 }}>
                  Ortalama out-degree
                </div>
              </div>
            </div>
          </div>
        )}

      </main>

      {/* Footer */}
      <footer style={{
        borderTop: `1px solid ${carbon.border}`,
        backgroundColor: carbon.layer,
        padding: '20px 32px',
        marginTop: 40,
      }}>
        <div style={{ maxWidth: '1400px', margin: '0 auto', display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: 12, color: carbon.textSecondary }}>
          <div>
            pharmapatent v{ECOSYSTEM.version} · SMP v1.0 compliant · IBM Carbon Design System
          </div>
          <div style={{ display: 'flex', gap: 16 }}>
            <code style={{ fontFamily: "'IBM Plex Mono', monospace" }}>smp-orchestrator</code>
            <code style={{ fontFamily: "'IBM Plex Mono', monospace" }}>carbon-html-report</code>
            <code style={{ fontFamily: "'IBM Plex Mono', monospace" }}>carbon-pptx</code>
            <code style={{ fontFamily: "'IBM Plex Mono', monospace" }}>lex-mercator</code>
          </div>
        </div>
      </footer>
    </div>
  );
}
