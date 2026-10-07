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
| **AI tables** | The same horoscope as flat tables, plus derived data (lordships, aspects, dignity, Vimsopaka, Ashtakavarga, yogas, every dasa level to pratyantar, transits and stations, a row of facts per period, what supports and weakens each topic, and where dasa and transit overlap), so an AI assistant can read every fact without working it out. A short `AI_Brief` serves an assistant that cannot load them all. See [AI sheets](#ai-sheets-and-json) |

Nothing is stored: birth details are used for the calculation and discarded.

## Files

| File | Purpose |
|---|---|
| `astro_engine.py` | All calculations. `compute()` is the single source for every output |
| `enrich.py` | `enrich(res)`: derived facts as flat tables for AI readers. A separate step, so `compute()` and the web page are not slowed down |
| `charts.py` | Chart contents and layout shared by web page, Excel and PDF |
| `i18n.py` | Names and labels (en, ta, hi, te, kn, ml, mr, bn, and `bi` = English + Tamil) |
| `excel_generator.py` | Workbook: Summary, Vedic, Divisional Charts, KP, ALP, Dasa, Notes; charts drawn with cells. With the AI block, the `AI_` sheets (28, or 30 when past events were entered) follow Notes |
| `pdf_generator.py` | PDF with the same content; Noto fonts embedded, text shaped by HarfBuzz |
| `app.py` | Flask routes |
| `fonts/` | Noto Sans fonts (SIL Open Font License, see `fonts/OFL.txt`) |
| `tests/` | `pytest` suite: `test_engine.py` (engine and reports), `test_enrich.py` (AI tables, AI sheets, JSON routes), `test_reader.py` (what schema 2 added: dasa levels, faster transits, stations, period facts, topic promise and windows, optional inputs, the brief). `golden_main.json` holds fingerprints of the seven report sheets and of the `/api/horoscope` response, made by `make_golden.py`, so a change to the old output is caught |

## API

All horoscope endpoints take the same JSON body.

```
POST /api/horoscope          -> JSON (meta, vedic, kp, alp, charts, varga_charts, varga_table, names)
                                add "ai": true to the body to also get the "ai" block
                                "ai": "brief" returns meta and the short AI_Brief table only
POST /api/download/excel     -> .xlsx (the seven report sheets, then the AI_ sheets)
POST /api/download/pdf       -> .pdf
POST /api/download/json      -> .json (meta, vedic, kp, alp and the "ai" block), named like the Excel file
                                with "ai": "brief": meta and the short AI_Brief table only (under 45 KB)
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
- `ai`: optional. On `/api/horoscope`, `true` adds the `ai` block; without it
  the response is exactly as before. `"brief"`, on `/api/horoscope` and
  `/api/download/json`, returns `meta` and `ai.brief` (the rows of `AI_Brief`)
  and nothing else: small enough to paste into a chat.

Optional inputs for the AI block. A reading needs none of them; they are what
only the user knows. They change nothing unless the AI block is asked for,
they are checked (a bad value is HTTP 400) and nothing is stored.

```json
{
  "tobUncertaintyMin": 5,
  "life": {
    "marital_status": "married", "marriage_year": 2012,
    "children_count": 1, "first_child_birth_year": 2014,
    "elder_siblings": 0, "younger_siblings": 1,
    "work_type": "employed", "lives_abroad": false,
    "events": [{"type": "marriage", "year": 2012}, {"type": "job change", "year": 2023}]
  }
}
```

- `tobUncertaintyMin`: 0 to 120, how many minutes the birth time may be off.
  It is repeated in `AI_Facts` and sets `lagna_uncertain_for_stated_accuracy`
  in `AI_VargaLagnas`.
- `life`: every field optional. `marital_status`: `single`, `married`, `other`.
  `work_type`: `employed`, `self-employed`, `business`, `student`, `homemaker`,
  `retired`, `not working`. Counts are 0 to 20. `events`: at most 10, each a
  `type` (`marriage`, `child born`, `job change`, `own business started`,
  `moved abroad`, `returned from abroad`, `home bought`, `higher study`) and a
  `year` between the birth year and the report year. They go into
  `AI_LifeFacts` and `AI_LifeEvents` as entered, and `AI_EventCheck` shows the
  periods and transits of each event's year.

## AI sheets and JSON

The picture sheets are laid out for a human eye. For an AI assistant the
workbook also carries sheets named `AI_...`, placed after Notes, and the
same tables are in the `ai` block of the JSON file. Give either file to an
assistant and it can read the facts directly. The schema is
`horoscopegen-ai/2`; it only adds to schema 1 (new sheets, and new columns at
the end of old sheets).

An assistant should start with `AI_Brief`, judge a period from its row in
`AI_PeriodFacts`, take the promise of a topic from `AI_TopicPromise` and the
timing from `AI_TopicWindows`. Counts, scores and windows are rule-based aids,
not predictions.

Rules the AI sheets keep:

- one table per sheet from A1, header in row 1, one fact per cell;
- values only: no merged cells, no formulas, no colour that carries meaning;
- always in English (the engine's names for signs, nakshatras and planets),
  whatever language the report is in;
- angles as decimal degrees (6 places) with a text column beside them; dates
  as real Excel dates, shown as `yyyy-mm-dd hh:mm:ss`;
- `*_local` moments are clock time at the birth place with the UTC offset in
  force at birth; `*_utc` moments are UTC;
- no status column: periods carry start and end dates to compare with today;
- an empty cell means "does not apply" or "could not be computed", and
  `AI_ReadMe` says which;
- nothing about length of life.

| Sheet | One row per | Holds |
|---|---|---|
| `AI_ReadMe` | line | What the sheets are, defaults (whole-sign houses, the Vedic dasa table), warnings (KP is separate; status labels go stale), what is not in the file, every rule, every column |
| `AI_Brief` | line | Start here: a short copy of the other sheets (birth facts, planets, houses, yogas, what runs on the report date, and per topic the promise counts and next windows); each line names its source sheet |
| `AI_Facts` | key | Birth details and settings as separate values |
| `AI_LifeFacts` | key | What the user chose to enter about their life, or `not given`; not computed |
| `AI_LifeEvents` | event | Past events the user entered (kind and year); present only when one was entered |
| `AI_Planets` | lagna, planet, Mandi | Position, the three house systems side by side, dignity, lordship, aspects, conjunctions, strength, bindus |
| `AI_Houses` | house | Sign, lord, occupants, aspects, bindus, KP cusp |
| `AI_Pairs` | pair of planets | Conjunction, separation, aspect, exchange, friendship each way, planetary war |
| `AI_Vargas` | point x chart | Sign, degree inside the chart, house, dignity in each of the 16 charts |
| `AI_VargaLagnas` | chart | Lagna, its lord, and how many seconds the birth time can move before that lagna changes |
| `AI_Strength` | planet | Four Vimsopaka figures and the dignity points behind them |
| `AI_Ashtakavarga` | planet x sign | Bhinnashtakavarga and Sarvashtakavarga by sign and house |
| `AI_Yogas` | yoga checked | Found, cancelled or not found, with the rule as applied |
| `AI_DasaPeriods` | dasa | 1st level: dates and the state of the dasa lord |
| `AI_Dasa` | bhukti | Dates and the state of the dasa lord and bhukti lord |
| `AI_Antaram` | antaram | 3rd level for the whole life |
| `AI_Pratyantar` | pratyantar | 4th level, from 1 year before the report date to 10 years after |
| `AI_PeriodFacts` | bhukti, antaram | Every fact about the lord of that period on one row: lordship, placement, dignity, strength, D9 and D10 dignity, star lord, relation to the dasa lord, tara, yogas, topics it is tied to |
| `AI_Transits` | sign entry | Saturn, Jupiter, Rahu, Ketu from birth to 10 years ahead, with houses, bindus, labels, the houses aspected and the natal points touched |
| `AI_TransitsFast` | sign entry | Mars (2 years back to 10 ahead) and the Sun, Mercury, Venus (1 back to 2 ahead), same columns |
| `AI_Stations` | station | Retrograde and direct stations of Mars, Jupiter, Saturn, 1 year back to 10 ahead |
| `AI_TransitNow` | planet | Positions on the report date |
| `AI_SadeSati` | span | Sade sati cycles and phases with retrograde breaks |
| `AI_DoubleTransit` | span | Houses reached by both Jupiter and Saturn (modern method) |
| `AI_TopicMap` | topic | Where to look for each common question |
| `AI_TopicFacts` | topic x fact | The facts of this chart for each topic |
| `AI_TopicPromise` | topic x test | The fixed tests that support or weaken a topic in this chart, with the two counts; rule-based, not a prediction |
| `AI_TopicScores` | bhukti x topic | Rule-based relevance, not a prediction, with its rank within the topic |
| `AI_TopicWindows` | topic x span | Spans of the next 10 years in which two or more of the layers bhukti, antaram, Jupiter and Saturn agree; rule-based overlap, not a prediction |
| `AI_EventCheck` | event x bhukti | For each past event entered: the bhuktis of that year, their score for the matching topic, and where Jupiter and Saturn were; present only when an event was entered |

In Python: `ai = enrich(compute(...), extras=None)`; `ai['tables'][sheet]` is a list of
rows keyed by column name, `ai['columns'][sheet]` explains the columns and
`ai['rules']` lists the rule and variant used for each derived value (also
printed on the Notes sheet). `generate_excel(res, lang, ai=ai)` adds the
sheets; without `ai` the workbook is the seven report sheets only. `extras`
carries the optional inputs (`tob_uncertainty_min`, `coordinates_source`,
`life`); `enrich.clean_extras` checks them.

## Run locally

```bash
pip install -r requirements.txt
python app.py                 # http://localhost:5000
pip install pytest pandas     # test-only; pandas is used by one test and is not needed to run the API
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
- AI tables: the rule and the variant behind each derived value are listed in
  `enrich.RULES`, on the Notes sheet and in `AI_ReadMe`. Transit sign entries
  are found by stepping (never further than the body can travel towards a
  sign boundary, one day at most near a boundary) and bisecting; the tests
  compare this with a plain one-day search for 1900-2100.
- Stations (`AI_Stations`) are the moments the daily motion in longitude is
  zero. The motion changes slowly there, so read a station as a date; the
  tests find the same moments as the extremes of the longitude itself.
- `AI_TopicPromise` and `AI_TopicWindows` apply fixed lists of tests, the same
  for every chart; the tests recompute both from the other sheets alone.

## Licence

This project uses the Swiss Ephemeris under the GNU Affero General Public
License (AGPL-3.0), so this source code is published under the same licence.
See <https://www.astro.com/swisseph/> for the Swiss Ephemeris terms.
