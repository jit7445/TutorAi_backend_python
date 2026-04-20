import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from docx import Document

def generate_notes(notes_data: dict, output_dir: str) -> dict:
    os.makedirs(output_dir, exist_ok=True)
    topic = notes_data.get("topic", "Topic")
    notes = notes_data.get("notes", [])
    
    pdf_path = os.path.join(output_dir, "notes.pdf")
    doc_path = os.path.join(output_dir, "notes.docx")
    
    # PDF using reportlab
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, f"Topic: {topic}")
    
    c.setFont("Helvetica", 12)
    y = height - 80
    for note in notes:
        # Simple rendering for now
        if y < 50:
            c.showPage()
            y = height - 50
        c.drawString(50, y, f"• {note[:90]}...")
        y -= 20
    c.save()
    
    # DOCX using python-docx
    doc = Document()
    doc.add_heading(f"Topic: {topic}", 0)
    
    for note in notes:
        doc.add_paragraph(note, style='List Bullet')
        
    doc.save(doc_path)
    
    return {
        "pdf_path": pdf_path,
        "doc_path": doc_path
    }
