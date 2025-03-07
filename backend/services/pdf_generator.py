from fpdf import FPDF
import datetime
import os

class PDFReport(FPDF):
    def header(self):
        self.set_font("Arial", "B", 16)
        self.cell(200, 10, "StockSight Competitor Report", ln=True, align="C")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Generated on {datetime.datetime.now().strftime('%Y-%m-%d')}", align="C")

    def add_chart(self, title, image_path):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, title, ln=True, align="L")
        self.ln(5)
        self.image(image_path, w=180)
        self.ln(10)

def generate_pdf_report(selected_charts):
    """Creates a PDF report with selected charts"""
    pdf = PDFReport()
    pdf.add_page()

    for chart in selected_charts:
        pdf.add_chart(chart["title"], chart["image_path"])

    os.makedirs("reports", exist_ok=True)
    pdf_path = f"reports/StockSight_Report_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    pdf.output(pdf_path)
    
    return pdf_path