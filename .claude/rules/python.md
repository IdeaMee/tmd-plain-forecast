---
paths:
  - "src/**/*.py"
  - "api/**/*.py"
  - "scripts/**/*.py"
  - "tests/**/*.py"
---
# Python rules (offline pipeline + one Vercel function)

Loaded whenever Python is touched. For adding or changing a pipeline stage, use the `python-pipeline` skill; for Thai text, the `thai-text-handling` skill.

## Structure
- All logic lives in the package under `src/tmd_plain/<stage>/`. `scripts/` only calls the package. `api/` holds thin entry files: parse the request, call the package, return JSON. No logic there; helpers in `api/` start with `_`.
- One package is shared by the laptop scripts and the Vercel function. Runtime dependencies stay minimal (PyThaiNLP, pypdfium2, pdfminer.six, Pydantic). No scikit-learn, pandas, numpy in code that ships.

## Code
- Each pipeline step is a pure function: typed input model in, typed output model out. No I/O, no global state, no mutation of arguments. I/O happens in the runner.
- Pydantic models at boundaries (files, DB rows, API). `@dataclass(frozen=True)` inside. Type hints on every public function (`X | None`).
- Config values (paths, thresholds, k, m-estimate) in a config file, not in code. Secrets from env only.
- Deterministic output: fixed seeds, sorted inputs, no timestamps inside result files (put them in metadata).
- Logging: `logger = logging.getLogger(__name__)`, `logger.info("x=%s", x)` (no f-strings in log calls). Configure logging only in entry points. `print` only for CLI output the user must see.
- Errors: raise a specific built-in exception, never bare `except:`, keep `try` blocks short. One bad record is logged as a warning, skipped, and counted; it must not stop the whole run.
- Ruff for lint and format (relax E501 if it only trips on Thai comments).

## Thai and encoding
- Open every file with `encoding="utf-8"`. Write JSON with `ensure_ascii=False, sort_keys=True, indent=2`.
- Tokenize with PyThaiNLP `newmm` plus the weather dictionary. Clean text extracted from PDFs before anything else (order and known defects: `thai-text-handling` skill).
- Comments and docstrings in Thai, one short line; identifiers in English.

## Output fidelity (never break)
- Every number, province name and advice sentence in generated output must appear in the source text of that region. Advice is copied verbatim, never written by the model or the code.
- Never turn "ร้อยละ N ของพื้นที่" into a probability. Use TMD's own thresholds when explaining levels.
- Unsupported or garbled input returns a typed error, not a guess.

## Tests
- pytest. Golden files for stage outputs (review the diff before updating a snapshot). Contract test: JSON the pipeline writes must validate against the schema the web app uses.
