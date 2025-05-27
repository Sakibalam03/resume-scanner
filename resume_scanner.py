import os
import io
import docx
import pytesseract
from PIL import Image
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import fitz 

TEXT_LENGTH_THRESHOLD = 100

RESUMES_DIRECTORY = r"C:\Users\sensh\OneDrive\Desktop\Projects\Resume Scanner\Sample Resumes"

RESUME_EXTENSIONS = ['.pdf', '.docx', '.txt', '.png', '.jpg', '.jpeg']

def extract_text_from_pdf_direct(pdf_path):
    text = ""
    try:
        doc = fitz.open(pdf_path)
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            text += page.get_text()
        doc.close()
        return text
    except Exception as e:
        return None 

def extract_text_from_docx_direct(docx_path):
    text = ""
    try:
        doc = docx.Document(docx_path)
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    except Exception as e:
        return None 

def extract_text_from_txt_direct(txt_path):
    try:
        with open(txt_path, 'r', encoding='utf-8') as f:
            text = f.read()
        return text
    except Exception as e:
        return None


def extract_text_with_ocr(file_path):
    text = ""
    try:
        if file_path.lower().endswith(('.pdf', '.xps', '.epub', '.fb2')): 
             doc = fitz.open(file_path)
             for page_num in range(doc.page_count):
                 page = doc.load_page(page_num)
                 pix = page.get_pixmap()
                 img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

                 page_text = pytesseract.image_to_string(img)
                 text += page_text + "\n" 
             doc.close()
        elif file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')): 
            img = Image.open(file_path)
            text = pytesseract.image_to_string(img)
        else:
             print(f"Warning: Attempting OCR on potentially unsupported file type {os.path.basename(file_path)}.")
             try:
                 doc = fitz.open(file_path)
                 for page_num in range(doc.page_count):
                     page = doc.load_page(page_num)
                     pix = page.get_pixmap()
                     img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                     page_text = pytesseract.image_to_string(img)
                     text += page_text + "\n"
                 doc.close()
             except Exception as e:
                 print(f"Error opening {os.path.basename(file_path)} with PyMuPDF for OCR: {e}")
                 return None


        return text.strip()

    except pytesseract.TesseractNotFoundError:
        print("Tesseract is not installed or not in your PATH. Please install it.")
        return None
    except Exception as e:
        print(f"Error during OCR extraction from {os.path.basename(file_path)}: {e}")
        return None 

def get_document_text(file_path):
    base_name = os.path.basename(file_path)
    text = None
    method = 'unknown' 

    if file_path.lower().endswith('.pdf'):
        text = extract_text_from_pdf_direct(file_path)
        method = 'direct_pdf'
    elif file_path.lower().endswith('.docx'):
        text = extract_text_from_docx_direct(file_path)
        method = 'direct_docx'
    elif file_path.lower().endswith('.txt'):
        text = extract_text_from_txt_direct(file_path)
        method = 'direct_txt'

    if text is not None and len(text.strip()) >= TEXT_LENGTH_THRESHOLD:
        print(f"Direct extraction successful for {base_name} using {method}.")
        return text.strip(), method

    if method != 'unknown':
         print(f"Direct extraction failed or insufficient text ({len(text.strip()) if text is not None else 0} chars) for {base_name} using {method}. Falling back to OCR.")
    else:
         print(f"Attempting OCR for {base_name} as direct extraction method is unknown.")

    method = 'ocr'
    text = extract_text_with_ocr(file_path)

    if text is not None and len(text.strip()) >= TEXT_LENGTH_THRESHOLD:
        print(f"OCR extraction successful for {base_name}.")
        return text.strip(), method
    else:
        method = 'failed'
        print(f"OCR extraction also failed or insufficient text ({len(text.strip()) if text is not None else 0} chars) for {base_name}.")
        return "", method 

def load_sentence_transformer_model(model_name='all-MiniLM-L6-v2'):
    try:
        model = SentenceTransformer(model_name)
        print(f"Successfully loaded Sentence Transformer model: {model_name}")
        return model
    except Exception as e:
        print(f"Error loading Sentence Transformer model {model_name}: {e}")
        print("Please ensure you have an internet connection to download the model.")
        return None

def get_embedding(text, model):
    if not text or not model:
        return None
    try:
        embedding = model.encode(text, convert_to_numpy=True)
        return embedding
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return None

def calculate_similarity(embedding1, embedding2):
    if embedding1 is None or embedding2 is None:
        return None
    try:
        similarity_score = cosine_similarity(embedding1.reshape(1, -1), embedding2.reshape(1, -1))[0][0]
        return max(0.0, min(1.0, similarity_score))
    except Exception as e:
        print(f"Error calculating similarity: {e}")
        return None


if __name__ == "__main__":
    job_description_path = "Sample Job Description.pdf"

    resume_paths = []
    if not os.path.isdir(RESUMES_DIRECTORY):
        print(f"Error: Resumes directory not found at {RESUMES_DIRECTORY}")
        exit()

    print(f"Scanning directory: {RESUMES_DIRECTORY} for resume files...")
    for root, _, files in os.walk(RESUMES_DIRECTORY):
        for file in files:
            if os.path.splitext(file)[1].lower() in RESUME_EXTENSIONS:
                resume_paths.append(os.path.join(root, file))

    if not resume_paths:
        print(f"No resume files found in {RESUMES_DIRECTORY} with extensions: {', '.join(RESUME_EXTENSIONS)}")
        exit()

    print(f"Found {len(resume_paths)} resume files to process.")

    embedding_model = load_sentence_transformer_model('all-MiniLM-L6-v2')

    if embedding_model is None:
        print("Exiting due to model loading failure.")
        exit()

    print("\n--- Processing Job Description ---")
    jd_text, jd_extraction_method = get_document_text(job_description_path)
    print(f"Extraction method for JD: {jd_extraction_method}")

    if not jd_text:
        print("Could not extract text from Job Description. Cannot proceed.")
        exit()

    jd_embedding = get_embedding(jd_text, embedding_model)
    if jd_embedding is None:
        print("Could not generate embedding for Job Description. Cannot proceed.")
        exit()

    print("\n--- Processing Resumes and Calculating Scores ---")
    match_results = []

    for resume_path in resume_paths:
        print(f"\nProcessing {os.path.basename(resume_path)}...")
        resume_text, resume_extraction_method = get_document_text(resume_path)
        print(f"Extraction method for Resume: {resume_extraction_method}")

        if not resume_text:
            print(f"Skipping {os.path.basename(resume_path)} due to text extraction failure.")
            continue

        resume_embedding = get_embedding(resume_text, embedding_model)

        if resume_embedding is None:
             print(f"Skipping {os.path.basename(resume_path)} due to embedding generation failure.")
             continue

        similarity_score = calculate_similarity(jd_embedding, resume_embedding)

        if similarity_score is not None:
            match_results.append({
                "resume": os.path.basename(resume_path),
                "score": similarity_score,
                "extraction_method": resume_extraction_method
            })
            print(f"Similarity Score: {similarity_score:.4f}")
        else:
            print(f"Could not calculate score for {os.path.basename(resume_path)}.")


    print("\n--- Match Results (Sorted by Score) ---")
    if match_results:
        match_results.sort(key=lambda x: x['score'], reverse=True)

        for i, result in enumerate(match_results):
            print(f"Rank {i+1}: Resume: {result['resume']}, Score: {result['score']:.4f}, Method: {result['extraction_method']}")
    else:
        print("No match results to display.")

