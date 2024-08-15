import os
from zugen.utils import ensure_file

ensure_file("@/old_resumer_data/awesome-cv.cls")
os.rename("pandoc.out", "resume.tex")
os.system("xelatex -interaction=nonstopmode resume.tex")
capture("resume.pdf")