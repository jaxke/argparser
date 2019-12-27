
from pdb import set_trace as st
import sys
import re

class Arger:
    sys_args = []
    args_parsed = []
    accepted_flags = []
    unnamed_args = []
    named_args = {}
    required_args = []

    def __init__(self):
        self.sys_args = sys.argv

    def add_arg(self, *argv, store_true=False, help="", required=False):
        for arg in argv:
            if arg in self.accepted_flags:
                raise ArgumentException("[Arger] Multiple different arguments try to use the flag " + arg)
        self.args_parsed.append(Argument(argv, store_true, help, required))
        for a in argv:
            self.accepted_flags.append(a)
            if required:
                self.required_args.append(a)

    def print_help(self):
        program_name = self.sys_args[0].split("/")[-1]
        help_text = "usage: "
        for arg in self.args_parsed:
            if not arg.required:
                help_text += "["
            for i, flag in enumerate(arg.valid_flags):
                if i != len(arg.valid_flags)-1:
                    help_text += flag + "|"
                else:
                    help_text += flag
                    if not arg.required:
                        help_text += "]"
                    help_text += " "
        help_text += program_name
        if self.required_args:
            help_text += "\n\nRequired arguments:\n"
            for arg in self.args_parsed:
                if arg.required:
                    help_text += ", ".join(arg.valid_flags) + "\t\t"
                    if arg.help:
                        help_text += arg.help
        help_text += "\n\nNon-required arguments:\n"
        for arg in self.args_parsed:
            if not set(arg.valid_flags) <= set(self.required_args):
                help_text += ", ".join(arg.valid_flags) + "\t\t" + arg.help + "\n"
        print(help_text)
        sys.exit(0)

    def parse(self):
        if "-h" in self.sys_args:
            self.print_help()
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
        # TODO possibly unsafe??
        for req_arg in self.required_args:
            if req_arg not in self.sys_args:
                raise ArgumentException("Argument " + req_arg + " is required!")

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
    required = False
    def __init__(self, flags, store_true, help, required):
        self.valid_flags = flags
        self.store_true = store_true
        self.help = help
        self.required = required
    def __str__(self):
        if type(self.arg_value) == list:
            return " ".join(self.arg_value)
        else:
            return str(self.arg_value)

if __name__ == "__main__":
    sys.exit("This is not a runnable script!")
