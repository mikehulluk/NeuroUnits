


.PHONEY: all clean

all:

clean:
	rm -rf **/*.pyc
	rm -rf sphinx/_build/
	rm -rf src/_output/
	rm -rf src/testing/_output/
