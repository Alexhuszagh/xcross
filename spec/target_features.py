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

bin_dir = "/opt/bin/"

def find_executable(executables, name):
    '''Find an executable if available.'''

    for exe in executables:
        if os.path.exists(exe):
            return exe
    raise ValueError(f'Unable to find {name}.')

def find_linker():
    '''Get the executable for the linker.'''

    linkers = ['ld', 'ld.bfd', 'ld.gold']
    linkers += [f'{bin_dir}/{i}' for i in linkers]
    return find_executable(linkers, 'linker')

def find_cc():
    '''Find the C compiler.'''

    compilers = ['cc', 'gcc', 'clang']
    compilers += [f'{bin_dir}/{i}' for i in compilers]
    return find_executable(compilers, 'cc')

def find_cxx():
    '''Find the C++ compiler.'''

    compilers = ['c++', 'g++', 'clang++']
    compilers += [f'{bin_dir}/{i}' for i in compilers]
    return find_executable(compilers, 'c++')

def linker_is_gnu(linker):
    '''Determine if the linker flavor is GNU.'''

    with subprocess.Popen(
        [linker, '--version'],
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

def parse_defines(cc):
    '''Dump and parse the GCC compiler defines.'''

    with subprocess.Popen(
        f'{cc} -dM -E - < /dev/null',
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

def eh_frame_header(linker, cxx):
    '''Determine if the linker supports --eh-frame-hdr.'''

    devnull = subprocess.DEVNULL
    with open('main.cc', 'w') as file:
        file.write('int main() { return 0; }')
    subprocess.check_call(
        [cxx, '-c', 'main.cc', '-o', 'main.o'],
        stderr=devnull,
        stdout=devnull,
    )
    code = subprocess.call(
        [linker, 'main.o', '-o', 'main', '--eh-frame-hdr'],
        stderr=devnull,
        stdout=devnull,
    )
    os.unlink('main.cc')
    os.unlink('main.o')
    try:
        os.unlink('main')
    except FileNotFoundError:
        pass
    return code == 0

def alignof(c_type, cc):
    '''Calculate the alignment of a given type.'''

    # We use the hack to get the alignment:
    #   char (*alignment)[alignof({type})] = 1;
    with open('main.c', 'w') as file:
        file.write('#include <stdalign.h>\n')
        file.write('#include <stdint.h>\n')
        file.write(f'char (*alignment)[alignof({c_type})] = 1.0;\n')
        file.write('int main() { return 0; }\n')

    with subprocess.Popen(
        [cc, 'main.c', '-o', 'main', '-std=c11'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    ) as process:
        stdout = process.stdout.read().decode('utf-8')

    # Delete file after getting output.
    os.unlink('main.c')
    try:
        os.unlink('main')
    except FileNotFoundError:
        pass

    # Match the type size.
    capture = r'\[(\d+)\]'
    quote = r'[\'‘’]'
    floats = r'(?:double|float|long double)'
    regexes = [
        re.compile(fr'{capture}{quote} with an expression of type'),
        re.compile(fr'{capture}{quote} with an expression of incompatible type'),
        re.compile(fr'{capture}{quote} from {quote}{floats}{quote} makes pointer'),
        re.compile(fr'{capture}{quote} using type {quote}{floats}{quote}'),
    ]
    for regex in regexes:
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
    elif byte_order == '__ORDER_PDP_ENDIAN__':
        return 'pdp'
    raise ValueError('Unknown byte order.')

def target_pointer(defines, cc):
    '''Get the size and alignment of a pointer.'''

    size = defines['__SIZEOF_POINTER__']
    align = alignof('char*', cc)
    return {
        'size': size,
        'align': align,
    }

def char_is_signed(cc):
    '''Determine if a character is signed.'''

    devnull = subprocess.DEVNULL
    with open('main.c', 'w') as file:
        file.write('#include <limits.h>\n')
        file.write('#if CHAR_MIN < 0\n')
        file.write('#error signed char\n')
        file.write('#endif\n')
        file.write('int main() { return 0; }\n')
    code = subprocess.call(
        [cc, 'main.c', '-o', 'main'],
        stdout=devnull,
        stderr=devnull,
    )
    os.unlink('main.c')
    try:
        os.unlink('main')
    except FileNotFoundError:
        pass
    return code != 0

def target_c_int(defines, cc):
    '''Get the size and alignment of `int`.'''

    size = defines['__SIZEOF_INT__']
    align = alignof('int', cc)
    return {
        'size': size,
        'align': align,
    }

def pic(defines):
    '''Determine the flag to support position-independent code.'''

    value = defines.get('__PIC__', '0')
    if value == '1':
        return '-fpic'
    if value == '2':
        return '-fPIC'
    return None

def pie(defines):
    '''Determine the flag to support position-independent executables.'''

    value = defines.get('__PIE__', '0')
    if value == '1':
        return '-fpie'
    if value == '2':
        return '-fPIE'
    return None

def main():
    '''Entry point.'''

    linker = find_linker()
    cc = find_cc()
    cxx = find_cxx()
    defines = parse_defines()
    data = {
        'arch': os.environ['ARCH'],
        'os': os.environ['OS'],
        'flags': os.environ['FLAGS'],
        'optional_flags': os.environ['OPTIONAL_FLAGS'],
        'eh-frame-header': eh_frame_header(linker, cxx),
        'linker-is-gnu': linker_is_gnu(linker),
        'target-endian': target_endian(defines),
        'target-pointer': target_pointer(defines, cc),
        'target-c-int': target_c_int(defines, cc),
        'pic': pic(defines),
        'pie': pie(defines),
        'target-c-char': {
            # Both the size and alignment are guaranteed
            # by the standard to be 1 in both C and C++,
            # although this is redundant, it's just for
            # consistency.
            'size': '1',
            'align': '1',
            'signed': char_is_signed(cc)
        },
    }
    c_types = {
        'size_t': 'size_t',
        'wchar_t': 'wchar_t',
        'float': 'float',
        'double': 'double',
        'long_double': 'long double',
        'float80': '__float80',
        'float128': '__float128',
        'short': 'short',
        'long': 'long',
        'long_long': 'long long',
        'int128': '__int128',
    }
    for label, c_type in c_types.items():
        define = f'__SIZEOF_{label.upper()}__'
        if define in defines:
            key = f'target-c-{label.replace("_", "-")}'
            data[key] = {
                'size': defines[define],
                'align': alignof(c_type, cc)
            }

    with open(f'{bin_dir}/target-specs.json', 'w') as file:
        json.dump(data, file)
    with open(f'{bin_dir}/target-specs', 'w') as file:
        file.write('#/bin/bash\n')
        file.write(f'cat {bin_dir}/target-specs.json | jq\n')
    flags = stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
    st = os.stat(f'{bin_dir}/target-specs')
    os.chmod(f'{bin_dir}/target-specs', st.st_mode | flags)

if __name__ == '__main__':
    main()
