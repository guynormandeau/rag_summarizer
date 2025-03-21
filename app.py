import gradio as gr
import os
from summarizer import summarize_text, extract_text_from_pdf, extract_text_from_docx

def process_file(file_path, num_paragraphs):
    """Handles reading and summarizing files."""
    file_extension = file_path.split('.')[-1].lower()

    if file_extension == "txt":
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                extracted_text = file.read()
        except UnicodeDecodeError:
            with open(file_path, "r", encoding="latin-1") as file:  # Fallback en latin-1
                extracted_text = file.read()

    elif file_extension == "docx":
        extracted_text = extract_text_from_docx(file_path)
        print(f"Extracted text from DOCX: {extracted_text[:500]}")  # Afficher les 500 premiers caractères
    elif file_extension == "pdf":
        extracted_text = extract_text_from_pdf(file_path)
    else:
        return "Error: Unsupported file format."

    return summarize_text(extracted_text, num_paragraphs)

def upload_and_summarize(file, num_paragraphs):
    """Handles file upload and calls the summarization function."""
    if file is None:
        return "Error: Please upload a valid file."
    
    file_path = file.name
    return process_file(file_path, num_paragraphs)

# Gradio UI in English
with gr.Blocks() as demo:
    gr.Markdown("## **Automatic Text Summarizer**")
    gr.Markdown("Upload a **TXT, DOCX, or PDF** file and choose the number of paragraphs for the summary.")

    file_input = gr.File(label="Upload File")
    num_paragraphs_slider = gr.Slider(minimum=1, maximum=10, value=5, step=1, label="Number of Summary Paragraphs")
    
    output_text = gr.Textbox(label="Summary Output", interactive=False)
    
    submit_button = gr.Button("Generate Summary")
    clear_button = gr.Button("Clear")

    submit_button.click(upload_and_summarize, inputs=[file_input, num_paragraphs_slider], outputs=output_text)
    clear_button.click(lambda: "", inputs=[], outputs=output_text)

demo.launch(share=True)