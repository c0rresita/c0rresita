from flask import Flask, Response, send_file
from flask_cors import CORS
import json
import os
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

DATA_FILE = "views_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {"total_views": 0, "daily_views": {}, "last_update": None}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def increment_view():
    data = load_data()
    today = datetime.now().strftime("%Y-%m-%d")
    data["total_views"] += 1
    if today not in data["daily_views"]:
        data["daily_views"][today] = 0
    data["daily_views"][today] += 1
    data["last_update"] = datetime.now().isoformat()
    save_data(data)
    return data

def get_last_30_days_data(data):
    today = datetime.now()
    last_30_days = []
    for i in range(30, -1, -1):
        date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        views = data["daily_views"].get(date, 0)
        last_30_days.append(views)
    return last_30_days

def generate_graph_path(views_data):
    if not views_data or all(v == 0 for v in views_data):
        return "M 60,330 L 740,330", "M 60,330 L 740,330 L 740,330 L 60,330 Z"
    
    max_views = max(views_data) if max(views_data) > 0 else 1
    min_y = 210
    max_y = 330
    x_start = 60
    x_end = 740
    x_step = (x_end - x_start) / (len(views_data) - 1)
    
    line_path = f"M {x_start},{max_y}"
    for i, views in enumerate(views_data):
        x = x_start + (i * x_step)
        y = max_y - ((views / max_views) * (max_y - min_y))
        line_path += f" L {x},{y}"
    
    area_path = line_path + f" L {x_end},{max_y} L {x_start},{max_y} Z"
    return line_path, area_path

def generate_peak_points(views_data):
    if not views_data or all(v == 0 for v in views_data):
        return ""
    
    max_views = max(views_data)
    min_y = 210
    max_y = 330
    x_start = 60
    x_end = 740
    x_step = (x_end - x_start) / (len(views_data) - 1)
    
    peaks = []
    for i in range(1, len(views_data) - 1):
        if views_data[i] > views_data[i-1] and views_data[i] > views_data[i+1]:
            peaks.append(i)
    
    max_index = views_data.index(max_views)
    if max_index not in peaks:
        peaks.append(max_index)
    
    peaks = sorted(peaks, key=lambda i: views_data[i], reverse=True)[:4]
    
    points_svg = ""
    colors = ["#1a1a1a", "#B22222", "#8B0000", "#4d4d4d"]
    
    for idx, peak_i in enumerate(peaks):
        x = x_start + (peak_i * x_step)
        y = max_y - ((views_data[peak_i] / max_views) * (max_y - min_y))
        color = colors[idx % len(colors)]
        points_svg += f'\n  <circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{color}"><animate attributeName="r" values="4;6;4" dur="{2 + idx*0.3}s" repeatCount="indefinite"/><animate attributeName="opacity" values="0.7;1;0.7" dur="{2 + idx*0.3}s" repeatCount="indefinite"/></circle>'
    
    return points_svg

@app.route('/view-counter.svg')
def view_counter():
    # Incrementar contador
    data = increment_view()
    views_data = get_last_30_days_data(data)
    
    # Calcular estadísticas
    total_views = data["total_views"]
    last_7_days = sum(views_data[-7:])
    prev_7_days = sum(views_data[-14:-7])
    weekly_change = last_7_days - prev_7_days
    peak_views = max(views_data) if views_data else 0
    
    # Generar paths
    line_path, area_path = generate_graph_path(views_data)
    peak_points = generate_peak_points(views_data)
    
    # Labels eje Y
    max_y_label = max(views_data) if views_data else 60
    mid_y_label = max_y_label // 2
    
    # Generar SVG
    svg = f'''<svg width="800" height="400" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="graphGradient" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#8B0000;stop-opacity:0.6"/>
      <stop offset="100%" style="stop-color:#450000;stop-opacity:0.1"/>
    </linearGradient>
    <linearGradient id="lineGradient" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#8B0000;stop-opacity:1"/>
      <stop offset="50%" style="stop-color:#B22222;stop-opacity:1">
        <animate attributeName="offset" values="0.3;0.7;0.3" dur="3s" repeatCount="indefinite"/>
      </stop>
      <stop offset="100%" style="stop-color:#8B0000;stop-opacity:1"/>
    </linearGradient>
    <filter id="shadow">
      <feDropShadow dx="0" dy="2" stdDeviation="4" flood-opacity="0.3"/>
    </filter>
  </defs>

  <rect x="20" y="20" width="760" height="360" rx="10" fill="none" stroke="#333333" stroke-width="1" opacity="0.5"/>
  
  <text x="400" y="140" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="72" font-weight="bold" fill="#1a1a1a" text-anchor="middle">{total_views:,}</text>
  
  <text x="400" y="170" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="14" fill="#8B0000" text-anchor="middle">↗ +{weekly_change} this week</text>
  
  <line x1="60" y1="200" x2="740" y2="200" stroke="#333333" stroke-width="1"/>
  
  <text x="60" y="225" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="14" font-weight="500" fill="#4d4d4d">Last 30 Days Activity</text>
  
  <g opacity="0.2">
    <line x1="60" y1="250" x2="740" y2="250" stroke="#444444" stroke-width="1"/>
    <line x1="60" y1="290" x2="740" y2="290" stroke="#444444" stroke-width="1"/>
    <line x1="60" y1="330" x2="740" y2="330" stroke="#444444" stroke-width="1"/>
  </g>
  
  <text x="50" y="254" font-family="monospace" font-size="11" fill="#4d4d4d" text-anchor="end">{max_y_label}</text>
  <text x="50" y="294" font-family="monospace" font-size="11" fill="#4d4d4d" text-anchor="end">{mid_y_label}</text>
  <text x="50" y="334" font-family="monospace" font-size="11" fill="#4d4d4d" text-anchor="end">0</text>
  
  <path d="{area_path}" fill="url(#graphGradient)" opacity="0.5"/>
  <path d="{line_path}" fill="none" stroke="url(#lineGradient)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" filter="url(#shadow)"/>
  {peak_points}
  
  <text x="60" y="355" font-family="monospace" font-size="10" fill="#4d4d4d">30d ago</text>
  <text x="350" y="355" font-family="monospace" font-size="10" fill="#4d4d4d" text-anchor="middle">15d ago</text>
  <text x="720" y="355" font-family="monospace" font-size="10" fill="#4d4d4d" text-anchor="end">Today</text>
  
  <g transform="translate(580, 60)">
    <text x="0" y="0" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="12" fill="#4d4d4d">Peak: <tspan fill="#B22222" font-weight="600">{peak_views} views/day</tspan></text>
  </g>
</svg>'''
    
    return Response(svg, mimetype='image/svg+xml', headers={
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
    })

@app.route('/')
def index():
    return "View Counter API - Use /view-counter.svg"

if __name__ == '__main__':
    app.run(debug=True, port=5000)
