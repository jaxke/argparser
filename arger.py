
from pdb import set_trace as st
import sys
import re

class Arger:
    sys_args = []
    args_parsed = []
    accepted_flags = []
    unnamed_args = []
    named_args = {}

    def __init__(self):
        self.sys_args = sys.argv

    def add_arg(self, *argv, store_true=False, help=""):
        for arg in argv:
            if arg in self.accepted_flags:
                raise ArgumentException("[Arger] Multiple different arguments try to use the flag " + arg)
        self.args_parsed.append(Argument(argv, store_true, help))
        for a in argv:
            self.accepted_flags.append(a)

    def parse(self):
        parsed_args = {}
        sys_args_str = " ".join(self.sys_args[1:])
        # Save all arguments before the first dash as unnamed
        unnamed_args = sys_args_str.split(" -")[0]
        named_args = re.findall("(-{1,2}\w* *\w*)", sys_args_str)
        for arg in named_args:
            flag = arg.strip().split(" ")[0]
            arg_values = arg.strip().split(" ")[1:]
            parsed_args[flag] = arg_values
        for arg in parsed_args.keys():
            # TODO even I don't know what this does tomorrow
            if arg not in " ".join([" ".join(x.valid_flags) for x in self.args_parsed]).split(" "):
                raise ArgumentException("Argument " + arg + " has not been specified in this program!")
            # elif [] and parsed_args[arg] != []:
            #     raise ArgumentException("Argument " + arg + " should not have argument values! (it is just a flag)")

    def readable(self):
        for arg in self.args_parsed:
            print("\nValid Flags: {}\nStore true: {}\nHelp: {}\nValue: {}".format(list(arg.valid_flags), arg.store_true, arg.help, arg.arg_value))


class ArgumentException(Exception):
    pass


class Argument:
    valid_flags = []
    store_true = False
    help = ""
    arg_value = None
    def __init__(self, flags, store_true, help):
        self.valid_flags = flags
        self.store_true = store_true
        self.help = help

if __name__ == "__main__":
    sys.exit("This is not a runnable script!")
