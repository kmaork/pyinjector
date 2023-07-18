#include <Python.h>
PyMODINIT_FUNC PyInit_pyinjector_tests_injection(void) {return NULL;}

const char *MAGIC = "Let it be green\n";

#ifdef _WIN32
    #include <windows.h>
    #include <io.h>

    BOOL WINAPI DllMain(HINSTANCE hinstDLL, DWORD fdwReason, LPVOID lpReserved) {
        if (fdwReason == DLL_PROCESS_ATTACH) {
            _write(1, MAGIC, strlen(MAGIC));
        }
        return TRUE;
    }
#else
    __attribute__((constructor))
    static void init(void) {
        write(1, MAGIC, strlen(MAGIC));
    }
#endif
