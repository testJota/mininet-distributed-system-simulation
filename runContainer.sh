#!/bin/bash

if [ $# -ne 1 ]; then
	echo "Must receive one argument, more information in readMe"
	exit 1
else
	docker run --rm --privileged -v `pwd`:`pwd` -w `pwd` mininet-container \
		 bash /home/vmFiles/run.sh $1
fi

#docker run -ti --rm --privileged mininet-container /bin/bash
