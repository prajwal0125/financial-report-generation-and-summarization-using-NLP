from flask import Flask, render_template, request, send_from_directory
import os
from transformers import pipeline
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from langchain.text_splitter import RecursiveCharacterTextSplitter

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
REPORT_FOLDER = 'reports'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORT_FOLDER, exist_ok=True)

# Load Hugging Face pipelines
extractor = pipeline("question-answering", model="deepset/roberta-base-squad2")
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# Define financial queries
queries = {
    "Total Revenue": "What is the company's total revenue?",
    "Product Sales Revenue": "How much revenue came from product sales?",
    "Service Revenue": "What is the service revenue?",
    "Subscription Revenue": "How much subscription revenue was earned?",
    "Total Expenses": "What are the total company expenses?",
    "COGS": "What is the cost of goods sold (COGS)?",
    "Marketing & R&D Expenses": "What are the marketing and R&D expenses?",
    "Net Profit": "What is the net profit?",
    "Profit Margin": "What is the company's profit margin percentage?",
    "Future Revenue Projection": "What is the projected revenue for next quarter?",
    "Investment Raised": "How much investment did the company raise?",
}

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/generate', methods=['POST'])
def generate_report():
    file = request.files.get('financial_file')
    if not file:
        return "No file uploaded", 400

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    docs = splitter.create_documents([text])
    full_text = " ".join(doc.page_content for doc in docs)

    # Extract answers
    data = {}
    for key, question in queries.items():
        res = extractor(question=question, context=full_text)
        data[key] = f"${res['answer']}" if res['score'] > 0.5 else "N/A"

    # Generate PDF
    filename = f"{os.path.splitext(file.filename)[0]}_report.pdf"
    pdf_path = os.path.join(REPORT_FOLDER, filename)
    c = canvas.Canvas(pdf_path, pagesize=letter)
    y = 750
    c.setFont("Helvetica-Bold", 16)
    c.drawString(180, y, "Financial Report - Q4 2024")
    y -= 40

    c.setFont("Helvetica", 12)
    for k, v in data.items():
        c.drawString(50, y, f"{k}: {v}")
        y -= 25
        if y < 100:
            c.showPage()
            y = 750

    c.save()
    return send_from_directory(REPORT_FOLDER, filename, as_attachment=True)

@app.route('/summarize', methods=['POST'])
def summarize_report():
    file = request.files.get('financial_file')
    if not file:
        return "No file uploaded", 400

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()

    if len(text.split()) > 1024:
        text = " ".join(text.split()[:1024])

    summary = summarizer(text, max_length=200, min_length=60, do_sample=False)[0]['summary_text']

    filename = f"{os.path.splitext(file.filename)[0]}_summary.txt"
    summary_path = os.path.join(REPORT_FOLDER, filename)
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write("Financial Summary - Q4 2024\n\n" + summary)

    return send_from_directory(REPORT_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
