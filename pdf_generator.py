"""
pdf_generator.py — HoroscopeGen PDF report.

Same content and order as the Excel workbook: summary, Vedic, divisional
charts, KP, ALP, dasa tables, notes. White pages for printing. Text is laid out with fpdf2
and shaped by HarfBuzz, with Noto fonts embedded, so Tamil and the other
Indian scripts are joined correctly instead of printing as boxes.
"""
import os

from fpdf import FPDF

import charts
import i18n

FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts')
SCRIPT_FONTS = {'tamil': 'NotoSansTamil', 'devanagari': 'NotoSansDevanagari', 'telugu': 'NotoSansTelugu',
                'kannada': 'NotoSansKannada', 'malayalam': 'NotoSansMalayalam', 'bengali': 'NotoSansBengali'}

INK = (43, 27, 14)
MUTED = (122, 106, 88)
BAND = (90, 42, 12)
HEAD = (138, 75, 20)
ACCENT = (200, 129, 26)
RULE = (201, 183, 156)
ALT = (251, 245, 234)
SOFT = (244, 231, 207)
LAGNA = (255, 226, 168)
CURRENT = (255, 241, 184)
WHITE = (255, 255, 255)

MARGIN = 12.0
PAGE_W = 210.0
BODY_W = PAGE_W - 2 * MARGIN
DATE = '%d-%m-%Y'
PURPOSE_H = 4.6            # height of one purpose line under a divisional chart's title


class Report(FPDF):
    def __init__(self, res, lang):
        super().__init__(orientation='P', unit='mm', format='A4')
        self.res, self.lang = res, lang
        self.set_margins(MARGIN, 16, MARGIN)
        self.set_auto_page_break(True, margin=16)
        self.add_font('main', '', os.path.join(FONT_DIR, 'NotoSans-Regular.ttf'))
        self.add_font('main', 'B', os.path.join(FONT_DIR, 'NotoSans-Bold.ttf'))
        script = i18n.script_of(lang)
        if script in SCRIPT_FONTS:
            base = SCRIPT_FONTS[script]
            self.add_font(script, '', os.path.join(FONT_DIR, f'{base}-Regular.ttf'))
            self.add_font(script, 'B', os.path.join(FONT_DIR, f'{base}-Bold.ttf'))
            self.set_fallback_fonts([script], exact_match=False)
        self.set_text_shaping(True)
        self.set_title(f"HoroscopeGen - {res['meta']['name']}")
        self.set_author('horoscopegen.in')
        self.set_creator('HoroscopeGen')
        self.alias_nb_pages()

    # -- text state ------------------------------------------------------------
    # When a piece of text needs the script (fallback) font, fpdf2 switches the
    # PDF's font for it but does not switch back, so the next Latin text would
    # be drawn with the wrong font's glyphs (digits and degrees turning into
    # stray letters). Wrapping every cell in its own graphics state confines
    # the switch to that cell.
    #
    # Shaping (HarfBuzz plus the bidirectional algorithm) is only needed for
    # the Indian scripts. Most cells hold numbers, dates and Latin text, so it
    # is switched off for those: this roughly halves the time to build a report.
    @staticmethod
    def _plain(text):
        return isinstance(text, str) and all(
            ord(ch) < 0x0590 or 0x2000 <= ord(ch) < 0x2400 for ch in text)

    def _unshaped(self, _text, fn, /, *args, **kwargs):
        if not self._plain(_text):
            return fn(*args, **kwargs)
        saved = self.text_shaping
        self.text_shaping = None
        try:
            return fn(*args, **kwargs)
        finally:
            self.text_shaping = saved

    def cell(self, *args, **kwargs):
        text = kwargs.get('text', args[2] if len(args) > 2 else '')
        with self.local_context():
            return self._unshaped(text, super().cell, *args, **kwargs)

    def multi_cell(self, *args, **kwargs):
        text = kwargs.get('text', args[2] if len(args) > 2 else '')
        if kwargs.get('dry_run'):
            return self._unshaped(text, super().multi_cell, *args, **kwargs)
        with self.local_context():
            return self._unshaped(text, super().multi_cell, *args, **kwargs)

    def get_string_width(self, s, *args, **kwargs):
        return self._unshaped(s, super().get_string_width, s, *args, **kwargs)

    # -- page furniture -------------------------------------------------------
    def header(self):
        self.set_font('main', 'B', 8)
        self.set_text_color(*BAND)
        self.set_xy(MARGIN, 7)
        self.cell(BODY_W / 2, 5, f"HoroscopeGen  ·  {i18n.L('report_title', self.lang)}")
        self.set_font('main', '', 8)
        self.set_text_color(*MUTED)
        self.cell(BODY_W / 2, 5, self.res['meta']['name'], align='R')
        self.set_draw_color(*ACCENT)
        self.set_line_width(0.4)
        self.line(MARGIN, 12.5, PAGE_W - MARGIN, 12.5)
        self.set_y(16)

    def footer(self):
        self.set_y(-12)
        self.set_font('main', '', 7)
        self.set_text_color(*MUTED)
        self.cell(BODY_W / 3, 5, 'horoscopegen.in')
        self.cell(BODY_W / 3, 5, f"{i18n.Lv('page', self.lang)} {self.page_no()} / {{nb}}", align='C')
        self.cell(BODY_W / 3, 5, self.res['meta']['generated_at'].strftime(DATE), align='R')

    # -- blocks ---------------------------------------------------------------
    def band(self, text, sub=None):
        self.set_fill_color(*BAND)
        self.set_text_color(*WHITE)
        self.set_font('main', 'B', 14)
        self.set_x(MARGIN)
        self.cell(BODY_W, 10, text, fill=True, align='C', new_x='LMARGIN', new_y='NEXT')
        if sub:
            self.set_fill_color(*SOFT)
            self.set_text_color(*MUTED)
            self.set_font('main', '', 8)
            self.cell(BODY_W, 6, self._fit(sub, BODY_W - 4), fill=True, align='C', new_x='LMARGIN', new_y='NEXT')
        self.ln(3)

    def section(self, text, x=MARGIN, w=BODY_W, need=30):
        """Section heading; starts a new page when fewer than `need` mm remain."""
        if self.get_y() + need > self.h - 16:
            self.add_page()
        self.set_x(x)
        self.set_fill_color(*HEAD)
        self.set_text_color(*WHITE)
        self.set_font('main', 'B', 9.5)
        self.cell(w, 6.5, '  ' + self._fit(text, w - 4), fill=True, new_x='LMARGIN', new_y='NEXT')

    def pairs(self, x, y, w, items, label_w=0.42, row_h=5.6):
        """Label / value box. Returns the y below it."""
        self.set_draw_color(*RULE)
        self.set_line_width(0.15)
        if self.lang == 'bi':
            label_w = max(label_w, 0.54)
        lw = w * label_w
        for label, value in items:
            self.set_xy(x, y)
            self.set_font('main', 'B', 7.6)
            self.set_text_color(*MUTED)
            self.set_fill_color(*SOFT)
            self.cell(lw, row_h, ' ' + self._fit(label, lw - 2), border=1, fill=True)
            self.set_font('main', '', 8.2)
            self.set_text_color(*INK)
            self.cell(w - lw, row_h, ' ' + self._fit(str(value), w - lw - 2), border=1)
            y += row_h
        return y

    def _fit(self, text, width):
        """Shrink the current font until text fits the width (never clips)."""
        size = self.font_size_pt
        while self.get_string_width(text) > width and size > 4.4:
            size -= 0.3
            self.set_font_size(size)
        return text

    def table(self, cols, rows, current=None, font_size=None, line_h=4.6, wrap=False):
        """
        cols: [(heading, relative width, align)]; rows: list of value lists.
        Headings repeat on every page and a row never splits across pages.
        Normal rows are one line each, with text shrunk to fit its column;
        wrap=True lays long text out on several lines (small tables only).
        """
        if font_size is None:
            # Indian scripts set wider than Latin; bilingual cells carry two names.
            font_size = {'en': 7.6, 'bi': 6.4}.get(self.lang, 7.0)
        total = sum(c[1] for c in cols)
        widths = [BODY_W * c[1] / total for c in cols]
        aligns = [c[2][0] for c in cols]
        has_head = any(c[0] for c in cols)
        bottom = self.h - 16
        self.set_draw_color(*RULE)
        self.set_line_width(0.15)

        def lines_for(text, w, style, size=None):
            self.set_font('main', style, size or font_size)
            return self.multi_cell(w, line_h, text, dry_run=True, output='LINES', padding=(0, 1))

        def head_size(text, w):
            """Largest size at which no single word of the heading has to be split."""
            size = font_size
            self.set_font('main', 'B', size)
            words = text.split() or ['']
            while size > 4.6 and max(self.get_string_width(x) for x in words) > w - 2.2:
                size -= 0.3
                self.set_font_size(size)
            return size

        def head_row():
            if not has_head:
                return
            sizes = [head_size(c[0], w) for c, w in zip(cols, widths)]
            counts = [len(lines_for(c[0], w, 'B', s)) for c, w, s in zip(cols, widths, sizes)]
            h = max(counts) * line_h + 1.6
            x, y = MARGIN, self.get_y()
            self.set_fill_color(*HEAD)
            self.set_text_color(*WHITE)
            for c, w, s, k in zip(cols, widths, sizes, counts):
                self.rect(x, y, w, h, style='DF')
                self.set_font('main', 'B', s)
                self.set_xy(x, y + (h - k * line_h) / 2)
                self.multi_cell(w, line_h, c[0], align='C', padding=(0, 1))
                x += w
            self.set_xy(MARGIN, y + h)

        head_row()
        for i, row in enumerate(rows):
            is_cur = bool(current) and i in current
            vals = ['' if v is None else str(v) for v in row]
            if wrap:
                counts = [len(lines_for(v, w, 'B' if (is_cur or (not has_head and j == 0)) else ''))
                          for j, (v, w) in enumerate(zip(vals, widths))]
                h = max(counts) * line_h + 1.4
            else:
                h = line_h + 0.6
            if self.get_y() + h > bottom:
                self.add_page()
                head_row()
            x, y = MARGIN, self.get_y()
            for j, (v, w, al) in enumerate(zip(vals, widths, aligns)):
                label = not has_head and j == 0
                self.set_fill_color(*(CURRENT if is_cur else SOFT if label else ALT if i % 2 else WHITE))
                self.set_text_color(*(MUTED if label else INK))
                self.set_font('main', 'B' if (is_cur or label) else '', font_size)
                if wrap:
                    self.rect(x, y, w, h, style='DF')
                    self.set_xy(x, y + 0.7)
                    self.multi_cell(w, line_h, v, align=al, padding=(0, 1))
                else:
                    # Measure only when the text could be too wide (saves shaping work).
                    if len(v) * font_size * 0.26 > w - 2:
                        self._fit(v, w - 2)
                    self.set_xy(x, y)
                    self.cell(w, h, v, border=1, fill=True, align=al)
                x += w
            self.set_xy(MARGIN, y + h)
        self.ln(3)

    # -- charts ---------------------------------------------------------------
    def chart(self, x, y, size, spec, style='south', purpose=None):
        """Title strip (and a purpose line when given) plus chart. Returns the y below it."""
        self.set_xy(x, y)
        self.set_fill_color(*HEAD)
        self.set_text_color(*WHITE)
        self.set_font('main', 'B', 8.5)
        self.cell(size, 5.5, self._fit(spec['title'], size - 2), fill=True, align='C')
        y += 5.5
        if purpose is not None:
            # one line per language, so bilingual text is not shrunk to fit a single line
            for line in ([purpose] if isinstance(purpose, str) else purpose):
                self.set_xy(x, y)
                self.set_fill_color(*SOFT)
                self.set_text_color(*MUTED)
                self.set_font('main', '', 7)
                self.cell(size, PURPOSE_H, self._fit(line, size - 2), fill=True, align='C')
                y += PURPOSE_H
        # Chart text is placed with cell() so the script fonts are used; a chart
        # near the foot of the page must not trigger an automatic page break.
        self.set_auto_page_break(False)
        if style == 'north':
            self._north(x, y, size, spec)
        else:
            self._south(x, y, size, spec)
        self.set_auto_page_break(True, margin=16)
        return y + size + 4

    def _put(self, x, y, w, h, text, align='L'):
        self.set_xy(x, y)
        self.cell(w, h, text, align=align)

    def _centered(self, cx, cy, lines, size_pt, bold=True, color=INK, lead=1.25, max_w=None):
        self.set_font('main', 'B' if bold else '', size_pt)
        if max_w:
            while size_pt > 5 and max(self.get_string_width(ln_) for ln_ in lines) > max_w:
                size_pt -= 0.3
                self.set_font_size(size_pt)
        self.set_text_color(*color)
        lh = size_pt * 0.3528 * lead
        y = cy - lh * len(lines) / 2
        for ln_ in lines:
            w = self.get_string_width(ln_) + 4
            self._put(cx - w / 2, y, w, lh, ln_, 'C')
            y += lh

    def _wrap(self, tokens, max_w, size_pt):
        """Greedy wrap of planet tokens into lines no wider than max_w."""
        self.set_font('main', 'B', size_pt)
        lines, cur = [], ''
        for t in tokens:
            trial = (cur + ' ' + t).strip()
            if cur and self.get_string_width(trial) > max_w:
                lines.append(cur)
                cur = t
            else:
                cur = trial
        if cur:
            lines.append(cur)
        return lines

    def _south(self, x, y, size, spec):
        c = size / 4.0
        self.set_line_width(0.2)
        self.set_draw_color(*INK)
        for cell in spec['signs']:
            gr, gc = charts.SOUTH_POS[cell['sign']]
            cx, cy = x + gc * c, y + gr * c
            if cell['lagna']:
                self.set_fill_color(*LAGNA)
                self.rect(cx, cy, c, c, style='DF')
            else:
                self.rect(cx, cy, c, c)
            self.set_font('main', 'B' if cell['lagna'] else '', 5.6)
            self.set_text_color(*MUTED)
            self._put(cx + 0.2, cy + 0.6, c / 2, 3, cell['label'], 'L')
            self._put(cx + c / 2, cy + 0.6, c / 2 - 0.2, 3, cell['tag'], 'R')
            size_pt = 8.4
            lines = self._wrap(cell['planets'], c - 2, size_pt)
            while len(lines) > 3 and size_pt > 6:
                size_pt -= 0.6
                lines = self._wrap(cell['planets'], c - 2, size_pt)
            if lines:
                self._centered(cx + c / 2, cy + c / 2 + 1.2, lines, size_pt)
        self.set_fill_color(*SOFT)
        self.rect(x + c, y + c, 2 * c, 2 * c, style='DF')
        self._centered(x + 2 * c, y + 2 * c, spec['center'], 8.2, color=BAND, max_w=2 * c - 3)
        self.set_line_width(0.5)
        self.rect(x, y, size, size)

    def _north(self, x, y, size, spec):
        self.set_draw_color(*INK)
        self.set_line_width(0.2)
        for (x1, y1), (x2, y2) in charts.NORTH_LINES:
            self.line(x + x1 * size, y + y1 * size, x + x2 * size, y + y2 * size)
        for h in spec['houses']:
            ax, ay, _ = charts.NORTH_HOUSES[h['house']]
            nx, ny = charts.NORTH_NUM[h['house']]
            diamond = h['house'] in (1, 4, 7, 10)
            side = h['house'] in (3, 5, 9, 11)
            if side:
                lines = h['planets']
                size_pt = 7.4 if len(lines) <= 4 else 6.2
            else:
                max_w = size * (0.30 if diamond else 0.26)
                size_pt = 8.2
                lines = self._wrap(h['planets'], max_w, size_pt)
                while len(lines) > (3 if diamond else 2) and size_pt > 5.8:
                    size_pt -= 0.6
                    lines = self._wrap(h['planets'], max_w, size_pt)
            if lines:
                self._centered(x + ax * size, y + ay * size, lines, size_pt)
            first = h['house'] == 1
            self._centered(x + nx * size, y + ny * size, [str(h['sign_num'])], 6.2, bold=first,
                           color=ACCENT if first else MUTED)
        self.set_line_width(0.5)
        self.rect(x, y, size, size)


# ── VALUE HELPERS ─────────────────────────────────────────────────────────────

def _state(p, lang):
    bits = []
    if p.get('retro'):
        bits.append(i18n.L('retro', lang))
    if p.get('combust'):
        bits.append(i18n.L('combust', lang))
    if p.get('dignity'):
        bits.append(i18n.word(p['dignity'], lang))
    return ', '.join(bits) if bits else '—'


def _status(row, now, lang):
    if row.get('current'):
        return i18n.L('current', lang)
    return i18n.L('completed', lang) if row['end'] <= now else i18n.L('upcoming', lang)


def _balance(bal, lang):
    return (f"{i18n.planet(bal['lord'], lang)}: {bal['y']} {i18n.Lv('y', lang)} "
            f"{bal['m']} {i18n.Lv('m', lang)} {bal['d']} {i18n.Lv('d', lang)}")


def _houses(nums):
    return ', '.join(str(n) for n in nums) if nums else '—'


def _points(v):
    """Rows of the planet table: lagna, the nine planets, then Mandi when available."""
    return v['planets'] + ([v['mandi']] if v.get('mandi') else [])


def _mandi_note(m, v):
    """Notes text explaining how Mandi was obtained for this chart."""
    base = ('Weekday ghati table for a 30-ghati day - Sunday 26, Monday 22, Tuesday 18, Wednesday 14, '
            'Thursday 10, Friday 6, Saturday 2 ghatis after sunrise; a night birth counts from sunset and '
            'uses the value of the 5th weekday from the birth weekday. The value is scaled to the actual '
            'length of the day or night, and Mandi is the lagna rising at that moment. Gulika is not shown.')
    md = v.get('mandi')
    if not md:
        return base + ' Mandi could not be computed for this chart: the Sun does not rise or set at this place on this date.'
    return (base + f" This chart: {'day' if md['is_day'] else 'night'} birth, {md['weekday']}, "
            f"{md['ghatis']} ghatis after {'sunrise' if md['is_day'] else 'sunset'} "
            f"({md['period_start'].strftime('%d-%m-%Y %H:%M:%S')}), rising at "
            f"{md['rise_time'].strftime('%d-%m-%Y %H:%M:%S')}.")


def _age(start, birth):
    return f"{(start - birth).days / 365.25:.2f}"


def _hm(dt):
    return dt.strftime('%H:%M:%S') if dt else '—'


# ── PAGES ─────────────────────────────────────────────────────────────────────

def _summary(pdf, specs):
    res, lang = pdf.res, pdf.lang
    m, v, kp, alp = res['meta'], res['vedic'], res['kp'], res['alp']
    L = lambda k: i18n.L(k, lang)
    pc, lagna, cur, al = v['panchangam'], v['planets'][0], v['dasa']['current'], alp['lagna']

    pdf.add_page()
    pdf.band(f"HoroscopeGen  ·  {L('report_title')}", f"{m['name']}  ·  {L('subtitle')}")
    half = (BODY_W - 4) / 2
    rx = MARGIN + half + 4

    pdf.section(L('birth_details'))
    y = pdf.get_y()
    left = [(L('name'), m['name']), (L('dob'), m['local_dt'].strftime(DATE)),
            (L('tob'), m['local_dt'].strftime('%H:%M:%S')), (L('pob'), m['pob']),
            (L('lat'), f"{m['lat']:.4f}°"), (L('lon'), f"{m['lon']:.4f}°")]
    if m.get('gender'):
        left.append((L('gender'), i18n.word(m['gender'].title(), lang)))
    right = [(L('tz'), f"{m['tz']} ({m['utc_offset_str']})"),
             (L('ayanamsha'), f"{m['ayanamsha_name']}  {v['ayanamsha_dms']}"),
             (L('kp_ayanamsha'), kp['ayanamsha_dms']),
             (L('nodes'), i18n.word('True' if m['node'] == 'true' else 'Mean', lang)),
             (L('sunrise'), _hm(pc['sunrise'])), (L('sunset'), _hm(pc['sunset']))]
    y = max(pdf.pairs(MARGIN, y, half, left), pdf.pairs(rx, y, half, right)) + 3

    pdf.set_y(y)
    pdf.section(L('core'))
    y = pdf.get_y()
    left = [(L('lagna'), f"{i18n.rasi(lagna['sign'], lang)}  {lagna['dms']}"),
            (L('janma_rasi'), i18n.rasi(v['moon_sign'], lang)),
            (L('nakshatra'), f"{i18n.nak(v['moon_nak'], lang)} - {i18n.Lv('pada', lang)} {v['moon_pada']}"),
            (L('nak_lord'), i18n.planet(v['dasa']['birth_star_lord'], lang)),
            (L('tithi'), f"{i18n.word(pc['paksha'], lang)} {i18n.tithi(pc['tithi'], lang)}"),
            (L('vara'), i18n.weekday(pc['vara'], lang))]
    md = v.get('mandi')
    if md:
        left.append((i18n.planet('Mandi', lang),
                     f"{i18n.rasi(md['sign'], lang)}  {md['dms']}  ({md['rise_time'].strftime('%H:%M:%S')})"))
    right = [(L('dasa_balance'), _balance(v['dasa']['balance'], lang))]
    for key, lab in (('dasa', 'dasa'), ('bhukti', 'bhukti'), ('antaram', 'antara')):
        if lab in cur:
            right.append((i18n.Lj(['current', key], lang),
                          f"{i18n.planet(cur[lab]['lord'], lang)}  ({i18n.Lv('until', lang)} "
                          f"{cur[lab]['end'].strftime(DATE)})"))
    right.append((L('alp_lagna_now'), f"{i18n.rasi(al['sign'], lang)}  {al['dms']}"))
    right.append((L('as_of'), m['generated_at'].strftime(DATE)))
    y = max(pdf.pairs(MARGIN, y, half, left), pdf.pairs(rx, y, half, right)) + 4

    size = min(half, (pdf.h - 18 - y - 2 * 10) / 2)
    off = (half - size) / 2
    style = m['chart_style']
    pdf.chart(MARGIN + off, y, size, specs['d1'], style)
    y2 = pdf.chart(rx + off, y, size, specs['d9'], style)
    pdf.chart(MARGIN + off, y2, size, specs['kp'], style)
    pdf.chart(rx + off, y2, size, specs['alp'], style)


def _vedic(pdf, specs):
    res, lang = pdf.res, pdf.lang
    m, v = res['meta'], res['vedic']
    L = lambda k: i18n.L(k, lang)
    P = lambda n: i18n.planet(n, lang)
    pc = v['panchangam']
    style = m['chart_style']

    pdf.add_page()
    pdf.band(f"{L('vedic')}  ·  {m['name']}", f"{L('ayanamsha')}: {m['ayanamsha_name']} {v['ayanamsha_dms']}")
    half = (BODY_W - 4) / 2
    rx = MARGIN + half + 4
    size = 78.0
    off = (half - size) / 2
    y = pdf.get_y()
    pdf.chart(MARGIN + off, y, size, specs['d1'], style)
    y = pdf.chart(rx + off, y, size, specs['d9'], style)
    y_after = pdf.chart(MARGIN + off, y, size, specs['bhava'], style)
    pdf.set_y(y)
    pdf.section(L('panchangam'), x=rx, w=half)
    pdf.pairs(rx, pdf.get_y(), half, [
        (L('tithi'), f"{i18n.word(pc['paksha'], lang)} {i18n.tithi(pc['tithi'], lang)}"),
        (L('vara'), i18n.weekday(pc['vara'], lang)),
        (L('nakshatra'), f"{i18n.nak(pc['nak'], lang)} - {i18n.Lv('pada', lang)} {pc['pada']}"),
        (L('yoga'), pc['yoga']), (L('karana'), pc['karana']),
        (L('sunrise'), _hm(pc['sunrise'])), (L('sunset'), _hm(pc['sunset'])),
        (L('mandi_rise'), _hm(v['mandi']['rise_time']) if v.get('mandi') else '—'),
        (L('dasa_balance'), _balance(v['dasa']['balance'], lang)),
    ], row_h=6.4)
    pdf.set_y(y_after)

    pdf.add_page()
    pdf.section(L('planet_positions'))
    cols = [(L('planet'), 12, 'LEFT'), (L('rasi'), 12, 'LEFT'), (L('degree'), 11, 'CENTER'),
            (L('nakshatra'), 15, 'LEFT'), (L('pada'), 7, 'CENTER'), (L('rasi_lord'), 11, 'LEFT'),
            (L('star_lord'), 11, 'LEFT'), (L('house'), 7, 'CENTER'), (L('bhava'), 7, 'CENTER'),
            (L('navamsa'), 11, 'LEFT'), (f"{L('retro')} / {L('combust')} / {L('dignity')}", 17, 'LEFT')]
    rows = [[P(p['name']), i18n.rasi(p['sign'], lang), p['dms'], i18n.nak(p['nak'], lang), p['pada'],
             P(p['sign_lord']), P(p['star_lord']), p['house'], p['bhava'], i18n.rasi(p['navamsa'], lang),
             _state(p, lang)] for p in _points(v)]
    pdf.table(cols, rows, wrap=lang == 'bi')

    pdf.section(L('bhava_table'), need=70)
    by_bhava = {}
    for p in _points(v):
        by_bhava.setdefault(p['bhava'], []).append(P(p['name']))
    cols = [(L('bhava'), 8, 'CENTER'), (L('bhava_start'), 26, 'LEFT'), (L('bhava_mid'), 26, 'LEFT'),
            (L('planet'), 40, 'LEFT')]
    rows = [[b['house'], f"{i18n.rasi(b['start_sign'], lang)}  {b['start_dms']}",
             f"{i18n.rasi(b['madhya_sign'], lang)}  {b['madhya_dms']}",
             ', '.join(by_bhava.get(b['house'], [])) or '—'] for b in v['bhavas']]
    pdf.table(cols, rows)


def _divisional(pdf):
    """Divisional charts: the table of signs with four charts, then six charts to a page."""
    res, lang = pdf.res, pdf.lang
    m = res['meta']
    L = lambda k: i18n.L(k, lang)
    vspecs = charts.build_varga_specs(res, lang)
    keys, rows = charts.varga_table(res, lang)
    style = m['chart_style']

    pdf.add_page()
    pdf.band(f"{L('divisional')}  ·  {m['name']}", L('varga_time_note'))
    pdf.section(L('varga_table'))
    cols = [(L('planet'), 13, 'LEFT')] + [(k, 5, 'CENTER') for k in keys] + [(L('vargottama'), 9, 'CENTER')]
    yes = i18n.word('Yes', lang)
    pdf.table(cols, [[row['label']] + row['signs'] + [yes if row['vargottama'] else '—'] for row in rows],
              font_size=6.6 if lang == 'en' else 6.0)
    pdf.set_y(pdf.get_y() - 2)
    pdf.set_font('main', '', 7)
    pdf.set_text_color(*MUTED)
    pdf.cell(BODY_W, 4, L('vargottama_note'), new_x='LMARGIN', new_y='NEXT')
    pdf.ln(2)

    half = (BODY_W - 4) / 2

    n_lines = 2 if lang == 'bi' else 1         # bilingual: English line, then Tamil line
    extra = 5.5 + n_lines * PURPOSE_H + 4      # title strip, purpose lines, gap below

    def draw(group, y, size):
        """Draw charts two to a row starting at y."""
        off = (half - size) / 2
        for i, spec in enumerate(group):
            x = MARGIN + off if i % 2 == 0 else MARGIN + half + 4 + off
            lines = spec['purpose'].split(' / ', 1) if lang == 'bi' else spec['purpose']
            nxt = pdf.chart(x, y, size, spec, style, purpose=lines)
            if i % 2 == 1:
                y = nxt
        return y

    # First page: whatever height is left takes two rows of charts.
    y = pdf.get_y()
    full = (pdf.h - 16 - 16) / 3 - extra       # three rows fill a page
    draw(vspecs[:4], y, min(full, (pdf.h - 16 - y) / 2 - extra))
    for start in (4, 10):                      # then six to a page
        pdf.add_page()
        draw(vspecs[start:start + 6], pdf.get_y(), full)


def _kp(pdf, specs):
    res, lang = pdf.res, pdf.lang
    m, kp = res['meta'], res['kp']
    L = lambda k: i18n.L(k, lang)
    P = lambda n: i18n.planet(n, lang)
    now = m['generated_at']

    pdf.add_page()
    pdf.band(f"{L('kp')}  ·  {m['name']}",
             f"{L('kp_ayanamsha')}: {kp['ayanamsha_dms']}  ·  {L('house_system')}: {i18n.word(kp['house_system'], lang)}")
    half = (BODY_W - 4) / 2
    rx = MARGIN + half + 4
    size = 78.0
    y = pdf.get_y()
    y_after = pdf.chart(MARGIN + (half - size) / 2, y, size, specs['kp'], m['chart_style'])
    rp = kp['ruling_planets']
    pdf.set_y(y)
    pdf.section(L('ruling_planets'), x=rx, w=half)
    pdf.pairs(rx, pdf.get_y(), half, [(L(k), P(rp[k])) for k in (
        'day_lord', 'moon_sign_lord', 'moon_star_lord', 'moon_sub_lord',
        'lagna_sign_lord', 'lagna_star_lord', 'lagna_sub_lord')], label_w=0.55, row_h=6.4)
    pdf.set_y(y_after)

    pdf.section(L('node_agents'))
    pdf.table([(L('node'), 14, 'LEFT'), (L('rasi_lord'), 18, 'LEFT'), (L('star_lord'), 18, 'LEFT'),
               (L('conjoined'), 50, 'LEFT')],
              [[P(a['node']), P(a['sign_lord']), P(a['star_lord']), i18n.planets(a['conjoined'], lang)]
               for a in kp['node_agents']])

    pdf.section(L('cusps'), need=75)
    cols = [(L('cusp'), 7, 'CENTER'), (L('rasi'), 14, 'LEFT'), (L('degree'), 12, 'CENTER'),
            (L('nakshatra'), 19, 'LEFT'), (L('rasi_lord'), 12, 'LEFT'), (L('star_lord'), 12, 'LEFT'),
            (L('sub_lord'), 12, 'LEFT'), (L('subsub_lord'), 12, 'LEFT')]
    pdf.table(cols, [[c['house'], i18n.rasi(c['sign'], lang), c['dms'], i18n.nak(c['nak'], lang),
                      P(c['sign_lord']), P(c['star_lord']), P(c['sub_lord']), P(c['subsub_lord'])]
                     for c in kp['cusps']], wrap=lang == 'bi')

    pdf.section(L('kp_planets'), need=65)
    cols = [(L('planet'), 12, 'LEFT'), (L('rasi'), 12, 'LEFT'), (L('degree'), 11, 'CENTER'),
            (L('nakshatra'), 16, 'LEFT'), (L('rasi_lord'), 10, 'LEFT'), (L('star_lord'), 10, 'LEFT'),
            (L('sub_lord'), 10, 'LEFT'), (L('subsub_lord'), 10, 'LEFT'), (L('house'), 6, 'CENTER'),
            (L('retro'), 7, 'CENTER')]
    pdf.table(cols, [[P(p['name']), i18n.rasi(p['sign'], lang), p['dms'], i18n.nak(p['nak'], lang),
                      P(p['sign_lord']), P(p['star_lord']), P(p['sub_lord']), P(p['subsub_lord']), p['house'],
                      i18n.retro_mark(lang).strip('()') if p['retro'] else '—'] for p in kp['planets']],
              wrap=lang == 'bi')

    pdf.section(L('planet_sig'), need=65)
    cols = [(L('planet'), 13, 'LEFT'), (L('star_lord'), 13, 'LEFT'), (L('sub_lord'), 13, 'LEFT'),
            (L('level1'), 15, 'CENTER'), (L('level2'), 15, 'CENTER'), (L('level3'), 15, 'CENTER'),
            (L('level4'), 15, 'CENTER')]
    pdf.table(cols, [[P(s['planet']), P(s['star_lord']), P(s['sub_lord']), _houses(s['l1']), _houses(s['l2']),
                      _houses(s['l3']), _houses(s['l4'])] for s in kp['planet_significators']], wrap=True)

    pdf.section(L('house_sig'), need=80)
    cols = [(L('house'), 7, 'CENTER'), (L('sig_a'), 29, 'LEFT'), (L('sig_b'), 24, 'LEFT'),
            (L('sig_c'), 27, 'LEFT'), (L('sig_d'), 13, 'LEFT')]
    pdf.table(cols, [[s['house'], i18n.planets(s['a'], lang), i18n.planets(s['b'], lang),
                      i18n.planets(s['c'], lang), i18n.planets(s['d'], lang)] for s in kp['house_significators']],
              wrap=True)

    pdf.add_page()
    pdf.section(f"{L('kp_dasa')}  ·  {L('dasa_balance')}: {_balance(kp['dasa']['balance'], lang)}")
    _dasa_bhukti_table(pdf, kp['dasa'], m, now)


def _dasa_bhukti_table(pdf, dasa, m, now):
    lang = pdf.lang
    L = lambda k: i18n.L(k, lang)
    P = lambda n: i18n.planet(n, lang)
    cols = [(L('dasa'), 18, 'LEFT'), (L('bhukti'), 18, 'LEFT'), (L('start'), 16, 'CENTER'),
            (L('end'), 16, 'CENTER'), (L('age'), 12, 'CENTER'), (L('status'), 20, 'CENTER')]
    rows, current = [], set()
    for d in dasa['dasas']:
        for b in d['sub']:
            if b['current']:
                current.add(len(rows))
            rows.append([P(d['lord']), P(b['lord']), b['start'].strftime(DATE), b['end'].strftime(DATE),
                         _age(b['start'], m['local_dt']), _status(b, now, lang)])
    pdf.table(cols, rows, current=current)


def _alp(pdf, specs):
    res, lang = pdf.res, pdf.lang
    m, v, alp = res['meta'], res['vedic'], res['alp']
    L = lambda k: i18n.L(k, lang)
    P = lambda n: i18n.planet(n, lang)
    now = m['generated_at']
    al, lagna = alp['lagna'], v['planets'][0]

    pdf.add_page()
    pdf.band(f"{L('alp_title')}  ·  {m['name']}", alp['rate'])
    half = (BODY_W - 4) / 2
    rx = MARGIN + half + 4
    size = 78.0
    y = pdf.get_y()
    y_after = pdf.chart(MARGIN + (half - size) / 2, y, size, specs['alp'], m['chart_style'])
    pdf.set_y(y)
    pdf.section(L('alp_lagna_now'), x=rx, w=half)
    pdf.pairs(rx, pdf.get_y(), half, [
        (L('alp_birth_lagna'), f"{i18n.rasi(lagna['sign'], lang)}  {lagna['dms']}"),
        (L('as_of'), now.strftime(DATE)),
        (L('age'), f"{alp['age_years']:.2f} {i18n.Lv('years', lang)}"),
        (L('alp_lagna_now'), f"{i18n.rasi(al['sign'], lang)}  {al['dms']}"),
        (L('nakshatra'), f"{i18n.nak(al['nak'], lang)} - {i18n.Lv('pada', lang)} {al['pada']}"),
        (L('rasi_lord'), P(al['sign_lord'])), (L('star_lord'), P(al['star_lord'])),
        (L('sub_lord'), P(al['sub_lord'])),
    ], row_h=6.4)
    pdf.set_y(y_after)

    pdf.section(L('alp_sign_periods'), need=80)
    cols = [(L('from'), 15, 'CENTER'), (L('to'), 15, 'CENTER'), (L('age_from'), 11, 'CENTER'),
            (L('age_to'), 11, 'CENTER'), (L('rasi'), 17, 'LEFT'), (L('rasi_lord'), 16, 'LEFT'),
            (L('status'), 15, 'CENTER')]
    rows, current = [], set()
    for s in alp['sign_periods']:
        if s['current']:
            current.add(len(rows))
        rows.append([s['start'].strftime(DATE), s['end'].strftime(DATE), f"{s['age_from']:.2f}",
                     f"{s['age_to']:.2f}", i18n.rasi(s['sign'], lang), P(s['sign_lord']), _status(s, now, lang)])
    pdf.table(cols, rows, current=current)

    pdf.add_page()
    pdf.section(L('alp_pada_periods'))
    cols = [(L('from'), 12, 'CENTER'), (L('to'), 12, 'CENTER'), (L('age_from'), 8, 'CENTER'),
            (L('age_to'), 8, 'CENTER'), (L('rasi'), 12, 'LEFT'), (L('nakshatra'), 16, 'LEFT'),
            (L('pada'), 6, 'CENTER'), (L('rasi_lord'), 10, 'LEFT'), (L('star_lord'), 10, 'LEFT'),
            (L('status'), 12, 'CENTER')]
    rows, current = [], set()
    for s in alp['pada_periods']:
        if s['current']:
            current.add(len(rows))
        rows.append([s['start'].strftime(DATE), s['end'].strftime(DATE), f"{s['age_from']:.2f}",
                     f"{s['age_to']:.2f}", i18n.rasi(s['sign'], lang), i18n.nak(s['nak'], lang), s['pada'],
                     P(s['sign_lord']), P(s['star_lord']), _status(s, now, lang)])
    pdf.table(cols, rows, current=current)


def _dasa(pdf):
    res, lang = pdf.res, pdf.lang
    m, v = res['meta'], res['vedic']
    L = lambda k: i18n.L(k, lang)
    P = lambda n: i18n.planet(n, lang)
    now = m['generated_at']
    dasa = v['dasa']

    pdf.add_page()
    pdf.band(f"{L('vim_dasa')}  ·  {m['name']}",
             f"{L('dasa_balance')}: {_balance(dasa['balance'], lang)}  ·  {L('ayanamsha')}: {m['ayanamsha_name']}")
    pdf.section(f"{L('dasa')} / {L('bhukti')}")
    _dasa_bhukti_table(pdf, dasa, m, now)

    # Antaram detail for the dasa now running (or the first one for a future birth date)
    cd = next((d for d in dasa['dasas'] if d['current']), dasa['dasas'][0])
    pdf.add_page()
    pdf.section(f"{L('antaram')}  ·  {P(cd['lord'])} {L('dasa')}  "
                f"({cd['start'].strftime(DATE)} - {cd['end'].strftime(DATE)})")
    cols = [(L('bhukti'), 18, 'LEFT'), (L('antaram'), 18, 'LEFT'), (L('start'), 16, 'CENTER'),
            (L('end'), 16, 'CENTER'), (L('age'), 12, 'CENTER'), (L('status'), 20, 'CENTER')]
    rows, current = [], set()
    for b in cd['sub']:
        for a in b['sub']:
            if a['current']:
                current.add(len(rows))
            rows.append([P(b['lord']), P(a['lord']), a['start'].strftime(DATE), a['end'].strftime(DATE),
                         _age(a['start'], m['local_dt']), _status(a, now, lang)])
    pdf.table(cols, rows, current=current)


def _notes(pdf):
    res, lang = pdf.res, pdf.lang
    m, v, kp = res['meta'], res['vedic'], res['kp']
    L = lambda k: i18n.L(k, lang)
    pdf.add_page()
    pdf.band(f"{L('notes')}  ·  {m['name']}")
    pdf.section(L('how_calculated'))
    node = 'True node' if m['node'] == 'true' else 'Mean node'
    items = [
        ('Ephemeris', f"{m['engine']}. Positions are geocentric, apparent, sidereal."),
        ('Birth moment', f"Local time {m['local_dt'].strftime('%d-%m-%Y %H:%M:%S')} at {m['tz']} "
                         f"({m['utc_offset_str']}) = UT {m['ut_dt'].strftime('%d-%m-%Y %H:%M:%S')}; "
                         f"Julian day (UT) {m['jd_ut']}."),
        ('Place', f"{m['pob']} - latitude {m['lat']:.4f}°, longitude {m['lon']:.4f}°. If these are not the "
                  'birth place, the lagna and house cusps will be wrong.'),
        ('Vedic ayanamsha', f"{m['ayanamsha_name']}: {v['ayanamsha_dms']} at birth."),
        ('KP ayanamsha', f"Krishnamurti: {kp['ayanamsha_dms']} at birth. The KP pages use this value "
                         'throughout, so KP positions differ slightly from the Vedic pages.'),
        ('Rahu / Ketu', f"{node}. Ketu is exactly opposite Rahu."),
        ('Vedic houses', 'House = whole sign counted from the lagna sign. Bhava = Sripati: the Porphyry cusps '
                         'are the bhava centres and each bhava begins midway between two centres.'),
        ('KP houses', f"{kp['house_system']} cusps; a planet belongs to the house whose cusp it has passed. "
                      'Star, sub and sub-sub lords divide each nakshatra in Vimshottari proportion.'),
        ('KP significators', 'Planet levels 1-4: house occupied by its star lord; house it occupies; houses '
                             'owned by its star lord; houses it owns. House levels A-D: planets in the star of '
                             'occupants; occupants; planets in the star of the owner; the owner. Rahu and Ketu '
                             'own no houses and also act for their sign lord and for planets in the same sign.'),
        ('Vimshottari', f"Year of {m['year_days']} days. Balance at birth from the Moon's position in its "
                        'nakshatra. Periods that ended before birth are not listed. The Excel workbook lists '
                        'antaram for every dasa; this PDF lists it for the dasa now running.'),
        ('Panchangam', 'Tithi, yoga and karana at the birth moment. Sunrise and sunset are for the visible '
                       'upper limb with standard refraction. The weekday runs from sunrise to sunrise.'),
        ('Mandi', _mandi_note(m, v)),
        ('Combustion', 'Orbs from the Sun: Moon 12°, Mars 17°, Mercury 14° (12° retrograde), Jupiter 11°, '
                       'Venus 10° (8° retrograde), Saturn 15°.'),
        ('Dignity', 'Only exaltation, debilitation and own sign are marked.'),
        ('ALP', 'Akshaya Lagna Paddhati: the birth lagna advances 30° every 10 years (3° a year), so one '
                f"nakshatra pada lasts 1 year 1 month 10 days. Year of {m['year_days']} days."),
        ('Generated', m['generated_at'].strftime('%d-%m-%Y %H:%M') + f" ({m['utc_offset_str']})"),
    ]
    pdf.table([('', 22, 'LEFT'), ('', 78, 'LEFT')], items, font_size=8, line_h=4.8, wrap=True)

    pdf.section(L('divisional'), need=60)
    en = i18n.LABELS['en']
    items = [(L('tob'), L('varga_time_note') if lang in ('ta', 'hi', 'mr', 'bi') else en['varga_time_note'])]
    items += [(i18n.varga_name(vg['key'], lang), vg['rule']) for vg in v['vargas']]
    items.append((L('vargottama'), en['vargottama_note']))
    pdf.table([('', 22, 'LEFT'), ('', 78, 'LEFT')], items, font_size=8, line_h=4.8, wrap=True)

    pdf.section(L('abbreviations'), need=45)
    names = ['Lagna', 'Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu', 'Mandi', 'ALP']
    items = [
        (L('planet'), '   '.join(f"{i18n.abbr(n, lang)} = "
                                 f"{i18n.planet(n, lang) if n != 'ALP' else L('alp_lagna_now')}" for n in names)),
        (L('retro'), f"{i18n.retro_mark(lang)} after a planet = retrograde"),
        (L('rasi'), '   '.join(f"{i + 1} = {i18n.rasi(i, lang)}" for i in range(12))),
        (L('kp_chart'), 'Roman numerals I-XII mark the sign in which each house cusp falls.'),
    ]
    pdf.table([('', 22, 'LEFT'), ('', 78, 'LEFT')], items, font_size=8, line_h=4.8, wrap=True)
    # Closing disclaimer: keep it whole, never one stray word on a new page.
    pdf.set_font('main', '', 7.5)
    pdf.set_text_color(*MUTED)
    need = len(pdf.multi_cell(BODY_W, 4.5, L('disclaimer'), dry_run=True, output='LINES')) * 4.5
    if pdf.get_y() + need > pdf.h - 13:
        pdf.add_page()
    pdf.set_auto_page_break(False)
    pdf.multi_cell(BODY_W, 4.5, L('disclaimer'), align='C')
    pdf.set_auto_page_break(True, margin=16)


# ── ENTRY POINT ───────────────────────────────────────────────────────────────

def generate_pdf(res, lang=None):
    """Build the PDF from compute() output. Returns bytes."""
    lang = lang or res['meta'].get('lang', 'en')
    if lang not in i18n.LANGS:
        lang = 'en'
    specs = charts.build_specs(res, lang)
    pdf = Report(res, lang)
    _summary(pdf, specs)
    _vedic(pdf, specs)
    _divisional(pdf)
    _kp(pdf, specs)
    _alp(pdf, specs)
    _dasa(pdf)
    _notes(pdf)
    return bytes(pdf.output())
