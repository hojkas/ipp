<?php

class html {
  private $start, $start_b, $style, $start_c, $header, $results, $body, $end, $title;
  private $total_rc, $total_out, $good_rc, $good_out, $err_log;
  private $is_testing;
  public $out;

  public function __construct() {
    $this->total_rc = 0;
    $this->total_out = 0;
    $this->good_rc = 0;
    $this->good_out = 0;
    $this->is_testing = false;

    $this->start = "<!DOCTYPE html>\n<html>\n<head>\n<title>";
    $this->title = "untitled";
    $this->start_b = "</title>\n";
    $this->style = "<style>\n".
".header {
  padding: 10px;
  text-align: center;
  background: #1abc9c;
  color: white;
  font-size: 30px;
}
h2 {
  padding: 0px;
  margin: 5px;
}
table {
  width: 60%;
  border: 1px solid black;
  margin-left: auto;
  margin-right: auto;
  border-collapse: collapse;
  font-size: 20px;
}
th {
  height: 40px;
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
    $this->body .= "<table>\n";
  }

  private function count_results() {
    $this->results .= "<br/>\n";
    $this->center_result_header(2, "Správné návratové kódy:");
    $this->center_result_header(2, $this->good_rc."/".$this->total_rc);
    $this->center_result_header(2, "Správné výstupy:");
    $this->center_result_header(2, $this->good_out."/".$this->total_out."\n");
    $this->results .= "<br/>\n";
  }

  private function end_testing() {
    $this->body .= "</table>\n";
    if(!empty($this->err_log)) {
      $this->body .= $this->header(3, "Vrácené rozdíly:");
    }
  }

  public function add_result($name, $real_rc, $got_rc, $rc_good, $only_rc, $out_good, $error_log) {
    if(!$this->is_testing) {
      $this->start_testing();
      $is_testing = true;
    }

    $this->body .= "  <tr>\n    <th style=\"background-color:";
    if($rc_good && ($only_rc || $out_good)) $this->body .= "green\"";
    else $this->body .= "red\"";
    $this->body .= ">".$name."</th>\n";
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
    $this->t_dir = './';
    $this->p_dir = './';
    $this->i_dir = './';
    //TODO default merlin value
    $this->jexamxml = './jexamxml/jexamxml.jar';
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

    if($this->i_only && ($this->p_only || array_key_exists("parse-script")) || ($this->p_only && array_key_exists("int-script"))) {
      echo "Zakazana kombinace parametru: nelze omezit funkci pouze na parser nebo interpret ",
      "a zaroven uvest parametry pro ten druhy.\n";
      exit(10);
    }

    /*
    //TODO remove, just debug
    echo "--- DEBUG INFO\ntest dir: ", $t_dir, "\npars dir: ", $p_dir,
    "\ninte dir: ", $i_dir, "\njxml dir: ", $jexamxml, "\nrecursive:  ";
    if($rec) echo "Y\n"; else echo "N\n";
    echo "parse-only: ";
    if($p_only) echo "Y\n"; else echo "N\n";
    echo "int-only:   ";
    if($i_only) echo "Y\n"; else echo "N\n";
    echo "---\n\n";
    */
  }
}

//start of dead code
/*
function extract_files($files, $dir) {
  if(preg_match("/GENERATED/", $dir)) return $files; //radek vynechava slozku GENERATED
  $last = "";
  foreach (scandir($dir) as $file) {
      if ($file !== '.' && $file !== '..') {
        if(is_dir($dir.$file)) {
          $new_dir = $dir.$file."/";
          $files = extract_files($files, $new_dir);
        }
        else {
          $file = preg_replace("/\.(rc|out|src|in)$/", "", $file);
          if($last !== $file) {
            $files[] = $dir.$file;
            $last = $file;
          }
        }
      }
  }
  return $files;
}

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

//main
/*
$p = new params;
$p->check_args($argc, $argv);
*/
$html = new html;
$html->title("Test");
$html->add_result("testik", 2, 2, true, false, true, "nothing");
$html->add_result("read_simple", 2, 2, true, false, false, "nothing3");
$html->add_result("write_simple", 2, 2, true, true, false, "nothing2");
$html->finish();


?>
