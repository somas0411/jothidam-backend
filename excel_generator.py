"""
excel_generator.py — Professional Excel Horoscope Generator
Generates a multi-sheet Excel with:
  Sheet 1: Summary
  Sheet 2: Rasi Chart (South Indian square drawn with cells)
  Sheet 3: Planet Positions
  Sheet 4: Vimshottari Dasa Bhukti
  Sheet 5: Yogas
"""

import io
from datetime import date
import openpyxl
from openpyxl.styles import PatternFill, Border, Side, Alignment, Font
from openpyxl.utils import get_column_letter


# ── CONSTANTS ─────────────────────────────────────────────────────────────────
GOLD        = 'FFD700'
DARK_BROWN  = '1A0A00'
LIGHT_GOLD  = 'FFF8E6'
LAGNA_BG    = 'FFE5B4'
CENTER_BG   = 'F5E6C8'
HEADER_BG   = '2C1810'
CURRENT_BG  = 'FFF3CD'
COMPLETED_BG= 'F0F0F0'
WHITE       = 'FFFFFF'
CREAM       = 'FFFEF5'

# South Indian grid: house numbers, -1 = center block
CHART_GRID = [
    [12,  1,  2,  3],
    [11, -1, -1,  4],
    [10, -1, -1,  5],
    [ 9,  8,  7,  6],
]

RASI_SHORT = {
    1:'Pis', 2:'Ari', 3:'Tau', 4:'Gem',
    5:'Can', 6:'Leo', 7:'Vir', 8:'Lib',
    9:'Sco', 10:'Sag', 11:'Cap', 12:'Aqu',
}

RASI_FULL = {
    1:'Meena (Pisces)',     2:'Mesha (Aries)',      3:'Vrishabha (Taurus)',
    4:'Mithuna (Gemini)',   5:'Kataka (Cancer)',    6:'Simha (Leo)',
    7:'Kanya (Virgo)',      8:'Tula (Libra)',        9:'Vrischika (Scorpio)',
    10:'Dhanus (Sagittarius)', 11:'Makara (Capricorn)', 12:'Kumbha (Aquarius)',
}

PLANET_ABBR = {
    'Lagna':'La', 'Sun':'Su', 'Moon':'Mo', 'Mars':'Ma',
    'Mercury':'Me', 'Jupiter':'Ju', 'Venus':'Ve',
    'Saturn':'Sa', 'Rahu':'Ra', 'Ketu':'Ke',
}


# ── STYLE HELPERS ─────────────────────────────────────────────────────────────
def thin_border(color=GOLD):
    s = Side(style='thin', color=color)
    return Border(left=s, right=s, top=s, bottom=s)

def thick_border(color=DARK_BROWN):
    s = Side(style='medium', color=color)
    return Border(left=s, right=s, top=s, bottom=s)

def fill(color):
    return PatternFill('solid', fgColor=color)

def font(bold=False, size=10, color=DARK_BROWN, italic=False):
    return Font(bold=bold, size=size, color=color, italic=italic, name='Calibri')

def align(h='center', v='center', wrap=False):
    return Alignment(horizontal=h, vertical=v, wrap_text=wrap)

def set_cell(ws, row, col, value='', bold=False, size=10, color=DARK_BROWN,
             bg=None, h_align='left', v_align='center', wrap=False,
             italic=False, border=None):
    cell = ws.cell(row=row, column=col, value=value)
    cell.font      = font(bold=bold, size=size, color=color, italic=italic)
    cell.alignment = align(h=h_align, v=v_align, wrap=wrap)
    if bg:
        cell.fill = fill(bg)
    if border:
        cell.border = border
    return cell


# ── SHEET 1: SUMMARY ─────────────────────────────────────────────────────────
def build_summary_sheet(wb, data, lang='en'):
    ws = wb.active
    ws.title = 'Summary'
    ws.sheet_view.showGridLines = False

    # Column widths
    ws.column_dimensions['A'].width = 2
    ws.column_dimensions['B'].width = 26
    ws.column_dimensions['C'].width = 32
    ws.column_dimensions['D'].width = 18
    ws.column_dimensions['E'].width = 18

    # Row 1: Main title banner
    ws.merge_cells('B1:E1')
    ws.row_dimensions[1].height = 36
    set_cell(ws, 1, 2, '🕉  JOTHIDAM  ·  VEDIC HOROSCOPE REPORT',
             bold=True, size=16, color=DARK_BROWN, bg=GOLD, h_align='center',
             border=thick_border())

    ws.row_dimensions[2].height = 8

    # Row 3: subtitle
    ws.merge_cells('B3:E3')
    ws.row_dimensions[3].height = 20
    set_cell(ws, 3, 2,
             f"Generated: {date.today().strftime('%d %b %Y')}  ·  horoscopegen.in",
             italic=True, size=9, color='7A5C2E', bg=LIGHT_GOLD, h_align='center')

    ws.row_dimensions[4].height = 10

    # Section: Birth Details
    def section_header(row, title):
        ws.merge_cells(f'B{row}:E{row}')
        ws.row_dimensions[row].height = 22
        set_cell(ws, row, 2, f'  {title}', bold=True, size=11,
                 color=GOLD, bg=HEADER_BG, h_align='left',
                 border=thick_border(GOLD))

    def data_row(row, label, value, highlight=False):
        ws.row_dimensions[row].height = 20
        bg = CURRENT_BG if highlight else LIGHT_GOLD
        set_cell(ws, row, 2, label, bold=True, size=10, color='5C3D11',
                 bg=bg, h_align='left', border=thin_border())
        ws.merge_cells(f'C{row}:E{row}')
        set_cell(ws, row, 3, value, size=10, color=DARK_BROWN,
                 bg=WHITE if not highlight else CURRENT_BG,
                 h_align='left', border=thin_border())

    r = 5
    section_header(r, '👤  BIRTH DETAILS')
    r += 1
    data_row(r, 'Full Name',      data.get('name', ''));           r += 1
    data_row(r, 'Date of Birth',  data.get('dob', ''));            r += 1
    data_row(r, 'Time of Birth',  data.get('tob', ''));            r += 1
    data_row(r, 'Place of Birth', data.get('pob', ''));            r += 1

    r += 1
    section_header(r, '🔷  CORE ASTROLOGICAL DETAILS')
    r += 1
    data_row(r, 'Lagna (Ascendant)',  data.get('lagnaName', '')); r += 1
    data_row(r, 'Janma Rasi',         data.get('moonRasiName', '')); r += 1
    data_row(r, 'Janma Nakshatra',
             f"{data.get('nakName','')} - Pada {data.get('nakPada','')}"); r += 1
    data_row(r, 'Nakshatra Lord',     data.get('nakLord', '')); r += 1

    r += 1
    section_header(r, '📅  CURRENT DASA PERIOD')
    r += 1
    cur_dasa   = data.get('curDasa', {})
    cur_bhukti = data.get('curBhukti', {})
    data_row(r, 'Current Dasa',
             f"{cur_dasa.get('dasa','')}  (ends {cur_dasa.get('end','')})",
             highlight=True); r += 1
    data_row(r, 'Current Bhukti',
             f"{cur_bhukti.get('bhukti','')}  (ends {cur_bhukti.get('end','')})",
             highlight=True); r += 1

    r += 1
    section_header(r, '💎  AUSPICIOUS DETAILS')
    r += 1
    data_row(r, 'Recommended Gemstone', data.get('gemstone', '')); r += 1
    data_row(r, 'Lucky Colors',         data.get('luckyColors', '')); r += 1
    lucky = data.get('luckyNumbers', [])
    data_row(r, 'Lucky Numbers',
             ', '.join(str(n) for n in lucky) if isinstance(lucky, list) else str(lucky))

    r += 2
    ws.merge_cells(f'B{r}:E{r}')
    set_cell(ws, r, 2,
             'This report is based on Vedic astrology principles. For guidance only.',
             italic=True, size=8, color='999999', h_align='center')


# ── SHEET 2: RASI CHART ───────────────────────────────────────────────────────
def build_chart_sheet(wb, data):
    ws = wb.create_sheet('Rasi Chart')
    ws.sheet_view.showGridLines = False

    # Build house → planet abbreviations map
    # Handles both dict format {planet, house, ...} and string format
    planets_by_house = {}
    lagna_rasi = data.get('lagnaRasi', 1)

    raw_planets = data.get('planets', [])
    for p in raw_planets:
        # If planet entry is a dict (from frontend payload or JSON)
        if isinstance(p, dict):
            h    = int(p.get('house', 0))
            name = p.get('planet', p.get('name', ''))
            abbr = PLANET_ABBR.get(name, name[:2] if name else '??')
        # If planet entry is a string like "Sun" — fallback
        elif isinstance(p, str):
            h    = 0  # unknown house, skip
            abbr = PLANET_ABBR.get(p, p[:2])
        else:
            continue

        if h == 0:
            continue
        if h not in planets_by_house:
            planets_by_house[h] = []
        planets_by_house[h].append(abbr)

    CELL_COLS = 4   # Excel columns per chart cell
    CELL_ROWS = 5   # Excel rows per chart cell
    START_COL = 2
    START_ROW = 4

    # Set column/row sizes
    ws.column_dimensions['A'].width = 2
    for c in range(START_COL, START_COL + 4 * CELL_COLS + 2):
        ws.column_dimensions[get_column_letter(c)].width = 9
    for r in range(START_ROW, START_ROW + 4 * CELL_ROWS + 1):
        ws.row_dimensions[r].height = 24

    name    = data.get('name', '')
    dob     = data.get('dob', '')
    tob     = data.get('tob', '')
    pob     = data.get('pob', '')
    nak     = data.get('nakName', '')
    nakpada = data.get('nakPada', '')
    lagna   = data.get('lagnaName', '')

    # Title row
    ws.merge_cells(start_row=1, start_column=START_COL,
                   end_row=1,   end_column=START_COL + 4*CELL_COLS - 1)
    ws.row_dimensions[1].height = 30
    t = ws.cell(row=1, column=START_COL,
                value='🕉  RASI CHART (South Indian Style)')
    t.font      = Font(bold=True, size=14, color=DARK_BROWN, name='Calibri')
    t.alignment = align(h='center')
    t.fill      = fill(GOLD)
    t.border    = thick_border()

    ws.merge_cells(start_row=2, start_column=START_COL,
                   end_row=2,   end_column=START_COL + 4*CELL_COLS - 1)
    ws.row_dimensions[2].height = 18
    s = ws.cell(row=2, column=START_COL,
                value=f'{name}  ·  {dob}  ·  {tob}  ·  {pob}  ·  Lagna: {lagna}')
    s.font      = Font(italic=True, size=9, color='5C3D11', name='Calibri')
    s.alignment = align(h='center')
    s.fill      = fill(LIGHT_GOLD)
    ws.row_dimensions[3].height = 6

    thin  = Side(style='thin',   color=GOLD)
    thick = Side(style='medium', color=DARK_BROWN)

    center_merged = False

    for grid_row in range(4):
        for grid_col in range(4):
            house = CHART_GRID[grid_row][grid_col]
            er    = START_ROW + grid_row * CELL_ROWS
            ec    = START_COL + grid_col * CELL_COLS

            if house == -1:
                # Center 2x2 block — merge once
                if not center_merged:
                    cr = START_ROW + CELL_ROWS
                    cc = START_COL + CELL_COLS
                    ws.merge_cells(
                        start_row=cr, start_column=cc,
                        end_row=cr + 2*CELL_ROWS - 1,
                        end_column=cc + 2*CELL_COLS - 1
                    )
                    c = ws.cell(row=cr, column=cc)
                    c.value     = f'🕉\n{name}\n\n{lagna}\nLagna\n\n{nak}\nPada {nakpada}'
                    c.font      = Font(bold=True, size=11, color=DARK_BROWN, name='Calibri')
                    c.alignment = align(h='center', v='center', wrap=True)
                    c.fill      = fill(CENTER_BG)
                    c.border    = Border(
                        left=Side(style='medium', color=DARK_BROWN),
                        right=Side(style='medium', color=DARK_BROWN),
                        top=Side(style='medium', color=DARK_BROWN),
                        bottom=Side(style='medium', color=DARK_BROWN),
                    )
                    center_merged = True
                continue

            # Merge the house cell block
            ws.merge_cells(
                start_row=er, start_column=ec,
                end_row=er + CELL_ROWS - 1,
                end_column=ec + CELL_COLS - 1
            )

            planets = planets_by_house.get(house, [])
            short   = RASI_SHORT.get(house, '')
            content = short + ('\n' + '  '.join(planets) if planets else '')

            is_lagna = (house == lagna_rasi)
            bg_color = LAGNA_BG if is_lagna else (CREAM if planets else LIGHT_GOLD)

            cell = ws.cell(row=er, column=ec, value=content)
            cell.font = Font(
                bold=bool(planets) or is_lagna,
                size=11 if planets else 9,
                color='8B0000' if is_lagna else (DARK_BROWN if planets else '8B6914'),
                name='Calibri'
            )
            cell.alignment = align(h='center', v='center', wrap=True)
            cell.fill      = fill(bg_color)
            cell.border    = Border(
                left=Side(style='thin', color=GOLD),
                right=Side(style='thin', color=GOLD),
                top=Side(style='thin', color=GOLD),
                bottom=Side(style='thin', color=GOLD),
            )

    # Thick outer border
    chart_end_row = START_ROW + 4 * CELL_ROWS - 1
    chart_end_col = START_COL + 4 * CELL_COLS - 1
    for r in range(START_ROW, chart_end_row + 1):
        for c_idx in range(START_COL, chart_end_col + 1):
            cell = ws.cell(row=r, column=c_idx)
            left   = Side(style='medium', color=DARK_BROWN) if c_idx == START_COL    else cell.border.left
            right  = Side(style='medium', color=DARK_BROWN) if c_idx == chart_end_col else cell.border.right
            top    = Side(style='medium', color=DARK_BROWN) if r == START_ROW         else cell.border.top
            bottom = Side(style='medium', color=DARK_BROWN) if r == chart_end_row     else cell.border.bottom
            cell.border = Border(left=left, right=right, top=top, bottom=bottom)

    # Legend
    leg_row = chart_end_row + 3
    ws.merge_cells(start_row=leg_row, start_column=START_COL,
                   end_row=leg_row,   end_column=START_COL + 4*CELL_COLS - 1)
    ws.row_dimensions[leg_row].height = 18
    h = ws.cell(row=leg_row, column=START_COL, value='PLANET ABBREVIATIONS')
    h.font = Font(bold=True, size=9, color=DARK_BROWN)
    h.fill = fill(LIGHT_GOLD)

    abbrevs = 'La=Lagna  ·  Su=Sun  ·  Mo=Moon  ·  Ma=Mars  ·  Me=Mercury  ·  Ju=Jupiter  ·  Ve=Venus  ·  Sa=Saturn  ·  Ra=Rahu  ·  Ke=Ketu'
    ws.merge_cells(start_row=leg_row+1, start_column=START_COL,
                   end_row=leg_row+1,   end_column=START_COL + 4*CELL_COLS - 1)
    ws.row_dimensions[leg_row+1].height = 16
    a = ws.cell(row=leg_row+1, column=START_COL, value=abbrevs)
    a.font = Font(italic=True, size=8, color='5C3D11')

    ws.merge_cells(start_row=leg_row+2, start_column=START_COL,
                   end_row=leg_row+2,   end_column=START_COL + 4*CELL_COLS - 1)
    n = ws.cell(row=leg_row+2, column=START_COL,
                value='★ Peach highlighted house = Lagna (Ascendant)')
    n.font = Font(italic=True, size=8, color='8B4513')


# ── SHEET 3: PLANET POSITIONS ────────────────────────────────────────────────
def build_planets_sheet(wb, data, lang='en'):
    ws = wb.create_sheet('Planet Positions')
    ws.sheet_view.showGridLines = False

    ws.column_dimensions['A'].width = 2
    ws.column_dimensions['B'].width = 16
    ws.column_dimensions['C'].width = 20
    ws.column_dimensions['D'].width = 14
    ws.column_dimensions['E'].width = 22
    ws.column_dimensions['F'].width = 8
    ws.column_dimensions['G'].width = 8

    # Title
    ws.merge_cells('B1:G1')
    ws.row_dimensions[1].height = 28
    t = ws.cell(row=1, column=2, value='🌟  PLANET POSITIONS')
    t.font = Font(bold=True, size=13, color=DARK_BROWN, name='Calibri')
    t.alignment = align(h='center')
    t.fill = fill(GOLD)
    t.border = thick_border()

    # Header row
    ws.row_dimensions[2].height = 6
    headers = ['Planet', 'Rasi', 'Degrees', 'Nakshatra', 'Pada', 'House']
    ws.row_dimensions[3].height = 22
    for i, h in enumerate(headers, start=2):
        c = ws.cell(row=3, column=i, value=h)
        c.font      = Font(bold=True, size=10, color=GOLD, name='Calibri')
        c.alignment = align(h='center')
        c.fill      = fill(HEADER_BG)
        c.border    = thin_border(GOLD)

    # Data rows
    lagna_rasi = data.get('lagnaRasi', 1)
    for ri, p in enumerate(data.get('planets', []), start=4):
        ws.row_dimensions[ri].height = 20
        if not isinstance(p, dict):
            continue
        is_lagna = p.get('planet') == 'Lagna'
        bg = LAGNA_BG if is_lagna else (LIGHT_GOLD if ri % 2 == 0 else WHITE)
        row_data = [
            p.get('planet', ''),
            p.get('rasi', ''),
            p.get('degrees', ''),
            p.get('nakshatra', ''),
            str(p.get('pada', '')),
            str(p.get('house', '')),
        ]
        for ci, val in enumerate(row_data, start=2):
            c = ws.cell(row=ri, column=ci, value=val)
            c.font      = Font(bold=is_lagna, size=10, color=DARK_BROWN, name='Calibri')
            c.alignment = align(h='center' if ci > 3 else 'left')
            c.fill      = fill(bg)
            c.border    = thin_border()


# ── SHEET 4: DASA BHUKTI ─────────────────────────────────────────────────────
def build_dasa_sheet(wb, data, lang='en'):
    ws = wb.create_sheet('Vimshottari Dasa Bhukti')
    ws.sheet_view.showGridLines = False

    ws.column_dimensions['A'].width = 2
    ws.column_dimensions['B'].width = 16
    ws.column_dimensions['C'].width = 16
    ws.column_dimensions['D'].width = 14
    ws.column_dimensions['E'].width = 14
    ws.column_dimensions['F'].width = 14

    ws.merge_cells('B1:F1')
    ws.row_dimensions[1].height = 28
    t = ws.cell(row=1, column=2, value='📅  VIMSHOTTARI DASA BHUKTI')
    t.font = Font(bold=True, size=13, color=DARK_BROWN, name='Calibri')
    t.alignment = align(h='center')
    t.fill = fill(GOLD)
    t.border = thick_border()

    ws.row_dimensions[2].height = 6
    headers = ['Dasa', 'Bhukti', 'Start', 'End', 'Status']
    ws.row_dimensions[3].height = 22
    for i, h in enumerate(headers, start=2):
        c = ws.cell(row=3, column=i, value=h)
        c.font      = Font(bold=True, size=10, color=GOLD, name='Calibri')
        c.alignment = align(h='center')
        c.fill      = fill(HEADER_BG)
        c.border    = thin_border(GOLD)

    for ri, d in enumerate(data.get('dasas', []), start=4):
        ws.row_dimensions[ri].height = 20
        status = d.get('status', '')
        if status == 'current':
            bg = CURRENT_BG
            st_color = '856404'
        elif status == 'completed':
            bg = COMPLETED_BG
            st_color = '6C757D'
        else:
            bg = WHITE
            st_color = '155724'

        row_data = [
            d.get('dasa', ''),
            d.get('bhukti', ''),
            d.get('start', ''),
            d.get('end', ''),
            status.capitalize(),
        ]
        for ci, val in enumerate(row_data, start=2):
            c = ws.cell(row=ri, column=ci, value=val)
            c.font      = Font(
                bold=(status == 'current'),
                size=10,
                color=st_color if ci == 6 else DARK_BROWN,
                name='Calibri'
            )
            c.alignment = align(h='center')
            c.fill      = fill(bg)
            c.border    = thin_border()

        # Gold left bar for current
        if status == 'current':
            ws.cell(row=ri, column=2).border = Border(
                left=Side(style='medium', color=GOLD),
                right=Side(style='thin', color=GOLD),
                top=Side(style='thin', color=GOLD),
                bottom=Side(style='thin', color=GOLD),
            )


# ── SHEET 5: YOGAS ───────────────────────────────────────────────────────────
def build_yogas_sheet(wb, data):
    ws = wb.create_sheet('Yogas & Remedies')
    ws.sheet_view.showGridLines = False

    ws.column_dimensions['A'].width = 2
    ws.column_dimensions['B'].width = 28
    ws.column_dimensions['C'].width = 52
    ws.column_dimensions['D'].width = 14

    ws.merge_cells('B1:C1')
    ws.row_dimensions[1].height = 28
    t = ws.cell(row=1, column=2, value='✨  PLANETARY YOGAS & AUSPICIOUS DETAILS')
    t.font = Font(bold=True, size=13, color=DARK_BROWN, name='Calibri')
    t.alignment = align(h='center')
    t.fill = fill(GOLD)
    t.border = thick_border()

    ws.row_dimensions[2].height = 6

    headers = ['Yoga Name', 'Significance']
    ws.row_dimensions[3].height = 22
    for i, h in enumerate(headers, start=2):
        c = ws.cell(row=3, column=i, value=h)
        c.font = Font(bold=True, size=10, color=GOLD, name='Calibri')
        c.alignment = align(h='center')
        c.fill = fill(HEADER_BG)
        c.border = thin_border(GOLD)

    for ri, y in enumerate(data.get('yogas', []), start=4):
        ws.row_dimensions[ri].height = 22
        bg = LIGHT_GOLD if ri % 2 == 0 else WHITE

        # Handle both dict {'name':..,'description':..} and tuple (name, desc)
        if isinstance(y, dict):
            y_name = y.get('name', '')
            y_desc = y.get('description', '')
        elif isinstance(y, (tuple, list)) and len(y) >= 2:
            y_name, y_desc = y[0], y[1]
        else:
            y_name = str(y)
            y_desc = ''

        c1 = ws.cell(row=ri, column=2, value=y_name)
        c1.font = Font(bold=True, size=10, color=DARK_BROWN, name='Calibri')
        c1.fill = fill(bg)
        c1.border = thin_border()
        c1.alignment = align(h='left')

        c2 = ws.cell(row=ri, column=3, value=y_desc)
        c2.font = Font(size=9, color='3D2B00', name='Calibri')
        c2.fill = fill(bg)
        c2.border = thin_border()
        c2.alignment = align(h='left', wrap=True)

    # Auspicious details section
    ri = 4 + len(data.get('yogas', [])) + 2
    ws.merge_cells(f'B{ri}:C{ri}')
    ws.row_dimensions[ri].height = 22
    h = ws.cell(row=ri, column=2, value='💎  AUSPICIOUS DETAILS')
    h.font = Font(bold=True, size=11, color=GOLD, name='Calibri')
    h.fill = fill(HEADER_BG)
    h.alignment = align(h='left')
    h.border = thick_border()
    ri += 1

    details = [
        ('Recommended Gemstone', data.get('gemstone', '')),
        ('Lucky Colors',         data.get('luckyColors', '')),
        ('Lucky Numbers',        ', '.join(str(n) for n in data.get('luckyNumbers', []))),
        ('Nakshatra Lord',       data.get('nakLord', '')),
        ('Current Dasa Ends',    data.get('curDasa', {}).get('end', '')),
        ('Current Bhukti Ends',  data.get('curBhukti', {}).get('end', '')),
    ]
    for label, val in details:
        ws.row_dimensions[ri].height = 20
        c1 = ws.cell(row=ri, column=2, value=label)
        c1.font = Font(bold=True, size=10, color='5C3D11', name='Calibri')
        c1.fill = fill(LIGHT_GOLD)
        c1.border = thin_border()
        c1.alignment = align(h='left')

        c2 = ws.cell(row=ri, column=3, value=val)
        c2.font = Font(size=10, color=DARK_BROWN, name='Calibri')
        c2.fill = fill(WHITE)
        c2.border = thin_border()
        c2.alignment = align(h='left')
        ri += 1


# ── MAIN ENTRY POINT ─────────────────────────────────────────────────────────
def generate_excel(data, lang='en'):
    """
    Generate professional Excel horoscope report.
    Args:
        data (dict): Horoscope data from compute() or frontend payload
        lang (str):  Language code
    Returns:
        bytes: Excel file as bytes
    """
    wb = openpyxl.Workbook()

    build_summary_sheet(wb, data, lang)
    build_chart_sheet(wb, data)
    build_planets_sheet(wb, data, lang)
    build_dasa_sheet(wb, data, lang)
    build_yogas_sheet(wb, data)

    # Save to bytes
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf.read()
