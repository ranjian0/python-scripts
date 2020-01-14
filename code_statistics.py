import os

code_ext = (
    '.py',
    '.gd',
    '.h', '.c', 'cc', 
    '.hpp', '.cpp', '.cxx',
    '.js', '.css', '.html',
    '.cmd', '.sh', '.bat',
    '.cmake'
)

comment_identifiers = (
    '#', '"""', "'''",
    '//', '/*'
)

def code_stats(path):
    code_lines = 0
    empty_lines = 0
    comment_lines = 0

    for dpath, dname, fname in os.walk(path):
        if fname:
            for name in fname:
                if any(name.endswith(ext) for ext in code_ext):
                    with open(os.path.join(dpath, name), 'r') as _file:
                        lines = []
                        try: lines = _file.readlines()
                        except Exception: pass
                        
                        for line in lines:
                            l = line.lstrip()
                            
                            if len(l) == 0:
                                empty_lines += 1
                            elif any(l.startswith(ci) for ci in comment_identifiers):
                                comment_lines += 1
                            else:
                                code_lines += 1

    stats = f"""
Code Statistics for "{path}"
`````````````````````{'`'*len(path)}`
Empty Lines = {empty_lines}
Comments    = {comment_lines}
LoC         = {code_lines}
``````````````{'`'*len(str(code_lines))}
TOTAL       = {empty_lines + comment_lines + code_lines}    
``````````````{'`'*len(str(code_lines))}
"""
    print(stats)
    
if __name__ == '__main__':
    import sys
    path = '/media/ranjian0/Backup/Workspace/projects/building_tool'
    if len(sys.argv) == 2:
        path = sys.argv[1]
    
    code_stats(path)
