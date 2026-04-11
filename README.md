# Resume Scanner

A CLI tool that ranks resumes against a job description using semantic similarity. Text is extracted from uploaded documents, converted to sentence embeddings, and scored via cosine similarity.

---

## What It Does

1. Reads a job description file (PDF, DOCX, or TXT)
2. Reads all resume files in a configured directory
3. Extracts text from each file — direct parsing for PDF/DOCX/TXT, OCR fallback for images or scanned documents
4. Generates embeddings using a local sentence transformer model (`all-MiniLM-L6-v2`)
5. Scores each resume by cosine similarity to the job description
6. Prints ranked results to the console

There is no AI reasoning, keyword weighting, or section-aware analysis — scoring is purely semantic similarity between full documents.

---

## Supported File Types

| Format | Extraction Method |
|--------|-------------------|
| PDF | Direct text extraction via PyMuPDF; falls back to OCR if text is sparse |
| DOCX | Direct via python-docx |
| TXT | Plain file read |
| PNG, JPG, JPEG | OCR via pytesseract |

---

## Requirements

**System dependency — install separately before running:**

- [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki) (required for image and scanned PDF support)
  - Windows: download installer from link above
  - macOS: `brew install tesseract`
  - Linux: `sudo apt-get install tesseract-ocr`

**Python dependencies:**

```bash
pip install -r requirements.txt
```

---

## Setup

1. Clone the repo
2. Install Tesseract OCR (see above)
3. Install Python dependencies: `pip install -r requirements.txt`
4. Copy `.env` and edit paths if needed:

```env
RESUMES_DIRECTORY=Sample Resumes
JOB_DESCRIPTION_PATH=Sample Job Description.pdf
EMBEDDING_MODEL=all-MiniLM-L6-v2
TEXT_LENGTH_THRESHOLD=100
```

5. Place your job description file and resumes folder in the project root (or set custom paths in `.env`)

---

## Usage

```bash
python resume_scanner.py
```

Example output:

```
Scanning directory: Sample Resumes for resume files...
Found 3 resume files to process.

--- Processing Job Description ---
Direct extraction successful for Sample Job Description.pdf using direct_pdf.

--- Processing Resumes and Calculating Scores ---
Processing Sakib ML Resume.pdf...
Similarity Score: 0.7812

Processing Sakib Alam Resume.docx...
Similarity Score: 0.7341

Processing Sakib Resume.png...
OCR extraction successful for Sakib Resume.png.
Similarity Score: 0.6918

--- Match Results (Sorted by Score) ---
Rank 1: Resume: Sakib ML Resume.pdf, Score: 0.7812, Method: direct_pdf
Rank 2: Resume: Sakib Alam Resume.docx, Score: 0.7341, Method: direct_docx
Rank 3: Resume: Sakib Resume.png, Score: 0.6918, Method: ocr
```

---

## Score Interpretation

Scores range from 0.0 to 1.0. Higher means more semantically similar content between the resume and job description. These are not calibrated thresholds — treat scores as relative rankings within a batch, not absolute pass/fail values.

| Range | Rough interpretation |
|-------|----------------------|
| > 0.75 | Strong topical overlap |
| 0.55 – 0.75 | Moderate overlap |
| < 0.55 | Low overlap |

---

## Limitations

- No UI — results are printed to console only
- Paths must be configured manually in `.env`
- OCR quality depends on Tesseract and document scan quality
- Model runs entirely locally; first run downloads ~90MB model weights
- No section-aware parsing — the entire resume text is treated as one document
- No keyword extraction, skill matching, or experience weighting

---

## Troubleshooting

**`TesseractNotFoundError`** — Tesseract is not installed or not on PATH. Install it and ensure it is accessible from the terminal.

**`No resume files found`** — Check `RESUMES_DIRECTORY` in `.env` matches the actual folder name and location.

**`Model loading failure`** — Requires internet access on first run to download model weights (~90MB). Subsequent runs use the cached model.

**Low text extraction** — If a PDF is a scanned image, direct extraction will return very little text and OCR will be used automatically.
