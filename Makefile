


.PHONEY: help



lint: 
	pylint
clean:
	@echo "Cleaning out temp-files"
	@rm -rfv mhutils.egg-info
	@rm -rfv src/mhutils.egg-info
	@find . -name "*.pyc" -exec rm -v  {} \;

lint:
	#-pylint --include-ids=y --output-format=html `find src -name "*.py"`  > out.html
	-pylint  --output-format=html `find src -name "*.py"`  > out.html

help:
	@echo "                                    "
	@echo "      Welcome to Neurounits         "
	@echo "      ---------------------         "
	@echo "Please use:                         "
	@echo "scons"
    



