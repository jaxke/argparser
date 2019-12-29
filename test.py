import arger

ap = arger.Arger()
ap.add_positional_arg("files", arg_type=list, help="Files that you want selected", required=True)
ap.add_arg("append", "-a", "--append", help="Use this flag to append files")
ap.add_arg("delete", "--delete", "-d", arg_type=list, required=True, help="Use this flag to delete files")
ap.add_arg("test_flag", "-f", store_true=True, help="Test")
ap.parse()
ap.readable()