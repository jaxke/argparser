
from pdb import set_trace as st
import sys
import re

# TODO RETURN ERROR IF NOT PARSED IN CLIENT

class Arger:
    sys_args = []
    args_parsed = []
    accepted_flags = []
    positional_arguments = None
    required_args = []
    arguments = {}

    # When testing, override system_arguments with given arg string
    def __init__(self, test_mode_arguments=None):
        self.sys_args = []
        self.args_parsed = []
        self.accepted_flags = []
        self.positional_arguments = None
        self.required_args = []
        self.arguments = {}
        if test_mode_arguments:
            self.sys_args = [x for x in test_mode_arguments.split(" ") if x != ""]
        else:
            self.sys_args = sys.argv

    # Adds argument objects to a list based on definitions.
    def add_arg(self, name, *flags, help="", store_true=False, required=False, arg_type=None):
        if name[0] == "-":
            raise ArgumentException("Argument can not start with a dash! ({})".format(name))
        if self.test_for_id_collisions(name, self.positional_arguments, self. args_parsed):
            raise ArgumentException("Can not define multiple arguments with name \"{}\"!".format(name))
        if self.test_for_flag_collisions(self.args_parsed, flags):
            raise ArgumentException("Multiple different arguments try to use the flag(s) {}!".format(" ".join(flags)))
        self.args_parsed.append(Argument(name, flags, store_true, help, required, arg_type))
        self.accepted_flags.extend(flags)
        if required:
            self.required_args.append(name)

    def add_positional_arg(self, name, help="", required=False, arg_type=None):
        self.positional_arguments = PositionalArgument(name, help, required, arg_type)

    # TODO I'm not sure about returning None?
    def get_arg(self, name):
        if not self.arguments:
            return None
        try:
            return self.arguments.get(name)
        except KeyError:
            if self.positional_arguments and self.positional_arguments.arg_name == name:
                return self.positional_arguments.arg_name
            else:
                return None

    def test_for_id_collisions(self, name, positional_arguments, args_parsed):
        if self.positional_arguments and positional_arguments.arg_name == name:
            return True
        for arg_parsed in args_parsed:
            if arg_parsed.arg_name == name:
                return True
        return False

    def test_for_flag_collisions(self, args_parsed, flags):
        for arg in args_parsed:
            for flag in flags:
                if flag in arg.valid_flags:
                    return True
        return False

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
    # "safe" argument: if True, a value of an argument can start with a dash, for 
    # example if flag -x was not defined but exists in sys args and safe=False,
    # parse() will fail because a dashed word USUALLY is a flag for an argument.
    def parse(self, safe=False):
        if "-h" in self.sys_args:
            self.print_help()
        for word in self.sys_args:
            if word[0] == "-" and word not in self.accepted_flags and safe == False:
                raise ArgumentException("Flag {} has not been defined in this program!".format(word))
        sys_args_str = " ".join(self.sys_args[1:])
        pos_arguments, named_arguments = self.get_positional_arguments_from_sysargs()
        # Consider all that start with - or --, select the words that belong to
        # that argument (that is words that appear before the next space+dash or eol)
        #named_args = re.findall("(-{1,2}.*?)(?= *-|$)", sys_args_str)
        named_args_dict = self.isolate_named_args_into_a_dict(named_arguments)
        if pos_arguments:
            self.arguments = self.validate_and_cast_positional_args(pos_arguments)
        if named_args_dict:
            try:
                self.arguments.update(self.validate_and_cast_named_arguments(named_args_dict, safe))
            except AttributeError:
                self.arguments = self.validate_and_cast_named_arguments(named_args_dict, safe)
        self.validate_requirements_satisfied(pos_arguments, named_args_dict)

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

    def validate_and_cast_positional_args(self, pos_arguments):
        casted_pos_arguments_dict = {}
        # add_positional_arg was never used and therefore unexpected
        if not self.positional_arguments:
            return
        if self.positional_arguments.arg_type == str:
            if len(pos_arguments) < 1:
                raise ArgumentException("Positional argument missing!")
            elif len(pos_arguments) > 1:
                raise ArgumentException("Positional argument must be a single string!")
            else:
                casted_pos_arguments_dict[self.positional_arguments.arg_name] = pos_arguments[0]
        elif self.positional_arguments.arg_type == list:
            casted_pos_arguments_dict[self.positional_arguments.arg_name] = pos_arguments
        elif self.positional_arguments.arg_type == int:
            if len(pos_arguments) < 1:
                raise ArgumentException("Positional argument missing!")
            elif len(pos_arguments) > 1:
                raise ArgumentException("Positional argument must be a single integer!")
            else:
                try:
                    casted_pos_arguments_dict[self.positional_arguments.arg_name] = int(pos_arguments[0])
                except ValueError:
                    raise ArgumentException("Positional argument must be an integer!")
        return casted_pos_arguments_dict

    def validate_and_cast_named_arguments(self, named_args, safe):
        casted_named_arguments_dict = {}
        if not self.args_parsed:
            return
        for arg_name, arg_value in named_args.items():
            """ if self.arg_is_store_true(arg_name) and arg_value:
                raise ArgumentException("Argument {} does not except a value!".format(arg_name)) """
            arg = None
            for arg_parsed in self.args_parsed:
                if arg_parsed.arg_name == arg_name:
                    arg = arg_parsed
                    break
            if not arg.store_true and named_args[arg.arg_name] == []:
                raise ArgumentException("Argument ({}) expects a value!".format(" ".join(arg.valid_flags)))
            if arg.arg_type == str:
                if len(arg_value) < 1:
                    raise ArgumentException("Expected argument {} to be a string, but it was not called with a value!".format(" ".join(self.get_flags_from_id(arg_name))))
                elif len(arg_value) > 1:
                    raise ArgumentException("Expected argument {} to be a single string but multiple values were found!".format(" ".join(self.get_flags_from_id(arg_name))))
                else:
                    casted_named_arguments_dict[arg_name] = arg_value[0]
            elif arg.arg_type == list:
                casted_named_arguments_dict[arg_name] = arg_value
            elif arg.arg_type == int:
                if len(arg_value) < 1:
                    raise ArgumentException("Expected argument {} to be a integer, but it was not called with a value!".format(" ".join(self.get_flags_from_id(arg_name))))
                elif len(arg_value) > 1:
                    raise ArgumentException("Expected argument {} to be a integer, but it was called with multiple values!".format(" ".join(self.get_flags_from_id(arg_name))))
                else:
                    try:
                        casted_named_arguments_dict[arg_name] = int(arg_value[0])
                    except ValueError:
                        raise ArgumentException("Expected argument {} to be a integer but, but {} cannot be cast to an integer!".format(" ".join(self.get_flags_from_id(arg_name)), arg_value))
            elif arg.store_true:
                casted_named_arguments_dict[arg_name] = True
        for arg in self.args_parsed:
            if arg.store_true and arg.arg_name not in named_args.keys():
                # If a store_true arg is defined but not used in system args -> it will default to False for consistency
                casted_named_arguments_dict[arg.arg_name] = False
        return casted_named_arguments_dict
        

    def arg_is_store_true(self, arg_name):
        for arg in self.args_parsed:
            if arg.arg_name == arg_name:
                return arg.store_true
        raise ArgumentException("Unknown error, {} not found?".format(arg_name))

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
                try:
                    value =  named_args_str.split(" ")[1:]
                # This should mean that the LAST argument is a store_true (no values after flag -> instead there's eol)
                except IndexError:
                    if self.arg_is_store_true(self.get_id_from_flag(found_flags_in_sysargs[i])):
                        value = True
                    else:
                        raise ArgumentException("Argument {} expects a value!".format(arg))
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
                named_args_dict[key] = True
        return named_args_dict

    def get_positional_arguments_from_sysargs(self):
        sys_args_str = " ".join(self.sys_args[1:])
        pos_args_str = ""
        rest = ""
        for i, word in enumerate(sys_args_str.split(" ")):
            if self.is_a_defined_flag(word):
                # Match with the first defined flag, everything before that belongs to positional arguments
                # TODO This is faulty logic and this should never happen?
                if i != 0 and not self.positional_arguments:
                    raise ArgumentException("This program does not expect positional arguments!")
                elif i == 0 and self.positional_arguments:
                    if self.positional_arguments.required:
                        raise ArgumentException("This program expects positional arguments!")
                pos_args_str = " ".join(sys_args_str.split(" ")[:i])
                rest = " ".join(sys_args_str.split(" ")[i:])
                break
            else:
                pos_args_str += word
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
        if self.positional_arguments:
            print("\nPositional argument name: {}\nHelp: {}".format(self.positional_arguments.arg_name, self.positional_arguments.help))
        # Prints arguments that were defined
        for arg in self.args_parsed:
            print("\nArgument name: {}\nValid Flags: {}\nStore true: {}\nHelp: {}".format(arg.arg_name, 
            list(arg.valid_flags), arg.store_true, arg.help))


class ArgumentException(Exception):
    # TODO 
    error_messages = {
        "excepts_positional_arguments": "This program expects positional arguments!",
        "can_not_start_with_dash": "Argument {} can not start with a dash!",
        "multiple_args_have_same_flag": "Multiple arguments try to use the flag {}!",
        "flag_not_defined": "Flag {} has not been defined in this program!",
        "argument_required_but_not_used": "Argument {} is required!",
    }
    pass


class Argument:
    possible_types = [bool, int, list, str]
    arg_name = ""
    valid_flags = []
    store_true = False
    help = ""
    required = False
    # So this will be default, however in add_arg method call the default is None
    arg_type = str
    def __init__(self, name, flags, store_true, help, required, arg_type):
        if not flags:
            raise ArgumentException("A named argument needs to have flag(s)! ({})".format(name))
        self.valid_flags = flags
        self.store_true = store_true
        self.help = help
        self.required = required
        self.arg_name = name
        # if arg_type = None, it will become str by default
        if required and store_true:
            raise ArgumentException("Can not define an argument with required=True and store_true=True!")
        elif arg_type and store_true:
            raise ArgumentException("Can not define an argument with store_true=True and arg_type (in {})!".format(name))
        elif store_true:
            self.arg_type = bool
        elif arg_type and arg_type not in self.possible_types:
            raise ArgumentException("Type {} is not supported for a named argument.".format(str(arg_type)))
        elif arg_type:
            self.arg_type = arg_type

class PositionalArgument(Argument):
    possible_types = [int, list, str]
    arg_name = ""
    help = ""
    required = False
    arg_type = str
    def __init__(self, name, help, required, arg_type):
        self.arg_name = name
        self.help = help
        self.required = required
        if arg_type and arg_type not in self.possible_types:
            raise ArgumentException("Type {} is not supported for a positional argument.".format(str(arg_type)))
        elif arg_type:
            self.arg_type = arg_type

if __name__ == "__main__":
    sys.exit("This is not a runnable script!")
