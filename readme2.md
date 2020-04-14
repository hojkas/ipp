# Implementační dokumentace k 1. úloze do IPP 2019/2020

Jméno a příjmení: Iveta Strnadová

Login: xstrna14

## interpret.py

Pro interpretaci je zásadní třída `ProcessSource`. Každá instrukce, argument instrukce, rámec a proměnná jsou implementovány jako objekty. I když je většina zajímavého kódu uvnitř třídních funkcí, je zde i pár užitečných pomocných vně, například na zpracování argumentů programu, kontrolu formátu typu atributů nebo funkce na zpracování instrukce z vstupního xml do objektu `Instruction`. 

Základní myšlenkou je projít instrukce dvakrát: první cyklus ověří existenci všech volaných návěští a uloží jejich pozice, druhý již opravdu vykonává program (včetně případných skoků).

Z hlavního těla programu je `ProcessSource` inicializováno, zavolána jeho funkce na pre-run a poté v cyklu volána funkce na zpracování další instrukce dokud nevrátí false.

### `ProcessSource` - inicializace

Při vytváření tohoto objektu skript pomocí `xml.etree.ElementTree` nahraje vstupní XML, ověří, zda jeho skladba odpovídá požadavkům, a pro každý element instruction volá funkci na zpracování do objektu instrukce. Tyto objekty poté naváže do seznamu, kterým bude možné procházet pomocí indexu. Tento seznam seřadí podle atributu order a zkontroluje, zda-li neexistuje duplicitní nebo menší než 1. Vytváří se mnoho objektů, za zmínku stojí např. globální rámec a prázdný seznam na lokální rámce, zásobníky na volání a proměnné nebo slovník návěští.

### `ProcessSource` - pre_run

Funkce `do_pre_run` projde seznam instrukcí a u každé ověří, zda jsou její argumenty odpovídajích hodnot a typů. U instrukce LABEL uloží po ověření možné redefinice jméno návěští a index instrukce do slovníku návěští. U instrukcí s podmíněným či nepodmíněným skokem ukládá jméno do seznamu návěští pro pozdější kontrolu. Skončí-li procházení instrukcí v pořádku, ověří ještě, zda-li ke každému jménu návěští v seznamu existuje odpovídající návěští ve slovníku.

### `ProcessSource` - zpracování další instrukce

Pomocí `opcode` se spustí funkce pro danou instrukci a vykoná se vše potřebné. V hojném množství jsou využívány pomocné funkce, např. pro načtení hodnoty z argumentu povolujícím typ `symb` (kde může jít o proměnnou či přímo hodnotu) nebo uložení hodnoty i s typem do proměnné. Šlo-li o instrukci se skokem, ukládá se do indexu instrukcí nová hodnota.

Za zmínku stojí, že každá funkce na zpracování instrukce má dvě části, první se spustí při pre-run, druhá při vlastní interpretaci. Z hlediska programu samotného není důvod mít je u sebe, ale díky tomuto uspořádání bylo snazší mít přehled o umístění potřebných kontrol argumentů funkce.

## test.php

Test zpracuje argumenty a použije dané zdroje na otestování a vytvoření přehledné html stránky. Většina funkcionality je řešena v třech základních třídách. Krom nich existuje ještě pomocná funkce na extrahování jmen souborů i s cestou do připraveného pole, které získá procházením zadaného adresáře.

Třída `params` zpracuje a uloží parametry skriptu tak, aby byly snadno dostupné a použitelné přímo v kódu. K tomu provede potřebná ověření jejich správnosti.

`html` se stará o vytváření výsledného html souboru. Již obsahuje kostru, do níž pouze vloží výsledky testů na základě opakovaného volání funkce `add_result` s parametry obsahujícími informace o správnosti testu.

O testování samotné se stará třída `testing`. Nad extrahovanými soubory opakovaně volá jednu z funkcí na provedení testu (podle toho, zda jde o testování pouze interpretu, parseru, nebo obou). Všechny tři funkce na začátku zjistí, zda-li existují soubory které potřebují (.out, .rc, krom parse-only i .in) a pokud ne, vytvoří si je s potřebnými hodnotami. Na konci vyčistí všechny soubory, co si vytvořily, včetně souborů pro mezivýstupy k porovnání.

### Parse-only

Nechá zadaný soubor s parse skriptem zpracovat .src soubor. Je-li návratový kód 0 a měl-li být této hodnoty, porovná navíc výstup s referenčním pomocí nástroje `JExamXML`. Bez ohledu na výsledek je volána funkce `add_result` s informacemi o úspěšnosti porovnání a případných nesrovnalostech.

### Int-only

Stejně jako v předchozím případě spustí program s daným vstupem a zkontroluje návratový kód. Narozdíl od parse-only na případné porovnání očekávaného výstupu se skutečným využívá nástroj `diff`.

### Parse i interpret

Neprve je použit na zpracování skript parse a výsledek uložen do dočasného souboru. Byl-li návratový kód 0, je spuštěn interpret s tímto vstupem a opět probíhá porovnání návratového kódu a výsledku (pomocí `diff`).
