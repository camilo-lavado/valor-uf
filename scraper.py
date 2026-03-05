import requests
from bs4 import BeautifulSoup
import json

YEARS = [2025, 2026]

def scrape_uf(year):
    url = f"https://www.sii.cl/valores_y_fechas/uf/uf{year}.htm"
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
                    date_str = f"{year}-{month_idx:02d}-{day:02d}"
                    uf_data[date_str] = val

    return uf_data

def scrape_all_years():
    all_data = {}
    for year in YEARS:
        year_data = scrape_uf(year)
        all_data.update(year_data)

    with open('uf_data.json', 'w', encoding='utf-8') as f:
        json.dump(all_data, f, indent=4)

    return all_data

if __name__ == "__main__":
    scrape_all_years()
