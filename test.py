
import arger

ap = arger.Arger()
ap.add_positional_arg("files", arg_type=list, help="Files that you want selected", required=True)
ap.add_arg("append", "-a", "--append", help="Use this flag to append files")
ap.add_arg("test1", "--delete", "-d", arg_type=list, required=True, help="Use this flag to delete files")
ap.add_arg("test2", "-f", store_true=True, help="Test")
ap.parse()
ap.readable()

pos_arg = ap.get_arg("files")
print("Positional arguments:", pos_arg)
