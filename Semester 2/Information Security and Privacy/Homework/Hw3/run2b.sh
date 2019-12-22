#!/bin/bash

files=`ls dicts`

for file in $files; do
	echo $file
	python ex2b.py dicts/$file
done
