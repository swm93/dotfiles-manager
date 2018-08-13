import json
import os
import subprocess
import sys
from .io_util import *
from .link import Link, LinkStatus



class DotFiles:
    def __init__(self, dotfiles_dir):
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
        ignored_files = []

        config_dir = os.path.join(dotfiles_dir, 'config')
        overrides_path = os.path.join(dotfiles_dir, 'overrides.json')
        ignored_files_path = os.path.join(dotfiles_dir, 'ignored_files.json')
        
        if not os.path.exists(config_dir):
            raise Exception(f'Config directory {config_dir} does not exist')
        if os.path.exists(overrides_path):
            with open(overrides_path, 'r') as file_handle:
                overrides = json.load(file_handle)
                target_dirs = {**overrides, **target_dirs}
        if os.path.exists(ignored_files_path):
            with open(ignored_files_path, 'r') as file_handle:
                ignored_files = json.load(file_handle)
        for (dirpath, _, filenames) in os.walk(config_dir):
            for filename in filenames:
                if filename in ignored_files:
                    continue
                source_path = os.path.join(dirpath, filename)
                rel_path = os.path.relpath(source_path, config_dir)
                target_dir = None
                if rel_path in target_dirs and sys.platform in target_dirs[rel_path]:
                    target_dir = target_dirs[rel_path][sys.platform]
                elif 'default' in target_dirs and sys.platform in target_dirs['default']:
                    target_dir = target_dirs['default'][sys.platform]
                else:
                    raise Exception(f'Unable to find target directory for file {rel_path}')
                target_path = os.path.join(target_dir, rel_path)
                links.append(Link(source_path, target_path))
        
        self.dotfiles_path = config_dir
        self.links = links


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
                print('--------------------------------------------------------')
                print(file_handle.read())

    
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
