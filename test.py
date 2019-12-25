
import arger

ap = arger.Arger()
ap.add_arg("-a")
ap.add_arg("-b", store_true=True, help="Test")
ap.parse()
ap.readable()
