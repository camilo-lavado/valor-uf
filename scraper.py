import requests
from bs4 import BeautifulSoup
import json
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

YEARS = [2025, 2026]
MAX_RETRIES = 3
RETRY_DELAY = 10
REQUEST_TIMEOUT = 30

def scrape_uf(year):
    url = f"https://www.sii.cl/valores_y_fechas/uf/uf{year}.htm"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'es-CL,es;q=0.9',
    }

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.info(f"Intento {attempt}/{MAX_RETRIES} para {url}")
            response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            break
        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response is not None else 'N/A'
            logger.warning(f"HTTP {status} en intento {attempt}/{MAX_RETRIES}")
            if attempt == MAX_RETRIES:
                raise
            if status in (403, 429, 503):
                wait = RETRY_DELAY * attempt
                logger.info(f"Posible bloqueo WAF/rate-limit. Esperando {wait}s...")
                time.sleep(wait)
            else:
                raise
        except requests.exceptions.RequestException as e:
            logger.warning(f"Error de conexión en intento {attempt}/{MAX_RETRIES}: {e}")
            if attempt == MAX_RETRIES:
                raise
            time.sleep(RETRY_DELAY * attempt)

    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', {'id': 'table_export'})

    uf_data = {}

    if table:
        tbody = table.find('tbody')
        rows = tbody.find_all('tr')
        for row in rows:
            th = row.find('th')
            if not th:
                continue
            day_text = th.text.strip()
            if not day_text.isdigit():
                continue
            day = int(day_text)
            cols = row.find_all('td')
            for month_idx, col in enumerate(cols, start=1):
                val = col.text.strip()
                if val:
                    date_str = f"{year}-{month_idx:02d}-{day:02d}"
                    uf_data[date_str] = val

    logger.info(f"{year}: {len(uf_data)} valores extraídos")
    return uf_data

def scrape_all_years():
    all_data = {}
    for year in YEARS:
        year_data = scrape_uf(year)
        all_data.update(year_data)

    with open('uf_data.json', 'w', encoding='utf-8') as f:
        json.dump(all_data, f, indent=4)

    logger.info(f"Total: {len(all_data)} valores guardados en uf_data.json")
    return all_data

if __name__ == "__main__":
    scrape_all_years()
