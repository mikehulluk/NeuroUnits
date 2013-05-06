

all:
	g++ -o ./out1.o -c -Wfatal-errors -std=c++0x  -Wno-write-strings  -fpermissive ./out1.c
	#g++ -o ./user_funcs.o -c   -Wno-write-strings ./user_funcs.c
	echo "Compilation OK!"
	g++ -o ./out1 out1.o -g -O2  /usr/lib/libsundials_cvode.a /usr/lib/libsundials_nvecserial.a -lm
	echo "Linking OK!"
