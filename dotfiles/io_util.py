import os



def print_columns(data, padding=2):
    column_widths = []
    for row in data:
        for (i, column) in enumerate(row):
            if len(column_widths) <= i:
                column_widths.append(len(column))
            else:
                column_widths[i] = max(column_widths[i], len(column))
    for row in data:
        row_str = ""
        for (i, column) in enumerate(row):
            if i < (len(row) - 1):
                row_str += column.ljust(column_widths[i] + padding)
            else:
                row_str += column
        print(row_str)


def boolean_input(message):
    response = None
    response_valid = False
    while not response_valid:
        print(f"{message}, (y)es or (n)o?")
        response = input().lower()
        response_valid = (response == 'yes' or response == 'y' or response == 'no' or response == 'n')
    return response == 'yes' or response == 'y'


def expand_path(path):
    return os.path.realpath(os.path.expandvars(os.path.expanduser(path)))