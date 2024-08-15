import os

os.rename("pandoc.out", "resume.txt")
print('{"capture": ["resume.txt"]}')

