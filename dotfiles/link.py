import enum
import os



class LinkStatus(enum.Enum):
    NOLINK = 0,
    INVALID = 1,
    LINKED = 2


    @property
    def color(self):
        if self == LinkStatus.NOLINK:
            return 94
        elif self == LinkStatus.INVALID:
            return 91
        elif self == LinkStatus.LINKED:
            return 92
        else:
            return 0
    

    @property
    def symbol(self):
        if self == LinkStatus.NOLINK:
            return ' '
        elif self == LinkStatus.INVALID:
            return '×'
        elif self == LinkStatus.LINKED:
            return '✓'
        else:
            return '?'

    
    @staticmethod
    def from_string(s):
        for status in list(LinkStatus):
            if str(status) == s.lower():
                return status
        raise ValueError()
    

    def __str__(self):
        return self.name.lower()



class Link:
    def __init__(self, source_path, target_path):
        self.source_path = Link.__expand_path__(source_path)
        self.target_path = Link.__expand_path__(target_path)


    @property
    def status(self):
        if self.is_linked:
            return LinkStatus.LINKED
        elif self.is_invalid_target_present:
            return LinkStatus.INVALID
        else:
            return LinkStatus.NOLINK


    @property
    def is_linked(self):
        return os.path.islink(self.target_path) and os.readlink(self.target_path) == self.source_path


    @property
    def is_invalid_target_present(self):
        return (
            (os.path.exists(self.target_path) and not os.path.islink(self.target_path)) or
            (os.path.islink(self.target_path) and os.readlink(self.target_path) != self.source_path)
        )


    @property
    def existing_target_path(self):
        result = None
        if os.path.exists(self.target_path) and os.path.islink(self.target_path):
            result = os.readlink(self.target_path)
        return result


    def link(self):
        if os.path.exists(self.target_path):
            raise Exception(f"Target path {self.target_path} already exists")
        elif not os.path.exists(self.source_path):
            raise Exception(f"Source path {self.source_path} does not exist")
        os.symlink(self.source_path, self.target_path)

    
    @staticmethod
    def __expand_path__(path):
        return os.path.abspath(os.path.expandvars(os.path.expanduser(path)))