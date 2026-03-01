"""
excel_generator.py — Professional Vedic Horoscope Excel Generator
Creates a formatted, colourful workbook with 4 sheets.
"""
import io
from openpyxl import Workbook
from openpyxl.styles import (PatternFill, Font, Alignment, Border, Side,
                              GradientFill)
from openpyxl.utils import get_column_letter
from openpyxl.styles.numbers import FORMAT_DATE_DDMMYY
from openpyxl.drawing.image import Image as XLImage
from datetime import date

from astro_engine import (
    get_rasi, get_deg, fmt_deg, get_nak, get_pada,
    get_rasi_name, get_nak_name, get_planet_name,
    build_bhuktis, fmt_date, lbl,
    LUCKY_NUMS, LUCKY_COLORS, get_gemstone, NAK_LORDS
)

# ── COLOUR CONSTANTS ──────────────────────────────────────────────────────────
DARK_BG   = '0D0600'
GOLD      = 'C9A03A'
GOLD_LT   = 'E8C96B'
GOLD_DIM  = '7A6020'
CREAM     = 'FFF8E8'
CREAM_D   = 'F5EDCF'
BROWN_D   = '1A0A00'
BROWN_M   = '3D2000'
WHITE     = 'FFFFFF'
CURRENT_Y = 'FFF3CD'  # yellow highlight for current dasa
PAST_G    = 'F0F0F0'
FUTURE_B  = 'EBF5FB'

P_COLORS = {
    'Sun':     'E8871A', 'Moon':    '2980B9', 'Mars':    'C0392B',
    'Mercury': '27AE60', 'Jupiter': '8B6914', 'Venus':   '8E44AD',
    'Saturn':  '5D6D7E', 'Rahu':    '2C3E50', 'Ketu':    '7F8C8D',
    'Lagna':   'E8871A',
}

def fill(hex_color):
    return PatternFill('solid', fgColor=hex_color)

def font(name='Calibri', size=10, bold=False, color=BROWN_D, italic=False):
    return Font(name=name, size=size, bold=bold, color=color, italic=italic)

def align(h='left', v='center', wrap=False):
    return Alignment(horizontal=h, vertical=v, wrap_text=wrap)

def thin_border():
    s = Side(style='thin', color='DDDDCC')
    return Border(left=s, right=s, top=s, bottom=s)

def medium_border():
    s = Side(style='medium', color=GOLD_DIM)
    return Border(left=s, right=s, top=s, bottom=s)

def set_cell(ws, row, col, value, fnt=None, aln=None, fill_=None, brd=None):
    cell = ws.cell(row=row, column=col, value=value)
    if fnt:   cell.font      = fnt
    if aln:   cell.alignment = aln
    if fill_: cell.fill      = fill_
    if brd:   cell.border    = brd
    return cell

def merge_set(ws, r1, c1, r2, c2, value, fnt=None, aln=None, fill_=None):
    ws.merge_cells(start_row=r1, start_column=c1, end_row=r2, end_column=c2)
    cell = ws.cell(row=r1, column=c1, value=value)
    if fnt:   cell.font      = fnt
    if aln:   cell.alignment = aln
    if fill_: cell.fill      = fill_
    return cell

# ── SHEET 1: SUMMARY ──────────────────────────────────────────────────────────

def build_summary_sheet(wb, data, lang):
    ws = wb.active
    ws.title = 'Summary' if lang == 'en' else ('சுருக்கம்' if lang=='ta' else 'Summary')
    ws.sheet_view.showGridLines = False

    # Column widths
    for col, w in [(1,4),(2,28),(3,28),(4,28),(5,4)]:
        ws.column_dimensions[get_column_letter(col)].width = w

    # Row 1: Header title
    ws.row_dimensions[1].height = 10
    ws.row_dimensions[2].height = 36
    merge_set(ws, 2, 1, 2, 5, f'🕉  JOTHIDAM  ·  {lbl("report_title", lang).upper()}',
              font('Calibri', 18, True, GOLD, False),
              align('center','center'),
              fill(DARK_BG))
    ws.row_dimensions[3].height = 8

    # Name
    ws.row_dimensions[4].height = 28
    merge_set(ws, 4, 2, 4, 4, data['name'],
              font('Calibri', 16, True, BROWN_D),
              align('center','center'),
              fill(GOLD))
    ws.row_dimensions[5].height = 6

    # Birth details header
    ws.row_dimensions[6].height = 20
    merge_set(ws, 6, 2, 6, 4, lbl('birth_details', lang),
              font('Calibri', 10, True, GOLD_LT),
              align('center','center'),
              fill(BROWN_M))

    details = [
        (lbl('dob',lang), data['dob']),
        (lbl('tob',lang), data['tob']),
        (lbl('pob',lang), data['pob']),
    ]
    for i, (k, v) in enumerate(details):
        r = 7 + i
        ws.row_dimensions[r].height = 18
        set_cell(ws, r, 2, k, font('Calibri', 9, False, GOLD_DIM), align('left','center'), fill(CREAM_D), thin_border())
        set_cell(ws, r, 3, v, font('Calibri', 10, True, BROWN_D), align('left','center'), fill(CREAM), thin_border())
        set_cell(ws, r, 4, '', fill_=fill(CREAM))

    # Blank row
    ws.row_dimensions[10].height = 8

    # Astro details header
    ws.row_dimensions[11].height = 20
    merge_set(ws, 11, 2, 11, 4, 'ASTROLOGICAL DETAILS',
              font('Calibri', 10, True, GOLD_LT),
              align('center','center'),
              fill(BROWN_M))

    lagna_name = get_rasi_name(data['lagna_rasi'], lang)
    rasi_name  = get_rasi_name(data['moon_rasi'],  lang)
    nak_name   = get_nak_name(data['nak_num'], lang)
    astro_rows = [
        (lbl('lagna',lang),      lagna_name),
        (lbl('janma_rasi',lang), rasi_name),
        (lbl('janma_nak',lang),  f'{nak_name} - {lbl("pada",lang)} {data["nak_pada"]}'),
        (lbl('cur_dasa',lang),   data['cur_dasa']['dasa']),
        (lbl('dasa_ends',lang),  fmt_date(data['cur_dasa']['end'])),
        (lbl('cur_bhukti',lang), data['cur_bhukti']['bhukti']),
        (lbl('bhukti_ends',lang),fmt_date(data['cur_bhukti']['end'])),
        (lbl('gemstone',lang),   get_gemstone(data['nak_lord'], lang)),
        (lbl('lucky_color',lang),LUCKY_COLORS.get(data['nak_lord'],'Gold')),
        (lbl('lucky_num',lang),  ', '.join(str(n) for n in LUCKY_NUMS.get(data['nak_lord'],[1,4,7]))),
    ]
    for i, (k, v) in enumerate(astro_rows):
        r = 12 + i
        ws.row_dimensions[r].height = 18
        bg = CREAM if i % 2 == 0 else CREAM_D
        set_cell(ws, r, 2, k, font('Calibri', 9, False, GOLD_DIM), align('left','center'), fill(bg), thin_border())
        set_cell(ws, r, 3, str(v), font('Calibri', 10, True, BROWN_D), align('left','center'), fill(bg), thin_border())
        set_cell(ws, r, 4, '', fill_=fill(bg))

    # Generated footer
    r = 12 + len(astro_rows) + 2
    ws.row_dimensions[r].height = 14
    merge_set(ws, r, 2, r, 4,
              f'Generated by Jothidam · horoscopegen.in · {date.today().strftime("%d %b %Y")}',
              font('Calibri', 8, False, GOLD_DIM, True),
              align('center','center'),
              fill(DARK_BG))

# ── SHEET 2: PLANET POSITIONS ─────────────────────────────────────────────────

def build_planets_sheet(wb, data, lang):
    ws = wb.create_sheet(lbl('planet_positions', lang)[:31])
    ws.sheet_view.showGridLines = False

    for col, w in [(1,2),(2,20),(3,20),(4,14),(5,22),(6,10),(7,10),(8,2)]:
        ws.column_dimensions[get_column_letter(col)].width = w

    ws.row_dimensions[1].height = 8
    ws.row_dimensions[2].height = 28
    merge_set(ws, 2, 2, 2, 7, lbl('planet_positions', lang),
              font('Calibri', 14, True, GOLD), align('center','center'), fill(DARK_BG))
    ws.row_dimensions[3].height = 8

    # Table header
    ws.row_dimensions[4].height = 22
    headers = [lbl('planet',lang), lbl('rasi',lang), lbl('degrees',lang),
               lbl('nakshatra',lang), lbl('pada',lang), lbl('house',lang)]
    for ci, h in enumerate(headers):
        cell = ws.cell(row=4, column=2+ci, value=h)
        cell.font      = font('Calibri', 10, True, GOLD_LT)
        cell.alignment = align('center','center')
        cell.fill      = fill(BROWN_M)
        cell.border    = thin_border()

    lagna_rasi = data['lagna_rasi']
    for ri, (pname, lon) in enumerate(data['planet_list']):
        r  = 5 + ri
        ws.row_dimensions[r].height = 20
        rasi_num   = get_rasi(lon)
        house      = ((rasi_num - lagna_rasi + 12) % 12) + 1
        nak_name   = get_nak_name(get_nak(lon), lang)
        pada       = get_pada(lon)
        rasi_name  = get_rasi_name(rasi_num, lang)
        deg_str    = fmt_deg(lon)
        pname_loc  = get_planet_name(pname, lang)
        p_hex      = P_COLORS.get(pname, BROWN_M)

        row_data = [pname_loc, rasi_name, deg_str, nak_name, str(pada), str(house)]
        for ci, val in enumerate(row_data):
            cell = ws.cell(row=r, column=2+ci, value=val)
            bg   = p_hex if ci == 0 else (CREAM if ri%2==0 else CREAM_D)
            fg   = WHITE if ci == 0 else BROWN_D
            cell.font      = font('Calibri', 10 if ci>0 else 11, ci==0, fg)
            cell.alignment = align('center' if ci>0 else 'left','center')
            cell.fill      = fill(bg)
            cell.border    = thin_border()

    # Freeze header
    ws.freeze_panes = 'B5'

# ── SHEET 3: DASA BHUKTI ──────────────────────────────────────────────────────

def build_dasa_sheet(wb, data, lang):
    ws = wb.create_sheet(lbl('dasa_bhukti', lang)[:31])
    ws.sheet_view.showGridLines = False

    for col, w in [(1,2),(2,18),(3,18),(4,14),(5,14),(6,14),(7,2)]:
        ws.column_dimensions[get_column_letter(col)].width = w

    ws.row_dimensions[1].height = 8
    ws.row_dimensions[2].height = 28
    merge_set(ws, 2, 2, 2, 6, lbl('dasa_bhukti', lang),
              font('Calibri', 14, True, GOLD), align('center','center'), fill(DARK_BG))
    ws.row_dimensions[3].height = 8

    # Header
    ws.row_dimensions[4].height = 22
    headers = [lbl('dasa',lang), lbl('bhukti',lang),
               lbl('start',lang), lbl('end',lang), lbl('status',lang)]
    for ci, h in enumerate(headers):
        cell = ws.cell(row=4, column=2+ci, value=h)
        cell.font      = font('Calibri', 10, True, GOLD_LT)
        cell.alignment = align('center','center')
        cell.fill      = fill(BROWN_M)
        cell.border    = thin_border()

    today = date.today()
    r = 5
    for drow in data['dasas']:
        bhuktis = build_bhuktis(drow['dasa'], drow['start'], drow['end'])
        for brow in bhuktis:
            ws.row_dimensions[r].height = 17
            is_cur  = brow['start'] <= today <= brow['end']
            is_past = brow['end'] < today

            if is_cur:   bg, status = CURRENT_Y, lbl('current', lang)
            elif is_past: bg, status = PAST_G,   lbl('completed', lang)
            else:         bg, status = FUTURE_B,  lbl('upcoming', lang)

            row_data = [
                get_planet_name(drow['dasa'],  lang),
                get_planet_name(brow['bhukti'],lang),
                fmt_date(brow['start']),
                fmt_date(brow['end']),
                status,
            ]
            for ci, val in enumerate(row_data):
                cell = ws.cell(row=r, column=2+ci, value=val)
                cell.font      = font('Calibri', 10, is_cur, BROWN_D if not is_cur else '5D4037')
                cell.alignment = align('center','center')
                cell.fill      = fill(bg)
                cell.border    = thin_border()
                # Status column colour
                if ci == 4:
                    if is_cur:
                        cell.font = font('Calibri', 10, True, '8B6914')
                    elif is_past:
                        cell.font = font('Calibri', 10, False, '888888')
                    else:
                        cell.font = font('Calibri', 10, False, '2980B9')
            r += 1

    ws.freeze_panes = 'B5'

# ── SHEET 4: YOGAS ────────────────────────────────────────────────────────────

def build_yogas_sheet(wb, data, lang):
    ws = wb.create_sheet('Yogas')
    ws.sheet_view.showGridLines = False

    for col, w in [(1,2),(2,28),(3,52),(4,2)]:
        ws.column_dimensions[get_column_letter(col)].width = w

    ws.row_dimensions[1].height = 8
    ws.row_dimensions[2].height = 28
    merge_set(ws, 2, 2, 2, 3, lbl('yogas', lang),
              font('Calibri', 14, True, GOLD), align('center','center'), fill(DARK_BG))
    ws.row_dimensions[3].height = 8

    ws.row_dimensions[4].height = 20
    for ci, h in enumerate(['Yoga Name', 'Significance']):
        cell = ws.cell(row=4, column=2+ci, value=h)
        cell.font = font('Calibri', 10, True, GOLD_LT)
        cell.alignment = align('center','center')
        cell.fill = fill(BROWN_M)
        cell.border = thin_border()

    for ri, (yname, ydesc) in enumerate(data['yogas']):
        r = 5 + ri
        ws.row_dimensions[r].height = 36
        bg = CREAM if ri%2==0 else CREAM_D
        n_cell = ws.cell(row=r, column=2, value=yname)
        n_cell.font = font('Calibri', 11, True, BROWN_D)
        n_cell.alignment = align('left','center')
        n_cell.fill = fill(bg)
        n_cell.border = thin_border()

        d_cell = ws.cell(row=r, column=3, value=ydesc)
        d_cell.font = font('Calibri', 9, False, BROWN_D)
        d_cell.alignment = align('left','center', wrap=True)
        d_cell.fill = fill(bg)
        d_cell.border = thin_border()

    # Footer
    r = 5 + len(data['yogas']) + 2
    ws.row_dimensions[r].height = 14
    merge_set(ws, r, 2, r, 3,
              'Note: Yoga interpretations are based on traditional Vedic astrology principles.',
              font('Calibri', 8, False, GOLD_DIM, True),
              align('center','center'), fill(DARK_BG))

# ── MAIN EXCEL GENERATOR ──────────────────────────────────────────────────────

def generate_excel(data, lang='en') -> bytes:
    wb = Workbook()
    build_summary_sheet(wb, data, lang)
    build_planets_sheet(wb, data, lang)
    build_dasa_sheet(wb, data, lang)
    build_yogas_sheet(wb, data, lang)

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf.read()
