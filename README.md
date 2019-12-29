# argparser
Argument parser for Python

## Usage  
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
--delete, -d                  Use this flag to delete files
-f                            Test
```