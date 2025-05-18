import sys
from os import path
import re
from pathlib import Path
from textwrap import dedent
import shutil


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


def colorize_code(line):
    indent = len(line) - len(line.lstrip())

    if line.startswith(indent*' '):
        line = line[indent:]
    line = line.replace('<', '&lt;').replace('>', '&gt;')   # make sure < and > are shown in code blocks
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
        line = line.replace('#', '<gray>#') + '</gray>'
    return line


# default values
path = Path('.')
file_types = '.sswg'
ignore = '_*'
language_tag = 'en'
output_folder = '.'

if '--help' in sys.argv:
    print(f'sswg.py --file_types={file_types} --ignore={ignore} --output_folder={output_folder} --language={language_tag}')
    # print(dedent('''\
    #     example settings:
    #         --file_types=.sswg,.txt (make it accept both .sswg and .txt files)
    #         --ignore=_* (ignore files starting with "_")
    #         --language_tag=es (changes html lang tag to "es")'''
    #     ))

for arg in sys.argv:
    if arg.startswith('--ignore='):
        ignore = arg.split('=')[1]

    if arg.startswith('--language_tag='):
        language_tag = arg.split('=')[1]

    if arg.startswith('--output_folder='):
        output_folder = arg.split('=')[1].strip('"').strip('\'')

# find files to parse
files = []
if ',' in file_types:
    file_types = file_types.split(',')
else:
    file_types = (file_types, )
# print('file_types:', file_types)

for suffix in file_types:
    files.extend(list(path.glob('*' + suffix)))

files_to_ignore = []
for ignore_pattern in ignore.split(','):
    files_to_ignore.extend(list(path.glob(ignore_pattern)))

files = [f for f in files if f.name not in files_to_ignore]


if not files:
    print('sswg: No source file found with extentions:', file_types)
    sys.exit()

output_folder_path = Path(output_folder)
if not output_folder_path.exists():
    output_folder_path.mkdir()

# create css file
with (output_folder_path/'sswg.css').open('w', encoding='utf-8') as css_file:
    css_file.write(dedent('''
        html {max-width: 100%; margin: auto; color: #333333;}
        body {font-size: 1em; line-height: 1.5; margin: auto; max-width: 100%;}
        h1 {font-size: 4em; line-height: 1;}
        h2 {font-size: 2em; font-weight: 600; line-height: 1;}
        h3 {font-size:1.5em;}

        a {transition: color .2s; color: #19405c; white-space: nowrap;}
        a:link, a:visited {color: #19405c;}
        a:hover {color: #7FDBFF;}
        a:active {transition: color .3s; color: #007BE6;}
        .link {text-decoration: none;}

        a.button {padding: 15px 32px; font-size:.85em; background-color: #555; border-radius: 2em; border-width: 0px; text-decoration: none; color: white; font-size: 25.0px; line-height: 2.5em;}
        a.button:hover {background-color: #777}
        a.button_big {padding: 0.5em; background-image: linear-gradient(to top, #427b0e, #9ba97d); background-color: lightgray; background-blend-mode: multiply; border-radius: .75em; border-width: 0px; text-decoration: none; min-width: 150px; max-width: 150px; min-height: 150px; max-height: 150px; display: inline-block; vertical-align: top; margin: 4px 4px 10px 4px; color: white; font-size: 25.0px; background-size: auto 100%; background-position-x: center;}
        a.button_big:hover {background-color: white; color: #e6d23f; text-decoration: underline;}
        mark {background: #ccff99;}
        span {background-color: whitesmoke; padding: .1em; line-height: 1.35em;}
        img {max-width: 100%; vertical-align: top;}
        code_block {display: block;
  width: 100%; background-color: whitesmoke; padding: 10px; margin: 1.5em 0px 1.5em 0px; position: relative; font-family: monospace; font-size: 1em; font-weight: normal; white-space: pre; overflow: auto; border-radius:4px; scrollbar-color:red;}
        .copy_code_button {position:absolute; right:10px; border:none; border-radius:5px; font-family:inherit; color:gray; user-select:none; -webkit-user-select:none;}
        /* Hide scrollbar for Chrome, Safari and Opera */
        code_block::-webkit-scrollbar {
        }
        .sidebar {position:fixed; z-index:1; left:1em; top:1em;}
        @media screen and (max-width: 1800px) {.sidebar {display:none;}}
        @media (max-width: 725px) {
            .button {display: block;}
        }

        purple {color: hsl(289.0, 50%, 50%);}
        gray {color: gray;}
        olive {color: olive;}
        yellow {color: darkgoldenrod;}
        green {color: seagreen;}
        blue {color: hsl(210, 50%, 50%);}
        ''')
    )

# convert files to html
for target_file in files:
    # print(txt.stem)
    with open(target_file, 'r', encoding='utf-8') as t:
        text = t.read()

    if '#insert ' in text:
        new_lines = []
        lines = text.split('\n')
        for l in lines:
            if l.startswith('#insert'):
                path = l.split('insert', 1)[1].strip()
                if path.startswith('Path('):
                    path = eval(path)

                with open(path, 'r', encoding='utf-8') as text_file:
                    new_lines.extend(text_file.read().splitlines())
                continue
            new_lines.append(l)
        text = '\n'.join(new_lines)

    title = target_file.stem
    if '#title' in text:
        title = text.split('#title')[1].split('\n',1)[0]

    new_text = dedent(f'''\
        <!DOCTYPE HTML>
        <!--generated with sswg-->
        <html lang="{language_tag}">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <head>
            <title>{title}</title>
            <link rel="stylesheet" href="sswg.css">
            <link rel="stylesheet" href="style.css">
            <link rel="icon" type="image/x-icon" href="favicon.ico">
        </head>
        <body>
        ''')


    # parse tags and ignore commented lines
    current_alignment = 'left'
    # current_scale = 5
    # current_font_weight = 'normal'
    # current_font_style = 'normal'
    current_width = 1200
    is_in_code_block = False
    is_in_style_tag = False
    inline_images = []
    code_block_id = 0

    lines = text.split('\n')

    # add support for markdown inspired tags
    new_lines = []
    new_text += f'<div style="max-width:{current_width}px; margin:auto;">\n'
    new_text += f'<div style="text-align:{current_alignment};">\n'

    for l in lines:

        if 'http' in l and not l.startswith('[') and not is_in_code_block:  # find urls and convert them to links
            words = l.split(' ')
            words = [f'<a href="{w}">{w}</a>' if w.startswith('http') else w for w in words]
            l = ' '.join(words)


        if l.startswith('### ') and not is_in_code_block:
            new_text += dedent(f'''\
                <h1 id="{l[4:]}">
                {l[4:]}
                </h1>''')
            continue

        if l.startswith('## ') and not is_in_code_block:
            new_text += dedent(f'''\
                <h2 id="{l[3:]}">
                {l[3:]}
                </h2>''')
            continue

        if l.startswith('# ') and not is_in_code_block:
            new_text += dedent(f'''\
                <h3 id="{l[2:]}">
                {l[2:]}
                </h3>''')
            continue

        if l.startswith('#title'):
            continue

        if l.startswith('#width '):
            value = int(l[len('#width '):])

            if value != current_width:
                # close pevious width div
                new_text += f'</div>\n'

                print('width change:', value)
                current_width = value
                new_text += f'<div style="max-width:{current_width}px; margin:auto;">\n'
            continue

        if l.startswith('#left') or l.startswith('#center') or l.startswith('#right'):
            new_alignment = l[1:]

            if new_alignment != current_alignment:
                # close pevious alignment div
                new_text += f'</div>\n'

                print(f'alignment change: {current_alignment} --> {new_alignment}')
                current_alignment = new_alignment
                new_text += f'<div style="text-align:{current_alignment};">\n'
            continue

        #index support
        if l.strip().startswith('#index '):
            current_indent = l.split('#')[0].replace('  ', '&nbsp;&nbsp;')
            # print('aaaaaaaaaaaa')
            tag, target_document = l.split('#')[1].strip().split(' ')
            with open(target_document, 'r', encoding='utf-8') as file:
                headlines = [l.split('## ')[1].strip() for l in file.readlines() if l.strip().startswith('## ')] # get name after ##
                for e in headlines:
                    link = target_document
                    for suffix in file_types:
                        link = link.replace(suffix, '.html')
                    link = f'{link}#{e}'
                    new_text += current_indent + f'• <a href="{link}">{e}</a><br>\n'
            continue

        elif l.startswith('```'):
            if not is_in_code_block:
                new_text += f'<code_block id="code_block_{code_block_id}">'
                new_text += f'<button class="copy_code_button" onclick="copy_to_clipboard(code_block_{code_block_id})">copy</button>'
                code_block_id += 1
            else:
                new_text += '</code_block>\n'
            is_in_code_block = not is_in_code_block
            continue

        elif '`' in l and not '```' in l and l.count('`') % 2 == 0 and not is_in_code_block:
            parts = l.split('`')

            for i, p in enumerate(parts):
                if i % 2 == 1:
                    parts[i] = f'<span>{p}</span>'

            l = ''.join(parts)

        elif l.startswith('#image ') and not is_in_code_block:
            image_name = l[len(l.split(' ')[0]):].strip()
            print('adding image:', image_name)
            for ft in ('.jpg', '.png', '.gif'):
                if image_name.endswith(ft):
                    new_text += f'<img src="{image_name}"></img> <br>\n'
                    inline_images.append(image_name)
            continue

        # elif tag.startswith('background'):
        #     style += 'background-color: ' + tag.split(' ')[1] + ';'


        elif not is_in_code_block:
            buttons = get_tags(l, '[', ']')
            for b in buttons:
                if not ',' in b:
                    # l = l.replace(f'[{b}]', f'''<a href="{b}"</a>''')
                    # print(l)
                    continue

                # print('button:', b)
                number_of_commas = b.count(',')
                name, link, image = b, '', None

                if number_of_commas == 1:
                    name, link = b.split(',')
                    l = l.replace(f'[{b}]', f'''<a href="{link}" class="button">{name}</a>''')

                elif number_of_commas == 2:
                    name, link, image = b.split(',')
                    is_image_button = True
                    image_code = ''
                    if len(image.strip()) > 0:
                        image_code = f'''style="background-image: url('{image.strip()}')"'''
                    # l += f'''<a href="{link}" class="button_big" {image_code}><span>{name}</span></a>'''
                    l = l.replace(f'[{b}]', f'''<a href="{link}" class="button_big" {image_code}><span>{name}</span></a>\n''')
                    continue
            if buttons:
                new_text += l
                continue

        if is_in_code_block:
            l = l.replace('  ', '&nbsp;&nbsp;')
            l = colorize_code(l)
            new_text += l + '\n'
            continue

        if l == '' and not is_in_code_block:
            new_text += '<br>\n'
            continue


        l = l.replace('  ', '&nbsp;&nbsp;')
        if ('((') in l and '))' in l:
            l = l.replace('((', '<button>')
            l = l.replace('))', '</button>')

        new_text += l
        if not is_in_code_block:
            new_text += '<br>\n'
        else:
            new_text += '\n'

    #             elif tag.startswith('background'):
    #                 style += 'background-color: ' + tag.split(' ')[1] + ';'


    new_text += dedent('''\
        <script>
        function copy_to_clipboard(containerid) {
            var range = document.createRange()
            range.selectNode(containerid)
            window.getSelection().removeAllRanges()
            window.getSelection().addRange(range)
            document.execCommand("copy")
            window.getSelection().removeAllRanges()
        }
        </script>
        ''')

    new_text += '<br>\n<br>'    # add some space at the bottom the content is never flush with the bottom of the screen.
    new_text += '\n</body>\n</html>'

    with open(output_folder_path / f'{target_file.stem}.html', 'w', encoding='utf-8') as text_file:
        text_file.write(new_text)
        print('finished building:', target_file.stem + '.html')
        # if __name__ == '__main__':
        #     print(new_text)


    # # if using output_folder, copy images over
    # if output_folder_path != '.':
    #     for img_name in inline_images:
    #         print('--------- copy over image:', img_name)
    #         # copy file to folder
    #         shutil.copy(path/img_name, output_folder_path/img_name)