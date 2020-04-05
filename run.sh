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
fi
