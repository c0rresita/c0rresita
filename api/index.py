from flask import Flask, Response
from datetime import datetime, timedelta
import os

app = Flask(__name__)

# Usamos variable de entorno para persistencia (Vercel KV o similar)
# Por ahora usamos contador temporal
counter = {"views": 0, "daily": {}}

def get_views_data():
    """Simula obtener datos - en producción usar Vercel KV o DB"""
    today = datetime.now().strftime("%Y-%m-%d")
    
    counter["views"] += 1
    if today not in counter["daily"]:
        counter["daily"][today] = 0
    counter["daily"][today] += 1
    
    # Últimos 30 días (simulado)
    last_30 = []
    for i in range(30, -1, -1):
        date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        views = counter["daily"].get(date, 0)
        last_30.append(views)
    
    return counter["views"], last_30

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

@app.route('/view-counter.svg')
@app.route('/api/view-counter.svg')
@app.route('/')
def view_counter():
    total_views, views_data = get_views_data()
    
    last_7 = sum(views_data[-7:])
    prev_7 = sum(views_data[-14:-7])
    weekly_change = last_7 - prev_7
    peak_views = max(views_data) if views_data else 0
    
    line_path, area_path = generate_graph_path(views_data)
    
    max_y_label = max(views_data) if views_data else 60
    mid_y_label = max_y_label // 2
    
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
  
  <text x="400" y="140" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" 
        font-size="72" font-weight="bold" fill="#1a1a1a" text-anchor="middle">
    {total_views:,}
  </text>
  
  <text x="400" y="170" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" 
        font-size="14" fill="#8B0000" text-anchor="middle">
    ↗ +{weekly_change} this week
  </text>
  
  <line x1="60" y1="200" x2="740" y2="200" stroke="#333333" stroke-width="1"/>
  
  <text x="60" y="225" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" 
        font-size="14" font-weight="500" fill="#4d4d4d">
    Last 30 Days Activity
  </text>
  
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
  
  <text x="60" y="355" font-family="monospace" font-size="10" fill="#4d4d4d">30d ago</text>
  <text x="350" y="355" font-family="monospace" font-size="10" fill="#4d4d4d" text-anchor="middle">15d ago</text>
  <text x="720" y="355" font-family="monospace" font-size="10" fill="#4d4d4d" text-anchor="end">Today</text>
  
  <g transform="translate(580, 60)">
    <text x="0" y="0" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" 
          font-size="12" fill="#4d4d4d">Peak: 
      <tspan fill="#B22222" font-weight="600">{peak_views} views/day</tspan>
    </text>
  </g>
</svg>'''
    
    return Response(svg, mimetype='image/svg+xml', headers={
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
    })
