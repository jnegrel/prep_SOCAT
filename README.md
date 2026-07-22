# SOCAT_prep

A Python script to automate the preparation of oceanographic datasets for submission to [SOCAT](https://www.socat.info/) (Surface Ocean CO₂ Atlas).

## Overview

`prep_SOCAT.py` bridges two data infrastructure systems used in the ICOS (Integrated Carbon Observation System) ocean data pipeline, and requires a user-provided metadata template:

1. **[QuinCE](https://quince.icos-cp.eu/)** – quality control system where processed datasets are stored
2. **[ICOS Carbon Portal](https://www.icos-cp.eu/)** – data repository providing persistent identifiers (PIDs/DOIs)
3. **OADS XML template** – a dataset-specific metadata file pre-filled by the user (see [XML template](#xml-template))

The script downloads a dataset from QuinCE, enriches it with metadata from the Carbon Portal, populates a SOCAT-compliant OADS XML metadata file, prepends the required SOCAT header to the TSV data file, and copies the resulting `.tsv` and `.xml` files to an output folder ready for SOCAT upload. The script runs on both Linux and Windows.

## Workflow

```
QuinCE API ──► Download dataset (zip)
                     │
                     ▼
              Unpack & read manifest.json + .tsv
                     │
                     ▼
         ICOS Carbon Portal (SPARQL) ──► Retrieve URI / PID
                     │
                     ▼
         OADS XML template ──► Populate with metadata ("TK" placeholders)
                     │
                     ▼
              Write SOCAT header to .tsv
                     │
                     ▼
         Move .tsv + .xml ──► output folder (SOCAT-ready)
                     │
                     ▼
              Clean up temporary files
```

## Requirements

- Python 3.x
- [`icoscp_core`](https://pypi.org/project/icoscp-core/) – ICOS Carbon Portal client
- [`requests`](https://pypi.org/project/requests/) – HTTP library for the QuinCE API
- `os`, `sys`, `json`, `zipfile`, `tempfile`, `shutil`, `xml.etree.ElementTree`, `datetime` – Python standard library (included with Python)

Install third-party dependencies:

```bash
pip install icoscp-core requests
```

## Directory structure

```
SOCAT_prep/
├── prep_SOCAT.py          # Main script
├── Data/
│   ├── credentials.json   # QuinCE connection credentials (not committed)
│   └── <name>_template.xml  # OADS XML template for the dataset
└── README.md
```

### `credentials.json` format

```json
{
    "url":      "https://<quince-instance>/api/",
    "username": "<your-username>",
    "password": "<your-password>"
}
```

> **Note:** Keep `credentials.json` out of version control (add it to `.gitignore`).

### XML template

The OADS XML template (schema `a0.2.2s`) must be pre-filled with all static metadata (investigators, instruments, methods, etc.). Fields that the script fills in automatically are marked with the placeholder `TK`:

| XML tag | Source |
|---|---|
| `metadataRecordCreationDate` | Current date |
| `submissionDate` | `manifest.json` → `last_touched` |
| `metadataURL` / `datasetURL` | Carbon Portal URI |
| `datasetDOI` | Carbon Portal PID |
| `startDate` / `endDate` | `manifest.json` → SOCAT export bounds |
| `westernBounds` … `southernBounds` | `manifest.json` → SOCAT spatial bounds |
| `expocode` | `manifest.json` → dataset name |

## Usage

```bash
python prep_SOCAT.py -n <dataset_name> -S <template_name> [options]
```

### Required arguments

| Flag | Description |
|---|---|
| `-n`, `--name` | Dataset name as stored in QuinCE (with or without `.zip` extension) |
| `-S`, `--SOCAT` | OADS XML template filename (with or without `.xml` extension), looked up in the data folder |

### Optional arguments

| Flag | Default | Description |
|---|---|---|
| `-t`, `--tmp` | System temp folder | Temporary working directory |
| `-o`, `--output` | Dataset name | Output folder for the final `.tsv` and `.xml` files |
| `-d`, `--data` | `Data/` | Folder containing `credentials.json` and the XML template |
| `-v`, `--version` | — | Print version and exit |

### Example

```bash
python prep_SOCAT.py -n 119920230901 -S 1199_template -d Data/ -o output/
```

This will:
1. Download `119920230901` from QuinCE
2. Read `Data/1199_template.xml` and fill in the `TK` fields
3. Query the Carbon Portal for the corresponding PID/URI
4. Prepend the SOCAT header to the TSV file
5. Write `output/119920230901.tsv` and `output/119920230901.xml` ready for SOCAT upload

## Exit codes

| Code | Category | Cause |
|---|---|---|
| `0` | Success | |
| `2` | Bad arguments | Missing `-n` or `-S` argument |
| `3` | Setup / config error | Cannot create folder or load `credentials.json` |
| `4` | Connection / download error | HTTP failure, network error, or empty response |
| `5` | File I/O error | Cannot read/write XML template, zip, manifest, or output files |
| `6` | Data error | SPARQL query to Carbon Portal failed or returned no results |

## Version

Current version: **1.1**

### Changelog

- **1.1** – Output the SOCAT-ready `.tsv` and `.xml` files directly to the output folder instead of repacking into a zip archive. Added Windows compatibility (system-independent temp folder and path handling). Various bug fixes.
- **1.0** – Initial release.

## Author

Jean Negrel (jean.negrel@norceresearch.no), NORCE Research AS, Bergen
