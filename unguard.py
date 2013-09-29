import argparse
import sys

from mapper import ProguardMap
from unwrap import read_and_unwrap


def prepare_arg_parser():
    parser = argparse.ArgumentParser(usage='%(prog)s [options] input_file')
    parser.add_argument('-o', '--output', type=argparse.FileType('w'), default=sys.stdout, dest='output',
                        help='output file. If omitted, standard output will be used')
    parser.add_argument('-m', '--map-file', required=True, dest='map_file',
                        help='proguard mapping file')
    parser.add_argument('-v', '--verbose', action='store_true', default=False, dest='verbose',
                        help='produce more output')
    parser.add_argument('infile', nargs='?', type=argparse.FileType('r'), default=sys.stdin,
                        help='input file to deobfuscate. If omitted standard input will be used')

    return parser.parse_args()


def main():
    args = prepare_arg_parser()
    mapper = ProguardMap(args.map_file, args.verbose)
    for line in read_and_unwrap(args.infile):
        args.output.write(mapper.deobfuscate_line(line) + '\n')


if __name__ == '__main__':
    main()