import ast, re, sys, os, json
from collections import defaultdict

glsllib_src = open(os.path.join(sys.argv[1], 'SPIRV', 'GLSL450Lib.h')).read()


constants = {}
masks = {}
for name, body in re.findall(r"enum\W(\w+)\W\{(.*?)\}", glsllib_src, re.DOTALL):
    to = constants
    table = {}
    index = 0
    for key, value in re.findall(r"^\s*(\w+)\s*(?:=\s*([0-9xA-Fa-f]+))?\s*\,?\s*(?://.*)?$", body, re.MULTILINE):
        if value != '':                     # Python and C literal syntax
            index = ast.literal_eval(value) # are similar enough.
        if name != 'Op': # The Op -prefix remains in the specification.
            key = re.sub("^"+name, "", key) # But other prefixes do not.
        if to == masks: # Also Masks do not have Mask -postfix.
            key = re.sub("Mask$", "", key)
            if key == 'MaskNone': # Isn't significant, and could be harmful to reader, so we can skip it.
                assert index == 0, index # Assuming it's zero.
                continue           
        assert key != '' # Substitutions might eliminate keys
        assert key not in table # If it appears again, something went wrong.
        table[key] = index # Allows ints to be ints in the json.
        index += 1 # enum increments if no constant is specified

        to[name] = table

libs = to['Entrypoints']

d = {}
d['GLSL450'] = libs

## Finally lets put everything together for easy consumption and pretty-print it out.
#instructions = []
#for name in sorted(opcodes, key=lambda x: opcodes[x]):
#    record = dict(
#        opcode = opcodes[name],
#        name = name,
#        result = has_result.get(name, True), # Apparently, if the result was not assumed in the
#        type = has_type.get(name, True),     # C++ source code, it was assumed to be 'true'
#        operands = operands.get(name, []),
#    )
#    instructions.append(record)
#specification = dict(instructions=instructions, constants=constants, masks=masks)
print json.dumps(d, indent=4)
