




import os
import string
import subprocess


class CCompilationSettings(object):



    def __init__(self, additional_include_paths=None, additional_library_paths=None, libraries=[], compile_flags=None ):

        self.additional_include_paths = additional_include_paths
        self.additional_library_paths = additional_library_paths
        self.libraries = libraries
        self.compile_flags = compile_flags



    @classmethod
    def default(self):
        return CCompilationSettings()






class CCompiler(object):


    @classmethod
    def prepare_to_create_file(cls, filename):
        output_dir = os.path.dirname(filename)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        if os.path.exists(filename):
            os.unlink(filename)


    @classmethod
    def build_executable(self,
                           src_text=None,
                           src_files=None,
                           compilation_settings = None,
                           run=False,
                           intermediate_filename='/tmp/nu/compilation/compile1.cpp',
                           output_filename = '/tmp/nu/compilation/exec.x'
                        ):

        # Only one form of input:
        assert  bool(src_text) != bool(src_files)
        compile_single_file = bool(src_text)


        if compilation_settings is None:
            compilation_settings = CCompilationSettings.default()


        # Write the src_text to a file:
        if compile_single_file:
            CCompiler.prepare_to_create_file(intermediate_filename)
            with open( intermediate_filename,'w') as f:
                f.write(src_text)
            src_files = [intermediate_filename]
            src_text = None

        # Ensure we can write to the output-files:
        CCompiler.prepare_to_create_file(output_filename)



        # OK, lets compile!
        compilation_dict = {
            'CC': 'g++',
            'INPUT_FILES' : ' '.join(src_files),
            'CXX_FLAGS' :   ' '.join(compilation_settings.compile_flags),
            'CXX_INCL_PATHS' : ' '.join(['-I'+ a for a in compilation_settings.additional_include_paths]),
            'CXX_LIB_PATHS' : ' '.join(['-L'+ a for a in compilation_settings.additional_library_paths]),
            'CXX_LIBS' : ' '.join(['-l'+ a for a in compilation_settings.libraries]),
            'OUTPUT_FILE' : output_filename,
        }


        compilation_string = string.Template("""${CC} -o ${OUTPUT_FILE} ${INPUT_FILES} ${CXX_FLAGS} ${CXX_INCL_PATHS} ${CXX_LIB_PATHS} ${CXX_LIBS} """).substitute(compilation_dict)

        print 'Compiling:'
        print compilation_string
        subprocess.check_call(compilation_string, shell=True)
        print 'Compilation sucessful'

        if run:
            LD_LIB_PATH = 'export LD_LIBRARY_PATH="%s:$LD_LIBRARY_PATH"' % ':'.join(compilation_settings.additional_library_paths)
            exec_cmd = LD_LIB_PATH + "; " + os.path.abspath( output_filename )
            print 'Running:', exec_cmd
            subprocess.check_call(exec_cmd, shell=True)

