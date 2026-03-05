# Valor UF Chile 🇨🇱

Sitio web estático y serverless que muestra el valor diario de la **Unidad de Fomento (UF)** de Chile. Incluye consulta por fecha, calculadora UF↔CLP, y API pública. Los datos se obtienen automáticamente desde el [SII](https://www.sii.cl/valores_y_fechas/uf/uf2026.htm).

## 🔗 Demo

Disponible en GitHub Pages: `https://camilo-lavado.github.io/valor-uf/`

## ✨ Funcionalidades

- **Valor del día:** muestra la UF actual con badge de estado
- **Consulta histórica:** date picker para buscar UF en cualquier fecha de 2025 y 2026
- **Calculadora:** conversión bidireccional UF↔CLP en tiempo real
- **API pública:** JSON accesible por HTTP para consumir desde otras apps

## 📁 Estructura del proyecto

```
valor-uf/
├── scraper.py                          # Scraper multi-año (2025-2026)
├── index.html                          # Frontend con consulta + calculadora
├── uf_data.json                        # Datos combinados de la UF
├── requirements.txt                    # Dependencias de Python
├── tests/
│   └── test_scraper.py                 # Tests unitarios (10 tests)
└── .github/
    └── workflows/
        └── actualizar_uf.yml           # Workflow de actualización mensual
```

## 🚀 Inicio rápido

### Requisitos

- Python 3.12+

### Instalación

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/Mac

pip install -r requirements.txt
```

### Generar datos

```bash
python scraper.py
```

Esto crea `uf_data.json` con los valores de la UF de 2025 y 2026.

### Ver el sitio localmente

```bash
python -m http.server 8000
```

Luego visita `http://localhost:8000`.

### Ejecutar tests

```bash
python -m pytest tests/ -v
```

## 📡 API — Uso desde otras apps

Los datos están disponibles como JSON estático. Una vez publicado en GitHub Pages:

```
GET https://camilo-lavado.github.io/valor-uf/uf_data.json
```

### Formato de respuesta

```json
{
    "2025-01-01": "38.079,43",
    "2025-01-02": "38.083,88",
    "2026-03-05": "39.819,01",
    "..."
}
```

Las claves son fechas en formato `YYYY-MM-DD` y los valores son strings con formato chileno (punto para miles, coma para decimales).

### Ejemplos con Postman

#### 1. Obtener todos los datos

| Campo   | Valor |
|---------|-------|
| Method  | `GET` |
| URL     | `https://camilo-lavado.github.io/valor-uf/uf_data.json` |
| Headers | Ninguno requerido |

Respuesta: JSON completo con todas las fechas disponibles.

#### 2. Filtrar una fecha específica con script de Postman

Configura la request `GET` a la URL anterior y en la pestaña **Tests** agrega:

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

#### 3. Calcular UF a pesos en Postman

En la pestaña **Tests** de tu request:

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

#### 4. Uso con cURL

```bash
# Obtener todos los datos
curl -s https://camilo-lavado.github.io/valor-uf/uf_data.json

# Obtener valor de una fecha con jq
curl -s https://camilo-lavado.github.io/valor-uf/uf_data.json | jq '.["2026-03-05"]'
```

#### 5. Uso con JavaScript (fetch)

```javascript
const response = await fetch('https://camilo-lavado.github.io/valor-uf/uf_data.json');
const data = await response.json();
console.log(data['2026-03-05']); // "39.819,01"
```

#### 6. Uso con Python (requests)

```python
import requests

data = requests.get('https://camilo-lavado.github.io/valor-uf/uf_data.json').json()
print(data['2026-03-05'])  # "39.819,01"
```

## ⚙️ Automatización con GitHub Actions

El workflow `.github/workflows/actualizar_uf.yml` ejecuta el scraper automáticamente:

- **Programado:** el día 1 de cada mes a las 00:00 UTC
- **Manual:** mediante *workflow_dispatch* desde la pestaña Actions

Los datos actualizados se commitean automáticamente al repositorio.

## 🌐 Despliegue con GitHub Pages

1. Ve a **Settings → Pages** en tu repositorio
2. En **Source**, selecciona la rama `main` y la carpeta `/ (root)`
3. Guarda y espera a que se publique

## 🔒 Seguridad

Al ser archivos estáticos servidos por GitHub Pages (CDN Fastly):

- **No hay servidor que atacar** — solo se sirve un archivo JSON
- **Rate limiting** automático por parte de GitHub
- **Límite de 100 GB/mes** de ancho de banda (~6.5M requests para este JSON)
- **Protección DDoS** incluida en la infraestructura de GitHub/Fastly

Para mayor control, se puede agregar Cloudflare como proxy (plan gratuito).

## 📄 Licencia

MIT
