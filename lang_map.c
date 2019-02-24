/* Copyright 2000-2001 ActiveState
 *
 * This file contains various conversion function to map
 * between perl and python datatypes.
 */

#include <EXTERN.h>
#include <perl.h>
#include <Python.h>

#include "lang_map.h"
#include "lang_lock.h"
#include "thrd_ctx.h"
#include "svrv_object.h"

//compat2-3
#if PY_MAJOR_VERSION >= 3
#define PyInt_FromLong(a) PyLong_FromLong(a)
#define PyString_FromStringAndSize PyUnicode_FromStringAndSize
#define PyString_FromString PyUnicode_FromString
#define PyString_Check PyUnicode_Check
#define PyString_GET_SIZE PyUnicode_GET_SIZE
#define PyString_AS_STRING PyBytes_AS_STRING
#define PyString_AsString PyBytes_AsString
#define PyString_Size PyBytes_Size
#define PyInt_AsLong PyLong_AsLong
#define PyInt_Check PyLong_Check
#define PyArg_NoArgs(v)		PyArg_Parse(v, "")
typedef PyObject *(*intargfunc)(PyObject *, int) Py_DEPRECATED(2.5);
typedef int(*intintobjargproc)(PyObject *, int, int, PyObject *);
#endif

#ifdef WIN32_NOT
extern SV* (*pnewPerlPyObject_inc)(PyObject *py);  /* From perlmodule.c */
//extern __declspec(dllimport) SV* newPerlPyObject_inc(PyObject *pyo)
;
//extern SV* newPerlPyObject_inc(PyObject *py);  /* From Python-Object/Object.xs */
#define newPerlPyObject_inc(x) (*pnewPerlPyObject_inc)(x)
#else
extern SV* vk_newPerlPyObject_inc(PyObject *py);  /* From Python-Object/Object.xs */
//SV* (*pnewPerlPyObject_inc)(PyObject *py) = newPerlPyObject_inc;
#endif

/* when the pyo2sv or sv2py functions are called, both the perl and the python
 * lock need to be held.  These functions must guaranty that they will not
 * trigger execution of any perl or python code (like stringify overload or
 * attribute access), but only execute pure api calls.
 */

SV*
pyo2sv(PyObject *o)
{
    dCTXP;

    ASSERT_LOCK_BOTH;

    if (o == Py_None) {
	//printf("pyo2sv(o == Py_None)\n");
	return newSV(0);
    }
    else if (PyString_Check(o)) {
	return newSVpvn(PyString_AS_STRING(o), PyString_GET_SIZE(o));
    }
    else if (PyInt_Check(o)) {
	return newSViv(PyInt_AsLong(o));
    }
    else if (PyLong_Check(o)) {
	unsigned long tmp = PyLong_AsUnsignedLong(o);
	if (tmp == (unsigned long)-1 && PyErr_Occurred()) {
	    /* overflow, don't convert after all */
	    PyErr_Clear();
	    return vk_newPerlPyObject_inc(o);
	}
	return newSVuv(tmp);
    }
    else if (PyFloat_Check(o)) {
	return newSVnv(PyFloat_AsDouble(o));
    }
    else if (PySVRV_Check(o)
#ifdef MULTI_PERL
             && ((PySVRV*)o)->owned_by == ctx->perl
#endif
            )
    {
	return SvREFCNT_inc(PySVRV_RV(o));
    }
    else {
	SV *sv =  vk_newPerlPyObject_inc(o);
	//printf("pyo2sv(PyObject *o) - leave; sv=%08X\n", sv);
	return sv;
    }
}


PyObject*
sv2pyo(SV* sv)
{
    PyObject* po;
    dCTXP;

    ASSERT_LOCK_BOTH;

    if (SvPOK(sv)) {
	STRLEN len;
	char *s = SvPV(sv, len);
	po = Py_BuildValue("s#", s, len);
    }
    else if (SvNOK(sv)) {
	po = Py_BuildValue("d", SvNV(sv));
    }
    else if (SvIOK(sv)) {
	po = Py_BuildValue("l", SvIV(sv));
    }
    else if (SvROK(sv) && sv_derived_from(sv, "Python::Object")) {
        IV ival = SvIV(SvRV(sv));
	if (ival) {
	    po = INT2PTR(PyObject*, ival);
	    Py_INCREF(po);
	}
	else {
	    /* Bad PyObject substitution */
	    po = Py_BuildValue("");
	}
    }
    else if (SvROK(sv)) {
	po = PySVRV_New(sv);
    }
    else if (!SvOK(sv)) {
	po = Py_BuildValue("");
    }
    else {
        /* XXX Let's just stringify all other stuff for now. */

	/* Switch to perl only mode in case there are some stringify
         * overloading taking place here.  Is that actually possible?
         */
	PYTHON_UNLOCK;
	STRLEN len;
	char *s = SvPV(sv, len);
	PYTHON_LOCK;
	po = Py_BuildValue("s#", s, len);
    }

    ASSERT_LOCK_BOTH;
    //printf("sv2pyo leave, sv=%08X po=%08X\n", sv,po);
    return po; 
}

