import re

def MyHex(i, j=6):
	t = hex(i).replace('0x','')
	if len(t) < j:
		t = ''.join(['0' for x in range(j-len(t))])+t
	elif len(t) > j:
		raise Exception('overflow')
	return t.upper()

class Instruction():
	def __init__(self, line):
		s = line[0]
		line = line.replace(', ',',')
		line = line.replace(' ,',',')
		line = line.split()
		if len(line) == 2:
			if s=='\t' or s==' ':
				line.insert(0,'')
			else:
				line.insert(2,'')
		elif len(line) == 1:
			line.insert(0,'')
			line.insert(2,'')
		line.insert(3,None)
		self.ins = line
	def __str__(self):
		l = self.Label()
		o = self.Operate()
		p = self.Param()
		if len(l) < 7:
			l = l + ''.join([' ' for x in range(7-len(l))])
		if len(o) < 7:
			o = o + ''.join([' ' for x in range(7-len(o))])
		if len(p) < 7:
			p = p + ''.join([' ' for x in range(7-len(p))])
		return 'Label: \''+l+'\'  Operate:\''+o+'\'  Param:\''+p+'\''
	def Label(self):
		return self.ins[0]
	def Operate(self):
		return self.ins[1]
	def Param(self):
		return self.ins[2]
	def Address(self):
		return self.ins[3]
	def Set_Address(self, addr):
		self.ins.insert(3, addr)
class	OPtable():
	def __init__(self, list=[]):
		try:
			self.OPTAB = {code.split()[0]:[int(code.split()[1],16),int(code.split()[2])] for code in list}
		except:
			self.OPTAB = {}
			raise Exception('input format error')
	def __str__(self):
		return '\n'.join([x+' \t'+hex(self.OPTAB[x][0]).upper()+' \t'+str(self.OPTAB[x][1]) for x in self.OPTAB])
	def Is_in_OPtable(self, op):
		return op in self.OPTAB
	def Format_Search(self, op):
		return self.OPTAB[op][1]
	def HexCode_Search(self, op):
		return hex(self.OPTAB[op][0])
	def CodeValue_Search(self, op):
		return self.OPTAB[op][0]
class ASM():
	def __init__(self):
		self.attribute ={
			'name': None,
			'start': None,
			'end': None
		}
		self.DIRECTIVES ={}
		self.OPTAB = OPtable()
		self.SYMTAB = {
			'A':0,
			'X':1,
			'L':2,
			'B':3,
			'S':4,
			'T':5,
			'F':6,
			'PC':8,
			'SW':9,
		}
		self.ins_list = []
		self.objcode = []
	def OpTable(self):
		return self.OPTAB
	def SymbolTable(self):
		return self.SYMTAB
	def Directives(self):
		return self.DIRECTIVES
	def Program_Start(self):
		return self.attribute['start']
	def Program_End(self):
		return self.attribute['end']
	def Instruction_List(self):
		return self.ins_list
	def Program_Name(self):
		return self.attribute['name']
	def RESET(self):
		self.__init__()
	def Set_Start_Address(self):
		for x in self.ins_list:
			if x.Operate() == 'START':
				self.attribute['start'] = int(x.Param())
		if self.attribute['start'] == None:
			raise Exception('without start directives')
	def Set_Program_Name(self):
		for x in self.ins_list:
			if x.Operate() == 'START':
				self.attribute['name'] = x.Label()
		if self.attribute['name'] == None:
			raise Exception('without start directives')
	def OPTAB_SETUP(self, file_name = 'utils/opcode'):
		try:
			f = open(file_name, 'r')
			self.OPTAB = OPtable(f.readlines())
			f.close()
		except Exception as e:
			raise e
	def SYMTAB_SETUP_AND_ADDRESS_ASSIGN(self):
		self.Set_Start_Address()
		self.Set_Program_Name()
		PC = self.attribute['start']
		for ins in self.ins_list:
		#setting address
			ins.Set_Address(PC)
		#put into Symbol table
			sym = ins.Label()
			if sym != '':
				if sym in self.SYMTAB:
					raise Exception('Duplicate definition')
				self.SYMTAB[sym] = PC
		#calculate Address of next instruction
			if ins.Operate() == 'BYTE':
				t = ins.Param()[0]
				if t == 'X':
					PC += (len(ins.Param()[1:].replace("'",''))+1)//2
				elif t == 'C':
					PC += len(ins.Param()[1:].replace("'",''))
				else:
					t = hex(int(ins.Param))
					t.replace('0x','')
					PC += (len(t)+1)//2
			elif ins.Operate() == 'WORD':
				PC += 3
			elif ins.Operate() == 'RESB':
				PC += int(ins.Param())
			elif ins.Operate() == 'RESW':
				PC += int(ins.Param())*3
			elif ins.Operate() == 'END':
				self.attribute['end'] = PC
			else:
				s = ins.Operate().replace('+','')
				if self.OPTAB.Is_in_OPtable(s):
					s_size = self.OPTAB.Format_Search(s)
					if (s_size) ==3 and ('+' in ins.Operate()):
						s_size = 4
					PC += s_size
		if self.attribute['end'] == None:
			self.attribute['end'] = PC
	def DIRECTIVES_SETUP(self, file_name = 'utils/directives'):
		try:
			f = open(file_name, 'r')
			self.DIRECTIVES = {word.replace('\n','') for word in f.readlines()}
			f.close()
		except Exception as e:
			raise e
	def Load_Instructions(self, file_name):
		try:
			f = open(file_name,'r')
			for x in f.readlines():
				if x.split()!=[]:
					self.ins_list.append(Instruction(x))
			f.close()
		except Exception as e:
			raise e
	def Compile(self, record_length_upper_bound = '0xFF'):
		########################  h record  ########################
		h = 'H'+'˰'+self.Program_Name()+'˰'+MyHex(self.Program_Start())+'˰'+MyHex(self.Program_End())
		###  m record declare  ##
		m_list = []
		########################  t record  ########################
		'''
		if put object code into entity
			1.check if the start has been setup or not
				--if not:
					setup the start address
					then continue your work
			2.check if the length can afford this object code
				--if not:
					cut t record and put into t_list
					start a new t record
					then continue your work
			3. if object code has information about ""absolute address of a label""
				add m record in to m_list
		'''
		t_list = []
		t = ''
		start = None
		length = 0##upper bound 0xFF
		upper_bound = record_length_upper_bound
		entity = ''
		
		BASE = 0
		base_ready = False
		for ins in self.ins_list:
			if t == '':
				t = 'T'+'˰'
			op = ins.Operate().replace('+','')
			par = ins.Param()
			addr = ins.Address()
			if self.OPTAB.Is_in_OPtable(op):########################################################## Operate
				#check if not yet start
				if start == None:
					start = addr
				fmt = self.OPTAB.Format_Search(op)
				if fmt == 1:######################################################## format 1 case
					#put into t record
					length += fmt
					entity = entity + MyHex(self.OPTAB.CodeValue_Search(op),2) + '˰'
				elif fmt == 2:###################################################### format 2 case
					#check if beyond bound or not
					if length+fmt > int(upper_bound,16):
						#cut t record
						t = t + MyHex(start) + '˰' + MyHex(length,2) + '˰' + entity
						t_list.append(t)
						#start a new t record
						t = 'T'+'˰'
						start = addr
						length = 0
						entity = ''
					par = par.split(',')
					par.append('A')
					r1 = par[0]
					r2 = par[1]
					#put into t record
					length += fmt
					entity = entity + MyHex(self.OPTAB.CodeValue_Search(op),2) + MyHex(self.SYMTAB[r1],1) + MyHex(self.SYMTAB[r2],1) + '˰'
				elif fmt == 3:###################################################### format 3/4 case
					n = '@' in par
					i = '#' in par
					x = ',X' in par
					e = '+' in ins.Operate()
					b = None
					p = None
					if e:
						fmt = 4
					#check if beyond bound or not
					if length+fmt > int(upper_bound,16):
						#cut t record
						t = t + MyHex(start) + '˰' + MyHex(length,2) + '˰' + entity
						t_list.append(t)
						#start a new t record
						t = 'T'+'˰'
						start = addr
						length = 0
						entity = ''
					#handle parameter
					par = par.replace('@','')
					par = par.replace('#','')
					par = par.replace(',X','')
					disp = None
					disp4 = None
					if par in self.SYMTAB:#Label
						label_addr = self.SYMTAB[par]
						if fmt == 3:
							pc_label = label_addr-(addr+fmt)
							base_label = label_addr-BASE
							if -2048 <= pc_label <= 2047:#(PC)+disp
								p = True
								b = False
								disp = pc_label
							elif base_ready and (0 <= base_label <= 4095):#(BASE)+disp
								p = False
								b = True
								disp = base_label
							else:
								raise Exception('label can\'t reach')
						elif fmt == 4:##ignore label address larger than 0xFFFFF case##
							p = False
							b = False
							disp4 = label_addr
							#generate m record and put into m_list
							m = 'M' + '˰' + MyHex(addr+1, 6) + '˰' + '05'
							m_list.append(m)
					elif par == '':#empty case
						p = False
						b = False
						disp = 0
						disp4 = 0
					else:#the data assign by programer
						##int assign
						p = False
						b = False
						disp = int(par)
						disp4 = int(par)
					#calculate object code
					if not n and not i:#simple #####ignore SIC simulation case 
						n = True
						i = True
					objcode = self.OPTAB.CodeValue_Search(op)
					if n:
						objcode += 2
					if i:
						objcode += 1
					if x:
						objcode = (objcode<<1)+1
					else:
						objcode = objcode<<1
					if b:
						objcode = (objcode<<1)+1
					else:
						objcode = objcode<<1
					if p:
						objcode = (objcode<<1)+1
					else:
						objcode = objcode<<1
					if e:
						objcode = (objcode<<1)+1
					else:
						objcode = objcode<<1
					if fmt == 3:
						if disp<0:
							objcode = ((objcode+1) << 12) + disp
						else:
							objcode = (objcode << 12) + disp
						objcode = MyHex(objcode, 6)
					elif fmt == 4:
						objcode = (objcode << 20) + disp4
						objcode = MyHex(objcode, 8)
					#put into t record
					length += fmt
					entity = entity + objcode + '˰'
			elif op in self.DIRECTIVES:############################################################### directives
				if op == 'START':################################################### START case
					pass
				elif op == 'END':################################################### END case
					pass
				elif op == 'BYTE':################################################## BYTE case
					#check if not yet start
					if start == None:
						start = addr
					if par[0] == 'C':#########################character case
						#convert into hex
						ct=par.replace("'",'')[1:]
						s=''
						for c in ct:
							s+=MyHex(ord(c),2)
						#check if beyond bound or not
						if length+len(ct) > int(upper_bound,16):
							#cut t record
							t = t + MyHex(start) + '˰' + MyHex(length,2) + '˰' + entity
							t_list.append(t)
							#start a new t record
							t = 'T'+'˰'
							start = addr
							length = 0
							entity = ''
						#put into t record
						length += len(ct)
						entity = entity + s +'˰'
					elif par[0] == 'X':#######################hex case
						#calculate lenth of hex code
						xt=par.replace("'",'')[1:]
						loft=(len(xt)+1)//2
						v=int(xt,16)
						#check if beyond bound or not
						if length+loft > int(upper_bound,16):
							#cut t record
							t = t + MyHex(start) + '˰' + MyHex(length,2) + '˰' + entity
							t_list.append(t)
							#start a new t record
							t = 'T'+'˰'
							start = addr
							length = 0
							entity = ''
						#put into t record
						length += loft
						entity = entity + MyHex(v,loft*2) + '˰'
					else:#####################################integer case
						#convert into hex
						it=hex(int(par)).replace('0x','')
						it=(len(it)+1)//2
						#check if beyond bound or not
						if length+t > int(upper_bound,16):
							#cut t record
							t = t + MyHex(start) + '˰' + MyHex(length,2) + '˰' + entity
							t_list.append(t)
							#start a new t record
							t = 'T'+'˰'
							start = addr
							length = 0
							entity = ''
						#put into t record
						length += it
						entity = entity + MyHex(int(par),it) + '˰'
				elif op == 'WORD':################################################## WORD case
					#check if not yet start
					if start == None:
						start = addr
					#check if beyond bound or not
					if length+3 > int(upper_bound,16):
							#cut t record
							t = t + MyHex(start) + '˰' + MyHex(length,2) + '˰' + entity
							t_list.append(t)
							#start a new t record
							t = 'T'+'˰'
							start = addr
							length = 0
							entity = ''
					length+=3
					entity = entity + MyHex(int(par)) + '˰'
				elif op == 'RESB' or op == 'RESW':################################## RESB/RESW case
					if start != None:#in t record
						#cut record
						t = t + MyHex(start) + '˰' + MyHex(length,2) + '˰' + entity
						t_list.append(t)
						#start a new t record
						t = 'T'+'˰'
						start = None
						length = 0
						entity = ''
				elif op == 'BASE':
					BASE = self.SYMTAB[par]
					base_ready = True
			else:#worng input
				raise Exception('instruction parsing error')
			#check t record length
			if length == int(upper_bound,16):
				#cut record
				t = t + MyHex(start) + '˰' + MyHex(length,2) + '˰' + entity
				t_list.append(t)
				#start a new t record
				t = 'T'+'˰'
				start = None
				length =0
				entity = ''
		#put into t_list
		t = t + MyHex(start) + '˰' + MyHex(length,2) + '˰' + entity
		t_list.append(t)
		########################  e record  ########################
		e = 'E'+'˰'+MyHex(self.Program_Start())
		########################  return object program  ########################
		objprogram = {
			'h_record' : h,
			't_record' : t_list,
			'm_record' : m_list,
			'e_record' : e,
			'object_program' : [h] + t_list + m_list + [e],
		}
		return objprogram