import sys
from argparse import ArgumentParser, Namespace
from typing import List, Optional
from pyinjector import inject
from pyinjector.api import PyInjectorError


def parse_args(args: Optional[List[str]]) -> Namespace:
    parser = ArgumentParser(description='Inject a dynamic library to a running process.')
    parser.add_argument('pid', type=int, help='pid of the process to inject the library into')
    parser.add_argument('library_path', type=str.encode, help='path of the library to inject')
    parser.add_argument('-u', '--uninject', action='store_true', help='Whether to uninject the library after injection')
    parser.add_argument('--process-root', type=str.encode, help="Path to the target's filesystem root if in a container or chroot jail.")
    return parser.parse_args(args)


def main(args: Optional[List[str]] = None) -> None:
    parsed_args = parse_args(args)
    try:
        handle = inject(parsed_args.pid, parsed_args.library_path, parsed_args.uninject, parsed_args.process_root)
    except PyInjectorError as e:
        print(f"pyinjector failed to inject: {e}", file=sys.stderr)
    else:
        print(f"Handle: {handle}")


if __name__ == '__main__':
    main()
