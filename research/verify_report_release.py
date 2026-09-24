"""Check exported content, table pagination, text bounds and theme colours."""
from pathlib import Path
import re
import sys
import pdfplumber
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_OVERRIDE = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else None
EXPECTED_VERSION = "1.7.0"
texts = []
targets = (
    ("light", "TF2_KOTH_Teleporter_Report_Light.pdf", "17678f", "ffffff"),
    ("dark", "TF2_KOTH_Teleporter_Report_Soft_Dark.pdf", "78b1cc", "ded9cf"),
) if OUTPUT_OVERRIDE is None else (
    (("light", OUTPUT_OVERRIDE.name, "17678f", "ffffff")
     if "Light" in OUTPUT_OVERRIDE.name
     else ("dark", OUTPUT_OVERRIDE.name, "78b1cc", "ded9cf")),
)
for theme, filename, blue, header in targets:
    path = OUTPUT_OVERRIDE if OUTPUT_OVERRIDE else ROOT / "output/pdf" / filename
    reader = PdfReader(path)
    pages = [p.extract_text() or "" for p in reader.pages]
    text = "\n".join(pages)
    normal = re.sub(r"\s+", " ", text)
    assert f"v{EXPECTED_VERSION}" in reader.metadata.subject
    assert reader.metadata.author == "plasmatech8 (w/ Codex)"
    assert all(f"v{EXPECTED_VERSION} | 24 September 2026" in p for p in pages)
    assert "Author: plasmatech8 (w/ Codex)" in pages[0]
    for required in (
        "209 near-simultaneous opposing death pairs",
        "four seconds for 123 pairs",
        "3.105 seconds apart",
        "modelled no-tele walking arrival",
        "a defender may walk when two defenders share one charged L3",
        "A Level 3 teleporter has 216 health, compared with 150 at Level 1",
        "The live game state may not fit one clean label",
        "51.94 x 1 + 5.84 x 2 = 63.62",
        "125874 / 31:28.11", "131458", "75.33-second",
        "tick 64995 / 16:14.92", "tick 65190", "tick 65337",
        "No reset call was made; a near-wipe continued as a fight",
        "A is the four-second defender gap and B is the eight-second defender gap",
        "8.7 seconds after placement", "wait no more than one second",
        "one attacker returns on each successive four-second attacking wave",
        "giving a theoretical 50% chance of +2 when two players per team trade lives",
        "With two returning attackers, keeping L3 gives a clear advantage over rebuilt L1",
        "maintains at least +1 for 9.4 seconds on Product or 10.4 seconds on Ashville",
        "This compares our returners with the defenders' returning cohort",
        "This report does two things. First, it models baseline teleporter reinforcement value for attackers",
        "7-9 seconds of staging or survival before the next relevant death",
        "The 7-9 second figure is a minimum delay, not a window",
        "retained L3 could have brought Sniper back about 6.4 seconds earlier",
        "In a later Product round-three grass-door contest",
        "crossed the audit's front-line threshold sooner than the generic rollout model predicted",
        "allow an additional return during a long fight",
        "Teleporter transfer sequence",
        "Appendix: expanded Product scenario timelines",
        "Product scenario 4A - four-second defender alignment",
        "Product scenario 4B - eight-second defender alignment",
        "Sensitivity: attacking returns eight seconds apart",
        "Sensitivity continued: eight-second defender alignment",
        "L2 recharges in time to serve every rider and therefore matches L3",
        "The no-tele case briefly falls to one fewer returning player at the front",
        "READY -> SENDING -> RECEIVING -> RECEIVING_RELEASE -> RECHARGING -> READY",
        "Destroying the exit removes one immediate misuse risk but can weaken reinforcement later",
        "A team may adopt an after-wipe destruction policy",
        "A player dies late or respawns behind the group",
        "Favours keeping the exit",
        "Favours destroying the exit",
        "Changes how much either choice matters",
        "300-HU/s baseline routes",
        "charged L3: 6.6 s travel",
        "Conclusion: when keeping or destroying helps",
    ):
        assert required in normal, (filename, required)
    assert not re.search(r"@@TOKEN|<font|</b>|travels 6\.6", text)
    for name in ("Main Product comparison", "Main Ashville comparison"):
        page = next(p for p in pages if name in p and "4B" in p)
        assert all(case in page for case in ("1A", "1B", "2A", "2B", "3A", "3B", "4A", "4B"))
        assert page.index("No tele") < page.index("Rebuild L1") < page.index("Rebuild L2") < page.index("Keep L3")
    rides = next(p for p in pages if "One connection: an unsafe use" in p)
    assert all(str(t) in rides for t in (126525,127164,128040,129327,129573,130413,130746))
    with pdfplumber.open(path) as pdf:
        for n, page in enumerate(pdf.pages, 1):
            assert all(-0.5 <= c["x0"] <= c["x1"] <= page.width + 0.5
                       and -0.5 <= c["top"] <= c["bottom"] <= page.height + 0.5
                       for c in page.chars), (filename, n, "text outside page")
        def rgb(colour):
            return "".join(f"{round(c * 255):02x}" for c in colour)
        # +1s in the explanatory paragraph must use the selected blue.
        explanation = next(p for p in pdf.pages if "Three quantities must stay separate" in (p.extract_text() or ""))
        runs = list(zip(explanation.chars, explanation.chars[1:]))
        ones = [a for a,b in runs if a["text"] == "+" and b["text"] == "1"]
        assert ones and all(rgb(c["non_stroking_color"]) == blue for c in ones), (theme, "+1 colour")
        # Bold header text must remain legible against the dark table header.
        main = next(p for p in pdf.pages if "Main Product comparison" in (p.extract_text() or "") and "4B" in (p.extract_text() or ""))
        words = main.extract_words(extra_attrs=["non_stroking_color"])
        candidates = [w for w in words if w["text"] in {"Keep", "Rebuild"}]
        header_top = min(w["top"] for w in candidates)
        headers = [w for w in candidates if abs(w["top"] - header_top) < 1]
        assert len(headers) >= 3 and all(rgb(w["non_stroking_color"]) == header for w in headers), (theme, "table headers")
    texts.append(text)
    print(f"{filename}: {len(pages)} pages; content, pagination, bounds and colours checked")
if len(texts) == 2:
    assert texts[0] == texts[1], "Light and dark content/layout differ"
print("Release checks passed")
