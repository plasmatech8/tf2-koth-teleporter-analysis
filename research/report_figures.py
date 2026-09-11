"""Render report figures with Pillow, using only bundled workspace dependencies."""
from pathlib import Path
import json
import sys
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
DARK = '--dark' in sys.argv
OUT = ROOT / ('report_assets_dark' if DARK else 'report_assets')
OUT.mkdir(exist_ok=True)
MODEL = json.loads((ROOT / 'report_model.json').read_text())
FRONT = json.loads((ROOT / 'demo_frontline_case.json').read_text())

if DARK:
    BG = '#2b3035'
    INK = '#d6d1c7'
    MUTED = '#aab0b4'
    GRID = '#485159'
    BLUE = '#4d98bc'
    BLUE2 = '#72abc2'
    RED = '#d27369'
    GREY = '#929da5'
    LIGHT = '#383f45'
    GOLD = '#d0a047'
    GREEN = '#68a986'
    POS1 = '#a8c1ae'
    POS2 = '#78c292'
    POS3 = '#a5d77b'
else:
    BG = '#ffffff'
    INK = '#26323b'
    MUTED = '#5f6b75'
    GRID = '#dce3e8'
    BLUE = '#246b8e'
    BLUE2 = '#66a5bf'
    RED = '#a4473d'
    GREY = '#8c98a4'
    LIGHT = '#e8edf1'
    GOLD = '#c28c28'
    GREEN = '#347a5a'
    POS1 = '#668776'
    POS2 = '#2f7d58'
    POS3 = '#4c8e42'

FONT = Path('C:/Windows/Fonts/arial.ttf')
FONT_BOLD = Path('C:/Windows/Fonts/arialbd.ttf')

def font(size, bold=False):
    return ImageFont.truetype(str(FONT_BOLD if bold else FONT), size)

def text(draw, xy, value, size=26, fill=INK, bold=False, anchor='la'):
    draw.text(xy, value, font=font(size, bold), fill=fill, anchor=anchor)

def line(draw, points, fill=GRID, width=2):
    draw.line(points, fill=fill, width=width)

def get_scenario(map_id, scenario_id):
    return next(x for x in MODEL['scenarios'] if x['map'] == map_id and x['id'] == scenario_id)

def clock(t):
    return f'{int(t // 60)}:{t % 60:05.2f}'

def save(img, name):
    img.save(OUT / name, optimize=True)


def advantage_colour(margin):
    if margin < 0:
        return RED
    if margin == 0:
        return LIGHT
    if margin == 1:
        return POS1
    if margin == 2:
        return POS2
    return POS3


def render_explainer_timeline(name, title, subtitle, panels, tmin, tmax, tick, axis_title):
    """Render compact explainer figures in the same grammar as Figure 1."""
    W = 1800
    x0, x1 = 360, 1710
    title_block = 175
    panel_title_height = 64
    row_height = 62
    panel_gap = 42
    footer = 92
    panel_heights = [panel_title_height + row_height * len(panel['rows']) for panel in panels]
    H = title_block + sum(panel_heights) + panel_gap * max(0, len(panels) - 1) + footer
    img = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(img)
    text(d, (90, 55), title, 39, bold=True)
    text(d, (90, 108), subtitle, 26, fill=MUTED)
    sx = lambda t: x0 + (x1 - x0) * (t - tmin) / (tmax - tmin)
    chart_top = title_block
    chart_bottom = H - footer

    first_tick = int(tmin // tick) * tick
    if first_tick < tmin:
        first_tick += tick
    for t in range(first_tick, int(tmax) + 1, tick):
        x = sx(t)
        line(d, [(x, chart_top), (x, chart_bottom)], fill=GRID, width=1)
        text(d, (x, chart_bottom + 34), str(t), 20, fill=MUTED, anchor='ma')

    y_cursor = chart_top
    for panel_index, panel in enumerate(panels):
        text(d, (90, y_cursor + 28), panel['title'], 29, bold=True)
        y_cursor += panel_title_height
        for row in panel['rows']:
            y = y_cursor + row_height // 2
            text(d, (x0 - 24, y), row['label'], 22, fill=MUTED, anchor='ra')
            if row['type'] == 'band':
                for interval in row['intervals']:
                    start, end, margin = interval['start'], interval['end'], interval['margin']
                    colour = advantage_colour(margin)
                    d.rectangle((sx(start), y - 22, sx(end), y + 22), fill=colour)
                    width = sx(end) - sx(start)
                    if width >= 68 or (margin != 0 and width >= 50):
                        label = interval.get('label', f'{margin:+d}')
                        label_colour = INK if margin == 0 else ('#f5f1e9' if margin < 0 else '#17231c')
                        text(d, ((sx(start) + sx(end)) / 2, y), label, 21,
                             fill=label_colour, bold=True, anchor='mm')
            else:
                spawn, arrival = row['spawn'], row['arrival']
                line(d, [(sx(spawn), y), (sx(arrival), y)], fill=MUTED, width=2)
                d.ellipse((sx(spawn) - 7, y - 7, sx(spawn) + 7, y + 7), outline=MUTED, width=2)
                if 'entrance' in row:
                    d.ellipse((sx(row['entrance']) - 4, y - 4, sx(row['entrance']) + 4, y + 4), fill=MUTED)
                team = row.get('team', 'attack')
                colour = BLUE if team == 'attack' else RED if team == 'defend' else GOLD
                if row.get('kind') == 'process':
                    line(d, [(sx(spawn), y), (sx(arrival), y)], fill=colour, width=14)
                else:
                    d.rounded_rectangle((sx(arrival), y - 15, sx(tmax), y + 15), radius=7, fill=colour)
                d.ellipse((sx(arrival) - 8, y - 8, sx(arrival) + 8, y + 8), fill=colour)
                label_x = sx(arrival) - 9 if arrival > tmax - (tmax - tmin) * 0.18 else sx(arrival) + 9
                horizontal = 'r' if label_x < sx(arrival) else 'l'
                if team == 'defend':
                    text(d, (label_x, y + 22), row['note'], 19, fill=colour, anchor=horizontal + 't')
                else:
                    text(d, (label_x, y - 20), row['note'], 19, fill=colour, anchor=horizontal + 's')
            y_cursor += row_height
        if panel_index < len(panels) - 1:
            y_cursor += panel_gap

    text(d, ((x0 + x1) / 2, H - 28), axis_title, 23, fill=MUTED, anchor='mm')
    save(img, name)


# Figure 1: attacker / advantage / defender lanes.
s = get_scenario('product', '2A')
W, H = 1800, 1240
img = Image.new('RGB', (W, H), BG)
d = ImageDraw.Draw(img)
text(d, (90, 58), 'Scenario 2A — two player trades; both defenders respawn together', 40, bold=True)
text(d, (90, 112), 'Returning attackers exceed returning defenders by +2 for 4.0 seconds with retained L3.', 27, fill=MUTED)

x0, x1 = 360, 1700
tmax = 20
sx = lambda t: x0 + (x1 - x0) * t / tmax
panels = [('l3', 'Keep the existing L3'), ('l1', 'Destroy it; rebuilt L1 is ready for the first return')]

for panel_index, (key, title) in enumerate(panels):
    top = 190 + panel_index * 500
    net = s['alternatives'][key]['net']
    text(d, (90, top), f"{title} — {net['playerSeconds']:.1f} net attacking player-seconds", 30, bold=True)
    for tick in range(0, 20, 2):
        x = sx(tick)
        line(d, [(x, top + 55), (x, top + 410)], fill=GRID, width=1)
        text(d, (x, top + 430), str(tick), 21, fill=MUTED, anchor='ma')
    labels = [(top + 110, 'A1'), (top + 170, 'A2'), (top + 245, 'front-line advantage'), (top + 320, 'D1'), (top + 380, 'D2')]
    for y, label in labels:
        text(d, (x0 - 24, y), label, 22, fill=MUTED, anchor='ra')
    horizon = max(x['arrival'] for x in s['alternatives'][key]['attack'] + s['defence'])
    for y, item in zip([top + 110, top + 170], s['alternatives'][key]['attack']):
        line(d, [(sx(item['spawn']), y), (sx(item['arrival']), y)], fill=MUTED, width=2)
        d.ellipse((sx(item['spawn']) - 7, y - 7, sx(item['spawn']) + 7, y + 7), outline=MUTED, width=2)
        if item['mode'] != 'walk' and 'entranceArrival' in item:
            d.ellipse((sx(item['entranceArrival']) - 4, y - 4, sx(item['entranceArrival']) + 4, y + 4), fill=MUTED)
        d.rounded_rectangle((sx(item['arrival']), y - 15, sx(horizon), y + 15), radius=7, fill=BLUE)
        d.ellipse((sx(item['arrival']) - 8, y - 8, sx(item['arrival']) + 8, y + 8), fill=BLUE)
        mode = 'walks' if item['mode'] == 'walk' else 'tele'
        text(d, (sx(item['arrival']) + 8, y - 25), f"{item['arrival']:.1f}s ({mode})", 20, fill=BLUE, anchor='ls')
    for y, item in zip([top + 320, top + 380], s['defence']):
        line(d, [(sx(item['spawn']), y), (sx(item['arrival']), y)], fill=MUTED, width=2)
        d.ellipse((sx(item['spawn']) - 7, y - 7, sx(item['spawn']) + 7, y + 7), outline=MUTED, width=2)
        if 'entranceArrival' in item:
            d.ellipse((sx(item['entranceArrival']) - 4, y - 4, sx(item['entranceArrival']) + 4, y + 4), fill=MUTED)
        d.rounded_rectangle((sx(item['arrival']), y - 15, sx(horizon), y + 15), radius=7, fill=RED)
        d.ellipse((sx(item['arrival']) - 8, y - 8, sx(item['arrival']) + 8, y + 8), fill=RED)
        text(d, (sx(item['arrival']) + 8, y + 25), f"{item['arrival']:.1f}s", 20, fill=RED, anchor='lt')
    for interval in net['intervals']:
        margin = interval['margin']
        color = advantage_colour(margin)
        d.rectangle((sx(interval['start']), top + 222, sx(interval['end']), top + 268), fill=color)
        text(d, ((sx(interval['start']) + sx(interval['end'])) / 2, top + 245), f'{margin:+d}', 23,
             fill=INK if margin == 0 else ('#f5f1e9' if margin < 0 else '#17231c'), bold=True, anchor='mm')

text(d, ((x0 + x1) / 2, H - 45), 'Seconds after the first attacking respawn; each bar starts when that player reaches the front line', 24, fill=MUTED, anchor='mm')
save(img, 'frontline-arrival-timeline.png')


# Figures 1a-1e: one consistent arrival-timeline explainer for calculation steps 1-5.
render_explainer_timeline(
    'step-1-average-trade-timeline.png',
    'One average simultaneous player trade on Product',
    'Equal charged-L3 routes preserve the theoretical mean six-second attacker arrival advantage.',
    [{
        'title': 'Both players die at 0.0 seconds',
        'rows': [
            {'type': 'player', 'label': 'Attacker', 'spawn': 12.4, 'entrance': 14.4, 'arrival': 19.0,
             'team': 'attack', 'note': '19.0s (tele)'},
            {'type': 'band', 'label': 'front-line advantage',
             'intervals': [{'start': 19.0, 'end': 25.0, 'margin': 1}]},
            {'type': 'player', 'label': 'Defender', 'spawn': 18.4, 'entrance': 20.4, 'arrival': 25.0,
             'team': 'defend', 'note': '25.0s (tele)'},
        ],
    }],
    0, 28, 4,
    'Seconds after the simultaneous deaths; each thick bar starts when that player reaches the front line',
)

render_explainer_timeline(
    'step-2-wave-alignments-timeline.png',
    'The two exact respawn-wave alignments on Product',
    'A paired death produces a four- or eight-second attacker arrival advantage, not an individual six-second result.',
    [
        {
            'title': 'Four-second alignment',
            'rows': [
                {'type': 'player', 'label': 'Attacker', 'spawn': 10.4, 'entrance': 12.4, 'arrival': 17.0,
                 'team': 'attack', 'note': '17.0s (tele)'},
                {'type': 'band', 'label': 'front-line advantage',
                 'intervals': [{'start': 17.0, 'end': 21.0, 'margin': 1}]},
                {'type': 'player', 'label': 'Defender', 'spawn': 14.4, 'entrance': 16.4, 'arrival': 21.0,
                 'team': 'defend', 'note': '21.0s (tele)'},
            ],
        },
        {
            'title': 'Eight-second alignment',
            'rows': [
                {'type': 'player', 'label': 'Attacker', 'spawn': 14.4, 'entrance': 16.4, 'arrival': 21.0,
                 'team': 'attack', 'note': '21.0s (tele)'},
                {'type': 'band', 'label': 'front-line advantage',
                 'intervals': [{'start': 21.0, 'end': 29.0, 'margin': 1}]},
                {'type': 'player', 'label': 'Defender', 'spawn': 22.4, 'entrance': 24.4, 'arrival': 29.0,
                 'team': 'defend', 'note': '29.0s (tele)'},
            ],
        },
    ],
    8, 32, 4,
    'Seconds after the paired deaths; both teams use the same charged-L3 route',
)

render_explainer_timeline(
    'step-3-no-tele-timeline.png',
    'Product when the attacker has no usable tele',
    'Walking consumes the four-second advantage and leaves only part of the eight-second advantage.',
    [
        {
            'title': 'Four-second alignment',
            'rows': [
                {'type': 'player', 'label': 'Attacker', 'spawn': 10.4, 'arrival': 22.4,
                 'team': 'attack', 'note': '22.4s (walks)'},
                {'type': 'band', 'label': 'front-line advantage',
                 'intervals': [{'start': 21.0, 'end': 22.4, 'margin': -1, 'label': '-1.4s'}]},
                {'type': 'player', 'label': 'Defender', 'spawn': 14.4, 'entrance': 16.4, 'arrival': 21.0,
                 'team': 'defend', 'note': '21.0s (tele)'},
            ],
        },
        {
            'title': 'Eight-second alignment',
            'rows': [
                {'type': 'player', 'label': 'Attacker', 'spawn': 14.4, 'arrival': 26.4,
                 'team': 'attack', 'note': '26.4s (walks)'},
                {'type': 'band', 'label': 'front-line advantage',
                 'intervals': [{'start': 26.4, 'end': 29.0, 'margin': 1, 'label': '+2.6s'}]},
                {'type': 'player', 'label': 'Defender', 'spawn': 22.4, 'entrance': 24.4, 'arrival': 29.0,
                 'team': 'defend', 'note': '29.0s (tele)'},
            ],
        },
    ],
    8, 32, 4,
    'Seconds after the paired deaths; the centre strip shows who reaches the front first',
)

render_explainer_timeline(
    'step-4-rebuild-readiness-timeline.png',
    'Whether the rebuilt L1 is ready for the first useful return',
    'The reference point is the rider reaching the entrance; construction need not begin at the wipe.',
    [
        {
            'title': 'Ready at the entrance: construction began at least 21.1 seconds earlier',
            'rows': [
                {'type': 'player', 'label': 'L1 construction', 'spawn': -21.1, 'arrival': 0.0,
                 'team': 'neutral', 'kind': 'process', 'note': 'ready at 0.0s'},
                {'type': 'player', 'label': 'Returner', 'spawn': -2.0, 'entrance': 0.0, 'arrival': 4.6,
                 'team': 'attack', 'note': '4.6s (tele)'},
                {'type': 'band', 'label': 'L1 versus walking',
                 'intervals': [{'start': 4.6, 'end': 10.0, 'margin': 1, 'label': '+1 for 5.4s'}]},
            ],
        },
        {
            'title': 'Illustrative late placement: construction began only 15 seconds earlier',
            'rows': [
                {'type': 'player', 'label': 'L1 construction', 'spawn': -15.0, 'arrival': 6.1,
                 'team': 'neutral', 'kind': 'process', 'note': 'ready at +6.1s'},
                {'type': 'player', 'label': 'Returner', 'spawn': -2.0, 'arrival': 10.0,
                 'team': 'attack', 'note': '10.0s (walks)'},
                {'type': 'band', 'label': 'L1 versus walking',
                 'intervals': [{'start': 4.6, 'end': 10.0, 'margin': 0, 'label': 'no saved arrival'}]},
            ],
        },
    ],
    -24, 14, 4,
    'Seconds from the first relevant arrival at the tele entrance',
)

shared = get_scenario('product', '4A')


def shared_attack_rows(level):
    rows = []
    for item in shared['alternatives'][level]['attack']:
        mode = 'walks' if item['mode'] == 'walk' else 'tele'
        row = {
            'type': 'player',
            'label': f"A{item['player']}",
            'spawn': item['spawn'],
            'arrival': item['arrival'],
            'team': 'attack',
            'note': f"{item['arrival']:.1f}s {mode}",
        }
        if item['mode'] != 'walk':
            row['entrance'] = item['entranceArrival']
        rows.append(row)
    net_intervals = []
    for interval in shared['alternatives'][level]['net']['intervals']:
        if (net_intervals and net_intervals[-1]['margin'] == interval['margin']
                and abs(net_intervals[-1]['end'] - interval['start']) < 1e-6):
            net_intervals[-1]['end'] = interval['end']
        else:
            net_intervals.append(dict(interval))
    rows.append({
        'type': 'band',
        'label': 'advantage vs defender L3',
        'intervals': net_intervals,
    })
    return rows


def shared_defence_rows():
    rows = []
    for item in shared['defence']:
        mode = 'walks' if item['mode'] == 'walk' else 'tele'
        row = {
            'type': 'player',
            'label': f"D{item['player']}",
            'spawn': item['spawn'],
            'arrival': item['arrival'],
            'team': 'defend',
            'note': f"{item['arrival']:.1f}s {mode}",
        }
        if item['mode'] != 'walk':
            row['entrance'] = item['entranceArrival']
        rows.append(row)
    return rows


render_explainer_timeline(
    'step-5-shared-tele-timeline.png',
    'Product scenario 4A - shared-tele queues against defender L3',
    'Each centre strip shows attacking returners minus defending returners at the front.',
    [
        {'title': 'Attacker L3 - every successive return is served', 'rows': shared_attack_rows('l3')},
        {'title': 'Attacker L2 - the second and fourth returns walk', 'rows': shared_attack_rows('l2')},
        {'title': 'Attacker L1 - the first and fourth returns are served', 'rows': shared_attack_rows('l1')},
        {'title': 'Defender L3 - two pairs respawn together', 'rows': shared_defence_rows()},
    ],
    0, 30, 4,
    'Seconds after the first attacking respawn; thick bars begin at front-line arrival',
)


# Figure 2: direct Product L3-minus-L1 timelines.
product = [x for x in MODEL['scenarios'] if x['map'] == 'product']
W, H = 1800, 900
img = Image.new('RGB', (W, H), BG)
d = ImageDraw.Draw(img)
text(d, (90, 55), 'Product — extra front-line presence from keeping L3 instead of rebuilding L1', 38, bold=True)
text(d, (90, 108), 'This is the direct policy difference. It does not include the defending return cohort.', 26, fill=MUTED)
x0, x1 = 405, 1650
tmax = 25
sx = lambda t: x0 + (x1 - x0) * t / tmax
for tick in range(0, 26, 2):
    x = sx(tick)
    line(d, [(x, 180), (x, 760)], fill=GRID, width=1)
    text(d, (x, 790), str(tick), 20, fill=MUTED, anchor='ma')
for index, trades in enumerate([1, 2, 3, 4]):
    scenario = next(x for x in product if x['trades'] == trades)
    net = scenario['alternatives']['l3_vs_l1']
    y = 235 + index * 135
    text(d, (x0 - 24, y), f'{trades} return' + ('' if trades == 1 else 's'), 24, anchor='ra')
    intervals = net['intervals']
    if not intervals:
        d.rectangle((sx(0), y - 23, sx(8), y + 23), fill=LIGHT)
        text(d, ((sx(0) + sx(8)) / 2, y), 'no difference', 20, fill=MUTED, anchor='mm')
    for interval in intervals:
        color = advantage_colour(interval['margin'])
        d.rectangle((sx(interval['start']), y - 23, sx(interval['end']), y + 23), fill=color)
        if interval['duration'] >= 1.0:
            label = 'even' if interval['margin'] == 0 else f"{interval['margin']:+d}"
            text(d, ((sx(interval['start']) + sx(interval['end'])) / 2, y), label, 20,
                 fill=INK if interval['margin'] == 0 else '#17231c', bold=True, anchor='mm')
    text(d, (x1 + 26, y), f"{net['playerSeconds']:+.1f} p·s", 23, fill=GREEN if net['playerSeconds'] > 0 else MUTED, bold=True, anchor='la')
text(d, ((x0 + x1) / 2, H - 45), 'Seconds after the first attacking respawn; green means an additional attacker under retained L3', 23, fill=MUTED, anchor='mm')
save(img, 'l3-minus-l1-timeline.png')


# Figure 3: all Product scenario totals.
product = [x for x in MODEL['scenarios'] if x['map'] == 'product']
W, H = 1800, 1320
img = Image.new('RGB', (W, H), BG)
d = ImageDraw.Draw(img)
text(d, (90, 55), 'Product — return-cohort advantage by teleporter state', 40, bold=True)
text(d, (90, 106), 'Positive player-seconds favour the attacking team. A/B are the two respawn-wave alignments.', 26, fill=MUTED)

x0, x1 = 300, 1690
vmin, vmax = -4, 34
sx = lambda v: x0 + (x1 - x0) * (v - vmin) / (vmax - vmin)
for tick in range(-4, 35, 2):
    x = sx(tick)
    line(d, [(x, 190), (x, 1180)], fill=GRID, width=1)
    if tick % 4 == 0:
        text(d, (x, 1205), str(tick), 20, fill=MUTED, anchor='ma')
line(d, [(sx(0), 175), (sx(0), 1185)], fill=MUTED, width=2)

keys = [('walk', 'No tele / walk', GREY), ('l1', 'Rebuilt L1', GOLD), ('l2', 'Rebuilt L2', GREEN), ('l3', 'Keep L3', BLUE)]
for i, (_, label, color) in enumerate(keys):
    lx = 370 + i * 300
    d.rectangle((lx, 145, lx + 34, 169), fill=color)
    text(d, (lx + 45, 157), label, 21, anchor='lm')

row_h = 120
for r, scenario in enumerate(product):
    yc = 230 + r * row_h
    text(d, (x0 - 25, yc + 32), f"{scenario['id']} ({scenario['trades']} trade{'s' if scenario['trades'] != 1 else ''})", 23, fill=INK, anchor='ra')
    for i, (key, _, color) in enumerate(keys):
        value = scenario['alternatives'][key]['net']['playerSeconds']
        y = yc + i * 22
        left, right = sorted([sx(0), sx(value)])
        d.rectangle((left, y, right, y + 17), fill=color)
        text(d, ((right + 8) if value >= 0 else (left - 8), y + 8), f'{value:.1f}', 18, fill=INK,
             anchor='lm' if value >= 0 else 'rm')

text(d, ((x0 + x1) / 2, H - 45), 'Net attacking front-line player-seconds before all modelled players return', 24, fill=MUTED, anchor='mm')
save(img, 'product-scenario-comparison.png')


# Figure 4: August 22 Ashville demo case.
windows = FRONT['earlierArrivalWindows']
start = 1479.75
reopen = FRONT['window']['start']
restored = FRONT['window']['end']
W, H = 1800, 1230
img = Image.new('RGB', (W, H), BG)
d = ImageDraw.Draw(img)
text(d, (90, 55), 'August 22 Ashville — potential earlier front-line presence', 40, bold=True)
text(d, (90, 108), 'Each bar is time the retained-L3 counterfactual supplies a player before the recorded arrival.', 26, fill=MUTED)
x0, x1 = 300, 1710
sx = lambda t: x0 + (x1 - x0) * (t - (start - 2)) / ((restored + 4) - (start - 2))

d.rectangle((sx(start), 185, sx(reopen), 1020), fill=LIGHT)
text(d, ((sx(start) + sx(reopen)) / 2, 230), 'Initial rollout excluded\nfrom tele benefit', 21, fill=MUTED, anchor='ma')
for t, label, color, anchor in [
    (start, f'L3 destroyed\n{clock(start)}', RED, 'la'),
    (reopen, f'Ground screen satisfied\n{clock(reopen)}', GREEN, 'ma'),
    (restored, f'Connection restored\n{clock(restored)}', BLUE, 'ra'),
]:
    line(d, [(sx(t), 170), (sx(t), 1035)], fill=color, width=3)
    text(d, (sx(t), 150), label, 20, fill=color, bold=True, anchor=anchor)

for t in range(1480, 1611, 20):
    line(d, [(sx(t), 185), (sx(t), 1035)], fill=GRID, width=1)
    text(d, (sx(t), 1070), clock(t), 20, fill=MUTED, anchor='ma')

for i, w in enumerate(windows):
    y = 390 + i * 105
    label = f"{w['class'].title()} return"
    text(d, (x0 - 22, y), label, 22, fill=MUTED, anchor='ra')
    d.rounded_rectangle((sx(w['start']), y - 18, sx(w['end']), y + 18), radius=7, fill=POS1)
    d.ellipse((sx(w['start']) - 8, y - 8, sx(w['start']) + 8, y + 8), fill=POS1)
    line(d, [(sx(w['end']), y - 24), (sx(w['end']), y + 24)], fill=INK, width=3)
    text(d, ((sx(w['start']) + sx(w['end'])) / 2, y - 28), f"{w['saved']:.1f} seconds", 18, fill=POS1, anchor='ms')

events = sorted([(w['start'], 1) for w in windows] + [(w['end'], -1) for w in windows], key=lambda x: (x[0], x[1]))
count = 0
y = 955
text(d, (x0 - 22, y), 'Extra front-line players', 22, fill=MUTED, anchor='ra')
for i, (t, delta) in enumerate(events):
    count += delta
    if i + 1 >= len(events):
        continue
    end = events[i + 1][0]
    if end <= t:
        continue
    color = advantage_colour(count)
    d.rectangle((sx(t), y - 24, sx(end), y + 24), fill=color)
    if count and (count >= 2 or end - t >= 1.5):
        text(d, ((sx(t) + sx(end)) / 2, y), f'+{count}', 21, fill='#17231c', bold=True, anchor='mm')

text(d, ((x0 + x1) / 2, H - 65), 'SourceTV demo time', 24, fill=MUTED, anchor='mm')
text(d, (90, H - 25), 'Route model: 22.25s at +1 and 5.84s at +2 = 33.93 potential player-seconds. Safety and later deaths are held fixed.', 21, fill=MUTED, anchor='ls')
save(img, 'ashville-demo-earlier-presence.png')

print(f'wrote figures to {OUT}')
