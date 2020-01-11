import os 
import sys

import shutil 
import re

dl_dir = '/home/acarnec/Downloads/'
college_dir = '/home/acarnec/Documents/3rdYear'
latex_dir = '/home/acarnec/Documents/Latex/'

modules = ['mta', 'ana', 'met', 'log', 'mat',
           'lin', 'min', 'pol', 'mic', 'mte']

michaelmas = ['mta', 'ana', 'met', 'log', 'mat']
hilary = ['lin', 'min', 'pol', 'mic', 'mte']

types = ['A', 'H', 'Q', 'N', 'R', 'T', 'S', 'M']
nonlinkables = ['Q','R','T', 'S', 'M']

exts = ['pdf', 'tex', 'djvu', 'xlsx', 'epub']
#script, path = sys.argv  

def change_directory(path):
    """ 
    Changes directory to path. 
    """
    os.chdir(path)

def list_files(path):
    """
    Returns a list of the filenames in the directory. 
    """
    ls_output = os.listdir(path)
    return ls_output

def move_file_to_dir(f, dest_dir):
    """
    moves a file to dest_dir if it not already there
    """
    ls = list_files(dest_dir)
    if f not in ls:
        shutil.move(f, dest_dir)

def get_key_from_values(f, catalog):
    """
    Gets the full associated with the filename in the catalog.
    """
    L_keys = []
    L_values = []
    for path, files in catalog.items():
        if f in catalog[path]:
            return path

def make_sym_links(f, source, dest_dir, catalog):
    """
    Gets file origin and makes symlink at destination.
    """
    source = get_key_from_values(f, catalog)
    source_path = f"{source}/{f}"
    dest_path = f"{dest_dir}/{f}"
    ls = os.listdir(dest_dir)
    if f not in ls: 
        os.symlink(source_path, dest_path)

def define_regex(module_names=modules, doc_types=types, exts=exts):
    """
    Defines a regex in function of the global lists at the top of the program.
    """
    letters = ''
    module_codes = ''
    file_exts = ''
    # Populate code letter String
    for letter in doc_types:
        letters += letter
    # Populate extension string
    for ext in exts:
        if ext != exts[-1]:
            file_exts += f"{ext}|"
        else:
            file_exts += ext
    # Populate modules string
    for module in modules:
        if module != modules[-1]:
            module_codes += f"{module}|"
        else:
            module_codes += module
    regex = r"(" + module_codes + "){1}[" + letters + "]{1}\_[^.]*\.(" + file_exts + ")" 
    return regex


def recognize_files(list_of_filenames): 
    """
    Matches list of filenames for pattern defined by the regex
    and returns a list of those files
    """
    reg_exp = define_regex()
    pattern = re.compile(reg_exp) 
    matched = []
    for filename in list_of_filenames:
        match = pattern.match(filename)
        if match != None:
            matched.append(filename)
    return matched

def catalog_files(directory):
    """
    Returns a dictionary of matched files as values and
    their respective directories as keys.
    """
    catalog = {}
    for dirpath, filename, files in os.walk(directory):
        catalog[dirpath] = files
    for dirpath, files in catalog.items():
        matched_files = recognize_files(files)
        catalog[dirpath] = matched_files
    return catalog


def sort_into_modules(catalog, modules=modules, types=types):
    """
    Returns a dictionary with module:associated file list as kv pair.
    """
    subject_dict = {}
    for code in modules:
        subject_dict[code] = []
    for files in catalog.values():
        for f in files:
            for code in modules:
                if code == f[:3]:
                    subject_dict[code].append(f)

    return subject_dict


def sort_into_type(subject_dict, modules=modules, types=types):
    """
    Returns dictionary with (module, type code):associated file list
    as kv pair.
    """
    subject_type_dict = {}
    for code in modules:
        for t in types:
            subject_type_dict[(code,t)] = []
    
    for files in subject_dict.values():
        for f in files:
            # f[:3] is module and f[3] is type
            subject_type_dict[(f[:3] ,f[3])].append(f)
    # Take out empty lists
    subject_type_dict = {t:l for t, l in subject_type_dict.items() if l != []}
            
    return subject_type_dict

def sort_to_dest_dir(subject_type_dict,
                     catalog,
                     dest_dir=college_dir, 
                     sym_link_check=nonlinkables, 
                     michaelmas=michaelmas):
    """
    Iterates through module type dictionary and specifies destination 
    in college_dir in accordance to filename, if file is of a certain 
    type, it is moved to destination, otherwise a symbolic link is made. 
    """
    for code_type, files in subject_type_dict.items():
        if code_type[0] in michaelmas:
            destination = f"{college_dir}/Michaelmas_Term/{code_type[0]}/{code_type[1]}"
        else:
            destination = f"{college_dir}/Hilary_Term/{code_type[0]}/{code_type[1]}"
        for f in files:
            if code_type[1] in nonlinkables:
                move_file_to_dir(f, destination) 
            else:
                if '.pdf' in f:
                    source = get_key_from_values(f, catalog)
                    make_sym_links(f, source, destination, catalog)
                else:
                    pass
                



def main(sort_origin):
    script, argument = sys.argv
    # Change to directory to operate upon files
    change_directory(sort_origin)
    # Make a dictionary to track file location in sort_origin
    catalog = catalog_files(sort_origin)
    # Sort into dict with module:files
    subject_dict = sort_into_modules(catalog)
    # Sort into dict with (module, type):files
    subject_type_dict = sort_into_type(subject_dict)
    # Sort files into their respective folders
    sort_to_dest_dir(subject_type_dict, catalog) 

script, argument = sys.argv

if argument == 'lat':
    sort_origin = latex_dir
    main(sort_origin)
elif argument == 'dl':
    sort_origin = dl_dir
    main(sort_origin)
elif argument == 'all':
    main(sort_origin=latex_dir)
    main(sort_origin=dl_dir)
else:
    msg = "dl for downloads\nlat for latex\nall for both"
    print(msg)
