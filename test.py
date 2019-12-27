
import arger

ap = arger.Arger()
ap.add_arg("append", "-a", "abc")
ap.add_arg("test1", "--delete", "-d", required=True)
ap.add_arg("test2", "-f", store_true=True, help="Test")
ap.parse()
ap.readable()
