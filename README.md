# argparser
Argument parser for Python

## Usage  

Initialize Arger object by calling ```arger.Arger()```. The following methods can be interacted with: 
  
```add_positional_arg(name, help="", required=False, arg_type=None)```  
This method is used to define positional arguments, that is (usually) the main arguments that don't need an argument flag. ```name```  is used to identify the argument, ```help``` is a string for the help text. If ```required``` is True, the library will raise an ArgumentException if no positional arguments were used. ```arg_type``` supports str, int and list for now.  
  
Positional arguments may appear in the beginning or the ending of the command. If positional arguments is expected to be a list, it can only appear in the beginning.  
  
```add_arg(name, *flags, help="", store_true=False, required=False, arg_type=None)```  
This methdod is used to define "named arguments", that means arguments that are grouped by the flags that were defined here. There may be multiple flags and they don't have to start with a dash (however this is not recommended). ```store_true``` may be used if the argument value should be a boolean value. Its value will be True if the flag is used in system arguments and will otherwise be False.  
  
```parse()```  
Parses arguments from command line and validates them against the arguments that were previously defined.  
  
```readable()```   
Mostly for debugging purposes, see below in code examples.  
  
```get_arg(name)```  
Main way to access argument values.  
  
### Examples
```
import arger

ap = arger.Arger()
ap.add_positional_arg("files", arg_type=list, help="Files that you want selected", required=True)
ap.add_arg("append", "-a", "--append", help="Use this flag to append files")
ap.add_arg("delete", "--delete", "-d", arg_type=list, required=True, help="Use this flag to delete files")
ap.add_arg("test_flag", "-f", store_true=True, help="Test")
ap.parse()
ap.readable()
```
```
>> python3 test.py file1 file2 -a abc -d file3 file4 -f
```
```
files: ['file1', 'file2']
append: abc
delete: ['file3', 'file4']
test_flag: True

Positional argument name: files
Help: Files that you want selected

Argument name: append
Valid Flags: ['-a', '--append']
Store true: False
Help: Use this flag to append files

Argument name: delete
Valid Flags: ['--delete', '-d']
Store true: False
Help: Use this flag to delete files

Argument name: test_flag
Valid Flags: ['-f']
Store true: True
Help: Test
```
  
```
pos_arg = ap.get_arg("files")
print("Positional arguments:", pos_arg)
```
```
Positional arguments: ['file1', 'file2']
```
```
>> python3 test.py -h
```

```
usage: test.py files [-a|--append append] --delete|-d delete [-f test_flag] 

Positional arguments:
files                         Files that you want selected (required)

Required arguments:
--delete, -d                  Use this flag to delete files

Non-required arguments:
-a, --append                  Use this flag to append files
-f                            Test
```