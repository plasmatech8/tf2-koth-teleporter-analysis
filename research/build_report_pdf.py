from __future__ import annotations

import html
import re
import sys
from datetime import date
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    HRFlowable,
    Image,
    KeepTogether,
    LongTable,
    PageBreak,
    PageTemplate,
    Paragraph,
    Preformatted,
    XPreformatted,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.tableofcontents import TableOfContents


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "TF2_KOTH_Teleporter_Report.md"
REPORT_VERSION = "1.5.17"
REPORT_DATE = "13 September 2026"
REPORT_TITLE = "Teleporter reinforcement value in Highlander KOTH"
DARK_MODE = "--dark" in sys.argv
output_override = next((arg.split("=", 1)[1] for arg in sys.argv[1:] if arg.startswith("--output=")), None)
OUTPUT = Path(output_override) if output_override else ROOT / "output" / "pdf" / (
    "TF2_KOTH_Teleporter_Report_Soft_Dark.pdf" if DARK_MODE else "TF2_KOTH_Teleporter_Report_Light.pdf"
)

PAGE_W, PAGE_H = A4
LEFT = 17 * mm
RIGHT = 17 * mm
TOP = 18 * mm
BOTTOM = 17 * mm
CONTENT_W = PAGE_W - LEFT - RIGHT

CONSOLAS_REGULAR = Path(r"C:\Windows\Fonts\consola.ttf")
CONSOLAS_BOLD = Path(r"C:\Windows\Fonts\consolab.ttf")
if CONSOLAS_REGULAR.exists() and CONSOLAS_BOLD.exists():
    pdfmetrics.registerFont(TTFont("Consolas", str(CONSOLAS_REGULAR)))
    pdfmetrics.registerFont(TTFont("Consolas-Bold", str(CONSOLAS_BOLD)))
    CODE_FONT = "Consolas"
else:
    CODE_FONT = "Courier"

if DARK_MODE:
    PAGE_BG = colors.HexColor("#2B3035")
    NAVY = colors.HexColor("#D6D1C7")
    TABLE_HEADER = colors.HexColor("#3B4B55")
    TABLE_HEADER_TEXT = colors.HexColor("#DED9CF")
    BLUE = colors.HexColor("#78B1CC")
    LIGHT_BLUE = colors.HexColor("#354249")
    GREEN = colors.HexColor("#83B99A")
    GOLD = colors.HexColor("#CDA554")
    RED = colors.HexColor("#D17A70")
    SLATE = colors.HexColor("#AAB0B4")
    GRID = colors.HexColor("#59636A")
    LIGHT = colors.HexColor("#343A3F")
    TABLE_ROWS = [colors.HexColor("#2F353A"), colors.HexColor("#353C42")]
    RESULT_ROW_BG = colors.HexColor("#34443D")
    BOLD_TEXT = colors.HexColor("#F1EDE5")
    ADVANTAGE_COLOURS = {
        "-4": "#B96861",
        "-3": "#C27067",
        "-2": "#D17A70",
        "-1": "#E18A7E",
        "+1": "#78B1CC",
        "+2": "#78C292",
        "+3": "#A5D77B",
        "+4": "#CFDA83",
    }
else:
    PAGE_BG = colors.white
    NAVY = colors.HexColor("#243442")
    TABLE_HEADER = NAVY
    TABLE_HEADER_TEXT = colors.white
    BLUE = colors.HexColor("#17678F")
    LIGHT_BLUE = colors.HexColor("#EAF3F7")
    GREEN = colors.HexColor("#2F7D58")
    GOLD = colors.HexColor("#C28B1F")
    RED = colors.HexColor("#A9443A")
    SLATE = colors.HexColor("#5D6B78")
    GRID = colors.HexColor("#CCD7DE")
    LIGHT = colors.HexColor("#F4F7F9")
    TABLE_ROWS = [colors.white, LIGHT]
    RESULT_ROW_BG = colors.HexColor("#EAF4EE")
    BOLD_TEXT = colors.HexColor("#152733")
    ADVANTAGE_COLOURS = {
        "-4": "#7E2E28",
        "-3": "#8E3730",
        "-2": "#9E4037",
        "-1": "#AD4B41",
        "+1": "#17678F",
        "+2": "#2F7D58",
        "+3": "#4C8E42",
        "+4": "#6F8E29",
    }


def ascii_safe(value: str) -> str:
    replacements = {
        "\u2010": "-",
        "\u2011": "-",
        "\u2012": "-",
        "\u2013": "-",
        "\u2014": "-",
        "\u2212": "-",
        "\u00d7": "x",
        "\u2248": "~",
        "\u2265": ">=",
        "\u2264": "<=",
        "\u2153": "1/3",
        "\u201c": '"',
        "\u201d": '"',
        "\u2018": "'",
        "\u2019": "'",
        "\u2026": "...",
        "\u00a0": " ",
    }
    for old, new in replacements.items():
        value = value.replace(old, new)
    return value


def inline_markup(value: str) -> str:
    value = ascii_safe(value)
    tokens: list[str] = []

    def stash(fragment: str) -> str:
        tokens.append(fragment)
        return f"@@TOKEN{len(tokens) - 1}@@"

    value = re.sub(r"<br\s*/?>", lambda _: stash("<br/>"), value, flags=re.IGNORECASE)
    value = re.sub(
        # Permit sentence punctuation after an advantage value (for example,
        # "+1.") without matching the integer part of a decimal such as "+1.4".
        r"(?<![\d.])([+-][1-4])(?!\d|\.\d)",
        lambda m: stash(f'<font color="{ADVANTAGE_COLOURS[m.group(1)]}">{m.group(1)}</font>'),
        value,
    )
    # Colour only the player-state sense of “even”. Ordinary prose such as
    # “even though” should retain the body colour.
    value = re.sub(
        r"\beven\b(?=(?:\s+for\b|\s+players\b|\*\*))",
        lambda m: stash(f'<font color="#{SLATE.hexval()[2:]}">{m.group(0)}</font>'),
        value,
    )
    value = re.sub(
        r"([+-]\d+(?:\.\d+)?)(?=\s+p·s)",
        lambda m: stash(
            f'<font color="#{(RED if float(m.group(1)) < 0 else SLATE if float(m.group(1)) == 0 else GREEN).hexval()[2:]}">{m.group(1)}</font>'
        ),
        value,
    )
    value = re.sub(
        r"\[([^\]]+)\]\((https?://[^)]+)\)",
        lambda m: stash(f'<link href="{html.escape(m.group(2), quote=True)}" color="#{BLUE.hexval()[2:]}">{html.escape(m.group(1))}</link>'),
        value,
    )
    value = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", lambda m: stash(f"<i>{html.escape(m.group(1))}</i>"), value)
    value = re.sub(r"`([^`]+)`", lambda m: stash(f'<font name="{CODE_FONT}">{html.escape(m.group(1))}</font>'), value)
    value = html.escape(value)
    value = re.sub(r"\*\*([^*]+)\*\*", rf'<font color="#{BOLD_TEXT.hexval()[2:]}"><b>\1</b></font>', value)
    value = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<i>\1</i>", value)
    for index, token in reversed(list(enumerate(tokens))):
        value = value.replace(f"@@TOKEN{index}@@", token)
    return value


styles = getSampleStyleSheet()
body = ParagraphStyle(
    "Body",
    parent=styles["BodyText"],
    fontName="Helvetica",
    fontSize=9.25,
    leading=13.0,
    textColor=NAVY,
    spaceAfter=5.5,
)
lead = ParagraphStyle(
    "Lead",
    parent=body,
    fontSize=11.2,
    leading=15.2,
    textColor=SLATE,
    alignment=TA_CENTER,
)
h1 = ParagraphStyle(
    "H1",
    parent=styles["Title"],
    fontName="Helvetica-Bold",
    fontSize=27,
    leading=31,
    textColor=NAVY,
    alignment=TA_CENTER,
    spaceAfter=9,
)
h2 = ParagraphStyle(
    "H2",
    parent=styles["Heading2"],
    fontName="Helvetica-Bold",
    fontSize=16,
    leading=20,
    textColor=BLUE,
    spaceBefore=11,
    spaceAfter=6,
    keepWithNext=True,
)
h3 = ParagraphStyle(
    "H3",
    parent=styles["Heading3"],
    fontName="Helvetica-Bold",
    fontSize=11.5,
    leading=14,
    textColor=GREEN,
    spaceBefore=8,
    spaceAfter=4,
    keepWithNext=True,
)
bullet = ParagraphStyle(
    "Bullet",
    parent=body,
    leftIndent=12,
    firstLineIndent=-7,
    bulletIndent=2,
    spaceAfter=3,
)
quote = ParagraphStyle(
    "Quote",
    parent=body,
    leftIndent=12,
    rightIndent=12,
    borderColor=BLUE,
    borderWidth=0,
    borderPadding=(5, 8, 5, 8),
    backColor=LIGHT_BLUE,
    fontName="Helvetica-Oblique",
    fontSize=10.2,
    leading=14,
    spaceBefore=3,
    spaceAfter=7,
)
code_style = ParagraphStyle(
    "Code",
    parent=body,
    fontName=CODE_FONT,
    fontSize=7.35,
    leading=10.1,
    leftIndent=8,
    rightIndent=8,
    borderPadding=7,
    backColor=LIGHT,
    textColor=NAVY,
    spaceBefore=10,
    spaceAfter=12,
)
caption = ParagraphStyle(
    "Caption",
    parent=body,
    fontSize=7.7,
    leading=10,
    textColor=SLATE,
    alignment=TA_CENTER,
    spaceAfter=8,
)
toc_h = ParagraphStyle(
    "TOCHeading",
    parent=h1,
    fontSize=22,
    leading=26,
    alignment=TA_LEFT,
)


class ReportDocTemplate(BaseDocTemplate):
    def __init__(self, filename: str):
        super().__init__(
            filename,
            pagesize=A4,
            leftMargin=LEFT,
            rightMargin=RIGHT,
            topMargin=TOP,
            bottomMargin=BOTTOM,
            title=REPORT_TITLE,
            author="plasmatech8",
            subject=f"Report v{REPORT_VERSION} | {REPORT_DATE} | Reinforcement value and after-wipe destruction policy",
        )
        frame = Frame(LEFT, BOTTOM, CONTENT_W, PAGE_H - TOP - BOTTOM, id="body")
        self.addPageTemplates(PageTemplate(id="report", frames=[frame], onPage=self.draw_page))

    def draw_page(self, canvas, doc):
        canvas.saveState()
        canvas.setFillColor(PAGE_BG)
        canvas.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
        if doc.page > 1:
            canvas.setStrokeColor(GRID)
            canvas.setLineWidth(0.5)
            canvas.line(LEFT, PAGE_H - 12 * mm, PAGE_W - RIGHT, PAGE_H - 12 * mm)
            canvas.setFont("Helvetica", 7.5)
            canvas.setFillColor(SLATE)
            canvas.drawString(LEFT, PAGE_H - 9.2 * mm, "TF2 KOTH teleporter analysis")
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(SLATE)
        canvas.drawString(LEFT, 8.5 * mm, f"v{REPORT_VERSION} | {REPORT_DATE}")
        canvas.drawRightString(PAGE_W - RIGHT, 8.5 * mm, str(doc.page))
        canvas.restoreState()

    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph) and flowable.style.name in {"H2", "H3"}:
            level = 0 if flowable.style.name == "H2" else 1
            text = flowable.getPlainText()
            key = f"section-{self.seq.nextf('heading')}"
            self.canv.bookmarkPage(key)
            self.canv.addOutlineEntry(text, key, level=level, closed=False)
            if level == 0:
                self.notify("TOCEntry", (level, text, self.page, key))


def make_table(rows: list[list[str]]) -> LongTable:
    columns = len(rows[0])
    is_main_comparison = columns == 8 and rows[0][0].strip() == "Case" and any("Keep L3" in c for c in rows[0])
    is_arrival_table = columns == 8 and rows[0][0].strip() == "Case" and "Defence L3 arrivals" in rows[0][3]
    is_decision_factors = columns == 3 and rows[0][0].strip() == "Situation or factor"
    font_size = 5.5 if is_main_comparison else 5.3 if is_arrival_table else 7.25 if is_decision_factors else 7.2 if columns >= 6 else 7.7 if columns == 5 else 8.0
    cell_leading = 6.9 if is_main_comparison else 6.7 if is_arrival_table else 9.35 if is_decision_factors else font_size + 2.4
    cell_style = ParagraphStyle(
        f"TableCell{columns}",
        parent=body,
        fontSize=font_size,
        leading=cell_leading,
        spaceAfter=0,
    )
    header_style = ParagraphStyle(
        f"TableHeader{columns}",
        parent=cell_style,
        fontName="Helvetica-Bold",
        textColor=TABLE_HEADER_TEXT,
    )
    clean_rows = []
    for row_index, row in enumerate(rows):
        rendered = []
        for cell in row:
            markup = inline_markup(cell.strip())
            if row_index == 0:
                # Bold/advantage inline colours must not override header contrast.
                markup = re.sub(r'color="#[0-9A-Fa-f]{6}"',
                    f'color="#{TABLE_HEADER_TEXT.hexval()[2:]}"', markup)
            rendered.append(Paragraph(markup, header_style if row_index == 0 else cell_style))
        clean_rows.append(rendered)
    max_chars = [max(len(ascii_safe(row[index])) for row in rows) for index in range(columns)]
    if is_main_comparison:
        weights = [28, 46, 48, 68, 68, 68, 68, 66]
    elif is_arrival_table:
        weights = [28, 47, 48, 58, 56, 56, 56, 56]
    elif columns == 2 and rows[0][0] == "Assumption":
        weights = [25, 75]
    elif columns == 2 and rows[0][0].startswith("Quantity"):
        weights = [38, 62]
    elif columns == 2 and rows[0][0] == "Factor":
        weights = [30, 70]
    elif is_decision_factors:
        weights = [22, 39, 39]
    else:
        weights = [max(5, min(value, 34)) for value in max_chars]
        if columns >= 5:
            weights[0] = max(weights[0], 10)
    total = sum(weights)
    widths = [CONTENT_W * weight / total for weight in weights]
    table = LongTable(clean_rows, colWidths=widths, repeatRows=1, hAlign="LEFT", splitByRow=True)
    commands = [
                ("BACKGROUND", (0, 0), (-1, 0), TABLE_HEADER),
                ("TEXTCOLOR", (0, 0), (-1, 0), TABLE_HEADER_TEXT),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), font_size),
                ("LEADING", (0, 0), (-1, -1), cell_leading),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("GRID", (0, 0), (-1, -1), 0.35, GRID),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), TABLE_ROWS),
                ("LEFTPADDING", (0, 0), (-1, -1), 3.2 if is_decision_factors else 2.5 if is_main_comparison else 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3.2 if is_decision_factors else 2.5 if is_main_comparison else 4),
                ("TOPPADDING", (0, 0), (-1, -1), 3.2 if is_decision_factors else 2.5 if is_main_comparison else 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3.2 if is_decision_factors else 2.5 if is_main_comparison else 4),
            ]
    if is_main_comparison:
        commands.extend(
            [
                ("LINEBELOW", (4, 0), (4, 0), 1.8, GOLD),
                ("LINEBEFORE", (4, 0), (4, -1), 0.8, GOLD),
                ("LINEAFTER", (4, 0), (4, -1), 0.8, GOLD),
                ("LINEBELOW", (6, 0), (6, 0), 1.8, GOLD),
                ("LINEBEFORE", (6, 0), (6, -1), 0.8, GOLD),
                ("LINEAFTER", (6, 0), (6, -1), 0.8, GOLD),
            ]
        )
    if rows[0][0] == "Input":
        for row_index, row in enumerate(rows):
            label = re.sub(r"\*\*", "", row[0]).strip()
            if label == "L3 saving over no-tele rollout":
                commands.extend(
                    [
                        ("BACKGROUND", (0, row_index), (-1, row_index), RESULT_ROW_BG),
                        ("LINEABOVE", (0, row_index), (-1, row_index), 0.8, GREEN),
                    ]
                )
    table.setStyle(TableStyle(commands))
    return table


def parse_markdown(text: str):
    lines = text.splitlines()
    story = []
    paragraph_lines: list[str] = []
    code_lines: list[str] = []
    in_code = False
    table_rows: list[list[str]] = []
    seen_title = False

    def flush_paragraph():
        nonlocal paragraph_lines
        if paragraph_lines:
            joined = " ".join(line.strip() for line in paragraph_lines)
            story.append(Paragraph(inline_markup(joined), body))
            paragraph_lines = []

    def flush_table():
        nonlocal table_rows
        if table_rows:
            table = make_table(table_rows)
            # Preserve a single-view comparison, including its heading and setup.
            grouped_headers = {"Case", "Map", "Assumption", "Tele-use time", "Input"}
            start = len(story)
            if table_rows[0][0] in grouped_headers:
                for index in range(len(story) - 1, -1, -1):
                    item = story[index]
                    if isinstance(item, Paragraph) and item.style.name in {"H2", "H3"}:
                        start = index
                        break
                    if isinstance(item, (PageBreak, KeepTogether, LongTable)):
                        break
            if start > 0 and isinstance(story[start - 1], Paragraph) and story[start - 1].style.name == "H2":
                start -= 1
            prefix = story[start:]
            del story[start:]
            story.append(KeepTogether(prefix + [Spacer(1, 3), table, Spacer(1, 7)]))
            table_rows = []

    for raw in lines:
        line = raw.rstrip()
        if line.strip() == "<pagebreak>":
            flush_paragraph()
            flush_table()
            story.append(PageBreak())
            continue
        if line.startswith("```"):
            flush_paragraph()
            flush_table()
            if in_code:
                story.append(KeepTogether([XPreformatted(inline_markup("\n".join(code_lines)), code_style)]))
                code_lines = []
                in_code = False
            else:
                in_code = True
            continue
        if in_code:
            code_lines.append(line)
            continue

        image_match = re.fullmatch(r"!\[([^\]]*)\]\(([^)]+)\)", line.strip())
        if image_match:
            flush_paragraph()
            flush_table()
            image_reference = image_match.group(2)
            if DARK_MODE:
                image_reference = image_reference.replace("research/report_assets/", "research/report_assets_dark/")
            image_path = ROOT / image_reference
            img = Image(str(image_path))
            max_image_height = 180 * mm if image_path.name == "step-5-shared-tele-timeline.png" else 154 * mm
            scale = min(CONTENT_W / img.imageWidth, max_image_height / img.imageHeight)
            if image_path.name == "l3-minus-l1-timeline.png":
                scale *= 0.94
            img.drawWidth = img.imageWidth * scale
            img.drawHeight = img.imageHeight * scale
            img.hAlign = "CENTER"
            story.append(KeepTogether([Spacer(1, 5), img,
                Paragraph(inline_markup(image_match.group(1)), caption)]))
            continue

        if line.startswith("|"):
            flush_paragraph()
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
                continue
            table_rows.append(cells)
            continue
        flush_table()

        if not line.strip():
            flush_paragraph()
            continue
        if line.startswith("# "):
            flush_paragraph()
            if not seen_title:
                title = line[2:].strip()
                story.extend(
                    [
                        Spacer(1, 38 * mm),
                        Paragraph(inline_markup(title), h1),
                        HRFlowable(width="45%", thickness=2.0, color=BLUE, hAlign="CENTER", spaceBefore=8, spaceAfter=14),
                        Paragraph("Competitive TF2 Highlander - King of the Hill", lead),
                        Spacer(1, 9 * mm),
                        Paragraph("Respawn waves, return timing, and whether to destroy the exit after a wipe", lead),
                        Spacer(1, 38 * mm),
                        Paragraph(
                            f'Report version {REPORT_VERSION} | {REPORT_DATE}<br/>Review edition<br/><font size="7">Author: plasmatech8</font>',
                            caption,
                        ),
                        PageBreak(),
                        Paragraph("Contents", toc_h),
                    ]
                )
                toc = TableOfContents()
                toc.levelStyles = [
                    ParagraphStyle("TOC0", parent=body, fontName="Helvetica-Bold", fontSize=9.5, leading=15, leftIndent=0, firstLineIndent=0, textColor=NAVY),
                    ParagraphStyle("TOC1", parent=body, fontSize=8.3, leading=12, leftIndent=12, firstLineIndent=0, textColor=SLATE),
                ]
                story.extend(
                    [
                        toc,
                        Spacer(1, 8 * mm),
                        Paragraph(
                            inline_markup(
                                "**Fast reading path:** Short answer (page 3) -> 7-9 second staging rule (page 6) -> Applying this to the after-wipe policy (page 17) -> Decision factors and conclusion table (pages 22-23). "
                                "Read the calculation and demo sections when you want to check the reasoning and evidence."
                            ),
                            quote,
                        ),
                        PageBreak(),
                    ]
                )
                seen_title = True
            continue
        if line.startswith("## "):
            flush_paragraph()
            if line[3:].strip() in {"Reading the numbers"}:
                story.append(PageBreak())
            story.append(Paragraph(inline_markup(line[3:].strip()), h2))
            continue
        if line.startswith("### "):
            flush_paragraph()
            heading = line[4:].strip()
            story.append(Paragraph(inline_markup(heading), h3))
            continue
        if line.startswith("> "):
            flush_paragraph()
            story.append(Paragraph(inline_markup(line[2:].strip()), quote))
            continue
        if re.match(r"^[-*] ", line):
            flush_paragraph()
            story.append(Paragraph(inline_markup(line[2:].strip()), bullet, bulletText="-"))
            continue
        ordered = re.match(r"^(\d+)\. (.+)", line)
        if ordered:
            flush_paragraph()
            story.append(Paragraph(inline_markup(ordered.group(2)), bullet, bulletText=f"{ordered.group(1)}."))
            continue
        if re.fullmatch(r"-{3,}", line.strip()):
            flush_paragraph()
            story.append(HRFlowable(width="100%", thickness=0.5, color=GRID, spaceBefore=4, spaceAfter=7))
            continue
        paragraph_lines.append(line)

    flush_paragraph()
    flush_table()
    if in_code and code_lines:
        story.append(Preformatted(ascii_safe("\n".join(code_lines)), code_style, maxLineLength=100))
    return story


def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    source = SOURCE.read_text(encoding="utf-8")
    story = parse_markdown(source)
    doc = ReportDocTemplate(str(OUTPUT))
    doc.multiBuild(story)
    print(OUTPUT)


if __name__ == "__main__":
    main()
