# Data Visualization Reference

Use this reference for: charts, graphs, infographics, dashboards, data storytelling, statistical graphics,
maps, diagrams, flowcharts, network graphs, treemaps, Sankey diagrams, interactive data experiences,
and any task involving the visual representation of data.

---

## TABLE OF CONTENTS
1. Chart Selection Guide
2. Chart Design Principles
3. Color for Data
4. Chart.js Patterns
5. D3.js Patterns
6. SVG Charts (Hand-Built)
7. Infographic Design
8. Diagram & Flowchart Design

---

## 1. CHART SELECTION GUIDE

| Data Relationship | Best Chart Types |
|-------------------|-----------------|
| **Comparison** (this vs that) | Bar chart, grouped bar, lollipop chart |
| **Trend over time** | Line chart, area chart, sparkline |
| **Part-to-whole** | Donut chart, stacked bar, treemap, waffle chart |
| **Distribution** | Histogram, box plot, violin plot, density plot |
| **Correlation** | Scatter plot, bubble chart, heatmap |
| **Ranking** | Horizontal bar chart, slope chart, bump chart |
| **Flow/Process** | Sankey diagram, flow chart, funnel chart |
| **Geographic** | Choropleth map, bubble map, cartogram |
| **Hierarchical** | Treemap, sunburst, nested circles |
| **Network/Relationship** | Node-link diagram, adjacency matrix, arc diagram |
| **Single value/KPI** | Big number, gauge, progress bar |

### When NOT to Use a Chart
- **Pie charts**: Almost never. Humans are bad at comparing angles. Use bar charts instead.
  Exception: Exactly 2-3 segments where one dominates (>60%).
- **3D charts**: Never. They distort data perception. Always use 2D.
- **Dual Y-axes**: Rarely. They invite misinterpretation. Use two separate charts instead.
- **Area charts for comparison**: Stacked areas obscure individual trends. Use multiple lines.

---

## 2. CHART DESIGN PRINCIPLES

### Data-Ink Ratio
Maximize the ratio of ink used to display data vs ink used for decoration:
- Remove chart borders and background fills
- Remove or lighten gridlines (use light gray, not black)
- Remove redundant labels (if the axis shows values, don't also label each bar)
- Never use 3D effects, bevels, or drop shadows on data elements

### Labeling Hierarchy
1. **Chart title**: Clear, specific, states the insight (not just the topic)
   - BAD: "Sales by Region"
   - GOOD: "Western Region Sales Grew 23% While Others Declined"
2. **Axis labels**: Short, clear, include units
3. **Data labels**: Only when needed (few data points, or to highlight specific values)
4. **Legend**: Only when multiple series; place near the data, not in a distant corner
5. **Source/footnote**: Small, bottom-left, lighter color

### Grid & Axis Rules
- Y-axis: Start at 0 for bar charts (truncating distorts comparison)
- Y-axis: Can start at non-zero for line charts IF clearly labeled
- Gridlines: Horizontal only (usually). Light gray. Remove axis line if gridlines present.
- Tick marks: 4-6 on each axis. Round numbers. Don't over-label.

### Annotation
The most powerful data viz technique: **annotate the insight directly on the chart.**
```svg
<!-- Annotation example -->
<g class="annotation" transform="translate(200, 80)">
  <line x1="-30" y1="20" x2="0" y2="0" stroke="#6b7280" stroke-width="1"/>
  <text x="-35" y="30" font-size="11" fill="#374151" text-anchor="end">
    Peak: 1,240 users
  </text>
</g>
```

---

## 3. COLOR FOR DATA

### Sequential Palette (low → high)
For continuous data (temperature, density, magnitude):
```
Light → Dark single hue:
#f0f9ff → #bae6fd → #7dd3fc → #38bdf8 → #0ea5e9 → #0284c7 → #0369a1 → #075985
```

### Diverging Palette (negative ← neutral → positive)
For data with a meaningful midpoint (profit/loss, sentiment, deviation):
```
Red ← Gray → Blue:
#dc2626 → #f87171 → #fca5a5 → #e5e7eb → #93c5fd → #60a5fa → #2563eb
```

### Categorical Palette (distinct categories)
For nominal data (regions, product lines, teams):
```
Maximum 6-8 colors. Beyond that, use other encoding (shape, pattern).
#3b82f6  (Blue)
#ef4444  (Red)
#22c55e  (Green)
#f59e0b  (Amber)
#8b5cf6  (Purple)
#ec4899  (Pink)
#06b6d4  (Cyan)
#f97316  (Orange)
```

### Color Accessibility for Data
- Never use red/green alone (8% of men are red-green colorblind)
- Pair color with shape, pattern, or direct labels
- Test with colorblind simulators
- Use blue-orange as a safe two-color default instead of red-green

---

## 4. CHART.JS PATTERNS

### Setup Template
```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<canvas id="myChart" width="800" height="400"></canvas>
<script>
const ctx = document.getElementById('myChart').getContext('2d');
const chart = new Chart(ctx, {
  type: 'bar', // or 'line', 'doughnut', 'scatter', 'radar', 'polarArea'
  data: {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    datasets: [{
      label: 'Revenue',
      data: [12, 19, 3, 5, 2, 3],
      backgroundColor: 'rgba(59, 130, 246, 0.8)',
      borderColor: 'rgb(59, 130, 246)',
      borderWidth: 1,
      borderRadius: 6,
    }]
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      title: {
        display: true,
        text: 'Monthly Revenue ($K)',
        font: { size: 16, weight: '600' },
        padding: { bottom: 20 }
      }
    },
    scales: {
      x: {
        grid: { display: false },
        border: { display: false },
        ticks: { font: { size: 12 } }
      },
      y: {
        grid: { color: 'rgba(0,0,0,0.05)' },
        border: { display: false },
        ticks: { font: { size: 12 } },
        beginAtZero: true
      }
    }
  }
});
</script>
```

### Styled Line Chart
```javascript
{
  type: 'line',
  data: {
    labels: [...],
    datasets: [{
      data: [...],
      borderColor: '#3b82f6',
      backgroundColor: 'rgba(59, 130, 246, 0.05)',
      fill: true,
      tension: 0.4,        // Smooth curves
      pointRadius: 0,       // Hide points by default
      pointHoverRadius: 6,  // Show on hover
      borderWidth: 2.5,
    }]
  }
}
```

### Styled Doughnut Chart
```javascript
{
  type: 'doughnut',
  data: {
    labels: ['Category A', 'Category B', 'Category C'],
    datasets: [{
      data: [55, 30, 15],
      backgroundColor: ['#3b82f6', '#8b5cf6', '#e5e7eb'],
      borderWidth: 0,
      cutout: '70%',      // Inner radius (donut hole)
      borderRadius: 4,     // Rounded segments
    }]
  },
  options: {
    plugins: {
      legend: {
        position: 'bottom',
        labels: { usePointStyle: true, padding: 20 }
      }
    }
  }
}
```

---

## 5. D3.JS PATTERNS

### Minimal D3 Bar Chart
```javascript
const data = [
  { label: 'A', value: 30 },
  { label: 'B', value: 80 },
  { label: 'C', value: 45 },
  { label: 'D', value: 60 },
  { label: 'E', value: 20 },
];

const margin = { top: 20, right: 20, bottom: 30, left: 40 };
const width = 600 - margin.left - margin.right;
const height = 300 - margin.top - margin.bottom;

const svg = d3.select('#chart')
  .append('svg')
  .attr('width', width + margin.left + margin.right)
  .attr('height', height + margin.top + margin.bottom)
  .append('g')
  .attr('transform', `translate(${margin.left},${margin.top})`);

const x = d3.scaleBand().domain(data.map(d => d.label)).range([0, width]).padding(0.3);
const y = d3.scaleLinear().domain([0, d3.max(data, d => d.value)]).nice().range([height, 0]);

// Bars
svg.selectAll('rect')
  .data(data).enter().append('rect')
  .attr('x', d => x(d.label))
  .attr('y', d => y(d.value))
  .attr('width', x.bandwidth())
  .attr('height', d => height - y(d.value))
  .attr('fill', '#3b82f6')
  .attr('rx', 4);

// Axes
svg.append('g').attr('transform', `translate(0,${height})`).call(d3.axisBottom(x));
svg.append('g').call(d3.axisLeft(y).ticks(5));
```

---

## 6. SVG CHARTS (HAND-BUILT)

### Simple SVG Bar Chart
```svg
<svg viewBox="0 0 500 300" xmlns="http://www.w3.org/2000/svg">
  <style>
    .bar { fill: #3b82f6; rx: 4; }
    .bar:hover { fill: #2563eb; }
    .label { font: 12px sans-serif; fill: #6b7280; text-anchor: middle; }
    .value { font: 11px sans-serif; fill: #374151; text-anchor: middle; font-weight: 600; }
    .grid { stroke: #f3f4f6; stroke-width: 1; }
  </style>

  <!-- Gridlines -->
  <line class="grid" x1="60" y1="40" x2="480" y2="40"/>
  <line class="grid" x1="60" y1="100" x2="480" y2="100"/>
  <line class="grid" x1="60" y1="160" x2="480" y2="160"/>
  <line class="grid" x1="60" y1="220" x2="480" y2="220"/>

  <!-- Bars (positioned manually, heights represent data) -->
  <rect class="bar" x="90" y="60" width="50" height="220"/>
  <rect class="bar" x="170" y="120" width="50" height="160"/>
  <rect class="bar" x="250" y="40" width="50" height="240"/>
  <rect class="bar" x="330" y="160" width="50" height="120"/>
  <rect class="bar" x="410" y="90" width="50" height="190"/>

  <!-- Value labels -->
  <text class="value" x="115" y="52">$240K</text>
  <text class="value" x="195" y="112">$160K</text>
  <text class="value" x="275" y="32">$280K</text>
  <text class="value" x="355" y="152">$120K</text>
  <text class="value" x="435" y="82">$190K</text>

  <!-- Category labels -->
  <text class="label" x="115" y="295">Q1</text>
  <text class="label" x="195" y="295">Q2</text>
  <text class="label" x="275" y="295">Q3</text>
  <text class="label" x="355" y="295">Q4</text>
  <text class="label" x="435" y="295">Q5</text>
</svg>
```

### SVG Donut Chart
```svg
<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
  <!-- Donut segments using stroke-dasharray on circles -->
  <!-- circumference = 2π × r = 2π × 70 ≈ 440 -->
  <circle cx="100" cy="100" r="70" fill="none" stroke="#3b82f6"
          stroke-width="25" stroke-dasharray="264 440"
          stroke-dashoffset="0" transform="rotate(-90 100 100)"/>
  <circle cx="100" cy="100" r="70" fill="none" stroke="#8b5cf6"
          stroke-width="25" stroke-dasharray="110 440"
          stroke-dashoffset="-264" transform="rotate(-90 100 100)"/>
  <circle cx="100" cy="100" r="70" fill="none" stroke="#e5e7eb"
          stroke-width="25" stroke-dasharray="66 440"
          stroke-dashoffset="-374" transform="rotate(-90 100 100)"/>
  <!-- Center label -->
  <text x="100" y="95" text-anchor="middle" font-size="28" font-weight="700" fill="#1f2937">72%</text>
  <text x="100" y="115" text-anchor="middle" font-size="11" fill="#6b7280">Complete</text>
</svg>
```

---

## 7. INFOGRAPHIC DESIGN

### Infographic Structure
1. **Header**: Bold title + subtitle + visual hook
2. **Key Stat**: One huge number that anchors the story
3. **Flow/Narrative**: 3-5 sections that tell a sequential story
4. **Comparison**: Visual comparison (before/after, this vs that)
5. **Data Points**: Supporting statistics with visual treatments
6. **Conclusion/CTA**: Takeaway message
7. **Source**: Data attribution

### Infographic Design Rules
- **One column layout** for long infographics (scrolling)
- **Consistent icon style** throughout
- **Number treatments**: Make stats large, bold, colored. Supporting text small, neutral.
- **Section dividers**: Use shape, color, or whitespace to separate sections
- **Maximum 3 fonts**: Display for numbers, body for text, maybe one accent
- **Limited palette**: 2-3 colors + neutrals. Too many colors = visual chaos.

### Stat/Number Treatment
```svg
<g class="stat-block">
  <text x="0" y="0" font-size="56" font-weight="800" fill="#3b82f6" font-family="var(--font-display)">
    73%
  </text>
  <text x="0" y="24" font-size="14" fill="#6b7280" font-family="var(--font-body)">
    of users prefer dark mode
  </text>
</g>
```

---

## 8. DIAGRAM & FLOWCHART DESIGN

### Flowchart Visual Style
```css
.flow-node {
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  text-align: center;
  min-width: 140px;
}
.flow-node-process { background: #dbeafe; border: 1.5px solid #93c5fd; color: #1e40af; }
.flow-node-decision { background: #fef3c7; border: 1.5px solid #fcd34d; color: #92400e;
                       transform: rotate(45deg); /* Diamond shape */ }
.flow-node-start-end { background: #d1fae5; border: 1.5px solid #6ee7b7; color: #065f46;
                         border-radius: 999px; }
.flow-node-io { background: #ede9fe; border: 1.5px solid #c4b5fd; color: #5b21b6; }

.flow-connector {
  stroke: #9ca3af;
  stroke-width: 1.5;
  fill: none;
  marker-end: url(#arrowhead);
}
```

### Mermaid-Style Flowchart (SVG)
```svg
<svg viewBox="0 0 600 500" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#9ca3af"/>
    </marker>
  </defs>

  <!-- Start node -->
  <rect x="220" y="20" width="160" height="44" rx="22" fill="#d1fae5" stroke="#6ee7b7" stroke-width="1.5"/>
  <text x="300" y="47" text-anchor="middle" font-size="14" font-weight="500" fill="#065f46">Start</text>

  <!-- Connector -->
  <line x1="300" y1="64" x2="300" y2="100" stroke="#9ca3af" stroke-width="1.5" marker-end="url(#arrow)"/>

  <!-- Process node -->
  <rect x="200" y="100" width="200" height="50" rx="8" fill="#dbeafe" stroke="#93c5fd" stroke-width="1.5"/>
  <text x="300" y="130" text-anchor="middle" font-size="14" font-weight="500" fill="#1e40af">Process Data</text>

  <!-- More nodes and connectors follow the same pattern -->
</svg>
```

### Architecture Diagram Elements
- **Boxes**: Services, servers, databases (distinct shapes per type)
- **Arrows**: Data flow direction (labeled with protocol/method)
- **Groups**: Dashed rectangles around related services (VPC, subnet, cluster)
- **Icons**: Use simple geometric icons for service types
- **Color coding**: Different colors for different tiers (frontend, backend, data, external)
