import sys
from argparse import ArgumentParser, Namespace
from typing import List, Optional
from pyinjector import inject
from pyinjector.api import PyInjectorError


def parse_args(args: Optional[List[str]]) -> Namespace:
    parser = ArgumentParser(description='Inject a dynamic library to a running process.')
    parser.add_argument('pid', type=int, help='pid of the process to inject the library into')
    parser.add_argument('library_path', type=str.encode, help='path of the library to inject')
    return parser.parse_args(args)


def main(args: Optional[List[str]] = None) -> None:
    parsed_args = parse_args(args)
    try:
        handle = inject(parsed_args.pid, parsed_args.library_path)
    except PyInjectorError as e:
        print("pyinjector failed to inject: {}".format(e), file=sys.stderr)
    else:
        print(f"Handle: {handle}")


if __name__ == '__main__':
    main()
