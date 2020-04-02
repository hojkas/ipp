import sys
import re
import xml.etree.ElementTree as et
import getopt
from os import access, R_OK
from os.path import isfile

int_source = ''
int_input = ''


# Funkce nacte argumenty, zpracuje, a do int_source a int_input vlozi z zadaneho zdroje obsah
# Vystup: v int_source a int_input nahrany obsah souboru/stdin
def check_args():
    global int_source, int_input
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


class ProcessXml:
    def __init__(self):
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


# MAIN BODY
check_args()
xml = ProcessXml()
print(xml.source.getroot().tag)


