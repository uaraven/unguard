import re

CLASS = 'class'
METHODS = 'methods'


class ProguardMap(object):
    """
    This class holds mapping between obfuscated and unobfuscated names.
    Data is read from ProGuard mapping file
    """
    JAVA_ID = r'[a-zA-Z_][a-zA-Z0-9_\$]*'

    CLASS_MAPPING = re.compile(r'^((%s)(\.%s)*) -> ((%s)(\.%s)*):$' % (JAVA_ID, JAVA_ID, JAVA_ID, JAVA_ID))
    METHOD_MAPPING = re.compile(r'^(\d+):(\d+):.* (%s)\(.*\) -> (%s)$' % (JAVA_ID, JAVA_ID))
    OBFUSCATED_METHOD_REFERENCE = re.compile(r'((%s(\.%s)+)\.(%s))\((.*)\)' % (JAVA_ID, JAVA_ID, JAVA_ID))
    OBFUSCATED_CLASS_REFERENCE = re.compile(r'%s(\.%s)+' % (JAVA_ID, JAVA_ID))
    SOURCE_LINE_INFO = re.compile(r'SourceFile:(\d+)')

    def __init__(self, map_file_name, verbose=False):
        """
        Read ProGuard mapping file and create in-memory mapping between obfuscated and non-obfuscated names

        Parameters:
            map_file_name - name of mapping file
            verbose - if True, write lot of text to standard output
        """
        self.verbose = verbose
        self.mapping = self.__read_proguard_mapping(map_file_name)

    def deobfuscate_line(self, line):
        """ Tries to find and replace all the references to obfuscated names in a text string """
        mi = self.OBFUSCATED_METHOD_REFERENCE.finditer(line.strip())
        for m in mi:
            line = self.__process_method(line, m)
        mi = self.OBFUSCATED_CLASS_REFERENCE.finditer(line.strip())
        for m in mi:
            line = self.__process_class(line, m)
        return line

    def __find_class(self, obfuscated_name):
        if obfuscated_name in self.mapping:
            return self.mapping[obfuscated_name]
        else:
            return None

    def __process_method(self, line, match):
        result = line
        class_name = match.group(2)
        if class_name in self.mapping:
            source_line = self.__extract_source_line(match.group(5))
            obfuscated_method_name = match.group(4)
            class_map = self.mapping[class_name]
            method_name = self.__get_method_name(class_map, obfuscated_method_name, source_line)
            if method_name is not None:
                deobfuscated_reference = class_map[CLASS] + '.' + method_name
                result = result.replace(match.group(1), deobfuscated_reference)
            else:
                result = result.replace(class_name, class_map[CLASS])
        return result

    def __process_class(self, line, match):
        result = line
        if match.group(0) in self.mapping:
            obfuscated_class_name = match.group(0)
            deobfuscated_class_name = self.mapping[obfuscated_class_name][CLASS]
            result = result.replace(obfuscated_class_name, deobfuscated_class_name)
        return result

    def __extract_source_line(self, line_info):
        m = self.SOURCE_LINE_INFO.match(line_info)
        if m is not None:
            return int(m.group(1))
        else:
            return -1

    @staticmethod
    def __get_method_name(class_map, obfuscated_method_name, source_line):
        for method in class_map[METHODS]:
            if obfuscated_method_name == method[0] and method[1] <= source_line <= method[2]:
                return class_map[METHODS][method]
        return None

    def __parse_member(self, input_line, result):
        matcher = self.METHOD_MAPPING.match(input_line.strip())
        if matcher is not None:
            start_line = int(matcher.group(1))
            end_line = int(matcher.group(2))
            method_name = matcher.group(3)
            obfuscated_name = matcher.group(4)
            if method_name != obfuscated_name:
                if self.verbose:
                    print '%s: %s -> %s (%d, %d)' % (result[CLASS], obfuscated_name, method_name, start_line, end_line)
                result[METHODS][(obfuscated_name, start_line, end_line)] = method_name
            else:
                if self.verbose:
                    print 'Method', method_name, 'is not obfuscated'

    def __read_class_mapping(self, map_file, class_map, result):
        matcher = self.CLASS_MAPPING.match(class_map.strip())
        if matcher is not None:
            class_name = matcher.group(1)
            obfuscated_name = matcher.group(4)
            if self.verbose:
                print 'Class', obfuscated_name, '->', class_name
            result[obfuscated_name] = {CLASS: class_name, METHODS: {}}
            ln = map_file.readline()
            while ln != '':
                if ln.startswith('    '):
                    self.__parse_member(ln, result[obfuscated_name])
                    ln = map_file.readline()
                else:
                    if len(result[obfuscated_name][METHODS]) == 0 and obfuscated_name == class_name:
                        if self.verbose:
                            print 'Class', class_name, 'is not obfuscated, removing from mapping'
                        del result[obfuscated_name]
                    return ln
        else:
            return ' '

    def __read_proguard_mapping(self, file_name):
        result = {}
        if self.verbose:
            print 'Reading mapping from', file_name
        with open(file_name) as map_file:
            ln = map_file.readline()
            while ln != '' and ln is not None:
                ln = self.__read_class_mapping(map_file, ln, result)
                if ln == ' ':
                    ln = map_file.readline()

        if self.verbose:
            print len(result), 'class definitions loaded'
        return result

