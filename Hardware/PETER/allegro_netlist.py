#!/usr/bin/env python3
# Copyright (c) 2021 Google LLC. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


# WARNING: Allegro is not case sensitive with net names.
#          Be sure to have the "labels are similar" ERC set to flag an error!
# TODO: error out if case-mismatched nets make it through

# NOTE: the Footprint field in KiCad is supposed to be a valid part in the KiCad
#       library, and needs to be specified as Library:File. This won't work well
#       for Allegro-centric designs, so instead the conversion script uses the
#       footprint filter definition to select the Allegro footprint. The first
#       entry in the footprint filter list will correspond to the name of the
#       footprint in allegro (should be the .psm file in one of the PSMPATH
#       directories, minus the .psm). The remaining names will be added as
#       ALT_SYMBOLS, which allow the PCB designer to select from a few options.
#       This is commonly used to allow old footprints that are cached in the
#       board database to continue to be used, or for enabling the selection of
#       more or less aggressive footprint metrics.

# NOTE: Allegro supports pin and function swapping. KiCad does not (see #1950).
#       To enable function/pinswap, we define a syntax for func_* properties
#       that specify function names, a shorthand for selecting pins within each
#       instance of that function, and which pins within a fucntion can also be
#       arbitrarily swapped amongst themselves. If the pinswap/function swap
#       functions are used in Allegro, you will need to bring the swaps back
#       into the schematic somehow. Allegro can export pinswap reports as well
#       as the effective netlist post-swaps ("Netlist w/ Properties"). These
#       swaps can either be manually applied back into the schematic or
#       automatically done so via an additional script. Potential approaches for
#       automatic back-annotation include renaming nets (not always feasible)
#       and auto-generating project-local parts with the pins rearranged
#       (somewhat involved, and doesn't allow for later library updates, but
#       works as long as you don't have multiple instances of a sheet with
#       different effective pin swappings).
#
#       Functions are defined by creating any number of properties named
#       func_name, where name can be anything other than main, which is the
#       default function name given to all remaining pins.
#       The func_* property contents are:
#         group1re1,group1re2,...;group2re1...;groupNre1.....;;swap,indices,...
#       Each group is a bunch of regexes. results for each regex are
#       alphabetically sorted. order between regexes are maintained.
#       All groups must resolve to the same number of pins, and pins can only be
#       in a single group across all functions. Regexes can overlap between
#       groups in a function (first group wins), but must not overlap between
#       functions, since function order isn't guaranteed.
#       Swap indices are optional and are 1-indexed ranges in the group pin list
#       that indicates these pins can be swapped within the group.
#       Alternatively, a * means all pins within the group can be swapped.
#       A single group followed by a ;;* is an easy way to specify a list of
#       pins that can be arbitrarily swapped, without having multiple groups.

# NOTE: Care is taken to output the files in a consistent way, by sorting things
#       that can be sorted. The goals are to minimze diffs in version control
#       (with equivalent netlists having no differences) as well as reasonably
#       match the output of Allegro's "Netlist w/ Properties" output.
#       In addition, we want to minimize the number of device files created,
#       since these tend to get added to version control but never cleaned up.
# TODO: detect extraneous device files in version control and list them out as a
#       report? Make sure it's not annoying if it's intentional, e.g., multiple
#       projects/netlists in the same directory. Easiest way for designer to
#       solve is to just delete the devices directory before generating a
#       netlist again.


import os
import re
import sys

# Import kicad's netlist reader helper.
# This is copied from the kicad install's plugins directory.
sys.dont_write_bytecode = True
import kicad_netlist_reader

# Routines to convert strings into various Telesis-safe output.
# Character safety rules (discovered by trial and error):
# ! and ' in strings will cause errors even if they're 'quoted'.
# Non-ASCII characters will also cause errors.
# Strings that include spaces, +, -, or . need to be 'quoted'.
# Device names cannot include spaces, +, -, /, or .
def format_text(t):
  # Convert a string into Telesis-safe format. Unsupported characters are
  # replaced with ?'s, and the string is quoted if necessary.
  # FIXME: replace unsupported characters with an encoding instead, to avoid
  #        having similar strings mapped to each other
  if not t:
    return ''
  t = re.sub("[!']|[^ -~]", '?', t.replace('\u03BC', 'u'))
  return f"'{t}'" if re.search('[^a-zA-Z0-9_/]', t) else t
def format_net(t):
  # Converts a string into one safe for a Telesis net name.
  # Since nets in Allegro are case-insensitive, make them all uppercase to match
  # Allegro's own output.
  return format_text(t).upper()
def format_dev(t):
  # Converts a string into one safe for a Telesis device name.
  # These are all lowercase and have a more restricted set of characters.
  # FIXME: replace unsupported characters with an encoding instead
  return re.sub('[^a-z0-9_-]', '_', t.lower())
def format_pin(p):
  # Generates a Telesis-compatible pin name from a pin node.
  # Telesis requires all pin names to be unique, and doesn't have separate
  # fields for pin number and pin name/function, so we combine them together to
  # make a unique name that still describes its function if you check pin info.
  # FIXME: replace unsupported characters with an encoding instead
  t = '%s__%s' % (p.get('pin', 'name'), p.get('pin', 'num'))
  return re.sub('[^A-Za-z0-9_+?/-]', '?', t)

def pin_sort_key(p):
  # Provide a sorting key for a pin so that the pin order within a function
  # group is consistent. Consistency is important when matching regexes in
  # pinswap definitions.
  name = p.get('pin', 'name')
  if name and name != '~':
    return name
  return p.get('pin', 'num')

def get_group_field(nl, grp, fields, sanitize=True):
  # Look up a field for a component group, which may have mismatched case, or
  # the component group may not have the field defined and instead the library
  # entry has to be searched.  Returns None if no fields exist.
  # nl: the netlist
  # grp: the component group to query
  # fields: one or more (equivalent) fields to query, in the order specified.
  #         first field that exists is returned.
  # sanitize: if true (default), will format/escape the field for Telesis output
  if isinstance(fields, str):
    fields = (fields,)
  for field in fields:
    # FIXME: redo this logic to do a case-insensitive search of fields rather
    #        than guessing some common alternative forms.
    field = (nl.getGroupField(grp, field)
          or nl.getGroupField(grp, field.upper())
          or nl.getGroupField(grp, field.lower())
          or nl.getGroupField(grp, field.capitalize()))
    if field:
      return format_text(field) if sanitize else field
  return None

def find_group_functions(group):
  # Searches a component group (and associated library) for function/pinswap
  # definitions and returns a list of all the names of functions in alphabetical
  # order. Component definitions will override library ones.
  field_names = set()
  for c in group:
    field_names.update((f.lower() for f in c.getFieldNames()))
  libpart = group[0].getLibPart()
  if libpart:
    field_names.update((f.lower() for f in libpart.getFieldNames()))
  functions = []
  for f in field_names:
    if f.startswith('func_'):
      functions.append(f[5:])
  return sorted(functions)

def format_function(name, pin_groups, swap_indices=None):
  # Generates the definition of a function in Telesis format, which consists of
  # multiple declarations (PINORDER, PINSWAP, and FUNCTIONs).
  is_multi = len(pin_groups) > 1
  name = name.upper()
  # Only one pin name can be defined across all instances of a function in a
  # part. We don't want to drop the details of the pin name and number, so
  # concatenate all the pin names across groups of the same function.
  # It's ugly, but it's the only way to get these details into Allegro.
  pinnames = list(format_pin(p) for p in pin_groups[0])
  for group in pin_groups[1:]:
    for i in range(len(pinnames)):
      pinnames[i] = '%s____%s' % (pinnames[i], format_pin(group[i]))
  # PINORDER defines all the pin names that go into a function.
  out = format_list('PINORDER %s ' % name, pinnames)
  # PINSWAP specifies which pin names within the function defined above are
  # arbitrarily swappable (e.g., a bunch of swappable GPIOs within a bank of
  # GPIOs that are in turn swappable with another equivalent bank).
  if swap_indices:
    out += format_list('PINSWAP %s ' % name,
                       sorted(pinnames[i] for i in swap_indices))
  # FUNCTION defines the mapping of each pin name to the footprint's pin
  # numbers, for each swappable instance of the function in the part.
  # These numbers are specified in the same order as the names in PINORDER.
  # This is why we only get one pin name across multiple instances of a
  # function, and why we have to make the pin name super ugly to keep details.
  for i, group in enumerate(pin_groups):
    groupname = name + str(i+1)*is_multi
    out += format_list('FUNCTION %s %s ' % (groupname, name), (
                       p.get('pin', 'num') for p in group))
  return out

def format_list(start, items):
  # Formats a list of items into a Telesis-compatible list. Prepends a prefix.
  # Lists are whitespace-separated and can be split across lines using comma as
  # a line continuation character. Long lines need to be split.
  # NOTE: instead of making things pretty and wrapping at Allegro's arbitrary
  # maximum line length (78 characters in the documentation but 1024 characters
  # based on testing), we instead just use line continuation characters and
  # newlines for every element in the list. This also makes diffing much more
  # useful, so it's not only due to laziness.
  return '%s%s\n' % (start, ',\n\t'.join(items))


# Process command line arguments. KiCad seems to specify .xml for output_dir
# regardless of what you did in the file chooser, so handle that case as well.
if len(sys.argv) < 3:
  sys.stderr.write('Usage: %s netlist.xml output_dir\n' % sys.argv[0])
  sys.exit(2)
src = sys.argv[1]
if not os.path.isfile(src):
  sys.stderr.write('KiCAD netlist not found: %s\n' % src)
  sys.exit(1)
if os.path.isdir(sys.argv[2]):
  dest = os.path.join(sys.argv[2], 'netlist.txt')
elif '.' in os.path.basename(sys.argv[2]):
  dest = '%s.txt' % sys.argv[2].rpartition('.')[0]
else:
  dest = '%s.txt' % sys.argv[2]
# Allegro will search many places for device definition files that are
# referenced in the netlist text file. This is configurable (DEVPATH in
# Allegro's env), but the default configuration includes the same directory as
# the netlist itself, which is the most sensible location for our output.
devdir = os.path.join(os.path.dirname(dest), 'devices')

# Load the netlist
nl = kicad_netlist_reader.netlist(src)

# Create the devices directory
os.makedirs(devdir, exist_ok=True)

# Write the netlist file
f = open(dest, 'w')
f.write('(Source: %s)\n' % nl.getSource())
f.write('(Date: %s)\n' % nl.getDate())

# $ SECTION markers are stateful and sometimes affect each other (so
# $A_PROPERTIES will relate to whichever $PACKAGES/$NETS was specified last).

# Start with package definitions, which we create from component groups.
f.write('$PACKAGES\n')
component_groups = nl.groupComponents()
for grp in component_groups:
  # FIXME: what should we do about parts with exclude_from_board set?
  #        Most of the time these will be BOM items that have no pins, so the
  #        following no-pin check will do the right thing. But if they have
  #        pins, do we need to exclude the item *and* remove them from all nets?
  #        We would need to remove subsequently-empty nets as well?
  libpart = grp[0].getLibPart()
  # Don't output components that don't have pins (such as BOM items), as the
  # Telesis format does not support pinless parts.
  if not libpart.element.getChild('pins'):
    continue
  # Generate the device type, which will be the filename for the device file.
  # This name needs to be unique not just for the footprint but also for the
  # properties (at least height, alt footprints, and functions, if not also
  # value and tolerance), so combine the footprint name with the value to get
  # something unique. If the footprint field isn't defined (which it probably
  # isn't in Allegro-centric designs), just use the part name.
  # TODO: It may be possible to not write value and tolerance into the device
  #       file (since it's overridden in the netlist's component list), and then
  #       combine all the parts that have the same properties into a single
  #       device file, named something like footprint_i where i indexes into the
  #       (consistently sorted) sets of properties. This would significantly
  #       reduce the number of device files generated for resistors and caps,
  #       and not create too many additional files as the design progresses
  #       (hashing the properties to generate the name would create a lot of
  #       leftover files in version control as parts change, so don't do that).
  # FIXME: if footprint isn't specified and value is ~ for some reason, this
  #        will create a "_" file that may collide with other similar mixups!
  #        Instead of using the part value, maybe the part name in the library
  #        would be a better choice, or at least a good fallback?
  device_type = format_dev(('%s_%s' % (
    grp[0].getValue(), grp[0].getFootprint())).rstrip('_'))
  # Telesis format allows for specifying value and tolerance, which is helpful
  # when looking at designs. The exact field name used to store the value
  # (resistance, capacitance) depends on the library implementation.
  # TODO: this list probably needs to be customizable, or perhaps include a more
  #       exhaustive list of reasonable options more options (val, res, cap, L,
  #       etc; whatever it seems people are doing).
  value = get_group_field(nl, grp, ('Spice_Model', 'VALUE'))
  tol = get_group_field(nl, grp, ('TOLERANCE', 'TOL'))
  # Instantiate the list of all the parts with these same specs.
  f.write(format_list('!%s!%s!%s;' % (device_type, value, tol),
                      (c.getRef() for c in grp)))
  # Write out the corresponding device file
  with open(os.path.join(devdir, '%s.txt' % device_type), 'w') as d:
    # We need to pick a reasonable footprint as the default Allegro footprint.
    # By default we'll use the contents of the Footprint field, with the leading
    # library name stripped out. This is unlikely to be defined in
    # Allegro-centric symbol libraries, though, in which case we use the
    # contents of the footprint filters list as described above.
    # If nothing is defined, give up and just throw in the device_type string,
    # which is unlikely to match anything unless you have a very strange
    # footprint library.
    # Use the instance's footprint in case it overrides the library's
    footprints = libpart.element.getChild('footprints')
    default_footprint = (footprints.getChildren('fp')[0].get('fp')
                         if footprints else device_type)
    # Remove the library name from the footprint, if present
    footprint = (grp[0].getFootprint() or default_footprint).rpartition(':')[2]
    # Write out the chosen default footprint. Additional footprints are written
    # to the ALT_SYMBOLS property.
    d.write("PACKAGE '%s'\n" % format_dev(footprint))
    # Valid classes are IC, IO, and DISCRETE. This mainly seems to enable
    # filtering in Quickplace, and BGA Text Out (requires IO) when using APD.
    # It also seems to affect default pin-swap options when they're not
    # specified (we fully-specify it so this shouldn't matter).
    # TODO: heuristically specify IO or DISCRETE, if it doesn't have unexpected
    #       consequences. IO could be selected when PINSWAP covers all pins.
    #       DISCRETE could be selected for two-terminal parts.
    d.write('CLASS IC\n')
    # Write out library part info
    pins = libpart.element.getChild('pins').getChildren('pin')
    d.write('PINCOUNT %u\n' % len(pins))
    # Collect functions, if specified
    for func in find_group_functions(grp):
      # Split out each group of pins
      group_sets = get_group_field(nl, grp, 'func_' + func, sanitize=False).split(';')
      # Set aside swap indices, if provided (first group after an empty one)
      swap_indices = set()
      swap_indices_text = ''
      if '' in group_sets:
        end_of_group_list = group_sets.index('')
        swap_indices_text = group_sets[end_of_group_list+1]
        # Drop any groups that are following this; they're invalid unless in the
        # future we use this to specify additional features.
        # TODO: Maybe output a warning if we're dropping additional fields, in
        #       case the definition accidentally has too many semicolons?
        del group_sets[end_of_group_list:]
      # Collect groups (a list of lists of pins)
      groups = []
      for group_res in group_sets:
        group_pins = []
        groups.append(group_pins)
        # Each group is made up of comma-separated regexes
        for group_re in group_res.split(','):
          if not group_re:
            continue
          regex_matches = set()
          regex = re.compile(group_re, re.IGNORECASE)
          # KiCad takes pin names that are ~ and writes them out to the netlist
          # as empty, so handle that case.
          include_empty = bool(regex.match('~'))
          # Check all the pins for matches; iterate in reverse so we can remove
          # matches from the list.
          for i in range(len(pins)-1, -1, -1):
            pinname = pins[i].get('pin', 'name')
            if regex.match(pinname) or include_empty and not pinname:
              regex_matches.add(pins[i])
              del pins[i]
          # Matches within a regex are sorted, but order between multiple
          # regexes are maintained.
          group_pins.extend(sorted(regex_matches, key=pin_sort_key))
        # Check that the pin count is the same
        if len(group_pins) != len(groups[0]):
          # Function is invalid; output a warning and drop the function.
          print(f'group length mismatch in function {func}')
          print(f'pattern {group_res} does not expand to the same number of pins')
          # Add pins back to the default list so at least netlist is complete.
          # This may affect subsequent function definitions if regexes
          # overlap...but that's explicitly disallowed so it's fine.
          for group in groups:
            pins.extend(group)
          groups = []
          break
      # Skip empty/broken groups
      if not groups or not len(groups[0]):
        # FIXME: spit out a warning?
        continue
      # Process swap indices range expansion
      if swap_indices_text == '*':
        swap_indices.update(range(len(groups[0])))
      elif swap_indices_text:
        for r in swap_indices_text.split(','):
          r = r.split('-')*2
          # Convert to 0-index
          swap_indices.update(range(
            min(int(r[0])-1, len(groups[0])),
            min(int(r[1]), len(groups[0]))))
      # Write out the collected function data
      d.write(format_function(func, groups, swap_indices))
    # Any pins left over belong to the main group.
    if pins:
      d.write(format_function('main', [pins]))
    # Write out properties; there are only a few that are supported.
    if value:
      d.write('PACKAGEPROP VALUE %s\n' % value)
    if tol:
      d.write('PACKAGEPROP TOL %s\n' % tol)
    # Only write out ALT_SYMBOLS if the footprint wasn't overridden.
    # This is to avoid mixups and stale footprints if e.g., the designer
    # overrides an 0402 part with an 0603, or overrides a generic part with a
    # special footprint for some purpose.
    if footprints and footprint in (libpart.getFootprint(), default_footprint):
      # Strip any library names out of the footprint filters.
      # TODO: implement glob support by searching PSMPATH?
      #       this would require parsing the Allegro environment files (tcl
      #       scripts) and may not be realistic to do. Alternatively, could
      #       require the designer to redundantly specify the psm directory list
      #       somewhere, ideally in the library.
      d.write("PACKAGEPROP ALT_SYMBOLS '(%s)'\n" % ','.join(
        format_dev(fp.get('fp').rpartition(':')[2])
        for fp in footprints.getChildren('fp')))
    # Include any remaining Allegro-recognizable properties
    # HEIGHT will set the default box height in the 3D view, if the footprint
    # doesn't have a PACKAGE_HEIGHT_MAX property on a PLACE_BOUND_* shape
    # TODO: either customize the field mapping to PART_NUMBER and HEIGHT, or
    #       include a more exhaustive list of reasonable options
    # TODO: it would be nice if PART_NUMBER could be prepended with the
    #       manufacturer, if specified
    for prop in (('PART_NUMBER', 'mpn', 'mfr_pn'), ('HEIGHT',)):
      data = get_group_field(nl, grp, prop)
      if data:
        d.write("PACKAGEPROP %s %s\n" % (prop[0], data))
    # Done with device file
    d.write('END\n')

# Write out nets
f.write('$NETS\n')
for net in nl.nets:
  netname = format_net(net.get('net', 'name'))
  # Each net has a list of refdes.pinnum
  f.write(format_list('%s ; ' % netname, (
      '%s.%s' % (n.get('node', 'ref'), n.get('node', 'pin'))
      for n in net.getChildren('node'))))

# Write out package properties. NOTE: Allegro doesn't recognize much...
f.write('$PACKAGES\n$A_PROPERTIES\n')
rooms = {}
for comp in nl.components:
  # Exclude parts whose definitions were previously excluded
  if not comp.getLibPart().element.getChild('pins'):
    continue
  # Use the sheet path as ROOM, if not otherwise specified.
  # This is the only way to enable placing by page, since the Telesis format
  # doesn't enable specifying page numbers in addition to ROOM definitions.
  room = format_text(comp.getField('ROOM')
                     or comp.element.get('sheetpath', 'names'))
  if room:
    rooms.setdefault(room, []).append(comp.getRef())
for room, refs in sorted(rooms.items(), key=lambda s: s[0].strip("'")):
  f.write(format_list('ROOM %s ; ' % room, refs))

# Done with the netlist
f.close()
