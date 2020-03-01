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

            if($line == false) {
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
          if($line == false) {
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

    /* Zkontroluje argumenty, aka položky 1 až n elements, a zpracuje do xml
    * volano exklusivne jen z process_instruction
    */
    private process_arguments() {

    }

    public process_instruction() {


      $this->process_arguments();
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
while(! $i->eof_reached) {
  var_dump($i->elements);
  $i->next_line();
}

end_xml($xml);

?>
