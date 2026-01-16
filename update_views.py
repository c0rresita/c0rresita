import json
import os
from datetime import datetime, timedelta
from pathlib import Path

# Archivos de datos
DATA_FILE = "views_data.json"
SVG_TEMPLATE = "github-profile-animation.svg"

def load_data():
    """Carga los datos de visitas o crea un archivo nuevo"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {
        "total_views": 0,
        "daily_views": {},
        "last_update": None
    }

def save_data(data):
    """Guarda los datos de visitas"""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def increment_view():
    """Incrementa el contador de visitas"""
    data = load_data()
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Incrementar contador total
    data["total_views"] += 1
    
    # Incrementar contador diario
    if today not in data["daily_views"]:
        data["daily_views"][today] = 0
    data["daily_views"][today] += 1
    
    data["last_update"] = datetime.now().isoformat()
    save_data(data)
    return data

def get_last_30_days_data(data):
    """Obtiene datos de los últimos 30 días"""
    today = datetime.now()
    last_30_days = []
    
    for i in range(30, -1, -1):
        date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        views = data["daily_views"].get(date, 0)
        last_30_days.append(views)
    
    return last_30_days

def generate_graph_path(views_data):
    """Genera el path SVG para el gráfico"""
    if not views_data or all(v == 0 for v in views_data):
        # Si no hay datos, retorna una línea plana
        return "M 60,330 L 740,330", "M 60,330 L 740,330 L 740,330 L 60,330 Z"
    
    max_views = max(views_data) if max(views_data) > 0 else 1
    min_y = 210
    max_y = 330
    
    # Calcular posiciones
    x_start = 60
    x_end = 740
    x_step = (x_end - x_start) / (len(views_data) - 1)
    
    # Construir path para la línea
    line_path = f"M {x_start},{max_y}"
    for i, views in enumerate(views_data):
        x = x_start + (i * x_step)
        y = max_y - ((views / max_views) * (max_y - min_y))
        line_path += f" L {x},{y}"
    
    # Construir path para el área (igual que la línea pero cerrado)
    area_path = line_path + f" L {x_end},{max_y} L {x_start},{max_y} Z"
    
    return line_path, area_path

def generate_peak_points(views_data):
    """Genera círculos para los picos del gráfico"""
    if not views_data or all(v == 0 for v in views_data):
        return ""
    
    max_views = max(views_data)
    min_y = 210
    max_y = 330
    
    x_start = 60
    x_end = 740
    x_step = (x_end - x_start) / (len(views_data) - 1)
    
    # Encontrar picos (valores mayores que sus vecinos)
    peaks = []
    for i in range(1, len(views_data) - 1):
        if views_data[i] > views_data[i-1] and views_data[i] > views_data[i+1]:
            peaks.append(i)
    
    # Incluir el punto más alto
    max_index = views_data.index(max_views)
    if max_index not in peaks:
        peaks.append(max_index)
    
    # Limitar a 4 picos máximo
    peaks = sorted(peaks, key=lambda i: views_data[i], reverse=True)[:4]
    
    points_svg = ""
    colors = ["#1a1a1a", "#B22222", "#8B0000", "#4d4d4d"]  # Negro, rojo, rojo oscuro, gris
    
    for idx, peak_i in enumerate(peaks):
        x = x_start + (peak_i * x_step)
        y = max_y - ((views_data[peak_i] / max_views) * (max_y - min_y))
        color = colors[idx % len(colors)]
        
        points_svg += f'''
  <circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{color}">
    <animate attributeName="r" values="4;6;4" dur="{2 + idx*0.3}s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="0.7;1;0.7" dur="{2 + idx*0.3}s" repeatCount="indefinite"/>
  </circle>'''
    
    return points_svg

def update_svg():
    """Actualiza el SVG con los datos reales"""
    data = load_data()
    views_data = get_last_30_days_data(data)
    
    # Calcular estadísticas
    total_views = data["total_views"]
    last_7_days = sum(views_data[-7:])
    prev_7_days = sum(views_data[-14:-7])
    weekly_change = last_7_days - prev_7_days
    peak_views = max(views_data) if views_data else 0
    
    # Generar paths del gráfico
    line_path, area_path = generate_graph_path(views_data)
    peak_points = generate_peak_points(views_data)
    
    # Calcular labels del eje Y
    max_y_label = max(views_data) if views_data else 60
    mid_y_label = max_y_label // 2
    min_y_label = 0
    
    # Leer template SVG
    with open(SVG_TEMPLATE, 'r', encoding='utf-8') as f:
        svg_content = f.read()
    
    # Reemplazar placeholders
    svg_content = svg_content.replace("{{VIEW_COUNT}}", f"{total_views:,}")
    svg_content = svg_content.replace("{{WEEKLY_CHANGE}}", str(weekly_change))
    svg_content = svg_content.replace("{{PEAK_VIEWS}}", str(peak_views))
    svg_content = svg_content.replace("{{MAX_Y}}", str(max_y_label))
    svg_content = svg_content.replace("{{MID_Y}}", str(mid_y_label))
    svg_content = svg_content.replace("{{MIN_Y}}", str(min_y_label))
    svg_content = svg_content.replace("{{GRAPH_PATH_LINE}}", line_path)
    svg_content = svg_content.replace("{{GRAPH_PATH_AREA}}", area_path)
    svg_content = svg_content.replace("{{PEAK_POINTS}}", peak_points)
    
    # Escribir SVG actualizado
    with open(SVG_TEMPLATE, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    
    print(f"✅ SVG actualizado - Total views: {total_views}, Cambio semanal: +{weekly_change}")

if __name__ == "__main__":
    # Incrementar visita
    data = increment_view()
    print(f"📊 Nueva visita registrada - Total: {data['total_views']}")
    
    # Actualizar SVG
    update_svg()
