# bugox — Local Debugging Lab

A clean, offline-first error interpretation tool built for people learning Python and JavaScript. Paste a traceback and get an understandable explanation, the reported line number (when available), and concrete next steps.

**Features:** Python/JS error recognition, no-code-execution diagnostics, no-cost Streamlit interface, safe CLI/JSON output, input length caps, credential-shaped string redaction, and offline regression tests.

## Quick start

```bash
python -m venv .venv
python -m pip install -r requirements.txt
streamlit run app.py
```

Or use the CLI with **no third-party dependencies**:

```bash
echo "NameError: name 'total' is not defined" | python -m bugox.cli
python -m bugox.cli trace.txt --json
python -m unittest discover -s tests -v
```

## Privacy and limitations

No submitted code is executed. The engine never sends network requests, collects credentials, or calls a language model. Detected patterns are suggestions—not verified diagnoses. Secret redaction is best-effort; don't paste confidential logs into shared machines.

## Origin and license

This is a newly written, independent educational edition inspired by [DatDevSteve/bugnix](https://github.com/DatDevSteve/bugnix), which uses Azure AI and was released under Apache-2.0. The original project and its contributors are not claimed as original work here. This implementation does **not** copy the upstream source or binary assets. Repository license: MIT for newly authored code.
