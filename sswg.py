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
ignore = '_*'
for arg in sys.argv:
    if arg.startswith('--ignore='):
        ignore = arg.split('=')[1]


if len(list(path.glob('*.txt'))) == 0:
    print('no text file found')
    sys.exit('no text file found')

for txt in path.glob('*.txt'):
    #  skip ignored files
    if ignore.endswith('*'):
        if txt.name.startswith(ignore[:-1]):
            print('skip file:', txt)
            continue
    if txt.name == ignore:
        print('skip file:', txt)
        continue

    # print(txt.stem)
    with open(txt, 'r', encoding='utf-8') as t:
        text = t.read()

    if '# insert ' in text:
        new_lines = []
        lines = text.split('\n')
        for l in lines:
            if l.startswith('# insert') or l.startswith('#insert'):
                path = l.split('insert', 1)[1].strip()
                if path.startswith('Path('):
                    path = eval(path)

                with open(path, 'r', encoding='utf-8') as text_file:
                    new_lines.extend(text_file.read().splitlines())
                continue
            new_lines.append(l)
        text = '\n'.join(new_lines)


    new_text = dedent('''
        <!DOCTYPE HTML>
        <!--generated with sswg-->
    ''')


    new_text += dedent('''
        <html>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <head> <link rel="stylesheet" href="sswg.css"> </head>
        <left>
    ''')
    if text.startswith('# style'):
        new_text += '<style>' + text.split('\n')[0].split('# style ')[1] + '</style>'

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

    # add support for markdown inspired tags
    new_lines = list()
    for l in lines:
        if l.startswith('### '):
            new_lines.extend(['# size 3, bold', f'<div id="{l[4:]}"/>', l[4:], '# size 1, normal'])
            continue

        if l.startswith('## '):
            new_lines.extend(['# size 2, bold', f'<div id="{l[3:]}"/>', l[3:], '# size 1, normal'])
            continue

        #index support
        if l.strip().startswith('# index ') or l.strip().startswith('#index '):
            current_indent = l.split('#')[0]
            # print('aaaaaaaaaaaa')
            tag, target_document = l.split('#')[1].strip().split(' ')
            with open(target_document, 'r', encoding='utf-8') as file:
                headlines = [l.split('## ')[1].strip() for l in file.readlines() if l.strip().startswith('## ')] # get name after ##
                for e in headlines:
                    link = target_document.replace('.txt', '.html') + f'#{e}'
                    new_lines.append(current_indent + f'• <a href="{link}">{e}</a>')

        new_lines.append(l)

    lines = new_lines

    for i, line in enumerate(lines):
        # print(line)
        original_line = line
        is_code_comment = is_code_block and not line.strip() in ('#text', '# text')
        if line.strip().startswith('#') and not is_code_comment:
            indent = len(line) - len(line.lstrip())

            line = line.strip()[1:].strip()
            tags = [tag.strip() for tag in line.split(',')]

            div_class = ''
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
                    style += f'margin-left: {indent//4}em;'
                    div_class = 'code_block'

                elif tag.startswith('text'):  # end code block
                    new_text += '</div>'
                    is_code_block = False


            if style:
                if div_class:
                    div_class = f'class="{div_class}" '

                new_text += f'<div {div_class}style="{style}">'

                if not is_code_block:
                    new_text += '\n'

            elif is_code_block: # keep comments in code blocks
                new_text += '<gray>' + original_line.lstrip() + '</gray>' + '\n'

        else:
            is_image_button = False
            if is_code_block:
                if line.startswith(indent*' '):
                    line = line[indent:]

                line = line.replace('def ', '<purple>def</purple> ')
                line = line.replace('from ', '<purple>from</purple> ')
                line = line.replace('import ', '<purple>import</purple> ')
                line = line.replace('for ', '<purple>for</purple> ')

                line = line.replace('elif ', '<purple>elif</purple> ')
                line = line.replace('if ', '<purple>if</purple> ')
                line = line.replace(' not ', ' <purple>not</purple> ')
                line = line.replace('else:', '<purple>else</purple>:')

                line = line.replace('Entity', '<olive>Entity</olive>')
                for e in ('print', 'range', 'hasattr', 'getattr', 'setattr'):
                    line = line.replace(f'{e}(' , f'<blue>{e}</blue>(')

                # colorize ursina specific params
                for e in ('enabled', 'parent', 'world_parent', 'model', 'highlight_color', 'color',
                    'texture_scale', 'texture', 'visible',
                    'position', 'z', 'y', 'z',
                    'rotation', 'rotation_x', 'rotation_y', 'rotation_z',
                    'scale', 'scale_x', 'scale_y', 'scale_z',
                    'origin', 'origin_x', 'origin_y', 'origin_z',
                    'text', 'on_click', 'icon', 'collider', 'shader', 'curve', 'ignore',
                    'vertices', 'triangles', 'uvs', 'normals', 'colors', 'mode', 'thickness'
                    ):
                    line = line.replace(f'{e}=' , f'<olive>{e}</olive>=')


                # colorize numbers
                for i in range(10):
                    line = line.replace(f'{i}', f'<yellow>{i}</yellow>')

                # destyle Vec2 and Vec3
                line = line.replace(f'<yellow>3</yellow>(', '3(')
                line = line.replace(f'<yellow>2</yellow>(', '2(')

                quotes = re.findall('\'(.*?)\'', line)
                quotes = ['\'' + q + '\'' for q in quotes]
                for q in quotes:
                    line = line.replace(q, '<green>' + q + '</green>')

                if line.endswith('# +'): # highlight line in code block
                    line = '<mark>' + line.replace('# +', '</mark>')
                elif line.endswith('# -'): # highlight line in code block
                    line = '<mark style="background:#ff9999;"> ' + line.replace('# -', '</mark>')

                if '#' in line:
                    line = line.replace('#', '<gray>#')
                    line += '</gray>'

            else:
                buttons = get_tags(line, '[', ']')

                for b in buttons:
                    if not ',' in b:
                        # line = line.replace(f'[{b}]', f'''<a href="{b}"</a>''')
                        # print(line)
                        continue

                    # print('button:', b)
                    number_of_commas = b.count(',')
                    name, link, image = b, '', None

                    if number_of_commas == 1:
                        name, link = b.split(',')
                        line = line.replace(f'[{b}]', f'''<a href="{link}" class="button">{name}</a>''')

                    elif number_of_commas == 2:
                        name, link, image = b.split(',')
                        is_image_button = True
                        image_code = ''
                        if len(image.strip()) > 0:
                            image_code = f'''style="background-image: url('{image.strip()}')"'''
                        # line += f'''<a href="{link}" class="button_big" {image_code}><span>{name}</span></a>'''
                        line = line.replace(f'[{b}]', f'''<a href="{link}" class="button_big" {image_code}><span>{name}</span></a>''')

                line = line.replace('  ', '&nbsp;&nbsp;')


            if 'http' in line and not 'class="button' in line:  # find urls and convert them to links
                words = line.split(' ')
                words = [f'<a href="{w}">{w}</a>' if w.startswith('http') else w for w in words]
                line = ' '.join(words)


            new_text += line
            if not is_image_button and not is_code_block:
                new_text += '<br>'

            new_text += '\n'


    new_text += '\n</html>'

    with open('sswg.css', 'w', encoding='utf-8') as css_file:
        css_file.write(dedent('''
            html {max-width: 100%; margin: auto; color: #333333;}
            a.button {padding: 15px 32px; background-color: #555; border-radius: 2em; border-width: 0px; text-decoration: none; color: white; font-size: 25.0px; line-height: 2.5em;}
            a.button:hover {background-color: #777}
            a.button_big {padding: 0.5em; background-image: linear-gradient(to top, #427b0e, #9ba97d); background-color: lightgray; background-blend-mode: multiply; border-radius: .75em; border-width: 0px; text-decoration: none; min-width: 150px; max-width: 150px; min-height: 150px; max-height: 150px; display: inline-block; vertical-align: top; margin: 4px 4px 10px 4px; color: white; font-size: 25.0px; background-size: auto 100%; background-position-x: center;}
            a.button_big:hover {background-color: white; color: #e6d23f; text-decoration: underline;}
            mark {background: #ccff99;}
            span {background-color: rgba(0, 0, 0, 0.55); padding: .1em; line-height: 1.35em;}
            img {max-width: 100%; vertical-align: top;}
            .code_block {background-color: whitesmoke; padding: 10px; margin: 0; font-family: monospace; font-size: 20; font-weight: normal; white-space: pre;}
            .sidebar {position:fixed; z-index:1; left:1em; top:1em;}
            @media screen and (max-width: 1800px) {.sidebar {display:none;}}

            purple {color: hsl(289.0, 50%, 50%);}
            gray {color: gray;}
            olive {color: olive;}
            yellow {color: darkgoldenrod;}
            green {color: seagreen;}
            blue {color: hsl(210, 50%, 50%);}
            ''')
        )


    with open(txt.stem + '.html', 'w', encoding='utf-8') as text_file:
        text_file.write(new_text)
        print('finished building:', txt.stem + '.html')
