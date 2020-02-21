#!/usr/bin/env python
""" Usage: call with <filename> <typename>
"""

import sys
import clang.cindex

def get_base_classes(node):
    for i in node.walk_preorder():
        if i.kind is clang.cindex.CursorKind.CXX_BASE_SPECIFIER:
            yield i

def get_classes(node):
    for i in node.walk_preorder():
        if i.kind is clang.cindex.CursorKind.CLASS_DECL:
            yield i

def get_forward_declares(cursor):
    for i in get_classes(cursor):
        if i.get_definition() is None:
            yield i

def get_functions(cursor):
    for i in cursor.walk_preorder():
        if i.kind is clang.cindex.CursorKind.CXX_METHOD:
            yield i

def get_parameters(cursor):
    for i in cursor.get_arguments():
        yield "{} {}".format(i.type.spelling, i.spelling)

def find_all(node, pre):
    print '%sFound2 ? %s %s [line=%s, col=%s]' % (pre, node.kind, node.spelling, node.location.line, node.location.column)
    for i in node.walk_preorder():
        if i.kind is not clang.cindex.CursorKind.MACRO_DEFINITION:
        #if i.kind is clang.cindex.CursorKind.CLASS_DECL:
            print "%s %s"%(i.kind, i.spelling)
            print ""
#    for c in node.get_children():
#        return find_all(c, pre + " ")

def find_typerefs(node, typename):
    """ Find all references to the type named 'typename'
    """
    if node.kind.is_reference():
        ref_node = node.referenced 
        if ref_node.spelling == typename:
            print 'Found ref %s [line=%s, col=%s]' % (
                typename, node.location.line, node.location.column)
    else:
        print 'Found ? %s %s [line=%s, col=%s]' % (node.kind, node.spelling, node.location.line, node.location.column)
    # Recurse for children of this node
    for c in node.get_children():
        find_typerefs(c, typename)

def doit(file):
    index = clang.cindex.Index.create()
    unsaved_files = [('./A.cpp', '''    
        #include "B.h"

        class C;
        

        class A : public B
        {
            int poo(int b, char c);
        };
        '''), 
        ('./B.h', '''
        class B
        {
            int a;
        };
        ''')]
    print 'Translation unit:', file
    tu = index.parse(file, unsaved_files=unsaved_files, args=['-I./', "-x", "c++", "--std=c++11"], options=clang.cindex.TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD)
#    for t in tu.get_tokens(extent=tu.cursor.extent):
#         print "%s %s" % (t.kind, t.spelling)
#    find_typerefs(tu.cursor, 'B')
#    find_all(tu.cursor, "")
    for p in get_forward_declares(tu.cursor):
        print "fwd decl: {}".format(p.spelling)
    for p in get_classes(tu.cursor):
        print "class: "+p.spelling
        for f in get_functions(p):
            param_str = ''
            for param in get_parameters(f):
                param_str = '{}{}'.format(param_str, param)
            print "{} {}::{}({})".format(f.result_type.spelling, p.spelling, f.spelling, param_str)
        for b in get_base_classes(p):
            print "base of {}: {}".format(p.spelling, b.spelling)
    for d in tu.diagnostics:
        print d

clang.cindex.Config.set_library_path('/home/byee/Downloads/clang+llvm-9.0.0-x86_64-linux-gnu-ubuntu-16.04/lib')
doit('./A.cpp')
doit('./B.h')
