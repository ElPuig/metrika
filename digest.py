from utils import trim_csv, extract_table, html_to_table

# trim_csv("docs/3b_t1_acta-avaluació.csv", "docs/3b_t1_acta-avaluació-DIGEST.csv")
# extract_table(pdf_file="docs/ActaAvaluacioGraella_ESO LOE (Modificada)_3_ESO 3B_2_437038.pdf", save_file=True)
html_to_table(html_file=r"C:\Users\elpel\root\edu\tutoria\statistics\docs\ActaAvaluacioGraella_ESO LOE (Modificada)_3_ESO 3B_2_437038\input-html.html")