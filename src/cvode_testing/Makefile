
all:
	g++ -o ./test_nineml.o -c  -Wno-write-strings  -fpermissive ./test_nineml.c
	g++ -o ./user_funcs.o -c   -Wno-write-strings ./user_funcs.c
	echo "Compilation OK!"
	g++ -o ./test_nineml test_nineml.o user_funcs.o -g -O2  /usr/lib/libsundials_cvode.a /usr/lib/libsundials_nvecserial.a -lm
	echo "Linking OK!"
