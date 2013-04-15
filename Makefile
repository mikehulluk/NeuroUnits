


.PHONEY: all clean force_look doc

all:
force_look:


examples: force_look
	make -C src/testing

doc: force_look
	make -C doc/ 

clean:
	# Documentation:
	make -C spec/latex/ clean
	make -C doc/ clean
	make -C src/ clean
	find . -name '*.new' -exec rm {} \;
	find . -name '*.pyc' -exec rm {} \;
	find . -name '*.pyo' -exec rm {} \;
	find . -name '*~' -exec rm {} \;
	rm -rf tmp_out/

test_all:
	rm -fr tmp_out/
	mkdir tmp_out/
	#./bin/neurounits --validate --extract --extract-level=L1 --extract-to='L1.txt'  src/test_data/valid_l1.nuts
	#./bin/neurounits --validate --extract --extract-level=L2 --extract-to='L2.txt'  src/test_data/valid_l1.nuts
	#./bin/neurounits --validate --extract --extract-level=L3 --extract-to='L3.txt'  src/test_data/valid_l1.nuts
	
	
	make -C src/testing
	./bin/neurounits --validate  src/test_data/valid_l1.nuts
	./bin/neurounits --validate  src/test_data/thesis_l1.nuts

lint:
	rm -f pylint.html
	pylint neurounits --output-format=html  --rcfile=/home/michael/.pylintrc --reports=n --include-ids=y > pylint.html

