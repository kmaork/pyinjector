#include <Python.h>
PyMODINIT_FUNC PyInit_pyinjector_tests_injection(void) {return NULL;}

const char *MAGIC = "Let it be green\n";

/* A trivial exported function used to test the remote-call API. */
#if defined(_WIN32)
__declspec(dllexport)
#else
__attribute__((visibility("default")))
#endif
int pyinjector_tests_injection_answer(void) { return 42; }

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
