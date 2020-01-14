import os
import re

HEADER = os.path.join(
    os.path.curdir, "extern", "include", "GLFW", "glfw3.h"
    )


def clean_comment(lines):
    # -- remove beginning '! '
    lines[0] = lines[0][2:]
    # -- remove c comment tokens, and right alignment
    lines = [line[2:].lstrip() for line in lines]
    # -- replace empty lines with '\n'
    for i in range(len(lines)):
        if not len(lines[i]):
            lines[i] = '\n'

    # -- remove doxygen references ['@sa', '@ingroup']
    lines = [l for l in lines if not l.startswith('@sa')]
    lines = [l for l in lines if not l.startswith('@ingroup')]

    # -- remove references between brackets {'[..](@ref ..)'}
    for i in range(len(lines)):
        res = re.findall(r'(?P<name>\[[\w\s]+\])(?P<ref>\(@ref \w+\))', lines[i])
        if res:
            data = lines[i]
            for name, ref in res:
                data = data.replace(name, name[1:-1])
                data = data.replace(ref, '')
            lines[i] = data

    # -- remove '@ref ' or '@ref'
    for i in range(len(lines)):
        if "@ref " in lines[i]:
            lines[i] = lines[i].replace('@ref ', '')
        if "@ref" in lines[i]:
            lines[i] = lines[i].replace('@ref', '')

    # -- Check if line starts with '@', and remove '@' then make titlecase
    # -- eg @brief -> Brief:
    for i in range(len(lines)):
        if lines[i].startswith('@'):
            sp = lines[i].find(' ')
            token = lines[i][0:sp]
            replacement = token[1:].title() + ':'
            lines[i] = lines[i].replace(token, replacement)

    # -- replace all other words that start with '@' with uppercase
    for i in range(len(lines)):
        res = re.findall(r'@\w+', lines[i])
        if res:
            token = res[-1]
            replacement = token[1:].upper()
            lines[i] = lines[i].replace(token, replacement)

    # -- remove empty lines at the end if any
    while lines[-1] == '\n':
        lines = lines[:-1]
    lines.append('\n')

    return lines


with open(HEADER, 'r') as header:
    lines = header.readlines()

    comments = []
    func_comments = {}
    start_comment, end_comment = None, None
    for idx, line in enumerate(lines):
        if line.strip().startswith('/*'):
            start_comment = idx
        elif line.strip().startswith('*/'):
            end_comment = idx

        # -- we have hit a function definition
        elif line.strip().startswith("GLFWAPI"):
            # -- get this function's python api name
            def_token = [t for t in line.strip().split() if t.startswith('glfw')][-1]
            func_name = def_token.split('(')[0][4:]

            # -- store the comment block for this function
            last_comment = clean_comment(comments[-1])
            func_comments[func_name] = last_comment

        # -- check if we found a comment block
        if start_comment and end_comment:
            comment = lines[start_comment:end_comment]
            comments.append(comment)

            start_comment, end_comment = None, None

with open("cyglfw.pyx", 'r') as IN, open('cydox.pyx', 'w') as OUT:

    out_lines = []
    for idx, line in enumerate(IN.readlines()):
        if line.startswith('def'):
            pyfunc_name = line.split()[1].split('(')[0]

            func_doc = func_comments.get(pyfunc_name)
            if not func_doc:
                print("FUCK : ", pyfunc_name)

            out_lines.append(line)
            out_lines.append('\t"""\n')
            out_lines.extend(['\t' + l for l in func_doc])
            out_lines.append('\t"""\n')

        else:
            out_lines.append(line)

    OUT.writelines(out_lines)
