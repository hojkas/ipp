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
        return
    print('Textovy atribut', integer, 'neodpovida zadanemu tvaru pro typ "int".', file=sys.stderr)
    exit(32)


def check_string(string):
    if re.search(r'^(([^#\\\s]|\\\d{3})*)?$', string):
        return
    print('Textovy atribut', string, 'neodpovida zadanemu tvaru pro typ "string".', file=sys.stderr)
    exit(32)


def check_bool(boolean):
    if boolean == 'true' or boolean == 'false':
        return
    print('Textovy atribut', boolean, 'neodpovida zadanemu tvaru pro typ "boolean".', file=sys.stderr)
    exit(32)


def check_nil(nil):
    if nil == 'nil':
        return
    print('Textovy atribut', nil, 'neodpovida zadanemu tvaru pro typ "nil".', file=sys.stderr)
    exit(32)


def check_label(label):
    if re.search(r'^[a-zA-Z_\-$&%*!?][a-zA-Z0-9_\-$&%*!?]*$', label):
        return
    print('Textovy atribut', label, 'neodpovida zadanemu tvaru pro typ "label".', file=sys.stderr)
    exit(32)


def check_type(t):
    if t == 'bool' or t == 'int' or t == 'string':
        return
    print('Textovy atribut', t, 'neodpovida zadanemu tvaru pro typ "type".', file=sys.stderr)
    exit(32)


def check_var(var):
    if re.search(r'^([GTL])F@[a-zA-Z_\-$&%*!?][a-zA-Z0-9_\-$&%*!?]*$', var):
        return
    print('Textovy atribut', var, 'neodpovida zadanemu tvaru pro typ "var".', file=sys.stderr)
    exit(32)


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
        if a_type == 'bool':
            check_bool(value)
            if value == 'false':
                self.value = False
            elif value == 'true':
                self.value = True
            else:
                print('Bool spatne hodnoty. Nemelo by nastat.', file=sys.stderr)
                exit(32)
        elif a_type == 'int':
            check_int(value)
            try:
                self.value = int(value)
            except ValueError:
                print('Int spatne hodnoty. Nemelo by nastat.', file=sys.stderr)
                exit(32)
        elif a_type == 'nil':
            check_nil(value)
            self.value = None
        elif a_type == 'type':
            check_type(value)
            self.value = value
        elif a_type == 'var':
            check_var(value)
            self.value = value
        else:
            check_string(value)
            self.value = value


class Instruction:
    def __init__(self, opcode, order, arg1, arg2, arg3):
        self.opcode = opcode
        self.order = order
        self.arg1 = arg1
        self.arg2 = arg2
        self.arg3 = arg3


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
                var_value = str(var.value)
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
        if arg.tag == 'arg1':
            arg1 = Argument(arg.attrib['type'], new_text)
        elif arg.tag == 'arg2':
            arg2 = Argument(arg.attrib['type'], new_text)
        elif arg.tag == 'arg3':
            arg3 = Argument(arg.attrib['type'], new_text)
        elif count > 3:
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


# noinspection DuplicatedCode
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
        self.ins_index = -1
        self.ins_len = len(self.ins)

        # vytvori global frame
        self.gf = Frame()
        self.lf = []
        self.tf = None

        self.call_stack = []
        self.labels = dict()
        self.labels_to_check = []
        self.symb_stack = []

        self.pre_run = True
        self.ins_done = 0

    # projede seznam instrukci pred programem a spusti kazdou funkci pro instrukci,
    # kde se zkontroluje pocet argumentu a odpovidajici typ (bez spravneho typu uvnitr promenne)
    # a resestuje iterator
    def do_pre_run(self):
        while self.do_next_ins():
            pass
        self.ins_index = -1
        self.pre_run = False
        self.ins_iter = iter(self.ins)
        self.ins_done = 0
        for label in self.labels_to_check:
            if not self.labels.get(label):
                print('Navesti "', label, '" co ma byt volano neexistuje.', sep='', file=sys.stderr)
                exit(52)

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
                print('Promenna', var, 'nema type. Hope this is error?', file=sys.stderr)
                exit(53)
            return v_type, value
        elif re.search(r'^TF@', var):
            if self.tf is None:
                print('Ramec TF neni inicializovan.')
                exit(55)
            searched = var.split('@')[1]
            found, v_type, value = self.tf.find_var(searched)
            if not found:
                print('Promenna', var, 'v ramci TF neexistuje.', file=sys.stderr)
                exit(54)
            if value is None:
                print('Promenna', var, 'nema hodnotu.', file=sys.stderr)
                exit(56)
            if v_type is None:
                print('Promenna', var, 'nema type. Hope this is error?', file=sys.stderr)
                exit(53)
            return v_type, value
        elif re.search(r'^LF@', var):
            if not self.lf:
                print('Ramec LF neni inicializovan.')
                exit(55)
            searched = var.split('@')[1]
            found, v_type, value = self.lf[-1].find_var(searched)
            if not found:
                print('Promenna', var, 'v ramci LF neexistuje.', file=sys.stderr)
                exit(54)
            if value is None:
                print('Promenna', var, 'nema hodnotu.', file=sys.stderr)
                exit(56)
            if v_type is None:
                print('Promenna', var, 'nema type. Hope this is error?', file=sys.stderr)
                exit(53)
            return v_type, value
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
            if self.tf is None:
                print('Ramec TF neni inicializovan.')
                exit(55)
            searched = var.split('@')[1]
            found = self.tf.change_type_value(searched, v_type, value)
            if not found:
                print('Promenna', var, 'v ramci TF neexistuje.', file=sys.stderr)
                exit(54)
        elif re.search(r'^LF@', var):
            if not self.lf:
                print('Ramec LF neni inicializovan.')
                exit(55)
            searched = var.split('@')[1]
            found = self.lf[-1].change_type_value(searched, v_type, value)
            if not found:
                print('Promenna', var, 'v ramci LF neexistuje.', file=sys.stderr)
                exit(54)
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
                if a[i].type == 'type' or a[i].type == 'label':
                    exit_msg_type_arg(self.cur_ins.opcode, self.cur_ins.order, t[i], a[i].type, a[i].value)
            elif t[i] == '<type>':
                if a[i].type != 'type':
                    exit_msg_type_arg(self.cur_ins.opcode, self.cur_ins.order, t[i], a[i].type, a[i].value)
            elif t[i] == '<var>':
                if a[i].type != 'var':
                    exit_msg_type_arg(self.cur_ins.opcode, self.cur_ins.order, t[i], a[i].type, a[i].value)
            elif t[i] == '<label>':
                if a[i].type != 'label':
                    exit_msg_type_arg(self.cur_ins.opcode, self.cur_ins.order, t[i], a[i].type, a[i].value)
            else:
                print('Pepega something wrong', t[i], a[i].value, file=sys.stderr)
                exit(99)

    # --- INSTRUKCE ---
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

        self.tf = Frame()

    def pushframe_func(self):
        # PUSHFRAME
        if self.pre_run:
            self.check_cur_args()
            return

        if not self.tf:
            print('Chyba, snaha PUSHFRAME kdyz neexistuje TF.', file=sys.stderr)
            exit(55)

        self.lf.append(self.tf)
        self.tf = None

    def popframe_func(self):
        # POPFRAME
        if self.pre_run:
            self.check_cur_args()
            return

        if not self.lf:
            print('Chyba, snaha POPFRAME kdyz je zasobnik LF prazdny.', file=sys.stderr)
            exit(55)

        self.tf = self.lf.pop()

    def defvar_func(self):
        # DEFVAR <var>
        if self.pre_run:
            self.check_cur_args('<var>')
            return

        frame, name = self.cur_ins.arg1.value.split('@')
        if frame == "GF":
            res = self.gf.find_var(name)
            if res[0]:
                print('Promenna ', name, 'jiz v GF existuje.', file=sys.stderr)
                exit(52)
            self.gf.add_var(Variable(name))
        elif frame == "TF":
            if self.tf is None:
                print('Snaha definovat promennou na TF, ktery neexistuje.', file=sys.stderr)
                exit(55)
            res = self.tf.find_var(name)
            if res[0]:
                print('Promenna ', name, 'jiz v TF existuje.', file=sys.stderr)
                exit(52)
            self.tf.add_var(Variable(name))
        elif frame == "LF":
            if not self.lf:
                print('Snaha definovat promennou na LF, ktery neexistuje.', file=sys.stderr)
                exit(55)
            res = self.lf[-1].find_var(name)
            if res[0]:
                print('Promenna ', name, 'jiz v LF existuje.', file=sys.stderr)
                exit(52)
            self.lf[-1].add_var(Variable(name))
        else:
            print('Neznamy ramec', frame, 'a sem by se to pravdepodobne nemelo dostat (defvar lookup).',
                  file=sys.stderr)
            exit(32)

    def call_func(self):
        # CALL <label>
        if self.pre_run:
            self.check_cur_args('<label>')
            return

        self.call_stack.append(self.ins_index)
        self.ins_index = self.labels.get(self.cur_ins.arg1.value)

    def return_func(self):
        # RETURN
        if self.pre_run:
            self.check_cur_args()
            return

        if not self.call_stack:
            print('Chyba, volani navratu z funkce kdyz je prazdny zasobnik volani.', file=sys.stderr)
            exit(56)

        self.ins_index = self.call_stack.pop()

    def pushs_func(self):
        # PUSHS <symb>
        if self.pre_run:
            self.check_cur_args('<symb>')
            return

        t, value = self.get_symb_type_value_from_arg(self.cur_ins.arg1)
        self.symb_stack.append((t, value))

    def pops_func(self):
        # POPS <var>
        if self.pre_run:
            self.check_cur_args('<var>')
            return

        if not self.symb_stack:
            print('Zasobnik na promenne/konstanty je prazdny.', file=sys.stderr)
            exit(56)

        new_type, new_value = self.symb_stack.pop()
        self.store_var_type_value_from_arg(self.cur_ins.arg1, new_type, new_value)

    def add_func(self):
        # ADD <var> <symb> <symb>
        if self.pre_run:
            self.check_cur_args('<var>', '<symb>', '<symb>')
            return

        op1_type, op1_value = self.get_symb_type_value_from_arg(self.cur_ins.arg2)
        op2_type, op2_value = self.get_symb_type_value_from_arg(self.cur_ins.arg3)
        if op1_type != 'int' or op2_type != 'int':
            print('Operandy instrukce ADD (order: ', self.cur_ins.order, ') nejsou typu int.', sep='', file=sys.stderr)
            exit(53)

        self.store_var_type_value_from_arg(self.cur_ins.arg1, 'int', op1_value + op2_value)

    def sub_func(self):
        # SUB <var> <symb> <symb>
        if self.pre_run:
            self.check_cur_args('<var>', '<symb>', '<symb>')
            return

        op1_type, op1_value = self.get_symb_type_value_from_arg(self.cur_ins.arg2)
        op2_type, op2_value = self.get_symb_type_value_from_arg(self.cur_ins.arg3)
        if op1_type != 'int' or op2_type != 'int':
            print('Operandy instrukce SUB (order: ', self.cur_ins.order, ') nejsou typu int.', sep='', file=sys.stderr)
            exit(53)

        self.store_var_type_value_from_arg(self.cur_ins.arg1, 'int', op1_value - op2_value)

    def mul_func(self):
        # MUL <var> <symb> <symb>
        if self.pre_run:
            self.check_cur_args('<var>', '<symb>', '<symb>')
            return

        op1_type, op1_value = self.get_symb_type_value_from_arg(self.cur_ins.arg2)
        op2_type, op2_value = self.get_symb_type_value_from_arg(self.cur_ins.arg3)
        if op1_type != 'int' or op2_type != 'int':
            print('Operandy instrukce MUL (order: ', self.cur_ins.order, ') nejsou typu int.', sep='', file=sys.stderr)
            exit(53)

        self.store_var_type_value_from_arg(self.cur_ins.arg1, 'int', op1_value * op2_value)

    def idiv_func(self):
        # IDIV <var> <symb> <symb>
        if self.pre_run:
            self.check_cur_args('<var>', '<symb>', '<symb>')
            return

        op1_type, op1_value = self.get_symb_type_value_from_arg(self.cur_ins.arg2)
        op2_type, op2_value = self.get_symb_type_value_from_arg(self.cur_ins.arg3)
        if op1_type != 'int' or op2_type != 'int':
            print('Operandy instrukce ADD (order: ', self.cur_ins.order, ') nejsou typu int.', sep='', file=sys.stderr)
            exit(53)

        if op2_value == 0:
            print('Chyba deleni nulou u IDIV instrukce (order: ', self.cur_ins.order, ').', sep='', file=sys.stderr)
            exit(57)

        self.store_var_type_value_from_arg(self.cur_ins.arg1, 'int', int(op1_value / op2_value))

    def lt_func(self):
        # LT <var> <symb> <symb>
        if self.pre_run:
            self.check_cur_args('<var>', '<symb>', '<symb>')
            return

        op1_type, op1_value = self.get_symb_type_value_from_arg(self.cur_ins.arg2)
        op2_type, op2_value = self.get_symb_type_value_from_arg(self.cur_ins.arg3)
        if op1_type == 'nil' or op2_type == 'nil':
            print('Jeden z operandu instrukce LT (order: ', self.cur_ins.order, ') je typu nil.', sep='',
                  file=sys.stderr)
            exit(53)
        if op1_type != op2_type:
            print('Typy operandu instrukce LT (order: ', self.cur_ins.order, ') se neshoduji.', sep='',
                  file=sys.stderr)
            exit(53)

        result = None
        if op1_type == 'int' or op2_type == 'string':
            result = (op1_value < op2_value)
        elif op1_type == 'bool':
            if not op1_value and op2_value:
                result = True
            else:
                result = False
        else:
            print('Something probably wrong.', file=sys.stderr)
            exit(32)
        self.store_var_type_value_from_arg(self.cur_ins.arg1, 'bool', result)

    def gt_func(self):
        # GT <var> <symb> <symb>
        if self.pre_run:
            self.check_cur_args('<var>', '<symb>', '<symb>')
            return

        op1_type, op1_value = self.get_symb_type_value_from_arg(self.cur_ins.arg2)
        op2_type, op2_value = self.get_symb_type_value_from_arg(self.cur_ins.arg3)
        if op1_type == 'nil' or op2_type == 'nil':
            print('Jeden z operandu instrukce GT (order: ', self.cur_ins.order, ') je typu nil.', sep='',
                  file=sys.stderr)
            exit(53)
        if op1_type != op2_type:
            print('Typy operandu instrukce GT (order: ', self.cur_ins.order, ') se neshoduji.', sep='',
                  file=sys.stderr)
            exit(53)

        result = None
        if op1_type == 'int' or op2_type == 'string':
            result = (op1_value > op2_value)
        elif op1_type == 'bool':
            if op1_value and not op2_value:
                result = True
            else:
                result = False
        else:
            print('Something probably wrong.', file=sys.stderr)
            exit(32)
        self.store_var_type_value_from_arg(self.cur_ins.arg1, 'bool', result)

    def eq_func(self):
        # EQ <var> <symb> <symb>
        if self.pre_run:
            self.check_cur_args('<var>', '<symb>', '<symb>')
            return

        op1_type, op1_value = self.get_symb_type_value_from_arg(self.cur_ins.arg2)
        op2_type, op2_value = self.get_symb_type_value_from_arg(self.cur_ins.arg3)
        result = None

        if op1_type == 'nil' or op2_type == 'nil':
            if op1_type == op2_type:
                result = True
            else:
                result = False
        elif op1_type != op2_type:
            print('Typy operandu instrukce EQ (order: ', self.cur_ins.order, ') se neshoduji.', sep='',
                  file=sys.stderr)
            exit(53)
        else:
            result = (op1_value == op2_value)

        self.store_var_type_value_from_arg(self.cur_ins.arg1, 'bool', result)

    def and_func(self):
        # AND <var> <symb> <symb>
        if self.pre_run:
            self.check_cur_args('<var>', '<symb>', '<symb>')
            return

        op1_type, op1_value = self.get_symb_type_value_from_arg(self.cur_ins.arg2)
        op2_type, op2_value = self.get_symb_type_value_from_arg(self.cur_ins.arg3)
        if op1_type != 'bool' or op2_type != 'bool':
            print('Operandy instrukce AND (order: ', self.cur_ins.order, ') nejsou typu bool.', sep='', file=sys.stderr)
            exit(53)

        self.store_var_type_value_from_arg(self.cur_ins.arg1, 'bool', op1_value and op2_value)

    def or_func(self):
        # OR <var> <symb> <symb>
        if self.pre_run:
            self.check_cur_args('<var>', '<symb>', '<symb>')
            return

        op1_type, op1_value = self.get_symb_type_value_from_arg(self.cur_ins.arg2)
        op2_type, op2_value = self.get_symb_type_value_from_arg(self.cur_ins.arg3)
        if op1_type != 'bool' or op2_type != 'bool':
            print('Operandy instrukce OR (order: ', self.cur_ins.order, ') nejsou typu bool.', sep='', file=sys.stderr)
            exit(53)

        self.store_var_type_value_from_arg(self.cur_ins.arg1, 'bool', op1_value or op2_value)

    def not_func(self):
        # NOT <var> <symb>
        if self.pre_run:
            self.check_cur_args('<var>', '<symb>')
            return

        op1_type, op1_value = self.get_symb_type_value_from_arg(self.cur_ins.arg2)
        if op1_type != 'bool':
            print('Operand instrukce OR (order: ', self.cur_ins.order, ') není typu bool.', sep='', file=sys.stderr)
            exit(53)

        self.store_var_type_value_from_arg(self.cur_ins.arg1, 'bool', not op1_value)

    def int2char_func(self):
        # INT2CHAR <var> <symb>
        if self.pre_run:
            self.check_cur_args('<var>', '<symb>')
            return

        op1_type, op1_value = self.get_symb_type_value_from_arg(self.cur_ins.arg2)
        if op1_type != 'int':
            print('Operand instrukce INT2CHAR (order: ', self.cur_ins.order, ') není typu int.', sep='',
                  file=sys.stderr)
            exit(53)

        try:
            result = chr(op1_value)
            self.store_var_type_value_from_arg(self.cur_ins.arg1, 'string', result)
        except ValueError:
            print('Hodnota mimo rozsah UNICODE znaku, instrukce INT2CHAR (order: ', self.cur_ins.order, ').',
                  sep='', file=sys.stderr)
            exit(58)

    def stri2int_func(self):
        # STRI2INT <var> <symb> <symb>
        # TODO
        if self.pre_run:
            self.check_cur_args('<var>', '<symb>', '<symb>')
            return

        pass

    def read_func(self):
        # READ <var> <type>
        # TODO
        if self.pre_run:
            self.check_cur_args('<var>', '<type>')
            return

        pass

    def write_func(self):
        # WRITE <symb>
        if self.pre_run:
            self.check_cur_args('<symb>')
            return

        t, value = self.get_symb_type_value_from_arg(self.cur_ins.arg1)
        if t == 'nil':
            value = 'nil'
        else:
            value = str(value)
        my_out_print(value)

    def concat_func(self):
        # CONCAT <var> <symb> <symb>
        if self.pre_run:
            self.check_cur_args('<var>', '<symb>', '<symb>')
            return

        op1_type, op1_value = self.get_symb_type_value_from_arg(self.cur_ins.arg2)
        op2_type, op2_value = self.get_symb_type_value_from_arg(self.cur_ins.arg3)
        if op1_type != 'string' or op2_type != 'string':
            print('Operandy instrukce CONCAT (order: ', self.cur_ins.order, ') nejsou typu string.', sep='',
                  file=sys.stderr)
            exit(53)

        self.store_var_type_value_from_arg(self.cur_ins.arg1, 'string', op1_value + op2_value)

    def strlen_func(self):
        # STRLEN <var> <symb>
        # TODO
        if self.pre_run:
            self.check_cur_args('<var>', '<symb>')
            return

        pass

    def getchar_func(self):
        # GETCHAR <var> <symb> <symb>
        # TODO
        if self.pre_run:
            self.check_cur_args('<var>', '<symb>', '<symb>')
            return

        pass

    def setchar_func(self):
        # SETCHAR <var> <symb> <symb>
        # TODO
        if self.pre_run:
            self.check_cur_args('<var>', '<symb>', '<symb>')
            return

        pass

    def type_func(self):
        # TYPE <var> <symb>
        # TODO
        if self.pre_run:
            self.check_cur_args('<var>', '<symb>')
            return

        pass

    def label_func(self):
        # LABEL <label>
        if self.pre_run:
            self.check_cur_args('<label>')
            if self.labels.get(self.cur_ins.arg1.value):
                print('Redefinice navesti "', self.cur_ins.arg1.value, '".', sep='', file=sys.stderr)
                exit(52)
            self.labels.update({self.cur_ins.arg1.value: self.ins_index})
            return

        pass

    def jump_func(self):
        # JUMP <label>
        if self.pre_run:
            self.check_cur_args('<label>')
            self.labels_to_check.append(self.cur_ins.arg1.value)
            return

        new_index = self.labels.get(self.cur_ins.arg1.value)
        if not new_index:
            print('Neexistujici navesti, pravdepodobne by se nemelo stat', file=sys.stderr)
        self.ins_index = new_index

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
            self.check_cur_args('<label>', '<symb>', '<symb>')
            return

        pass

    def exit_func(self):
        # EXIT <symb>
        if self.pre_run:
            self.check_cur_args('<symb>')
            return

        t, value = self.get_symb_type_value_from_arg(self.cur_ins.arg1)
        if t != 'int':
            print('Exit zavolan nad hodnotou co neni integer.', file=sys.stderr)
            exit(53)
        if value < 0 or value > 49:
            print('Exit zavolan s hodnotou mimo interval <0,49>', file=sys.stderr)
            exit(53)
        exit(value)

    def dprint_func(self):
        # DPRINT <symb>
        if self.pre_run:
            self.check_cur_args('<symb>')
            return

        t, value = self.get_symb_type_value_from_arg(self.cur_ins.arg1)
        if t == 'nil':
            value = 'nil'
        elif value == '':
            value = 'empty string'
        print(t, ':', str(value), file=sys.stderr)

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
        print(self.gf.debug_frame(), file=sys.stderr)

        if self.tf:
            print('Ramec TF:')
            print(self.tf.debug_frame(), file=sys.stderr)

        if self.lf:
            print('LF ramce (posledni aktualni):')
        for frame in self.lf:
            print('LF:')
            print(frame.debug_frame(), file=sys.stderr)

    def do_next_ins(self):
        # TODO delete this
        """
        old code with iteration
        try:
            self.cur_ins = next(self.ins_iter)
        except StopIteration:
            return False
        """
        self.ins_index += 1
        if self.ins_index == self.ins_len:
            return False
        self.cur_ins = self.ins[self.ins_index]

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
src.do_pre_run()
# write_all_ins(src.ins)

while src.do_next_ins():
    # TODO delete
    # print('Did:', src.cur_ins.opcode)
    pass
