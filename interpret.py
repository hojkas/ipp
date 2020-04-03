import sys
import re
import xml.etree.ElementTree as et
import getopt


# Funkce nacte argumenty, zpracuje, a do int_source a int_input vlozi z zadaneho zdroje obsah
# Vystup: vraci int_source a int_input v tomto poradi, kde je bud prazdny retezec indikujici stdin nebo nazev
# souboru, odkud se ma dany text brat
def check_args():
    int_source = ''
    int_input = ''
    opts = ['']
    file_error = False
    file_err_msg = ''
    try:
        opts, args = getopt.getopt(sys.argv[1:], '', ['help', 'source=', 'input='])
    except getopt.GetoptError as err:
        print(err, file=sys.stderr)
        exit(10)

    for option, argument in opts:
        if option == '--help':
            if len(opts) != 1:
                print('Zakazana kombinace parametru, help nelze s nicim kombinovat.', file=sys.stderr)
                exit(10)
            print('Program načte XML reprezentaci programu a tento program s využitím vstupu dle parametrů příkazové '
                  'řádky interpretuje a generuje výstup.')
            print('Parametry "--source=file" se nastavi file jako zdrojova XML, "--input=file" jako samotny input '
                  'programu. Aspon jeden musí být využit.')
            exit(0)
        if option == '--source':
            try:
                with open(argument) as f:
                    pass
                int_source = argument
            except IOError as err:
                file_err_msg += 'Nepodarilo se otevrit soubor "' + argument + '".\n'
                file_error = True
        if option == '--input':
            try:
                with open(argument) as f:
                    pass
                int_input = argument
            except IOError:
                file_err_msg += 'Nepodarilo se otevrit soubor "' + argument + '".\n'
                file_error = True

    if file_error:
        print(file_err_msg, end='', file=sys.stderr)
        exit(11)
    if not int_source and not int_input:
        print('Minimalne jeden z parametru --input=file nebo --source=file musi byt zadan', file=sys.stderr)
        exit(10)
    return int_source, int_input


class Variable:
    def __init__(self, name):
        self.name = name
        self.type = None
        self.value = None

    def add_value(self, value):
        self.value = value

    def add_type(self, val_type):
        self.type = val_type


class Argument:
    def __init__(self, a_type, value):
        if a_type != 'symb' and a_type != 'var' and a_type != 'type' and a_type != 'label':
            print('Neexistujici atribut type "', a_type, '" u argumentu.', sep='', file=sys.stderr)
            exit(32)
        self.type = a_type
        # TODO pokud nevyresim pozdeji, zde kontrola podminek pro symb/var/type/label
        self.value = value


class Instruction:
    def __init__(self, name, order, arg1, arg2, arg3):
        name = name.upper()
        self.opcode = name
        self.order = order

        # pole moznych instrukci a jejich operandu
        possible = [
          ['MOVE',       'var', 'symb',  None],
          ['CREATEFRAME', None,  None,   None],
          ['PUSHFRAME',   None,  None,   None],
          ['POPFRAME',    None,  None,   None],
          ['DEFVAR',     'var',  None,   None],
          ['CALL',       'label', None,  None],
          ['RETURN',      None,  None,   None],
          ['PUSHS',      'symb', None,   None],
          ['POPS',       'var',  None,   None],
          ['ADD',        'var', 'symb', 'symb'],
          ['SUB',        'var', 'symb', 'symb'],
          ['MUL',        'var', 'symb', 'symb'],
          ['IDIV',       'var', 'symb', 'symb'],
          ['LG',         'var', 'symb', 'symb'],
          ['GT',         'var', 'symb', 'symb'],
          ['EQ',         'var', 'symb', 'symb'],
          ['AND',        'var', 'symb', 'symb'],
          ['OR',         'var', 'symb', 'symb'],
          ['NOT',        'var', 'symb',  None],
          ['INT2CHAR',   'var', 'symb',  None],
          ['STRI2INT',   'var', 'symb', 'symb'],
          ['READ',       'var', 'type',  None],
          ['WRITE',      'symb', None,   None],
          ['CONCAT',     'var', 'symb', 'symb'],
          ['STRLEN',     'var', 'symb',  None],
          ['GETCHAR',    'var', 'symb', 'symb'],
          ['SETCHAR',    'var', 'symb', 'symb'],
          ['TYPE',       'var', 'symb',  None],
          ['LABEL',      'label', None,  None],
          ['JUMP',       'label', None,  None],
          ['JUMPIFEQ',   'label', 'symb', 'symb'],
          ['JUMPIFNEQ',  'label', 'symb', 'symb'],
          ['EXIT',       'symb',  None,   None],
          ['DPRINT',     'symb',  None,   None],
          ['BREAK',       None,   None,   None]]

        # uprava typu arg kvuli snazsimu porovnavani pozdeji
        if arg1 is None:
            arg1_type = None
        else:
            arg1_type = arg1.type
        if arg2 is None:
            arg2_type = None
        else:
            arg2_type = arg2.type
        if arg3 is None:
            arg3_type = None
        else:
            arg3_type = arg3.type

        # cyklus najde jmeno instrukce v possible a overi typ argumentu, existuji-li
        valid = False
        for poss, a1, a2, a3 in possible:
            if poss == name:
                valid = True
                if a1 != arg1_type or a2 != arg2_type or a3 != arg3_type:
                    print('U instrukce "', poss, '" nesedi typ argumentu. Ocekavany "', a1, '/', a2, '/', a3,
                          '" ale obdrzeny byly "', arg1_type, '/', arg2_type, '/', arg3_type,
                          '".', sep='', file=sys.stderr)
                    exit(32)
                self.arg1 = arg1
                self.arg2 = arg2
                self.arg3 = arg3
                break

        if not valid:
            print('Neznama instrukce"', name, '".', sep='', file=sys.stderr)
            exit(32)


class Frame:
    def __init__(self):
        self.n_var = 0
        self.vars = []

    def add_var(self, var):
        self.n_var += 1
        self.vars.append(var)

    # Vraci bool, zda-li var existuje, typ, a value ('' pokud nema typ/value)
    def find_var(self, name):
        for var in self.vars:
            if var.name == name:
                return True, var.type, var.value
        return False, '', ''


class ProcessSource:
    # inicializace nacte XML soubor, zkontroluje "well-formed", korenovy element program a jeho atributy
    # zpracuje
    def __init__(self):
        int_source, int_input = check_args()
        self.at_end = False
        if not int_source:
            try:
                self.source = et.parse(sys.stdin)
            except et.ParseError:
                print('XML source ze stdin neni "well-formed".', file=sys.stderr)
                exit(31)
        else:
            try:
                self.source = et.parse(int_source)
            except et.ParseError:
                print('XML source ze souboru "', int_source, '" neni "well-formed".', sep='', file=sys.stderr)
                exit(31)
        self.root = self.source.getroot()
        if self.root.tag != 'program':
            print('Korenovy element XML zdroje neni "program".', file=sys.stderr)
            exit(32)

        attribs = self.root.attrib
        lang_found = False

        for att_name, att_value in attribs.items():
            if att_name == 'language':
                lang_found = True
                if att_value != 'IPPcode20':
                    print('Program nema pozadovany atribut language "IPPcode20".', file=sys.stderr)
                    exit(32)
            elif att_name != 'name' and att_name != 'description':
                print('Neznamy textovy atribut "', att_name, '" v korenovem elementu program.', sep='', file=sys.stderr)
                exit(32)

        if not lang_found:
            print('Program nema pozadovany atribut language "IPPcode20".', file=sys.stderr)
            exit(32)

        self.ins = []
        for inst in self.root:
            if inst.tag != 'instruction':
                print('Neznamy element s nazvem "', inst.tag, '", ocekavany element "instruction".',
                      sep='', file=sys.stderr)
                exit(32)
            self.get_instruction(inst)
            self.ins.append(inst)

        # self.ins.sort(key=lambda x: x.opcode)

    def get_instruction(self, elem):
        count = 0
        for arg in elem:
            if arg.tag != 'arg1' and arg.tag != 'arg2' and arg.tag != 'arg3':
                print('Neocekavany element "', arg, '" nalezen, ocekavano arg1-3.', sep='', file=sys.stderr)
                exit(32)
            if len(arg.attrib) != 1 or not 'type' in arg.attrib:
                print('Spatny pocet atributu argumentu v instrukci', elem.attrib['opcode'], 'nebo neslo o atribut "type".', file=sys.stderr)
                exit(32)


# MAIN BODY
src = ProcessSource()
i = Instruction('WRite', 5, Argument('symb', 4), None, None)
