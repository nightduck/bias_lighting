//
// Created by oren on 5/20/18.
//

#include <Python.h>
#include <arrayobject.h>

// ----------------------Python Methods------------------------------
static PyObject* pong_ani(PyObject* self, PyObject* args) {
    PyObject* strip;
    int* pixel_number;
    int* color;

    int status = PyArg_ParseTuple(args, "Oii;pong_ani - couldn't parse args", strip, pixel_number, color);

    return nullptr;
}

static PyObject* ember_ani(PyObject* self, PyObject* args) {
    PyObject* strip;
    PyListObject* states;
    PyObject* temp;

    int status = PyArg_ParseTuple(args, "OOO;ember_ani - couldn't parse args", strip, states, temp);

    PyObject* instructions = PyArray_FROM_OTF(temp, NPY_DOUBLE, NPY_ARRAY_IN_ARRAY);

    return nullptr;
}

static PyObject* wipe_ani(PyObject* self, PyObject* args) {
    PyObject* strip;
    int* position;
    PyListObject* swaths;

    int status = PyArg_ParseTuple(args, "OiO;wipe_ani - couldn't parse args", strip, position, swaths);

    return nullptr;
}

static PyObject* flash_ani(PyObject* self, PyObject* args) {
    PyObject* strip;
    int* position;
    PyListObject* swaths;

    int status = PyArg_ParseTuple(args, "OiO;flash_ani - couldn't parse args", strip, position, swaths);

    return nullptr;
}

// ---------------------Python docs----------------------------------
char* animations_doc = "animations(): TODO - Write a doc";
char* pong_ani_doc = "pong_ani(): TODO - Write a doc";
char* ember_ani_doc = "ember_ani(): TODO - Write a doc";
char* wipe_ani_doc = "wipe_ani(): TODO - Write a doc";
char* flash_ani_doc = "flash_ani(): TODO - Write a doc";

// ---------------------Python method defs---------------------------
static PyMethodDef animations_methods[] = {
        {"pong_ani", (PyCFunction)pong_ani, METH_VARARGS, pong_ani_doc},
        {"ember_ani", (PyCFunction)ember_ani, METH_VARARGS, ember_ani_doc},
        {"wipe_ani", (PyCFunction)wipe_ani, METH_VARARGS, wipe_ani_doc},
        {"flash_ani", (PyCFunction)flash_ani, METH_VARARGS, flash_ani_doc},
        {NULL}
};

// ---------------------Python module defs---------------------------
static struct  PyModuleDef animations_module = {
        PyModuleDef_HEAD_INIT,
        "animations",
        animations_doc,
        -1,
        animations_methods
};