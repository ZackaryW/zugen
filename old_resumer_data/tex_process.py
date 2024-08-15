import os

os.rename("pandoc.out", "resume.tex")
os.system("xelatex resume.tex")
print('{"capture": ["resume.pdf"]}')