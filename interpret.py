import sys
import re
import xml.etree.ElementTree as et
import getopt

int_source = ''
int_input = ''


def check_args():
    global int_source, int_input
    opts = ['']
    try:
        opts, args = getopt.getopt(sys.argv[1:], '', ['help', 'source=', 'input='])
    except getopt.GetoptError as err:
        print(err, file=sys.stderr)
        exit(10)

    for option, argument in opts:
        if option == '--help':
            print('Program načte XML reprezentaci programu a tento program s využitím vstupu dle parametrů příkazové '
                  'řádky interpretuje a generuje výstup.')
            print('Parametry "--source=file" se nastavi file jako zdrojova XML, "--input=file" jako samotny input '
                  'programu. Aspon jeden musí být využit.')
            exit(0)
        if option == '--source':
            try:
                src = open(argument, 'r')
                int_source = src.read()
            except IOError as err:
                print('Nepodarilo se otevrit soubor "', argument, '".', sep='', file=sys.stderr)
                exit(11)
        if option == '--input':
            try:
                inp = open(argument, 'r')
                int_input = inp.read()
            except IOError:
                print('Nepodarilo se otevrit soubor "', argument, '".', sep='', file=sys.stderr)
                exit(11)

    if not int_source and not int_input:
        print('Minimalne jeden z parametru --input=file nebo --source=file musi byt zadan', file=sys.stderr)
        exit(10)
    if not int_source:
        int_source = sys.stdin.read()
    if not int_input:
        int_input = sys.stdin.read()


# MAIN BODY
check_args()

print('Src:', int_source, 'Input:', int_input)
