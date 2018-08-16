import json
import os
import subprocess
import re
import sys
from .io_util import *
from .link import Link, LinkStatus



class DotFiles:
    def __init__(self, dotfiles_path, config):
        links = []
        target_dirs = {
            'default': {
                'darwin': '$HOME',
                'linux': '$XDG_CONFIG_HOME',
                'linux2': '$XDG_CONFIG_HOME',
                'win32': '%APPDATA%',
                'cygwin': '%APPDATA%'
            }
        }

        if not os.path.exists(dotfiles_path):
            raise Exception(f"Dotfiles directory '{dotfiles_path}' does not exist")
        for (dirpath, _, filenames) in os.walk(dotfiles_path):
            for filename in filenames:
                if filename in config.ignore:
                    continue
                source_path = os.path.join(dirpath, filename)
                rel_path = os.path.relpath(source_path, dotfiles_path)
                target_dir = None
                config_section = config.get_section('file', rel_path)
                if config_section is not None:
                    target_dir = config_section.get_property(f'path_{sys.platform}')
                if target_dir is None:
                    target_dir = DotFiles.get_default_config_dir()
                target_path = os.path.join(target_dir, rel_path)
                links.append(Link(source_path, target_path))
        
        self.dotfiles_path = dotfiles_path
        self.links = links


    @staticmethod
    def get_default_config_dir():
        if sys.platform in ('win32', 'cygwin'):
            return '%APPDATA%'
        elif sys.platform in ('linux', 'linux2'):
            return '$XDG_CONFIG_HOME'
        else:
            return '$HOME'


    def link(self, files=None, force=False, interactive=False, preview=False):
        links = None
        if len(files) > 0:
            links = []
            for rel_path in files:
                link = self.__find_link__(rel_path)
                if link is None:
                    print(f"Skipped file {rel_path}; unable to find source file")
                    continue
                links.append(link)
        else:
            links = []
            for link in self.links:
                if link.status != LinkStatus.LINKED:
                    links.append(link)
        for link in links:
            rel_path = self.__get_rel_path__(link.source_path)
            target_dir = os.path.dirname(link.target_path)
            status = link.status
            if not os.path.exists(target_dir):
                if force or (interactive and boolean_input(f"Target directory {target_dir} does not exist, create it")):
                    if not preview:
                        try:
                            os.makedirs(target_dir)
                        # guard against race condition
                        except OSError as exc:
                            if exc.errno != errno.EEXIST:
                                raise
                else:
                    print(f"Skipped file {rel_path}; target directory {target_dir} does not exist")
                    continue
            if status == LinkStatus.LINKED:
                if force or (interactive and boolean_input(f"File {rel_path} is already linked, re-link it")):
                    if not preview:
                        os.remove(link.target_path)
                        link.link()
                    print(f"Relinked file {rel_path}")
                else:
                    print(f"Skipped file {rel_path}; file is already linked correctly")
                    continue
            elif status == LinkStatus.INVALID:
                if force or (interactive and boolean_input(f"File {link.target_path} aready exists and is not linked to {link.source_path}, delete it and create link")):
                    if not preview:
                        os.remove(link.target_path)
                        link.link()
                    print(f"Overwrote file with link {rel_path}")
                else:
                    print(f"Skipped file {rel_path}; file already exists at target path")
                    continue
            elif status == LinkStatus.NOLINK:
                if not interactive or boolean_input(f"Link {rel_path} does not exist, create it"):
                    if not preview:
                        link.link()
                print(f"Linked file {rel_path}")
            else:
                print(f"Skipped file {rel_path}; unexpected status {status.name}")
                continue


    def list(self, type=None):
        link_data = []
        for link in self.links:
            if type is not None and link.status != type:
                continue
            data = []
            status = link.status
            data.append(f'\033[{str(status.color)}m[{status.symbol}]\033[0m')
            rel_path = self.__get_rel_path__(link.source_path)
            data.append(rel_path)
            data.append(link.target_path.replace(rel_path, ''))
            link_data.append(data)
        print_columns(link_data)


    def info(self, rel_path, contents=False):
        data = []
        link = self.__find_link__(rel_path)
        if link is None:
            raise Exception(f"Unable to find link with relative path {rel_path}")
        data.append(['Relative Path:', rel_path])
        data.append(['Status:', link.status.name])
        data.append(['Source Path:', link.source_path])
        data.append(['Target Path:', link.target_path])
        if link.existing_target_path != None:
            data.append(['  Existing Target Source Path:', link.existing_target_path])
        print_columns(data)
        if contents:
            with open(link.source_path, 'r') as file_handle:
                print()
                print('--------------------------------------------------------')
                print()
                print(file_handle.read().rstrip())

    
    def edit(self, rel_path):
        link = self.__find_link__(rel_path)
        if link is None:
            raise Exception(f"Unable to find link with relative path {rel_path}")
        if sys.platform == 'win32' or sys.platform == 'cygwin':
            subprocess.call([link.source_path])
        else:
            editor = os.getenv('EDITOR')
            if editor is None:
                if sys.platform == 'darwin':
                    editor = 'open'
                elif sys.platform == 'linux' or sys.platform == 'linux2':
                    editor = 'xdg-open'
            if editor is None:
                raise Exception("Unable to file default editor")
            subprocess.call([editor, link.source_path])
            
        

    def __find_link__(self, rel_path):
        result = None
        for link in self.links:
            if rel_path == self.__get_rel_path__(link.source_path):
                result = link
                break
        return result


    def __get_rel_path__(self, source_path):
        return os.path.relpath(source_path, self.dotfiles_path)



class DotConfigSection:
    def __init__(self, name, subsection_name):
        self.name = name
        self.subsection_name = subsection_name
        self.__properties = {}


    def add_property(self, key, value):
        self.__properties[str(key).strip()] = str(value).strip()

    
    def remove_property(self, key):
        if key in self.__properties:
            self.__properties.pop(key) 

    
    def get_property(self, key):
        if key in self.__properties:
            return self.__properties[key]



class DotConfig:
    def __init__(self, config_dir):
        self.path = os.path.join(config_dir, '.dotconfig')
        self.ignore_path = os.path.join(config_dir, '.dotignore')
        self.config = DotConfig.__load_config(self.path)
        self.ignore = DotConfig.__load_ignore(self.config, self.ignore_path)
    

    def get_section(self, name, subsection_name = None):
        for section in self.config:
            if section.name == name and (subsection_name is None or section.subsection_name == subsection_name):
                return section
    

    @staticmethod
    def __load_config(path):
        sections = []
        if os.path.exists(path):
            section_re1 = re.compile(r'\[\s*(.*)\s+\"(.*)\"\s*\]')
            section_re2 = re.compile(r'\[\s*(.*)\s*\]')
            with open(path, 'r') as fp:
                current_section = None
                for line in fp:
                    line = line.strip()
                    if line == '':
                        continue
                    elif line.startswith('['):
                        section_match = section_re1.match(line)
                        if not section_match:
                            section_match = section_re2.match(line)
                        if not section_match:
                            raise Exception(f".dotconfig section is invalid: '{line}'")
                        groups = section_match.groups()
                        section_name = groups[0]
                        subsection_name = None
                        if len(groups) > 1:
                            subsection_name = groups[1]
                        if current_section is not None:
                            sections.append(current_section)
                        current_section = DotConfigSection(section_name, subsection_name)
                    else:
                        kvp = line.split('=', 1)
                        if len(kvp) != 2:
                            raise Exception(f".dotconfig parameter is invalid: '{line}'")
                        if current_section is None:
                            raise Exception(f".dotconfig parameter must be part of section: '{line}")
                        current_section.add_property(kvp[0], kvp[1])
                if current_section is not None:
                    sections.append(current_section)
        return sections
                    
                    
    @staticmethod
    def __load_ignore(config, default_ignore_path):
        ignored_files = []
        ignore_path = default_ignore_path
        for section in config:
            if section.name != 'ignore':
                continue
            path = section.get_property('path')
            if path is not None:
                ignore_path = path
            break
        ignore_path = os.path.realpath(os.path.expandvars(os.path.expanduser(ignore_path)))
        if os.path.exists(ignore_path):
            with open(ignore_path, 'r') as fp:
                for line in fp:
                    ignored_files.append(line.strip())
        return ignored_files