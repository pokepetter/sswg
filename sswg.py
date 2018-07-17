import sys
from os import path
from glob import glob
from pathlib import Path

target_dir = sys.argv[0]
if len(sys.argv) > 1:
    target_dir = sys.argv[1]

# for arg in sys.argv:
#     print('arg:', arg)
# print('TARGET DIR:', target_dir)

images = glob('*.jpg')

css = ''
css = '<left>\n<body>'
css += '<html style="max-width: 800px; margin: auto;">'
css += '<font color="#333333" face=""Century Gothic", CenturyGothic, AppleGothic, sans-serif" size="10em">\n'
#
# #images
# for img in images:
#     print('img:', path.splitext(img)[0])
#     html_string += '''<img src="''' + img + '''" width=75%> <br>\n'''

# print(html_string)

txt = glob('*.txt')[0]
css += '<title>' + txt.split('.')[0] + '</title>\n\n'

with open(txt, 'r', encoding='utf-8') as t:
    text = t.read()


text = text.replace('title:', '<h1 size="10em"><center> ', 1)
text = text.replace('text:', '<font color="#222222" size="5em">')

text = text.replace('\n', '<br>\n')
text = text.replace('  ', '&nbsp;&nbsp;')

# delete commented lines
new_text = ''
tags = list()

for line in text.split('\n'):
    if line.startswith('#'):
        print('parse tag')
        tag = line[1:]
        if tag[0] == ' ':
            tag = tag[1:]

        # tag = line.split(' ')[1]
        # if tag.startswith('#'):
        #     tag = tag[1:]
        # else:
        #     tag = line.split(' ')[1]
        print('TAG:', tag)
    else:
        new_text += line + '\n'

text = new_text

html_string = css + text
# print(html_string)

with open("index.html", "w", encoding='utf-8') as text_file:
    text_file.write(html_string)
