#!/user/bin/env python
'''
    target_features
    ---------------

    Detect target features for a given architecture.
'''

import json
import os
import re
import stat
import subprocess

def find_linker():
    '''Get the executable for the linker.'''

    for linker in ['ld', 'ld.bfd', 'ld.gold']:
        path = os.path.join('/opt/bin', linker)
        if os.path.exists(path):
            return linker
    raise ValueError('Unable to find linker.')

def linker_is_gnu(linker):
    '''Determine if the linker flavor is GNU.'''

    with subprocess.Popen(
        [f'/opt/bin/{linker}', '--version'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    ) as process:
        code = process.wait()
        if code == 0:
            stdout = process.stdout.read().decode('utf-8')
            if 'GNU' in stdout:
                return True
            else:
                return False
    raise ValueError('Unable to call version to linker.')

def parse_defines():
    '''Dump and parse the GCC compiler defines.'''

    with subprocess.Popen(
        '/opt/bin/cc -dM -E - < /dev/null',
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    ) as process:
        code = process.wait()
        assert code == 0
        stdout = process.stdout.read().decode('utf-8')

    lines = stdout.splitlines()
    regex = re.compile(r'^#define (\S+) ?(.*)$')
    data = [regex.match(i).groups() for i in lines]
    return {k: v for k, v in data}

def eh_frame_header(linker):
    '''Determine if the linker supports --eh-frame-hdr.'''

    devnull = subprocess.DEVNULL
    with open('main.cc', 'w') as file:
        file.write('int main() { return 0; }')
    subprocess.check_call(['/opt/bin/c++', '-c', 'main.cc', '-o', 'main.o'], stdin=devnull, stdout=devnull)
    code = subprocess.call(
        [f'/opt/bin/{linker}', 'main.o', '-o', 'main', '--eh-frame-hdr'],
        stderr=devnull,
        stdout=devnull
    )
    os.unlink('main.cc')
    os.unlink('main.o')
    os.unlink('main')
    return code == 0

def alignof(c_type):
    '''Calculate the alignment of a given type.'''

    # We use the hack to get the alignment:
    #   char (*alignment)[alignof({type})] = 1;
    with open('main.c', 'w') as file:
        file.write('#include <stdalign.h>\n')
        file.write('#include <stdint.h>\n')
        file.write(f'char (*alignment)[alignof({c_type})] = 1;\n')
        file.write('int main() { return 0; }\n')

    with subprocess.Popen(
        ['/opt/bin/cc', 'main.c', '-o', 'main', '-std=c11'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    ) as process:
        stdout = process.stdout.read().decode('utf-8')

    # Delete file after getting output.
    os.unlink('main.c')

    # Match the type size.
    regex = re.compile(r'\[(\d+)\]\' with an expression of type')
    match = regex.search(stdout)
    if match is not None:
        return match.group(1)
    regex = re.compile(r'\[(\d+)\][\'‘’] from [\'‘’]int[\'‘’] makes pointer')
    match = regex.search(stdout)
    if match is not None:
        return match.group(1)

    raise ValueError(stdout)

def target_endian(defines):
    '''Get if the architecture is little-endian'''

    byte_order = defines['__BYTE_ORDER__']
    if byte_order == '__ORDER_LITTLE_ENDIAN__':
        return 'little'
    elif byte_order == '__ORDER_BIG_ENDIAN__':
        return 'big'
    raise ValueError('Unknown byte order.')

def target_pointer(defines):
    '''Get the size and alignment of a pointer.'''

    size = defines['__SIZEOF_POINTER__']
    align = alignof('char*')
    return {
        'size': size,
        'align': align,
    }

def target_c_int(defines):
    '''Get the size and alignment of `int`.'''

    size = defines['__SIZEOF_INT__']
    align = alignof('int')
    return {
        'size': size,
        'align': align,
    }

def main():
    '''Entry point.'''

    linker = find_linker()
    defines = parse_defines()
    data = {
        'arch': os.environ['ARCH'],
        'os': os.environ['OS'],
        'flags': os.environ['FLAGS'],
        'optional_flags': os.environ['OPTIONAL_FLAGS'],
        'eh-frame-header': eh_frame_header(linker),
        'linker-is-gnu': linker_is_gnu(linker),
        'target-endian': target_endian(defines),
        'target-pointer': target_pointer(defines),
        'target-c-int': target_c_int(defines),
        'pic': defines.get('__PIC__', '0'),
        'pie': defines.get('__PIE__', '0'),
    }
    c_types = {
        'size_t': 'size_t',
        'wchar_t': 'wchar_t',
        'float': 'float',
        'double': 'double',
        'short': 'short',
        'long': 'long',
        'long_long': 'long long',
        'int128': '__int128',
        'float128': '__float128',
    }
    for label, c_type in c_types.items():
        define = f'__SIZEOF_{label.upper()}__'
        if define in defines:
            key = f'target-c-{label.replace("_", "-")}'
            data[key] = {
                'size': defines[define],
                'align': alignof(c_type)
            }

    with open('/opt/bin/target-specs.json', 'w') as file:
        json.dump(data, file)
    with open('/opt/bin/target-specs.sh', 'w') as file:
        file.write('#/bin/bash\n')
        file.write('cat /opt/bin/target-specs.json | jq\n')
    flags = stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
    st = os.stat('/opt/bin/target-specs.sh')
    os.chmod('/opt/bin/target-specs.sh', st.st_mode | flags)

if __name__ == '__main__':
    main()
