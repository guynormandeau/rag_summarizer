import re
from transformers import pipeline

import fitz  # PyMuPDF

from docx import Document

def extract_text_from_docx(file_path):
    """Extracts text from a DOCX file."""
    try:
        doc = Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text
    except Exception as e:
        return f"Error extracting DOCX: {e}"

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file."""
    text = ""
    try:
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text("text") + "\n"
    except Exception as e:
        return f"Error extracting text from PDF: {str(e)}"
    return text.strip()

# Charger le modèle de résumé
summarizer = pipeline("summarization", model="google/flan-t5-base")

def chunk_text(text, chunk_size=1024):
    """Divise le texte en segments de `chunk_size` mots (plus longs pour améliorer la cohérence)."""
    words = text.split()
    return [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]

def clean_summary(text):
    """Corrige certaines erreurs linguistiques dans le résumé."""
    text = text.replace("and", "et").replace("of", "de")
    text = re.sub(r'\bmodéles\b', "modèles", text)
    text = re.sub(r'\bgrets\b', "grands", text)  # Correction automatique
    return text.strip()

def summarize_text(text, num_paragraphs=5):
    """Génère un résumé plus détaillé et mieux structuré."""

    text = text.strip().replace("\n", " ").replace("\r", " ")  # Nettoyage du texte

    if not text:
        return "Le fichier ne contient aucun texte exploitable."

    text_length = len(text.split())
    if text_length < 100:
        return "Le texte est trop court pour être résumé."

    # 🔹 AUGMENTATION DE LA LONGUEUR DU RÉSUMÉ
    max_length = int(min(text_length // 1.1, 1200))  # Augmenté à 1200 tokens pour un résumé plus complet
    min_length = int(max_length // 2)  # On s'assure que ce soit détaillé

    # 🔹 Segmentation du texte (évite une découpe trop fine)
    if text_length <= 1200:
        chunks = [text]
    else:
        chunks = chunk_text(text, chunk_size=1024)

    summarized_chunks = []
    for chunk in chunks:
        try:
            summary = summarizer(chunk, max_length=max_length, min_length=min_length, do_sample=False)
            summarized_chunks.append(summary[0]['summary_text'])
        except Exception as e:
            summarized_chunks.append(f"[Erreur : {str(e)}]")

    if not summarized_chunks or all("Erreur" in chunk for chunk in summarized_chunks):
        return "Erreur : Aucun résumé généré."

    # 🔹 AMÉLIORATION : On fusionne le résumé et ajuste mieux les paragraphes
    final_summary = " ".join(summarized_chunks)
    return split_into_paragraphs(final_summary, num_paragraphs)

def split_into_paragraphs(text, num_paragraphs):
    """Divise un résumé en plusieurs paragraphes équilibrés."""
    sentences = re.split(r'(?<=\.)\s+', text)  # Séparation par phrases

    if len(sentences) < num_paragraphs:
        num_paragraphs = len(sentences)  # Évite d'ajouter des paragraphes artificiels

    avg_sentences_per_paragraph = max(2, len(sentences) // num_paragraphs)

    paragraphs = []
    for i in range(0, len(sentences), avg_sentences_per_paragraph):
        paragraph = " ".join(sentences[i:i + avg_sentences_per_paragraph])
        paragraphs.append(paragraph.strip())

    return "\n\n".join(paragraphs[:num_paragraphs])  # Retourne exactement le nombre demandé