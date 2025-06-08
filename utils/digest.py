import os
from helpers import pdf_to_table

#for i in [1,2]:
#    pdf_to_table(pdf_file=rf"C:\Users\elpel\root\edu\tutoria\statistics\docs\ActaAvaluacioGraella_ESO LOE (Modificada)_3_ESO 3B_T{i}.pdf", digest=True)

# loop over all files in the folder
fn = os.path.join(os.path.dirname(__file__), 'docs')
for file in os.listdir(fn):
    if file.endswith(".pdf"):
        pdf_to_table(pdf_file=rf"{fn}\{file}", digest=True)

