HEAD ="""[files]
%(file_list)s

[fields]
%(fields)s
"""
FILE_BLOCK = """

# ---------------------------------------
# %(file_name)s
# ---------------------------------------
[%(section_name)s]
pages:%(pages)s\n
"""

PAGE_BLOCK = """

# ***************************************
[%(section_name)s:%(page_name)s]
%(value_list)s
[%(section_name)s:%(page_name)s:fields]
%(names_list)s

[%(section_name)s:%(page_name)s:flags]
# flags are are constructed like: 'target : name ? value, name2 ? value2, ..'
# example: all : source ? filexy
# where target is all, name is source, value is filexy
%(flag_list)s"""
