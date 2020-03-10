<?php
function check_args($argc, $argv) {
    /*$opt = getopt(NULL, array("help"));
    var_dump($opt);*/
    if($argc == 2 && (strcmp($argv[1], "--parse-only") == 0)) {
        return;
    }
    else {
      fprintf(STDERR, "test.php zatim podporuje pouze parse-only\n");
      exit(0);
    }
}

function extract_files($files, $dir) {
  $last = "";
  foreach (scandir($dir) as $file) {
      if ($file !== '.' && $file !== '..') {
        if(is_dir($dir.$file)) {
          $new_dir = $dir.$file."/";
          $files = extract_files($files, $new_dir);
        }
        else {
          $file = preg_replace("/\.(rc|out|src)$/", "", $file);
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

function test_one($file) {
  $rc = shell_exec('php parse.php <'.$file.'.src');
  $real_rc = file_get_contents($file.'.rc');
  $real_rc = trim($real_rc);
  printf("my rc: %d\nreal rc: %d\n", $rc, $real_rc);
  if($rc === $real_rc) return true;
  else return false;
}

function test_all($files) {
  $count = 0;
  $total = 0;
  foreach($files as $file) {
    if(is_testable($file)) {
      if(test_one($file)) $count++;
      $total++;
    }
  }
  printf("Return codes:\n%d / %d\n", $count, $total);
}

check_args($argc, $argv);
//$rc = shell_exec('php parse.php <text.txt');
//echo "$rc\n"

$dir = './ofi_tests/parse-only/';
$files = array();
$files = extract_files($files, $dir);
test_all($files);


?>
