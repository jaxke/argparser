
from pdb import set_trace as st
import sys
import re

class Arger:
    sys_args = []
    args_parsed = []
    accepted_flags = []
    # TODO delete unnamed_args once positional arguments is completed
    unnamed_args = []
    positional_arguments = None
    named_args = {}
    required_args = []
    found_args = {}


    def __init__(self):
        self.sys_args = sys.argv

    # TODO maybe move the default values to the init of Argument?
    # TODO rename parameter argv to something more verbose
    # Adds argument objects to a list based on definitions.
    def add_arg(self, name, *argv, help="", store_true=False, required=False):
        # TODO unsafe, don't use dashes for identification
        if name[0] == "-":
            raise ArgumentException("[Arger] Missing argument name in " + name)
        for arg in argv:
            if arg in self.accepted_flags:
                raise ArgumentException("[Arger] Multiple different arguments try to use the flag " + arg)
        self.args_parsed.append(Argument(name, argv, store_true, help, required))
        self.accepted_flags.extend(argv)
        if required:
            self.required_args.append(name)

    def add_positional_arg(self, name, help="", required=False):
        self.positional_argument = PositionalArgument(name, help, required)

    # TODO this method needs to work with positional arguments
    # Builds a help message from arguments that have been definied.
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
                        help_text += " {}] ".format(arg.arg_name)
                    else:
                        help_text += " {} ".format(arg.arg_name)
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

    # Parses command line arguments and their values. Validates that requirements 
    # are met and that the data types are correct (Ie. store_true argument should 
    # not have values, because such arguments are booleans, based on if they're 
    # specified or not in cmd).
    def parse(self):
        if "-h" in self.sys_args:
            self.print_help()
        sys_args_str = " ".join(self.sys_args[1:])
        # TODO Will 100% sure fail if positional arguments were not defined
        self.positional_arguments, named_args = self.get_positional_arguments_from_sysargs()
        # Consider all that start with - or --, select the words that belong to
        # that argument (that is words that appear before the next space+dash or eol)
        #named_args = re.findall("(-{1,2}.*?)(?= *-|$)", sys_args_str)
        named_args_dict = self.isolate_named_args_into_a_dict(named_args)
        ############# DELETE ->
        named_args_dict = {}
        for arg in named_args:
            arg_flag = arg.split(" ")[0]
            named_args_dict[self.get_id_from_flag(arg_flag)] = arg.split(" ")[1:]
        for arg in named_args_dict:
            self.validate_used_args_datatype(arg, named_args_dict[arg])
        self.found_args = self.get_sys_arg_dict(named_args_dict, self.positional_arguments)
        # Will raise ArgumentException if validation fails
        self.validate_requirements_satisfied()

    def isolate_named_args_into_a_dict(self, named_args):
        named_args_str = " ".join(named_args)
        named_args_dict = {}
        found_flags_in_sysargs = []
        indexes_of_found_arguments = []
        TEST_ARRAY = []
        for word in named_args:
            if self.is_a_defined_flag(word):
                found_flags_in_sysargs.append(word)
        for i in range(len(found_flags_in_sysargs)):
            if i == len(found_flags_in_sysargs)-1:
                TEST_ARRAY.append(named_args_str)
                break
            re_arg_and_values = re.search(r"^({}.*)(?= {})".format(found_flags_in_sysargs[i], found_flags_in_sysargs[i+1]), named_args_str)
            re_rest           = re.search(r"({}.*)$".format(found_flags_in_sysargs[i+1]), named_args_str)
            TEST_ARRAY.append(re_arg_and_values.group(0))
            named_args_str = re_rest.group(0)
            print()
        sys.exit(0)
        return None


    def get_positional_arguments_from_sysargs(self):
        sys_args_str = " ".join(self.sys_args[1:])
        pos_args_str = ""
        for i, word in enumerate(sys_args_str.split(" ")):
            if self.is_a_defined_flag(word):
                pos_args_str = " ".join(sys_args_str.split(" ")[:i])
                rest = " ".join(sys_args_str.split(" ")[i:])
                break
        return pos_args_str.split(" "), rest.split(" ")

    def is_a_defined_flag(self, word):
        for accepted_flag in self.accepted_flags:
                if accepted_flag == word:
                    return True
        return False

    # All defined arguments that are "required" in method call in the parent script
    # should be in the cmd arguments.
    def validate_requirements_satisfied(self):
        requirements_satisfied = []
        for req_arg in self.required_args:
            for i, arg in enumerate(self.found_args.keys()):
                if arg == req_arg:
                    requirements_satisfied.append(arg)
        if requirements_satisfied != self.required_args:
            non_satisfied_requirements = " ,".join(set(self.required_args) - set(requirements_satisfied))
            raise ArgumentException("Argument(s) {} is required!".format(non_satisfied_requirements))

    # Parameter = argument identifier (name)
    # Return    = its valid flags
    def get_flags_from_id(self, id):
        for arg in self.args_parsed:
            if arg.arg_name == id:
                return arg.valid_flags

    # Parameter = argument flag
    # Return    = argument identifier (name) that corresponds to this cmd flag
    def get_id_from_flag(self, flag):
        for arg in self.args_parsed:
            if flag in arg.valid_flags:
                return arg.arg_name
        return False
        # TODO implement this elsewhere
        raise ArgumentException("Argument {} has not been defined in this program!".format(flag))

    # Builds a dict object to correspond the cmd arguments.
    def get_sys_arg_dict(self, named_args, unnamed_args):
        sys_args_dict = {}
        sys_args_dict["Unnamed"] = []
        for ua in unnamed_args:
            sys_args_dict["Unnamed"].append(ua)
        for na_key, na_val in named_args.items():
            if na_val == []:
                sys_args_dict[na_key] = True
            else:
                sys_args_dict[na_key] = na_val
        return sys_args_dict
        
    # TODO once the option to choose whether an array is required or not, the validation should be here
    # Validates that store_true arguments don't have a value attached to them, and that arguments that 
    # aren't store_true have value(s) attached to them.
    def validate_used_args_datatype(self, arg_key, arg_val):
        for parsed_arg in self.args_parsed:
            if arg_key == parsed_arg.arg_name:
                if arg_val == [] and parsed_arg.store_true:
                    return True
                elif arg_val != [] and parsed_arg.store_true:
                    raise ArgumentException("Argument \"{}\" does not expect a value!".format(" ".join(parsed_arg.valid_flags)))
                elif arg_val != [] and not parsed_arg.store_true:
                    return True
        # This should not be needed?
        raise ArgumentException("Argument", arg_key, "has not been defined in this program!")
    
    # Debugging
    def readable(self):
        # Prints arguments that were used in cmd
        for ua in self.found_args:
            print("{}: {}".format(ua, self.found_args[ua]))
        # Prints arguments that were defined
        for arg in self.args_parsed:
            print("\nValid Flags: {}\nStore true: {}\nHelp: {}\nValue: {}".format(list(arg.valid_flags), arg.store_true, arg.help, arg.arg_value))

    # TODO needed or not?
    def arg_is_store_true(self, flag):
        for arg in self.args_parsed:
            if flag in arg.valid_flags:
                if arg.store_true:
                    return True
                else:
                    return False


class ArgumentException(Exception):
    pass


class Argument:
    arg_name = ""
    valid_flags = []
    store_true = False
    help = ""
    arg_value = None
    required = False
    def __init__(self, name, flags, store_true, help, required):
        self.valid_flags = flags
        self.store_true = store_true
        self.help = help
        self.required = required
        self.arg_name = name
    def __str__(self):
        if type(self.arg_value) == list:
            return " ".join(self.arg_value)
        else:
            return str(self.arg_value)

class PositionalArgument(Argument):
    arg_name = ""
    help = ""
    arg_value = None
    required = False
    def __init__(self, name, help, required):
        self.arg_name = name
        self.help = help
        self.required = required
    def __str__(self):
        return " ".join(self.arg_value)

if __name__ == "__main__":
    sys.exit("This is not a runnable script!")
