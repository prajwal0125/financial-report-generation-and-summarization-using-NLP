import re
import openai
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from transformers import pipeline

# Load financial data from the text file
file_path = "financial_data.txt"
with open(file_path, "r") as file:
    financial_text = file.read()

# AI Model: Use HuggingFace Financial NLP Model for Key Figures Extraction
extractor = pipeline("question-answering", model="deepset/roberta-base-squad2")

# Define queries for AI extraction
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

# Extract financial data using AI
extracted_data = {}
for key, query in queries.items():
    response = extractor(question=query, context=financial_text)
    extracted_data[key] = f"${response['answer']}" if response['score'] > 0.5 else "N/A"

# Generate PDF Report
pdf_file = "Financial_Report_Q4_2024.pdf"

def generate_pdf_report(filename, data):
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    y_position = height - 50  # Start position

    c.setFont("Helvetica-Bold", 16)
    c.drawString(200, y_position, "Financial Report - Q4 2024")
    y_position -= 30  # Move down

    c.setFont("Helvetica", 12)
    for key, value in data.items():
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y_position, key + ": ")  # Heading
        y_position -= 20
        c.setFont("Helvetica", 12)
        c.drawString(80, y_position, value)  # Value
        y_position -= 30  # Move down further

        if y_position < 50:  # Avoid overflowing the page
            c.showPage()
            c.setFont("Helvetica", 12)
            y_position = height - 50

    c.save()

# Generate and save the PDF
generate_pdf_report(pdf_file, extracted_data)

print(f"✅ AI-Powered Financial report successfully saved as {pdf_file}")
