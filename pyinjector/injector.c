#include <Python.h>
#include <stddef.h>
#include "injector.h"
#include <structmember.h>

static PyObject *InjectorException;

typedef struct {
    PyObject_HEAD
    injector_t *injector;
} Injector;

void Injector_raise(int result) {
    PyObject* error_args = Py_BuildValue("is", result, injector_error());
    PyErr_SetObject(InjectorException, error_args);
    Py_DECREF(error_args);
}

static void Injector_dealloc(Injector* self)
{
    Py_TYPE(self)->tp_free((PyObject*)self);
}

static PyObject *Injector_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    Injector *self = (Injector *)type->tp_alloc(type, 0);
    if (self != NULL) {
        self->injector = NULL;
    }
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
        Injector_raise(result);
        return NULL;
    }

    Py_RETURN_NONE;
}

static PyObject *Injector_inject(Injector *self, PyObject *args)
{
    Py_buffer buffer;
    void *handle;
    int result;

    if (!PyArg_ParseTuple(args, "y*", &buffer)) {
        return NULL;
    }

    char* path = buffer.buf;

    result = injector_inject(self->injector, path, &handle);
    if (result != INJERR_SUCCESS) {
        Injector_raise(result);
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
        Injector_raise(result);
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
        Injector_raise(result);
        return NULL;
    }

    Py_RETURN_NONE;
}

static PyObject *Injector_detach(Injector *self, PyObject *args)
{
    int result = injector_detach(self->injector);
    if (result != INJERR_SUCCESS) {
        Injector_raise(result);
        return NULL;
    }

    Py_RETURN_NONE;
}

static PyMethodDef Injector_methods[] = {
    {"attach", (PyCFunction)Injector_attach, METH_VARARGS, "Attach the injector to a process."},
    {"inject", (PyCFunction)Injector_inject, METH_VARARGS, "Inject a shared library into the process."},
    #if defined(__APPLE__) || defined(__linux)
    {"call", (PyCFunction)Injector_call, METH_VARARGS, "Call a function in the injected library."},
    #endif
    {"uninject", (PyCFunction)Injector_uninject, METH_VARARGS, "Uninject a previously injected library."},
    {"detach", (PyCFunction)Injector_detach, METH_NOARGS, "Detach the injector from the process."},
    {NULL}  /* Sentinel */
};

static PyTypeObject InjectorType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "injector.Injector",
    .tp_doc = "Injector objects",
    .tp_basicsize = sizeof(Injector),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_new = Injector_new,
    .tp_dealloc = (destructor)Injector_dealloc,
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
    PyModule_AddObject(m, "InjectorException", InjectorException);

    return m;
}
