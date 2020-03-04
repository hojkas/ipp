<?php

$xml = new XMLWriter();

$i_array = array(
  array("MOVE",       "var", "symb"),
  array("CREATEFRAME"),
  array("PUSHFRAME"),
  array("POPFRAME"),
  array("DEFVAR",     "var"),
  array("CALL",       "label"),
  array("RETURN"),
  array("PUSHS",      "symb"),
  array("POPS",       "var"),
  array("ADD",        "var", "symb", "symb"),
  array("SUB",        "var", "symb", "symb"),
  array("MUL",        "var", "symb", "symb"),
  array("IDIV",       "var", "symb", "symb"),
  array("LG",         "var", "symb", "symb"),
  array("GT",         "var", "symb", "symb"),
  array("EQ",         "var", "symb", "symb"),
  array("AND",        "var", "symb", "symb"),
  array("OR",         "var", "symb", "symb"),
  array("NOT",        "var", "symb"),
  array("INT2CHAR",   "var", "symb"),
  array("STRI2INT",   "var", "symb", "symb"),
  array("READ",       "var", "type"),
  array("WRITE",      "symb"),
  array("CONCAT",     "var", "symb", "symb"),
  array("STRLEN",     "var", "symb"),
  array("GETCHAR",    "var", "symb", "symb"),
  array("SETCHAR",    "var", "symb", "symb"),
  array("TYPE",       "var", "symb"),
  array("LABEL",      "label"),
  array("JUMP",       "label"),
  array("JUMPIFEQ",   "label", "symb", "symb"),
  array("JUMPIFNEQ",  "label", "symb", "symb"),
  array("EXIT",       "symb"),
  array("DPRINT",     "symb"),
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
    private $last_type;

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

            $line = preg_replace("/#/", " #", $line);
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
          $line = preg_replace("/#/", " #", $line);
          $this->elements= preg_split('/\s+/', $line);
          $this->destroy_comments();

          if(sizeof($this->elements)) break;
        }
    }

    private function check_symb($index, $can_be_nil) {
      //kontrola zdaůli jde o promennou
      if(preg_match("/^(G|T|L)F@[a-zA-Z_\-$&%\*!\?][a-zA-Z0-9_\-$&%\*!\?]*$/", $this->elements[$index])) {
        $this->last_type = "var";
        return;
      }
      //jde-li o cisty nil
      else if(preg_match("/^nil@nil/", $this->elements[$index])) {
        $this->last_type = "nil";
        $this->elements[$index] = preg_replace("/^nil@/", "", $this->elements[$index]);
        return;
      }
      //kontrola zda-li jde o bool
      else if(preg_match("/^bool@/", $this->elements[$index])) {
        $this->last_type = "bool";
        if(preg_match("/^bool@(true|false)$/", $this->elements[$index])) {
          $this->elements[$index] = preg_replace("/^bool@/", "", $this->elements[$index]);
          return;
        }
        else {
          if(preg_match("/^bool@nil$/", $this->elements[$index]) === false && $can_be_nil) {
            $this->elements[$index] = preg_replace("/^bool@/", "", $this->elements[$index]);
          }
          fprintf(STDERR, "Chybna hodnota boolu v %s.\n", $this->elements[$index]);
          exit(22);
        }
      }
      //kontrola int
      else if(preg_match("/^int@/", $this->elements[$index])) {
        $this->last_type = "int";
        if(preg_match("/^int@(\-|\+)?(\d)+$/", $this->elements[$index]) === false) {
          if(preg_match("/^int@nil$/", $this->elements[$index]) === false && $can_be_nil === true) {
            $this->elements[$index] = preg_replace("/^int@/", "", $this->elements[$index]);
            return;
          }
          fprintf(STDERR, "Chybna hodnota int v %s.\n", $this->elements[$index]);
          exit(22);
        }
        $this->elements[$index] = preg_replace("/^int@/", "", $this->elements[$index]);
      }
      //kontrola retezce
      else if(preg_match("/^string@/", $this->elements[$index])) {
        $this->last_type = "string";
        if(preg_match("/^string@[([^#\s\\]|(\\\d{3}))]+$/", $this->elements[$index]) === false) {
          if(preg_match("/^string@nil$/", $this->elements[$index]) === false && $can_be_nil) return;
          fprintf(STDERR, "Chybna hodnota string v %s.\n", $this->elements[$index]);
          exit(22);
        }
        else {
          //je-li retezec ok, jeste je treba upravit znaky co jsou specificke pro xml
          $this->elements[$index] = preg_replace("/^string@/", "", $this->elements[$index]);
          $this->elements[$index] = preg_replace("/&/", "@amp;", $this->elements[$index]);
          $this->elements[$index] = preg_replace("/>/", "&lt;", $this->elements[$index]);
          $this->elements[$index] = preg_replace("/</", " &gt;", $this->elements[$index]);
        }
      }
      //pokud nevyhovuje ani jednomu
      else {
        fprintf(STDERR, "Chybna syntax %s, ocekavana promenna nebo dobre formatovana hodnota.\n", $this->elements[$index]);
        exit(22);
      }
    }

    private function check_var($index) {
      if(preg_match("/^(G|T|L)F@[a-zA-Z_\-$&%*!?][a-zA-Z0-9_\-$&%*!?]*$/", $this->elements[$index]) == false) {
        fprintf(STDERR, "Promenna %s nevyhovuje pozadavkum.\n", $this->elements[$index]);
        exit(22);
      }
    }

    private function check_label($index) {
      if(preg_match("/^[a-zA-Z_\-$&%*!?][a-zA-Z0-9_\-$&%*!?]*$/", $this->elements[$index]) == false) {
        fprintf(STDERR, "Navesti (label) %s nevyhovuje pozadavkum.\n", $this->elements[$index]);
        exit(22);
      }
    }

    /* Zkontroluje argumenty, aka položky 1 až n elements, a zpracuje do xml
    * volano exklusivne jen z process_instruction
    */
    private function process_arguments($key) {
      global $xml;
      global $i_array;

      if(sizeof($i_array[$key]) != sizeof($this->elements)) {
        fprintf(STDERR, "Chybny pocet argumentu dane instrukce %s, ocekavano %d argumentu.\n",
        $this->elements[0], sizeof($i_array[$key]) - 1);
        exit(22);
      }

      if(sizeof($i_array[$key]) == 1) return; //zadny operand, vse ok

      //kontrola a zpracovani prvniho argumentu
      if(strcmp($i_array[$key][1], "var") === 0) {
        /*placeholder na specialni pripady
        */
        $this->check_var(1);
        $xml->startElement('arg1');
        $xml->writeAttribute('type', 'var');
        $xml->text($this->elements[1]);
        $xml->endElement();
      }
      else if(strcmp($i_array[$key][1], "symb") === 0) {
        $this->check_symb(1, true);
        $xml->startElement('arg1');
        $xml->writeAttribute('type', $this->last_type);
        $xml->text($this->elements[1]);
        $xml->endElement();
      }
      else if(strcmp($i_array[$key][1], "label") === 0) {
        /*placeholder na specialni pripady
        */
        $this->check_label(1);
        $xml->startElement('arg1');
        $xml->writeAttribute('type', 'label');
        $xml->text($this->elements[1]);
        $xml->endElement();
      }
      else {
        fprintf(STDERR, "! Sem se to dostat nemelo\n");
      }
      if(sizeof($i_array[$key]) == 2) return;

      //kontrola a zpracovani druheho argumentu
      if(strcmp($i_array[$key][2], "type") === 0) {
        //tady trochu weird, boola prochází, vše prochází TODO
        if(preg_match("/^(int|bool|string)$/", $this->elements[2]) === false) {
          fprintf(STDERR, "Nepovoleny type (zadano %s).\n", $this->elements[2]);
          exit(22);
        }
        $xml->startElement('arg2');
        $xml->writeAttribute('type', 'type');
        $xml->text($this->elements[2]);
        $xml->endElement();
      }
      else {
        //bylo to symb
        $this->check_symb(2, true);
        $xml->startElement('arg2');
        $xml->writeAttribute('type', $this->last_type);
        $xml->text($this->elements[2]);
        $xml->endElement();
      }
      if(sizeof($i_array[$key]) == 3) return;

      //treti argument
      //existuje, jinak bychom se sem nedostali, takze je symb bez kontroly
      $this->check_symb(3, true);
      $xml->startElement('arg3');
      $xml->writeAttribute('type', $this->last_type);
      $xml->text($this->elements[3]);
      $xml->endElement();
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
