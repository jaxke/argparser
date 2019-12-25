
from pdb import set_trace as st
import sys

class Arger:
    sys_args = []
    args_parsed = []
    accepted_flags = []

    def __init__(self):
        self.sys_args = sys.argv

    def add_arg(self, *argv, store_true=False, help=""):
        for arg in argv:
            if arg in self.accepted_flags:
                raise ArgumentException("[Arger] Multiple different arguments try to use the flag " + arg)
        self.args_parsed.append(Argument(argv, store_true, help))
        for a in argv:
            self.accepted_flags.append(a)

    # TODO object boolean attribute to accept arrays OR NOT?
    def parse(self):
        for i, sys_arg in enumerate(self.sys_args):
            if sys_arg[0] == "-" and sys_arg not in self.accepted_flags:
                # TODO this is more of a developer orientated exception message?
                raise ArgumentException("[Arger] " + sys_arg + " was not added and therefore not accepted.")
            for j, arg_parsed in enumerate(self.args_parsed):
                if sys_arg in arg_parsed.valid_flags:
                    # Store value as True
                    if arg_parsed.store_true:
                        arg_parsed.arg_value = True
                    # Store value as str
                    else:
                        arg_parsed.arg_value = []
                        for next_argument_after_flag in self.sys_args[i+1:]:
                            # ...until the start of the next argument flag...
                            if next_argument_after_flag[0] == "-":
                                break
                            arg_parsed.arg_value.append(next_argument_after_flag)

                        if len(arg_parsed.arg_value) == 0:
                            raise ArgumentException("[Arger] Argument " + sys_arg + " expects a value!")

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
