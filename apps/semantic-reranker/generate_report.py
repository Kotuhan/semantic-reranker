"""Generate a single-page HTML benchmark report from benchmark_results.json.

Usage:
    python generate_report.py                    # reads benchmark_results.json, writes report.html
    python generate_report.py results.json       # custom input
    python generate_report.py results.json out.html  # custom input + output
"""

import json
import sys
from pathlib import Path

THEORIES = [
    {
        "id": 1,
        "title": "More text = better understanding",
        "question": "Does adding location and subcategories to document text help the model?",
        "verdict": "confirmed",
        "summary": "Adding flattened subcategories gave +5-14% NDCG lift across all models. Location gave a small boost for geo-queries.",
        "experiments": ["title only", "title + desc", "title + desc + loc", "title + desc + loc + subcats"],
    },
    {
        "id": 2,
        "title": "A bigger model scores better",
        "question": "Does MiniLM-L-12 beat MiniLM-L-6? Does bge-reranker-base beat both?",
        "verdict": "partial",
        "summary": "L-12 offered marginal improvement over L-6. bge-reranker-base was the clear winner — architecture mattered more than layer count.",
        "experiments": ["MiniLM-L-12-v2", "bge-reranker-base"],
    },
    {
        "id": 3,
        "title": "Hybrid scoring combines the best of both worlds",
        "question": "Does blending keyword + semantic scores improve results?",
        "verdict": "rejected",
        "summary": "Hybrid scoring degraded results at every alpha value. The keyword scores added noise — the semantic model already captures what keywords measure.",
        "experiments": ["hybrid alpha=0.7", "hybrid alpha=0.8", "hybrid alpha=0.9"],
    },
    {
        "id": 4,
        "title": "Structured metadata matching helps",
        "question": "Does a category-match bonus (subcategory overlap counting) improve scoring?",
        "verdict": "rejected",
        "summary": "Less than 1% improvement — not worth the complexity. The cross-encoder already picks up associations through flattened text.",
        "experiments": ["category bonus beta=0.5", "category bonus beta=1.0", "category bonus beta=2.0"],
    },
    {
        "id": 5,
        "title": "Repeating important fields amplifies signal",
        "question": "Does duplicating high-value subcategory axes boost relevance?",
        "verdict": "rejected",
        "summary": "No meaningful effect. The cross-encoder's attention mechanism doesn't benefit from repetition like a bag-of-words model would.",
        "experiments": ["weighted subcat enrichment"],
    },
]


def generate_html(data: dict) -> str:
    experiments_json = json.dumps(data["experiments"])
    queries_json = json.dumps(data["queries"])
    theories_json = json.dumps(THEORIES)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Semantic Re-Ranker Benchmark Report</title>
<style>
  :root {{
    --bg: #0d1117; --surface: #161b22; --border: #30363d;
    --text: #e6edf3; --text-dim: #8b949e; --text-muted: #484f58;
    --green: #3fb950; --red: #f85149; --yellow: #d29922; --blue: #58a6ff;
    --green-bg: rgba(63,185,80,0.1); --red-bg: rgba(248,81,73,0.1);
    --yellow-bg: rgba(210,153,34,0.1);
  }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ background: var(--bg); color: var(--text); font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; line-height: 1.5; padding: 2rem; max-width: 1400px; margin: 0 auto; }}
  h1 {{ font-size: 1.75rem; margin-bottom: 0.25rem; }}
  h2 {{ font-size: 1.25rem; margin: 2rem 0 1rem; color: var(--text-dim); border-bottom: 1px solid var(--border); padding-bottom: 0.5rem; }}
  .subtitle {{ color: var(--text-dim); margin-bottom: 2rem; }}

  /* Summary cards */
  .cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem; }}
  .card {{ background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 1.25rem; }}
  .card-label {{ font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-dim); margin-bottom: 0.25rem; }}
  .card-value {{ font-size: 1.5rem; font-weight: 600; }}
  .card-value.green {{ color: var(--green); }}
  .card-detail {{ font-size: 0.8rem; color: var(--text-dim); margin-top: 0.25rem; }}

  /* Table */
  .table-wrap {{ overflow-x: auto; margin-bottom: 2rem; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 0.875rem; }}
  th, td {{ padding: 0.6rem 0.75rem; text-align: left; border-bottom: 1px solid var(--border); }}
  th {{ background: var(--surface); color: var(--text-dim); font-weight: 600; cursor: pointer; user-select: none; white-space: nowrap; }}
  th:hover {{ color: var(--text); }}
  th .arrow {{ font-size: 0.7rem; margin-left: 0.25rem; }}
  td {{ white-space: nowrap; }}
  tr:hover {{ background: rgba(255,255,255,0.02); }}
  tr.best {{ background: var(--green-bg); }}
  tr.baseline {{ font-weight: 600; }}
  .group-header td {{ background: var(--surface); color: var(--text-dim); font-weight: 600; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em; padding: 0.4rem 0.75rem; }}
  .delta-pos {{ color: var(--green); }}
  .delta-neg {{ color: var(--red); }}
  .delta-zero {{ color: var(--text-muted); }}
  td.num {{ text-align: right; font-variant-numeric: tabular-nums; }}

  /* Bar chart */
  .chart {{ background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 1.5rem; margin-bottom: 2rem; }}
  .bar-row {{ display: flex; align-items: center; margin-bottom: 0.4rem; }}
  .bar-label {{ width: 220px; font-size: 0.8rem; text-align: right; padding-right: 1rem; flex-shrink: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
  .bar-track {{ flex: 1; height: 24px; background: rgba(255,255,255,0.03); border-radius: 4px; position: relative; }}
  .bar-fill {{ height: 100%; border-radius: 4px; display: flex; align-items: center; padding-left: 0.5rem; font-size: 0.75rem; font-weight: 600; transition: width 0.3s; min-width: 2rem; }}
  .bar-fill.best {{ background: var(--green); color: var(--bg); }}
  .bar-fill.above {{ background: var(--blue); color: var(--bg); }}
  .bar-fill.at {{ background: var(--text-dim); color: var(--bg); }}
  .bar-fill.below {{ background: var(--red); color: white; }}
  .baseline-line {{ position: absolute; top: -2px; bottom: -2px; width: 2px; background: var(--yellow); z-index: 1; }}

  /* Heatmap */
  .heatmap {{ background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 1.5rem; overflow-x: auto; margin-bottom: 2rem; }}
  .heatmap table {{ font-size: 0.8rem; }}
  .heatmap th {{ font-size: 0.75rem; }}
  .heatmap td.heat {{ text-align: center; font-weight: 600; font-size: 0.8rem; border: 1px solid var(--border); min-width: 60px; }}
  .heatmap td.query-label {{ font-size: 0.75rem; max-width: 250px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}

  /* Scatter */
  .scatter {{ background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 1.5rem; margin-bottom: 2rem; }}
  .scatter svg {{ width: 100%; }}
  .scatter text {{ fill: var(--text-dim); font-size: 11px; }}
  .scatter .axis {{ stroke: var(--border); }}
  .scatter .dot {{ cursor: pointer; }}
  .scatter .dot:hover {{ r: 8; }}
  .scatter .label {{ font-size: 10px; fill: var(--text); pointer-events: none; }}

  /* Theory cards */
  .theories {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 1rem; margin-bottom: 2rem; }}
  .theory {{ background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 1.25rem; }}
  .theory-header {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem; }}
  .theory-title {{ font-weight: 600; font-size: 0.95rem; }}
  .badge {{ font-size: 0.7rem; padding: 0.15rem 0.5rem; border-radius: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.03em; flex-shrink: 0; margin-left: 0.5rem; }}
  .badge.confirmed {{ background: var(--green-bg); color: var(--green); border: 1px solid var(--green); }}
  .badge.rejected {{ background: var(--red-bg); color: var(--red); border: 1px solid var(--red); }}
  .badge.partial {{ background: var(--yellow-bg); color: var(--yellow); border: 1px solid var(--yellow); }}
  .theory-question {{ font-size: 0.85rem; color: var(--text-dim); font-style: italic; margin-bottom: 0.5rem; }}
  .theory-summary {{ font-size: 0.85rem; }}

  .footer {{ text-align: center; color: var(--text-muted); font-size: 0.75rem; margin-top: 3rem; padding-top: 1rem; border-top: 1px solid var(--border); }}
</style>
</head>
<body>

<h1>Semantic Re-Ranker Benchmark</h1>
<p class="subtitle">Systematic comparison of 15 re-ranking approaches across models, text compositions, and scoring strategies</p>

<div id="cards" class="cards"></div>

<h2>Comparison Table</h2>
<div class="table-wrap"><table id="main-table"><thead></thead><tbody></tbody></table></div>

<h2>NDCG@10 by Experiment</h2>
<div id="bar-chart" class="chart"></div>

<h2>Per-Query Heatmap (NDCG@10)</h2>
<div id="heatmap" class="heatmap"></div>

<h2>Quality vs Latency</h2>
<div id="scatter" class="scatter"></div>

<h2>Theories Tested</h2>
<div id="theories" class="theories"></div>

<div class="footer">
  Generated from <code>benchmark_results.json</code> &middot; <span id="timestamp"></span>
</div>

<script>
const DATA = {experiments_json};
const QUERIES = {queries_json};
const THEORIES = {theories_json};
const TIMESTAMP = "{data['timestamp']}";
const BASELINE_NAME = "{data['baseline']}";
const BEST_NAME = "{data['best']}";

const baseline = DATA.find(e => e.name === BASELINE_NAME);
const best = DATA.find(e => e.name === BEST_NAME);

// --- Summary cards ---
document.getElementById('cards').innerHTML = `
  <div class="card"><div class="card-label">Best Configuration</div><div class="card-value green">${{BEST_NAME}}</div></div>
  <div class="card"><div class="card-label">Best NDCG@10</div><div class="card-value green">${{best.ndcg10.toFixed(4)}}</div><div class="card-detail">vs baseline ${{baseline.ndcg10.toFixed(4)}}</div></div>
  <div class="card"><div class="card-label">Improvement</div><div class="card-value green">+${{((best.ndcg10 - baseline.ndcg10) / baseline.ndcg10 * 100).toFixed(1)}}%</div><div class="card-detail">NDCG@10 over baseline</div></div>
  <div class="card"><div class="card-label">Best P@5</div><div class="card-value green">${{best.precision5.toFixed(4)}}</div><div class="card-detail">vs baseline ${{baseline.precision5.toFixed(4)}}</div></div>
  <div class="card"><div class="card-label">Experiments</div><div class="card-value">${{DATA.length}}</div><div class="card-detail">across ${{[...new Set(DATA.map(e=>e.group))].length}} categories</div></div>
`;

// --- Table ---
let sortCol = 'ndcg10', sortAsc = false;

function renderTable() {{
  const thead = document.querySelector('#main-table thead');
  const tbody = document.querySelector('#main-table tbody');
  const cols = [
    ['#','num',false], ['Experiment','name',false], ['Group','group',false],
    ['NDCG@10','ndcg10',true], ['P@5','precision5',true],
    ['dNDCG','delta_ndcg',true], ['dP@5','delta_precision',true], ['Time (s)','elapsed_seconds',true]
  ];
  thead.innerHTML = '<tr>' + cols.map(([label,key,isNum]) => {{
    const arrow = key === sortCol ? (sortAsc ? ' \\u25B2' : ' \\u25BC') : '';
    return `<th data-key="${{key}}">${{label}}<span class="arrow">${{arrow}}</span></th>`;
  }}).join('') + '</tr>';

  const sorted = [...DATA].sort((a,b) => {{
    const va = a[sortCol], vb = b[sortCol];
    return sortAsc ? (va > vb ? 1 : -1) : (va < vb ? 1 : -1);
  }});

  let html = '';
  let lastGroup = '';
  sorted.forEach((e, i) => {{
    if (e.group !== lastGroup) {{
      html += `<tr class="group-header"><td colspan="8">${{e.group}}</td></tr>`;
      lastGroup = e.group;
    }}
    const cls = e.name === BEST_NAME ? 'best' : (e.name === BASELINE_NAME ? 'baseline' : '');
    const dc = (v) => v > 0.001 ? 'delta-pos' : (v < -0.001 ? 'delta-neg' : 'delta-zero');
    html += `<tr class="${{cls}}">
      <td class="num">${{i+1}}</td><td>${{e.name}}</td><td>${{e.group}}</td>
      <td class="num">${{e.ndcg10.toFixed(4)}}</td><td class="num">${{e.precision5.toFixed(4)}}</td>
      <td class="num ${{dc(e.delta_ndcg)}}">${{e.delta_ndcg >= 0 ? '+' : ''}}${{e.delta_ndcg.toFixed(4)}}</td>
      <td class="num ${{dc(e.delta_precision)}}">${{e.delta_precision >= 0 ? '+' : ''}}${{e.delta_precision.toFixed(4)}}</td>
      <td class="num">${{e.elapsed_seconds.toFixed(2)}}</td>
    </tr>`;
  }});
  tbody.innerHTML = html;
}}

document.querySelector('#main-table thead').addEventListener('click', (ev) => {{
  const th = ev.target.closest('th');
  if (!th) return;
  const key = th.dataset.key;
  if (sortCol === key) sortAsc = !sortAsc;
  else {{ sortCol = key; sortAsc = key === 'name' || key === 'group'; }}
  renderTable();
}});
renderTable();

// --- Bar chart ---
(function() {{
  const maxNdcg = Math.max(...DATA.map(e => e.ndcg10));
  const baselineNdcg = baseline.ndcg10;
  const baselinePct = (baselineNdcg / maxNdcg * 100);
  let html = '';
  let lastGroup = '';
  DATA.forEach(e => {{
    if (e.group !== lastGroup) {{
      html += `<div style="font-size:0.75rem;color:var(--text-dim);margin:0.75rem 0 0.25rem 220px;text-transform:uppercase;letter-spacing:0.05em">${{e.group}}</div>`;
      lastGroup = e.group;
    }}
    const pct = (e.ndcg10 / maxNdcg * 100);
    const cls = e.name === BEST_NAME ? 'best' : (e.ndcg10 > baselineNdcg ? 'above' : (e.ndcg10 === baselineNdcg ? 'at' : 'below'));
    html += `<div class="bar-row">
      <div class="bar-label">${{e.name}}</div>
      <div class="bar-track">
        <div class="baseline-line" style="left:${{baselinePct}}%"></div>
        <div class="bar-fill ${{cls}}" style="width:${{pct}}%">${{e.ndcg10.toFixed(4)}}</div>
      </div>
    </div>`;
  }});
  document.getElementById('bar-chart').innerHTML = html;
}})();

// --- Heatmap ---
(function() {{
  let html = '<table><thead><tr><th></th>';
  QUERIES.forEach((q, i) => {{ html += `<th>Q${{i+1}}</th>`; }});
  html += '</tr></thead><tbody>';
  DATA.forEach(e => {{
    html += `<tr><td class="query-label">${{e.name}}</td>`;
    e.per_query_ndcg.forEach(v => {{
      const hue = Math.round(v * 120); // 0=red, 60=yellow, 120=green
      const bg = `hsl(${{hue}}, 70%, ${{15 + v * 25}}%)`;
      html += `<td class="heat" style="background:${{bg}}">${{v.toFixed(2)}}</td>`;
    }});
    html += '</tr>';
  }});
  html += '</tbody></table>';
  html += '<div style="margin-top:0.75rem;font-size:0.75rem;color:var(--text-dim)">';
  QUERIES.forEach((q, i) => {{ html += `<strong>Q${{i+1}}</strong>: ${{q}}<br>`; }});
  html += '</div>';
  document.getElementById('heatmap').innerHTML = html;
}})();

// --- Scatter: Quality vs Latency ---
(function() {{
  const W = 800, H = 400, pad = {{t:30,r:30,b:50,l:60}};
  const pw = W - pad.l - pad.r, ph = H - pad.t - pad.b;
  const maxT = Math.max(...DATA.map(e => e.elapsed_seconds)) * 1.1;
  const minN = Math.min(...DATA.map(e => e.ndcg10)) * 0.95;
  const maxN = Math.max(...DATA.map(e => e.ndcg10)) * 1.02;
  const x = (t) => pad.l + (t / maxT) * pw;
  const y = (n) => pad.t + (1 - (n - minN) / (maxN - minN)) * ph;

  let svg = `<svg viewBox="0 0 ${{W}} ${{H}}">`;
  // Axes
  svg += `<line class="axis" x1="${{pad.l}}" y1="${{pad.t}}" x2="${{pad.l}}" y2="${{H-pad.b}}" />`;
  svg += `<line class="axis" x1="${{pad.l}}" y1="${{H-pad.b}}" x2="${{W-pad.r}}" y2="${{H-pad.b}}" />`;
  svg += `<text x="${{W/2}}" y="${{H-8}}" text-anchor="middle">Latency (seconds)</text>`;
  svg += `<text x="15" y="${{H/2}}" text-anchor="middle" transform="rotate(-90,15,${{H/2}})">NDCG@10</text>`;
  // Tick marks
  for (let t = 0; t <= maxT; t += Math.ceil(maxT / 5)) {{
    svg += `<text x="${{x(t)}}" y="${{H-pad.b+18}}" text-anchor="middle">${{t.toFixed(1)}}</text>`;
    svg += `<line stroke="var(--border)" stroke-dasharray="2" x1="${{x(t)}}" y1="${{pad.t}}" x2="${{x(t)}}" y2="${{H-pad.b}}" />`;
  }}
  for (let n = Math.ceil(minN*10)/10; n <= maxN; n += 0.05) {{
    svg += `<text x="${{pad.l-8}}" y="${{y(n)+4}}" text-anchor="end">${{n.toFixed(2)}}</text>`;
    svg += `<line stroke="var(--border)" stroke-dasharray="2" x1="${{pad.l}}" y1="${{y(n)}}" x2="${{W-pad.r}}" y2="${{y(n)}}" />`;
  }}
  // Baseline line
  svg += `<line stroke="var(--yellow)" stroke-dasharray="4" x1="${{pad.l}}" y1="${{y(baseline.ndcg10)}}" x2="${{W-pad.r}}" y2="${{y(baseline.ndcg10)}}" />`;
  // Points
  DATA.forEach(e => {{
    const color = e.name === BEST_NAME ? 'var(--green)' : (e.ndcg10 > baseline.ndcg10 ? 'var(--blue)' : 'var(--red)');
    svg += `<circle class="dot" cx="${{x(e.elapsed_seconds)}}" cy="${{y(e.ndcg10)}}" r="5" fill="${{color}}"><title>${{e.name}}\\nNDCG: ${{e.ndcg10.toFixed(4)}}\\nTime: ${{e.elapsed_seconds.toFixed(2)}}s</title></circle>`;
    // Label best and worst
    if (e.name === BEST_NAME || e.ndcg10 === Math.min(...DATA.map(d=>d.ndcg10))) {{
      svg += `<text class="label" x="${{x(e.elapsed_seconds)+8}}" y="${{y(e.ndcg10)+4}}">${{e.name}}</text>`;
    }}
  }});
  svg += '</svg>';
  document.getElementById('scatter').innerHTML = svg;
}})();

// --- Theory cards ---
document.getElementById('theories').innerHTML = THEORIES.map(t => `
  <div class="theory">
    <div class="theory-header">
      <span class="theory-title">#${{t.id}}. "${{t.title}}"</span>
      <span class="badge ${{t.verdict}}">${{t.verdict}}</span>
    </div>
    <div class="theory-question">${{t.question}}</div>
    <div class="theory-summary">${{t.summary}}</div>
  </div>
`).join('');

document.getElementById('timestamp').textContent = new Date(TIMESTAMP).toLocaleString();
</script>
</body>
</html>"""


def main() -> None:
    input_path = sys.argv[1] if len(sys.argv) > 1 else "benchmark_results.json"
    output_path = sys.argv[2] if len(sys.argv) > 2 else "report.html"

    path = Path(input_path)
    if not path.exists():
        print(f"Error: {input_path} not found. Run benchmark.py first.")
        sys.exit(1)

    with open(path) as f:
        data = json.load(f)

    html = generate_html(data)
    with open(output_path, "w") as f:
        f.write(html)

    print(f"Report generated: {output_path}")


if __name__ == "__main__":
    main()
