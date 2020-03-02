<?php

$xml = new XMLWriter();

$i_array = array(
  array("MOVE", "var", "symb"),
  array("CREATEFRAME"),
  array("PUSHFRAME"),
  array("POPFRAME"),
  array("DEFVAR", "var"),
  array("CALL", "label"),
  array("RETURN"),
  array("PUSHS", "symb"),
  array("POPS", "var"),
  array("ADD", "var", "symb", "symb"),
  array("SUB", "var", "symb", "symb"),
  array("MUL", "var", "symb", "symb"),
  array("IDIV", "var", "symb", "symb"),
  array("LG", "var", "symb", "symb"),
  array("GT", "var", "symb", "symb"),
  array("EQ", "var", "symb", "symb"),
  array("AND", "var", "symb", "symb"),
  array("OR", "var", "symb", "symb"),
  array("NOT", "var", "symb", "symb"),
  array("INT2CHAR", "var", "symb"),
  array("STRI2INT", "var", "symb", "symb"),
  array("READ", "var", "type"),
  array("WRITE", "symb"),
  array("CONCAT", "var", "symb", "symb"),
  array("STRLEN", "var", "symb"),
  array("GETCHAR", "var", "symb", "symb"),
  array("SETCHAR", "var", "symb", "symb"),
  array("TYPE", "var", "symb"),
  array("LABEL", "label"),
  array("JUMP", "label"),
  array("JUMPIFEQ", "label", "symb", "symb"),
  array("JUMPIFNEQ", "label", "symb", "symb"),
  array("EXIT", "symb"),
  array("DPRINT", "symb"),
  array("BREAK")
);

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
    public $eof_reached;
    private $elements;
    private $header;
    private $name;

    public function __construct() {
        $this->line_cnt = 0;
        $this->eof_reached = false;
        $this->header = false;
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
    * radek s hlavickou zahodi a nacita az dalsi
    * ignoruje prazdne radky
    * zahodi komentare
    * vytvori $elements s polem stringu (osekane o bile znaky)
    */
    public function next_line() {
        $this->line_cnt++;

        //cyklus starajici se o kontrolu hlavicky a jeji zahozeni
        while($this->header == false) {
            $line = fgets(STDIN);

            if($line === false) {
              fprintf(STDERR, "Chybejici nebo chybna hlavicka.\n");
              exit(21);
            }

            //rozdeleni nacteneho radku do pole stringu podle whitespace
            $line = trim($line);
            if(empty($line)) continue;

            $this->elements= preg_split('/\s+/', $line);
            $this->destroy_comments();

            if(sizeof($this->elements) == 0) continue;
            else if(preg_match("/^.[iI][pP][pP][cC][oO][dD][eE]20/", $this->elements[0]) && sizeof($this->elements) == 1) {
              $this->header = true;
              break;
            }
            else {
              fprintf(STDERR, "Chybejici nebo chybna hlavicka.\n");
              exit(21);
            }
        }

        //nacteni radku a zpracovani do $elements, while kvuli vyhozeni pripadnych prazdnych
        while(true) {
          $line = fgets(STDIN);
          if($line === false) {
            $this->eof_reached = true;
            return;
          }
          //rozdeleni nacteneho radku do pole stringu podle whitespace
          $line = trim($line);
          if(empty($line)) continue;
          $this->elements= preg_split('/\s+/', $line);
          $this->destroy_comments();

          if(sizeof($this->elements)) break;
        }
    }

    private function check_symb($index) {

    }

    private function check_var($index) {

    }

    private function check_label($index) {

    }

    /* Zkontroluje argumenty, aka položky 1 až n elements, a zpracuje do xml
    * volano exklusivne jen z process_instruction
    */
    private function process_arguments($key) {

    }

    /* Zkontroluje nazev instrukce,
    * vola kontrolu argumentu, generuje patricny xml kod
    */
    public function process_instruction() {
      global $xml;
      global $i_array;

      //overi existenci operacniho kodu dane instrukce a ulozi klic
      $this->elements[0] = strtoupper($this->elements[0]);
      $key = array_search($this->elements[0], array_column($i_array, '0'));
      if($key === false) {
        fprintf(STDERR, "Chybny nebo neznamy operacni kod: %s \n", $this->elements[0]);
        exit(22);
      }

      $xml->startElement('instruction');
      $xml->writeAttribute('order', $this->line_cnt);
      $xml->writeAttribute('opcode', $this->elements[0]);

      $this->process_arguments($key);

      $xml->endElement();
    }

}

check_args($argc, $argv);
start_xml($xml);

$i = new instruction;
$i->next_line();
while($i->eof_reached === FALSE) {
  $i->process_instruction();
  $i->next_line();
}

end_xml($xml);

?>
