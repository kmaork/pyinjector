#include <Python.h>
PyMODINIT_FUNC PyInit_pyinjector_tests_injection(void) {return NULL;}

#ifdef _WIN32
    #include <windows.h>
    #include <io.h>

    const char *MAGIC = "Hello, world!";

    BOOL WINAPI DllMain(HINSTANCE hinstDLL, DWORD fdwReason, LPVOID lpReserved) {
        if (fdwReason == DLL_PROCESS_ATTACH) {
            _write(1, MAGIC, strlen(MAGIC));
            _close(1);
        }
        return TRUE;
    }
#else
    __attribute__((constructor))
    static void init(void) {
        const char *s = "Hello, world!";
        write(1, s, strlen(s));
        close(1);
    }
#endif
