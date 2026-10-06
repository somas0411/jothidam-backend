# HoroscopeGen backend

Flask API behind [horoscopegen.in](https://www.horoscopegen.in). It computes a
horoscope with the Swiss Ephemeris and returns it as JSON, an Excel workbook
or a PDF. Three systems are produced from one birth moment:

| System | What is computed |
|---|---|
| **Vedic** | D1 Rasi, D9 Navamsa, Sripati Bhava, planet table (rasi, nakshatra, pada, lords, retrograde, combust, dignity), Mandi, birth panchangam, Vimshottari dasa / bhukti / antaram |
| **Divisional** | The 16 charts of the Shodasavarga (D1 to D60, Parashara's rules) for the lagna, the planets and Mandi |
| **KP** | KP ayanamsha, Placidus cusps, star / sub / sub-sub lords for cusps and planets, 4-level significators, ruling planets, Vimshottari |
| **ALP** | Akshaya Lagna: birth lagna progressed 30° per 10 years, with rasi and nakshatra-pada period tables |

Nothing is stored: birth details are used for the calculation and discarded.

## Files

| File | Purpose |
|---|---|
| `astro_engine.py` | All calculations. `compute()` is the single source for every output |
| `charts.py` | Chart contents and layout shared by web page, Excel and PDF |
| `i18n.py` | Names and labels (en, ta, hi, te, kn, ml, mr, bn, and `bi` = English + Tamil) |
| `excel_generator.py` | Workbook: Summary, Vedic, Divisional Charts, KP, ALP, Dasa, Notes; charts drawn with cells |
| `pdf_generator.py` | PDF with the same content; Noto fonts embedded, text shaped by HarfBuzz |
| `app.py` | Flask routes |
| `fonts/` | Noto Sans fonts (SIL Open Font License, see `fonts/OFL.txt`) |
| `tests/` | `pytest` suite |

## API

All horoscope endpoints take the same JSON body.

```
POST /api/horoscope          -> JSON (meta, vedic, kp, alp, charts, varga_charts, varga_table, names)
POST /api/download/excel     -> .xlsx
POST /api/download/pdf       -> .pdf
GET  /api/geocode?q=Chennai  -> place candidates with latitude, longitude, time zone
GET  /health
```

```json
{
  "name": "Sample Native", "dob": "1998-03-06", "tob": "01:37", "pob": "Delhi",
  "lat": 28.6139, "lon": 77.2090,
  "tz": "Asia/Kolkata", "utcOffset": null,
  "ayanamsha": "lahiri", "node": "mean", "gender": "",
  "lang": "en", "chartStyle": "south"
}
```

- `lat` / `lon`: decimal degrees, east and north positive. If omitted, `pob` is
  looked up; an unknown place is an error (HTTP 400), never a silent default.
- `tz`: IANA zone; historical offsets are applied. If omitted it is found from
  the coordinates. `utcOffset` (hours) overrides it.
- `ayanamsha`: `lahiri`, `kp`, `raman`, `yukteshwar` (Vedic and ALP sections;
  the KP section always uses the KP ayanamsha).
- `node`: `mean` or `true`. `chartStyle`: `south` or `north`.

## Run locally

```bash
pip install -r requirements.txt
python app.py                 # http://localhost:5000
python -m pytest -q tests
```

`EXTRA_ORIGINS` (comma-separated) adds allowed CORS origins for local testing.

## Deploy (Render)

- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app` (`gunicorn.conf.py` sets the timeout)
- No environment variables are required.

## Calculation notes

- Ephemeris: Swiss Ephemeris, built-in Moshier mode (no data files needed).
- Dasa and ALP year: 365.25 days.
- Sunrise / sunset: visible upper limb with standard refraction.
- Mandi: weekday ghati table (day: Sun 26, Mon 22, Tue 18, Wed 14, Thu 10, Fri 6,
  Sat 2; night: the value of the 5th weekday), scaled to the actual day or night
  length; its longitude is the lagna rising at that moment. Gulika is not computed.
- Rahu / Ketu own no houses in KP significators; the nodes' sign lord and
  conjunct planets are listed separately.
- Every report carries a Notes page stating the settings used.

## Licence

This project uses the Swiss Ephemeris under the GNU Affero General Public
License (AGPL-3.0), so this source code is published under the same licence.
See <https://www.astro.com/swisseph/> for the Swiss Ephemeris terms.
