import sys,re
addr = 0
lnum = 0
memTable = {}
memText = {}

opcodeMap = {
    'ADD'   :  {'FMT' : "RD,RS1,RS2",  'IWORD' : "RD RS1 RS2 000000000000 0000 0000"},
    'SUB'   :  {'FMT' : "RD,RS1,RS2",  'IWORD' : "RD RS1 RS2 000000000000 0001 0000"},
    'AND'   :  {'FMT' : "RD,RS1,RS2",  'IWORD' : "RD RS1 RS2 000000000000 0100 0000"},
    'OR'    :  {'FMT' : "RD,RS1,RS2",  'IWORD' : "RD RS1 RS2 000000000000 0101 0000"},
    'XOR'   :  {'FMT' : "RD,RS1,RS2",  'IWORD' : "RD RS1 RS2 000000000000 0110 0000"},
    'NAND'  :  {'FMT' : "RD,RS1,RS2",  'IWORD' : "RD RS1 RS2 000000000000 1100 0000"},
    'NOR'   :  {'FMT' : "RD,RS1,RS2",  'IWORD' : "RD RS1 RS2 000000000000 1101 0000"},
    'XNOR'  :  {'FMT' : "RD,RS1,RS2",  'IWORD' : "RD RS1 RS2 000000000000 1110 0000"},
    
    'ADDI'  : {'FMT': "RD,RS1,Imm",    'IWORD' : "RD RS1 Imm              0000 1000"},
    'SUBI'  : {'FMT': "RD,RS1,Imm",    'IWORD' : "RD RS1 Imm              0001 1000"},
    'ANDI'  : {'FMT': "RD,RS1,Imm",    'IWORD' : "RD RS1 Imm              0100 1000"},
    'ORI'   : {'FMT': "RD,RS1,Imm",    'IWORD' : "RD RS1 Imm              0101 1000"},
    'XORI'  : {'FMT': "RD,RS1,Imm",    'IWORD' : "RD RS1 Imm              0110 1000"},
    'NANDI' : {'FMT': "RD,RS1,Imm",    'IWORD' : "RD RS1 Imm              1100 1000"},
    'NORI'  : {'FMT': "RD,RS1,Imm",    'IWORD' : "RD RS1 Imm              1101 1000"},
    'XNORI' : {'FMT': "RD,RS1,Imm",    'IWORD' : "RD RS1 Imm              1110 1000"},

    'MVHI'  : {'FMT': "RD,Imm",        'IWORD' : "RD 0000 Imm             1011 1000"},
    
    'LW'    : {'FMT': "RD,Imm(RS1)",   'IWORD' : "RD RS1 Imm              0000 1001"},
    'SW'    : {'FMT': "RS2,Imm(RS1)",  'IWORD' : "RS1 RS2 Imm             0000 0101"},
    #CMP-R
    'F'     : {'FMT': "RD,RS1,RS2",    'IWORD' : "RD RS1 RS2 000000000000 0000 0010"},
    'EQ'    : {'FMT': "RD,RS1,RS2",    'IWORD' : "RD RS1 RS2 000000000000 0001 0010"},
    'LT'    : {'FMT': "RD,RS1,RS2",    'IWORD' : "RD RS1 RS2 000000000000 0010 0010"},
    'LTE'   : {'FMT': "RD,RS1,RS2",    'IWORD' : "RD RS1 RS2 000000000000 0011 0010"},
    'T'     : {'FMT': "RD,RS1,RS2",    'IWORD' : "RD RS1 RS2 000000000000 1000 0010"},
    'NE'    : {'FMT': "RD,RS1,RS2",    'IWORD' : "RD RS1 RS2 000000000000 1001 0010"},
    'GTE'   : {'FMT': "RD,RS1,RS2",    'IWORD' : "RD RS1 RS2 000000000000 1010 0010"},
    'GT'    : {'FMT': "RD,RS1,RS2",    'IWORD' : "RD RS1 RS2 000000000000 1011 0010"},
    
    'FI'    : {'FMT': "RD,RS1,Imm",    'IWORD' : "RD RS1 Imm              0000 1010"},
    'EQI'   : {'FMT': "RD,RS1,Imm",    'IWORD' : "RD RS1 Imm              0001 1010"},
    'LTI'   : {'FMT': "RD,RS1,Imm",    'IWORD' : "RD RS1 Imm              0010 1010"},
    'LTEI'  : {'FMT': "RD,RS1,Imm",    'IWORD' : "RD RS1 Imm              0011 1010"},
    'TI'    : {'FMT': "RD,RS1,Imm",    'IWORD' : "RD RS1 Imm              1000 1010"},
    'NEI'   : {'FMT': "RD,RS1,Imm",    'IWORD' : "RD RS1 Imm              1001 1010"},
    'GTEI'  : {'FMT': "RD,RS1,Imm",    'IWORD' : "RD RS1 Imm              1010 1010"},
    'GTI'   : {'FMT': "RD,RS1,Imm",    'IWORD' : "RD RS1 Imm              1011 1010"},

    'BF'    : {'FMT': "RS1,RS2,Imm",   'IWORD' : "RS1 RS2  Imm            0000 0110"},
    'BEQ'   : {'FMT': "RS1,RS2,Imm",   'IWORD' : "RS1 RS2  Imm            0001 0110"},
    'BLT'   : {'FMT': "RS1,RS2,Imm",   'IWORD' : "RS1 RS2  Imm            0010 0110"},
    'BLTE'  : {'FMT': "RS1,RS2,Imm",   'IWORD' : "RS1 RS2  Imm            0011 0110"},
    'BEQZ'  : {'FMT': "RS1,Imm",       'IWORD' : "RS1 0000 Imm            0101 0110"},
    'BLTZ'  : {'FMT': "RS1,Imm",       'IWORD' : "RS1 0000 Imm            0110 0110"},
    'BLTEZ' : {'FMT': "RS1,Imm",       'IWORD' : "RS1 0000 Imm            0111 0110"},
    
    'BT'    : {'FMT': "RS1,RS2,Imm",   'IWORD' : "RS1 RS2  Imm            1000 0110"},
    'BNE'   : {'FMT': "RS1,RS2,Imm",   'IWORD' : "RS1 RS2  Imm            1001 0110"},
    'BGTE'  : {'FMT': "RS1,RS2,Imm",   'IWORD' : "RS1 RS2  Imm            1010 0110"},
    'BGT'   : {'FMT': "RS1,RS2,Imm",   'IWORD' : "RS1 RS2  Imm            1011 0110"},
    'BNEZ'  : {'FMT': "RS1,Imm",       'IWORD' : "RS1 0000 Imm            1101 0110"},
    'BGTEZ' : {'FMT': "RS1,Imm",       'IWORD' : "RS1 0000 Imm            1110 0110"},
    'BGTZ'  : {'FMT': "RS1,Imm",       'IWORD' : "RS1 0000 Imm            1111 0110"},
    
    'JAL'   : {'FMT': "RD,Imm(RS1)",   'IWORD' : "RD RS1  Imm             0000 1011"},

    #BR is implemented using BEQ
    'BR'    : {'FMT': "Imm",           'ITEXT' : ("BEQ R6,R6,Imm",)},
    #NOT is implemeted using NAND
    'NOT'   : {'FMT': "RD, RS",       'ITEXT' : ("NAND RD,RS,RS",)},
    #BLE, BEG are implemented using LTE/GTE and BNEZ
    'BLE'   : {'FMT':"RS1,RS2,Imm",    'ITEXT' :("LE  R6,RS1,RS2","BNE R6,Zero,Imm",)},
    'BGT'   : {'FMT':"RS1,RS2,Imm",    'ITEXT' :("GT R6,RS1,RS2","BNE R6,Zero,Imm",)},
    'CALL'  : {'FMT':"Imm(RS1)",       'ITEXT' :("JAL RA,Imm(RS1)",)},
    'RET'   : {'FMT':"",               'ITEXT' :("JAL R9,0(RA)",)},
    'JMP'   : {'FMT':"Imm(RS1)",       'ITEXT' :("JAL R9,Imm(RS1)",)}, 
    }

#psecode
isa_ITEXT = set(['BR','NOT','BLE','BGT','CALL','RET','JMP'])

WordSize = 32
InstSize = WordSize
ImmSize = 15
regNumSize = 4
lbs = {}
pcMemTable = {}
memPcTable = {}
regNames = {
    0 : ['R0','A0'],
    1 : ['R1','A1'],
    2 : ['R2','A2'],
    3 : ['R3','A3','RV'],
    4 : ['R4','T0'],
    5 : ["R5", "T1"],
    6 : ["R6", "S0"],
    7 : ["R7", "S1"],
    8 : ["R8", "S2"],
    9 : ["R9"],
   10 : ["R10"],
   11 : ["R11"],
   12 : ["R12","GP"],
   13 : ["R13","FP"],
   14 : ["R14","SP"],
   15 : ["R15","RA"],
}

isa_type_12_zero = set([
                'ADD', 'SUB', 'AND', 'OR', 'XOR', 'NAND', 'NOR', 'XNOR',
                'F', 'EQ', 'LT', 'LTE', 'T', 'NE', 'GTE', 'GT'])

isa_type_imm16 = set([
    'ADDI', 'SUBI', 'ANDI', 'ORI', 'XORI', 'NANDI', 'NORI', 'XNORI',
    'FI', 'EQI', 'LTI', 'LTEI', 'TI', 'NEI', 'GTEI', 'GTI'])

isa_type_lw_sw = set(['LW', 'SW'])

isa_type_mvhi = set(['MVHI'])
isa_type_jal = set(['JAL'])
isa_type_pcrel = set([
    'BF', 'BEQ', 'BLT', 'BLTE', 'BEQZ', 'BLTZ', 'BLTEZ',
    'BT', 'BNE', 'BGTE', 'BGT', 'BNEZ', 'BGTEZ', 'BGTZ'
    ])
isa_branch_2op = set(['BEQZ','BLTZ','BLTEZ','BNEZ','BGTEZ','BGTZ'])
regNums = {}


def regNumMap():
    for rnum in regNames.keys():
        for rnam in regNames[rnum] :
            regNums[rnam] = IntToBinary(rnum, regNumSize)
            
            
def IntToBinary(num,size):
    print bin(num)[2:]
    if (num < 0):
        binstr = bin(num % ( 1<<size))[2:]
    else:
        binstr = bin(num)[2:].zfill(size)
    return binstr

def get_imm16(target, hi=False):
    print "pass to getimm16"
    print target
    ''' get the imm from target, regardless its a immdiate value or a variable'''
    imm16 = None
    if target in names.keys():
        print "get names"
        print names[target]
        
        if hi:
            print "mvhi"
            imm16 = IntToBinary(names[target],32)[:16]
        else:
            print "normal"
            imm16 = IntToBinary(names[target],32)[16:]
        print imm16
    elif target in lbs.keys():
        print "lbs address : " + hex(lbs[target]/4)
        if hi:
            print "mvhi"
            imm16 = IntToBinary(lbs[target]/4,32)[:16]
        else:
            print "normal"
            imm16 = IntToBinary(lbs[target]/4,32)[16:]
        print imm16
    elif target.find('0X') != -1:
        target = target[2:]
        if re.match(numfmt,target):
            target = int(target, 16)
            if hi:
                imm16 = IntToBinary(target,32)[:16]
            else:
                imm16 = IntToBinary(target,32)[16:] 
    elif re.match(numfmt,target):
        print "match number"
        target = int(target)
        print target
        if hi:
            imm16 = IntToBinary(target,32)[:16]
        else:
            imm16 = IntToBinary(target,32)[16:] 
            print imm16
    else:
        print "invalid imm"
        print target
        sys.exit()
    print hex(int(imm16,2))
    return imm16
def find_pcrel(imm,pc):

    nextPc = pc + 1
    print imm
    immaddress = lbs[imm]
    print immaddress
    immC = memPcTable[immaddress]
    offset = immC - nextPc
    offset = IntToBinary(offset,16)
    return offset
   
#deal with normal opcode   
def asmInstr(opcode, args,addr,line,lnum,pc):  
    print "opcode = {} \nargs = {}\naddrvalue = {} \nline = {}\nline Number = {}\npcvalue = {}\n".format(opcode,args,addr,line,lnum,pc)
    #print "start format : " + sformat + "\n"
    opcode = opcode.strip()
    mformat = opcodeMap[opcode]['IWORD']
    #print "m format : " + mformat + "\n"
    
    args = args.replace(" ","")
    args = args.split(",")
    if opcode in isa_type_12_zero:
        print args
        if args[0] in regNums.keys() and args[1] in regNums.keys() and args[2] in regNums.keys():
            rd = regNums[args[0]]
            rs1 = regNums[args[1]]
            rs2 = regNums[args[2]]
        else:
            print "invalid reg number"
            sys.exit()
        mformat = mformat.replace("RD",rd)
        mformat = mformat.replace("RS1",rs1)
        mformat = mformat.replace("RS2",rs2)
        mformat = mformat.replace(" ","")
        print mformat
    elif opcode in isa_type_imm16:
        if args[0] in regNums.keys() and args[1] in regNums.keys():
            rd = regNums[args[0]]
            rs1 = regNums[args[1]]
        else:
            
            print "invalid reg number"
            sys.exit()
        mformat = mformat.replace("RD",rd)
        mformat = mformat.replace("RS1",rs1)
        imm = args[2]
        imm16 = get_imm16(args[2])
        mformat = mformat.replace("Imm",imm16)
        mformat = mformat.replace(" ","")
        print mformat
    elif opcode in isa_type_lw_sw:
        
        #print "argimm : " + argimm
        #print "argBase : "+ argBase
        print "get lwsw"
        if opcode == "LW":
            rd = args[0]
            immBase = args[1]
            commaIndex = immBase.find('(')
            imm = immBase[:commaIndex].strip()
            rs1 = immBase[commaIndex + 1: -1].strip()
            if rd in regNums.keys() and rs1 in regNums.keys():
                rd = regNums[rd]
                rs1 = regNums[rs1]
            else:
                print "invalid reg number"
                sys.exit()
            imm16 = get_imm16(imm)
            mformat = mformat.replace("RD",rd)
            mformat = mformat.replace("RS1",rs1)
            mformat = mformat.replace("Imm",imm16)
            mformat = mformat.replace(" ","")
            print mformat
        if opcode == "SW":
            rs2 = args[0]
            immBase = args[1]
            commaIndex = immBase.find('(')
            imm = immBase[:commaIndex].strip()
            rs1 = immBase[commaIndex + 1: -1].strip()
            if rs2 in regNums.keys() and rs1 in regNums.keys():
                rs2 = regNums[rs2]
                rs1 = regNums[rs1]
            else:
                print "invalid reg number"
                sys.exit()
            imm16 = get_imm16(imm)
            mformat = mformat.replace("RS2",rs2)
            mformat = mformat.replace("RS1",rs1)
            mformat = mformat.replace("Imm",imm16)
            mformat = mformat.replace(" ","")
            print mformat
    elif opcode in isa_type_pcrel:
        if opcode in isa_branch_2op:
            rs1 = args[0]
            if rs1 in regNums.keys():
                rs1 = regNums[rs1]
            else:
                print "invalid reg number"
                sys.exit()
            mformat = mformat.replace("RS1",rs1)
            imm = args[1]
        else:
            rs1 = args[0]
            rs2 = args[1]
            if rs1 in regNums.keys() and rs2 in regNums.keys():
                rs1 = regNums[rs1]
                rs2 = regNums[rs2]
            else:
                print "invalid reg number"
                sys.exit()
            mformat = mformat.replace("RS1",rs1)
            mformat = mformat.replace("RS2",rs2)
            imm = args[2] 
        if imm in lbs.keys():
            offset = find_pcrel(imm,pc)
        else:
            print "invalid offset"
            sys.exit()
        
        mformat = mformat.replace("Imm",offset)
        
    elif opcode in isa_type_jal:
        print args
        rd = args[0]
        immBase = args[1]
        commaIndex = immBase.find('(')
        imm = immBase[:commaIndex].strip()
        rs1 = immBase[commaIndex + 1: -1].strip()
        if rd in regNums.keys() and rs1 in regNums.keys():
            rd = regNums[rd]
            rs1 = regNums[rs1]
        else:
            print "invalid reg number"
            sys.exit()
        imm16 = get_imm16(imm)
        print "Jal imm " + imm16
        mformat = mformat.replace("RD",rd)
        mformat = mformat.replace("RS1",rs1)
        mformat = mformat.replace("Imm",imm16)
        mformat = mformat.replace(" ","")
        print mformat
    elif opcode in isa_type_mvhi:
        if args[0] in regNums.keys():
            rd = regNums[args[0]]
        else:
            print "invalid reg number"
        mformat = mformat.replace("RD",rd)
        imm = args[1]
        imm16 = get_imm16(imm, hi=True)
        mformat = mformat.replace("Imm",imm16)
        mformat = mformat.replace(" ","")
        print mformat
    mformat = mformat.replace(" ","")
    #iword = int(mformat,2)
    setMem(addr, mformat, line, lnum)
    
    print "pc" + str(pc)
    print "addr" + str(addr)
    


#deal with implemented opcode
def ImpInst(opcode,args,substfmt,addr,line,lnum,pc):
    print "pass to imiinst"
    argsfmt = opcodeMap[opcode]['FMT']
    fmtlist = argsfmt.replace(" ","").split(',')
    print opcode
    if (opcode == 'RET'):
        opcodei = 'JAL    '
        argsi = 'R9,0(RA)'
        asmInstr(opcodei, argsi, addr, substfmt, lnum,pc)
    elif opcode == 'CALL' or opcode == " JMP":
        print "find call or JMP"
        opcodei = "JAL"
        print args
        
        immBase = args.strip()
        commaIndex = immBase.find('(')
        imm = immBase[:commaIndex].strip()
        rs1 = immBase[commaIndex + 1: -1].strip()
        substfmt = substfmt.replace("RS1",rs1)
        substfmt = substfmt.replace("Imm",imm)
        sublist= substfmt.strip().split()
        
        print "substfmt " + str(substfmt)
        print 'sublist' + str(sublist)
        argi = sublist[1].strip()
        print "argi " + argi
        asmInstr(opcodei, argi,addr,substfmt,lnum,pc)
    else:   
        arglist = args.split(',')
    
    
        print "substfmt :" + str(substfmt)
        print "argsfmt : " + str(argsfmt)
        print "arglist : " + str(arglist)
        print "fmtlist : " + str(fmtlist)
        for i in range(0,len(fmtlist)):
            substfmt = substfmt.replace(fmtlist[i], arglist[i])
            print "substfmt " + str(i) +" " + str(substfmt) 

        print "substfmt"
        sublist = substfmt.split(" ")
        opi = sublist[0].strip()    
        argi = sublist[1].strip()
        asmInstr(opi, argi, addr, substfmt, lnum,pc)
#memmap

def setMem(addr, val, line, lnum):
    line = line.strip()
    if addr in memTable.keys():
        print "Memory address already filled: " + str(addr)
        sys.exit(1)
    memTable[addr] = val
    print hex(int(memTable[addr],2))[2:].zfill(8)

    

numfmt = r'[0-9A-F]+|-?[0-9]+'

def NumGet(numstr):
    if numstr[0:2] == "0X":
        numstr = numstr[2:]
        if re.match(numfmt,numstr):
            retVal = int(numstr,16)
       
    elif re.match(numfmt,numstr):
        retVal = int(numstr)
    else:
        retVal = ""
    #if (retVal and (1 << WordSize - 1)):
    #    retVal = retVal or ((-1)^((1<<(WordSize - 1))-1))
    return retVal

names = {}

    

def LblGet(straddr):
    lableName = straddr.strip()
    if (lableName not in lbs.keys()):
        print "invalid label"
        return ""
    print "label name = " + str(lableName)
    print lbs[straddr]
    return lbs[straddr]


#start

regNumMap()
fileName = raw_input("Enter the file name")
file_suffix = '.mif'
outputfileName = ''.join([fileName[:-4],file_suffix])

for passNum in [1,2]:
    pc = 10
    lnum = 1
    print "pass:" + str(passNum)
    with open(fileName,'r') as f:
        
        file_line_number = 1
        file_mem_number = 1
        total_instruction = 0
        for line in f.xreadlines():
            line= line.upper()
            print "\n###########\n new line" + str(lnum) + "   " + line
            print "\n" + str(addr) 
        #remove comment from the end of the line
            #if re.match(r'^s\s*;'):
            if line.find(';') != -1:
                index = line.find(";")
                line = (line[:index] + '\n').strip()
                print "\nafter clean comment: " + line
            #empty line
            if(len(line.strip()) == 0):
                print "empty line\n"
                pass
            elif re.match(r'\s*.ORIG',line):
                print "deal with orig\n"
                curr =line.split()
                addr = NumGet(curr[1])
                print "addr {}, curr = {}\n".format(hex(addr),curr[1])
            #Deal with .NAME
            elif re.match(r'\s*.NAME',line):
                print "deal with name\n"
                curr = ''.join([e for i, e in enumerate(line.split()) if i > 0])
                curr = curr.split('=')
                name = curr[0]
                addre = curr[1]
                if passNum == 1:
                    print "name in pass 1"
                    if name in names.keys():
                        print "label redefined"
                        sys.exit(1)
                else:
                    print "name in pass 2"
                    if (names[name] != (NumGet(addre))):
                        print addre
                        print NumGet(addre)
                        print "labelGet =" + str(names[name])
                        print "address =" + hex(NumGet(addre))
                        print "different address in two passes"
                        sys.exit(1)
                if curr[1].find('0X') != -1:
                    names[curr[0]] = int(curr[1],16)
                else:
                    names[curr[0]] = int(curr[1],10)
                print "put value to names"
                print type(int(curr[1],16))
                print str([curr[0]]) + "  " + str(names[curr[0]])
            #Deal with .WORD
            elif re.match(r'\s*.WORD',line):
                curr = ''.join([e for i, e in enumerate(line.split()) if i > 0])
                if passNum == 2:
                    addrStr = curr[0]
                    if (re.match(numfmt,addrStr)) :
                        num = NumGet(addrStr)
                        if (num == "") :
                            print "Invalid numeric constant"
                            sys.exit(1)
                        num = IntToBinary(num,32)
                        setMem(addr, num,line,lnum)
                    else:
                        lbl = LblGet(addrStr)
                        if (lbl == ""):
                            print "Invalid label address"
                            sys.exit(1)
                        lbl = IntToBinary(lbl,32)
                        setMem(addr,lbl,line,lnum)
                addr += 4
            #Deal with label:
            elif line.find(":") != -1:
                print "deal with label addr = " + str(addr)
                curr = line.strip().split(':')
                labelName = curr[0].upper()
                print "label name : " + labelName 
                if passNum == 1:
                    print "label pass 1"
                    if (labelName in lbs.keys()):
                        print "label already defined"
                        sys.exit(1)
                else:
                    print "label pass 2"
                    if (LblGet(labelName) != addr):
                        print "/nlabelGet =" + str(LblGet(labelName))
                        print "address =" + str(addr)
                        print "/nLabel is pass 2 not the same as in pass 1"
                lbs[labelName] = addr
                print labelName
                print "put value to lbs"
        
                print "label addr" + hex(addr)
            #Deal with actual opcode instructions
            else: # re.match(r'\s([a-zA-Z]+)',line) or line.find('SW') != -1 or line.find('LW') != -1 or line.find('JAL') != -1:
                print '\n instructions'
                curr = line.strip().split()
                curOpcode = curr[0].upper()
                pcMemTable[pc] = addr
                memPcTable[addr] = pc
                # print '\nopcode = {}, args = {}'.format(curOpcode,curArgs)
                #not valid opcode
                if (curOpcode not in opcodeMap.keys()):
                    print "invalid opcode"
                    sys.exit()
                #normal opcode
                if (curOpcode in opcodeMap.keys()) and (curOpcode not in isa_ITEXT):
                    print "\nnormal opcode"
                    curArgs = curr[1]
                    if (passNum == 2):
                        print "\n opcode in pass 2"
                        asmInstr(curOpcode, curArgs, addr, line, lnum,pc)
                    memText[addr] = line.strip() + '\n'
                    print "put text to mem text " + line.strip() + " "+str(addr)
                    addr += 4
                    pc += 1
                #implemented opcode
                elif curOpcode in isa_ITEXT :
                    print '\nimplemented opcode'
                    tup = tuple(opcodeMap[curOpcode]['ITEXT'])
                    print len(tup)
                    if curOpcode == 'RET':
                        curArgs = ""
                    else:
                        curArgs = curr[1]
                    for i in range(0,len(tup)):
                        if passNum == 2:  
                            ImpInst(curOpcode,curArgs,tup[i],addr,line,lnum,pc)
                        memText[addr] = line.strip() + '\n'
                        print "put text to mem text" + line.strip() + " "+ str(addr)
                        addr += 4
                        pc += 1
                        
                else:
                    print "invalid opcode:" + str(curOpcode)
                    sys.exit()
            #else:
            #   print "invalid line:" + str(lnum)
            #  sys.exit 
            lnum = lnum + 1  
print "pass done pc" + str(pc)
#start write
Memwords = 2048
AddrGran = 1
outputfile = open(outputfileName,'w')
outputfile.write("WIDTH=32;\nDEPTH=2048;\nADDRESS_RADIX=HEX;\nDATA_RADIX=HEX;\nCONTENT BEGIN\n")
#outputfile.write("[00000000..0000000f] : DEAD;\n")
fillStart = 0
for i in range(0,Memwords):
    cur = i * (WordSize/(8*AddrGran))

    if cur in memTable.keys():
        if (fillStart < i):
            outputfile.write("[{:08x}..{:08x}] : DEAD;\n".format(fillStart, i -1)) 
            print "DEAD"  
        if (cur in memText.keys()): 
            #print "pc " + str(pc)  
            outputfile.write("--@ 0x{:08x} : ".format(cur))
            #print  (hex(int(memTable[cur],2))[2:].zfill(8))
            outputfile.write("{}".format(memText[cur]))
            #print memText[cur]
            out = hex(int(memTable[cur],2))[2:].zfill(8)
            outputfile.write("{:08x} : {};\n".format(i,out))

            fillStart = i + 1
    
if fillStart < Memwords:
    outputfile.write("[{:04x}..{:04x}] : DEAD;\n".format(fillStart,Memwords - 1))
outputfile.write("END;\n")
outputfile.close()
print "all finish"
