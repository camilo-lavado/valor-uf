import requests
from bs4 import BeautifulSoup
import json

def scrape_uf():
    url = "https://www.sii.cl/valores_y_fechas/uf/uf2026.htm"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
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
                    date_str = f"2026-{month_idx:02d}-{day:02d}"
                    uf_data[date_str] = val
                    
    with open('uf_2026.json', 'w', encoding='utf-8') as f:
        json.dump(uf_data, f, indent=4)

if __name__ == "__main__":
    scrape_uf()
