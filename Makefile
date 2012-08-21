


.PHONEY: all clean force_look doc

all:
force_look:


examples: force_look
	make -C src/testing

doc: force_look
	make -C doc/ 

clean:
	# Documentation:
	make -C doc/ clean
	make -C src/ clean
	find . -name '*.new' -exec rm {} \;
	find . -name '*~' -exec rm {} \;
