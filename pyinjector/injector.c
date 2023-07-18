#include <Python.h>
#include <stddef.h>
#include "injector.h"
#include <structmember.h>

static PyObject *InjectorException;

typedef struct {
    PyObject_HEAD
    injector_t *injector;
} Injector;

void Injector_raise(char* func_name, int result)
{
    PyObject* error_args = Py_BuildValue("sis", func_name, result, injector_error());
    PyErr_SetObject(InjectorException, error_args);
    Py_DECREF(error_args);
}

static PyObject *Injector_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    Injector *self = (Injector *)type->tp_alloc(type, 0);
    if (self == NULL) {
        return NULL;
    }
    self->injector = NULL;
    return (PyObject *)self;
}

static PyObject *Injector_attach(Injector *self, PyObject *args)
{
    injector_pid_t pid;
    int result;

    if (!PyArg_ParseTuple(args, "i", &pid)) {
        return NULL;
    }

    result = injector_attach(&(self->injector), pid);
    if (result != INJERR_SUCCESS) {
        Injector_raise("injector_attach", result);
        return NULL;
    }

    Py_RETURN_NONE;
}

static PyObject *Injector_inject(Injector *self, PyObject *args)
{
    Py_buffer path_buffer;
    void *handle;
    int result;

    if (!PyArg_ParseTuple(args, "y*", &path_buffer)) {
        return NULL;
    }

    result = injector_inject(self->injector, path_buffer.buf, &handle);
    PyBuffer_Release(&path_buffer);
    if (result != INJERR_SUCCESS) {
        Injector_raise("injector_inject", result);
        return NULL;
    }

    return PyLong_FromVoidPtr(handle);
}

#if defined(__APPLE__) || defined(__linux)
static PyObject *Injector_call(Injector *self, PyObject *args)
{
    void *handle;
    const char *name;
    int result;

    if (!PyArg_ParseTuple(args, "Ks", &handle, &name)) {
        return NULL;
    }

    result = injector_call(self->injector, handle, name);
    if (result != INJERR_SUCCESS) {
        Injector_raise("injector_call", result);
        return NULL;
    }

    Py_RETURN_NONE;
}
#endif

static PyObject *Injector_uninject(Injector *self, PyObject *args)
{
    void *handle;
    int result;

    if (!PyArg_ParseTuple(args, "K", &handle)) {
        return NULL;
    }

    result = injector_uninject(self->injector, handle);
    if (result != INJERR_SUCCESS) {
        Injector_raise("injector_uninject", result);
        return NULL;
    }

    Py_RETURN_NONE;
}

static PyObject *Injector_detach(Injector *self, PyObject *args)
{
    int result = injector_detach(self->injector);
    if (result != INJERR_SUCCESS) {
        Injector_raise("injector_detach", result);
        return NULL;
    }
    // injector_detach frees the injector
    self->injector = NULL;
    Py_RETURN_NONE;
}

static PyMethodDef Injector_methods[] = {
    {"attach", (PyCFunction)Injector_attach, METH_VARARGS, "Attach the injector to a process."},
    {"inject", (PyCFunction)Injector_inject, METH_VARARGS, "Inject a shared library into the process."},
    #if defined(__APPLE__) || defined(__linux)
    {"call", (PyCFunction)Injector_call, METH_VARARGS, NULL},
    #endif
    {"uninject", (PyCFunction)Injector_uninject, METH_VARARGS, "Uninject a previously injected library."},
    {"detach", (PyCFunction)Injector_detach, METH_NOARGS, "Detach the injector from the process."},
    {NULL}  /* Sentinel */
};

static PyTypeObject InjectorType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "injector.Injector",
    .tp_doc = "Low level wrapper for injector functions",
    .tp_basicsize = sizeof(Injector),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_new = Injector_new,
    .tp_methods = Injector_methods,
};

static PyModuleDef injectormodule = {
    PyModuleDef_HEAD_INIT,
    .m_name = "injector",
    .m_doc = "Python wrapper for the injector library.",
    .m_size = -1,
};

PyMODINIT_FUNC PyInit_injector(void)
{
    PyObject* m;

    if (PyType_Ready(&InjectorType) < 0)
        return NULL;

    m = PyModule_Create(&injectormodule);
    if (m == NULL)
        return NULL;

    Py_INCREF(&InjectorType);
    if (PyModule_AddObject(m, "Injector", (PyObject *)&InjectorType) < 0) {
        Py_DECREF(&InjectorType);
        Py_DECREF(m);
        return NULL;
    }

    InjectorException = PyErr_NewException("injector.InjectorException", NULL, NULL);
    Py_INCREF(InjectorException);
    if (PyModule_AddObject(m, "InjectorException", InjectorException) < 0) {
        Py_DECREF(InjectorException);
        Py_DECREF(&InjectorType);
        Py_DECREF(m);
        return NULL;
    }

    return m;
}
