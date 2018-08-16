# Dotfiles Manager
Dotfiles Manager is a minimal tool for keeping track of and editing a set of configuration files across platforms. It makes it easy to store all of your configuration files in a single directory regardless of which standard and application follows.

## Getting Started
1. Create a directory for all of your configuration files (see https://github.com/swm93/dotfiles for an example)
0. Find any configuration files that you want Dotfiles Manager to know about and move them to the directory that you just created
0. Define an environment variable called `DOTFILES_PATH` and set its value to the directory you created
0. Run Dotfiles Manager in interactive mode using `dotfiles link -i` and specify whether or not you want to link each of the files in the configuration directory (this is useful when there are platform or host specific configuration files in the configuration directory); if there is already a configuration file at the destination you will be asked if you'd like to overwrite it

That's it! Now you can rest assured knowing that all of your configuration files live under a single directory.

## Installation
In a command prompt navigate to the root of the Dotfiles Manager directory and run:
```
pip3 install -e .
```

## Configuration
Dotfiles Manager will operate on files that exist in the `$DOTFILES_PATH` (or in the directory specifed by the `--directory` flag). To change its default behavior additional settings files can be added that impact settings such as the configuration directory to link a certain file to.

### Default Configuration Directories
By default, configuration files are linked to the following directories:
* Linux: `$XDG_CONFIG_HOME`
* MacOS: `$HOME`
* Windows: `%APPDATA%` 

### .dotconfig
A `.dotconfig` file can be added to the default configuration directory to specify additional options to Dotfiles Manager. The structure of the file loosely resembles that of a `.gitconfig` files; however, you should not assume that the specification is exactly the same.

```
; use a semicolon to begin a comment

[file]                      ; settings that apply to all files
  path =                    ; configuration directory
  {platform_name}_path =    ; configuration directory for a specific plaform

[file ""]                   ; settings for a file
  path =                    ; configuration directory
  {platform_name}_path =    ; configuration directory for a specific plaform

[ignore]                    ; settings for the ignore file
  path =                    ; path to the ignore file
  {platform_name}_path =    ; configuration directory for a specific plaform
```

### .dotignore
A `.dotignore` file can be added to the default configuration directory to specify files that Dotfiles Manager should ignore in the `$DOTFILES_PATH`. This can be useful for ignoring system files that might end up in the `$DOTFILES_PATH` or for ignoring files that aren't needed on a certain platform. Each line in the `.dotignore` file represents a file that should be ignored. Currently wildcards are not supported.

## How It Works
Configuration files are stored in a single directory structure that can be checked in to a source controlled repository. Dotfiles Manager then creates symlinks for all these files in the directories that the applications which use them expect them to be. When you want to list, view or edit a configuration file, Dotfiles Manager knows where the configuration files live and provides a set of commands to interface with them.

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

### Link
```
usage: dotfiles link [-h] [-f] [-i] [-p] [files [files ...]]

positional arguments:
  files              files to create links for; if not specified all links
                     will be created

optional arguments:
  -h, --help         show this help message and exit
  -f, --force        overwrite existing files in target directory
  -i, --interactive  prompt to override existing files in target directory
  -p, --preview      show output, but do not create links
```

### List
```
usage: dotfiles list [-h] [-t {nolink,invalid,linked}]

optional arguments:
  -h, --help            show this help message and exit
  -t {nolink,invalid,linked}, --type {nolink,invalid,linked}
                        type of links to display; if not specified all links
                        will be displayed
```

### Info
```
usage: dotfiles info [-h] [-c] file

positional arguments:
  file            file to display information for

optional arguments:
  -h, --help      show this help message and exit
  -c, --contents  display the file contents
```

### Edit
```
usage: dotfiles edit [-h] file

positional arguments:
  file        file to edit

optional arguments:
  -h, --help  show this help message and exit
```