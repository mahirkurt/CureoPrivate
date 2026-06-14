// artifacts/skill-showcase.jsx
// pharmapatent v1.6.0 — Interactive Ekosistem Showcase
// Usage: paste into any React environment with Tailwind CSS
// Tested: claude.ai artifacts, CodeSandbox, Vite + React 18

import React, { useState } from "react";

const MODES = [
  { id: 1, name: "FTO Analizi", short: "FTO", type: "fto", audience: "Legal",
    desc: "Faaliyet Serbestisi tarama — patent × ülke × istem matrisi", visuals: ["fto-patent-country-heatmap", "fto-feature-matrix", "fto-design-around-tree", "fto-loe-gantt"],
    scripts: ["loe-calculator.py", "claim-parser.py", "family-tracer.py"], example: "fto-ornek-atorvastatin.md" },
  { id: 2, name: "Invalidity Briefing", short: "INV", type: "invalidity", audience: "Legal",
    desc: "Prior art mozaik + buluş basamağı + forum seçimi", visuals: ["invalidity-mosaic", "invalidity-radar", "invalidity-citation-network", "invalidity-forum-tree"],
    scripts: ["claim-parser.py", "priority-date-matrix.py"], example: "invalidity-ornek-trastuzumab.md" },
  { id: 3, name: "Landscape Raporu", short: "LND", type: "landscape", audience: "Executive",
    desc: "Teknoloji peyzajı — trend + assignee + white space", visuals: ["landscape-filing-trend", "landscape-assignee-bar", "landscape-geo-choropleth", "landscape-evergreening-timeline"],
    scripts: ["cpc-recommender.py", "family-tracer.py"], example: "landscape-ornek-adc-2030.md" },
  { id: 4, name: "Lifecycle Yol Haritası", short: "LCM", type: "lifecycle", audience: "Executive",
    desc: "LOE sonrası pazar savunma + genişleme stratejisi", visuals: ["lifecycle-gantt", "lifecycle-erosion", "lifecycle-quadrant"],
    scripts: ["loe-calculator.py", "royalty-calculator.py"], example: null },
  { id: 5, name: "Pazara Giriş Takvimi", short: "REG", type: "regulatory", audience: "Executive",
    desc: "MAX formülü — patent + veri imtiyazı + Bolar + SGK", visuals: ["fto-loe-gantt", "launch-max-formula"],
    scripts: ["loe-calculator.py", "spc-calculator.py"], example: "regulatory-ornek-semaglutide.md" },
  { id: 6, name: "Litigation Briefing", short: "LIT", type: "litigation", audience: "Legal",
    desc: "FSHHM dava stratejisi — ihtiyati tedbir + tazminat", visuals: ["litigation-decision-tree", "litigation-cost-curve", "litigation-forum-matrix"],
    scripts: ["royalty-calculator.py"], example: null },
  { id: 7, name: "Due Diligence (M&A)", short: "DD", type: "dd", audience: "Executive",
    desc: "Akuistisyon DD — IP + klinik + finansal + Monte Carlo", visuals: ["fto-patent-country-heatmap", "dd-radar", "dd-montecarlo", "dd-tornado"],
    scripts: ["royalty-calculator.py", "family-tracer.py", "priority-date-matrix.py"], example: "ddreport-ornek-ma.md" },
  { id: 8, name: "EPO Opposition", short: "OPP", type: "opposition", audience: "Legal",
    desc: "9 aylık opposition — EPC Art.100 gerekçe haritası", visuals: ["opposition-art100-map", "opposition-problem-solution", "opposition-timeline"],
    scripts: ["claim-parser.py", "priority-date-matrix.py"], example: "opposition-ornek-epo.md" },
  { id: 9, name: "Biosimilar Pathway", short: "BIO", type: "biosimilar", audience: "Executive",
    desc: "CQA comparability + klinik + 3-jurisdiksiyon launch", visuals: ["biosimilar-multi-gantt", "biosimilar-sankey", "biosimilar-market-share", "biosimilar-launch-calendar"],
    scripts: ["loe-calculator.py", "biosimilar-comparator.py"], example: null },
  { id: 10, name: "License Negotiation", short: "LIC", type: "licensing", audience: "Executive",
    desc: "Deal yapısı — upfront + milestones + royalty + BATNA", visuals: ["lifecycle-gantt", "dd-montecarlo", "dd-tornado"],
    scripts: ["royalty-calculator.py"], example: "licensing-ornek-adc.md" },
  { id: 11, name: "Landscape Forecast", short: "FCT", type: "landscape", audience: "Executive",
    desc: "BERT-tabanlı 5 yıllık teknoloji öngörüsü", visuals: ["landscape-filing-trend", "landscape-evergreening-timeline"],
    scripts: ["cpc-recommender.py"], example: "landscape-ornek-adc-2030.md" },
  { id: 12, name: "Expert Witness (FSHHM)", short: "EXP", type: "expert_witness", audience: "Legal",
    desc: "HMK m.266 bilirkişi raporu + bağımsızlık beyanı", visuals: ["fto-feature-matrix", "expert-verdict-summary"],
    scripts: ["claim-parser.py"], example: null },
];

const DOMAINS = [
  { name: "Onkoloji", file: "onkoloji-ip.md", topics: "ICI, ADC, CAR-T, bispecific, TKI" },
  { name: "Hematoloji", file: "hematoloji-ip.md", topics: "CAR-T heme, glofitamab, Roche, hemofili" },
  { name: "İmmunoloji", file: "immunoloji-ip.md", topics: "TNF-α, IL-17/23, JAK, TYK2, Dupixent" },
  { name: "Nöroloji", file: "noroloji-ip.md", topics: "MS, Alzheimer, CGRP, SMA, ALS" },
  { name: "Enfeksiyon", file: "enfeksiyon-ip.md", topics: "HIV, HCV, antibiyotik, mRNA aşı" },
  { name: "Kardiyoloji", file: "kardiyoloji-ip.md", topics: "PCSK9, Factor XI, Lp(a), ATTR" },
  { name: "Metabolik", file: "metabolik-ip.md", topics: "GLP-1, obezite, MASH, KOAH" },
  { name: "Oftalmoloji", file: "oftalmoloji-ip.md", topics: "Anti-VEGF, Vabysmo, retinal gene tx" },
  { name: "Dermatoloji", file: "dermatoloji-ip.md", topics: "Psöriazis, AD, alopesi, vitiligo" },
];

const SCRIPTS = [
  { file: "loe-calculator.py", desc: "TR LOE + MAX(patent, veri imtiyazı + ruhsat)" },
  { file: "spc-calculator.py", desc: "AB SPC (Art. 13) — TR vs AB karşılaştırma" },
  { file: "claim-parser.py", desc: "İstem ayrıştırma + özellik extraction" },
  { file: "family-tracer.py", desc: "INPADOC aile izleme + coverage matrix" },
  { file: "cpc-recommender.py", desc: "CPC hiyerarşi + Boolean sorgu üretimi" },
  { file: "priority-date-matrix.py", desc: "Paris + PCT priority tutarlılık kontrolü" },
  { file: "royalty-calculator.py", desc: "NPV + Monte Carlo + tornado analiz" },
  { file: "patent-expiry-monitor.py", desc: "Portföy expiry takvimi" },
  { file: "report-builder.py", desc: "11 rapor tipi iskelet orkestratör" },
  { file: "biosimilar-comparator.py", desc: "CQA 3-tier benzerlik skorlama" },
];

export default function SkillShowcase() {
  const [selectedMode, setSelectedMode] = useState(MODES[0]);
  const [tab, setTab] = useState("modes");

  const audienceColor = (a) => a === "Legal" ? "bg-purple-50 text-purple-800 border-purple-200" :
                              a === "Executive" ? "bg-blue-50 text-blue-800 border-blue-200" :
                              "bg-gray-50 text-gray-800 border-gray-200";

  return (
    <div style={{ fontFamily: "'IBM Plex Sans', -apple-system, sans-serif", maxWidth: 1100, margin: "0 auto", padding: "1.5rem", background: "#f4f4f4", borderRadius: 12 }}>
      
      {/* Header */}
      <div style={{ borderBottom: "2px solid #161616", paddingBottom: 16, marginBottom: 20 }}>
        <div style={{ display: "flex", alignItems: "baseline", gap: 12 }}>
          <h1 style={{ fontSize: 22, fontWeight: 500, color: "#161616", margin: 0 }}>pharmapatent</h1>
          <span style={{ background: "#0f62fe", color: "white", padding: "2px 10px", borderRadius: 4, fontSize: 12, fontFamily: "'IBM Plex Mono', monospace" }}>v1.6.0</span>
        </div>
        <p style={{ color: "#525252", fontSize: 14, margin: "6px 0 0 0" }}>
          Farmasötik + tıbbi cihaz patent skill — 12 operasyonel mod, 9 domain, 10 script, 33 görsel şablonu
        </p>
      </div>

      {/* Tab nav */}
      <div style={{ display: "flex", gap: 4, marginBottom: 20, borderBottom: "1px solid #c6c6c6" }}>
        {[
          { id: "modes", label: "Operasyonel Modlar", count: 12 },
          { id: "domains", label: "Domain Derinlikleri", count: 9 },
          { id: "scripts", label: "Scripts", count: 10 },
          { id: "visuals", label: "Görsel Kütüphanesi", count: 33 },
        ].map(t => (
          <button key={t.id} onClick={() => setTab(t.id)} style={{
            padding: "10px 16px",
            background: tab === t.id ? "#0f62fe" : "transparent",
            color: tab === t.id ? "white" : "#161616",
            border: "none",
            borderBottom: tab === t.id ? "2px solid #0f62fe" : "2px solid transparent",
            cursor: "pointer", fontSize: 13, fontWeight: 500,
          }}>
            {t.label} <span style={{ opacity: 0.7, fontFamily: "'IBM Plex Mono', monospace" }}>({t.count})</span>
          </button>
        ))}
      </div>

      {/* MODES TAB */}
      {tab === "modes" && (
        <div style={{ display: "grid", gridTemplateColumns: "280px 1fr", gap: 20 }}>
          {/* Mode list */}
          <div style={{ background: "white", borderRadius: 8, border: "0.5px solid #c6c6c6", padding: 8, maxHeight: 540, overflowY: "auto" }}>
            {MODES.map(m => (
              <div key={m.id} onClick={() => setSelectedMode(m)} style={{
                padding: "8px 10px", borderRadius: 4, cursor: "pointer",
                background: selectedMode.id === m.id ? "#edf5ff" : "transparent",
                borderLeft: selectedMode.id === m.id ? "3px solid #0f62fe" : "3px solid transparent",
                marginBottom: 2,
              }}>
                <div style={{ display: "flex", alignItems: "baseline", gap: 8 }}>
                  <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: 11, color: "#525252" }}>Mod {m.id}</span>
                  <span style={{ fontSize: 12, fontWeight: 500 }}>{m.name}</span>
                </div>
                <div style={{ fontSize: 11, color: "#6f6f6f", marginTop: 2 }}>{m.short} · {m.audience}</div>
              </div>
            ))}
          </div>

          {/* Mode detail */}
          <div style={{ background: "white", borderRadius: 8, border: "0.5px solid #c6c6c6", padding: 20 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 12 }}>
              <h2 style={{ fontSize: 18, fontWeight: 500, margin: 0 }}>Mod {selectedMode.id} — {selectedMode.name}</h2>
              <span style={{ fontSize: 11, padding: "3px 8px", borderRadius: 3, border: "1px solid", ...{ background: audienceColor(selectedMode.audience).split(" ")[0].replace("bg-", ""), color: audienceColor(selectedMode.audience).split(" ")[1].replace("text-", "") } }} className={audienceColor(selectedMode.audience)}>
                {selectedMode.audience}
              </span>
            </div>
            <p style={{ color: "#525252", fontSize: 13, margin: "0 0 16px 0" }}>{selectedMode.desc}</p>

            <div style={{ marginBottom: 14 }}>
              <div style={{ fontSize: 11, color: "#6f6f6f", textTransform: "uppercase", letterSpacing: 0.5, marginBottom: 6 }}>Zorunlu görseller ({selectedMode.visuals.length})</div>
              <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
                {selectedMode.visuals.map(v => (
                  <span key={v} style={{ background: "#e5f6ff", color: "#0043ce", padding: "4px 8px", borderRadius: 3, fontSize: 11, fontFamily: "'IBM Plex Mono', monospace" }}>{v}</span>
                ))}
              </div>
            </div>

            <div style={{ marginBottom: 14 }}>
              <div style={{ fontSize: 11, color: "#6f6f6f", textTransform: "uppercase", letterSpacing: 0.5, marginBottom: 6 }}>İlgili scripts ({selectedMode.scripts.length})</div>
              <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
                {selectedMode.scripts.map(s => (
                  <span key={s} style={{ background: "#d9fbfb", color: "#004d40", padding: "4px 8px", borderRadius: 3, fontSize: 11, fontFamily: "'IBM Plex Mono', monospace" }}>{s}</span>
                ))}
              </div>
            </div>

            {selectedMode.example && (
              <div style={{ marginBottom: 14 }}>
                <div style={{ fontSize: 11, color: "#6f6f6f", textTransform: "uppercase", letterSpacing: 0.5, marginBottom: 6 }}>Filled example</div>
                <code style={{ background: "#f4f4f4", padding: "4px 8px", borderRadius: 3, fontSize: 12 }}>examples/{selectedMode.example}</code>
              </div>
            )}

            <div style={{ marginTop: 20, padding: 12, background: "#f4f4f4", borderLeft: "3px solid #0f62fe", fontSize: 12 }}>
              <div style={{ fontWeight: 500, marginBottom: 4 }}>Kullanım akışı:</div>
              <ol style={{ margin: 0, paddingLeft: 20, color: "#525252" }}>
                <li><code>report-builder.py --type {selectedMode.type} --asset "X"</code> ile iskelet</li>
                <li>Visuals için <code>visualize:read_me</code> → kütüphaneden şablon</li>
                <li>Scripts ile hesaplamalar</li>
                <li>Compliance + review + deliver</li>
              </ol>
            </div>
          </div>
        </div>
      )}

      {/* DOMAINS TAB */}
      {tab === "domains" && (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: 12 }}>
          {DOMAINS.map(d => (
            <div key={d.file} style={{ background: "white", borderRadius: 8, border: "0.5px solid #c6c6c6", padding: 16 }}>
              <div style={{ fontSize: 15, fontWeight: 500, marginBottom: 4 }}>{d.name}</div>
              <div style={{ fontSize: 11, color: "#6f6f6f", fontFamily: "'IBM Plex Mono', monospace", marginBottom: 8 }}>domains/{d.file}</div>
              <div style={{ fontSize: 12, color: "#525252" }}>{d.topics}</div>
            </div>
          ))}
        </div>
      )}

      {/* SCRIPTS TAB */}
      {tab === "scripts" && (
        <div style={{ background: "white", borderRadius: 8, border: "0.5px solid #c6c6c6", overflow: "hidden" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
            <thead>
              <tr style={{ background: "#e0e0e0" }}>
                <th style={{ padding: 10, textAlign: "left", borderBottom: "1px solid #c6c6c6" }}>Script</th>
                <th style={{ padding: 10, textAlign: "left", borderBottom: "1px solid #c6c6c6" }}>Açıklama</th>
              </tr>
            </thead>
            <tbody>
              {SCRIPTS.map(s => (
                <tr key={s.file}>
                  <td style={{ padding: 10, borderBottom: "0.5px solid #e0e0e0", fontFamily: "'IBM Plex Mono', monospace", color: "#0043ce" }}>scripts/{s.file}</td>
                  <td style={{ padding: 10, borderBottom: "0.5px solid #e0e0e0", color: "#525252" }}>{s.desc}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* VISUALS TAB */}
      {tab === "visuals" && (
        <div>
          <p style={{ color: "#525252", fontSize: 13, marginBottom: 16 }}>
            <code>references/visualize-widget-kutuphanesi.md</code> — IBM Carbon Design System uyumlu 33 SVG/Mermaid/HTML şablonu.
          </p>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))", gap: 8 }}>
            {["fto-patent-country-heatmap", "fto-feature-matrix", "fto-design-around-tree", "fto-loe-gantt",
              "invalidity-mosaic", "invalidity-radar", "invalidity-citation-network", "invalidity-forum-tree",
              "landscape-filing-trend", "landscape-assignee-bar", "landscape-geo-choropleth", "landscape-evergreening-timeline",
              "lifecycle-gantt", "lifecycle-erosion", "lifecycle-quadrant",
              "launch-max-formula",
              "litigation-decision-tree", "litigation-cost-curve", "litigation-forum-matrix",
              "dd-radar", "dd-montecarlo", "dd-tornado",
              "opposition-art100-map", "opposition-problem-solution", "opposition-timeline",
              "biosimilar-multi-gantt", "biosimilar-sankey", "biosimilar-market-share", "biosimilar-launch-calendar",
              "expert-verdict-summary"
            ].map(v => (
              <div key={v} style={{ background: "white", borderRadius: 4, border: "0.5px solid #c6c6c6", padding: "8px 10px", fontSize: 11, fontFamily: "'IBM Plex Mono', monospace" }}>
                {v}
              </div>
            ))}
          </div>
        </div>
      )}

      <div style={{ marginTop: 24, paddingTop: 16, borderTop: "1px solid #e0e0e0", fontSize: 11, color: "#6f6f6f", textAlign: "center" }}>
        pharmapatent v1.6.0 · SMP v1.0 · IBM Carbon Design System · 2026-04-24
      </div>
    </div>
  );
}
