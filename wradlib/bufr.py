#-------------------------------------------------------------------------------
# Name:        bufr
# Purpose:
#
# Authors:     Maik Heistermann, Stephan Jacobi and Thomas Pfaff
#
# Created:     01.08.2012
# Copyright:   (c) Maik Heistermann, Stephan Jacobi and Thomas Pfaff 2011
# Licence:     The MIT License
#-------------------------------------------------------------------------------
#!/usr/bin/env python

import os
import ctypes as C
import numpy as np
import pylab as pl
import sys
from subprocess import call


# Using fixed names for temporary files in order to enforce a stable function interface
descfile ="desc.src"
imgfile  = "img.dec"
sect1file= "section.1.out"

# BUFR library directory location
bufrlibdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bufr_3.1")

# external file names for shared libraries and executables
winshlib = 'bufr2wradlib.dll'
linuxshlib = 'bufr2wradlib.a'
winexecutable = 'decbufr.exe'
linuxexecutable = 'decbufr'

if not os.path.exists(bufrlibdir):
    print ("Cannot find the BUFR library directory under %s." % bufrlibdir)
    print ("Check your wradlib installation directory.")
    print ("BUFR decoding is not operational for this wradlib installation!")

# remember where you are
myhome = os.path.abspath( os.getcwd() )

#-------------------------------------------------------------------------------
# THE FOLLOWING SECTIONS WILL BE USED IN CASE THE SHARED LIBRARY FROM BUFR WILL WORK
# FOR THE TIME BEING, THESE PARTS ARE OUTCOMMENTED IN ORDER TO ENSURE STABILITY

# START OUTCOMMENT

### change into the OPERA BUFR library directory
##os.chdir(bufrlibdir)
##
### Load shared library
##if 'win' in os.sys.platform:
##    # Use under Windows
##    try:
##        decbufr = C.CDLL(winshlib)
##    except:
##        print "Cannot load windows dll for BUFR library: %s" % os.path.join(bufrlibdir, winshlib)
##        print "Potential reason #1: Failed installation - The BUFR library has to be successfully compiled during installation of wradlib."
##        print "Potential reason #2: Directories are mixed up...check if the file library file exists in another directory."
##        print "Also check the Exception message"
##        raise
##elif "linux" in os.sys.platform:
##    # Use under Linux
##    try:
##        decbufr = C.cdll.LoadLibrary(linuxshlib)
##    except:
##        print "Cannot load shared BUFR library: %s" % os.path.join(bufrlibdir, linuxshlib)
##        print "Potential reason #1: Failed installation - The BUFR library has to be successfully compiled during installation of wradlib."
##        print "Potential reason #2: Directories are mixed up...check if the file library file exists in another directory."
##        print "Note: Linux funcitonality has not yet been tested! You might be the first to encounter this error."
##        print "Please contact wradlib developers via wradlib-users@googlegroups.com"
##        print "Also check the Exception message"
##        raise
##else:
##    # Other OS
##    raise Exception("Cannot use wradlib BUFR module under operating systems other than Linux or Windows, yet.")
##
### return home
##os.chdir(myhome)
##
### ------------------------------------------------------------------------------
### definition of C structures from apisample.h in terms of Python classes
##
##
### internal radar data structure
##class radar_data_t(C.Structure):
##    pass
##radar_data_t._fields_ = [
##                  ("data",C.POINTER(C.c_ushort)),
##                  ("desctable",C.c_char_p)]
##
### internal radar data structure
##class radar_data2_t(C.Structure):
##    pass
##radar_data2_t._fields_ = [
##                  ("data",C.POINTER(C.c_ubyte)),
##                  ("desctable",C.c_char_p)]
##
##
### Prototype for calling the 1st shared library function
##decbufr.py2bufr.restype = radar_data_t
##decbufr.py2bufr.argtypes = [C.c_char_p]
##alldata = decbufr.py2bufr(C.c_char_p(fname))
### create buffer which holds the actual data
##buffer_size = nrow * ncol * C.sizeof(C.c_ushort)
##mybuffer = C.create_string_buffer(buffer_size)
##C.memmove(mybuffer, alldata.data, buffer_size)
### buffer to integer array
##vals = np.frombuffer(mybuffer, dtype=np.uint16)
##vals = vals.reshape((nrow,ncol))
##
##
### Prototype for calling the 2nd shared library function
##decbufr.py2bufr2.restype = radar_data2_t
##decbufr.py2bufr2.argtypes = [C.c_char_p]
##alldata = decbufr.py2bufr2(C.c_char_p(fname))
### create buffer which holds the actual data
##buffer_size = nrow * ncol * C.sizeof(C.c_ubyte)
##mybuffer = C.create_string_buffer(buffer_size)
##C.memmove(mybuffer, alldata.data, buffer_size)
### buffer to integer array
##vals = np.frombuffer(mybuffer, dtype=np.uint8)
##vals = vals.reshape((nrow,ncol))


# END OUTCOMMENT
#-------------------------------------------------------------------------------

def parse_desctable(fpath):
    """Parses the decriptor table and returns a dict of descriptors
    """
    desc2name = {}
    name2val  = {}
    descs = []
    vals  = []
    names = []
    try:
        f = open(fpath, "r")
    except:
        print "Could not open file for reading: %s" % (fpath,)
        raise
    lines = f.readlines()
    f.close()
    # iterate over all lines and organize table entries in lists
    for i, line in enumerate(lines):
        if line.strip()=="":
            continue
        ldesc = parse_desc(line[0:10])
        if ldesc==(3,21,193):
            pass
        try:
            vals.append(eval(line[10:26].strip()))
        except:
            vals.append(line[10:26].strip())
        rdesc = parse_desc(line[26:35])
        names.append(line[35:].strip())
        if not rdesc==():
            descs.append(rdesc)
        else:
            descs.append(ldesc)
    # now mapping descriptors to descriptor names and names to descriptor values
    for i in range(0, len(descs)):
        # just an ordinary assignment
        if descs[i] in desc2name.keys():
            if type(name2val[names[i]])==list:
                # append to list if already exists
                name2val[names[i]].append(vals[i])
            else:
                # create a list if this is the first time the same descriptor appears
                name2val[names[i]] = [name2val[names[i]], vals[i]]
        else:
            desc2name[descs[i]] = names[i]
            name2val[names[i]] = vals[i]
        i += 1
    return desc2name, name2val


def parse_desc(seqdesc):
    """Parses a sequence string and returns a tuple
    """
    out = []
    seqdesc = seqdesc.split(" ")
    for elem in seqdesc:
        if not elem=="":
            out.append(int(elem))
    return tuple(out)


def parse_buffer(fpath):
    """Parses string buffer from file and returns a numpy integer array
    """
    try:
        f = open(fpath, "rb")
    except:
        print "Could not open file for reading: %s" % (fpath,)
        raise
    buf = f.read()
    f.close()
    vals = np.frombuffer(buf, dtype=np.uint8)
    return vals.copy()


def map_to_levelsclices(vals, levels, nodata):
    """Returns array of actual values based on index array *arr* and slicing *levels*
    """
    mask  = np.where(vals==nodata)[0]
    vals[mask] = 0
    try:
        vals = np.array(levels)[vals]
    except:
        print "BUFR values are probably inconsistent with slicing information."
        raise
    vals[mask] = np.nan
    return vals


def get_slicing_levels(descnames, descvals):
    """Returns array of slicing values from lookup table
    """
    levels = None
    # convert to actual values based on lookup table
    for desc in descnames.keys():
        if (desc[0] == 0) and (desc[1] == 21):
            if not levels==None:
                print "The descriptor table seems indicates that more than one variable is contained in the BUFR file."
                print "Please check the following descriptors:"
                print descnames
                raise Exception("See message above...")
            else:
                levels = descvals[descnames[desc]]
    return levels

def check_descriptor(desc, descnames, descvals, allowed=None, typecast=int, mandatory=True):
    """Checks if descriptor exists, has a valid value and, if yes, returns the value
    """
    if not desc in descnames.keys():
        if mandatory:
            print descnames
            raise Exception( "Invalid descriptor table (see above printout): decriptor %r is missing." % (desc,) )
        else:
            return None
    val = typecast( descvals[descnames[desc]] )
    if not allowed==None:
        if not val in allowed:
            raise Exception( "Invalid value %r for descriptor %r" % (val, desc) )
    return val


def decodebufr(buffile):
    """Main interface: Decodes BUFR file and returns a dict of descriptors and value array
    """
    # change to BUFR directory
    os.chdir(bufrlibdir)
    # read the file by using the C BUFR library
    if os.sys.platform=="win32":
        try:
##            retval = decbufr.decbufr2py(C.c_char_p(buffile), C.c_char_p(descfile))
            retval = call([winexecutable, buffile, descfile, imgfile])
        except:
            print "Error in calling the external C BUFR decoder."
            raise
    elif "linux" in os.sys.platform:
        try:
##            retval = decbufr.decbufr2py(C.c_char_p(buffile), C.c_char_p(descfile))
            retval = call([linuxexecutable, buffile, descfile, imgfile])
        except:
            print "Error in calling the external C BUFR decoder."
            print "This might be a Linux issue...code has not yet been tested on Linux."
            print "Please contact wradlib developers via wradlib-users@googlegroups.com"
            raise
    else:
        raise Exception("wradlib BUFR module cannot be used on platforms other than Windows and Linux")
    # This is just a teporary solution: better get a hand on the stderr object
    if not retval==0:
        raise Exception( "An error occured in calling the external C BUFR decoder." )
    # get metadata
    descnames, descvals = parse_desctable(descfile)
    # get value width (in bits) per pixel for the pixel bitmap
    if (3,21,192) in descnames.keys():
        depth = 4
        nodata= 15
    elif (3,21,193) in descnames.keys():
        depth = 8
        nodata=255
    else:
        print "Cannot determine pixel depth."
        print "Try to adapt the code in function bufr.decodebufr if possible."
        print "Otherwise contact wradlib developers via google group wradlib-users."
        raise Exception()
    # get raw value array
    vals  = parse_buffer(imgfile)
    # get the slicing information
    levels = get_slicing_levels(descnames, descvals)
    # get the actual value array
    if not levels==None:
        vals = map_to_levelsclices(vals, levels, nodata)
    # which type of grid? (0 for cartesian; 1 for polar)
    gridtype = check_descriptor((0,29,2), descnames, descvals, allowed=(0,1))
    # which type of image? (0=PPI; 1=composite; 2=CAPPI)
    imgtype = check_descriptor((0,30,196), descnames, descvals, allowed=(0,1,2), mandatory=False)
    if imgtype==None:
        imgtype = check_descriptor((0,30,31), descnames, descvals, allowed=(0,1,2))
    # grid dimensions?
    if gridtype==1:
        numazims = check_descriptor((0,30,195), descnames, descvals, mandatory=False)
        numranges= check_descriptor((0,30,194), descnames, descvals, mandatory=False)
        if numazims==None:
            numazims = check_descriptor((0,30,22), descnames, descvals)
        if numranges==None:
            numranges = check_descriptor((0,30,21), descnames, descvals)
        gridshape = (numazims, numranges)
    else:
        numrows = check_descriptor((0,30,22), descnames, descvals)
        numcols = check_descriptor((0,30,21), descnames, descvals)
        gridshape = (numrows, numcols)
    # reshape according to grid specs
    try:
        vals = vals.reshape(gridshape)
    except:
        print "Length of raw value array seems inconsistent with grid dimensions."
        raise
    # clean up your mess
    if os.path.exists(descfile):
        os.remove(descfile)
    if os.path.exists(imgfile):
        os.remove(imgfile)
    if os.path.exists(sect1file):
        os.remove(sect1file)
    os.chdir(myhome)
    return descnames, descvals, vals


if __name__ == '__main__':
    print 'wradlib: Calling module <bufr> as main...'






