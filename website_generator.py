from os import path
from glob import glob
from pathlib import Path

images = glob('*.jpg')

html_string = '<center>\n'

# title
title = path.basename(path.dirname(path.realpath(__file__))).replace('_', ' ').title()
print('Title:', title)
html_string += '<title>' + title + '</title>'
html_string += '<font color="#333333" face=""Century Gothic", CenturyGothic, AppleGothic, sans-serif" size="10em">'
html_string += '<br>'
html_string += '<h3>' + title + '</h3><br>\n'

# text
html_string += '<font color="#222222" size="5em">'
text_files = glob('*.txt')
for txt in text_files:
    html_string += Path(txt).read_text().replace('\n', '<br>\n')
html_string += '<br><br><br>'

#images
for img in images:
    html_string += '''<img src="''' + img + '''" width=75%> <br>\n'''

print(html_string)

with open("index.html", "w") as text_file:
    text_file.write(html_string)
