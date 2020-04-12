<?php
//xdg-open html

class html {
  private $start, $start_b, $style, $start_c, $header, $results, $body, $end, $title;
  private $total_rc, $total_out, $good_rc, $good_out, $err_log, $err_cnt;
  private $is_testing;
  public $out;

  public function __construct() {
    $this->total_rc = 0;
    $this->total_out = 0;
    $this->good_rc = 0;
    $this->good_out = 0;
    $this->is_testing = false;
    $this->err_cnt = 0;

    $this->start = "<!DOCTYPE html>\n<html>\n<head>\n<title>";
    $this->title = "untitled";
    $this->start_b = "</title>\n";
    $this->style = "<script>
function toggle() {
 if( document.getElementsByClassName(\"hidethis\").style.display=='none' ){
   document.getElementsByClassName(\"hidethis\").style.display = '';
 }else{
   document.getElementsByClassName(\"hidethis\").style.display = 'none';
 }
}
</script>
<style>\n".
".header {
  padding: 10px;
  text-align: center;
  background: #00ba06;
  color: white;
  font-size: 30px;
}
h2 {
  padding: 0px;
  margin: 5px;
}
code {
  background: #cfcfcf;
}
table {
  width: 80%;
  margin-left: auto;
  margin-right: auto;
  border-collapse: collapse;
  font-size: 20px;
  table-layout: fixed;
}
th {
  height: 40px;
  border: 2px solid black;
  border-collapse: collapse;
}
ul {
  margin-left: 30px;
  margin-right: 30px;
}
li {
  font-size: 20px;
  padding: 10px;
}
:target {
  -webkit-animation: target-fade 6s 1;
  -moz-animation: target-fade 6s 1;
}
@-webkit-keyframes target-fade {
    0% { background-color: #cfcfcf }
    100% { background-color: rgba(0,0,0,0); }
}
@-moz-keyframes target-fade {
    0% { background-color: #cfcfcf }
    100% { background-color: rgba(0,0,0,0); }
}
.meter {
  border: 2px solid black;
	height: 20px;
  width: 20%;
	background: #ff2200;
	-moz-border-radius: 25px;
	-webkit-border-radius: 25px;
}
.meter > span {
  display: block;
  height: 100%;
  border-top-right-radius: 8px;
  border-bottom-right-radius: 8px;
  border-top-left-radius: 20px;
  border-bottom-left-radius: 20px;
  background-color: #00ba06;
  position: relative;
  overflow: hidden;
}
}\n"
      ."</style>\n";
    $this->start_c = "</head>\n";
    $this->end = "</html>\n";
    $this->header = "<div class=\"header\">\n<h1 style=\"padding:0\">IPP projekt: Test</h1>".
    "\n<p style=\"font-size:20px\">Testováno ".
    date("d.m.y H:m")."</p>\n</div>\n";
    $this->results = "";
    $this->body = "";
    $err_log = "";
  }

  public function title($new) {
    $this->title = $new;
  }

  public function header($n, $header) {
    $this->body .= "<h".$n.">".$header."</h".$n.">\n";
  }

  public function center_header($n, $str) {
    $this->body .= "<h".$n." align=\"center\">".$str."</h".$n.">\n";
  }

  public function center_result_header($n, $str) {
    $this->results .= "<h".$n." align=\"center\">".$str."</h".$n.">\n";
  }

  private function start_testing() {
    $this->body .= "<p align=\"center\"><button onClick=\"toggle();\">Skrýt úspěšné testy</button></p>\n<table>\n".
    " <tr>\n    <th>Název</th>\n   <th>Správný rc</th>\n".
    "   <th>Správný output</th>\n     <th>Podrobněji chyby</th>\n </tr>\n";
  }

  private function count_results() {
    $this->results .= "<br/>\n";
    $this->center_result_header(2, "Správné návratové kódy:");
    if($this->total_rc == 0) {
      $this->center_result_header(2, "Žádné nebyly otestovány");
    }
    else {
      $this->center_result_header(2, $this->good_rc."/".$this->total_rc);
      $this->results .= "<div class=\"meter\" style=\"margin-left:auto; margin-right:auto\">\n  <span style=\"width: ".(($this->good_rc/$this->total_rc)*100)."%\"></span>\n</div>";
    }
    $this->center_result_header(2, "Správné výstupy:");
    if($this->total_out == 0) {
      $this->center_result_header(2, "Žádné nebyly otestovány");
    }
    else {
      $this->center_result_header(2, $this->good_out."/".$this->total_out."\n");
      $this->results .= "<div class=\"meter\" style=\"margin-left:auto; margin-right:auto\">\n  <span style=\"width: ".(($this->good_out/$this->total_out)*100)."%\"></span>\n</div>";
    }
    $this->results .= "<br/>\n";
  }

  private function end_testing() {
    $this->body .= "</table>\n";
    if(!empty($this->err_log)) {
      $this->body .= $this->header("2 style=\"margin-left:20px; margin-right:20px+\"", "Podrobněji chyby:");
      $this->err_log = "<ul>\n".$this->err_log."</ul>\n";
    }
  }

  public function add_param_info($param) {
    $ne_rec = "";
    if(! $param->rec) $ne_rec = "ne";
    $this->results .= "<br/>\n";
    $this->center_result_header(2, "Testování probíhá ze složky ".$param->t_dir.", ".$ne_rec."rekurzivně.");
    if($param->i_only) $this->center_result_header(2, "Interpret.py only.");
    else if($param->p_only) $this->center_result_header(2, "Parse.php only.");
    else $this->center_result_header(2, "Parse.php i intepret.py.");
  }

  public function add_result($name, $rc_good, $only_rc, $out_good, $error_log) {
    if(!$this->is_testing) {
      $this->start_testing();
      $this->is_testing = true;
    }

    $this->total_rc++;
    if($rc_good) $this->good_rc++;
    if(!$only_rc) {
      $this->total_out++;
      if($out_good) $this->good_out++;
    }

    $this->body .= "  <tr";
    $this->body .= "";
    if($rc_good && ($only_rc || $out_good)) $this->body .= " id=\"hidethis\">\n    <th style=\"background-color:#00ba06\"";
    else $this->body .= ">\n    <th style=\"background-color:#ff2200\"";
    $this->body .= ">".$name."</th>\n";

    if($rc_good) $this->body .= "   <th>ANO</th>\n";
    else $this->body .= "   <th style=\"font-color:#ff2200\">NE</th>";

    if($out_good) $this->body .= "   <th>ANO</th>\n";
    else if($only_rc) $this->body .= "   <th>-</th>\n";
    else $this->body .= "   <th style=\"color:#ff2200\">NE</th>\n";

    if(empty($error_log)) $this->body .= "    <th>-</th>\n";
    else {
      $this->err_cnt++;
      $this->err_log .= "<li id=\"err_".$this->err_cnt."\">".$this->err_cnt." ".$error_log."</li>\n";
      $this->body .= "    <th><a href=#err_".$this->err_cnt.">[".$this->err_cnt."]</th>";
    }

    $this->body .= "  </tr>\n";
  }

  public function finish() {
    $this->end_testing();
    $this->count_results();
    $this->out = $this->start.$this->title.$this->start_b.$this->style.$this->start_c."<body>\n".
    $this->header.$this->results.$this->body.$this->err_log."</body>\n".$this->end;
    echo $this->out;
  }
}

class params {
  public $t_dir, $p_dir, $i_dir, $jexamxml, $rec, $p_only, $i_only;

  public function __construct() {
    $this->t_dir = '';
    $this->p_dir = 'parse.php';
    $this->i_dir = 'interpret.py';
    //TODO default merlin value
    $this->jexamxml = 'jexamxml/jexamxml.jar';
    //$jexamxml = '/pub/courses/ipp/jexamxml/jexamxml.jar';

    $this->rec = false;
    $this->p_only = false;
    $this->i_only = false;
  }

  public function check_args($argc, $argv) {
    $long_opts = array("help", "directory:", "recursive", "parse-script:", "int-script:",
    "parse-only", "int-only", "jexamxml:");
    $opt = getopt(NULL, $long_opts);

    if(array_key_exists("help", $opt)) {
      //TODO real hlaseni
      echo "temp help text\n";
      exit(0);
    }

    if(array_key_exists("directory", $opt)) $this->t_dir = $opt["directory"];
    if(array_key_exists("recursive", $opt)) $this->rec = true;
    if(array_key_exists("parse-script", $opt)) $this->p_dir = $opt["parse-script"];
    if(array_key_exists("int-script", $opt)) $this->i_dir = $opt["int-script"];
    if(array_key_exists("parse-only", $opt)) $this->p_only = true;
    if(array_key_exists("int-only", $opt)) $this->i_only = true;
    if(array_key_exists("jexamxml", $opt)) $this->jexamxml = $opt["jexamxml"];

    if($this->i_only && ($this->p_only || array_key_exists("parse-script", $opt)) || ($this->p_only && array_key_exists("int-script", $opt))) {
      echo "Zakazana kombinace parametru: nelze omezit funkci pouze na parser nebo interpret ",
      "a zaroven uvest parametry pro ten druhy.\n";
      exit(10);
    }
  }
}

function extract_files($files, $dir, $rec) {
  //TODO delete this line
  if(preg_match("/GENERATED/", $dir)) return $files; //radek vynechava slozku GENERATED
  foreach (scandir($dir) as $file) {
      if ($file !== '.' && $file !== '..') {
        if(is_dir($dir.$file)) {
          if($rec) {
            $new_dir = $dir.$file."/";
            $files = extract_files($files, $new_dir, $rec);
          }
        }
        else {
          if(preg_match("/.src$/", $file)) {
            $file = preg_replace("/.src$/", "", $file);
            $files[] = $dir.$file;
          }
        }
      }
  }
  return $files;
}

//start of dead code
/*
function is_testable($file) {
  if(is_readable($file.".rc") && is_readable($file.".src")) return true;
  else return false;
}

function has_out($file) {
  if(is_readable($file.".out")) return true;
  else return false;
}

function test_one_rc($file) {
  global $error_log;
  exec('php parse.php <'.$file.'.src 2>/dev/null', $output, $rc);
  $real_rc = file_get_contents($file.'.rc');
  $real_rc = trim($real_rc);
  if($rc == $real_rc) return true;
  else {
    $error_log[] = 'Got '.$rc.' expected '.$real_rc.' in test '.$file;
    return false;
  }
}

//non working, stacks diffs
function test_one_out($file) {
  global $error_log;
  exec('php parse.php <'.$file.'.src >my_out 2>/dev/null', $output, $rc);
  $real_rc = file_get_contents($file.'.rc');
  $real_rc = trim($real_rc);
  exec('java -jar ./jexamxml/jexamxml.jar '.$file.'.out my_out diffs.xml -D ./jexamxml/options', $xml_out, $xml_rc);
  //var_dump($xml_rc);
  shell_exec('rm my_out');
  $xml_rc = trim($xml_rc);

  if($rc === $real_rc && $xml_rc === 0) return true;
  else {
    if($rc !== $real_rc) $error_log[] = 'Got '.$rc.' expected '.$real_rc.' in test '.$file;
    if($xml_rc !== 0) {
      if(is_readable('diffs.xml')) {
        $diffs = file_get_contents('diffs.xml');
        $error_log[] = 'XML was different: '.$diffs;
        shell_exec('rm diffs.xml');
      }
    }
    return false;
  }
}

function test_all($files) {
  global $error_log;
  $count = 0;
  $total = 0;
  $out = 0;
  $outable = 0;
  $size = sizeof($files);
  foreach($files as $file) {
    echo "\rTesting ", $total+1, " / ", $size;
    if(is_testable($file)) {
      if(has_out($file)) {
        if(test_one_out($file)) {
          $out++;
          $count++;
        }
        $outable++;
        $total++;
      }
      else {
        if(test_one_rc($file)) $count++;
        $total++;
      //}
    }
  }
  echo "\n";
  printf("Return codes:\n%d / %d\n", $count, $total);
  echo "ERR LOG:\n\n";
  foreach($error_log as $err) {
    echo $err, "\n";
  }
}*/
//end of dead code

class testing {
  private $files;
  private $files_i;
  private $files_n;
  private $p;
  private $html;

  public function __construct($p, $html) {
    $this->files = extract_files([],$p->t_dir, $p->rec);
    $this->files_n = sizeof($this->files);
    $this->files_i = 0;
    $this->p = $p;
    $this->html = $html;
  }

  private function test_one_as_ponly($file) {
    //TODO
    print("Parse only: ".$file."\n");
  }

  private function test_one_as_ionly($file) {
    $clean_in = false;
    $clean_out = false;
    $clean_rc = false;
    if(!file_exists($file.".in")) {
      $clean_in = true;
      shell_exec("touch ipp_testing_temp.in");
      $in = "ipp_testing_temp.in";
    }
    else {
      $in = $file.".in";
    }
    if(!file_exists($file.".out")) {
      $clean_out = true;
      shell_exec("touch ipp_testing_temp.out");
      $out = "ipp_testing_temp.out";
    }
    else {
      $out = $file.".out";
    }
    if(!file_exists($file.".rc")) {
      $clean_rc = true;
      shell_exec("echo \"0\" >ipp_testing_temp.rc");
      $rc = "ipp_testing_temp.rc";
    }
    else {
      $rc = $file.".rc";
    }
    //konec pripravy souboru

    //spusteni programu a porovnávání
    shell_exec("python3 ".$this->p->i_dir." --source=".$file.".src --input=".
    $in." >ipp_testing.out 2>ipp_testing_err_log; echo $? >ipp_testing.rc");
    $diff_rc = shell_exec("diff -w ipp_testing.rc ".$rc." >/dev/null; echo $?");

    if($diff_rc == 2) {
      fprint(STDERR, "Interni chyba diff u testu ".$file);
      goto clean_up;
    }

    //vytvori pouze filename bez cesty pro ucely vypisu
    $file_name = explode('/', $file);
    $file_name = end($file_name);

    $got_rc = shell_exec("cat ipp_testing.rc");
    if($diff_rc == 1) {
      $expected_rc = shell_exec("cat ".$rc);
      $err_log = "Očekáván návratový kód: <code>".$expected_rc.
      "</code> Skutečný návratový kód: <code>".$got_rc."</code>";
      $this->html->add_result($file_name, false, true, false, $err_log);
    }
    elseif($got_rc != 0) {
      $this->html->add_result($file_name, true, true, false, NULL);
    }
    else {
      //diff na rc probehl v poradku
      $diff_rc = shell_exec("diff ipp_testing.out ".$out." >/dev/null; echo $?");

      if($diff_rc == 2) {
        fprint(STDERR, "Interni chyba diff u testu ".$file);
        goto clean_up;
      }

      if($diff_rc == 1) {
        $expected_out = shell_exec("cat ".$out);
        $got_out = shell_exec("cat ipp_testing.out");
        $err_log = "Očekáván výstup: <code>".$expected_out.
        "</code> Skutečný výstup: <code>".$got_out."</code>";
        $this->html->add_result($file_name, true, false, false, $err_log);
      }
      else {
        //diff na out probehl v poradku
        $this->html->add_result($file_name, true, false, true, NULL);
      }
    }

    //vycisteni souboru
    clean_up:
    if(file_exists("ipp_testing_err_log")) shell_exec("rm ipp_testing_err_log");
    if(file_exists("ipp_testing.out")) shell_exec("rm ipp_testing.out");
    if(file_exists("ipp_testing.rc")) shell_exec("rm ipp_testing.rc");
    if($clean_in) shell_exec("rm ipp_testing_temp.in");
    if($clean_out) shell_exec("rm ipp_testing_temp.out");
    if($clean_rc) shell_exec("rm ipp_testing_temp.rc");
  }

  private function test_one_as_both($file) {
    $clean_in = false;
    $clean_out = false;
    $clean_rc = false;
    if(!file_exists($file.".in")) {
      $clean_in = true;
      shell_exec("touch ipp_testing_temp.in");
      $in = "ipp_testing_temp.in";
    }
    else {
      $in = $file.".in";
    }
    if(!file_exists($file.".out")) {
      $clean_out = true;
      shell_exec("touch ipp_testing_temp.out");
      $out = "ipp_testing_temp.out";
    }
    else {
      $out = $file.".out";
    }
    if(!file_exists($file.".rc")) {
      $clean_rc = true;
      shell_exec("echo \"0\" >ipp_testing_temp.rc");
      $rc = "ipp_testing_temp.rc";
    }
    else {
      $rc = $file.".rc";
    }
    //konec pripravy souboru

    //vytvori pouze filename bez cesty pro ucely vypisu
    $file_name = explode('/', $file);
    $file_name = end($file_name);
    $expected_rc = shell_exec("cat ".$rc);

    //spusteni programu a porovnávání
    shell_exec("php7.4 parse.php <".$file.".src >ipp_testing_mid.out; echo $? >ipp_testing_mid.rc");
    $diff_rc = shell_exec("diff -w ipp_testing_mid.rc ".$rc." >/dev/null; echo $?");

    if($diff_rc == 2) {
      fprint(STDERR, "Interni chyba diff u testu ".$file);
      goto clean_up;
    }

    $got_mid_rc = shell_exec("cat ipp_testing_mid.rc");
    if($diff_rc == 1) {
      if ($got_mid_rc != 0) {
        $err_log = "[chyba nastala již u parse.php] Očekáván návratový kód: <code>".$expected_rc.
        "</code> Skutečný návratový kód: <code>".$got_mid_rc."</code>";
        $this->html->add_result($file_name, false, true, false, $err_log);
        goto clean_up;
      }
    }
    elseif($got_mid_rc != 0) {
      $this->html->add_result($file_name, true, true, false, NULL);
      goto clean_up;
    }

    //testovani interpret.py, nemusi se sem dostat pokud uz parse vratil nenulovy rc
    shell_exec("python3 ".$this->p->i_dir." --source=ipp_testing_mid.out --input=".
    $in." >ipp_testing.out 2>ipp_testing_err_log; echo $? >ipp_testing.rc");
    $diff_rc = shell_exec("diff -w ipp_testing.rc ".$rc." >/dev/null; echo $?");
    $int_err = shell_exec("cat ipp_testing_err_log");

    if($diff_rc == 2) {
      fprint(STDERR, "Interni chyba diff u testu ".$file);
      goto clean_up;
    }

    $got_rc = shell_exec("cat ipp_testing.rc");
    if($diff_rc == 1) {
      $err_log = "Očekáván návratový kód: <code>".$expected_rc.
      "</code> Skutečný návratový kód: <code>".$got_rc."</code>";
      if(!empty($int_err)) $err_log .= "Chybové hlášení z interpretu: <code>".
        $int_err."</code>";
      if($got_rc == 31) {
        $mid_out = shell_exec("cat ipp_testing_mid.out");
        $err_log .= "XML vstup z parse.php nebyl v pořádku. XML:".
        " <code>".$mid_out."</code>";
      }
      $this->html->add_result($file_name, false, true, false, $err_log);
    }
    elseif($got_rc != 0) {
      $this->html->add_result($file_name, true, true, false, NULL);
    }
    else {
      //diff na rc probehl v poradku
      $diff_rc = shell_exec("diff ipp_testing.out ".$out." >/dev/null; echo $?");

      if($diff_rc == 2) {
        fprint(STDERR, "Interni chyba diff u testu ".$file);
        goto clean_up;
      }

      if($diff_rc == 1) {
        $expected_out = shell_exec("cat ".$out);
        $got_out = shell_exec("cat ipp_testing.out");
        $err_log = "Očekáván výstup: <code>".$expected_out.
        "</code> Skutečný výstup: <code>".$got_out."</code>";
        $this->html->add_result($file_name, true, false, false, $err_log);
      }
      else {
        //diff na out probehl v poradku
        $this->html->add_result($file_name, true, false, true, NULL);
      }
    }

    //vycisteni souboru
    clean_up:
    if(file_exists("ipp_testing_err_log")) shell_exec("rm ipp_testing_err_log");
    if(file_exists("ipp_testing.out")) shell_exec("rm ipp_testing.out");
    if(file_exists("ipp_testing.rc")) shell_exec("rm ipp_testing.rc");
    if(file_exists("ipp_testing_mid.rc")) shell_exec("rm ipp_testing_mid.rc");
    if(file_exists("ipp_testing_mid.out")) shell_exec("rm ipp_testing_mid.out");
    if($clean_in) shell_exec("rm ipp_testing_temp.in");
    if($clean_out) shell_exec("rm ipp_testing_temp.out");
    if($clean_rc) shell_exec("rm ipp_testing_temp.rc");
  }

  public function test() {
    //TODO delete this bit
    $total = sizeof($this->files);
    $count = 0;

    if(empty($this->files)) return;
    while($this->files_i < $this->files_n) {
      if($this->p->i_only) $this->test_one_as_ionly($this->files[$this->files_i]);
      else if($this->p->p_only) $this->test_one_as_ponly($this->files[$this->files_i]);
      else $this->test_one_as_both($this->files[$this->files_i]);
      $this->files_i++;

      //TODO delete after
      $count++;
      fprintf(STDERR, "Testing ".$count."/".$total."\r");
    }
  }
}

$p = new params;
$p->check_args($argc, $argv);

$html = new html;
$html->title("Test");
$html->add_param_info($p);

$testing = new testing($p, $html);
$testing->test();

$html->finish();

/*
$html->add_result("testik", true, false, true, "nothing");
$html->add_result("read_simple", true, false, false, NULL);
$html->add_result("write_simple", true, true, false, "nothing2");
$html->add_result("hey", true, true, false, "Hello this is a message, cool right? Return code was 1, but expected 0. That sucks, rigth?");
$html->add_result("testik", true, false, true, "nothing");
$html->add_result("read_simple", true, false, false, NULL);
$html->add_result("write_simple", true, true, false, "nothing2");
$html->add_result("testik", true, false, true, "nothing");
$html->add_result("read_simple",true, false, false, NULL);
$html->add_result("write_simple", true, true, false, "nothing2");
$html->add_result("testik", true, false, true, "nothing");
$html->add_result("read_simple", true, false, false, NULL);
$html->add_result("write_simple", true, true, false, "nothing2");
$html->add_result("testik", true, false, true, "nothing");
$html->add_result("read_simple", true, false, false, NULL);
$html->add_result("write_simple", true, true, false, "nothing2");
*/

?>
