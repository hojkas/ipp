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
                with open(argument):
                    pass
                int_source = argument
            except IOError:
                file_err_msg += 'Nepodarilo se otevrit soubor "' + argument + '".\n'
                file_error = True
        if option == '--input':
            try:
                with open(argument):
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


def check_int(integer):
    if re.search(r'^([-+])?(\d)+$', integer):
        return True
    return False


def check_string(string):
    if re.search(r'^(([^#\\\s]|\\\d{3})*)?$', string):
        return True
    return False


def check_bool(boolean):
    if boolean == 'true' or boolean == 'false':
        return True
    return False


def check_nil(nil):
    if nil == 'nil':
        return True
    return False


def check_label(label):
    if re.search(r'^[a-zA-Z_\-$&%*!?][a-zA-Z0-9_\-$&%*!?]*$', label):
        return True
    return False


def check_var(var):
    if re.search(r'^([GTL])F@[a-zA-Z_\-$&%*!?][a-zA-Z0-9_\-$&%*!?]*$', var):
        return True
    return False


def check_symb(symb):
    return check_var(symb) or check_nil(symb) or check_bool(symb) or check_int(symb) or check_string(symb)


def exit_msg_num_args(name, order, right):
    print('Spatny pocet argumentu u instrukce "', name, '" (order: ', order, '), ocekavano ', right,
          '.', sep='', file=sys.stderr)
    exit(32)


def exit_msg_type_arg(name, order, expected, got_type, got_value):
    print('Argument [', got_type, '/', got_value, '] instrukce "', name, '" (order: ', order, ') nesplnuje pozadavky ',
          expected, '.', sep='', file=sys.stderr)
    exit(32)


def my_out_print(s):
    res = ''
    skip = 0
    for i in range(0, len(s)):
        if s[i] == '\\':
            skip = 4
            res += chr(int(s[i + 1:i + 4]))

        if skip == 0:
            res += s[i]
        else:
            skip -= 1

    print(res, sep='', end='')


# TODO delete
def exit_neumim_ramce():
    print('Jsem baby program, jeste neumim ramce, pardon.', file=sys.stderr)
    exit(99)


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
        if (a_type != 'int' and a_type != 'string' and a_type != 'bool' and a_type != 'nil' and a_type != 'var'
                and a_type != 'type' and a_type != 'label'):
            print('Neexistujici atribut type "', a_type, '" u argumentu.', sep='', file=sys.stderr)
            exit(32)
        self.type = a_type
        # TODO pokud nevyresim pozdeji, zde kontrola podminek pro symb/var/type/label
        self.value = value


class Instruction:
    def __init__(self, opcode, order, arg1, arg2, arg3):
        self.opcode = opcode
        self.order = order
        self.arg1 = arg1
        self.arg2 = arg2
        self.arg3 = arg3

        # TODO delete, existuje jen kdybych zjistila, ze je to tu treba checkovat
        # pole moznych instrukci a jejich operandu
        '''
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
        '''


class Frame:
    def __init__(self):
        self.n_var = 0
        self.vars = []

    def add_var(self, var):
        self.n_var += 1
        self.vars.append(var)

    # Vraci bool, zda-li var existuje, typ, a value (None pokud nema typ/value)
    def find_var(self, name):
        for var in self.vars:
            if var.name == name:
                return True, var.type, var.value
        return False, None, None

    def change_type_value(self, name, new_type, new_value):
        for var in self.vars:
            if var.name == name:
                var.type = new_type
                var.value = new_value
                return True
        return False

    def change_type(self, name, new_type):
        for var in self.vars:
            if var.name == name:
                var.type = new_type
                return True
        return False

    def change_value(self, name, new_value):
        for var in self.vars:
            if var.name == name:
                var.value = new_value
                return True
        return False

    def debug_frame(self):
        res = 'Obsah: (total: ' + str(self.n_var) + ') (name/type/value)'
        for var in self.vars:
            if var.value is None:
                var_value = 'None'
            else:
                var_value = var.value
            if var.type is None:
                var_type = 'None'
            else:
                var_type = var.type
            res += '\n  ' + var.name + '/' + var_type + '/' + var_value
        return res


# Vytvori z predaneho elementu instrukce objekt instruction s navazanymi objekty argument
def get_instruction(elem):
    count = 0
    arg1 = None
    arg2 = None
    arg3 = None

    # zpracovani argumentu instrukce
    for arg in elem:
        if arg.tag != 'arg1' and arg.tag != 'arg2' and arg.tag != 'arg3':
            print('Neocekavany element "', arg, '" nalezen, ocekavano arg1-3.', sep='', file=sys.stderr)
            exit(32)
        if len(arg.attrib) != 1 or 'type' not in arg.attrib:
            print('Spatny pocet atributu argumentu v instrukci', elem.attrib['opcode'],
                  'nebo neslo o atribut "type".', file=sys.stderr)
            exit(32)
        count += 1
        if arg.text is None:
            new_text = ''
        else:
            new_text = arg.text
        if count == 1:
            arg1 = Argument(arg.attrib['type'], new_text)
        elif count == 2:
            arg2 = Argument(arg.attrib['type'], new_text)
        elif count == 3:
            arg3 = Argument(arg.attrib['type'], new_text)
        else:
            print('Prilis argumentu u instrukce', elem.attrib['opcode'], file=sys.stderr)
            exit(32)

    # kontrola atributu instrukce
    if 'opcode' not in elem.attrib or 'order' not in elem.attrib or len(elem.attrib) != 2:
        print('U instrukce nejsou vhodne atributy (chybi opcode, order ci existuje nejaky extra.', file=sys.stderr)

    # kontrola existujiciho opcode
    possible = ['MOVE', 'CREATEFRAME', 'PUSHFRAME', 'POPFRAME', 'DEFVAR', 'CALL', 'RETURN', 'PUSHS', 'POPS',
                'ADD', 'SUB', 'MUL', 'IDIV', 'LG', 'GT', 'EQ', 'AND', 'OR', 'NOT', 'INT2CHAR', 'STRI2INT', 'READ',
                'WRITE', 'CONCAT', 'STRLEN', 'GETCHAR', 'SETCHAR', 'TYPE', 'LABEL', 'JUMP', 'JUMPIFEQ',
                'JUMPIFNEQ', 'EXIT', 'DPRINT', 'BREAK']

    # cyklus najde jmeno instrukce v possible a overi typ argumentu, existuji-li
    valid = False
    opcode = elem.attrib['opcode'].upper()
    for poss in possible:
        if poss == opcode:
            valid = True
            break
    if not valid:
        print('Neznama instrukce"', opcode, '".', sep='', file=sys.stderr)
        exit(32)

    # samotna tvorba objektu instrukce
    return Instruction(opcode, int(elem.attrib['order']), arg1, arg2, arg3)


class ProcessSource:
    # inicializace nacte XML soubor, zkontroluje "well-formed", korenovy element program a jeho atributy
    # zpracuje instrukce do self.ins, zalozi iterator pres ne
    # vytvori self.gf jako global frame
    def __init__(self):
        int_source, int_input = check_args()
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
            self.ins.append(get_instruction(inst))
        # seradi list objektu instruction podle order hodnoty
        self.ins.sort(key=lambda x: x.order)

        # projede ins podle hodnoty order, zkontroluje, jestli nejsou hodnoty < 1 nebo duplicitni
        if self.ins[0].order < 1:
            print('Order atribut instrukce nesmi zacinat cislem mensim nez 1.', file=sys.stderr)
            exit(32)
        last = self.ins[0].order
        for one in self.ins[1:]:
            if last == one.order:
                print('Opakujici se order', one.order, 'mezi instrukcemi.', file=sys.stderr)
                exit(32)
            last = one.order

        # inicializuje iterator pres list instrukci
        self.ins_iter = iter(self.ins)
        self.cur_ins = None

        # vytvori global frame
        self.gf = Frame()

        self.pre_run = True
        self.ins_done = 0

    # projede seznam instrukci pred programem a spusti kazdou funkci pro instrukci,
    # kde se zkontroluje pocet argumentu a odpovidajici typ (bez spravneho typu uvnitr promenne)
    # a resestuje iterator
    def do_pre_run(self):
        while self.do_next_ins():
            pass
        self.pre_run = False
        self.ins_iter = iter(self.ins)
        self.ins_done = 0

    # extrahuje ramec, najde v nem var, spadne s odpovidajicim kodem pokud var/ramec neexistuje
    def get_var_type_value_from_arg(self, arg):
        var = arg.value
        if re.search(r'^GF@', var):
            # prohleda gf
            searched = var.split('@')[1]
            found, v_type, value = self.gf.find_var(searched)
            if not found:
                print('Promenna', var, 'v ramci GF neexistuje.', file=sys.stderr)
                exit(54)
            if value is None:
                print('Promenna', var, 'nema hodnotu.', file=sys.stderr)
                exit(56)
            if v_type is None:
                # TODO is this actually error?
                print('Promenna', var, 'nema type. Hope this is error?', file=sys.stderr)
                exit(53)
            return v_type, value
        elif re.search(r'^TF@', var):
            # TODO az budou ramce, a muze to existovat?
            exit_neumim_ramce()
        elif re.search(r'^LF@', var):
            # TODO az budou ramce
            exit_neumim_ramce()
        else:
            print('Neznamy ramec promenne', var, '+ tato chyba by nemela nastat (get_var_value).', file=sys.stderr)
            exit(55)

    def store_var_type_value_from_arg(self, arg, v_type, value):
        var = arg.value
        if re.search(r'^GF@', var):
            # prohleda gf
            searched = var.split('@')[1]
            found = self.gf.change_type_value(searched, v_type, value)
            if not found:
                print('Promenna', var, 'v ramci GF neexistuje.', file=sys.stderr)
                exit(54)
        elif re.search(r'^TF@', var):
            # TODO az budou ramce, a muze to existovat?
            exit_neumim_ramce()
        elif re.search(r'^LF@', var):
            # TODO az budou ramce
            exit_neumim_ramce()
        else:
            print('Neznamy ramec promenne', var, '+ tato chyba by nemela nastat (store_var_value).', file=sys.stderr)
            exit(55)

    # extrahuje hodnotu symb z argumentu, v pripade var vola funci get_var_value a pada na danych chybach
    def get_symb_type_value_from_arg(self, arg):
        if arg.type == 'var':
            return self.get_var_type_value_from_arg(arg)
        else:
            return arg.type, arg.value

    def check_cur_args(self, t1=None, t2=None, t3=None):
        n = sum(x is not None for x in [t1, t2, t3])
        # zkontroluje pocet argumentu
        if n == 0:
            if self.cur_ins.arg1 or self.cur_ins.arg2 or self.cur_ins.arg3:
                exit_msg_num_args(self.cur_ins.opcode, self.cur_ins.order, 0)
            return
        elif n == 1:
            if not self.cur_ins.arg1 or self.cur_ins.arg2 or self.cur_ins.arg3:
                exit_msg_num_args(self.cur_ins.opcode, self.cur_ins.order, 1)
        elif n == 2:
            if not self.cur_ins.arg1 or not self.cur_ins.arg2 or self.cur_ins.arg3:
                exit_msg_num_args(self.cur_ins.opcode, self.cur_ins.order, 2)
        elif n == 3:
            if not self.cur_ins.arg1 or not self.cur_ins.arg2 or not self.cur_ins.arg3:
                exit_msg_num_args(self.cur_ins.opcode, self.cur_ins.order, 3)

        t = []
        a = []
        if n == 1:
            t = [t1]
            a = [self.cur_ins.arg1]
        if n == 2:
            t = [t1, t2]
            a = [self.cur_ins.arg1, self.cur_ins.arg2]
        if n == 3:
            t = [t1, t2, t3]
            a = [self.cur_ins.arg1, self.cur_ins.arg2, self.cur_ins.arg3]

        for i in range(0, n):
            if t[i] == '<symb>':
                if not check_symb(a[i].value) and a[i].type == 'type' and a[i].type == 'label':
                    exit_msg_type_arg(self.cur_ins.opcode, self.cur_ins.order, t[i], a[i].type, a[i].value)
            elif t[i] == '<type>':
                if (not a[i].value == 'bool' and not a[i].value == 'int' and not a[i].value == 'string'
                        and a[i].type != 'type'):
                    exit_msg_type_arg(self.cur_ins.opcode, self.cur_ins.order, t[i], a[i].type, a[i].value)
            elif t[i] == '<var>':
                if not check_var(a[i].value) and a[i].type != 'var':
                    exit_msg_type_arg(self.cur_ins.opcode, self.cur_ins.order, t[i], a[i].type, a[i].value)
            elif t[i] == '<label>':
                if not check_label(a[i].value) and a[i].type != 'label':
                    exit_msg_type_arg(self.cur_ins.opcode, self.cur_ins.order, t[i], a[i].type, a[i].value)
            else:
                print('Pepega something wrong', t[i], a[i].value, file=sys.stderr)
                exit(99)

    def move_func(self):
        # MOVE <var> <symb>
        if self.pre_run:
            # cast, ktera se provede pri kontrole syntaxe pred zacatkem interpretace
            # u kazde funkce, zahrnuje napr. kontrolu poctu argumentu a spravny typ symb/var/label obsahu
            self.check_cur_args('<var>', '<symb>')
            return

        # cast, ktera se provede pri samotne interpretaci
        new_type, new_value = self.get_symb_type_value_from_arg(self.cur_ins.arg2)
        self.store_var_type_value_from_arg(self.cur_ins.arg1, new_type, new_value)

    def createframe_func(self):
        # CREATEFRAME
        if self.pre_run:
            self.check_cur_args()
            return

        # TODO
        pass

    def pushframe_func(self):
        # PUSHFRAME
        if self.pre_run:
            self.check_cur_args()
            return

        # TODO
        pass

    def popframe_func(self):
        # POPFRAME
        if self.pre_run:
            self.check_cur_args()
            return

        # TODO
        pass

    def defvar_func(self):
        # DEFVAR <var>
        if self.pre_run:
            self.check_cur_args('<var>')
            return

        frame, name = self.cur_ins.arg1.value.split('@')
        if frame == "GF":
            res = self.gf.find_var(name)
            if res[0]:
                print('Promenna ', name, 'jiz v GF existuje.')
                exit(52)
            self.gf.add_var(Variable(name))
        elif frame == "TF":
            # TODO jak budou ramce... a muze toto existovat?
            exit_neumim_ramce()
        elif frame == "LF":
            # TODO jak budou ramce
            exit_neumim_ramce()
        else:
            print('Neznamy ramec', frame, 'a sem by se to pravdepodobne nemelo dostat (defvar lookup).',
                  file=sys.stderr)
            exit(32)

    def call_func(self):
        # CALL <label>
        # TODO
        if self.pre_run:
            self.check_cur_args('<label>')
            return

        pass

    def return_func(self):
        # RETURN
        if self.pre_run:
            self.check_cur_args()
            return

        # TODO
        pass

    def pushs_func(self):
        # PUSHS <symb>
        # TODO
        if self.pre_run:
            self.check_cur_args('<symb>')
            return

        pass

    def pops_func(self):
        # POPS <var>
        # TODO
        if self.pre_run:
            return

        pass

    def add_func(self):
        # ADD <var> <symb> <symb>
        # TODO
        if self.pre_run:
            return

        pass

    def sub_func(self):
        # SUB <var> <symb> <symb>
        # TODO
        if self.pre_run:
            return

        pass

    def mul_func(self):
        # MUL <var> <symb> <symb>
        # TODO
        if self.pre_run:
            return

        pass

    def idiv_func(self):
        # IDIV <var> <symb> <symb>
        # TODO
        if self.pre_run:
            return

        pass

    def lt_func(self):
        # LT <var> <symb> <symb>
        # TODO
        if self.pre_run:
            return

        pass

    def gt_func(self):
        # GT <var> <symb> <symb>
        # TODO
        if self.pre_run:
            return

        pass

    def eq_func(self):
        # EQ <var> <symb> <symb>
        # TODO
        if self.pre_run:
            return

        pass

    def and_func(self):
        # AND <var> <symb> <symb>
        # TODO
        if self.pre_run:
            return

        pass

    def or_func(self):
        # OR <var> <symb> <symb>
        # TODO
        if self.pre_run:
            return

        pass

    def not_func(self):
        # NOT <var> <symb>
        # TODO
        if self.pre_run:
            return

        pass

    def int2char_func(self):
        # INT2CHAR <var> <symb>
        # TODO
        if self.pre_run:
            return

        pass

    def stri2int_func(self):
        # STRI2INT <var> <symb> <symb>
        # TODO
        if self.pre_run:
            return

        pass

    def read_func(self):
        # READ <var> <type>
        # TODO
        if self.pre_run:
            return

        pass

    def write_func(self):
        # WRITE <symb>
        if self.pre_run:
            self.check_cur_args('<symb>')
            return

        t, value = self.get_symb_type_value_from_arg(self.cur_ins.arg1)
        my_out_print(value)

    def concat_func(self):
        # CONCAT <var> <symb> <symb>
        # TODO
        if self.pre_run:
            return

        pass

    def strlen_func(self):
        # STRLEN <var> <symb>
        # TODO
        if self.pre_run:
            return

        pass

    def getchar_func(self):
        # GETCHAR <var> <symb> <symb>
        # TODO
        if self.pre_run:
            return

        pass

    def setchar_func(self):
        # SETCHAR <var> <symb> <symb>
        # TODO
        if self.pre_run:
            return

        pass

    def type_func(self):
        # TYPE <var> <symb>
        # TODO
        if self.pre_run:
            return

        pass

    def label_func(self):
        # LABEL <label>
        # TODO
        if self.pre_run:
            return

        pass

    def jump_func(self):
        # JUMP <label>
        # TODO
        if self.pre_run:
            return

        pass

    def jumpifeq_func(self):
        # JUMPIFEQ <label> <symb> <symb>
        # TODO
        if self.pre_run:
            self.check_cur_args('<label>', '<symb>', '<symb>')
            return

        pass

    def jumpifneq_func(self):
        # JUMIFNEQ <label> <symb> <symb>
        # TODO
        if self.pre_run:
            return

        pass

    def exit_func(self):
        # EXIT <symb>
        # TODO
        if self.pre_run:
            return

        pass

    def dprint_func(self):
        # DPRINT <symb>
        if self.pre_run:
            self.check_cur_args('<symb>')
            '''if not self.cur_ins.arg1 or self.cur_ins.arg2 or self.cur_ins.arg3:
                exit_msg_num_args(self.cur_ins.opcode, self.cur_ins.order, 1)
            if not check_symb(self.cur_ins.arg1.value):
                exit_msg_type_arg(self.cur_ins.opcode, self.cur_ins.order, '<symb>', self.cur_ins.arg1.type,
                                  self.cur_ins.arg1.value)'''
            return

        t, value = self.get_symb_type_value_from_arg(self.cur_ins.arg1)
        if value == '':
            value = 'empty string'
        print(t, ':', value, file=sys.stderr)

    def break_func(self):
        # BREAK
        if self.pre_run:
            if self.cur_ins.arg1 or self.cur_ins.arg2 or self.cur_ins.arg3:
                exit_msg_num_args(self.cur_ins.opcode, self.cur_ins.order, 0)
            return

        print('Stav interpretu:\n----------------\nAktualni instrukce: ', self.cur_ins.opcode, ' (order: ',
              self.cur_ins.order, ')\nPocet zpracovanych instrukci (bez teto): ', self.ins_done,
              sep='', file=sys.stderr)

        print('Ramec GF:')
        print(self.gf.debug_frame())

        # TODO pridat debug ostatnich frames, az budou hotove

    def do_next_ins(self):
        try:
            self.cur_ins = next(self.ins_iter)
        except StopIteration:
            return False

        try:
            # spusti funkci dane instrukce, naming convention name_func()
            func = 'self.' + self.cur_ins.opcode.lower() + '_func()'
            eval(func)
            self.ins_done += 1
        except NameError as err:
            print(err, '\nInvalidní opcode "', self.cur_ins.opcode, '" nebo neni funkce z nejakeho duvodu jeste'
                                                                    ' naimplementovana.', sep='', file=sys.stderr)
            exit(32)
        return True


# temp funkce na vypisy
# TODO odstranit
def write_arg(arg):
    if arg.value == '':
        print(arg.type, '-', 'empty')
    else:
        print(arg.type, '-', arg.value)


def write_ins(ins):
    print('Instruction: ', ins.opcode, ' (', ins.order, ')', sep='')
    if ins.arg1:
        write_arg(ins.arg1)
    if ins.arg2:
        write_arg(ins.arg2)
    if ins.arg3:
        write_arg(ins.arg3)


def write_all_ins(inss):
    print('--- INS BEGIN ---')
    for ins in inss:
        write_ins(ins)
    print('--- INS END ---')


# MAIN BODY

src = ProcessSource()
# write_all_ins(src.ins)
src.do_pre_run()

while src.do_next_ins():
    # TODO delete
    # print('Did:', src.cur_ins.opcode)
    pass
