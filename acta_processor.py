import csv
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm

nom_fitxer = 'ActaAvaluacioGraella_ESO LOE (Modificada)_1_ESO 1A_2_436963.csv'


# Funció per afegir un paràgraf amb word wrap i retorn de l'alçada utilitzada
def afegeix_paragraf(c, text, x, y, amplada):
    styles = getSampleStyleSheet()
    style = styles["Normal"]
    par = Paragraph(text, style)
    w, h = par.wrap(amplada, 1000)

    if y - h < 50:
        c.showPage()
        y = A4[1] - 50
        c.setFont("Helvetica", 12)

    # Final wrap i draw sempre després del showPage (si s'ha fet)
    par = Paragraph(text, style)
    w, h = par.wrap(amplada, 1000)
    par.drawOn(c, x, y - h)
    y -= h
    return h, y  # retorna l'alçada i nova posició y


def genera_pdf(alumne):
    nom_arxiu = f"{alumne['nom_cognoms']}_{alumne['id']}.pdf"
    canv = canvas.Canvas(nom_arxiu, pagesize=A4)

    amplada, alcada = A4
    y = alcada - 50  # Punt de partida des de daltdra

    canv.setFont("Helvetica-Bold", 16)
    text = f"Informe d'avaluació de {alumne['nom_cognoms']}"
    height, y = afegeix_paragraf(canv, text, 50, y, amplada - 100)

    y -= 40
    canv.setFont("Helvetica", 12)

    # Itera per les assignatures dinàmiques c1, c2, ..., c100
    for i in range(1, 101):
        m = f'm{i}'
        q = f'q{i}'
        c = f'c{i}'
        materia = alumne.get(m, '')

        if materia == '':
            break

        qualificacio = alumne.get(q, 'Pendent de qualificar')
        if qualificacio == '':
            qualificacio = 'Pendent de qualificar'
        comentari = alumne.get(c, 'Sense comentari')
        if comentari == '':
            comentari = 'Sense comentari'
        text = f"{materia}: {qualificacio} - Comentari: {comentari}"
        height, y = afegeix_paragraf(canv, text, 50, y, amplada - 100)
        y -= 10

    # Comentari final
    y -= 20
    canv.setFont("Helvetica-Oblique", 11)
    comentari_general = alumne.get('comentari general', 'Sense comentari')
    if comentari_general == '':
        comentari_general = 'Sense comentari'
    text = f"Comentari del tutor/a: {comentari_general}"
    height, y = afegeix_paragraf(canv, text, 50, y, amplada - 100)

    canv.save()
    print(f"PDF generat: {nom_arxiu}")


# Llegeix i genera PDFs
try:
    with open(nom_fitxer, newline='', encoding='utf-8') as csvfile:
        lector = csv.DictReader(csvfile, delimiter='|')
        for alumne in lector:
            # Hay que usar como claves los nombres de la cabecera del csv
            print(f"{alumne[nom_cognoms]} {alumne[id]}")
            genera_pdf(alumne)

except FileNotFoundError:
    print(f"El fitxer '{nom_fitxer}' no s'ha trobat.")
except Exception as e:
    print(f"S'ha produït un error: {e}")