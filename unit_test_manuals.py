
'''
    Manual testing file to check that "testing mode" does not impede the workings of the program
'''

import arger
import unittest

def case1():
    ap = arger.Arger()
    ap.add_positional_arg("files", arg_type=str, help="Files that you want selected")
    ap.add_arg("append", "-a", "--append", help="Use this flag to append files")
    ap.add_arg("bee", "-b", arg_type=int)
    ap.add_arg("delete", "--delete", "-d", arg_type=list, required=True, help="Use this flag to delete files")
    ap.add_arg("test_flag", "-f", store_true=True, help="Test")

    files = ap.get_arg("files")
    assert files == "abc"

# TODO FAILS
def case2():
    ap = arger.Arger()
    ap.add_positional_arg("files", arg_type=int, help="Files that you want selected")
    ap.parse()
    files = ap.get_arg("files")
    assert files == "abc"

def case3():
    ap = arger.Arger()
    ap.add_positional_arg("files", arg_type=str, help="Files that you want selected")
    ap.parse()
    files = ap.get_arg("files")
    assert files == "abc"

case3()
