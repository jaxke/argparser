
from pdb import set_trace as st
import sys
import re

# TODO "this argument is not defined in this program"

class Arger:
    # TODO need to clean up attributes and decide if dict is better than a list of objects
    sys_args = []
    args_parsed = []
    accepted_flags = []
    # TODO delete unnamed_args once positional arguments is completed
    unnamed_args = []
    positional_arguments = None
    named_args = {}
    required_args = []
    found_args = {}

    arguments = {}

    def __init__(self):
        self.sys_args = sys.argv

    # Adds argument objects to a list based on definitions.
    def add_arg(self, name, *flags, help="", store_true=False, required=False, arg_type=None):
        if store_true and arg_type:
            raise ArgumentException("[Arger] Can't define an argument with store_true and arg_type in argument " + name)
        # TODO unsafe, don't use dashes for identification
        if name[0] == "-":
            raise ArgumentException("[Arger] Missing argument name in " + name)
        for arg in flags:
            if arg in self.accepted_flags:
                raise ArgumentException("[Arger] Multiple different arguments try to use the flag " + arg)
        self.args_parsed.append(Argument(name, flags, store_true, help, required, arg_type))
        self.accepted_flags.extend(flags)
        if required:
            self.required_args.append(name)

    def add_positional_arg(self, name, help="", required=False, arg_type=None):
        self.positional_arguments = PositionalArgument(name, help, required, arg_type)

    def get_arg(self, name):
        return self.arguments[name]

    # Builds a help message from arguments that have been definied.
    def print_help(self):
        width = 30
        program_name = self.sys_args[0].split("/")[-1]
        help_text = "usage: "
        help_text += program_name
        if self.positional_arguments:
            help_text += " "
            if self.positional_arguments.required:
                help_text += self.positional_arguments.arg_name
            else:
                help_text += "[{}]".format(self.positional_arguments.arg_name)
            help_text += " "
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
        if self.positional_arguments:
            help_text += "\n\nPositional arguments:\n"
            help_text += self.positional_arguments.arg_name + " "*(width - len(self.positional_arguments.arg_name)) + self.positional_arguments.help
            if self.positional_arguments.required:
                help_text += " (required)"
        if self.required_args:
            help_text += "\n\nRequired arguments:\n"
            for arg in self.args_parsed:
                if arg.required:
                    help_text += ", ".join(arg.valid_flags) + " "*(width - len(", ".join(arg.valid_flags)))
                    if arg.help:
                        help_text += arg.help
        help_text += "\n\nNon-required arguments:\n"
        for arg in self.args_parsed:
            if not set(arg.valid_flags) <= set(self.required_args):
                help_text += ", ".join(arg.valid_flags) + " "*(width - len(", ".join(arg.valid_flags))) + arg.help + "\n"
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
        pos_arguments, named_arguments = self.get_positional_arguments_from_sysargs()
        # Consider all that start with - or --, select the words that belong to
        # that argument (that is words that appear before the next space+dash or eol)
        #named_args = re.findall("(-{1,2}.*?)(?= *-|$)", sys_args_str)
        named_args_dict = self.isolate_named_args_into_a_dict(named_arguments)
        # TODO NO RAISES HERE!!
        if not self.validate_and_cast_positional_args(pos_arguments):
            raise ArgumentException
        if not self.validate_and_cast_named_arguments(named_args_dict):
            raise ArgumentException
        if not self.validate_requirements_satisfied(pos_arguments, named_args_dict):
            raise ArgumentException

    # All defined arguments that are "required" in method call in the parent script
    # should be in the cmd arguments.
    def validate_requirements_satisfied(self, pos_arguments, named_arguments):
        requirements_satisfied = []
        for req_arg in self.required_args:
            for i, arg in enumerate(self.arguments.keys()):
                if arg == req_arg:
                    requirements_satisfied.append(arg)
        if requirements_satisfied != self.required_args:
            non_satisfied_requirements = " ,".join(set(self.required_args) - set(requirements_satisfied))
            raise ArgumentException("Argument(s) {} is required!".format(non_satisfied_requirements))
        return True

    # TODO exceptions should be raised here, hence the elifs
    # TODO remove all functionality of returns!
    def validate_and_cast_positional_args(self, pos_arguments):
        # add_positional_arg was never used and therefore unexpected
        if not self.positional_arguments:
            return True
        if self.positional_arguments.arg_type == str:
            if len(pos_arguments) < 1:
                return False
            elif len(pos_arguments) > 1:
                return False
            else:
                self.arguments[self.positional_arguments.arg_name] = pos_arguments[0]
                return True
        elif self.positional_arguments.arg_type == list:
            self.arguments[self.positional_arguments.arg_name] = pos_arguments
            return True
        elif self.positional_arguments.arg_type == int:
            if len(pos_arguments) < 1:
                return False
            elif len(pos_arguments) > 1:
                return False
            else:
                try:
                    self.arguments[self.positional_arguments.arg_name] = int(pos_arguments[0])
                    return True
                except ValueError:
                    return False

    def validate_and_cast_named_arguments(self, named_args):
        for arg_name, arg_value in named_args.items():
            arg = None
            for arg_parsed in self.args_parsed:
                if arg_parsed.arg_name == arg_name:
                    arg = arg_parsed
                    break
            if not self.args_parsed:
                return False
            if arg.arg_type == str:
                if len(arg_value) < 1:
                    raise ArgumentException("Expected argument {} to be a string, but it was not called with a value!".format(" ".join(self.get_flags_from_id(arg_name))))
                    return False
                elif len(arg_value) > 1:
                    raise ArgumentException("Expected argument {} to be a single string but multiple values were found!".format(" ".join(self.get_flags_from_id(arg_name))))
                    return False
                else:
                    self.arguments[arg_name] = arg_value[0]
            elif arg.arg_type == list:
                self.arguments[arg_name] = arg_value
            elif arg.arg_type == int:
                if len(arg_value) < 1:
                    raise ArgumentException("Expected argument {} to be a integer, but it was not called with a value!".format(" ".join(self.get_flags_from_id(arg_name))))
                    return False
                elif len(arg_value) > 1:
                    raise ArgumentException("Expected argument {} to be a inteher, but it was called with multiple values!".format(" ".join(self.get_flags_from_id(arg_name))))
                    return False
                else:
                    try:
                        self.arguments[arg_name] = int(arg_value[0])
                        return True
                    except ValueError:
                        raise ArgumentException("Expected argument {} to be a integer but, but {} cannot be cast to an integer!".format(" ".join(self.get_flags_from_id(arg_name)), arg_value))
                        return False
        return True


    # Take in everything past the positional args and turn them into a dictionary of flag-value pairs
    def isolate_named_args_into_a_dict(self, named_args):
        named_args_str = " ".join(named_args)
        named_args_dict = {}
        found_flags_in_sysargs = []
        for word in named_args:
            if self.is_a_defined_flag(word):
                found_flags_in_sysargs.append(word)
        for i in range(len(found_flags_in_sysargs)):
            if i == len(found_flags_in_sysargs)-1:
                arg = named_args_str.split(" ")[0]
                value =  named_args_str.split(" ")[1]
                named_args_dict[self.get_id_from_flag(arg)] = value
                break
            # captures everything between the first character up until the next flag
            re_arg_and_values = re.search(r"^({}.*)(?= {})".format(found_flags_in_sysargs[i], found_flags_in_sysargs[i+1]), named_args_str)
            # captures everything that follows the above substring
            re_rest           = re.search(r"({}.*)$".format(found_flags_in_sysargs[i+1]), named_args_str)
            arg = re_arg_and_values.group(0).split(" ")[0]
            value = re_arg_and_values.group(0).split(" ")[1:]
            named_args_dict[self.get_id_from_flag(arg)] = value
            # shorten the string as we go
            named_args_str = re_rest.group(0)
        # To keep it consistent, every value must be an array, even if there's no value (is a store_true arg) or if the value is a single string.
        # There will be a validation later, but I think it should not belong here to avoid confusing code.
        for key, val in named_args_dict.items():
            if type(val) == str:
                named_args_dict[key] = [val]
            elif val == "":
                named_args_dict[key] = []
        return named_args_dict

    def get_positional_arguments_from_sysargs(self):
        sys_args_str = " ".join(self.sys_args[1:])
        pos_args_str = ""
        for i, word in enumerate(sys_args_str.split(" ")):
            # Match with the first defined flag, everything before that belongs to positional arguments
            if self.is_a_defined_flag(word):
                if i != 0 and not self.positional_arguments:
                    raise ArgumentException("This program does not expect positional arguments!")
                elif i == 0 and self.positional_arguments:
                    if self.positional_arguments.required:
                        raise ArgumentException("This program expects positional arguments!")
                pos_args_str = " ".join(sys_args_str.split(" ")[:i])
                rest = " ".join(sys_args_str.split(" ")[i:])
                break
        return pos_args_str.split(" "), rest.split(" ")

    def is_a_defined_flag(self, word):
        for accepted_flag in self.accepted_flags:
                if accepted_flag == word:
                    return True
        return False

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
    
    # Debugging
    def readable(self):
        # Prints arguments that were used in cmd
        for ua in self.arguments:
            print("{}: {}".format(ua, self.arguments[ua]))
        if self.required_args:
            print("\nPositional argument name: {}\nHelp: {}".format(self.positional_arguments.arg_name, self.positional_arguments.help))
        # Prints arguments that were defined
        for arg in self.args_parsed:
            print("\nArgument name: {}\nValid Flags: {}\nStore true: {}\nHelp: {}\nValue: {}".format(arg.arg_name, 
            list(arg.valid_flags), arg.store_true, arg.help, arg.arg_value))

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
    # TODO value does not come here anymore
    arg_value = None
    required = False
    # So this will be default, however in add_arg method call the default is None
    arg_type = str
    def __init__(self, name, flags, store_true, help, required, arg_type):
        self.valid_flags = flags
        self.store_true = store_true
        self.help = help
        self.required = required
        self.arg_name = name
        if arg_type:
            self.arg_type = arg_type
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
    arg_type = str
    def __init__(self, name, help, required, arg_type):
        self.arg_name = name
        self.help = help
        self.required = required
        if arg_type:
            self.arg_type = arg_type
    def __str__(self):
        return " ".join(self.arg_value)

if __name__ == "__main__":
    sys.exit("This is not a runnable script!")
