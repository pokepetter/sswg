import sys
from os import path
from glob import glob
from pathlib import Path


images = glob('*.jpg')

css = ''
css += '''<html style="
    max-width: 100%;
    margin: auto;
    color: #333333;
    ">'''
css += '\n<left>\n'
css += '<meta name="viewport" content="width=device-width, initial-scale=1.0">'
# css += '<pre>'


if len(glob('*.txt')) == 0:
    print('no text file found')
    sys.exit('no text file found')

txt = glob('*.txt')[0]
css += '<title>' + txt.split('.')[0] + '</title>\n\n'

with open(txt, 'r', encoding='utf-8') as t:
    text = t.read()


# parse tags and ignore commented lines
new_text = ''
current_alignment = 'left'
current_scale = 5
current_font_weight = 'normal'
current_font_style = 'normal'
inline_images = list()
stop = False

for line in text.split('\n'):
    if stop:
        break

    if line.startswith('#'):
        line = line[1:]
        tags = [tag.strip() for tag in line.split(',')]

        for tag in tags:
            if tag.startswith('width'):
                new_text += '<div style="max-width: ' + tag.split(' ')[1] + 'px; margin: auto;">'

            if tag in ('left', 'right', 'center'):
                print('tag', tag)
                if tag != current_alignment:
                    new_text += '<div align="' + tag + '">'
                    current_alignment = tag

            if tag.startswith('scale') or tag.startswith('size'):
                new_scale = tag.split(' ')[1]
                print('tag', new_scale)
                if tag != new_scale:
                    new_text += '<div style="font-size: ' + str(float(new_scale)*20) + 'px">'
                    current_scale = new_scale

            if tag in ('normal', 'bold', 'bolder', 'lighter'):
                if tag != current_font_weight:
                    new_text += '<div style="font-weight: ' + tag + '">'
                    current_font_weight = tag

            if (tag.lower() in
                ('arial', 'times', 'helvetica', 'courier', 'courier new', 'verdana', 'tahoma', 'bookman', 'monospace')):
                new_text += '<div style="font-family: ' + tag.lower() + '">'


            if tag.startswith('image'): 
                image_name = tag[len(tag.split(' ')[0]):].strip()
                print('.............', image_name)
                for ft in ('.jpg', '.png', '.gif'):
                    full_name = image_name + ft
                    if path.isfile(path.join(path.dirname(path.realpath(__file__)), full_name)):
                        new_text += '''<img src="''' + full_name + '''"     width=100%> <br>\n'''
                        inline_images.append(full_name)

            if tag == 'stop':
                stop = True
                break

            new_text += '\n'

    else:
        new_text += line + '<br>\n'
text = new_text
text = text.replace('  ', '&nbsp;&nbsp;')

#images
if not stop:
    for img in images:
        if img in inline_images:
            continue
        text += '''<img src="''' + img + '''" width=100%> <br>\n'''
        text += '<br><br>'



html_string = css + text
print(html_string)

with open("index.html", "w", encoding='utf-8') as text_file:
    text_file.write(html_string)
    print("finished building html")
