import io
import os
import tempfile
import time
import subprocess
import concurrent.futures
from typing import List
from PyPDF2 import PdfReader
import docx
import fitz  
from PIL import Image
import pytesseract

#  Image Parser
def extract_text_from_image_bytes(image_bytes: bytes, timeout: int = 8) -> str:
    """
    Extract text from an image using Tesseract OCR with timeout.
    Skips empty or unreadable pages automatically.
    """
    try:
        # Save bytes to temporary file
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp.write(image_bytes)
            tmp_path = tmp.name

        # Run Tesseract OCR
        result = subprocess.run(
            ["tesseract", tmp_path, "stdout", "--dpi", "100"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout
        )

        # Remove temp file
        os.remove(tmp_path)

        # Extracted text
        text = result.stdout.strip()

        # Skip low-quality or blank pages
        if not text or len(text) < 20:
            print("[OCR SKIP] Page seems empty or unreadable. Skipping.")
            return ""

        return text

    except subprocess.TimeoutExpired:
        print("[OCR TIMEOUT] Skipping slow page.")
        return ""

    except Exception as e:
        print(f"[OCR ERROR] {e}")
        return ""
    


def parallel_ocr(doc: fitz.Document, blank_pages: List[int], max_pages: int = 5) -> List[str]:
    """
    Perform OCR on up to `max_pages` blank pages concurrently.
    Skips large or unreadable pages automatically.
    """
    ocr_results = []
    pages_to_process = blank_pages[:max_pages]

    def ocr_task(page_index):
        try:
            page = doc.load_page(page_index)
            pix = page.get_pixmap(dpi=72)

            # Skip extremely large images
            if pix.width * pix.height > 3_000_000:
                print(f"[OCR SKIP] Page {page_index + 1} too large ({pix.width}x{pix.height}) — skipping.")
                return ""

            img_bytes = pix.tobytes("png")
            return extract_text_from_image_bytes(img_bytes, timeout=8)

        except Exception as e:
            print(f"[OCR TASK ERROR] Page {page_index + 1}: {e}")
            return ""

    # Run OCR in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(ocr_task, idx) for idx in pages_to_process]
        for f in concurrent.futures.as_completed(futures):
            text = f.result()
            if text.strip():
                ocr_results.append(text)

    return ocr_results

def extract_image_ocr(pix, timeout=8):
    """Run OCR on a pixmap image safely."""
    try:
        start = time.time()

        img_bytes = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_bytes))

        # Timeout protection
        if time.time() - start > timeout:
            print("[OCR TIMEOUT] Skipping slow image.")
            return ""

        # Perform OCR
        text = pytesseract.image_to_string(img)

        # Filter low-quality OCR results
        if len(text.strip()) < 20:
            return ""

        return text.strip()

    except Exception as e:
        print(f"[OCR ERROR] {e}")
        return ""


# PDF Parser
def parse_pdf(file_bytes: bytes, ocr_timeout: int = 8, max_image_pixels: int = 3_000_000) -> str:
    """
    Smart PDF parser:
    - Extracts text normally first.
    - If a page has no text or very low text, performs OCR.
    - Skips huge images, unreadable pages, or slow pages.
    - Never crashes.
    """
    final_text = ""

    try:
        # Load PDF
        pdf = PdfReader(io.BytesIO(file_bytes))
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        total_pages = len(pdf.pages)

        print(f"[PDF INFO] Total pages: {total_pages}")

        for idx, page in enumerate(pdf.pages, start=1):
            print(f"\n--- Processing Page {idx}/{total_pages} ---")

            page_text = ""

            # STEP 1 → Normal text extraction
            try:
                raw_text = page.extract_text()
                if raw_text and raw_text.strip():
                    page_text = raw_text.strip()
                    print("[TEXT] Extracted via normal text extraction.")
                else:
                    print("[INFO] No text found. Might be scanned or image-only.")
            except Exception as e:
                print(f"[WARN] Normal extraction error: {e}")

            # STEP 2 → Use OCR only if necessary
            if not page_text:
                try:
                    fpage = doc.load_page(idx - 1)
                    pix = fpage.get_pixmap(dpi=150)   

                    # Skip huge pages (memory saver)
                    if pix.width * pix.height > max_image_pixels:
                        print(f"[OCR SKIP] Page too large ({pix.width}x{pix.height}). Skipping OCR.")
                    else:
                        print("[OCR] Running OCR on this page...")
                        ocr_text = extract_image_ocr(pix, timeout=ocr_timeout)
                        if ocr_text:
                            page_text = ocr_text
                            print("[OCR] OCR successful.")
                        else:
                            print("[OCR] OCR returned no text.")

                except Exception as e:
                    print(f"[OCR ERROR] Page {idx}: {e}")

            # FINAL DECISION: append text
            if page_text:
                final_text += page_text + "\n\n"
            else:
                print("[INFO] No extractable text on this page (even after OCR).")

    except Exception as e:
        print(f"[ERROR] PDF parsing failure: {e}")

    return final_text.strip()

# Docx Parser
def parse_docx(file_bytes: bytes) -> str:
    """Extract text from a DOCX document."""
    try:
        f = io.BytesIO(file_bytes)
        doc = docx.Document(f)
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n".join(paragraphs)
    except Exception as e:
        print(f"[DOCX ERROR] {e}")
        return ""


# Text Chunker
def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
    """
    Split text into overlapping chunks for embedding / RAG.
    Includes detailed logging for debugging and infinite-loop protection.
    """

    print("[chunk_text] Step 1: Starting text chunking...")
    print(f"[chunk_text] Received text length: {len(text)} characters")

    # Step 2: Normalize newlines
    text = text.replace("\r\n", "\n").strip()
    print("[chunk_text] Step 2: Normalized newlines.")

    # Step 3: Split into paragraphs and remove blank lines
    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    print(f"[chunk_text] Step 3: Paragraphs extracted: {len(paragraphs)}")

    # Step 4: Join paragraphs back into one continuous string
    joined = " ".join(paragraphs)
    print(f"[chunk_text] Step 4: Joined text length: {len(joined)}")

    # Step 5: Early exit if no valid text found
    if not joined:
        print("[chunk_text] Step 5: No valid text found. Returning empty list.")
        return []

    # Step 6: Prevent invalid parameters
    if chunk_size <= overlap:
        raise ValueError("[chunk_text] chunk_size must be greater than overlap to avoid infinite loops.")

    # Step 7: If text smaller than one chunk, return single chunk
    if len(joined) <= chunk_size:
        print("[chunk_text] Step 7: Text shorter than chunk size. Returning as single chunk.")
        return [joined]

    # Step 8: Initialize loop variables
    chunks = []
    start = 0
    length = len(joined)
    iteration = 0

    print(f"[chunk_text] Step 8: Starting chunk loop (length={length}, chunk_size={chunk_size}, overlap={overlap})")

    # Step 9: Main loop — create overlapping chunks
    while start < length:
        iteration += 1
        print(f"[chunk_text] Step 9.{iteration}: Iteration {iteration}, start={start}")

        # Calculate end index safely
        end = min(start + chunk_size, length)
        print(f"[chunk_text]    └─ Calculated end={end}")

        # Extract this chunk
        chunk = joined[start:end].strip()
        print(f"[chunk_text]    └─ Chunk length: {len(chunk)}")

        # Add chunk only if it's non-empty
        if chunk:
            chunks.append(chunk)
            print(f"[chunk_text]    └─ Added chunk #{len(chunks)}")

        # Move forward (overlap applied)
        next_start = start + chunk_size - overlap
        print(f"[chunk_text]    └─ Calculated next start position: {next_start}")

        # Stop if no progress (avoids infinite loop)
        if next_start <= start:
            print("[chunk_text] Detected no forward progress, breaking loop to avoid infinite loop.")
            break

        start = next_start

        # Stop if reached end
        if start >= length:
            print("[chunk_text] Step 10: Reached end of text. Breaking loop.")
            break

        # Safety guard
        if iteration > 100000:
            print("[chunk_text] Safety break: Too many iterations (possible infinite loop).")
            break

    #  Step 11: Summary
    print(f"[chunk_text] Step 11: Chunking complete. Total chunks created: {len(chunks)}")
    return chunks