# Implementační dokumentace k 1. úloze do IPP 2019/2020

Jméno a příjmení: Iveta Strnadová

Login: xstrna14

Na vypisování xml formátu se používá `XMLWriter`. Celý skript se sestává z ověření argumentů, vytvoření začátku dokumentu xml, volání funkcí třídy `instruction` a ukončení xml dokumentu. V případě nalezení argumentu `--help` skript vypíše nápovědu a skončí.

## Třída `instruction`

Třída obsahuje proměnné a funkce potřebné ke zpracování vstupu na xml kód. Využívá výše zmíněný XMLWriter a dvojrozměrné pole instrukcí a jejich požadovaných argumentů definované na začátku skriptu. Pouze její konstruktor, `next_line` a `process_instruction` jsou veřejné funkce, zbylé jsou volány pouze z jiných instrukcí této třídy. Z hlavního těla programu je využívána opakovaným voláním `next_line` a `process_instruction` v tomto pořadí, dokud není stdin prázdný.

### `next_line`

Po zavolání načte do proměnné `elements` platný řádek instrukce a rozdělí na pole podle bílých znaků. Pokud ještě nebyla nalezena hlavička, nejprve ověřuje její přítomnost a případně vrací chybu. Zároveň odstraňuje komentáře pomocí funkce `destroy_comments`. Nemá-li co načítat, nastavuje proměnnou `eof_reached`.

### `process_instruction`

Funkce podle první položky `elements` rozhodne, zda se jedná o platnou instrukci IPPcode20 a pokud ano, volá funkci na zpracování argumentů. Zároveň vytváří xml zápis pro instrukci.

Následuje `process_arguments`, která podle připraveného pole vyhledá žádané typy argumentů pro nalezenou instrukci. Pro každý z nich volá patřičnou funkci `check_var`, `check_label` nebo `check_symb` (v případě argumentu tvaru `type` proběhne ověření již zde). Tyto funkce pomocí regulárních výrazů ověří, zda se jedná o požadovaný tvar argumentu. V případě, že argument nesplňuje podmínky pro instrukci nebo `elements` obsahuje nevhodný počet položek, skript vrací odpovídající chybový kód a končí ve zpracování. Kromě kontroly se zde také provádí generování žádaného xml formátu z informací argumentů.
