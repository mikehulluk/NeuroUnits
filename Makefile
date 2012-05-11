


.PHONEY: all clean force_look doc

all:
force_look:


examples: force_look
	make -C src/testing

doc: force_look
	make -C doc/ 

clean:
	# Source Code:
	#find . -name "*.pyc" -exec rm {} \;

	# Documentation:
	make -C doc/ clean
	make -C src/ clean
