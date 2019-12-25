
from pdb import set_trace as st
import sys

class Arger:
    sys_args = []
    args_parsed = []

    def __init__(self):
        self.sys_args = sys.argv

    def add_arg(self, *argv, store_true=False, help=""):
        if len(argv) > 1:
            raise Exception
        self.args_parsed.append(Argument(argv[0], store_true, help=""))

    def parse(self):
        for i, sys_arg in enumerate(self.sys_args):
            for arg_parsed in self.args_parsed:
                if arg_parsed.name == sys_arg:
                    # Store value as True
                    if arg_parsed.store_true:
                        arg_parsed.arg_value = True
                    # Store value as str
                    else:
                        try:
                            arg_parsed.arg_value = self.sys_args[i+1]
                            # Argument value is possibly just a flag for another argument
                            if arg_parsed.arg_value[0] == "-":
                                raise IndexError
                        except IndexError:
                            sys.exit("[Arger] Argument " + sys_arg + " expects a value!")

    def readable(self):
        for arg in self.args_parsed:
            print("\nName: {}\nStore true: {}\nHelp: {}\nValue: {}".format(arg.name, arg.store_true, arg.help, arg.arg_value))


class Argument:
    name = ""
    store_true = False
    help = ""
    arg_value = None
    def __init__(self, name, store_true, help):
        self.name = name
        self.store_true = store_true
        self.help = help

if __name__ == "__main__":
    sys.exit("This is not a runnable script!")
