#!/bin/bash

if [ "$1" == "parse" ]
then
	#echo "parse"
	php parse.php <text >src
elif [ "$1" == "all" ]
then
	#echo "all"
	php parse.php <text >src
	python3 interpret.py --source=src --input=i
elif [ "$1" == "int" ]
then
	#echo "int"
	python3 interpret.py --source=src --input=i
else
	if [ "$1" == "in" ]
	then
		php parse.php <$2.src | python3 interpret.py --input=$2.in >my_out
		$my_rc="$?"
	else
		touch temp_input
		php parse.php <$2.src | python3 interpret.py --input=temp_input >my_out
		$my_rc="$?"
		rm temp_input
	fi
	echo "Real rc: "
	cat $2.rc
	echo "My rc: "
	echo "$my_rc"
	diff -s my_out $2.out >diff
	echo "DIFF
"
	echo "$diff"
fi
