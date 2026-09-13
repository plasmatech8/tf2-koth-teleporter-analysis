# TF2 KOTH teleporter analysis

This repository contains plasmatech8's report on the reinforcement value of keeping or destroying an Engineer's teleporter exit during competitive Team Fortress 2 King of the Hill resets.

- Read the current PDF: [dark theme](output/pdf/TF2_KOTH_Teleporter_Report_Soft_Dark_v1.5.17.pdf) or [light theme](output/pdf/TF2_KOTH_Teleporter_Report_Light_v1.5.17.pdf)
- [Read the Markdown source](TF2_KOTH_Teleporter_Report.md)
- [See the data and privacy notes](docs/DATA.md)

The report combines a deterministic respawn and travel model with a demo audit. Its main comparison follows paired attacking and defending return waves through walking, teleporter construction, recharge, and front-line travel.

## Repository contents

- `TF2_KOTH_Teleporter_Report.md` — report source.
- `output/pdf/` — current published PDF only.
- `research/report_model.mjs` — mathematical scenario model.
- `research/report_figures.py` — chart generation.
- `research/build_report_pdf.py` — PDF renderer.
- `research/demo_extract/` — Source demo event and snapshot extractor.
- `research/*_audit.mjs` and related method notes — demo-audit logic without the private raw data.

## Rebuild and validation

The scripts require Node.js and Python 3. Python package requirements are imported directly by the scripts; the PDF build uses ReportLab, PyMuPDF, Pillow, pdfplumber, and pypdf, while the charts use Matplotlib.

```powershell
node research/report_model.mjs
node research/validate_report.mjs
python research/report_figures.py
python research/build_report_pdf.py --output=output/pdf/TF2_KOTH_Teleporter_Report_Light_v1.5.17.pdf
python research/build_report_pdf.py --dark --output=output/pdf/TF2_KOTH_Teleporter_Report_Soft_Dark_v1.5.17.pdf
python research/verify_report_release.py output/pdf/TF2_KOTH_Teleporter_Report_Light_v1.5.17.pdf
python research/verify_report_release.py output/pdf/TF2_KOTH_Teleporter_Report_Soft_Dark_v1.5.17.pdf
```

Raw demos and extracted player data are intentionally excluded. The mathematical report model and published aggregate outputs remain available without them.
