"""
The command line interface for personio_py.

If you're calling this module from Python instead of using the cli, please use the
``cli.main()`` function and pass your arguments as array of strings.
"""
import argparse
import sys

from personio_py import __version__


def main(*args: str):
    """
    The main function, point of entry for the CLI.
    Creates the command line parser, parses the provided args (if any)
    and executes the desired functions.

    :param args: these are interpreted as command line args, if specified.
           Otherwise, sys.argv is used (the actual command line args).
    """
    parsed_args = parse_args(*args)
    # TODO your journey starts here


def parse_args(*args: str) -> argparse.Namespace:
    """
    Specifies the command line argument parser using the builtin argparse module and parses
    the command line args that were given to this application (if any).

    There are two exceptions to this behaviour:

    * --version: prints the current program version and exits
    * --help: prints usage instructions and exits (argparse default behaviour)

    :param args: these are interpreted as command line args, if specified.
           Otherwise, sys.argv is used (the actual command line args).
    :return: a Namespace object that contains the parsed command line args.
             Note: the program will exit, if the --version or --help flag is specified.
    """
    # define the available command line arguments
    ap = argparse.ArgumentParser(description="personio-py")
    ap.add_argument('-v', '--version', action='store_true',
                    help="prints the current program version and exits")
    # parse the command line arguments
    parsed_args = ap.parse_args(args=args or None)
    # handle the --version flag
    if parsed_args.version:
        print('personio-py ' + __version__)
        sys.exit(0)
    # return the parsed command line args
    return parsed_args
