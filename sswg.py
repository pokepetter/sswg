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
css = '<center>\n<body>'
# css += '<html style="max-width: 50em; margin: auto;">'
# css += '<div max-width="500px">'
# css += '<body style="padding-left: 20%;>'
css += '<font color="#333333" face=""Century Gothic", CenturyGothic, AppleGothic, sans-serif" size="10em">\n'
# css += '<br style="display: block; content: ""; margin-top: 0;" />'
# css += '<br style="line-height:12px">'
# css += '<body style="line-height:1em">'
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
# text = text.replace('heading:', '<font color="#222222" size="5em"><center>')
text = text.replace('text:', '<font color="#222222" size="5em">')
# text = text.replace('text:', '<font color="#222222" size="5em"><left>')

text = text.replace('\n', '<br>\n')
text = text.replace('  ', '&nbsp;&nbsp;')

# delete commented lines
new_text = ''
for line in text.split('\n'):
    if not line.startswith('#'):
        new_text += line
        if line.startswith('<h3'):
            new_text += '--------------------------------------</h3>'
        if line.startswith('<h1'):
            new_text += '</h1>'
        # if line.startswith('<p'):
        #     new_text += '</p>'
        new_text += '\n'

text = new_text

html_string = css + text
print(html_string)

with open("index.html", "w", encoding='utf-8') as text_file:
    text_file.write(html_string)
