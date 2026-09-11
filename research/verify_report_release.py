"""Check exported content, table pagination, text bounds and theme colours."""
from pathlib import Path
import re
import sys
import pdfplumber
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_OVERRIDE = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else None
EXPECTED_VERSION = "1.5.16"
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
    assert reader.metadata.author == "plasmatech8"
    assert all(f"v{EXPECTED_VERSION} | 12 September 2026" in p for p in pages)
    assert "Author: plasmatech8" in pages[0]
    for required in (
        "199 near-simultaneous opposing death pairs",
        "51.94 x 1 + 5.84 x 2 = 63.62",
        "125874 / 31:28.11", "131458", "75.33-second",
        "tick 64995 / 16:14.92", "tick 65190", "tick 65337",
        "Near-reset became a continued fight",
        "A and B mean the two possible defender respawn-wave arrangements",
        "8.7 seconds after placement", "wait no more than one second",
        "one attacker returns on each successive four-second attacking wave",
        "giving a theoretical 50% chance of +2 when two players per team trade lives",
        "With two returning attackers, keeping L3 gives a clear advantage over rebuilt L1",
        "maintains at least +1 for 9.4 seconds on Product or 10.4 seconds on Ashville",
        "This compares our returners with theirs, not the direct L3-versus-L1 comparison below",
        "Destroying the exit trades immediate safety for potentially weaker reinforcement later",
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
