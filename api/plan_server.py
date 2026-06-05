import os
from flask import Flask, request, send_file
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER
import io

app = Flask(__name__)

REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def ajustar_por_condiciones(data):
    hipertension = data.get('hipertension') == 'si'
    diabetes = data.get('diabetes') in ('1', '2', 'insulinodependiente')
    insulinodependiente = data.get('diabetes') == 'insulinodependiente'
    actividad = data.get('actividad')

    reglas = {
        'notas': []
    }
    if hipertension:
        reglas['notas'].append('Plan bajo en sodio y sin enlatados.')
    if diabetes:
        reglas['notas'].append('Plan controlado en azúcares y carbohidratos de absorción rápida.')
    if insulinodependiente:
        reglas['notas'].append('Distribución equilibrada de hidratos para picos de insulina.')
    if not actividad:
        reglas['notas'].append('Rutina moderada: énfasis en saciedad y digestión.')
    return reglas

def generar_pdf(usuario, reglas):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=60, leftMargin=60,
                            topMargin=60, bottomMargin=40)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=22,
                                  textColor=colors.HexColor('#166534'), alignment=TA_CENTER, spaceAfter=10)
    subtitle_style = ParagraphStyle('Sub', parent=styles['Normal'], fontSize=11,
                                     textColor=colors.HexColor('#15803d'), alignment=TA_CENTER, spaceAfter=16)
    day_style = ParagraphStyle('Day', parent=styles['Heading2'], fontSize=13,
                                textColor=colors.white, alignment=TA_CENTER)
    body_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=10, leading=13)

    story = []
    story.append(Paragraph("Plan Semanal — DietaMex 45+", title_style))

    subt = "1500 kcal · 4 a 6 comidas · Bajo en sodio · Comida mexicana"
    if reglas['notas']:
        subt += "<br/>" + " · ".join(reglas['notas'])
    story.append(Paragraph(subt, subtitle_style))
    story.append(Spacer(1, 6))

    meals = [
        ('Lunes', 'Frijoles', [
            ('Desayuno (300 kcal)', 'Huevo revuelto (2) con nopal y tomate · 1 tortilla de maíz'),
            ('Almuerzo (400 kcal)', 'Pollo desmenuzado (120 g) con calabacita · 1 taza de frijoles · 2 tortillas'),
            ('Merienda 1 (200 kcal)', 'Jicama con limón y chile en polvo (sin sal)'),
            ('Merienda 2 (300 kcal)', 'Yogur natural sin azúcar + 8 nueces'),
            ('Cena (300 kcal)', 'Sopa de verduras con pollo deshebrado'),
        ]),
        ('Martes', 'Pescado', [
            ('Desayuno (300 kcal)', 'Licuado de avena con leche light · plátano y canela'),
            ('Almuerzo (400 kcal)', 'Filete de pescado a la plancha · arroz integral · ensalada de jícama'),
            ('Merienda 1 (200 kcal)', 'Tostada de maíz con aguacate (¼) y limón'),
            ('Merienda 2 (300 kcal)', 'Manzana al horno con canela'),
            ('Cena (300 kcal)', 'Caldo de pollo con verduras · 1 tortilla de maíz'),
        ]),
        ('Miércoles', 'Lentejas', [
            ('Desayuno (250 kcal)', 'Té de hierbabuena · 1 pan dulce pequeño'),
            ('Colación media mañana (200 kcal)', 'Gelatina light sin azúcar'),
            ('Almuerzo (350 kcal)', 'Guiso de lentejas con zanahoria y calabacín · 1 naranja'),
            ('Merienda 1 (200 kcal)', 'Pepino con limón y chile'),
            ('Merienda 2 (250 kcal)', 'Palomitas de maíz (sin sal, sin mantequilla)'),
            ('Cena (250 kcal)', 'Crema de chayote con elote · 1 tortilla'),
        ]),
        ('Jueves', 'Res magra', [
            ('Desayuno (300 kcal)', 'Avena cocida con leche light · trozos de pera'),
            ('Almuerzo (400 kcal)', 'Bistec de res magra · ensalada de nopales · 2 tortillas'),
            ('Merienda 1 (200 kcal)', 'Naranja fileteada'),
            ('Merienda 2 (300 kcal)', 'Yogur natural sin azúcar con fresas'),
            ('Cena (300 kcal)', 'Sopa de verduras con pollo y limón'),
        ]),
        ('Viernes', 'Pavo', [
            ('Desayuno (300 kcal)', 'Chilaquiles verdes (2 tortillas, queso panela, sin crema)'),
            ('Almuerzo (400 kcal)', 'Pechuga de pavo · arroz con verduras · ensalada'),
            ('Merienda 1 (200 kcal)', 'Kiwi en rodajas'),
            ('Merienda 2 (300 kcal)', 'Tortilla de maíz con frijoles negros (¼ taza)'),
            ('Cena (300 kcal)', 'Caldo tlalpeño light (pollo y verduras, sin grasa extra)'),
        ]),
        ('Sábado', 'Hidratación', [
            ('Desayuno (250 kcal)', 'Té de limón · 1 huevo cocido'),
            ('Colación media mañana (150 kcal)', 'Gelatina light sin azúcar'),
            ('Almuerzo (350 kcal)', 'Tacos de canasta de pollo (3 uds) con salsa de jitomate (sin crema)'),
            ('Merienda 1 (200 kcal)', 'Zanahoria baby con limón'),
            ('Merienda 2 (300 kcal)', 'Ensalada de elote, jícama y pepino con limón'),
            ('Cena (250 kcal)', 'Crema de flor de calabaza · 1 tortilla'),
        ]),
        ('Domingo', 'Descanso', [
            ('Desayuno (300 kcal)', 'Fruta de temporada (papaya o sandía, 1 taza) · 1 rebanada de pan integral'),
            ('Almuerzo (400 kcal)', 'Sopa de fideo con pollo (poca sal) · ensalada de lechuga'),
            ('Merienda 1 (200 kcal)', 'Pera en rodajas'),
            ('Merienda 2 (300 kcal)', 'Licuado de leche light + avena y canela'),
            ('Cena (300 kcal)', 'Calabacitas rellenas de atún al vapor (sin aceite)'),
        ]),
    ]

    tag_bg = {
        'Frijoles': colors.HexColor('#166534'),
        'Pescado': colors.HexColor('#1e40af'),
        'Lentejas': colors.HexColor('#92400e'),
        'Res magra': colors.HexColor('#6b21a8'),
        'Pavo': colors.HexColor('#991b1b'),
        'Hidratación': colors.HexColor('#115e59'),
        'Descanso': colors.HexColor('#3730a3'),
    }

    for dia, tag, comidas in meals:
        day_data = [[Paragraph(f"{dia} — {tag}", day_style)]]
        day_tbl = Table(day_data, colWidths=[6.6*inch])
        day_tbl.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), tag_bg.get(tag, colors.black)),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(day_tbl)
        story.append(Spacer(1, 4))

        rows = [['Tiempo', 'Receta']]
        for t, r in comidas:
            rows.append([Paragraph(t, body_style), Paragraph(r, body_style)])
        t = Table(rows, colWidths=[2.2*inch, 4.4*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0fdf6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#166534')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('TOPPADDING', (0, 0), (-1, 0), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(t)
        story.append(Spacer(1, 10))

    story.append(Spacer(1, 8))
    story.append(Paragraph("® 2026 DietaMex 45+ — Plan referencial. Consulta a tu médico antes de iniciar.", body_style))
    doc.build(story)
    buffer.seek(0)
    return buffer.read()

@app.route("/")
def index():
    return send_file(os.path.join(REPO_DIR, "landing-dietas.html"))

@app.route("/api/current-plan", methods=["POST"])
def current_plan():
    data = request.form.to_dict() or {}
    reglas = ajustar_por_condiciones(data)
    pdf_bytes = generar_pdf(data, reglas)
    return send_file(io.BytesIO(pdf_bytes), mimetype='application/pdf',
                     as_attachment=True, download_name='plan-semanal-dietamex-45.pdf')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
