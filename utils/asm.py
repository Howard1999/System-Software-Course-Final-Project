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
		l=line
		try:
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
			self.literal_identify = False
		except:
			raise Exception('instruction parsing error: '+l)
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
	def Set_Param(self, par):
		self.ins[2] = par
	def Address(self):
		return self.ins[3]
	def Set_Address(self, addr):
		self.ins.insert(3, addr)
	def Literal(self):
		return self.literal_identify
	def Enable_Literal(self):
		self.literal_identify = True
	def Disable_Literal(self):
		self.literal_identify = False
class OPtable():
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
		self.DEBUG=False
		self.attribute ={
			'name' : None,
			'start' : None,
			'end' : None
		}
		self.DIRECTIVES ={}
		self.OPTAB = OPtable()
		self.SYMTAB = {
			'A':[0,'A'],
			'X':[1,'A'],
			'L':[2,'A'],
			'B':[3,'A'],
			'S':[4,'A'],
			'T':[5,'A'],
			'F':[6,'A'],
			'PC':[8,'A'],
			'SW':[9,'A'],
		}
		self.Literal_Address = {}
		self.ins_list = []
		self.origin_ins_list = []
		self.objcode = []
	def Turn_On_Debug(self):
		self.DEBUG = True
	def Turn_Off_Debug(self):
		self.DEBUG = False
	def OpTable(self):
		return self.OPTAB
	def SymbolTable(self):
		return self.SYMTAB.copy()
	def Directives(self):
		return self.DIRECTIVES.copy()
	def Program_Start(self):
		return self.attribute['start']
	def Program_End(self):
		return self.attribute['end']
	def Instruction_List(self):
		return self.origin_ins_list.copy()
	def Instruction_List_After_Handler(self):
		return self.ins_list.copy()
	def Literals(self):
		return self.Literal_Address.copy()
	def Program_Name(self):
		return self.attribute['name']
	def RESET(self):
		self.__init__()
	def Check_Start_Directive(self):
		if self.ins_list[0].Operate() == 'START':
			return True
		return False
	def OPTAB_SETUP(self, file_name = 'utils/opcode'):
		try:
			if self.DEBUG:
				print('Load OPTAB...>',end='')
			f = open(file_name, 'r')
			self.OPTAB = OPtable(f.readlines())
			f.close()
			if self.DEBUG:
				print('Success')
				print(self.OPTAB)
		except Exception as e:
			if self.DEBUG:
				print('Fail')
			raise e
	def Blocks_Handler(self):
		if self.DEBUG:
			print('Handel program block...>',end='')
		blocks = {
			'(default)' : [],
			'CDATA' : [],
			'CBLKS': []
		}
		imm_block = '(default)'
		for ins in self.ins_list:
			if ins.Operate() == 'USE':
				if ins.Param() in blocks:
					imm_block = ins.Param()
				elif ins.Param() == '':
					imm_block = '(default)'
				else:
					raise Exception('BLOCK name error at:'+str(ins))
			else:
				blocks[imm_block].append(ins)
		self.ins_list = blocks['(default)'] + blocks['CDATA'] + blocks['CBLKS']
		if self.DEBUG:
			print('Success')
	def Literal_Handler(self):
		if self.DEBUG:
			print('Handel literal...>',end='')
		def int_to_chr(i):
			if 0<=i<=(26*26-1):
				return chr(ord('A')+(i//26)) + chr(ord('A')+(i%26))
			else:
				raise Exception('Out of range')
		count = 0
		queue = []
		index = 0
		cp_ins_list = self.ins_list.copy()
		for ins in cp_ins_list:
			op = ins.Operate()
			par = ins.Param()
			if '=' in par and self.OPTAB.Is_in_OPtable(op):#literal
				set=False
				for q in queue:
					if q.Param()==par.replace('=','') and par.replace('=','')!='*':
						self.ins_list[index].Set_Param('='+q.Label())
						set=True
						break
				if set:
					index += 1
					continue
				t = int_to_chr(count)
				i = Instruction(t+' BYTE '+par.replace('=',''))
				i.Enable_Literal()
				queue.append(i)
				self.ins_list[index].Set_Param('='+t)
				count += 1
			elif op == 'LTORG':#directive
				for q in queue:
					self.ins_list.insert(index+1, q)
					index += 1
				queue = []
			index += 1
		self.ins_list = self.ins_list + queue
		if self.DEBUG:
			print('Success')
	def SYMTAB_SETUP_AND_ADDRESS_ASSIGN(self):
		if self.DEBUG:
			print('Build symbol table and address assign...>')
		#START directive
		if not self.Check_Start_Directive():
			raise Exception('Without START directives')
		else:
			self.attribute['start'] = int(self.ins_list[0].Param())
			self.attribute['name'] = self.ins_list[0].Label()
			PC = self.attribute['start']
			end_of_program = PC
		for ins in self.ins_list:
			if self.DEBUG:
				print('addr:'+str(PC),ins)
		#set instruction address
			ins.Set_Address(PC)
		#put into Symbol table
			sym = ins.Label()
			if self.OPTAB.Is_in_OPtable(sym) or sym in self.DIRECTIVES:
				raise Exception('Label Name Not Allow at:',str(ins))
			if ins.Literal():
				self.Literal_Address[sym] = PC
			elif sym != '':
				if sym in self.SYMTAB:
					raise Exception('Duplicate definition at:'+str(ins))
				if ins.Operate() == 'EQU':
					try:
						self.SYMTAB[sym] = [int(ins.Param()),'A']
					except:
						if re.search('.+\*.+',ins.Param()):#multi
							self.SYMTAB[sym] = [ins.Param(),'U']
						elif ins.Param().count('*')<=1:#pc
							self.SYMTAB[sym] = [ins.Param().replace('*',str(int(PC))),'U']
						else:#error
							raise Exception("Symbol definition error: "+sym)
				else:
					self.SYMTAB[sym] = [PC,'R']
		#calculate Address of next instruction
			if ins.Operate() == 'BYTE':
				t = ins.Param()[0]
				if t == 'X':
					PC += (len(ins.Param()[1:].replace("'",''))+1)//2
					if PC>end_of_program:
						end_of_program = PC
				elif t == 'C':
					PC += len(ins.Param()[1:].replace("'",''))
					if PC>end_of_program:
						end_of_program = PC
			elif ins.Operate() == 'WORD':
				PC += 3
				if PC>end_of_program:
						end_of_program = PC
			elif ins.Operate() == 'RESB':
				PC += int(ins.Param())
				if PC>end_of_program:
						end_of_program = PC
			elif ins.Operate() == 'RESW':
				PC += int(ins.Param())*3
				if PC>end_of_program:
						end_of_program = PC
			elif ins.Operate() == 'END':
				pass
			elif ins.Operate() == 'ORG':
				try:
					PC = self.SYMTAB[ins.Param()][0]
				except:
					raise Exception('Symbol is not definition yet at:'+str(ins))
			else:
				s = ins.Operate().replace('+','')
				if self.OPTAB.Is_in_OPtable(s):
					s_size = self.OPTAB.Format_Search(s)
					if (s_size) == 3 and ('+' in ins.Operate()):
						s_size = 4
					PC += s_size
					if PC>end_of_program:
						end_of_program = PC
		self.attribute['end'] = end_of_program
		if self.DEBUG:
			print(self.SYMTAB)
	def Symbol_Defining_Handler(self):
		if self.DEBUG:
			print('Handel symbol defining...>',end='')
		#check
		for sym in self.SYMTAB:
			par = self.SYMTAB[sym][0]
			flag = self.SYMTAB[sym][1]
			if flag == 'U':
				if '+' in par:
					par = par.split('+')
				elif '-' in par:
					par = par.split('-')
				elif '/' in par:
					par = par.split('/')
				elif '*' in par:
					par = par.split('*')
				else:
					par = [par]
				for p in par:
					try:
						int(p)
					except:
						if p not in self.SYMTAB:
							raise Exception("EQU expression can't be solved: "+sym)
		#solve
		def solved():
			for sym in self.SYMTAB:
				if self.SYMTAB[sym][1] == 'U':
					return False
			return True
		count = 0
		while not solved():
			for sym in self.SYMTAB:
				par = self.SYMTAB[sym][0]
				flag = self.SYMTAB[sym][1]
				if flag == 'U':
					if '+' in par:
						op = '+'
						par = par.split('+')
					elif '-' in par:
						op = '-'
						par = par.split('-')
					elif '/' in par:
						op = '/'
						par = par.split('/')
					elif '*' in par:
						op = '*'
						par = par.split('*')
					else:
						par=[par]
					if len(par)==1:
						try:#PC
							self.SYMTAB[sym] = [int(par[0]),'R']
						except:
							if self.SYMTAB[par[0]][1]!='U':
								self.SYMTAB[sym] = [self.SYMTAB[par[0]][0],self.SYMTAB[par[0]][1]]
					elif len(par)==2:
						try:
							v1 = int(par[0])
							v1_type = 'A'
						except:
							if self.SYMTAB[par[0]][1]=='U':
								continue
							v1 = self.SYMTAB[par[0]][0]
							v1_type = self.SYMTAB[par[0]][1]
						try:
							v2 = int(par[1])
							v2_type = 'A'
						except:
							if self.SYMTAB[par[1]][1]=='U':
								continue
							v2 = self.SYMTAB[par[1]][0]
							v2_type = self.SYMTAB[par[1]][1]
						if op=='+':
							if v1_type=='A' and v2_type=='A':
								self.SYMTAB[sym] = [v1+v2,'A']
							elif v1_type=='R' and v2_type=='A':
								self.SYMTAB[sym] = [v1+v2,'R']
							elif v1_type=='A' and v2_type=='R':
								self.SYMTAB[sym] = [v1+v2,'R']
							else:
								raise Exception("Symbol definition error: "+sym)
						elif op=='-':
							if v1_type=='A' and v2_type=='A':
								self.SYMTAB[sym] = [v1-v2,'A']
							elif v1_type=='R' and v2_type=='A':
								self.SYMTAB[sym] = [v1-v2,'R']
							elif v1_type=='R' and v2_type=='R':
								self.SYMTAB[sym] = [v1-v2,'A']
							else:
								raise Exception("Symbol definition error: "+sym)
						elif op=='/':
							if v1_type=='A' and v2_type=='A':
								self.SYMTAB[sym] = [v1//v2,'A']
							else:
								raise Exception("Symbol definition error: "+sym)
						elif op=='*':
							if v1_type=='A' and v2_type=='A':
								self.SYMTAB[sym] = [v1*v2,'A']
							else:
								raise Exception("Symbol definition error: "+sym)
			count+=1
			if count>=len(self.SYMTAB):
				raise Exception('Recurse symbol definition')
		if self.DEBUG:
			print('Success')
			print(self.SYMTAB)
	def DIRECTIVES_SETUP(self, file_name = 'utils/directives'):
		try:
			if self.DEBUG:
				print('Load directives table...>',end='')
			f = open(file_name, 'r')
			self.DIRECTIVES = {word.replace('\n','') for word in f.readlines()}
			f.close()
			if self.DEBUG:
				print('Success')
				print(self.DIRECTIVES)
		except Exception as e:
			if DEBUG:
				print('Fail')
			raise e
	def Load_Instructions(self, file_name):
		try:
			if self.DEBUG:
				print('Load instructions...>')
			f = open(file_name,'r')
			for x in f.readlines():
				if x.split()!=[]:
					self.ins_list.append(Instruction(x))
					self.origin_ins_list.append(Instruction(x))
					if self.DEBUG:
						print(self.ins_list[len(self.ins_list)-1])
			f.close()
		except Exception as e:
			raise Exception('Open file failure')
	def Compile(self, record_length_upper_bound = '0xFF',split_symbol = '˰'):
		if self.DEBUG:
			print('Compile...>')
		########################  h record  ########################
		h = 'H'+split_symbol+self.Program_Name()+split_symbol+MyHex(self.Program_Start())+split_symbol+MyHex(self.Program_End())
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
			if self.DEBUG:
				print(str(ins)+' ',end='')
			if t == '':
				t = 'T'+split_symbol
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
					if self.DEBUG:
						print(MyHex(self.OPTAB.CodeValue_Search(op),2))
					entity = entity + MyHex(self.OPTAB.CodeValue_Search(op),2) + split_symbol
				elif fmt == 2:###################################################### format 2 case
					#check if beyond bound or not
					if length+fmt > int(upper_bound,16):
						#cut t record
						t = t + MyHex(start) + split_symbol + MyHex(length,2) + split_symbol + entity
						t_list.append(t)
						#start a new t record
						t = 'T'+split_symbol
						start = addr
						length = 0
						entity = ''
					par = par.split(',')
					par.append('A')
					r1 = par[0]
					r2 = par[1]
					#put into t record
					length += fmt
					if self.DEBUG:
						print(MyHex(self.OPTAB.CodeValue_Search(op),2) + MyHex(self.SYMTAB[r1][0],1) + MyHex(self.SYMTAB[r2][0],1))
					entity = entity + MyHex(self.OPTAB.CodeValue_Search(op),2) + MyHex(self.SYMTAB[r1][0],1) + MyHex(self.SYMTAB[r2][0],1) + split_symbol
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
						t = t + MyHex(start) + split_symbol + MyHex(length,2) + split_symbol + entity
						t_list.append(t)
						#start a new t record
						t = 'T'+split_symbol
						start = addr
						length = 0
						entity = ''
					#handle parameter
					par = par.replace('@','')
					par = par.replace('#','')
					par = par.replace(',X','')
					disp = None
					disp4 = None
					if par in self.SYMTAB or '=' in par or '*' in par:#Label or Literal or PC Assignment
						#Label Address Assign
						if '=' in par:
							label_addr = self.Literal_Address[par.replace('=','')]
						#PC Assignment
						elif '*' in par:
							#only accept {*(+-)int} form
							try:
								if par == '*':
									label_addr = addr
								elif not re.search('.+\*.+',par) and '/' not in par:
									label_addr = addr + int(par.replace('*',''))
								else:
									raise Exception()
							except:
								raise Exception('Expression is illegal at:'+str(ins))
						else:
							label_addr = self.SYMTAB[par][0]
						#Caulate disp
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
								raise Exception('Label can\'t Reach at:'+str(ins))
						elif fmt == 4:##ignore label address larger than 0xFFFFF case##
							p = False
							b = False
							disp4 = label_addr
							#generate m record and put into m_list
							if self.SYMTAB[par][1]=='R':
								m = 'M' + split_symbol + MyHex(addr+1, 6) + split_symbol + '05'
								m_list.append(m)
					elif par == '':#empty case
						p = False
						b = False
						disp = 0
						disp4 = 0
					else:#the data assign by programer
						try:
							##int assign
							p = False
							b = False
							disp = int(par)
							disp4 = int(par)
						except:
							raise Exception('Parameter Error: at'+str(ins))
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
					if self.DEBUG:
						print(objcode)
					entity = entity + objcode + split_symbol
			elif op in self.DIRECTIVES:############################################################### directives
				if op == 'START' or op == 'END' or op == 'USE' or op == 'LTORG' or op == 'ORG' or op == 'EQU':
					if self.DEBUG:
						print()
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
							t = t + MyHex(start) + split_symbol + MyHex(length,2) + split_symbol + entity
							t_list.append(t)
							#start a new t record
							t = 'T'+split_symbol
							start = addr
							length = 0
							entity = ''
						#put into t record
						length += len(ct)
						if self.DEBUG:
							print(s)
						entity = entity + s +split_symbol
					elif par[0] == 'X':#######################hex case
						#calculate lenth of hex code
						xt=par.replace("'",'')[1:]
						loft=(len(xt)+1)//2
						v=int(xt,16)
						#check if beyond bound or not
						if length+loft > int(upper_bound,16):
							#cut t record
							t = t + MyHex(start) + split_symbol + MyHex(length,2) + split_symbol + entity
							t_list.append(t)
							#start a new t record
							t = 'T'+split_symbol
							start = addr
							length = 0
							entity = ''
						#put into t record
						length += loft
						if self.DEBUG:
							print(MyHex(v,loft*2))
						entity = entity + MyHex(v,loft*2) + split_symbol
					else:
						raise Exception('Parsing error at: '+str(ins))
				elif op == 'WORD':################################################## WORD case
					#check if not yet start
					if start == None:
						start = addr
					#check if beyond bound or not
					if length+3 > int(upper_bound,16):
							#cut t record
							t = t + MyHex(start) + split_symbol + MyHex(length,2) + split_symbol + entity
							t_list.append(t)
							#start a new t record
							t = 'T'+split_symbol
							start = addr
							length = 0
							entity = ''
					length+=3
					if self.DEBUG:
						print(MyHex(int(par)))
					entity = entity + MyHex(int(par)) + split_symbol
				elif op == 'RESB' or op == 'RESW':################################## RESB/RESW case
					if self.DEBUG:
						print()
					if start != None:#in t record
						#cut record
						t = t + MyHex(start) + split_symbol + MyHex(length,2) + split_symbol + entity
						t_list.append(t)
						#start a new t record
						t = 'T'+split_symbol
						start = None
						length = 0
						entity = ''
				elif op == 'BASE':################################################## BASE case
					if self.DEBUG:
						print()
					if par=='*':
						BASE = addr
					else:
						BASE = self.SYMTAB[par][0]
					base_ready = True
			else:#worng input
				raise Exception('Instruction Parsing Error at:'+str(ins))
			#check t record length
			if length == int(upper_bound,16):
				#cut record
				t = t + MyHex(start) + split_symbol + MyHex(length,2) + split_symbol + entity
				t_list.append(t)
				#start a new t record
				t = 'T'+split_symbol
				start = None
				length =0
				entity = ''
		#put into t_list
		if entity!='':
			t = t + MyHex(start) + split_symbol + MyHex(length,2) + split_symbol + entity
			t_list.append(t)
		########################  e record  ########################
		e = 'E'+split_symbol+MyHex(self.Program_Start())
		########################  return object program  ########################
		objprogram = {
			'h_record' : h,
			't_record' : t_list,
			'm_record' : m_list,
			'e_record' : e,
			'object_program' : [h] + t_list + m_list + [e],
		}
		return objprogram