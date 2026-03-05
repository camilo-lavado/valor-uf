import json
import os
import pytest
from unittest.mock import patch, MagicMock
from scraper import scrape_uf, scrape_all_years


SAMPLE_HTML = """
<html>
<body>
<table id="table_export">
<thead><tr><th>Día</th><th>Enero</th><th>Febrero</th></tr></thead>
<tbody>
<tr><th>1</th><td>39.731,79</td><td>39.703,50</td></tr>
<tr><th>2</th><td>39.735,63</td><td>39.700,94</td></tr>
<tr><th>15</th><td>39.747,12</td><td>39.716,95</td></tr>
<tr><th>31</th><td>39.706,07</td><td></td></tr>
</tbody>
</table>
</body>
</html>
"""

SAMPLE_HTML_NO_TABLE = """
<html><body><p>Sin datos</p></body></html>
"""

OUTPUT_FILE = "uf_data.json"


@pytest.fixture(autouse=True)
def cleanup_json():
    yield
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)


@patch("scraper.requests.get")
def test_scrape_uf_returns_dict(mock_get):
    mock_response = MagicMock()
    mock_response.text = SAMPLE_HTML
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    result = scrape_uf(2026)

    assert isinstance(result, dict)
    assert len(result) == 7


@patch("scraper.requests.get")
def test_scrape_uf_uses_correct_year(mock_get):
    mock_response = MagicMock()
    mock_response.text = SAMPLE_HTML
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    result = scrape_uf(2025)

    assert all(k.startswith("2025-") for k in result)


@patch("scraper.requests.get")
def test_scrape_uf_extracts_correct_dates(mock_get):
    mock_response = MagicMock()
    mock_response.text = SAMPLE_HTML
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    result = scrape_uf(2026)

    assert "2026-01-01" in result
    assert "2026-02-01" in result
    assert "2026-01-15" in result
    assert "2026-02-15" in result
    assert "2026-01-31" in result


@patch("scraper.requests.get")
def test_scrape_uf_extracts_correct_values(mock_get):
    mock_response = MagicMock()
    mock_response.text = SAMPLE_HTML
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    result = scrape_uf(2026)

    assert result["2026-01-01"] == "39.731,79"
    assert result["2026-02-02"] == "39.700,94"
    assert result["2026-01-31"] == "39.706,07"


@patch("scraper.requests.get")
def test_scrape_uf_skips_empty_cells(mock_get):
    mock_response = MagicMock()
    mock_response.text = SAMPLE_HTML
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    result = scrape_uf(2026)

    assert "2026-02-31" not in result


@patch("scraper.requests.get")
def test_scrape_uf_no_table(mock_get):
    mock_response = MagicMock()
    mock_response.text = SAMPLE_HTML_NO_TABLE
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    result = scrape_uf(2026)

    assert result == {}


@patch("scraper.requests.get")
def test_scrape_uf_http_error(mock_get):
    mock_get.side_effect = Exception("Connection error")

    with pytest.raises(Exception, match="Connection error"):
        scrape_uf(2026)


@patch("scraper.requests.get")
def test_scrape_all_years_combines_data(mock_get):
    mock_response = MagicMock()
    mock_response.text = SAMPLE_HTML
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    result = scrape_all_years()

    assert any(k.startswith("2025-") for k in result)
    assert any(k.startswith("2026-") for k in result)
    assert os.path.exists(OUTPUT_FILE)


@patch("scraper.requests.get")
def test_scrape_all_years_creates_valid_json(mock_get):
    mock_response = MagicMock()
    mock_response.text = SAMPLE_HTML
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    scrape_all_years()

    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert isinstance(data, dict)
    for key in data:
        parts = key.split("-")
        assert len(parts) == 3
        assert parts[0] in ("2025", "2026")
        assert 1 <= int(parts[1]) <= 12
        assert 1 <= int(parts[2]) <= 31


@patch("scraper.requests.get")
def test_scrape_all_years_calls_both_years(mock_get):
    mock_response = MagicMock()
    mock_response.text = SAMPLE_HTML
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    scrape_all_years()

    urls_called = [call[0][0] for call in mock_get.call_args_list]
    assert "https://www.sii.cl/valores_y_fechas/uf/uf2025.htm" in urls_called
    assert "https://www.sii.cl/valores_y_fechas/uf/uf2026.htm" in urls_called
