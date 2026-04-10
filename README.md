# 📄 Resume Scanner

**AI-powered resume matching tool that ranks candidates by similarity to job descriptions using semantic analysis.**

## 🚀 Features

- **📊 Smart Text Extraction**: Supports PDF, DOCX, TXT, and image formats
- **🔍 OCR Fallback**: Automatic OCR when direct extraction fails
- **🧠 Semantic Matching**: Uses sentence transformers for intelligent similarity scoring
- **📈 Ranked Results**: Automatically sorts candidates by match score
- **🔄 Batch Processing**: Scans entire directories of resumes

## 📋 Requirements

### Dependencies
```bash
pip install python-docx pytesseract pillow numpy scikit-learn sentence-transformers PyMuPDF
```

### System Requirements
- **Tesseract OCR**: Required for image and scanned document processing
  - Windows: Download from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
  - macOS: `brew install tesseract`
  - Linux: `sudo apt-get install tesseract-ocr`

## 🛠️ Setup

1. **Clone/Download** the script
2. **Install dependencies** (see above)
3. **Configure paths** in the script:
   ```python
   RESUMES_DIRECTORY = r"path/to/your/resumes"
   job_description_path = "your_job_description.pdf"
   ```
4. **Add your files**:
   - Place job description in the root directory
   - Create a folder named "Sample Resumes" and add all resumes in it

## 📁 Supported File Types

| Format | Method | Symbol |
|--------|--------|--------|
| PDF | Direct + OCR | 📄 |
| DOCX | Direct | 📝 |
| TXT | Direct | 📃 |
| Images | OCR Only | 🖼️ |

*Supported image formats: PNG, JPG, JPEG, TIFF, BMP, GIF*

## ⚡ Usage

```bash
python resume_scanner.py
```

### Output Example
```
--- Match Results (Sorted by Score) ---
Rank 1: Resume: john_doe.pdf, Score: 0.8542, Method: direct_pdf
Rank 2: Resume: jane_smith.docx, Score: 0.7891, Method: direct_docx
Rank 3: Resume: alex_jones.png, Score: 0.6734, Method: ocr
```

## ⚙️ Configuration

### Key Settings
```python
TEXT_LENGTH_THRESHOLD = 100        # Minimum text length for valid extraction
RESUMES_DIRECTORY = "path/to/resumes"  # Resume folder path
RESUME_EXTENSIONS = ['.pdf', '.docx', '.txt', '.png', '.jpg', '.jpeg']
```

### Model Selection
Default: `all-MiniLM-L6-v2` (fast, accurate)
- Change in `load_sentence_transformer_model()` function

## 🔧 How It Works

1. **📖 Text Extraction**: Direct parsing → OCR fallback if needed
2. **🤖 Embedding Generation**: Converts text to numerical vectors
3. **📐 Similarity Calculation**: Cosine similarity between job description and resumes
4. **📊 Ranking**: Sort candidates by match score (0.0 - 1.0)

## 🎯 Scoring Guide

| Score Range | Match Quality | Action |
|-------------|---------------|---------|
| 0.8 - 1.0 | Excellent | 🟢 Strong candidate |
| 0.6 - 0.8 | Good | 🟡 Consider for interview |
| 0.4 - 0.6 | Fair | 🟠 Review manually |
| 0.0 - 0.4 | Poor | 🔴 Likely not a match |

## 🚨 Troubleshooting

### Common Issues

**❌ "Tesseract not found"**
- Install Tesseract OCR and add to PATH

**❌ "No resume files found"** 
- Check `RESUMES_DIRECTORY` path
- Verify file extensions match `RESUME_EXTENSIONS`

**❌ "Model loading failure"**
- Ensure internet connection for first run
- Check Python environment has required packages

**❌ "Insufficient text extracted"**
- Check if documents are password protected
- Try OCR for scanned documents
- Verify file isn't corrupted

## 📈 Performance Tips

- **🔥 Fast Processing**: Use PDF/DOCX when possible (direct extraction)
- **🎯 Better Accuracy**: Ensure job descriptions are detailed
- **💾 Memory**: Large batches may require more RAM for embeddings
- **⚡ Speed**: First run slower due to model download

## 🤝 Contributing

Found a bug or want to add features? Contributions welcome!

## 📄 License

Open source - feel free to modify and distribute.
