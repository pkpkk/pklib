import argparse
import sys
import pkg_resources
from .bypass_gdtot import *

distribution = pkg_resources.get_distribution("byp")
class _ShowVersionAction(argparse.Action):
    def __init__(self, *args, **kwargs):
        kwargs["nargs"] = 0
        self.version = kwargs.pop("version")
        super(self.__class__, self).__init__(*args, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        print(
            "gdownh {ver} at {pos}".format(
                ver=self.version, pos=distribution.location
            )
        )
        parser.exit()
def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "-V",
        "--version",
        version=distribution.version,
        action=_ShowVersionAction,
        help="display version",
    )
    parser.add_argument(
        "url", help="""Just call gdownh with --gdrive tag to 
download gdrive links & --ddl tag for direct download 
links Examples: gdownh --gdrive your gdrive link , gdownh --ddl your direct download link"""
    )
    args = parser.parse_args()
    if args.url:
      url=args.url
      if "shortingly" in url:
          t=shortlingly(url)
          print(t)
          return t
      elif "tnlink" in url:
         rt=tnlink(url)
         print(rt)
         return rt
      elif 'gdtot' in url:
          print(gdtot(url))
      elif 'gofile' in url:
           print(gofile_dl(url))
      elif 'anonfile' in url:
            print(anonfile(url))
      elif 'zippyshare' in url:
            print(zippyshare(url))
      elif 'mediafire' in url:
            print(mediafire(url))
      else:
          print("No argument Passed")
          sys.exit(1)
    else:
          print("Nothing")
          sys.exit(2)

if __name__=='__main__':
	main()


