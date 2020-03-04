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

check_args($argc, $argv);
$rc = shell_exec('php parse.php <text.txt');
echo "$rc\n";

?>
