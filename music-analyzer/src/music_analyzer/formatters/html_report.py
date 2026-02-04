"""HTML visualization report generator.

Produces a self-contained single-file HTML report with embedded JSON data
and interactive charts for all analysis dimensions.
"""

from __future__ import annotations

import json
from pathlib import Path

from music_analyzer.models import MusicAnalysisResult, DreaminaOutput, StoryboardOutput

_TEMPLATE = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>%%TITLE%% — Music Analysis</title>
<style>
  :root {
    --bg: #0e0e12;
    --card: #17171e;
    --border: #2a2a35;
    --text: #e4e4e8;
    --text-dim: #8888a0;
    --accent: #FFD700;
    --accent2: #FF6B35;
    --accent3: #FF1493;
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: -apple-system, 'SF Pro Display', 'Helvetica Neue', sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.6;
    overflow-x: hidden;
  }

  /* Hero */
  .hero {
    position: relative;
    padding: 60px 40px 40px;
    background: linear-gradient(135deg, #1a1025 0%, #0e0e12 50%, #0d1520 100%);
    border-bottom: 1px solid var(--border);
    overflow: hidden;
  }
  .hero::before {
    content: '';
    position: absolute;
    top: -100px; right: -100px;
    width: 400px; height: 400px;
    background: radial-gradient(circle, rgba(255,215,0,0.08) 0%, transparent 70%);
    pointer-events: none;
  }
  .hero-title {
    font-size: 48px;
    font-weight: 700;
    letter-spacing: -1px;
    background: linear-gradient(135deg, #FFD700, #FF6B35);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }
  .hero-sub {
    font-size: 18px;
    color: var(--text-dim);
    margin-top: 8px;
  }
  .hero-meta {
    display: flex;
    gap: 24px;
    margin-top: 24px;
    flex-wrap: wrap;
  }
  .meta-chip {
    display: flex;
    align-items: center;
    gap: 8px;
    background: rgba(255,255,255,0.05);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 6px 16px;
    font-size: 14px;
  }
  .meta-chip .label { color: var(--text-dim); }
  .meta-chip .value { color: var(--accent); font-weight: 600; }

  /* Layout */
  .container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 40px 24px;
  }
  .grid-2 {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 24px;
  }
  .grid-3 {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 24px;
  }
  @media (max-width: 768px) {
    .grid-2, .grid-3 { grid-template-columns: 1fr; }
    .hero { padding: 32px 20px; }
    .hero-title { font-size: 32px; }
  }

  /* Cards */
  .card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 28px;
    transition: border-color 0.2s;
  }
  .card:hover { border-color: rgba(255,215,0,0.3); }
  .card-title {
    font-size: 13px;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: var(--text-dim);
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .card-title .icon { font-size: 16px; }
  .big-number {
    font-size: 56px;
    font-weight: 800;
    line-height: 1;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }
  .big-label {
    font-size: 14px;
    color: var(--text-dim);
    margin-top: 4px;
  }
  .stat-row {
    display: flex;
    justify-content: space-between;
    padding: 10px 0;
    border-bottom: 1px solid rgba(255,255,255,0.04);
  }
  .stat-row:last-child { border-bottom: none; }
  .stat-key { color: var(--text-dim); font-size: 14px; }
  .stat-val { font-weight: 600; font-size: 14px; }

  /* Section title */
  .section-title {
    font-size: 24px;
    font-weight: 700;
    margin: 48px 0 24px;
    padding-bottom: 12px;
    border-bottom: 1px solid var(--border);
  }

  /* Energy bar chart */
  .energy-chart {
    display: flex;
    align-items: flex-end;
    gap: 6px;
    height: 100px;
    margin-top: 16px;
  }
  .energy-bar {
    flex: 1;
    border-radius: 4px 4px 0 0;
    position: relative;
    min-width: 20px;
    transition: height 0.3s;
  }
  .energy-bar:hover { opacity: 0.8; }
  .energy-bar .bar-label {
    position: absolute;
    bottom: -20px;
    left: 50%;
    transform: translateX(-50%);
    font-size: 10px;
    color: var(--text-dim);
  }
  .energy-bar .bar-value {
    position: absolute;
    top: -18px;
    left: 50%;
    transform: translateX(-50%);
    font-size: 11px;
    color: var(--text);
    font-weight: 600;
  }

  /* Color palette */
  .palette-large {
    display: flex;
    gap: 0;
    height: 80px;
    border-radius: 12px;
    overflow: hidden;
    margin-top: 16px;
  }
  .palette-large-swatch {
    flex: 1;
    display: flex;
    align-items: flex-end;
    justify-content: center;
    padding-bottom: 8px;
    font-size: 11px;
    font-weight: 600;
    color: rgba(0,0,0,0.5);
  }

  /* Tags */
  .tags {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 12px;
  }
  .tag {
    background: rgba(255,215,0,0.1);
    border: 1px solid rgba(255,215,0,0.2);
    color: var(--accent);
    border-radius: 16px;
    padding: 4px 14px;
    font-size: 13px;
  }

  /* Gauge */
  .gauge-container {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-top: 8px;
  }
  .gauge {
    flex: 1;
    height: 6px;
    background: rgba(255,255,255,0.06);
    border-radius: 3px;
    position: relative;
  }
  .gauge-fill {
    height: 100%;
    border-radius: 3px;
  }
  .gauge-value {
    font-size: 14px;
    font-weight: 700;
    min-width: 40px;
    text-align: right;
  }

  /* Beats visualization */
  .beats-strip {
    height: 40px;
    background: rgba(255,255,255,0.02);
    border-radius: 8px;
    position: relative;
    overflow: hidden;
    margin-top: 12px;
  }
  .beat-tick {
    position: absolute;
    top: 0;
    width: 1px;
    height: 100%;
    background: var(--accent);
    opacity: 0.3;
  }
  .section-highlight {
    position: absolute;
    top: 0;
    height: 100%;
    opacity: 0.15;
    border-radius: 4px;
  }

  /* Chord flow */
  .chord-flow {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
    margin-top: 12px;
  }
  .chord-box {
    background: rgba(255,255,255,0.05);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 4px 10px;
    font-size: 13px;
    font-family: 'SF Mono', monospace;
    color: var(--text);
  }
  .chord-arrow {
    color: var(--text-dim);
    font-size: 12px;
    display: flex;
    align-items: center;
  }

  /* Storyboard */
  .shot-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 16px;
    display: grid;
    grid-template-columns: 60px 1fr 200px;
    gap: 20px;
    align-items: start;
    transition: border-color 0.2s;
  }
  .shot-card:hover { border-color: rgba(255,215,0,0.3); }
  .shot-num {
    font-size: 28px;
    font-weight: 800;
    color: var(--accent);
    text-align: center;
  }
  .shot-section-tag {
    font-size: 11px;
    text-transform: uppercase;
    color: var(--text-dim);
    text-align: center;
  }
  .shot-content h4 {
    font-size: 14px;
    font-weight: 600;
    margin-bottom: 8px;
  }
  .shot-content p {
    font-size: 13px;
    color: var(--text-dim);
    line-height: 1.5;
  }
  .shot-meta {
    font-size: 12px;
    color: var(--text-dim);
  }
  .shot-meta .shot-meta-item {
    display: flex;
    justify-content: space-between;
    padding: 4px 0;
    border-bottom: 1px solid rgba(255,255,255,0.03);
  }
  .shot-colors {
    display: flex;
    gap: 4px;
    margin-top: 8px;
  }
  .shot-colors .mini-swatch {
    width: 16px;
    height: 16px;
    border-radius: 4px;
  }
  @media (max-width: 768px) {
    .shot-card { grid-template-columns: 1fr; }
  }

  /* Dreamina prompts */
  .dreamina-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 12px;
  }
  .dreamina-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
  }
  .dreamina-section-label {
    font-weight: 700;
    font-size: 14px;
  }
  .dreamina-time {
    font-size: 12px;
    color: var(--text-dim);
    font-family: 'SF Mono', monospace;
  }
  .dreamina-prompt {
    font-size: 13px;
    line-height: 1.6;
    padding: 12px 16px;
    background: rgba(255,215,0,0.04);
    border: 1px solid rgba(255,215,0,0.1);
    border-radius: 8px;
    margin-bottom: 8px;
    cursor: pointer;
    transition: background 0.2s;
  }
  .dreamina-prompt:hover { background: rgba(255,215,0,0.08); }
  .dreamina-prompt.en {
    background: rgba(255,107,53,0.04);
    border-color: rgba(255,107,53,0.1);
  }
  .dreamina-prompt.en:hover { background: rgba(255,107,53,0.08); }
  .dreamina-prompt .lang-label {
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: var(--text-dim);
    margin-bottom: 4px;
  }
  .copy-hint {
    font-size: 10px;
    color: var(--text-dim);
    text-align: right;
    margin-top: 4px;
  }
  .copied-toast {
    position: fixed;
    bottom: 30px;
    left: 50%;
    transform: translateX(-50%);
    background: var(--accent);
    color: #000;
    padding: 8px 20px;
    border-radius: 20px;
    font-size: 14px;
    font-weight: 600;
    opacity: 0;
    transition: opacity 0.3s;
    pointer-events: none;
    z-index: 100;
  }
  .copied-toast.show { opacity: 1; }
</style>
</head>
<body>

<div class="hero">
  <div class="hero-title">%%TITLE%%</div>
  <div class="hero-sub">Music Analysis Report — Generated by music-analyzer</div>
  <div class="hero-meta" id="heroMeta"></div>
</div>

<div class="container">
  <div class="grid-3" id="overviewCards"></div>

  <div class="section-title">Song Structure & Beats</div>
  <div class="card">
    <div class="card-title"><span class="icon">&#9833;</span> Beat Grid & Sections</div>
    <div class="beats-strip" id="beatsStrip"></div>
    <div style="display:flex; gap:16px; margin-top:16px; flex-wrap:wrap;" id="sectionLegend"></div>
  </div>

  <div class="section-title">Emotion & Energy</div>
  <div class="grid-2">
    <div class="card">
      <div class="card-title"><span class="icon">&#9829;</span> Emotion Profile</div>
      <div id="emotionProfile"></div>
    </div>
    <div class="card">
      <div class="card-title"><span class="icon">&#9889;</span> Energy Curve</div>
      <div class="energy-chart" id="energyChart"></div>
      <div style="height:24px"></div>
    </div>
  </div>

  <div class="section-title">Timbre & Tonality</div>
  <div class="grid-2">
    <div class="card">
      <div class="card-title"><span class="icon">&#9678;</span> Timbre Characteristics</div>
      <div id="timbreProfile"></div>
    </div>
    <div class="card">
      <div class="card-title"><span class="icon">&#9839;</span> Tonality & Chords</div>
      <div id="tonalityProfile"></div>
    </div>
  </div>

  <div class="section-title">Color Palette</div>
  <div class="card">
    <div class="card-title"><span class="icon">&#9670;</span> Mood-Derived Colors</div>
    <div class="palette-large" id="paletteLarge"></div>
    <div style="margin-top:16px" id="paletteDetails"></div>
  </div>

  <div class="section-title">Dreamina Prompts</div>
  <p style="color:var(--text-dim); margin-bottom:16px; font-size:14px;">
    Click any prompt to copy to clipboard. Use with <code>/dreamina-gen-image</code> to generate visuals.
  </p>
  <div id="dreaminaList"></div>

  <div class="section-title">Storyboard</div>
  <p style="color:var(--text-dim); margin-bottom:16px; font-size:14px;">
    Shot-by-shot breakdown compatible with pull-film's storyboard-generator.
  </p>
  <div class="storyboard-timeline" id="storyboardList"></div>
</div>

<div class="copied-toast" id="copiedToast">Copied!</div>

<script>
const analysis = %%ANALYSIS_JSON%%;
const dreamina = %%DREAMINA_JSON%%;
const storyboard = %%STORYBOARD_JSON%%;

function fmt(n, d=1) { return Number(n).toFixed(d); }
function fmtTime(s) {
  const m = Math.floor(s/60);
  const sec = Math.floor(s%60);
  return m+':'+sec.toString().padStart(2,'0');
}
function copyText(text) {
  navigator.clipboard.writeText(text);
  const t = document.getElementById('copiedToast');
  t.classList.add('show');
  setTimeout(function(){ t.classList.remove('show'); }, 1200);
}
const sectionColors = {
  intro:'#3498DB', verse:'#2ECC71', chorus:'#E74C3C',
  bridge:'#9B59B6', outro:'#95A5A6', full:'#F39C12'
};

/* Hero meta */
document.getElementById('heroMeta').innerHTML = [
  ['BPM', fmt(analysis.rhythm.bpm,1)],
  ['Key', analysis.tonality.key],
  ['Duration', fmtTime(analysis.duration)],
  ['Mood', analysis.emotion.primary_emotion],
  ['Energy', fmt(analysis.emotion.overall_energy*100,0)+'%'],
  ['Tier', analysis.dependency_tier],
].map(function(a){return '<div class="meta-chip"><span class="label">'+a[0]+'</span><span class="value">'+a[1]+'</span></div>';}).join('');

/* Overview cards */
document.getElementById('overviewCards').innerHTML =
  '<div class="card"><div class="card-title"><span class="icon">&#9833;</span> Tempo</div>'
  +'<div class="big-number">'+fmt(analysis.rhythm.bpm,1)+'</div>'
  +'<div class="big-label">BPM &middot; '+analysis.rhythm.time_signature+'</div>'
  +'<div class="stat-row"><span class="stat-key">Beats</span><span class="stat-val">'+analysis.rhythm.beats.length+'</span></div>'
  +'<div class="stat-row"><span class="stat-key">Sections</span><span class="stat-val">'+analysis.rhythm.sections.length+'</span></div>'
  +'<div class="stat-row"><span class="stat-key">Duration</span><span class="stat-val">'+fmtTime(analysis.duration)+'</span></div></div>'
  +'<div class="card"><div class="card-title"><span class="icon">&#9829;</span> Emotion</div>'
  +'<div class="big-number" style="font-size:36px">'+analysis.emotion.primary_emotion+'</div>'
  +'<div class="big-label">'+(analysis.emotion.genre!=='unknown'?analysis.emotion.genre:'genre pending')+'</div>'
  +'<div class="stat-row"><span class="stat-key">Valence</span><span class="stat-val">'+fmt(analysis.emotion.valence,2)+'</span></div>'
  +'<div class="stat-row"><span class="stat-key">Arousal</span><span class="stat-val">'+fmt(analysis.emotion.arousal,2)+'</span></div>'
  +'<div class="stat-row"><span class="stat-key">Method</span><span class="stat-val">'+analysis.emotion.method+'</span></div></div>'
  +'<div class="card"><div class="card-title"><span class="icon">&#9839;</span> Tonality</div>'
  +'<div class="big-number" style="font-size:36px">'+analysis.tonality.key+'</div>'
  +'<div class="big-label">confidence '+fmt(analysis.tonality.key_confidence*100,0)+'%</div>'
  +'<div class="stat-row"><span class="stat-key">Chords</span><span class="stat-val">'+analysis.tonality.chords.length+'</span></div>'
  +'<div class="stat-row"><span class="stat-key">Onsets</span><span class="stat-val">'+analysis.onsets.onset_times.length+'</span></div>'
  +'<div class="stat-row"><span class="stat-key">Onset rate</span><span class="stat-val">'+analysis.onsets.onset_rate+'/s</span></div></div>';

/* Beats strip */
(function(){
  var strip = document.getElementById('beatsStrip');
  var dur = analysis.duration;
  analysis.rhythm.sections.forEach(function(s){
    var base = s.label.split('_')[0].toLowerCase();
    var color = sectionColors[base]||'#F39C12';
    var left = (s.start/dur*100);
    var width = ((s.end-s.start)/dur*100);
    strip.innerHTML += '<div class="section-highlight" style="left:'+left+'%;width:'+width+'%;background:'+color+'"></div>';
  });
  var beats = analysis.rhythm.beats;
  var step = Math.max(1, Math.floor(beats.length/200));
  for (var i=0; i<beats.length; i+=step) {
    var b = beats[i];
    var left = (b.time/dur*100);
    var opacity = 0.15+b.strength*0.6;
    strip.innerHTML += '<div class="beat-tick" style="left:'+left+'%;opacity:'+opacity+'"></div>';
  }
  var legend = document.getElementById('sectionLegend');
  var used = [];
  analysis.rhythm.sections.forEach(function(s){ var l=s.label.split('_')[0].toLowerCase(); if(used.indexOf(l)===-1) used.push(l); });
  legend.innerHTML = used.map(function(s){return '<div style="display:flex;align-items:center;gap:6px;font-size:12px;color:var(--text-dim)"><div style="width:12px;height:12px;border-radius:3px;background:'+(sectionColors[s]||'#F39C12')+'"></div>'+s+'</div>';}).join('');
})();

/* Emotion profile */
(function(){
  var e = analysis.emotion;
  var html = '<div style="font-size:20px;font-weight:700;margin-bottom:16px">'+e.primary_emotion+'</div>';
  var gauges = [
    ['Energy', e.overall_energy, 'linear-gradient(90deg, #2ECC71, #FFD700, #E74C3C)'],
    ['Valence', (e.valence+1)/2, 'linear-gradient(90deg, #4682B4, #98D8C8, #FFD700)'],
    ['Arousal', e.arousal, 'linear-gradient(90deg, #5F9EA0, #9B59B6, #FF1493)'],
  ];
  gauges.forEach(function(g){
    html += '<div style="margin-top:12px"><div style="font-size:12px;color:var(--text-dim)">'+g[0]+'</div>';
    html += '<div class="gauge-container"><div class="gauge"><div class="gauge-fill" style="width:'+g[1]*100+'%;background:'+g[2]+'"></div></div><div class="gauge-value">'+fmt(g[1]*100,0)+'%</div></div></div>';
  });
  html += '<div class="tags">';
  e.mood_tags.forEach(function(t){ html += '<span class="tag">'+t+'</span>'; });
  html += '</div>';
  document.getElementById('emotionProfile').innerHTML = html;
})();

/* Energy chart */
(function(){
  var chart = document.getElementById('energyChart');
  var curve = analysis.emotion.energy_curve;
  var max = Math.max.apply(null, curve.concat([0.01]));
  var segDur = analysis.duration / curve.length;
  curve.forEach(function(v,i){
    var h = Math.max(4, (v/max)*90);
    var hue = 120-(v*120);
    chart.innerHTML += '<div class="energy-bar" style="height:'+h+'%;background:hsl('+hue+',70%,50%)"><span class="bar-value">'+fmt(v*100,0)+'</span><span class="bar-label">'+fmtTime(i*segDur)+'</span></div>';
  });
})();

/* Timbre */
(function(){
  var t = analysis.timbre;
  var html = '';
  [['Brightness',t.brightness,'#FFD700'],['Warmth',t.warmth,'#FF6B35']].forEach(function(g){
    html += '<div style="margin-bottom:12px"><div style="font-size:12px;color:var(--text-dim)">'+g[0]+'</div>';
    html += '<div class="gauge-container"><div class="gauge"><div class="gauge-fill" style="width:'+g[1]*100+'%;background:'+g[2]+'"></div></div><div class="gauge-value">'+fmt(g[1]*100,0)+'%</div></div></div>';
  });
  html += '<div class="stat-row"><span class="stat-key">Dynamic Range</span><span class="stat-val">'+t.dynamic_range_db+' dB</span></div>';
  html += '<div class="stat-row"><span class="stat-key">Spectral Centroid</span><span class="stat-val">'+fmt(t.spectral.spectral_centroid_mean,0)+' Hz</span></div>';
  html += '<div class="stat-row"><span class="stat-key">Spectral Bandwidth</span><span class="stat-val">'+fmt(t.spectral.spectral_bandwidth_mean,0)+' Hz</span></div>';
  html += '<div class="stat-row"><span class="stat-key">Spectral Rolloff</span><span class="stat-val">'+fmt(t.spectral.spectral_rolloff_mean,0)+' Hz</span></div>';
  html += '<div class="stat-row"><span class="stat-key">ZCR</span><span class="stat-val">'+fmt(t.spectral.zero_crossing_rate_mean,4)+'</span></div>';
  if (t.loudness_lufs!=null) html += '<div class="stat-row"><span class="stat-key">Loudness</span><span class="stat-val">'+t.loudness_lufs+' LUFS</span></div>';
  document.getElementById('timbreProfile').innerHTML = html;
})();

/* Tonality */
(function(){
  var t = analysis.tonality;
  var html = '<div style="font-size:24px;font-weight:700">'+t.key+'</div>';
  html += '<div style="font-size:13px;color:var(--text-dim);margin-top:4px">Confidence: '+fmt(t.key_confidence*100,0)+'% &middot; Method: '+t.method+'</div>';
  html += '<div style="margin-top:16px;font-size:12px;color:var(--text-dim)">Chord Progression (first 20)</div>';
  html += '<div class="chord-flow">';
  t.chords.slice(0,20).forEach(function(c,i){
    html += '<span class="chord-box">'+c.chord+'</span>';
    if (i<Math.min(t.chords.length,20)-1) html += '<span class="chord-arrow">&rarr;</span>';
  });
  html += '</div>';
  document.getElementById('tonalityProfile').innerHTML = html;
})();

/* Color palette */
(function(){
  var cp = analysis.color_palette;
  var large = document.getElementById('paletteLarge');
  cp.palette.forEach(function(hex){
    var r=parseInt(hex.slice(1,3),16), g=parseInt(hex.slice(3,5),16), b=parseInt(hex.slice(5,7),16);
    var lum = (0.299*r+0.587*g+0.114*b)/255;
    var tc = lum>0.5?'rgba(0,0,0,0.6)':'rgba(255,255,255,0.7)';
    large.innerHTML += '<div class="palette-large-swatch" style="background:'+hex+';color:'+tc+'">'+hex+'</div>';
  });
  var details = document.getElementById('paletteDetails');
  var roles = [['Primary',cp.primary],['Secondary',cp.secondary],['Accent',cp.accent],['Background',cp.background],['Text',cp.text]];
  details.innerHTML = '<div style="display:flex;gap:24px;flex-wrap:wrap">'
    +roles.map(function(r){return '<div style="text-align:center"><div style="width:48px;height:48px;border-radius:10px;background:'+r[1]+';border:1px solid var(--border)"></div><div style="font-size:11px;color:var(--text-dim);margin-top:6px">'+r[0]+'</div><div style="font-size:11px;font-family:monospace">'+r[1]+'</div></div>';}).join('')
    +'</div><div style="margin-top:12px;font-size:13px;color:var(--text-dim)">Mood: <strong style="color:var(--text)">'+cp.mood_association+'</strong></div>';
})();

/* Dreamina */
(function(){
  var list = document.getElementById('dreaminaList');
  var sections = dreamina.sections;
  var show = sections.length<=8 ? sections : [sections[0],sections[Math.floor(sections.length*0.2)],sections[Math.floor(sections.length*0.4)],sections[Math.floor(sections.length*0.6)],sections[Math.floor(sections.length*0.8)],sections[sections.length-1]];
  show.forEach(function(s){
    var ec = s.energy_level>0.6?'#E74C3C':s.energy_level>0.4?'#FFD700':'#2ECC71';
    list.innerHTML += '<div class="dreamina-card"><div class="dreamina-header"><div><span class="dreamina-section-label">'+s.section+'</span><span style="margin-left:12px;font-size:12px;color:'+ec+';font-weight:600">Energy '+fmt(s.energy_level*100,0)+'%</span></div><span class="dreamina-time">'+fmtTime(s.time_range.start)+' &mdash; '+fmtTime(s.time_range.end)+'</span></div>'
      +'<div class="dreamina-prompt" onclick="copyText(this.querySelector(\'.prompt-text\').textContent)"><div class="lang-label">Chinese Prompt</div><div class="prompt-text">'+s.prompt_zh+'</div></div>'
      +'<div class="dreamina-prompt en" onclick="copyText(this.querySelector(\'.prompt-text\').textContent)"><div class="lang-label">English Prompt</div><div class="prompt-text">'+s.prompt_en+'</div></div>'
      +'<div style="display:flex;justify-content:space-between;align-items:center;margin-top:8px"><div class="shot-colors">'+s.color_palette.map(function(c){return '<div class="mini-swatch" style="background:'+c+'"></div>';}).join('')+'</div><div class="copy-hint">click prompt to copy</div></div></div>';
  });
  if (sections.length>8) list.innerHTML += '<div style="text-align:center;color:var(--text-dim);font-size:14px;padding:12px">Showing 6 of '+sections.length+' sections</div>';
})();

/* Storyboard */
(function(){
  var list = document.getElementById('storyboardList');
  var shots = storyboard.shots;
  var show = shots.length<=10 ? shots : [shots[0],shots[1],shots[Math.floor(shots.length*0.3)],shots[Math.floor(shots.length*0.5)],shots[Math.floor(shots.length*0.7)],shots[Math.floor(shots.length*0.85)],shots[shots.length-2],shots[shots.length-1]];
  show.forEach(function(s){
    var base = s.section.split('_')[0].toLowerCase();
    var color = sectionColors[base]||'#F39C12';
    list.innerHTML += '<div class="shot-card"><div><div class="shot-num">#'+s.shot_number+'</div><div class="shot-section-tag" style="color:'+color+'">'+s.section+'</div></div>'
      +'<div class="shot-content"><h4>'+s.visual_description_zh+'</h4><p>'+s.visual_description_en+'</p></div>'
      +'<div class="shot-meta">'
      +'<div class="shot-meta-item"><span>Time</span><span>'+fmtTime(s.time_range.start)+' &mdash; '+fmtTime(s.time_range.end)+'</span></div>'
      +'<div class="shot-meta-item"><span>Duration</span><span>'+fmt(s.duration,1)+'s</span></div>'
      +'<div class="shot-meta-item"><span>Shot</span><span>'+s.shot_type+'</span></div>'
      +'<div class="shot-meta-item"><span>Camera</span><span>'+s.camera_movement+'</span></div>'
      +'<div class="shot-meta-item"><span>Transition</span><span>'+s.transition+'</span></div>'
      +'<div class="shot-meta-item"><span>Energy</span><span>'+fmt(s.energy_level*100,0)+'%</span></div>'
      +'<div class="shot-colors">'+s.color_palette.map(function(c){return '<div class="mini-swatch" style="background:'+c+'"></div>';}).join('')+'</div>'
      +'</div></div>';
  });
  if (shots.length>10) list.innerHTML += '<div style="text-align:center;color:var(--text-dim);font-size:14px;padding:12px">Showing 8 of '+shots.length+' shots</div>';
})();
</script>
</body>
</html>'''


def generate_html_report(
    analysis: MusicAnalysisResult,
    dreamina_output: DreaminaOutput,
    storyboard_output: StoryboardOutput,
    title: str | None = None,
) -> str:
    """Generate a self-contained HTML visualization report.

    Returns the complete HTML string.
    """
    if title is None:
        title = analysis.file_name or "Music Analysis"

    analysis_json = analysis.model_dump_json(exclude_none=True)
    dreamina_json = dreamina_output.model_dump_json(exclude_none=True)
    storyboard_json = storyboard_output.model_dump_json(exclude_none=True)

    html = _TEMPLATE
    html = html.replace("%%TITLE%%", _escape_html(title))
    html = html.replace("%%ANALYSIS_JSON%%", analysis_json)
    html = html.replace("%%DREAMINA_JSON%%", dreamina_json)
    html = html.replace("%%STORYBOARD_JSON%%", storyboard_json)

    return html


def _escape_html(text: str) -> str:
    """Minimal HTML escaping for title text."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
