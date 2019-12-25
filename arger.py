
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
        found_args = {}
        sys_args_str = " ".join(self.sys_args[1:])
        # Save all arguments before the first dash as unnamed
        unnamed = sys_args_str.split(" -")[0]
        for ua in unnamed.split(" "):
            self.unnamed_args.append(ua)
        # Consider all that start with - or --, select the words that belong to
        # that argument (that is words that appear before the next space+dash or eol)
        named_args = re.findall("(-{1,2}.*?)(?= *-|$)", sys_args_str)
        for arg in named_args:
            flag = arg.strip().split(" ")[0]
            arg_values = arg.strip().split(" ")[1:]
            found_args[flag] = arg_values
        # Validate and add values to Argument objects in args_parsed
        for arg in found_args.keys():
            # TODO even I don't know what this does tomorrow
            if arg not in " ".join([" ".join(x.valid_flags) for x in self.args_parsed]).split(" "):
                raise ArgumentException("Argument " + arg + " has not been specified in this program!")
            else:
                for parsed_arg in self.args_parsed:
                    if arg in parsed_arg.valid_flags and parsed_arg.store_true and found_args[arg] != []:
                        raise ArgumentException("Argument " + arg + " stores true and does not expect a value!")
                    elif arg in parsed_arg.valid_flags and not parsed_arg.store_true and found_args[arg] == []:
                            raise ArgumentException("Argument " + arg + " expects a value!")
                    elif arg in parsed_arg.valid_flags and parsed_arg.store_true:
                        parsed_arg.arg_value = True
                    elif arg not in parsed_arg.valid_flags and parsed_arg.store_true:
                        parsed_arg.arg_value = False
                    elif arg in parsed_arg.valid_flags and not parsed_arg.store_true:
                        parsed_arg.arg_value = found_args[arg]

    def readable(self):
        if self.unnamed_args:
            print("Unnamed args:", self.unnamed_args)
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
