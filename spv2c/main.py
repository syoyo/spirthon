import os
import sys
sys.path.append("..")

import json

import array
import spirv
import struct

def asFloat(v):
    if type(v) == type(list()):
        if len(v) > 1: # float64
            x0 = hex(v[0])
            x1 = hex(v[1])
            if x0[-1] == 'L':
                x0 = x0[:-1] # strip last 'L'
            if x1[-1] == 'L':
                x1 = x1[:-1] # strip last 'L'

            return struct.unpack('d', struct.pack('II', int(x0, 16), int(x1, 16)))[0]

        else: # float32
            x = hex(v[0])
            if x[-1] == 'L':
                x = x[:-1] # strip last 'L'

            return struct.unpack('f', struct.pack('I', int(x, 16)))[0]
    else:
        x = hex(v)
        if x[-1] == 'L':
            x = x[:-1] # strip last 'L'

        return struct.unpack('f', struct.pack('I', int(x, 16)))[0]

def printVector(vv):
    s = []
    for v in vv:
        s.append(str(v))

    return ",".join(s)

class Spv2C:
    def __init__(self, instructions, info, glsl450lib):
        self.instructions = instructions
        self.info = info
        self.typeTable = {} 
        self.constTable = {}
        self.varTable = {}
        self.nameTable = {}
        self.decorateTable = {}
        self.tmpCount = 0
        self.glsl450lib = glsl450lib

    def genTemp(self):
        s = "tmp%08d" % self.tmpCount
        self.tmpCount = self.tmpCount + 1
        return s
        
    def EmitFunction(self, insn):
        s = ""
        s += "{0} {1}() {".format(insn.name, insn.name)
        s += "}"
        return s

    #def WrapBuiltIn

    def getSrc(self, result_id):
        if self.constTable.has_key(result_id):
            return self.constTable[result_id]
        if self.varTable.has_key(result_id):
            return self.varTable[result_id]
        if self.nameTable.has_key(result_id):
            return self.nameTable[result_id]

        print(result_id)
        raise

    def getVarOrGen(self, result_id):
        if self.varTable.has_key(result_id):
            var = self.varTable[result_id]
        else:
            self.varTable[result_id] = self.genTemp()
            var = self.varTable[result_id]

        return var

    def Emit(self):
        s = ""
        for insn in self.instructions:
            print(insn)
            if insn.name == 'OpName':
                self.nameTable[insn.args[0].result_id] = insn.args[1]
            if insn.name == 'OpDecorate':
                self.decorateTable[insn.args[0].result_id] = insn.args[1]
            elif insn.name == 'OpFunction':
                s += "void %s() { // OpFunction(%d)\n" % (self.nameTable[insn.result_id], insn.result_id)
            elif insn.name == 'OpFunctionEnd':
                s += "} // OpFunctionEnd(%d)\n" % (insn.result_id)
            elif insn.name == 'OpLabel':
                s += "  label_%d:\n" % (insn.result_id)
            elif insn.name == 'OpReturn':
                s += "  return; // OpReturn(%d)\n" % (insn.result_id)
            elif insn.name == 'OpBranch':
                s += "  goto label_%d; // OpBranch(%d)\n" % (insn.args[0].result_id, insn.result_id)
            elif insn.name == 'OpStore':
                dst = self.getSrc(insn.args[0].result_id)
                src = self.getSrc(insn.args[1].result_id)
                s += "  %s = make_vec4(%s); // OpStore(%d)\n" % (dst, printVector(src), insn.result_id)
            elif insn.name == 'OpVariable':
                var = self.getSrc(insn.result_id)
                self.varTable[insn.result_id] = var
            elif insn.name == 'OpTypeSampler':
                self.typeTable[insn.result_id] = insn
            elif insn.name == 'OpTypeVoid':
                self.typeTable[insn.result_id] = insn
            elif insn.name == 'OpTypePointer':
                self.typeTable[insn.result_id] = insn
            elif insn.name == 'OpTypeFunction':
                self.typeTable[insn.result_id] = insn
            elif insn.name == 'OpTypeFloat':
                self.typeTable[insn.result_id] = insn
            elif insn.name == 'OpTypeInt':
                self.typeTable[insn.result_id] = insn
            elif insn.name == 'OpTypeVector':
                print(insn.args[0].result_id)
                baseTy = self.typeTable[insn.args[0].result_id]
                n = insn.args[1]
                self.typeTable[insn.result_id] = (baseTy, n)
            elif insn.name == 'OpConstant':
                self.constTable[insn.result_id] = insn.args[0] 
                print("DBG: add {0} to [{1}]".format(insn.args[0], insn.result_id))
                # assume float
                print(asFloat(insn.args[0]))
            elif insn.name == 'OpCompositeConstruct':
                s += "TODO: " + insn.name
                s += "\n"
            elif insn.name == 'OpConstantComposite':
                n = len(insn.args[0])
                cc = []
                for arg in insn.args[0]:
                    # Assume arg = instanceof(Id)
                    c = self.constTable[arg.result_id][0]
                    cc.append(asFloat(c))
                ty = self.typeTable[insn.type_id]
                print("type", ty)
                self.constTable[insn.result_id] = cc
                print("DBG: add {0} to [{1}]".format(cc, insn.result_id))
            elif insn.name == 'OpLoad':
                print("ret: ", insn.result_id)
                dst = self.getVarOrGen(insn.result_id)
                src = self.getSrc(insn.args[0].result_id)
                ss = "  %s = %s; // OpLoad(%d)\n" % (dst, src, insn.result_id)
                print(ss)
                s += ss
                # todo
                pass
            elif insn.name == 'OpVectorShuffle':
                s += "TODO: " + insn.name
                s += "\n"
            elif insn.name == 'OpBitcast':
                dst = self.getVarOrGen(insn.result_id)
                s += "TODO: " + insn.name
                s += "\n"
            elif insn.name == 'OpISub':
                dst = self.getVarOrGen(insn.result_id)
                s += "TODO: " + insn.name
                s += "\n"
            elif insn.name == 'OpConvertSToF':
                dst = self.getVarOrGen(insn.result_id)
                s += "TODO: " + insn.name
                s += "\n"
            elif insn.name == 'OpFSub':
                dst = self.getVarOrGen(insn.result_id)
                s += "TODO: " + insn.name
                s += "\n"
            elif insn.name == 'OpFMul':
                dst = self.getVarOrGen(insn.result_id)
                s += "TODO: " + insn.name
                s += "\n"
            elif insn.name == 'OpFDiv':
                dst = self.getVarOrGen(insn.result_id)
                s += "TODO: " + insn.name
                s += "\n"
            elif insn.name == 'OpFConvert':
                dst = self.getVarOrGen(insn.result_id)
                s += "TODO: " + insn.name
                s += "\n"
            elif insn.name == 'OpExtInst':
                dst = self.getVarOrGen(insn.result_id)
                s += "TODO: " + str(insn.args)
                s += "\n"
            elif insn.name == 'OpImagePointer':
                dst = self.getVarOrGen(insn.result_id)
                s += "TODO: " + insn.name
                s += "\n"
            elif insn.name == 'OpSource':
                # todo
                pass
            elif insn.name == 'OpExtInstImport':
                # todo
                pass
            elif insn.name == 'OpMemoryModel':
                # todo
                pass
            elif insn.name == 'OpEntryPoint':
                # todo
                pass
            elif insn.name == 'OpName':
                # todo
                pass
            else:
                raise "Unsupported op"

        return s

def main():
    print("SPIR to C translator")

    if len(sys.argv) < 2:
        print("Need input.spv")
        os.exit(-1)

    instructions, info = spirv.decode_spirv(array.array('I', open(sys.argv[1], "rb").read()))
    print("info", info)

    # Get GLSL450 lib code
    libs = json.loads(open("../glsl450lib.json").read())

    glsl450lib = {}
    for name in libs['GLSL450']:
        n = libs['GLSL450'][name]
        glsl450lib[n] = name

    s = Spv2C(instructions, info, glsl450lib)
    code = s.Emit()
    print(code)

main()
