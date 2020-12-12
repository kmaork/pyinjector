#include <Python.h>
PyMODINIT_FUNC PyInit_injection(void) { return NULL; }

#ifdef _WIN32
    #include <windows.h>
    #include <io.h>

    BOOL WINAPI DllMain(HINSTANCE hinstDLL, DWORD fdwReason, LPVOID lpReserved ) {
        const char *s = "Hello, world!";
        switch( fdwReason ) {
            case DLL_PROCESS_ATTACH:
                _write(1, s, strlen(s));
                _close(1);
                break;
        }
        return TRUE;
    }
#else
    static void init(void) __attribute__((constructor));

    static void init(void) {
        const char *s = "Hello, world!";
        write(1, s, strlen(s));
        close(1);
    }
#endif
