# REQUIRES fetools library
# (pip install fetools)s


from fetools.alias import load
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from argparse import ArgumentParser
import xml.etree.ElementTree as ET
import datetime
import gzip
import sys


# Set up argument parser
parser = ArgumentParser()
parser.add_argument("alias_file", help="VRC alias file (.txt format)")
parser.add_argument("facilities", nargs="+", help="One or more vSTARS/vERAM facilities")
# Only parse args if any were provided
args = parser.parse_args() if len(sys.argv)>1 else None


# Hide tkinter window
Tk().withdraw()

# Get .gz facility(s)
if args:
    # Command line mode
    facils = args.facilities
else:
    # Interactive mode
    facils = askopenfilename(
        title="Select vSTARS/vERAM facilities",
        filetypes=[("vSTARS/vERAM facility","*.gz")],
        multiple=True)
    if not facils: sys.exit()

# Get .txt alias file
if args:
    # Command line mode
    alias_file = args.alias_file
else:
    # Interactive mode
    alias_file = askopenfilename(
        title="Select alias file",
        filetypes=[("VRC alias file","*.txt")])
    if not alias_file: sys.exit()

print("Working...")

# Convert alias format
with open(alias_file) as f:
    aliases = load(f).dumpxml()

# Extract CommandAlias tags
aliases = aliases.iterfind(".//CommandAlias")

# Replace each facility's CommandAliases tag with the `aliases` one
for name in facils:
    # Parse facility
    with gzip.open(name) as facility:
        root = ET.parse(facility).getroot()
    # Get current CommandAliases element
    current = root.find(".//CommandAliases")
    # Clear it...
    current.clear()
    # ... and add all the new commands
    for a in aliases:
        current.append(a)
    # Update CommandAliasesLastImported
    time = datetime.datetime.now().astimezone().isoformat()
    root.find(".//CommandAliasesLastImported").text = time
    # Write new facility!
    with gzip.open(name, "w") as facility:
        # (Remember to make it look nice)
        ET.indent(root)
        facility.write(ET.tostring(root))
