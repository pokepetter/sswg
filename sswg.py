import sys
from os import path
from glob import glob
from pathlib import Path
import textwrap


images = glob('*.jpg')

css = ''
css += '''
<style>
    html {
        max-width: 100%;
        margin: auto;
        color: #333333;
    }
    a.button {
        padding: 15px 32px;
        background-color: #4CAF50;
        border-radius: 8px;
        border-width: 0px;
        text-decoration: none;
        color: white;
        font-size: 25.0px;
    }
</style>
'''

css += '<html>'
css += '\n<left>\n'
css += '<meta name="viewport" content="width=device-width, initial-scale=1.0">'

if len(glob('*.txt')) == 0:
    print('no text file found')
    sys.exit('no text file found')

txt = glob('*.txt')[0]
css += '<title>' + txt.split('.')[0] + '</title>\n<br>\n\n'

with open(txt, 'r', encoding='utf-8') as t:
    text = t.read()


# parse tags and ignore commented lines
new_text = ''
current_alignment = 'left'
current_scale = 5
current_font_weight = 'normal'
current_font_style = 'normal'
code_div_indent = 0
inline_images = list()
stop = False

lines = text.split('\n')
for i, line in enumerate(lines):
    if stop:
        break

    if textwrap.dedent(line).startswith('#'):
        line = textwrap.dedent(line)[1:]
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
                    if image_name.endswith(ft):
                        new_text += '''<img src="''' + image_name + '''"     width=100%> <br>\n'''
                        inline_images.append(image_name)

            if tag.startswith('background'):
                new_text += '<div style="background-color:' + tag.split(' ')[1] + ';">'

            if tag.startswith('code'):
                new_text += textwrap.dedent('''<div style="
                    background-color: whitesmoke;
                    padding: 10px;
                    margin: 0;
                    margin-left: 60px;
                    font-family: monospace;
                    font-size: 20;
                    font-weight: normal;
                    white-space: pre;">''')

                code_div_indent = (len(lines[i]) - len(lines[i].lstrip())) // 4
                continue

            if tag == 'stop':
                stop = True
                break

            new_text += '\n'

    else:
        if code_div_indent:
            current_indent = (len(lines[i]) - len(lines[i].lstrip())) // 4

            if (current_indent < code_div_indent and current_indent > 0
            or textwrap.dedent(lines[i+1]).startswith('#') or len(lines[i+1] + lines[i+2] + lines[i+2]) == 0):
                # print('end code block')
                new_text += line[code_div_indent*4:]
                new_text += '</div>\n'
                code_div_indent = 0
                continue

            new_text += line[code_div_indent*4:] + '\n'
            continue

        else:
            indent = (len(lines[i]) - len(lines[i].lstrip())) // 4
            new_text += f'<div style="margin-left:{indent}em; white-space: pre-wrap;">' + textwrap.dedent(line) + '\n</div>\n'
            # new_text += line.replace('  ', '&nbsp;&nbsp;') + '<br>\n'

text = new_text
# text = text.replace('  ', '&nbsp;&nbsp;')

# buttons
def get_tags(string, start_tag, end_tag):
    tags = list()

    for s in string.split(start_tag)[1:]:
        t = s.split(end_tag, 1)[0]
        if ',' in t:
            tags.append(t)
            print('button:', s.split(end_tag, 1)[0])
    return tags


buttons = get_tags(text, '[', ']')
for b in buttons:
    text = text.replace(b, f'''<a href="{b.split(',')[1]}" class="button">{b.split(',')[0]}''')


text = text.replace('[', '')
text = text.replace(']', '</a>')

#images
if not stop:
    for img in images:
        if img in inline_images:
            continue
        text += '''<img src="''' + img + '''" width=100%> <br>\n'''
        text += '<br><br>'



html_string = css + text
# print(html_string)

with open("index.html", "w", encoding='utf-8') as text_file:
    text_file.write(html_string)
    print("finished building html")
