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


def render_explainer_timeline(name, title, subtitle, panels, tmin, tmax, tick, axis_title, markers=None):
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

    for marker in markers or []:
        x = sx(marker['time'])
        marker_colour = marker.get('color', RED)
        for y in range(chart_top, chart_bottom, 18):
            line(d, [(x, y), (x, min(y + 9, chart_bottom))], fill=marker_colour, width=2)
        if marker.get('kind') == 'death':
            # A small drawn skull avoids relying on an emoji glyph.
            d.ellipse((x - 12, chart_top - 33, x + 12, chart_top - 9),
                      outline=marker_colour, width=3)
            d.ellipse((x - 7, chart_top - 26, x - 3, chart_top - 22), fill=marker_colour)
            d.ellipse((x + 3, chart_top - 26, x + 7, chart_top - 22), fill=marker_colour)
            d.rectangle((x - 7, chart_top - 13, x + 7, chart_top - 6),
                        outline=marker_colour, width=2)
        text(d, (x + 19, chart_top - 18), marker['label'], 20,
             fill=marker_colour, bold=True, anchor='lm')

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


def render_rebuild_readiness_timeline():
    """Show the 7-9 second rule while preserving the report's timeline grammar."""
    name = 'step-4-rebuild-readiness-timeline.png'
    W, H = 1800, 1370
    img = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(img)

    text(d, (90, 52),
         'The 7-9 second staging rule: minimum time before the next relevant death',
         38, bold=True)
    text(d, (90, 104),
         'About 7 seconds under mean respawn timing and 9 seconds for the fastest return. Later deaths also work.',
         25, fill=MUTED)
    text(d, (90, 140),
         'After respawning, the player walks 2.0 seconds from spawn to the tele entrance; the model allows waiting there for up to 1.0 second.',
         21, fill=MUTED)

    x0, x1 = 385, 1710
    tmin, tmax = 0.0, 33.0
    sx = lambda t: x0 + (x1 - x0) * (t - tmin) / (tmax - tmin)
    chart_top, chart_bottom = 180, 1240

    for tick_value in range(0, 34, 3):
        x = sx(tick_value)
        line(d, [(x, chart_top), (x, chart_bottom)], fill=GRID, width=1)
        text(d, (x, chart_bottom + 34), str(tick_value), 20, fill=MUTED, anchor='ma')

    ready_x = sx(21.1)
    for y in range(chart_top, chart_bottom, 18):
        line(d, [(ready_x, y), (ready_x, min(y + 9, chart_bottom))], fill=GOLD, width=2)
    text(d, (ready_x + 13, chart_top + 15), 'L1 ready: 21.1s', 20,
         fill=GOLD, bold=True, anchor='ls')

    def skull(x, y):
        d.ellipse((x - 12, y - 14, x + 12, y + 10), outline=RED, width=3)
        d.ellipse((x - 7, y - 7, x - 3, y - 3), fill=RED)
        d.ellipse((x + 3, y - 7, x + 7, y - 3), fill=RED)
        d.rectangle((x - 7, y + 6, x + 7, y + 13), outline=RED, width=2)

    def cross(x, y):
        line(d, [(x - 9, y - 9), (x + 9, y + 9)], fill=RED, width=5)
        line(d, [(x - 9, y + 9), (x + 9, y - 9)], fill=RED, width=5)

    def draw_panel(top, title, death, respawn, entrance, arrival,
                   walk_arrival, mode, wait_needed=None):
        text(d, (90, top), title, 28, bold=True)
        construction_y = top + 74
        returner_y = top + 142
        gain_y = top + 213

        text(d, (x0 - 25, construction_y), 'L1 construction', 21,
             fill=MUTED, anchor='ra')
        line(d, [(sx(0), construction_y), (sx(21.1), construction_y)],
             fill=GOLD, width=14)
        d.ellipse((sx(0) - 7, construction_y - 7, sx(0) + 7, construction_y + 7),
                  outline=MUTED, width=2)
        d.ellipse((sx(21.1) - 8, construction_y - 8,
                   sx(21.1) + 8, construction_y + 8), fill=GOLD)

        text(d, (x0 - 25, returner_y), 'Returner', 21,
             fill=MUTED, anchor='ra')
        line(d, [(sx(death), returner_y), (sx(respawn), returner_y)],
             fill=GREY, width=18)
        skull(sx(death), returner_y)
        d.ellipse((sx(respawn) - 8, returner_y - 8,
                   sx(respawn) + 8, returner_y + 8), outline=INK, width=3)
        line(d, [(sx(respawn), returner_y), (sx(arrival), returner_y)],
             fill=MUTED, width=3)

        if mode == 'tele':
            d.ellipse((sx(entrance) - 5, returner_y - 5,
                       sx(entrance) + 5, returner_y + 5), fill=MUTED)
        else:
            d.ellipse((sx(entrance) - 5, returner_y - 5,
                       sx(entrance) + 5, returner_y + 5), fill=RED)
            cross(sx(entrance), returner_y - 23)
            for dash_x in range(int(sx(entrance)), int(sx(21.1)), 16):
                line(d, [(dash_x, returner_y + 21),
                         (min(dash_x + 8, sx(21.1)), returner_y + 21)],
                     fill=RED, width=2)
            text(d, (sx(21.1), returner_y + 26),
                 f'wait needed {wait_needed:.1f}s; model allows 1.0s',
                 17, fill=RED, bold=True, anchor='rt')

        # Thick blue bars retain their established meaning: presence at the front line.
        d.rounded_rectangle((sx(arrival), returner_y - 15,
                             sx(tmax), returner_y + 15), radius=7, fill=BLUE)
        d.ellipse((sx(arrival) - 8, returner_y - 8,
                   sx(arrival) + 8, returner_y + 8), fill=BLUE)
        text(d, (sx(death), returner_y - 25), f'death {death:.1f}s',
             18, fill=RED, bold=True, anchor='ms')
        text(d, ((sx(death) + sx(respawn)) / 2, returner_y),
             'dead / awaiting wave', 17, fill=BG, bold=True, anchor='mm')
        text(d, (sx(respawn), returner_y - 25), f'spawn {respawn:.1f}s',
             18, fill=INK, anchor='ms')
        text(d, (sx(arrival) + 10, returner_y - 24),
             f'{arrival:.1f}s ({mode})', 19, fill=BLUE, bold=True, anchor='ls')

        text(d, (x0 - 25, gain_y), 'L1 versus walking', 21,
             fill=MUTED, anchor='ra')
        if mode == 'tele':
            d.rectangle((sx(arrival), gain_y - 22,
                         sx(walk_arrival), gain_y + 22), fill=POS1)
            text(d, ((sx(arrival) + sx(walk_arrival)) / 2, gain_y),
                 f'+1 for {walk_arrival - arrival:.1f}s', 20,
                 fill='#17231c', bold=True, anchor='mm')
        else:
            text(d, (sx(arrival) + 10, gain_y), 'walks: no tele saving',
                 19, fill=MUTED, bold=True, anchor='lm')

    draw_panel(
        200,
        'Mean-respawn boundary - death 6.7 seconds after placement',
        death=6.7, respawn=19.1, entrance=21.1, arrival=25.7,
        walk_arrival=31.1, mode='tele')
    draw_panel(
        545,
        'Fastest-respawn boundary - death 8.7 seconds after placement',
        death=8.7, respawn=19.1, entrance=21.1, arrival=25.7,
        walk_arrival=31.1, mode='tele')
    draw_panel(
        890,
        'Too-early example - death 5.0 seconds after placement',
        death=5.0, respawn=17.4, entrance=19.4, arrival=29.4,
        walk_arrival=29.4, mode='walks', wait_needed=1.7)

    text(d, ((x0 + x1) / 2, H - 52),
         'Seconds after exit placement; open circle = respawn; small dot = tele entrance; thick blue = at the front line',
         23, fill=MUTED, anchor='mm')
    save(img, name)


# Figure 1: attacker / advantage / defender lanes.
s = get_scenario('product', '2B')
W, H = 1800, 1240
img = Image.new('RGB', (W, H), BG)
d = ImageDraw.Draw(img)
text(d, (90, 58), 'Scenario 2B — two player trades; both defenders respawn together', 40, bold=True)
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
        if item['mode'] != 'walk' and 'entranceArrival' in item:
            d.ellipse((sx(item['entranceArrival']) - 4, y - 4, sx(item['entranceArrival']) + 4, y + 4), fill=MUTED)
        d.rounded_rectangle((sx(item['arrival']), y - 15, sx(horizon), y + 15), radius=7, fill=RED)
        d.ellipse((sx(item['arrival']) - 8, y - 8, sx(item['arrival']) + 8, y + 8), fill=RED)
        mode = 'walks' if item['mode'] == 'walk' else 'tele'
        endpoint = item['arrival'] >= tmax - 1
        label_x = sx(item['arrival']) - 8 if endpoint else sx(item['arrival']) + 8
        text(d, (label_x, y + 25), f"{item['arrival']:.1f}s ({mode})", 20, fill=RED,
             anchor='rt' if endpoint else 'lt')
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

render_rebuild_readiness_timeline()

shared = get_scenario('product', '4B')


def shared_attack_rows(level, scenario=shared):
    rows = []
    for item in scenario['alternatives'][level]['attack']:
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
    for interval in scenario['alternatives'][level]['net']['intervals']:
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


def shared_defence_rows(scenario=shared):
    rows = []
    for item in scenario['defence']:
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
    'Product scenario 4B - shared-tele queues against defender L3',
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


# Expanded appendix figures: the same four attacker states under both defender-wave alignments.
for scenario_id, alignment_label, defender_offsets in (
        ('4A', 'four-second defender alignment', '4, 12, 12 and 20'),
        ('4B', 'eight-second defender alignment', '8, 8, 16 and 16')):
    scenario = get_scenario('product', scenario_id)
    render_explainer_timeline(
        f'product-scenario-{scenario_id.lower()}-shared-tele-with-no-tele.png',
        f'Product scenario {scenario_id} - {alignment_label}',
        'Each centre strip shows attacking returners minus defending returners at the front.',
        [
            {'title': 'Attacker L3 - every successive return is served',
             'rows': shared_attack_rows('l3', scenario)},
            {'title': 'Attacker L2 - the second and fourth returns walk',
             'rows': shared_attack_rows('l2', scenario)},
            {'title': 'Attacker L1 - the first and fourth returns are served',
             'rows': shared_attack_rows('l1', scenario)},
            {'title': 'Attacker no tele - every return walks',
             'rows': shared_attack_rows('walk', scenario)},
            {'title': f'Defender L3 - respawn offsets {defender_offsets}',
             'rows': shared_defence_rows(scenario)},
        ],
        0, 30, 4,
        'Seconds after the first attacking respawn; red means defenders have more returners at the front',
    )


# Appendix sensitivity: widen successive attacking returns from four to eight seconds
# while keeping Product routes and defender L3 fixed.
def spaced_return_rows(spawns, level):
    route = MODEL['inputs']['maps']['product']
    walk_time = route['walk']
    entrance_time = route['entrance']
    tele_travel_after_entrance = MODEL['inputs']['transit'] + route['exitToFront']
    cycles = MODEL['inputs']['cycles']
    ready = float('-inf')
    rows = []
    arrivals = []
    for player, spawn in enumerate(spawns, 1):
        if level == 'walk':
            arrival = spawn + walk_time
            mode = 'walk'
            entrance = None
        else:
            entrance = spawn + entrance_time
            use = max(entrance, ready)
            tele_arrival = use + tele_travel_after_entrance
            walk_arrival = spawn + walk_time
            if use - entrance <= 1.0 and tele_arrival < walk_arrival:
                arrival = tele_arrival
                mode = level
                ready = use + cycles[level]
            else:
                arrival = walk_arrival
                mode = 'walk'
                entrance = None
        arrivals.append(arrival)
        row = {
            'type': 'player',
            'label': f'A{player}',
            'spawn': spawn,
            'arrival': arrival,
            'team': 'attack',
            'note': f"{arrival:.1f}s {'walks' if mode == 'walk' else 'tele'}",
        }
        if entrance is not None:
            row['entrance'] = entrance
        rows.append(row)
    return rows, arrivals


def spaced_defence_rows(spawns):
    rows, arrivals = spaced_return_rows(spawns, 'l3')
    for player, row in enumerate(rows, 1):
        row['label'] = f'D{player}'
        row['team'] = 'defend'
    return rows, arrivals


def arrival_margin_intervals(attack_arrivals, defence_arrivals):
    changes = {}
    for arrival in attack_arrivals:
        changes[arrival] = changes.get(arrival, 0) + 1
    for arrival in defence_arrivals:
        changes[arrival] = changes.get(arrival, 0) - 1
    times = sorted(changes)
    margin = 0
    intervals = []
    for index, start in enumerate(times):
        margin += changes[start]
        if index + 1 >= len(times):
            continue
        end = times[index + 1]
        if end <= start:
            continue
        if intervals and intervals[-1]['margin'] == margin and abs(intervals[-1]['end'] - start) < 1e-6:
            intervals[-1]['end'] = end
        else:
            interval = {'start': start, 'end': end, 'margin': margin}
            if margin == 0:
                interval['label'] = 'even'
            intervals.append(interval)
    return intervals


attacker_spawns_8s = [0.0, 8.0, 16.0, 24.0]
for scenario_id, alignment_label, defender_spawns in (
        ('A', 'four-second defender alignment', [4.0, 12.0, 20.0, 28.0]),
        ('B', 'eight-second defender alignment', [8.0, 16.0, 24.0, 32.0])):
    defence_rows, defence_arrivals = spaced_defence_rows(defender_spawns)
    panels = []
    totals = {}
    for level, panel_title in (
            ('l3', 'Attacker L3 - every eight-second return is served'),
            ('l2', 'Attacker L2 - every eight-second return is served'),
            ('l1', 'Attacker L1 - the first and third returns are served'),
            ('walk', 'Attacker no tele - every return walks')):
        attack_rows, attack_arrivals = spaced_return_rows(attacker_spawns_8s, level)
        intervals = arrival_margin_intervals(attack_arrivals, defence_arrivals)
        totals[level] = sum((item['end'] - item['start']) * item['margin'] for item in intervals)
        attack_rows.append({
            'type': 'band',
            'label': 'advantage vs defender L3',
            'intervals': intervals,
        })
        panels.append({'title': panel_title, 'rows': attack_rows})
    panels.append({
        'title': f"Defender L3 - respawn offsets {', '.join(str(int(x)) for x in defender_spawns[:-1])} and {int(defender_spawns[-1])}",
        'rows': defence_rows,
    })
    render_explainer_timeline(
        f'product-eight-second-return-spacing-{scenario_id.lower()}.png',
        f'Product - four paired trades eight seconds apart; {alignment_label}',
        f"Attacking returns are eight seconds apart; totals: L3/L2 {totals['l3']:+.1f}, L1 {totals['l1']:+.1f}, no tele {totals['walk']:+.1f} p-s.",
        panels,
        0, 44, 4,
        'Seconds after the first attacking respawn; only attacking return spacing changed',
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
text(d, (90, 108), 'Each bar runs from a modelled retained-L3 arrival to a modelled no-tele walking arrival.', 26, fill=MUTED)
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
