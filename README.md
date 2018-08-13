# Dotfiles Manager

## Usage
```
usage: dotfiles [-h] [--version] [-d DIRECTORY] {link,list,info,edit} ...

A management system for configuration files.

positional arguments:
  {link,list,info,edit}
    link                create links for configuration files
    list                list available configuration files
    info                display information for a specific configuration file
    edit                edit a configuration file

optional arguments:
  -h, --help            show this help message and exit
  --version             print version and exit
  -d DIRECTORY, --directory DIRECTORY
                        path to dotfiles directory; if not specified
                        $DOTFILES_PATH must be set
```
