import argparse
import os
import pkg_resources
import sys
from .dotfiles import DotFiles, DotConfig
from .link import LinkStatus



def main():
    dotfiles = None

    parser = argparse.ArgumentParser(description='A management system for configuration files.')
    parser.add_argument('--version', action='store_true', help='print version and exit')
    parser.add_argument('-d', '--directory', required=os.getenv('DOTFILES_PATH') is None, default=os.getenv('DOTFILES_PATH'), help='path to dotfiles directory; if not specified $DOTFILES_PATH must be set')

    subparsers = parser.add_subparsers(dest='command')

    link_parser = subparsers.add_parser('link', help='create links for configuration files')
    link_parser.set_defaults(func=lambda dotfiles, args: dotfiles.link(files=args.files, force=args.force, interactive=args.interactive, preview=args.preview))
    link_parser.add_argument('-f', '--force', action='store_true', help='overwrite existing files in target directory')
    link_parser.add_argument('-i', '--interactive', action='store_true', help='prompt to override existing files in target directory')
    link_parser.add_argument('-p', '--preview', action='store_true', help='show output, but do not create links')
    link_parser.add_argument('files', nargs='*', help='files to create links for; if not specified all links will be created')

    list_parser = subparsers.add_parser('list', help='list available configuration files')
    list_parser.set_defaults(func=lambda dotfiles, args: dotfiles.list(type=args.type))
    list_parser.add_argument('-t', '--type', type=LinkStatus.from_string, choices=list(LinkStatus), help='type of links to display; if not specified all links will be displayed')

    info_parser = subparsers.add_parser('info', help='display information for a specific configuration file')
    info_parser.set_defaults(func=lambda dotfiles, args: dotfiles.info(args.file, contents=args.contents))
    info_parser.add_argument('-c', '--contents', action='store_true', help='display the file contents')
    info_parser.add_argument('file', help='file to display information for')

    edit_parser = subparsers.add_parser('edit', help='edit a configuration file')
    edit_parser.set_defaults(func=lambda dotfiles, args: dotfiles.edit(args.file))
    edit_parser.add_argument('file', help='file to edit')

    args = parser.parse_args()

    try:
        if args.version:
            __print_version__()
        elif not 'func' in args:
            parser.print_help()
        else:
            dotfiles_dir = os.path.realpath(os.path.expandvars(os.path.expanduser(args.directory)))
            config_dir = os.path.realpath(os.path.expandvars(os.path.expanduser(DotFiles.get_default_config_dir())))
            config = DotConfig(config_dir)
            dotfiles = DotFiles(dotfiles_dir, config)
            args.func(dotfiles, args)
    except Exception as ex:
        print(f'\033[91m{ex}\033[0m')
        sys.exit(1)


def __print_version__():
    package = pkg_resources.require("dotfiles")[0]
    print(package)



if __name__ == '__main__':
    main()
