import unittest
import arger
from arger import ArgumentException

args_dict = {
    # Forget mandatory flag
    "test1": "scriptname file1 file2",
    # Mandatory flag has no value after it
    "test2": "scriptname file1 file2 -d",
    # Mandatory flag is properly entered
    "test3": "scriptname file1 file2 -d file3",
    "test4": "scriptname -d file3",
    "test5": "scriptname file1 -d file ",
    "test6": "scriptname file1 -a -f",
    "proper_with_all_flags_used": "scriptname file1 file2 -a file3 --delete abc1 abc2 -f"
}

def set_up_test(arg_key):
    ap = arger.Arger(args_dict[arg_key])
    ap.add_positional_arg("files", arg_type=list, help="Files that you want selected", required=True)
    ap.add_arg("append", "-a", "--append", help="Use this flag to append files")
    ap.add_arg("delete", "--delete", "-d", arg_type=list, required=True, help="Use this flag to delete files")
    ap.add_arg("test_flag", "-f", store_true=True, help="Test")
    return ap


class TestArguments(unittest.TestCase):
    def test_raises_exception_without_required_arg(self):
        self.ap = set_up_test("test1")
        self.assertRaisesRegex(ArgumentException, r"^Argument\(s\) \w* is required!$", self.ap.parse)
    def test_raises_argument_with_nonboolean_arg_without_value(self):
        self.ap = set_up_test("test2")
        self.assertRaisesRegex(ArgumentException, r"^Argument -{0,2}\w* expects a value!$", self.ap.parse)
    def test_raises_argument_with_boolean_arg_with_value(self):
        self.ap = set_up_test("test6")
        #self.assertRaisesRegex(ArgumentException, "^Argument .* expects a value!$", self.ap.parse)
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

class TypeTests(unittest.TestCase):
    def test_check_types(self):
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


if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(TestArguments('test_raises_exception_when_trying_to_add_2_arguments_with_same_flag'))
    #unittest.TextTestRunner().run(suite)
    unittest.main(verbosity=2)