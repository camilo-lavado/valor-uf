# Valor UF Chile 🇨🇱

[![Actualizar UF](https://github.com/camilo-lavado/valor-uf/actions/workflows/actualizar_uf.yml/badge.svg)](https://github.com/camilo-lavado/valor-uf/actions/workflows/actualizar_uf.yml)

Sitio web estático y serverless que muestra el valor diario de la **Unidad de Fomento (UF)** de Chile. Incluye consulta por fecha (2025–2026), calculadora UF↔CLP, y API pública JSON. Los datos se obtienen automáticamente desde el [Servicio de Impuestos Internos (SII)](https://www.sii.cl/valores_y_fechas/uf/uf2026.htm).

## 🔗 Demo

👉 **[https://camilo-lavado.github.io/valor-uf/](https://camilo-lavado.github.io/valor-uf/)**

## ✨ Funcionalidades

| Feature | Descripción |
|---------|-------------|
| **📊 Valor del día** | Muestra la UF actual con badge de estado, forzando zona horaria Chile (`America/Santiago`) |
| **📅 Consulta histórica** | Date picker para buscar la UF en cualquier fecha de 2025 y 2026 |
| **🧮 Calculadora** | Conversión bidireccional UF↔CLP en tiempo real |
| **📡 API pública** | JSON estático accesible por HTTP — sin backend, sin autenticación |
| **🔄 Actualización diaria** | GitHub Actions ejecuta el scraper todos los días a las 12:00 UTC |
| **🛡️ Resiliencia** | Retry con backoff exponencial y manejo de bloqueos WAF del SII |

## 📁 Estructura del proyecto

```
valor-uf/
├── scraper.py                          # Scraper multi-año con retry y logging
├── index.html                          # Frontend (dark mode, date picker, calculadora)
├── uf_data.json                        # Datos combinados 2025-2026 (~433 registros)
├── requirements.txt                    # Dependencias Python
├── tests/
│   └── test_scraper.py                 # 12 tests unitarios
└── .github/
    └── workflows/
        └── actualizar_uf.yml           # Workflow de actualización diaria
```

## 🚀 Inicio rápido

### Requisitos

- Python 3.12+

### Instalación

```bash
git clone https://github.com/camilo-lavado/valor-uf.git
cd valor-uf

python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/Mac

pip install -r requirements.txt
```

### Generar datos

```bash
python scraper.py
```

El scraper descarga los valores de la UF de 2025 y 2026 desde el SII y los guarda en `uf_data.json`. Incluye:

- **3 reintentos** con backoff exponencial (10s, 20s, 30s)
- **Manejo de WAF** del SII (HTTP 403, 429, 503)
- **Timeout** de 30 segundos por request
- **Logging** detallado para diagnóstico

### Ver el sitio localmente

```bash
python -m http.server 8000
```

Abre `http://localhost:8000` en tu navegador.

### Ejecutar tests

```bash
python -m pytest tests/ -v
```

12 tests cubriendo: extracción de datos, celdas vacías, tabla inexistente, errores HTTP, reintentos por WAF, y validación de formato JSON.

---

## 📡 API — Uso desde otras apps

Los datos están disponibles como **JSON estático público**. No se requiere autenticación ni API key.

### Endpoint

```
GET https://camilo-lavado.github.io/valor-uf/uf_data.json
```

### Formato de respuesta

```json
{
    "2025-01-01": "38.079,43",
    "2025-06-15": "39.227,86",
    "2026-03-05": "39.819,01"
}
```

- **Claves:** fechas en formato `YYYY-MM-DD`
- **Valores:** strings con formato numérico chileno (`.` miles, `,` decimales)
- **Cobertura:** todas las fechas con dato publicado por el SII entre 2025 y 2026

### Parsear el valor a número

El formato chileno necesita transformación antes de operar matemáticamente:

```
"39.819,01" → quitar puntos → "39819,01" → coma a punto → 39819.01
```

---

### Ejemplos de uso

#### Postman — Obtener todos los datos

| Campo   | Valor |
|---------|-------|
| Method  | `GET` |
| URL     | `https://camilo-lavado.github.io/valor-uf/uf_data.json` |
| Headers | Ninguno requerido |

#### Postman — Filtrar una fecha con script

En la pestaña **Tests** de tu request:

```javascript
const data = pm.response.json();
const fecha = "2026-03-05";
const valor = data[fecha];

pm.test(`UF para ${fecha}`, function () {
    pm.expect(valor).to.exist;
    console.log(`UF ${fecha}: $${valor}`);
});

pm.environment.set("uf_valor", valor);
```

#### Postman — Calcular UF a pesos

```javascript
const data = pm.response.json();
const fecha = "2026-03-05";
const ufStr = data[fecha];

if (ufStr) {
    const ufNumerico = parseFloat(ufStr.replace(/\./g, '').replace(',', '.'));
    const montoUF = 10;
    const totalCLP = Math.round(montoUF * ufNumerico);

    console.log(`${montoUF} UF = $${totalCLP.toLocaleString('es-CL')} CLP`);

    pm.test("Conversión UF a CLP", function () {
        pm.expect(totalCLP).to.be.above(0);
    });
}
```

#### cURL

```bash
# Todos los datos
curl -s https://camilo-lavado.github.io/valor-uf/uf_data.json

# Valor de una fecha específica (requiere jq)
curl -s https://camilo-lavado.github.io/valor-uf/uf_data.json | jq '.["2026-03-05"]'

# Listar todas las fechas disponibles
curl -s https://camilo-lavado.github.io/valor-uf/uf_data.json | jq 'keys[]'
```

#### JavaScript

```javascript
const response = await fetch('https://camilo-lavado.github.io/valor-uf/uf_data.json');
const data = await response.json();

const ufStr = data['2026-03-05'];
const ufNum = parseFloat(ufStr.replace(/\./g, '').replace(',', '.'));
console.log(`UF: ${ufStr} → ${ufNum}`); // UF: 39.819,01 → 39819.01
```

#### Python

```python
import requests

data = requests.get('https://camilo-lavado.github.io/valor-uf/uf_data.json').json()

uf_str = data['2026-03-05']
uf_num = float(uf_str.replace('.', '').replace(',', '.'))
print(f"UF: {uf_str} → {uf_num}")  # UF: 39.819,01 → 39819.01
```

---

## ⚙️ Automatización con GitHub Actions

El workflow ejecuta el scraper **diariamente a las 12:00 UTC** (09:00 hora Chile):

- **`0 12 * * *`** — se ejecuta todos los días para capturar actualizaciones del SII apenas se publiquen
- **`workflow_dispatch`** — ejecución manual desde la pestaña Actions

> **¿Por qué diario y no mensual?** El SII publica los valores de la UF del mes en curso (día 10 al 9 del siguiente) en los primeros días del mes. Ejecutar diariamente asegura capturar la actualización sin importar el día exacto de publicación. El proceso es gratuito e idempotente.

Los datos se commitean solo si hay cambios, con mensaje que incluye la fecha.

## 🌐 Despliegue con GitHub Pages

1. Ve a **Settings → Pages** en tu repositorio
2. En **Source**, selecciona la rama `main` y la carpeta `/ (root)`
3. Guarda — el sitio estará disponible en minutos

## 🛡️ Seguridad y rendimiento

### Scraper

| Protección | Implementación |
|------------|----------------|
| **Retry** | 3 intentos con backoff exponencial (10s, 20s, 30s) |
| **WAF** | Manejo de HTTP 403, 429, 503 |
| **Timeout** | 30 segundos por request |
| **User-Agent** | Simula navegador real (Chrome) |
| **Logging** | Registro completo de intentos y errores |

### Frontend

| Aspecto | Implementación |
|---------|----------------|
| **Timezone** | Forzado a `America/Santiago` con `Intl.DateTimeFormat` |
| **Hosting** | CDN global de GitHub Pages (Fastly) |
| **DDoS** | Protección incluida en la infraestructura de GitHub |
| **Rate limit** | ~6.5M requests/mes (100 GB bandwidth, ~15 KB por request) |

Para mayor control, se puede agregar **Cloudflare como proxy** (plan gratuito) con protección DDoS avanzada, analytics, y cache rules.

## 📄 Licencia

MIT
