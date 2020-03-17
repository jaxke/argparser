
import unittest
import arger
from arger import ArgumentException
import sys


args_dict = {
    # Forget mandatory flag
    "test1": "scriptname file1 file2",
    # Mandatory flag has no value after it
    "test2": "scriptname file1 file2 -d",
    # Mandatory flag is properly entered
    "test3": "scriptname file1 file2 -d file3",
    # No pos args
    "test4": "scriptname -d file3",
    "test5": "scriptname file1 -d file ",
    "test6": "scriptname file1 -a -f",
    "proper_with_all_flags_used": "scriptname file1 file2 -a file3 --delete abc1 abc2 -f",
    "proper_with_all_flags_used_files_int": "scriptname 1 -a file3 --delete abc1 abc2 -f",
    "proper_with_all_flags_used_files_int_pos_arg_ONLY": "scriptname 1",
    "proper_with_all_flags_used_files_str": "scriptname abc -a file3 --delete abc1 abc2 -f",
    "proper_with_all_flags_used_bee_int_list": "scriptname 1 -a file3 --delete abc1 abc2 -f -b 1 2",

}

def set_up_test(arg_key):
    ap = arger.Arger(args_dict[arg_key])
    ap.add_positional_arg("files", arg_type=list, help="Files that you want selected", required=True)
    ap.add_arg("append", "-a", "--append", help="Use this flag to append files")
    ap.add_arg("bee", "-b", arg_type=int)
    ap.add_arg("delete", "--delete", "-d", arg_type=list, required=True, help="Use this flag to delete files")
    ap.add_arg("test_flag", "-f", store_true=True, help="Test")
    return ap


class TestRaises(unittest.TestCase):
    def test_raises_exception_without_required_arg(self):
        self.ap = set_up_test("test1")
        self.assertRaisesRegex(ArgumentException, r"^Argument\(s\) \w* is required!$", self.ap.parse)
    def test_raises_argument_with_nonboolean_arg_without_value(self):
        self.ap = set_up_test("test2")
        self.assertRaisesRegex(ArgumentException, r"^Argument \(.*\) expects a value!$", self.ap.parse)
    def test_raises_argument_with_boolean_arg_with_value(self):
        self.ap = set_up_test("test6")
        self.assertRaisesRegex(ArgumentException, "^Argument .* expects a value!$", self.ap.parse)
    def test_does_not_raise_exception_when_all_mandatory_args_filled(self):
        try:
            self.ap = set_up_test("test3")
            self.ap.parse()
        except Exception as e:
            self.fail(e)
        self.assertEqual(self.ap.get_arg("files"), ["file1", "file2"])
    def test_raises_exception_when_no_mandatory_pos_args(self):
        self.ap = set_up_test("test4")
        self.assertRaisesRegex(ArgumentException, "This program expects positional arguments!", self.ap.parse)
    def test_raises_exception_when_trying_to_add_2_named_args_with_same_id(self):
        self.ap = set_up_test("test4")
        self.assertRaisesRegex(ArgumentException, "^Can not define multiple arguments with name.*", self.ap.add_arg, "test_flag", "-q", store_true=True, help="Test")
    def test_raises_exception_when_trying_to_add_named_arg_with_same_id_as_posarg(self):
        self.ap = set_up_test("test4")
        self.assertRaisesRegex(ArgumentException, "^Can not define multiple arguments with name.*", self.ap.add_arg, "files", "-q", store_true=True, help="Test")
    def test_raises_exception_when_trying_to_add_2_arguments_with_same_flag(self):
        self.ap = set_up_test("test4")
        self.assertRaisesRegex(ArgumentException, r"^Multiple different arguments try to use the flag\(s\).*$", self.ap.add_arg, "test_abc", "-d", store_true=True, help="Test")
    def test_raises_when_named_arg_has_no_name(self):
        ap = arger.Arger("")
        self.assertRaisesRegex(ArgumentException, "Argument can not start with a dash!", ap.add_arg, "-a", "--append",arg_type=list, help="Files that you want selected", required=True)
    def test_raises_when_named_arg_has_no_flags(self):
        ap = arger.Arger("")
        self.assertRaisesRegex(ArgumentException, r"A named argument needs to have flag\(s\)! \(.*\)", ap.add_arg, "a", arg_type=list, help="Files that you want selected", required=True)
     

class TypeTests(unittest.TestCase):
    def test_check_types1(self):
        self.ap = set_up_test("proper_with_all_flags_used")
        self.ap.parse()
        files = self.ap.get_arg("files")
        append = self.ap.get_arg("append")
        delete = self.ap.get_arg("delete")
        test_flag = self.ap.get_arg("test_flag")
        self.assertEqual(files, ["file1", "file2"])
        self.assertEqual(append, "file3")
        self.assertEqual(delete, ["abc1", "abc2"])
        self.assertEqual(test_flag, True)

    def test_check_types2(self):
        self.ap = arger.Arger(args_dict["proper_with_all_flags_used_files_int"])
        self.ap.add_positional_arg("files", arg_type=int, help="Files that you want selected", required=True)
        self.ap.add_arg("append", "-a", "--append", help="Use this flag to append files")
        self.ap.add_arg("delete", "--delete", "-d", arg_type=list, required=True, help="Use this flag to delete files")
        self.ap.add_arg("test_flag", "-f", store_true=True, help="Test")
        self.ap.parse()
        files = self.ap.get_arg("files")
        append = self.ap.get_arg("append")
        delete = self.ap.get_arg("delete")
        test_flag = self.ap.get_arg("test_flag")
        self.assertEqual(files, 1)
        self.assertEqual(append, "file3")
        self.assertEqual(delete, ["abc1", "abc2"])
        self.assertEqual(test_flag, True)

    def test_check_types3(self):
        self.ap = arger.Arger(args_dict["proper_with_all_flags_used_files_str"])
        self.ap.add_positional_arg("files", help="Files that you want selected", required=True)
        self.ap.parse()
        files = self.ap.get_arg("files")
        self.assertEqual(files, "abc")

    def test_check_types4(self):
        self.ap = arger.Arger(args_dict["proper_with_all_flags_used_files_int_pos_arg_ONLY"])
        self.ap.add_positional_arg("files", arg_type=int, help="Files that you want selected", required=True)
        self.ap.parse()
        files = self.ap.get_arg("files")
        self.assertEqual(files, 1)
        

    def test_raise_on_improper_type_definition_on_posarg(self):
        self.ap = arger.Arger(args_dict["proper_with_all_flags_used_files_int"])
        self.assertRaisesRegex(ArgumentException, r"^Type .* is not supported for a positional argument.$", self.ap.add_positional_arg, "files", arg_type=dict)
    
    def test_raise_on_improper_type_definition_on_named_arg(self):
        self.ap = arger.Arger(args_dict["proper_with_all_flags_used_files_int"])
        self.assertRaisesRegex(ArgumentException, r"^Type .* is not supported for a named argument.$", self.ap.add_arg, "append", "-a", arg_type=dict)

    def test_start_program_with_incorrect_types_in_sys_args1(self):
        self.ap = set_up_test("proper_with_all_flags_used_bee_int_list")
        self.assertRaises(ArgumentException, self.ap.parse)
        # TODO why does this fail
        #self.assertRaisesRegex(ArgumentException, r"Expected argument .+ to be a integer, but it was called with multiple values!", self.ap.parse())
    
    def test_store_true_should_always_have_value(self):
        self.ap = set_up_test("test5")
        self.ap.parse()
        test_flag = self.ap.get_arg("test_flag")
        self.assertEqual(test_flag, False)

    def test_raise_with_store_true_and_type(self):
        self.ap = arger.Arger(args_dict["test3"])
        self.assertRaisesRegex(ArgumentException, r"^Can not define an argument with store_true=True and arg_type \(.*\)!", self.ap.add_arg, "files", store_true=True, arg_type=list, help="Files that you want selected")
   
    
"""  def test_raises_with_incompatible_type_in_def_posarg(self):
        self.ap = arger.Arger(args_dict["test3"])
        self.assertRaisesRegex(ArgumentException, r"^Type <.*> is not supported for a positional argument.", self.ap.add_positional_arg, "files", arg_type=dict, help="Files that you want selected")
    def test_raises_with_incompatible_type_in_def_narg(self):
        self.ap = arger.Arger(args_dict["test3"])
        self.assertRaisesRegex(ArgumentException, r"^Type <.*> is not supported for a named argument.", self.ap.add_arg, "a", "-a", arg_type=dict, help="Files that you want selected")
 """

if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(TypeTests('test_check_types4'))
    unittest.TextTestRunner().run(suite); sys.exit(0)
    unittest.main(verbosity=2)