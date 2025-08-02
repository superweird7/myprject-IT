# utils.py
import csv
from reportlab.lib.pagesizes import landscape, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
import arabic_reshaper
from bidi.algorithm import get_display

def export_to_csv(data, filename="exported_data.csv"):
    with open(filename, "w", newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerows(data)

def export_to_pdf(data, filename="exported_data.pdf", title="تقرير بيانات الصيانة"):
    """
    Exports data to a PDF file with correct Arabic rendering and column sizing.
    """
    try:
        # --- Font Handling for Arabic ---
        font_path = "c:/windows/fonts/arial.ttf"
        if os.path.exists(font_path):
            pdfmetrics.registerFont(TTFont('ArabicFont', font_path))
            font_name = 'ArabicFont'
        else:
            print(f"Warning: Font file not found at {font_path}. Using default font.")
            font_name = 'Helvetica'

        # --- Create PDF Document (using landscape for more space) ---
        doc = SimpleDocTemplate(filename, pagesize=landscape(A4))
        elements = []

        # --- Styles ---
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(name='Title', parent=styles['Heading1'], fontName=font_name, alignment=2)
        cell_style = ParagraphStyle(name='Cell', parent=styles['Normal'], fontName=font_name, alignment=2)
        header_style = ParagraphStyle(name='Header', parent=cell_style, textColor=colors.whitesmoke)

        # --- Title ---
        shaped_title = get_display(arabic_reshaper.reshape(title))
        title_para = Paragraph(shaped_title, title_style)
        elements.append(title_para)
        elements.append(Spacer(1, 12))

        # --- Prepare Table Data with Arabic Shaping and Paragraph Wrapping ---
        if not data or len(data) == 0:
            table_data = [["لا توجد بيانات للعرض"]]
        else:
            headers = [Paragraph(get_display(arabic_reshaper.reshape(str(cell))), header_style) for cell in data[0]]
            body_rows = [[Paragraph(get_display(arabic_reshaper.reshape(str(cell))), cell_style) for cell in row] for row in data[1:]]
            table_data = [headers] + body_rows

        # --- Calculate Column Widths (to fit landscape A4 page) ---
        page_width = doc.width
        proportions = [0.04, 0.09, 0.10, 0.10, 0.10, 0.20, 0.12, 0.10, 0.10, 0.05]
        col_widths = [page_width * p for p in proportions]
        
        # --- Create and Style Table ---
        table = Table(table_data, colWidths=col_widths)
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, -1), font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ])
        table.setStyle(style)
        elements.append(table)

        # --- Build PDF ---
        doc.build(elements)

    except Exception as e:
        print(f"Error exporting to PDF: {e}")
        raise