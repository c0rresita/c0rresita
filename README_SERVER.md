# Profile View Counter con Servidor Propio 🚀

Este es tu contador de visitas personalizado que funciona como komarev - se actualiza en cada vista.

## 🌟 Características

- ✅ Contador en tiempo real (se actualiza con cada visita)
- 📊 Gráfico de los últimos 30 días
- 🎨 Diseño personalizado en negro/gris/rojo
- 🌙 Compatible con modo oscuro/claro
- 🔥 Animaciones suaves

## 🚀 Despliegue Rápido

### Opción 1: Vercel (Recomendado - Gratis)

1. Instala Vercel CLI:
```bash
npm i -g vercel
```

2. Despliega:
```bash
vercel
```

3. Sigue las instrucciones y tu servidor estará en línea en 30 segundos

### Opción 2: Railway (Gratis)

1. Visita [railway.app](https://railway.app)
2. Conecta tu repositorio de GitHub
3. Railway detectará automáticamente Flask y lo desplegará
4. Copia la URL que te dan

### Opción 3: Render (Gratis)

1. Visita [render.com](https://render.com)
2. Crea un nuevo "Web Service"
3. Conecta tu repositorio
4. Render lo desplegará automáticamente

### Opción 4: Local (Para pruebas)

```bash
cd server
pip install -r requirements.txt
python app.py
```

Accede a: `http://localhost:5000/view-counter.svg`

## 📝 Uso en GitHub

Una vez desplegado, agrega esto a tu README.md:

```markdown
![Profile Views](https://tu-servidor.vercel.app/view-counter.svg)
```

Reemplaza `tu-servidor.vercel.app` con la URL que te den.

## 🔧 Cómo Funciona

1. Cada vez que alguien visita tu perfil de GitHub
2. El navegador carga la imagen del SVG
3. El servidor recibe la petición
4. Incrementa el contador
5. Genera el SVG dinámicamente con los datos actualizados
6. Devuelve la imagen

¡Es exactamente como funciona komarev! 🎯

## 📁 Estructura

```
server/
  ├── app.py                    # Servidor Flask
  ├── requirements.txt          # Dependencias
  └── view_counter_data.json    # Base de datos (se crea automáticamente)
```

## 🎨 Personalización

Edita `app.py` para cambiar:
- Colores (#1a1a1a, #B22222, etc.)
- Tamaño del SVG (800x400)
- Animaciones
- Textos

## 🐛 Troubleshooting

**El contador no se actualiza:**
- Asegúrate de que el servidor esté corriendo
- Verifica que la URL sea correcta
- Limpia la caché del navegador (Ctrl + F5)

**Error 500:**
- Revisa los logs del servidor
- Verifica que las dependencias estén instaladas

## 📊 Datos

Los datos se guardan en `view_counter_data.json`:
```json
{
  "total_views": 100,
  "daily_views": {
    "2026-01-16": 10,
    "2026-01-15": 15
  },
  "last_update": "2026-01-16T10:30:00"
}
```

---

💡 **Tip:** El primer despliegue en Vercel es gratis y muy rápido. ¡Empieza por ahí!
