import sys
from os import path
import re
from pathlib import Path
from textwrap import dedent


def get_html_tags(string, start_tag='>', end_tag='>'):
    tags = list()
    for s in string.split(start_tag):
        tags.append(s.split(end_tag, 1)[0])

    return tags


def get_tags(string, start_tag, end_tag, include_tags=False):
    tags = list()

    for ss in string.split(start_tag)[1:]:
        content = ss.split(end_tag)[0]
        if include_tags:
            content = start_tag + content + end_tag
        tags.append(content)

    return tags


# --------------------------------------------------------------------
path = Path('.')

if len(list(path.glob('*.txt'))) == 0:
    print('no text file found')
    sys.exit('no text file found')

for txt in path.glob('*.txt'):
    # print(txt.stem)
    with open(txt, 'r', encoding='utf-8') as t:
        text = t.read()

    new_text = ''
    new_text += dedent('''
        <!--generated with sswg-->
        <style>
            html {max-width: 100%; margin: auto; color: #333333;}
            a.button {padding: 15px 32px; background-color: #555; border-radius: 2em; border-width: 0px; text-decoration: none; color: white; font-size: 25.0px; line-height: 2.5em;}
            a.button:hover {background-color: #777}
            mark {background: #ccff99;}
            img {max-width: 100%;}
    ''')
    if text.startswith('# style'):
        new_text += text.split('\n')[0].split('# style ')[1]

    new_text += dedent('''
        </style>
        <html>
        <left>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    ''')

    if '# title' in text:
        title = text.split('# title')[1].split('\n',1)[0]
    else:
        title = txt.stem

    new_text += '<title>' + title + '</title>\n<br>\n\n'

    # parse tags and ignore commented lines
    current_alignment = 'left'
    current_scale = 5
    current_font_weight = 'normal'
    current_font_style = 'normal'
    is_code_block = False
    inline_images = list()


    lines = text.split('\n')
    for i, line in enumerate(lines):
        # print(line)
        original_line = line
        if line.strip().startswith('#'):
            indent = len(line) - len(line.lstrip())
            line = line.strip()[1:].strip()
            tags = [tag.strip() for tag in line.split(',')]

            style = ''
            for tag in tags:
                if tag.startswith('width'):
                    tag = tag.split(' ')[1]
                    style += f'max-width: {tag}px; margin: auto;'

                elif tag in ('left', 'right', 'center'):
                    # print('tag', tag)
                    if tag != current_alignment:
                        style += 'text-align: ' + tag + ';'
                        current_alignment = tag

                elif tag.startswith('scale') or tag.startswith('size'):
                    new_scale = tag.split(' ')[1]
                    # print('tag', new_scale)
                    if tag != new_scale:
                        style += 'font-size: ' + str(float(new_scale)*20) + 'px;'
                        current_scale = new_scale

                elif tag in ('normal', 'bold', 'bolder', 'lighter'):
                    if tag != current_font_weight:
                        style += 'font-weight: ' + tag + ';'
                        current_font_weight = tag

                elif (tag.lower() in
                    ('arial', 'times', 'helvetica', 'courier', 'courier new', 'verdana', 'tahoma', 'bookman', 'monospace')):
                    style += f'font-family: {tag.lower()};'


                elif tag.startswith('image'):
                    image_name = tag[len(tag.split(' ')[0]):].strip()
                    print('.............', image_name)
                    for ft in ('.jpg', '.png', '.gif'):
                        if image_name.endswith(ft):
                            new_text += f'<img src="{image_name}"></img> <br>\n'
                            inline_images.append(image_name)

                elif tag.startswith('background'):
                    style += 'background-color: ' + tag.split(' ')[1] + ';'

                elif tag.startswith('code'):
                    is_code_block = True
                    style += dedent(f'''
                        background-color: whitesmoke;
                        padding: 10px;
                        margin: 0;
                        margin-left: {indent//4}em;
                        font-family: monospace;
                        font-size: 20;
                        font-weight: normal;
                        white-space: pre;''').replace('\n', ' ')

                elif tag.startswith('text'):  # end code block
                    new_text += '</div>'
                    is_code_block = False

            if style:
                new_text += '<div style="' + style + '">'

                if not is_code_block:
                    new_text += '\n'

            elif is_code_block: # keep comments in code blocks
                new_text += '<font color="gray">' + original_line.lstrip() + '</font>' + '\n'

        else:
            if is_code_block:
                # purple olive green
                line = line[indent:]
                line = line.replace('def ', '<font color="purple">def</font> ')
                line = line.replace('from ', '<font color="purple">from</font> ')
                line = line.replace('import ', '<font color="purple">import</font> ')
                line = line.replace('Entity', '<font color="olive">Entity</font>')

                quotes = re.findall('\'(.*?)\'', line)
                quotes = ['\'' + q + '\'' for q in quotes]
                for q in quotes:
                    line = line.replace(q, '<font color="green">' + q + '</font>')

                if original_line.endswith('# +'): # highlight line in code block
                    line = '<mark> ' + line.replace('# +', '</mark>')
                elif line.endswith('# -'): # highlight line in code block
                    line = '<mark style="background:#ff9999;"> ' + line.replace('# -', '</mark>')

                elif '#' in line:
                    comment = line.split('#')[1]
                    comment = re.sub(re.compile('<.*?>'), '', comment)
                    line = line.split('#')[0] + '<font color="gray">#' + comment + '</font>'


            else:
                buttons = get_tags(line, '[', ']')
                for b in buttons:
                    if not ',' in b:
                        print(line)
                        continue

                    print('button:', b)
                    line = line.replace(b, f'''<a href="{b.split(',')[1]}" class="button">{b.split(',')[0]}</a>''')
                    line = line.replace('[', '')
                    line = line.replace(']', '')

                line = line.replace('  ', '&nbsp;&nbsp;')


            if 'http' in line and not 'class="button"' in line:  # find urls and convert them to links
                words = line.split(' ')
                words = [f'<a href="{w}">{w}</a>' if w.startswith('http') else w for w in words]
                line = ' '.join(words)


            new_text += line + '<br>'
            if not is_code_block:
                new_text += '\n'


    new_text += '\n</html>'


    with open(txt.stem + '.html', 'w', encoding='utf-8') as text_file:
        text_file.write(new_text)
        print('finished building:', txt.stem + '.html')
