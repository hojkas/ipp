<?php
$error_log = array();

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

function test_all($files) {
  global $error_log;
  $count = 0;
  $total = 0;
  $size = sizeof($files) - 1;
  foreach($files as $file) {
    echo "\rTesting ", $total, " / ", $size;
    if(is_testable($file)) {
      if(test_one_rc($file)) $count++;
      $total++;
    }
  }
  echo "\n";
  printf("Return codes:\n%d / %d\n", $count, $total);
  echo "ERR LOG:\n\n";
  foreach($error_log as $err) {
    echo $err, "\n";
  }
}

check_args($argc, $argv);
//$rc = shell_exec('php parse.php <text.txt');
//echo "$rc\n"

//$dir = './ofi_tests/parse-only/';
$dir = './people_tests/parse-only/';
$files = array();
$files = extract_files($files, $dir);
test_all($files);


?>
