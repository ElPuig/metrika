import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import plotly.io as pio
import pandas as pd
from utils.constants import MarkConfig
from reportlab.platypus.flowables import KeepTogether
import openai
from collections import defaultdict

def wrap_text(text, width):
    """Wrap text to fit within a given width"""
    words = text.split()
    lines = []
    current_line = []
    
    for word in words:
        # Si la palabra es muy larga, dividirla
        if len(word) > width:
            if current_line:
                lines.append(' '.join(current_line))
                current_line = []
            # Dividir la palabra larga
            for i in range(0, len(word), width):
                lines.append(word[i:i+width])
        else:
            # Probar si la palabra cabe en la línea actual
            test_line = ' '.join(current_line + [word])
            if len(test_line) <= width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
    
    if current_line:
        lines.append(' '.join(current_line))
    
    return '\n'.join(lines)

def generate_student_review(student_name, comments_data):
    """Generate an AI-powered review of a student based on their comments"""
    try:
        # Agrupar comentarios por asignatura
        subject_comments = defaultdict(list)
        for comment in comments_data:
            if comment['Alumne'] == student_name:
                subject_comments[comment['Qualificació']].append(comment['Comentari'])
        
        # Preparar el prompt para el modelo
        prompt = f"Analiza los siguientes comentarios del alumno {student_name} y genera un resumen conciso en catalán que incluya:\n"
        prompt += "1. Puntos fuertes\n2. Áreas de mejora\n3. Recomendaciones específicas\n\n"
        prompt += "Comentarios por calificación:\n"
        
        for qual, comments in subject_comments.items():
            prompt += f"\n{qual}:\n"
            for comment in comments:
                prompt += f"- {comment}\n"
        
        # Llamar a la API de OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un profesor experimentado que analiza comentarios de alumnos para generar resúmenes útiles y constructivos."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"No s'ha pogut generar la revisió automàtica: {str(e)}"

def create_pdf_report(students, output_path="informe.pdf"):
    """Create a PDF report with student statistics and visualizations"""
    # Create the PDF document
    doc = SimpleDocTemplate(
        output_path,
        pagesize=landscape(letter),
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    # Container for PDF elements
    elements = []
    styles = getSampleStyleSheet()
    
    # Create custom styles for tables and reviews
    table_style = ParagraphStyle(
        'TableStyle',
        parent=styles['Normal'],
        fontSize=9,
        leading=11,
        spaceBefore=0,
        spaceAfter=0
    )
    
    review_style = ParagraphStyle(
        'ReviewStyle',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        spaceBefore=12,
        spaceAfter=12,
        leftIndent=20,
        rightIndent=20
    )
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30
    )
    elements.append(Paragraph("Informe de Qualificacions", title_style))
    elements.append(Spacer(1, 20))
    
    # Add group statistics
    elements.append(Paragraph("Estadístiques del Grup", styles['Heading2']))
    elements.append(Spacer(1, 12))
    
    # Add group statistics pie chart
    fig = create_group_statistics_chart(students)
    img_data = pio.to_image(fig, format='png')
    img = Image(io.BytesIO(img_data), width=6*inch, height=4*inch)
    elements.append(img)
    elements.append(Spacer(1, 20))
    
    # Add failure table
    failure_data = create_failure_table(students)
    elements.append(Paragraph("Resum de Suspensos per Alumne", styles['Heading2']))
    elements.append(Spacer(1, 12))
    
    # Create table from failure data with wrapped text
    table_data = [['Categoria', 'Nº d\'alumnes', '%', 'Alumnes']]
    for row in failure_data:
        wrapped_students = wrap_text(row['Alumnes'], 40)
        table_data.append([
            Paragraph(row['Categoria'], table_style),
            Paragraph(str(row['Nº d\'alumnes']), table_style),
            Paragraph(row['%'], table_style),
            Paragraph(wrapped_students, table_style)
        ])
    
    # Ajustar anchos de columna
    col_widths = [1.5*inch, 1*inch, 0.8*inch, 4.2*inch]
    table = Table(table_data, colWidths=col_widths, repeatRows=1)
    
    # Estilo de tabla mejorado
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 20))
    
    # Add subject statistics
    elements.append(PageBreak())
    elements.append(Paragraph("Estadístiques per Assignatura", styles['Heading2']))
    elements.append(Spacer(1, 12))
    
    # Get all subjects
    all_subjects = set()
    for student in students:
        for materia in student['materies']:
            if '3r' in materia['materia']:
                all_subjects.add(materia['materia'])
    
    if not all_subjects:
        elements.append(Paragraph("No s'han trobat assignatures de 3r", styles['Heading3']))
        doc.build(elements)
        return
    
    # Add statistics for each subject
    for subject in sorted(all_subjects):        
        # Add subject title
        elements.append(Paragraph(f"Estadístiques de {subject}", styles['Heading2']))
        elements.append(Spacer(1, 12))
        
        # Create subject statistics chart
        fig = create_subject_statistics_chart(students, subject)
        img_data = pio.to_image(fig, format='png')
        img = Image(io.BytesIO(img_data), width=6*inch, height=4*inch)
        elements.append(img)
        elements.append(Spacer(1, 12))
        
        # Add comments table
        comments_data = get_subject_comments(students, subject)
        if comments_data:
            elements.append(Paragraph("Comentaris per Alumne", styles['Heading3']))
            elements.append(Spacer(1, 12))
            
            table_data = [['Alumne', 'Qualificació', 'Comentari']]
            for row in comments_data:
                wrapped_comment = wrap_text(row['Comentari'], 50)
                table_data.append([
                    Paragraph(row['Alumne'], table_style),
                    Paragraph(row['Qualificació'], table_style),
                    Paragraph(wrapped_comment, table_style)
                ])
            
            # Ajustar anchos de columna
            col_widths = [2*inch, 1.5*inch, 4.5*inch]
            table = Table(table_data, colWidths=col_widths, repeatRows=1)
            
            # Estilo de tabla mejorado
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            
            elements.append(table)
            
            # Add AI-generated review for each student
            elements.append(Spacer(1, 20))
            elements.append(Paragraph("Anàlisi Individual per Alumne", styles['Heading3']))
            elements.append(Spacer(1, 12))
            
            # Get unique students
            unique_students = sorted(set(row['Alumne'] for row in comments_data))
            
            for student in unique_students:
                elements.append(Paragraph(f"Revisió de {student}", styles['Heading4']))
                review = generate_student_review(student, comments_data)
                elements.append(Paragraph(review, review_style))
                elements.append(Spacer(1, 12))
        
        # Add page break before each subject
        elements.append(PageBreak())
    
    # Build the PDF
    doc.build(elements)

def create_group_statistics_chart(students):
    """Create a pie chart for group statistics"""
    import plotly.graph_objects as go
    
    # Count marks
    mark_counts = {
        MarkConfig.NA.value: 0,
        MarkConfig.AS.value: 0,
        MarkConfig.AN.value: 0,
        MarkConfig.AE.value: 0
    }
    
    for student in students:
        for materia in student['materies']:
            qualificacio = materia['qualificacio']
            if qualificacio in mark_counts:
                mark_counts[qualificacio] += 1
    
    # Filter out marks with zero count
    filtered_counts = {k: v for k, v in mark_counts.items() if v > 0}
    
    # Create pie chart
    fig = go.Figure(data=[go.Pie(
        labels=list(filtered_counts.keys()),
        values=list(filtered_counts.values()),
        hole=.3,
        textinfo='label+percent+value',
        insidetextorientation='radial',
        marker_colors=[MarkConfig.COLOR_MAP.value[mark] for mark in filtered_counts.keys()]
    )])
    
    fig.update_layout(
        showlegend=False,
        height=500,
        margin=dict(t=50, b=50, l=50, r=50)
    )
    
    return fig

def create_failure_table(students):
    """Create failure statistics table data"""
    categories = {
        "Tot aprovat": [],
        "Fins a 3 susp.": [],
        "4 o 5 susp.": [],
        "Més de 5 susp.": []
    }
    
    for student in students:
        n_susp = sum(1 for m in student['materies'] if m['qualificacio'] == MarkConfig.NA.value)
        name = student['nom_cognoms']
        if n_susp == 0:
            categories["Tot aprovat"].append(name)
        elif 1 <= n_susp <= 3:
            categories["Fins a 3 susp."].append(name)
        elif 4 <= n_susp <= 5:
            categories["4 o 5 susp."].append(name)
        else:
            categories["Més de 5 susp."].append(name)
    
    total = len(students)
    data = []
    for cat, names in categories.items():
        data.append({
            "Categoria": cat,
            "Nº d'alumnes": len(names),
            "%": f"{(len(names)/total*100):.1f}%",
            "Alumnes": '; '.join(names)
        })
    
    return data

def create_subject_statistics_chart(students, subject):
    """Create a pie chart for subject statistics"""
    import plotly.graph_objects as go
    
    # Count marks for the selected subject
    mark_counts = {
        MarkConfig.NA.value: 0,
        MarkConfig.AS.value: 0,
        MarkConfig.AN.value: 0,
        MarkConfig.AE.value: 0
    }
    
    for student in students:
        for materia in student['materies']:
            if materia['materia'] == subject:
                mark = materia['qualificacio']
                if mark in mark_counts:
                    mark_counts[mark] += 1
    
    # Filter out marks with zero count
    filtered_counts = {k: v for k, v in mark_counts.items() if v > 0}
    
    # Create pie chart
    fig = go.Figure(data=[go.Pie(
        labels=list(filtered_counts.keys()),
        values=list(filtered_counts.values()),
        hole=.3,
        textinfo='label+percent+value',
        insidetextorientation='radial',
        marker_colors=[MarkConfig.COLOR_MAP.value[mark] for mark in filtered_counts.keys()]
    )])
    
    fig.update_layout(
        showlegend=False,
        height=500,
        margin=dict(t=50, b=50, l=50, r=50)
    )
    
    return fig

def get_subject_comments(students, subject):
    """Get comments data for a specific subject"""
    comments_data = []
    
    for student in students:
        for materia in student['materies']:
            if materia['materia'] == subject:
                comments_data.append({
                    'Alumne': student['nom_cognoms'],
                    'Qualificació': materia['qualificacio'],
                    'Comentari': materia['comentari']
                })
    
    return sorted(comments_data, key=lambda x: x['Alumne']) 