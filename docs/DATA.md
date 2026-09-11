# Data and privacy

The real demo archive and its extracted data are intentionally excluded from Git. SourceTV demos and parser output can contain player names, Steam account IDs, chat messages, server details, positions, and other information that is unnecessary for reviewing the published analysis.

The ignored material includes:

- raw `.dem` and `.dem.bz2` recordings;
- line-delimited event and snapshot streams;
- per-demo audit JSON and CSV files;
- the private match-history notes and manual working archive;
- generated review packages and superseded report exports.

Public demo and log links may still appear in the report and findings because they point to already public source pages. Aggregate results, selected scene ticks, the mathematical model, and the current report are included.

## Local data layout

The historical scripts expect private inputs under `research/history/`. A local manifest can follow [the example](../examples/demo-manifest.example.json). The Rust extractor in `research/demo_extract/` writes a summary JSON file and a `.jsonl` event/snapshot stream for each demo.

Before running `research/history_audit.mjs`, set `TF2_ENGINEER_STEAM_ID` to the Engineer's Steam3 account ID, such as `[U:1:123456789]`. The value is read from the environment so it does not need to be saved in the repository.

```powershell
$env:TF2_ENGINEER_STEAM_ID = '[U:1:123456789]'
node research/history_audit.mjs
```

The `.gitignore` treats all files in `research/` as private by default and explicitly permits only reviewed source, aggregate output, and figures. New generated files therefore remain outside Git until they are deliberately reviewed and added to the allowlist.
