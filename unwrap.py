def read_and_unwrap(input):
    '''Reads input file and concatenates wrapped lines. Lines are concatenated if next line starts with space or tab

    input is a file-like object
    '''
    accumulator = ''
    ln = input.readline()
    while ln != '':
        if ln.startswith(' ') or ln.startswith('\t'):
            accumulator += ln.strip()
        else:
            if len(accumulator) > 0:
                yield accumulator
            accumulator = ln.strip()
        ln = input.readline()
    yield accumulator

