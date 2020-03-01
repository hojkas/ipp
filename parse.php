<?php

$xml = new XMLWriter();

function check_args($argc, $argv) {
    /*$opt = getopt(NULL, array("help"));
    var_dump($opt);*/
    if($argc == 2 && (strcmp($argv[1], "--help") == 0)) {
        echo "Skript typu filtr nacte ze standardniho vstupu zdrojovy kod v IPPcode20,
zkontroluje lexikalni a syntaktickou spravnost kodu a vypise\nna standardni výstup XML reprezentaci programu dle specifikace.\n";
        exit(0);
    }
    else if($argc == 1) return;
    fprintf(STDERR, "Chybna kombinace parametru.\n");
    exit(10);
}

//Zacataek xml dokumentu
function start_xml($xml) {
    $xml->openUri('php://output');
    $xml->startDocument('1.0', 'UTF-8');
    $xml->startElement('program');
    $xml->startAttribute('language');
    $xml->text('IPPcode20');
    $xml->endAttribute();
    $xml->setIndent(true);
}

//Ukonceni xml dokumentu
function end_xml($xml) {
    $xml->endElement();
    $xml->endDocument();
}

//Trida na zpracovani instrukci
class instruction {
    public $line_cnt;
    public $name;
    public $args;

    public $elements;

    public function __construct() {
        $this->line_cnt = 0;
    }

    /* Odstrani komentare z elements array
    */
    private function destroy_comments() {
      $found = false;
      $index = 0;
      foreach($this->elements as $word) {
        if($word[0] == '#') {
          $found = true;
          break;
        }
        $index++;
      }
      if($found) array_splice($this->elements, $index);
    }

    /* Nacte dalsi radek ze stdout
    */
    public function next_line() {
        $this->line_cnt++;
        $line = fgets(STDIN);
        $header = false;

        while($header == false) {
            if($line == false && $this->line_cnt == 1) {
                fprintf(STDERR, "Zadan prazdny soubor.\n");
                exit(21);
            }

            //rozdeleni nacteneho radku do pole stringu podle whitespace
            $line = trim($line);
            $this->elements= preg_split('/\s+/', $line);
            $this->destroy_comments();/*
            while(empty($this->elements)) {
              if(empty($line))
            }*/
            var_dump($this->elements);
        }
    }


}

check_args($argc, $argv);
start_xml($xml);




/*
$xml->startElement('instruction');
$xml->text('yes');
$xml->setindent(true);
$xml->startAttribute('in');
$xml->text('yes');
$xml->endAttribute();
$xml->endElement();*/

$i = new instruction;
$i->next_line();
$i->next_line();

end_xml($xml);

?>
