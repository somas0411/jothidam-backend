"""
pdf_generator.py — Professional Vedic Horoscope PDF Generator
Uses ReportLab to draw proper South/North Indian Rasi charts
"""
import io
import math
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import date

from astro_engine import (
    get_rasi, get_deg, fmt_deg, get_nak, get_pada,
    get_rasi_name, get_nak_name, get_planet_name, get_planet_abbr,
    get_navamsa_rasi, fmt_date, lbl,
    RASIS_FULL, NAKS, NAKS_TA, PLANET_COLORS, DASA_ORDER,
    LUCKY_NUMS, LUCKY_COLORS, get_gemstone,
    LABELS
)

# ── COLOUR PALETTE ─────────────────────────────────────────────────────────────
DARK_BG    = colors.HexColor('#0D0600')
GOLD       = colors.HexColor('#C9A03A')
GOLD_LIGHT = colors.HexColor('#E8C96B')
GOLD_DIM   = colors.HexColor('#7A6020')
CREAM      = colors.HexColor('#FFF8E8')
CREAM_DARK = colors.HexColor('#F5EDCF')
BROWN_DARK = colors.HexColor('#1A0A00')
BROWN_MID  = colors.HexColor('#3D2000')
WHITE      = colors.white
RED_ACCENT = colors.HexColor('#C0392B')
BLUE_ACCENT= colors.HexColor('#2980B9')
GREEN_ACC  = colors.HexColor('#27AE60')
PURPLE_ACC = colors.HexColor('#8E44AD')

# Planet chip colours
P_COLORS = {
    'Lagna':   (colors.HexColor('#E8871A'), WHITE),
    'Sun':     (colors.HexColor('#E8871A'), WHITE),
    'Moon':    (colors.HexColor('#2980B9'), WHITE),
    'Mars':    (colors.HexColor('#C0392B'), WHITE),
    'Mercury': (colors.HexColor('#27AE60'), WHITE),
    'Jupiter': (colors.HexColor('#8B6914'), WHITE),
    'Venus':   (colors.HexColor('#8E44AD'), WHITE),
    'Saturn':  (colors.HexColor('#5D6D7E'), WHITE),
    'Rahu':    (colors.HexColor('#2C3E50'), colors.HexColor('#DDD')),
    'Ketu':    (colors.HexColor('#7F8C8D'), WHITE),
}

W, H = A4
M    = 15*mm   # page margin

# South Indian Rasi positions in 4x4 grid (0-indexed row,col)
# Row 0=top, Col 0=left
SOUTH_POS = {
    0:  (0,1), 1:  (0,2), 2:  (0,3), 3:  (1,3),
    4:  (2,3), 5:  (3,3), 6:  (3,2), 7:  (3,1),
    8:  (3,0), 9:  (2,0), 10: (1,0), 11: (0,0),
}

# ── FONT SETUP ──────────────────────────────────────────────────────────────────

_fonts_registered = False

def register_fonts():
    global _fonts_registered
    if _fonts_registered:
        return
    # Register DejaVu for Unicode (Tamil, Hindi etc)
    # We'll use built-in Helvetica for ASCII and embed Unicode safely
    try:
        import urllib.request, os, tempfile
        # Try to use system fonts
        import platform
        font_paths = []
        if platform.system() == 'Linux':
            font_paths = [
                '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
                '/usr/share/fonts/truetype/freefont/FreeSans.ttf',
                '/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf',
                '/usr/share/fonts/opentype/noto/NotoSansTamil-Regular.otf',
            ]
        for fp in font_paths:
            if os.path.exists(fp):
                try:
                    pdfmetrics.registerFont(TTFont('Unicode', fp))
                    _fonts_registered = True
                    return
                except:
                    continue
    except:
        pass
    _fonts_registered = True

def get_font(lang='en', bold=False):
    """Return best font for the language"""
    register_fonts()
    # For complex scripts, try Unicode font
    if lang in ['ta','hi','te','kn','ml','mr','bn']:
        try:
            pdfmetrics.getFont('Unicode')
            return 'Unicode'
        except:
            pass
    return 'Helvetica-Bold' if bold else 'Helvetica'

def safe_text(c, text, x, y, font='Helvetica', size=10, color=colors.black):
    """Draw text safely, falling back to ASCII if Unicode font unavailable"""
    c.setFont(font, size)
    c.setFillColor(color)
    try:
        c.drawString(x, y, text)
    except Exception:
        # Fallback: encode as ASCII with replacement
        c.setFont('Helvetica', size)
        ascii_text = text.encode('ascii', 'replace').decode('ascii')
        c.drawString(x, y, ascii_text)

def draw_text_centered(c, text, x, y, font='Helvetica', size=10, color=colors.black):
    c.setFont(font, size)
    c.setFillColor(color)
    try:
        c.drawCentredString(x, y, text)
    except:
        c.setFont('Helvetica', size)
        c.drawCentredString(x, y, text.encode('ascii','replace').decode())

# ── PAGE SETUP HELPERS ─────────────────────────────────────────────────────────

def new_page(c, page_num, total_pages, data, lang):
    """Draw page border, header strip, footer"""
    # Subtle background
    c.setFillColor(CREAM)
    c.rect(0, 0, W, H, fill=1, stroke=0)

    # Top gold band
    c.setFillColor(DARK_BG)
    c.rect(0, H-18*mm, W, 18*mm, fill=1, stroke=0)

    # OM symbol + title
    f = get_font(lang)
    draw_text_centered(c, '🕉  JOTHIDAM · ஜோதிடம்', W/2, H-10*mm, 'Helvetica-Bold', 13, GOLD)
    draw_text_centered(c, lbl('report_title', lang), W/2, H-15*mm, f, 8, GOLD_LIGHT)

    # Side decorative lines
    c.setStrokeColor(GOLD_DIM)
    c.setLineWidth(0.5)
    c.line(M, H-20*mm, W-M, H-20*mm)

    # Footer band
    c.setFillColor(DARK_BG)
    c.rect(0, 0, W, 12*mm, fill=1, stroke=0)
    f_sm = 'Helvetica'
    c.setFont(f_sm, 7)
    c.setFillColor(GOLD_DIM)
    c.drawString(M, 4*mm, f'{lbl("generated", lang)}: {date.today().strftime("%d %b %Y")} · horoscopegen.in')
    c.drawRightString(W-M, 4*mm, f'{lbl("page", lang)} {page_num} {lbl("of", lang)} {total_pages}')
    c.setFillColor(GOLD_DIM)
    c.drawCentredString(W/2, 4*mm, lbl('footer_note', lang))

    # Border
    c.setStrokeColor(GOLD_DIM)
    c.setLineWidth(0.7)
    c.rect(M/2, 12*mm + 2, W-M, H-18*mm - 12*mm - 4, stroke=1, fill=0)

    return H - 22*mm  # return starting Y for content

# ── COVER PAGE ────────────────────────────────────────────────────────────────

def draw_cover(c, data, lang):
    # Full dark background
    c.setFillColor(DARK_BG)
    c.rect(0, 0, W, H, fill=1, stroke=0)

    # Decorative golden border
    c.setStrokeColor(GOLD)
    c.setLineWidth(2)
    c.rect(10*mm, 10*mm, W-20*mm, H-20*mm, stroke=1, fill=0)
    c.setLineWidth(0.5)
    c.rect(12*mm, 12*mm, W-24*mm, H-24*mm, stroke=1, fill=0)

    # Top decorative strip
    c.setFillColor(GOLD)
    c.rect(10*mm, H-40*mm, W-20*mm, 3*mm, fill=1, stroke=0)
    c.rect(10*mm, H-44*mm, W-20*mm, 0.5*mm, fill=1, stroke=0)

    # OM symbol large
    draw_text_centered(c, '🕉', W/2, H-70*mm, 'Helvetica-Bold', 36, GOLD)

    # Title
    draw_text_centered(c, 'JOTHIDAM', W/2, H-88*mm, 'Helvetica-Bold', 32, GOLD)
    draw_text_centered(c, 'ஜோதிடம்  ·  ज्योतिषम्', W/2, H-96*mm, get_font('ta'), 14, GOLD_LIGHT)

    # Divider
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.7)
    c.line(M*3, H-102*mm, W-M*3, H-102*mm)

    # Report type
    draw_text_centered(c, lbl('report_title', lang), W/2, H-112*mm, 'Helvetica-Bold', 16, GOLD_LIGHT)

    # Name
    c.setFillColor(GOLD)
    c.rect(M*2, H-140*mm, W-M*4, 20*mm, fill=1, stroke=0)
    draw_text_centered(c, data['name'], W/2, H-132*mm, 'Helvetica-Bold', 18, DARK_BG)

    # Birth details box
    c.setFillColor(BROWN_MID)
    c.rect(M*2, H-195*mm, W-M*4, 48*mm, fill=1, stroke=0)
    c.setStrokeColor(GOLD_DIM)
    c.setLineWidth(0.5)
    c.rect(M*2, H-195*mm, W-M*4, 48*mm, stroke=1, fill=0)

    bf = get_font(lang)
    y = H-157*mm
    for key, val in [
        (lbl('dob', lang), data['dob']),
        (lbl('tob', lang), data['tob']),
        (lbl('pob', lang), data['pob']),
    ]:
        c.setFont('Helvetica', 9)
        c.setFillColor(GOLD_DIM)
        c.drawString(M*3, y, key + ' :')
        c.setFont(bf, 10)
        c.setFillColor(GOLD_LIGHT)
        c.drawString(M*3 + 45*mm, y, val)
        y -= 13*mm

    # Bottom astro info
    lagna_name = get_rasi_name(data['lagna_rasi'], lang)
    rasi_name  = get_rasi_name(data['moon_rasi'],  lang)
    nak_name   = get_nak_name(data['nak_num'], lang)
    c.setFillColor(BROWN_MID)
    c.rect(M*2, H-255*mm, W-M*4, 50*mm, fill=1, stroke=0)
    c.setStrokeColor(GOLD_DIM)
    c.rect(M*2, H-255*mm, W-M*4, 50*mm, stroke=1, fill=0)

    box_items = [
        (lbl('lagna', lang),    lagna_name),
        (lbl('janma_rasi',lang), rasi_name),
        (lbl('janma_nak',lang),  f'{nak_name} - {lbl("pada",lang)} {data["nak_pada"]}'),
        (lbl('cur_dasa',lang),   f'{data["cur_dasa"]["dasa"]} → {data["cur_bhukti"]["bhukti"]}'),
    ]
    y = H-223*mm
    for key, val in box_items:
        c.setFont('Helvetica', 8)
        c.setFillColor(GOLD_DIM)
        c.drawString(M*3, y, key + ' :')
        c.setFont(bf, 10)
        c.setFillColor(GOLD_LIGHT)
        c.drawString(M*3 + 55*mm, y, str(val))
        y -= 10*mm

    # Bottom note
    draw_text_centered(c, 'horoscopegen.in', W/2, 35*mm, 'Helvetica', 9, GOLD_DIM)
    draw_text_centered(c, 'Generated by Jothidam · Vedic Astrology', W/2, 28*mm, 'Helvetica', 8, GOLD_DIM)

    c.showPage()

# ── SOUTH INDIAN RASI CHART DRAWER ────────────────────────────────────────────

def draw_south_chart(c, data, ox, oy, size, lang, is_navamsa=False):
    """
    Draw proper South Indian square chart.
    ox,oy = bottom-left corner of the chart square
    size  = side length of the entire chart
    """
    # Background
    c.setFillColor(DARK_BG)
    c.rect(ox, oy, size, size, fill=1, stroke=0)

    # Outer border
    c.setStrokeColor(GOLD)
    c.setLineWidth(1.5)
    c.rect(ox, oy, size, size, stroke=1, fill=0)

    # Inner grid lines (4x4)
    cell = size / 4
    c.setStrokeColor(GOLD_DIM)
    c.setLineWidth(0.6)

    # Vertical lines at 1/4, 1/2, 3/4
    for i in [1,2,3]:
        c.line(ox + i*cell, oy, ox + i*cell, oy+size)
    # Horizontal lines at 1/4, 1/2, 3/4
    for i in [1,2,3]:
        c.line(ox, oy + i*cell, ox+size, oy + i*cell)

    # Diagonal lines in corner cells
    diag_pairs = {
        (0,0): ((ox+cell, oy+3*cell), (ox, oy+4*cell)),        # top-left: TL→BR becomes ↘
        (0,3): ((ox+3*cell, oy+3*cell), (ox+4*cell, oy+4*cell)), # top-right
        (3,0): ((ox, oy), (ox+cell, oy+cell)),                  # bottom-left
        (3,3): ((ox+3*cell, oy), (ox+4*cell, oy+cell)),         # bottom-right
    }
    c.setStrokeColor(GOLD_DIM)
    c.setLineWidth(0.8)
    # Corner diagonal lines (cross pattern)
    # Top-left corner
    c.line(ox, oy+3*cell, ox+cell, oy+4*cell)
    c.line(ox, oy+4*cell, ox+cell, oy+3*cell)
    # Top-right corner
    c.line(ox+3*cell, oy+3*cell, ox+4*cell, oy+4*cell)
    c.line(ox+3*cell, oy+4*cell, ox+4*cell, oy+3*cell)
    # Bottom-left corner
    c.line(ox, oy, ox+cell, oy+cell)
    c.line(ox, oy+cell, ox+cell, oy)
    # Bottom-right corner
    c.line(ox+3*cell, oy, ox+4*cell, oy+cell)
    c.line(ox+3*cell, oy+cell, ox+4*cell, oy)

    # Center 2×2 block — fill with dark and draw birth details
    cx_left  = ox + cell
    cy_bottom = oy + cell
    c.setFillColor(BROWN_MID)
    c.rect(cx_left, cy_bottom, 2*cell, 2*cell, fill=1, stroke=0)
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.8)
    c.rect(cx_left, cy_bottom, 2*cell, 2*cell, stroke=1, fill=0)

    # Center text
    cx = ox + 2*cell  # horizontal center
    if not is_navamsa:
        bf = get_font(lang)
        draw_text_centered(c, data['name'], cx, oy+2*cell+8*mm, 'Helvetica-Bold', 7, GOLD)
        dob_parts = data['dob'].split('-')
        dob_str = f"{dob_parts[2]}-{dob_parts[1]}-{dob_parts[0]}" if len(dob_parts)==3 else data['dob']
        draw_text_centered(c, dob_str, cx, oy+2*cell+3*mm, 'Helvetica', 6, GOLD_LIGHT)
        draw_text_centered(c, data['tob'], cx, oy+2*cell-1*mm, 'Helvetica', 6, GOLD_DIM)
        nak_n = get_nak_name(data['nak_num'], lang)
        draw_text_centered(c, f'{nak_n}-{data["nak_pada"]}', cx, oy+2*cell-6*mm, get_font(lang), 5.5, GOLD_DIM)
        # "ராசி" label
        chart_label = lbl('south_indian', lang) if lang != 'en' else 'Rasi'
        draw_text_centered(c, chart_label, cx, oy+cell+2*mm, get_font(lang), 5.5, GOLD_DIM)
    else:
        draw_text_centered(c, 'D9', cx, oy+2*cell+2*mm, 'Helvetica-Bold', 9, GOLD)
        draw_text_centered(c, 'Navamsa', cx, oy+2*cell-4*mm, 'Helvetica', 7, GOLD_LIGHT)

    # Determine which planets go in which cell
    if is_navamsa:
        # Use navamsa positions
        rasi_planets = [[] for _ in range(12)]
        for pname, lon in data['planet_list']:
            nav_rasi = get_navamsa_rasi(lon)
            rasi_planets[nav_rasi].append(pname)
        lagna_rasi = get_navamsa_rasi(data['planets']['lag'])
    else:
        rasi_planets = [[] for _ in range(12)]
        for pname, lon in data['planet_list']:
            rasi_planets[get_rasi(lon)].append(pname)
        lagna_rasi = data['lagna_rasi']

    # Draw each cell
    abbr_font = get_font(lang)
    for rasi_idx, (row, col) in SOUTH_POS.items():
        # Grid in ReportLab: row 0 = top → in RL coords: oy + (3-row)*cell
        cell_x = ox + col*cell
        cell_y = oy + (3-row)*cell

        # Skip center cells
        if (row in [1,2]) and (col in [1,2]):
            continue

        is_lagna = (rasi_idx == lagna_rasi)

        # Cell background highlight for lagna
        if is_lagna:
            c.setFillColor(colors.HexColor('#2A1500'))
            c.rect(cell_x, cell_y, cell, cell, fill=1, stroke=0)

        # Rasi name (top-left of cell)
        rasi_short = get_rasi_name(rasi_idx, lang, short=True)
        c.setFont(abbr_font, 5)
        c.setFillColor(GOLD_DIM if not is_lagna else GOLD)
        try:
            c.drawString(cell_x + 1.5*mm, cell_y + cell - 4*mm, rasi_short)
        except:
            c.setFont('Helvetica', 5)
            c.drawString(cell_x + 1.5*mm, cell_y + cell - 4*mm, RASIS_FULL['en'][rasi_idx][:4])

        # House number (top-right)
        house_num = ((rasi_idx - lagna_rasi + 12) % 12) + 1
        c.setFont('Helvetica', 4.5)
        c.setFillColor(GOLD_DIM)
        c.drawRightString(cell_x + cell - 1.5*mm, cell_y + cell - 4*mm, str(house_num))

        # Planet chips — vertical stack
        planets_here = rasi_planets[rasi_idx]
        chip_h   = 3.8*mm
        chip_w   = cell - 3*mm
        start_y  = cell_y + cell - 8*mm  # start below rasi name

        for pi, pname in enumerate(planets_here[:5]):  # max 5 planets per cell
            py = start_y - pi * (chip_h + 0.5*mm)
            if py < cell_y + 1*mm:
                break
            bg_col, fg_col = P_COLORS.get(pname, (BROWN_MID, GOLD_LIGHT))

            # Draw chip background
            c.setFillColor(bg_col)
            c.roundRect(cell_x + 1.5*mm, py - chip_h + 0.5*mm, chip_w, chip_h, 1*mm, fill=1, stroke=0)

            # Planet abbreviation
            abbr = get_planet_abbr(pname, lang)
            c.setFont(abbr_font, 5)
            c.setFillColor(fg_col)
            try:
                c.drawCentredString(cell_x + cell/2, py - chip_h + 1.5*mm, abbr)
            except:
                c.setFont('Helvetica', 5)
                c.drawCentredString(cell_x + cell/2, py - chip_h + 1.5*mm, pname[:2])

    # Lagna marker (bold border on lagna cell)
    if lagna_rasi in SOUTH_POS:
        row, col = SOUTH_POS[lagna_rasi]
        lx = ox + col*cell
        ly = oy + (3-row)*cell
        c.setStrokeColor(GOLD)
        c.setLineWidth(1.5)
        c.rect(lx, ly, cell, cell, stroke=1, fill=0)

# ── PLANET TABLE ───────────────────────────────────────────────────────────────

def draw_planet_table(c, data, y, lang):
    """Draw planet positions table, returns new Y"""
    f  = get_font(lang)
    W_inner = W - 2*M

    # Section header
    c.setFillColor(DARK_BG)
    c.rect(M, y-8*mm, W_inner, 8*mm, fill=1, stroke=0)
    draw_text_centered(c, lbl('planet_positions', lang), W/2, y-5.5*mm, 'Helvetica-Bold', 11, GOLD)
    y -= 8*mm

    # Column widths
    cols = [32*mm, 34*mm, 22*mm, 40*mm, 14*mm, 16*mm]
    headers = [lbl('planet',lang), lbl('rasi',lang), lbl('degrees',lang),
               lbl('nakshatra',lang), lbl('pada',lang), lbl('house',lang)]

    # Header row
    c.setFillColor(BROWN_MID)
    c.rect(M, y-7*mm, W_inner, 7*mm, fill=1, stroke=0)
    x = M
    for i, h in enumerate(headers):
        c.setFont(f, 8)
        c.setFillColor(GOLD_LIGHT)
        try:
            c.drawString(x + 2*mm, y-5*mm, h)
        except:
            c.setFont('Helvetica', 8)
            c.drawString(x + 2*mm, y-5*mm, h.encode('ascii','replace').decode())
        x += cols[i]
    y -= 7*mm

    # Rows
    lagna_rasi = data['lagna_rasi']
    for ri, (pname, lon) in enumerate(data['planet_list']):
        rasi_num  = get_rasi(lon)
        house     = ((rasi_num - lagna_rasi + 12) % 12) + 1
        nak_n     = get_nak_name(get_nak(lon), lang)
        pada      = get_pada(lon)
        rasi_name = get_rasi_name(rasi_num, lang)
        deg_str   = fmt_deg(lon)
        pname_loc = get_planet_name(pname, lang)
        abbr_loc  = get_planet_abbr(pname, lang)

        # Row background
        bg = CREAM if ri % 2 == 0 else CREAM_DARK
        c.setFillColor(bg)
        c.rect(M, y-6.5*mm, W_inner, 6.5*mm, fill=1, stroke=0)

        # Planet name with colour chip
        chip_col, _ = P_COLORS.get(pname, (BROWN_MID, WHITE))
        c.setFillColor(chip_col)
        c.roundRect(M+1*mm, y-5.5*mm, 5*mm, 4.5*mm, 1*mm, fill=1, stroke=0)
        c.setFont('Helvetica-Bold', 6)
        c.setFillColor(WHITE)
        c.drawCentredString(M+3.5*mm, y-4*mm, pname[:2])

        # Planet full name
        c.setFont(f, 8.5)
        c.setFillColor(BROWN_DARK)
        try:
            c.drawString(M+7*mm, y-4.5*mm, pname_loc)
        except:
            c.setFont('Helvetica', 8.5)
            c.drawString(M+7*mm, y-4.5*mm, pname)

        # Other columns
        row_data = [None, rasi_name, deg_str, nak_n, str(pada), str(house)]
        x = M
        for ci, val in enumerate(row_data):
            if ci == 0:
                x += cols[0]; continue
            c.setFont(f, 8)
            c.setFillColor(BROWN_DARK)
            try:
                c.drawString(x + 2*mm, y-4.5*mm, str(val) if val else '')
            except:
                c.setFont('Helvetica', 8)
                c.drawString(x + 2*mm, y-4.5*mm, str(val).encode('ascii','replace').decode() if val else '')
            x += cols[ci]

        # Row border
        c.setStrokeColor(colors.HexColor('#DDDBC0'))
        c.setLineWidth(0.3)
        c.line(M, y-6.5*mm, M+W_inner, y-6.5*mm)
        y -= 6.5*mm

    # Table border
    c.setStrokeColor(GOLD_DIM)
    c.setLineWidth(0.6)
    table_height = 7*mm + len(data['planet_list'])*6.5*mm
    c.rect(M, y, W_inner, table_height, stroke=1, fill=0)

    return y - 4*mm

# ── DASA BHUKTI TABLE ──────────────────────────────────────────────────────────

def draw_dasa_table(c, data, y, lang, max_rows=None):
    """Draw Dasa-Bhukti table. Returns new Y."""
    f  = get_font(lang)
    today = date.today()
    W_inner = W - 2*M

    # Section header
    c.setFillColor(DARK_BG)
    c.rect(M, y-8*mm, W_inner, 8*mm, fill=1, stroke=0)
    draw_text_centered(c, lbl('dasa_bhukti', lang), W/2, y-5.5*mm, 'Helvetica-Bold', 11, GOLD)
    y -= 8*mm

    cols = [34*mm, 34*mm, 32*mm, 32*mm, 26*mm]
    headers = [lbl('dasa',lang), lbl('bhukti',lang), lbl('start',lang), lbl('end',lang), lbl('status',lang)]

    # Header
    c.setFillColor(BROWN_MID)
    c.rect(M, y-7*mm, W_inner, 7*mm, fill=1, stroke=0)
    x = M
    for i, h in enumerate(headers):
        c.setFont(f, 8)
        c.setFillColor(GOLD_LIGHT)
        try:
            c.drawString(x + 2*mm, y-5*mm, h)
        except:
            c.setFont('Helvetica', 8)
            c.drawString(x + 2*mm, y-5*mm, h.encode('ascii','replace').decode())
        x += cols[i]
    y -= 7*mm

    # All bhukti rows
    from astro_engine import build_bhuktis, DASA_ORDER, DASA_YRS
    rows_drawn = 0
    for drow in data['dasas']:
        bhuktis = build_bhuktis(drow['dasa'], drow['start'], drow['end'])
        for brow in bhuktis:
            if max_rows and rows_drawn >= max_rows:
                return y
            is_cur = (brow['start'] <= today <= brow['end'])
            is_past = brow['end'] < today

            if is_cur:
                bg = colors.HexColor('#FFF3CD')
                status_text = lbl('current', lang)
                status_col  = colors.HexColor('#8B6914')
            elif is_past:
                bg = CREAM_DARK
                status_text = lbl('completed', lang)
                status_col  = BROWN_MID
            else:
                bg = CREAM if rows_drawn % 2 == 0 else CREAM_DARK
                status_text = lbl('upcoming', lang)
                status_col  = BLUE_ACCENT

            c.setFillColor(bg)
            c.rect(M, y-6*mm, W_inner, 6*mm, fill=1, stroke=0)

            # Gold bar for current
            if is_cur:
                c.setFillColor(GOLD)
                c.rect(M, y-6*mm, 1.5*mm, 6*mm, fill=1, stroke=0)

            row_vals = [
                get_planet_name(drow['dasa'], lang),
                get_planet_name(brow['bhukti'], lang),
                fmt_date(brow['start']),
                fmt_date(brow['end']),
                status_text,
            ]
            x = M
            for ci, val in enumerate(row_vals):
                font_w = 'Helvetica-Bold' if is_cur else f
                c.setFont(font_w, 7.5 if ci < 2 else 7)
                c.setFillColor(status_col if ci == 4 else BROWN_DARK)
                try:
                    c.drawString(x + 2*mm, y-4.5*mm, str(val))
                except:
                    c.setFont('Helvetica', 7.5)
                    c.drawString(x + 2*mm, y-4.5*mm, str(val).encode('ascii','replace').decode())
                x += cols[ci]

            c.setStrokeColor(colors.HexColor('#DDDBC0'))
            c.setLineWidth(0.3)
            c.line(M, y-6*mm, M+W_inner, y-6*mm)
            y -= 6*mm
            rows_drawn += 1

    return y - 3*mm

# ── YOGAS PAGE ────────────────────────────────────────────────────────────────

def draw_yogas_section(c, data, y, lang):
    f = get_font(lang)
    W_inner = W - 2*M

    c.setFillColor(DARK_BG)
    c.rect(M, y-8*mm, W_inner, 8*mm, fill=1, stroke=0)
    draw_text_centered(c, lbl('yogas', lang), W/2, y-5.5*mm, 'Helvetica-Bold', 11, GOLD)
    y -= 8*mm

    for i, (yoga_name, yoga_desc) in enumerate(data['yogas']):
        box_h = 18*mm
        bg    = CREAM if i % 2 == 0 else CREAM_DARK
        c.setFillColor(bg)
        c.rect(M, y-box_h, W_inner, box_h, fill=1, stroke=0)

        # Yoga name
        c.setFillColor(GOLD)
        c.rect(M, y-box_h, 2*mm, box_h, fill=1, stroke=0)
        c.setFont('Helvetica-Bold', 10)
        c.setFillColor(BROWN_DARK)
        c.drawString(M+5*mm, y-8*mm, yoga_name)

        # Description
        c.setFont('Helvetica', 8)
        c.setFillColor(BROWN_MID)
        # Simple word wrap
        words = yoga_desc.split()
        line = ''
        ly   = y - 13*mm
        for w in words:
            test = (line + ' ' + w).strip()
            if len(test) * 3.5 > (W_inner - 10*mm):
                c.drawString(M+5*mm, ly, line)
                ly -= 4*mm
                line = w
            else:
                line = test
        if line:
            c.drawString(M+5*mm, ly, line)

        c.setStrokeColor(colors.HexColor('#DDDBC0'))
        c.setLineWidth(0.3)
        c.line(M, y-box_h, M+W_inner, y-box_h)
        y -= box_h

    return y - 4*mm

# ── LUCKY INFO BOX ────────────────────────────────────────────────────────────

def draw_lucky_section(c, data, y, lang):
    f = get_font(lang)
    W_inner = W - 2*M
    nak_lord = data['nak_lord']

    c.setFillColor(DARK_BG)
    c.rect(M, y-8*mm, W_inner, 8*mm, fill=1, stroke=0)
    draw_text_centered(c, 'Auspicious Details', W/2, y-5.5*mm, 'Helvetica-Bold', 11, GOLD)
    y -= 8*mm

    items = [
        (lbl('gemstone', lang),   get_gemstone(nak_lord, lang)),
        (lbl('lucky_color', lang), LUCKY_COLORS.get(nak_lord, 'Gold, Yellow')),
        (lbl('lucky_num', lang),   ', '.join(str(n) for n in LUCKY_NUMS.get(nak_lord, [1,4,7]))),
        ('Nakshatra Lord',          get_planet_name(nak_lord, lang)),
        (lbl('dasa_ends', lang),   fmt_date(data['cur_dasa']['end'])),
        (lbl('bhukti_ends', lang), fmt_date(data['cur_bhukti']['end'])),
    ]

    col_w   = (W_inner) / 2
    row_h   = 12*mm
    for i, (key, val) in enumerate(items):
        row = i // 2
        col = i %  2
        bx  = M + col*col_w
        by  = y - row*row_h

        bg = CREAM if (row+col)%2==0 else CREAM_DARK
        c.setFillColor(bg)
        c.rect(bx, by-row_h, col_w, row_h, fill=1, stroke=0)

        c.setFont('Helvetica', 7.5)
        c.setFillColor(GOLD_DIM)
        try:
            c.drawString(bx+3*mm, by-6*mm, key)
        except:
            c.setFont('Helvetica', 7.5)
            c.drawString(bx+3*mm, by-6*mm, key.encode('ascii','replace').decode())

        c.setFont('Helvetica-Bold', 9)
        c.setFillColor(BROWN_DARK)
        try:
            c.drawString(bx+3*mm, by-11*mm, str(val))
        except:
            c.setFont('Helvetica-Bold', 9)
            c.drawString(bx+3*mm, by-11*mm, str(val).encode('ascii','replace').decode())

        c.setStrokeColor(colors.HexColor('#DDDBC0'))
        c.setLineWidth(0.3)
        c.rect(bx, by-row_h, col_w, row_h, stroke=1, fill=0)

    return y - (len(items)//2 + len(items)%2) * row_h - 4*mm

# ── MAIN PDF GENERATOR ────────────────────────────────────────────────────────

def generate_pdf(data, lang='en', chart_style='south') -> bytes:
    """Generate complete professional horoscope PDF. Returns bytes."""
    register_fonts()
    buf    = io.BytesIO()
    c      = rl_canvas.Canvas(buf, pagesize=A4)
    c.setTitle(f'Jothidam — {data["name"]}')
    c.setAuthor('Jothidam · horoscopegen.in')
    c.setSubject('Vedic Horoscope Report')

    total_pages = 4

    # ── PAGE 1: Cover ─────────────────────────────────────────────────────────
    draw_cover(c, data, lang)

    # ── PAGE 2: Charts ────────────────────────────────────────────────────────
    y = new_page(c, 2, total_pages, data, lang)

    # Name & birth summary strip
    c.setFillColor(DARK_BG)
    c.rect(M, y-20*mm, W-2*M, 20*mm, fill=1, stroke=0)
    bf = get_font(lang)
    draw_text_centered(c, data['name'], W/2, y-9*mm, 'Helvetica-Bold', 14, GOLD)
    summary_line = f"{data['dob']}  ·  {data['tob']}  ·  {data['pob']}"
    draw_text_centered(c, summary_line, W/2, y-16*mm, 'Helvetica', 8, GOLD_DIM)
    y -= 22*mm

    # Tags row: Lagna / Rasi / Nak / Dasa
    tag_items = [
        (lbl('lagna', lang),     get_rasi_name(data['lagna_rasi'], lang)),
        (lbl('janma_rasi',lang), get_rasi_name(data['moon_rasi'], lang)),
        (lbl('janma_nak',lang),  f'{get_nak_name(data["nak_num"],lang)}-{data["nak_pada"]}'),
        (lbl('cur_dasa', lang),  f'{data["cur_dasa"]["dasa"]}→{data["cur_bhukti"]["bhukti"]}'),
    ]
    tag_w = (W-2*M) / len(tag_items)
    for ti, (tlabel, tval) in enumerate(tag_items):
        tx = M + ti*tag_w
        c.setFillColor(BROWN_MID)
        c.rect(tx, y-14*mm, tag_w-1*mm, 14*mm, fill=1, stroke=0)
        c.setFont('Helvetica', 6.5)
        c.setFillColor(GOLD_DIM)
        try:
            c.drawCentredString(tx + tag_w/2, y-7*mm, tlabel)
        except:
            c.setFont('Helvetica', 6.5)
            c.drawCentredString(tx + tag_w/2, y-7*mm, tlabel.encode('ascii','replace').decode())
        c.setFont(bf, 8.5)
        c.setFillColor(GOLD_LIGHT)
        try:
            c.drawCentredString(tx + tag_w/2, y-12*mm, str(tval))
        except:
            c.setFont('Helvetica', 8.5)
            c.drawCentredString(tx + tag_w/2, y-12*mm, str(tval).encode('ascii','replace').decode())
    y -= 16*mm

    # Two charts side by side
    chart_size = (W - 2*M - 5*mm) / 2
    y -= 2*mm

    # South Indian Rasi Chart (left)
    chart_label_y = y - 6*mm
    c.setFont('Helvetica-Bold', 9)
    c.setFillColor(BROWN_DARK)
    c.drawCentredString(M + chart_size/2, chart_label_y, lbl('rasi_chart', lang))
    chart_top_y = chart_label_y - 3*mm
    draw_south_chart(c, data, M, chart_top_y - chart_size, chart_size, lang, is_navamsa=False)

    # Navamsa Chart (right)
    nav_x = M + chart_size + 5*mm
    c.setFont('Helvetica-Bold', 9)
    c.setFillColor(BROWN_DARK)
    c.drawCentredString(nav_x + chart_size/2, chart_label_y, lbl('navamsa_chart', lang))
    draw_south_chart(c, data, nav_x, chart_top_y - chart_size, chart_size, lang, is_navamsa=True)

    y = chart_top_y - chart_size - 4*mm

    # Brief planet summary below charts
    c.setFont('Helvetica', 7)
    c.setFillColor(BROWN_MID)
    summary_planets = []
    for pname, lon in data['planet_list'][:4]:
        rn = get_rasi_name(get_rasi(lon), lang, short=True)
        summary_planets.append(f'{get_planet_abbr(pname,"en")}: {rn}')
    c.drawCentredString(W/2, y-3*mm, '  ·  '.join(summary_planets))

    c.showPage()

    # ── PAGE 3: Planet Table + Dasa Table (first portion) ────────────────────
    y = new_page(c, 3, total_pages, data, lang)
    y -= 3*mm
    y = draw_planet_table(c, data, y, lang)
    y -= 5*mm

    # How many dasa rows fit on this page?
    remaining = y - 18*mm  # footer space
    rows_fit  = int(remaining / 6)
    y = draw_dasa_table(c, data, y, lang, max_rows=rows_fit)

    c.showPage()

    # ── PAGE 4: Remaining Dasa + Yogas + Lucky Info ───────────────────────────
    y = new_page(c, 4, total_pages, data, lang)
    y -= 3*mm

    # Count how many bhukti rows were already drawn
    from astro_engine import build_bhuktis
    total_bhuktis = sum(len(build_bhuktis(d['dasa'], d['start'], d['end'])) for d in data['dasas'])
    already_shown = rows_fit
    remaining_rows = total_bhuktis - already_shown

    if remaining_rows > 0:
        # Draw remaining dasa rows — skip first already_shown
        from astro_engine import build_bhuktis as bb
        today = date.today()
        skipped = 0
        W_inner = W - 2*M
        f  = get_font(lang)
        cols = [34*mm, 34*mm, 32*mm, 32*mm, 26*mm]
        # Header
        c.setFillColor(DARK_BG)
        c.rect(M, y-8*mm, W_inner, 8*mm, fill=1, stroke=0)
        draw_text_centered(c, lbl('dasa_bhukti', lang) + ' (contd.)', W/2, y-5.5*mm, 'Helvetica-Bold', 10, GOLD)
        y -= 8*mm
        # Header row
        c.setFillColor(BROWN_MID)
        c.rect(M, y-7*mm, W_inner, 7*mm, fill=1, stroke=0)
        x = M
        for i, h in enumerate([lbl('dasa',lang),lbl('bhukti',lang),lbl('start',lang),lbl('end',lang),lbl('status',lang)]):
            c.setFont(f, 8); c.setFillColor(GOLD_LIGHT)
            try: c.drawString(x+2*mm, y-5*mm, h)
            except: c.setFont('Helvetica',8); c.drawString(x+2*mm, y-5*mm, h.encode('ascii','replace').decode())
            x += cols[i]
        y -= 7*mm

        drawn = 0
        for drow in data['dasas']:
            bhuktis = bb(drow['dasa'], drow['start'], drow['end'])
            for brow in bhuktis:
                if skipped < already_shown:
                    skipped += 1; continue
                if y < 22*mm: break
                is_cur  = (brow['start'] <= today <= brow['end'])
                is_past = brow['end'] < today
                if is_cur:   bg, sc, st = colors.HexColor('#FFF3CD'), colors.HexColor('#8B6914'), lbl('current',lang)
                elif is_past: bg, sc, st = CREAM_DARK, BROWN_MID, lbl('completed',lang)
                else:         bg, sc, st = (CREAM if drawn%2==0 else CREAM_DARK), BLUE_ACCENT, lbl('upcoming',lang)
                c.setFillColor(bg); c.rect(M, y-6*mm, W_inner, 6*mm, fill=1, stroke=0)
                if is_cur: c.setFillColor(GOLD); c.rect(M, y-6*mm, 1.5*mm, 6*mm, fill=1, stroke=0)
                row_vals = [get_planet_name(drow['dasa'],lang), get_planet_name(brow['bhukti'],lang),
                            fmt_date(brow['start']), fmt_date(brow['end']), st]
                x = M
                for ci, val in enumerate(row_vals):
                    c.setFont('Helvetica-Bold' if is_cur else f, 7.5 if ci<2 else 7)
                    c.setFillColor(sc if ci==4 else BROWN_DARK)
                    try: c.drawString(x+2*mm, y-4.5*mm, val)
                    except: c.setFont('Helvetica',7); c.drawString(x+2*mm, y-4.5*mm, val.encode('ascii','replace').decode())
                    x += cols[ci]
                c.setStrokeColor(colors.HexColor('#DDDBC0')); c.setLineWidth(0.3)
                c.line(M, y-6*mm, M+W_inner, y-6*mm)
                y -= 6*mm; drawn += 1

    y -= 6*mm

    # Yogas
    if y > 60*mm:
        y = draw_yogas_section(c, data, y, lang)

    # Lucky details
    if y > 50*mm:
        y = draw_lucky_section(c, data, y, lang)

    c.showPage()
    c.save()
    buf.seek(0)
    return buf.read()
