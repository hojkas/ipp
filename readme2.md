# Implementační dokumentace k 1. úloze do IPP 2019/2020

Jméno a příjmení: Iveta Strnadová

Login: xstrna14

## interpret.py

Základem interpretace je třída `ProcessSource`. Každá instrukce, argument instrukce, rámec a proměnná jsou implementovány jako objekty. I když je většina zajímavého kódu uvnitř třídních funkcí, je zde i pár užitečných pomocných vně, například na zpracování argumentů programu, kontrolu formátu typu atributů nebo funkce na zpracování instrukce z vstupního xml do objektu instrukce. 

Základní myšlenkou je dvojí procházení instrukcí: první cyklus krok po kroku kvůli ověření návěští a uložení pozic o nich, druhé skutečné vykonávání programu.

### `ProcessSource` - inicializace

Při vytváření tohoto objektu se pomocí `xml.etree.ElementTree` nahraje vstupní XML, ověří zda jeho skladba odpovídá požadavkům a pro každý element instruction volá funkci na zpracování do objektu instrukce. Tyto objekty poté naváže do seznamu, kterým bude možné procházet pomocí indexu. Tento seznam seřadí podle atributu order a zkontroluje, zda-li neexistuje duplicitní nebo menší než 1. Vytváří se mnoho objektů, za zmínku stojí např. globální rámec a prázdný seznam na lokální rámce, zásobníky na volání a proměnné nebo slovník návěští.

### `ProcessSource` - pre_run

Funkce `do_pre_run` projde seznam instrukcí a u každé ověří, zda jsou její argumenty odpovídajích hodnot a typů. U instrukce LABEL uloží po ověření možné redefinice jméno návěští a index instrukce do slovníku návěští. U instrukcí s podmíněným či nepodmíněným skokem ukládá jméno do seznamu návěští pro pozdější kontrolu. Skončí-li procházení instrukcí v pořádku, ověří ještě, zda-li ke každému jménu návěští v seznamu existuje odpovídající návěští ve slovníku.

### `ProcessSource` - zpracování další instrukce

Pomocí `opcode` se spustí funkce pro danou instrukci a vykoná se vše potřebné. V hojném množství jsou využívány pomocné funkce, např. pro načtení hodnoty kde je povolen argument typu `symb` (kde může jít o proměnnou) nebo uložení hodnoty i s typem do proměnné. Šlo-li o instrukci skoku, ukládá se do indexu instrukcí nová hodnota.

## test.php
