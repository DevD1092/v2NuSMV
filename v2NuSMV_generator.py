#!/usr/bin/env python

# IMPORTANT GUIDELINES:  to whom so ever it may concern who is refering this code for extending it or for study purpose 
# Please read the NOTE instructions wherever mentioned carefully, as they describe the all the information brielfy!
# All the classes and their functions and their information are written in their comments. Even all the variables and lists and dictionaries and their respective functions are described in the comments beside them. So that one can easily understand what each thing is used for and its significance ahead.
# Finally for the extension purposes, the work is made easy. One can look at the TODO statements for extending the work and hope it will get extended to include the a large subset of Verilog Grammar one day!
# While running the code if one types '--log' in the input, one will receive all the information that this code parses and to 'just' get the input language of the NuSMV for the input Verilog HDL netlist donot type '--log' in the input!

import lex
import yacc
import sys
from re import *
import re

class wire: # Stores the information of the wire name and its width
	def __init__(self, name=None, source=None, loads=None, width=None):
		self.type='wire'
		self.name = name
		self.source = source
		self.loads = loads
		self.width = width
	def printinfo(self):
		print("Wire name: " + self.name)
		if self.width != None:
			print("-----> Width: " + str(self.width))

class assign: # Stores the information of the variables assigned and the values assigned to them
	def __init__(self, name=None, value=None):
		self.type='assign'
		self.name = name
		self.value = value
	def printinfo(self):
		print("Assign: " + self.name)
		print("------>" + self.value)

class port: # Stores the information of all the ports (Module and even Module Instances), with the port name,type, width and connection
	def __init__(self, name=None, porttype=None, width=None, connection=None):
		self.type='port'
		self.name=name #string (name of the port)
		self.porttype=porttype  #string in ('input', 'output')
		self.width=width  #tuple of integers (int1, int2)
		self.connection=connection   #string Stores the information of .port(connection)
	def printinfo(self):
		if log:
			print "> portname: ", self.name,
			print ";   porttype: ",  self.porttype,
			print ";   portwidth: ", self.width,
			print ";   connection: ", self.connection

class moduleinstance: # Stores the information of the module instances, module types and the ports (calls the class port)
	def __init__(self, moduletype=None, name=None, ports=None):
		self.type='moduleinstance'
		self.moduletype=moduletype #string (name of the module type)
		self.name=name #string (name of the module instance)
		self.ports=ports #list of port objects
	def printinfo(self):
		print("> Module instance. Name " + self.name + " of type " + self.moduletype)
		print("> Ports found: ")
		if self.ports != None:
			for i in self.ports:
				print "---> ",
				i.printinfo()


class item: # Stores the information regarding the module items contained in a module. 
	def __init__(self,itemtype=None, itemvalue=None):
		self.type=item    
		self.itemtype=itemtype  #can be LISTOFPORTS, LISTOFWIRES, MODULEINSTANCE,LISTOFASSIGNS
		self.itemvalue=itemvalue
		#it itemtype=LISTOFPORTS, itemvalue is of type list of port objects
		#if itemtype=LISTOFWIRES, itemvalue is a list of wire objects
		#if itemtype=MODULEINSTANCE, itemvalue is a moduleinstance object
		#if itemtype=LISTOFASSIGNS, itemvalue is a list of assign objects 
	def printinfo(self):
		print ("itemtype: " + self.itemtype)
		print ("itemvalue: ")
		try:
			if type(self.itemvalue)==list:
				for element in self.itemvalue:
					element.printinfo()
			else:
				self.itemvalue.printinfo()
		except:
			print("cannot print itemvalue")
		print " "

class module: # For extracting the information of the information stored in the above classes and trnaslation purposes. 
	def __init__(self, name=None, ports=None, wires=None, items=None):
		self.type = 'module'
		self.name = name  #string
		self.ports = ports #list of port objects for the Module Ports 
		self.port = port # list of the input and output port objects only
		self.wires = wires #list of wire objects
		self.items = items  #list of item objects
		self.connections_in_module = None #stores the information of what is connected to input output ports within the module.
		self.tot_modules = None # Stores the total no. of module Types 
		self.tot_modules_1 = None # Stores the total number of the name of the module instances
		self.tot_no_ports = None #Stores the total no. of expressions appearing in the port of the module instances   
		self.indi_ports = None   # stores the total no. of ports in a particular module instantiation  
		self.len_port = None #Stores the total no. of expressions in each module instance
		self.output = None #Stores the last expression of each and every module instance
		self.output_connection = None #Gives the Connection of the particular module instance and its output port!! 
		self.rem_ports = None #A list of the Remaining ports except the last port of each Module Instance
		self.rem_ports_conn = None # A dict
		self.o_ports = None # Output ports
		self.i_ports = None # Input Ports
		self.all_ports = None # All the Ports
		self.port_type = None # Port type
		self.width = None # Contains the list of Width of each Module Port and not the Module Instantiation port   
		self.w_i_port = None # Contains the width of the input ports 
		self.w_o_port = None # Contains the width of the output ports
		self.indi_ports = None # Contains the individual module instance's ports  
		self.test = None # A test variable
		self.allassigns = None # A list containing the particular variables on which the 'assign' statement is implemented!
		self.allvalues = None # A list containing the particular values assigned in the same order as the allassign list     
		self.__isparsed__ = False


	# NOTE: Please do not change any logical functions of for loop or if else statement in this function, as this is used to extract important and required information required for translation to NuSMV Code, because it has been tested on many input Verilog HDL code's and this thing works perfect! One can add information for extending the code and including the Verilog Grammar, but please do not alter or delete anything already prespecified!
	def extract_module_information(self):	
	   try:
					
		if self.items != None:
			allwiresfound = []
			allportsfound = []
			for itemobj in self.items:
				if itemobj.itemtype == 'LISTOFWIRES':
					allwiresfound += itemobj.itemvalue
			if allwiresfound != []:
				self.wires = allwiresfound
				#all the wires are now in self.wires 

		if self.wires != None:
			connections = {}
			for wireobj in self.wires:
				connections[wireobj.name] = []
				if self.items != None:
				    for itemobj in self.items:
					if itemobj.itemtype == 'MODULEINSTANCE':
						#found a module instance
						if itemobj.itemvalue.ports != None:
							for moduleport in itemobj.itemvalue.ports:
								if moduleport.connection != None:
									if moduleport.connection == wireobj.name:
										connections[wireobj.name] += [ (itemobj.itemvalue.name, itemobj.itemvalue.moduletype, moduleport.name) ]
			if connections != {}:
				self.connections_in_module = connections

		if self.items !=None:
			length = []
			output_conn = {} # A dictionary which stores the particular module instance and its last output element 
			ports_already = [] # An intermediate list for extracting the total ports of a module instance 
			tot_ports = [] # A list of total ports of the module instances 
			tot_indi_ports = [] # Total individual ports of any module instance 
			last_element = [] # Last element of each and every module instance for writing the output 
			modules_already = [] # An intermediate list for extracting the list of the modules 
			modules_already_1 = [] # An intermediate list for extracting the Name of the Module Instances 
			rem_ports_1 = [] #A list of the remaining ports  except the last port of each and every module instance 
			indi_ports_1 = [] # A list of the individual ports of each and every module instance 
			rem_ports_conn = {} # A dictionary which contains the connection of the particular name of the module instances with the remaining ports except the last port of each Module Instance  
			tot_no_modules = [] # list of strings of the module types 
			tot_no_modules_1 = [] #list of name of the module instances 
			for itemobj in self.items:
				if itemobj.itemtype == 'MODULEINSTANCE':
					#found a module instance
					if itemobj.itemvalue.moduletype !=None: 
					        tot_no_modules.append(itemobj.itemvalue.moduletype)
					for module_m in itemobj.itemvalue.name: 
						if itemobj.itemvalue.name not in modules_already_1:
							tot_no_modules_1.append(itemobj.itemvalue.name)
							modules_already_1.append(itemobj.itemvalue.name)
					if tot_no_modules_1 != []:
						self.tot_modules_1 = tot_no_modules_1
					if tot_no_modules != []:
						self.tot_modules = tot_no_modules

					tot_no_modules_11 = tot_no_modules_1
					tot_no_modules_ty = tot_no_modules
									
					for moduleport in itemobj.itemvalue.ports:
						if moduleport.connection not in ports_already:
								tot_ports.append(moduleport.connection)
								ports_already.append(moduleport.connection)
					if tot_ports != []:
						self.tot_no_ports = tot_ports

			for itemobj in self.items:
				if itemobj.itemtype == 'MODULEINSTANCE':
					#found a module instance 
					for module_n in tot_no_modules_1:
						for module_n1 in tot_no_modules_11:
							tot_indi_ports = []
							for moduleport in itemobj.itemvalue.ports:
								if(module_n == module_n1):
									tot_indi_ports.append(moduleport.connection)   
					self.indi_ports=tot_indi_ports
					l=len(tot_indi_ports)
					length.append(l)
					self.len_port=length
					last_element.append(tot_indi_ports[l-1])
					self.output=last_element
					output_conn = zip(tot_no_modules_1,last_element)
					self.output_connection = output_conn
					rem_ports = []
					indi_ports = []
					for i in range(l-1):
						rem_ports.append(tot_indi_ports[i])
					indi_ports = tot_indi_ports
					indi_ports_1.append(indi_ports)
					self.indi_ports = indi_ports_1
					rem_ports_1.append(rem_ports)
					self.rem_ports = rem_ports_1
					rem_ports_conn = zip(tot_no_modules_1,rem_ports_1)
					self.rem_ports_conn = rem_ports_conn
		if self.items !=None:
			o_ports = []
			i_ports = []
			all_ports = []
			already_ports = []
			port_type = []
			width = []
			w_i_port = []
			w_o_port = []
			for itemobj in self.items:
				if itemobj.itemtype == 'LISTOFPORTS':
					for port_i in itemobj.itemvalue:
						all_ports.append(port_i.name)
						port_type.append(port_i.porttype)
						width.append(port_i.width)
					for port_id in self.ports:
						if port_id.name not in already_ports:						
							already_ports.append(port_id.name)														
					self.all_ports = all_ports
					self.port_type = port_type
					self.width = width		
		for i in range(len(all_ports)):
			if port_type[i] == 'output' :
				o_ports.append(all_ports[i])
				w_o_port.append(width[i])
		self.o_ports = o_ports
		self.w_o_port = w_o_port 

		for i in range(len(all_ports)):
			if port_type[i] == 'input' :
				i_ports.append(all_ports[i])
				w_i_port.append(width[i])
		self.i_ports = i_ports  
		self.w_i_port = w_i_port
	
		
		# TODO : LOGIC FOR ASSIGN STATEMENTS TRANSLATION IN NuSMV CODE (STILL TO BE IMPLEMENTED)
		#if self.items !=None:
		#	allassigns = []
		#	allvalues = []
		#	already_assign = []
		#	for itemobj in self.items:
		#		if itemobj.itemtype == 'LISTOFASSIGNS':
		#			for assign_o in itemobj.itemvalue:
		#				allassigns.append(assign_o.name)
		#				allvalues.append(assign_o.value)
		#			self.allassigns = allassigns
		#			self.allvalues = allvalues

				   				
	   except:
		print("An error has occurred extracting information from the module. Some parts of the parser has to be implemented")

	def addports(self, portstoadd=None):
		#ports to add should be a list of port objects
		pass		

	def printinfo(self):
		if log:
	
			print("vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv")
			print "Module: "
			print "Name:  ", self.name
			print ("________")
			print "Ports: "
			try:
				for i in self.ports:
					i.printinfo()	
			except:
				print("Cannot print ports")
			print ("________")
			print "Wires: "
			if self.wires != None:
				for i in self.wires:
					i.printinfo(),

			print ("________")
			print "Assign Statements: "
			print self.allassigns 

			print("_________")
			print "The corresponding values assigned to the variables: "
			print self.allvalues 
		
			print ("________")
			print "Connections in the module: "
			if self.connections_in_module != None:
				for k in self.connections_in_module.keys():
					print(k + "  is connected to ")
					print "---> ",
					print self.connections_in_module[k]
	
			print ("________")
			print "Total Number of Module Types : "
			for k in self.tot_modules:
				print k	

			print ("________")
			print "Total Number of Ports in all the Module Instance: "
			for i in self.tot_no_ports:	
				print i
		
			print ("________")
			print "Total Number of the Name of the Module Instances: "
			for i in self.tot_modules_1:
				print i	

			print ("________")
			print ("Total Number of Ports in each module instance: ")
			for i in self.len_port:
				print i	

			print ("________")
			print ("Last element of each Module Instance: ")
			for i in self.output:
				print i

			print ("________")
			print "The corresponding Output of each module insatnce: "
			for k in self.output_connection:
				print (k[0] + " has the output port----->" + k[1])
				

			print ("________")
			print "The remaining ports except the last port of each and every module instance:"
			for i in self.rem_ports:
				print i
			

			print ("________")
			print "The corresponding ports for the individual module instances "
			for i in self.indi_ports:
				print i

			print ("________")
			print "Output Ports: "
			print self.o_ports 	

			print ("________")
			print "Input Ports: "
			print self.i_ports

			print ("________")
			print "All the Ports are: "
			print self.all_ports

			print ("________")
			print "Width of each Module Port and not the Module Instance Port: "
			print self.width 

			print ("________")
			print "Width of the Output Ports: "
			print self.w_o_port

			print ("________")
			print "Width of the Input Ports: "
			print self.w_i_port  
			
				
			print ("________")
			print "Items: "
			if self.items != None:
				for i in self.items:
						try:
							i.printinfo()
						except:
							print("cannot print information for item. ")
			else:
				print("No items present in the module. ")
			print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")

		if log or logmod:
			print("______________________________________________NuSMV Code__________________________________")
		pri = [] # A list which checks the already printed Module Types, so that to avoid redudancy of the already printed Module Types
		# TODO: DICT1 stores the logic of the output of the module instances, still all the logic functions from the NanGateOpenCell are not yet embedded into this, so extension has to be done
		dict1 = {'NOR3_X1' : '!(A1|A2|A3)', 'NOR3_X2' : '!(A1|A2|A3)', 'NOR3_X4' : '!(A1|A2|A3)', 'NOR2_X1' : '!(A1|A2)', 'NOR2_X2' : '!(A1|A2)', 'NOR2_X4' : '!(A1|A2)', 'MUX2_X1':'(!Sin&Ain)|(Sin&Bin)', 'MUX2_X2' : '(!Sin&Ain)|(Sin&Bin)', 'NAND2_X1' : '!(A1 & A2)', 'NAND2_X2' : '!(A1 & A2)', 'NAND2_X4' : '!(A1 & A2)', 'INV_X1' : '!A', 'INV_X16' : '!A', 'INV_X2' : '!A', 'INV_X32' : '!A', 'INV_X4' : '!A', 'INV_X8' : '!A', 'OAI22_X1' : '!((B1|B2)&(A1|A2))', 'OAI22_X2' : '!((B1|B2)&(A1|A2))', 'OAI22_X4' : '!((B1|B2)&(A1|A2))', 'AOI21_X1' : '!(A|(B1&B2))', 'OAI21_X1' : '!(A&(B1|B2))', 'OAI21_X2' : '!(A&(B1|B2))', 'OAI21_X4' : '!(A&(B1|B2))', 'AOI211_X1' : '!(A|B|(C1&C2))', 'OR2_X1' : '(A1|A2)', 'OR2_X2' : '(A1|A2)', 'OR2_X4' : '(A1|A2)', 'OAI211_X1' : '!(A&B&(C1|C2))', 'OAI211_X2' : '!(A&B&(C1|C2))', 'OAI211_X4' : '!(A&B&(C1|C2))', 'AND3_X1' : '(A1&A2&A3)', 'AOI22_X1' : '!((A1&A2)|(B1&B2))', 'XNOR2_X1' : '!(A1 xor A2)', 'XNOR2_X2' : '!(A1 xor A2)', 'NAND4_X1' :'!(A1&A2&A3&A4)', 'NAND4_X2' : '!(A1&A2&A3&A4)', 'NAND4_X4' : '!(A1&A2&A3&A4)', 'AND2_X1' : '(A1&A2)', 'AND2_X2' : '(A1&A2)', 'AND2_X4' : '(A1&A2)', 'AND3_X2' : '(A1&A2&A3)', 'AND3_X4' : '(A1&A2&A3)', 'AND4_X1' : '(A1&A2&A3&A4)', 'AND4_X2' : '(A1&A2&A3&A4)', 'AND4_X4' : '(A1&A2&A3&A4)', 'AOI211_X2' : '!(A|B|(C1&C2))', 'AOI211_X4' : '!(A|B|(C1&C2))', 'AOI21_X2' : '!(A|(B1&B2))', 'AOI21_X4' : '!(A|(B1&B2))', 'AOI221_X1' : '!(A|(B1&B2)|(C1&C2))', 'AOI221_X2' : '!(A|(B1&B2)|(C1&C2))', 'AOI221_X4' : '!(A|(B1&B2)|(C1&C2))', 'AOI222_X1' : '!((A1&A2)|(B1&B2)|(C1&C2))', 'AOI222_X2' : '!((A1&A2)|(B1&B2)|(C1&C2))', 'AOI222_X4' : '!((A1&A2)|(B1&B2)|(C1&C2))', 'AOI22_X2' : '!((A1&A2)|(B1&B2))', 'AOI22_X4' : '!((A1&A2)|(B1&B2))', 'BUF_X1' : 'A', 'BUF_X16' : 'A', 'BUF_X2' : 'A', 'BUF_X32' : 'A', 'BUF_X4' : 'A', 'BUF_X8' : 'A', 'CLKBUF_X1' : 'A', 'CLKBUF_X2' : 'A', 'CLKBUF_X3' : 'A', 'LOGIC0_X1' : '0', 'LOGIC1_X1' : '1', 'NAND3_X1' : '!(A1&A2&A3)', 'NAND3_X2' : '!(A1&A2&A3)', 'NAND3_X4' : '!(A1&A2&A3)', 'NOR4_X1' : '!(A1|A2|A3|A4)', 'NOR4_X2' : '!(A1|A2|A3|A4)', 'NOR4_X4' : '!(A1|A2|A3|A4)', 'OAI221_X1' : '!((A&(B1|B2))&(C1|C2))', 'OAI221_X2' :  '!((A&(B1|B2))&(C1|C2))', 'OAI221_X4' :  '!((A&(B1|B2))&(C1|C2))', 'OAI222_X1' : '!((A1|A2) & (B1|B2) & (C1|C2))', 'OAI222_X2' : '!((A1|A2) & (B1|B2) & (C1|C2))', 'OAI222_X4' : '!((A1|A2) & (B1|B2) & (C1|C2))', 'OAI33_X1' : '!((A1|A2|A3) & (B1|B2|B3))', 'OR3_X1' : '(A1|A2|A3)', 'OR3_X2' : '(A1|A2|A3)', 'OR3_X4' : '(A1|A2|A3)', 'XOR2_X1' : '(A xor B)', 'XOR2_X2' : '(A xor B)'}

		#TODO: DICT2 stores the particular order of the input to be given to the input list of the module instance, same extension has to be done as with DICT1 
		dict2 = {'NOR3_X1' : 'A1,A2,A3', 'NOR3_X2' : 'A1,A2,A3', 'NOR3_X4' : 'A1,A2,A3', 'NOR2_X1' : 'A1,A2', 'NOR2_X2' : '!(A1|A2)', 'NOR2_X4' : '!(A1|A2)', 'MUX2_X1' : 'Ain,Bin,Sin', 'MUX2_X2' : 'Ain,Bin,Sin', 'NAND2_X1' : 'A1,A2', 'NAND2_X2' : 'A1,A2', 'NAND2_X4' : 'A1,A2', 'INV_X1' : 'A', 'INV_X16' : 'A', 'INV_X2' : 'A', 'INV_X32' : 'A', 'INV_X4' : 'A', 'INV_X8' : 'A', 'OAI22_X1' : 'A1,A2,B1,B2', 'OAI22_X2' : 'A1,A2,B1,B2', 'OAI22_X4' : 'A1,A2,B1,B2', 'AOI21_X1' : 'A,B1,B2', 'OAI21_X1' : 'A,B1,B2', 'OAI21_X2' : 'A,B1,B2', 'OAI21_X4' : 'A,B1,B2', 'AOI211_X1' : 'A,B,C1,C2', 'OR2_X1' : 'A1,A2', 'OR2_X2' : 'A1,A2', 'OR2_X4' : 'A1,A2', 'OAI211_X1' : 'A,B,C1,C2', 'OAI211_X2' : 'A,B,C1,C2', 'OAI211_X4' : 'A,B,C1,C2', 'AND3_X1' : 'A1,A2,A3', 'AOI22_X1' : 'A1,A2,B1,B2', 'XNOR2_X1' : 'A1,A2', 'XNOR2_X2' : 'A1,A2', 'NAND4_X1' : 'A1,A2,A3,A4', 'NAND4_X2' : 'A1,A2,A3,A4', 'NAND4_X4' : 'A1,A2,A3,A4', 'AND2_X1' : 'A1,A2', 'AND2_X2' : 'A1,A2', 'AND2_X4' : 'A1,A2', 'AND3_X2' : 'A1,A2,A3', 'AND3_X4' : 'A1,A2,A3', 'AND4_X1' : 'A1,A2,A3,A4', 'AND4_X2' : 'A1,A2,A3,A4', 'AND4_X4' : 'A1,A2,A3,A4', 'AOI211_X2' : 'A,B,C1,C2', 'AOI211_X4' : 'A,B,C1,C2', 'AOI21_X2' : 'A,B1,B2', 'AOI21_X4' : 'A,B1,B2', 'AOI221_X1' : 'A,B1,B2,C1,C2', 'AOI221_X2' : 'A,B1,B2,C1,C2', 'AOI221_X4' : 'A,B1,B2,C1,C2', 'AOI222_X1' : 'A1,A2,B1,B2,C1,C2', 'AOI222_X2' : 'A1,A2,B1,B2,C1,C2', 'AOI222_X4' : 'A1,A2,B1,B2,C1,C2', 'AOI22_X2' : 'A1,A2,B1,B2', 'AOI22_X4' : 'A1,A2,B1,B2', 'BUF_X1' : 'A', 'BUF_X16' : 'A', 'BUF_X2' : 'A', 'BUF_X32' : 'A', 'BUF_X4' : 'A', 'BUF_X8' : 'A', 'CLKBUF_X1' : 'A', 'CLKBUF_X2' : 'A', 'CLKBUF_X3' : 'A', 'LOGIC0_X1' : '', 'LOGIC1_X1' : '', 'NAND3_X1' : 'A1,A2,A3', 'NAND3_X2' : 'A1,A2,A3', 'NAND3_X4' : 'A1,A2,A3', 'NOR4_X1' : 'A1,A2,A3,A4', 'NOR4_X2' : 'A1,A2,A3,A4', 'NOR4_X4' : 'A1,A2,A3,A4', 'OAI221_X1' : 'A,B1,B2,C1,C2', 'OAI221_X2' : 'A,B1,B2,C1,C2', 'OAI221_X4' : 'A,B1,B2,C1,C2', 'OAI222_X1' : 'A1,A2,B1,B2,C1,C2', 'OAI222_X2' : 'A1,A2,B1,B2,C1,C2', 'OAI222_X4' : 'A1,A2,B1,B2,C1,C2', 'OAI33_X1' : 'A1,A2,A3,B1,B2,B3', 'OR3_X1' : 'A1,A2,A3', 'OR3_X2' : 'A1,A2,A3', 'OR3_X4' : 'A1,A2,A3', 'XOR2_X1' : 'A,B', 'XOR2_X2' : 'A,B'}
		for k in self.tot_modules:
			if k in dict1:
				if k not in pri:
					print ("MODULE " + k + "("+dict2[k]+")")
					print("DEFINE")
					print("           OUT :="+dict1[k]+ ";" )
					pri.append(k)
			else:
				if k not in pri:
					#TODO: This has been only implemented for the D_FF till now!. Exten it for the other filp flops by refering to the NangateOpenCellLibrary. 
					print("MODULE "+ k + "(D)")
					print("VAR")
					print("			Q: boolean;")
					print("			QN: boolean;")
					print("ASSIGN")
					print("			init(Q) := FALSE;")
					print("			init(QN) := TRUE;")
					print("			next(Q) := D;")
					print("			next(QN) := !D;")
					pri.append(k)

		# TODO : Works for only one module, the case of module within a module and more than one module has to be implemented, then corresponding to the number of modules present there would the same number of main MODULES and information would be confided within them
		print ("MODULE main")
		
		print ("VAR")
		if self.i_ports != None:
			for i in range(len(self.i_ports)):
				if (self.i_ports[i] != 'clk'):
					print ("	" + self.i_ports[i] + ": " + "boolean;")		
		for i in range(len(self.tot_modules_1)):
			if (self.tot_modules[i]) in dict1:
				print ("	" + self.tot_modules_1[i] + ": " + self.tot_modules[i] + "(" + ", ".join(self.rem_ports[i]) + ");")		
			else: 
				print ("	" + self.tot_modules_1[i] + ": " + self.tot_modules[i] + "(" + self.rem_ports[i][0] + ");" )
		
		print("ASSIGN")
		if self.i_ports != None:
			for i in range(len(self.i_ports)):
				if (self.i_ports[i] != 'clk'):
					print ("	init(" + self.i_ports[i] + ")" + " := TRUE;")
					
		print ("DEFINE")
		for i in range(len(self.tot_modules_1)): 			
				if self.tot_modules[i] in dict1:
					print ("	" + self.output[i] + " := " + self.tot_modules_1[i] + ".OUT;")
				else:	 
					if (self.len_port[i] == 3):
						print("		" + self.output[i] + " := " + self.tot_modules_1[i] + ".Q;")
					elif (self.len_port[i] == 4):
						print ("	" + self.indi_ports[i][3] + " := " + self.tot_modules_1[i] + ".QN;")
						print ("	" + self.indi_ports[i][2] + " := " + self.tot_modules_1[i] + ".Q;")
							
							
															
						

					


		if log or logmod:
			print("_____________________________________________NuSMV Code________________________________________")

		
		
# NOTE: Please do not change or delete the functions that follow from now onwards. One can add the information or something in addition that needs to be passed for extending the code and including more and more Verilog HDL Grammar, but please DO NOT delete or alter any existing information as it can lead to incorrect results which are already obtained and then one might have to reconfigure the some part of the code again   
def toint(string):
	remove_ = ''
	for i in string:
		if i == '_':
			pass
		else:
			remove_ += i
	try:
		return int(remove_)
	except:
		print("invalid number")
		sys.exit()
	

if (len(sys.argv) >= 2):
        input_file = open(sys.argv[1],'r')
else:
        try:
                input_file = open("input.v",'r')
        except:
                print("Error in opening input.v")
                sys.exit(0)

vfile = input_file.read()

for argm in sys.argv:
	if (argm == '--log'):
		log = 1
	else:
		log = 0
	if (argm == '--logmod'):
		logmod = 1
	else:
		logmod = 0

tokens = [
        "unsigned_number",
	"simple_identifier",
	"COMMA_list_of_port_declarations_TOKEN",
	"escaped_identifier",
]

reserved = {
	'module' : 'module_keyword',
	'endmodule' : 'endmodule_keyword',
	'assign' : 'assign_keyword',
	'input' : 'input_keyword',
	'output' : 'output_keyword',
	'wire' : 'wire_keyword',
	'primitive' : 'primitive_keyword', 
	'endprimitive' : 'endprimitive_keyword',
	'table' : 'table_keyword', 
	'endtable' : 'endtable_keyword', 
	'initial' : 'initial_keyword', 
	'always' : 'always_keyword', 
	'case' : 'case_keyword', 
	'endcase' : 'endcase_keyword'
}

tokens += reserved.values()

t_ignore = ' \t\n'
t_unsigned_number =  r"[0-9](_|[0-9])*"  #regular expression begins with 0-9
literals = ['(',')','[',']', '.', ',', '.', '=' , ':', ';']

def t_escaped_identifier(t):
	r'\\[a-zA-Z0-9_\[\]]+'
	t.type = 'escaped_identifier'
	t.value = 'ESC_' + t.value[1:]
	return t

def t_RESERVED_KEYWORDS(t):
	r'[a-zA-Z_][a-zA-Z0-9_$]*'
	#regular expression begins with a-z A-Z or _
	if t.value in reserved:
		t.type = reserved[ t.value ]
	else: 
		t.type = 'simple_identifier'
	return t

def t_COMMA_list_of_port_declarations_TOKEN(t):
	r'\,[\s|\n]*((?=input)|(?=output))'
	return t

#the same as in the lines before is obtained with the next line (in case uncomment):
#t_COMMA_list_of_port_declarations_TOKEN = r'\,[\s|\n]*((?=input)|(?=output))'


def t_error(t):
        print("LEXER ERROR at: " + t.value)
        # raise TypeError("Parsing error")


precedence = (
#	('nonassoc', 'simple_identifier', 'escaped_identifier'   ),
#	('nonassoc', '[', ']'),
)

lexer = lex.lex()

def p_source_text(p):
        '''source_text : description 
        | source_text description'''
	if log or logmod:
		print("Parsing success")

def p_description(p):
        "description : module_declaration"

def p_description_01(p):
	"description : udp_declaration"

#NOTE: UDP Declaration starts here!

def p_udp_declaration_01(p):
	'''udp_declaration : primitive_keyword udp_identifier '(' udp_declaration_port_list ')' ';' udp_body endprimitive_keyword '''
	#TODO: One more case of UDP still needs to be included!

def p_udp_identifier(p):
	'''udp_identifier : identifier '''

def p_udp_declaration_port_list(p):
	'''udp_declaration_port_list : udp_output_declaration ',' udp_input_declaration_BNF '''

def p_udp_input_declaration_BNF(p):
	'''udp_input_declaration_BNF : udp_input_declaration '''

def p_udp_input_declaration_BNF_01(p):
	'''udp_input_declaration_BNF : udp_input_declaration ',' udp_input_declaration_BNF '''

def p_udp_input_declaration(p):
	'''udp_input_declaration : input_keyword list_of_port_identifiers '''

def p_udp_output_declaration(p):
	'''udp_output_declaration : output_keyword port_identifier '''

def p_udp_body(p):
	'''udp_body : combinational_body '''

def p_udp_body_01(p):
	'''udp_body : sequential_body '''

def p_combinational_body(p):
	'''combinational_body : table_keyword combinational_entry_BNF endtable_keyword'''

def p_combinational_entry_BNF(p):
	'''combinational_entry_BNF : combinational_entry '''

def p_combinational_entry_BNF_01(p):
	'''combinational_entry_BNF : combinational_entry_BNF combinational_entry '''

def p_combinational_entry(p):
	'''combinational_entry : level_input_list_BNF ':' output_symbol '''

def p_level_input_list_BNF(p):
	'''level_input_list_BNF : level_symbol '''

def p_level_input_symbol_BNF_01(p):
	'''level_input_list_BNF : level_symbol level_input_list_BNF '''

def p_level_symbol(p):
	'''level_symbol : '0' '''

def p_level_symbol_01(p):
	'''level_symbol : '1' '''

def p_level_symbol_02(p):
	'''level_symbol : 'x' '''

def p_level_symbol_03(p):
	'''level_symbol : 'X' '''

def p_level_symbol_04(p):
	'''level_symbol : '?' '''

def p_level_symbol_05(p):
	'''level_symbol : 'b' '''

def p_level_symbol_06(p):
	'''level_symbol : 'B' '''

def p_sequential_body(p):
	'''sequential_body : table_keyword sequential_entry_list_BNF endtable_keyword '''

def p_sequential_entry_list_BNF(p):
	'''sequential_entry_list_BNF : sequential_entry '''

def p_sequential_entry_list_BNF_01(p):
	'''sequential_entry_list_BNF : sequential_entry sequential_entry_list_BNF '''

def p_sequential_entry(p):
	'''sequential_entry : seq_input_list ':' current_state ':' next_state ';' '''

def p_seq_input_list(p):
	'''seq_input_list : level_input_list_BNF '''

def p_current_state(p):
	'''current_state : level_symbol '''

def p_next_state(p):
	'''next_state : output_symbol '''

def p_next_state_01(p):
	'''next_state : '-' '''

def p_seq_input_list_01(p):
	'''seq_input_list : '''
	#TODO: Implement this for edge_input_list!

def p_output_symbol(p):
	'''output_symbol : '0' '''

def p_output_symbol_01(p):
	'''output_symbol : '1' '''

def p_output_symbol_02(p):
	'''output_symbol : 'x' '''

def p_output_symbol_03(p):
	'''output_symbol : 'X' '''

#NOTE: UDP Declaration ends here! and Module Declaration starts here!

def p_module_declaration_01(p):
        '''module_declaration : module_keyword module_identifier list_of_port_declarations ';' module_items_BNF endmodule_keyword'''
	#p[2] is a string
	#p[3] is a list of port objects
	#p[5] is a list of item objects

	moduleobj = module(name=p[2], ports=p[3], items=p[5])
	moduleobj.extract_module_information()
	p[0] = moduleobj
	#returns a module object				
	#if log or logmod:
	moduleobj.printinfo()
	



def p_module_delcaration_02(p):
	'''module_declaration :  module_keyword module_identifier list_of_ports ';' module_items_BNF endmodule_keyword'''

	#TO DO: attention: list_of_ports here is NOT implemented !
	moduleobj = module(name=p[2], ports=p[3], items=p[5])
	moduleobj.extract_module_information()
	p[0] = moduleobj
	#to do: check this
	#if log or logmod:
	#print("Module found: ")
	moduleobj.printinfo()
		
def p_list_of_port_declarations(p):
	'''list_of_port_declarations : '(' list_of_port_declarations_BNF ')' '''
	p[0] = p[2]
	#returns a list of port objects

def p_list_of_port_declarations_BNF(p):
	'''list_of_port_declarations_BNF : port_declaration'''
	#p[1] is a list of port objects
	p[0] = p[1]
	#returns a list of port objects


def p_list_of_port_declarations_BNF02(p):
	'''list_of_port_declarations_BNF : list_of_port_declarations_BNF COMMA_list_of_port_declarations_TOKEN port_declaration '''
	#p[3] is a list of port objects
	#p[1] is a list of port objects
	if p[1] != None:
		p[0] = p[1] + p[3]
	else:
		p[0] = p[3]
	#returns a list of port objects


def p_module_identifier(p):
        "module_identifier : identifier"
	p[0] = p[1]
	#retuns a string
	#if log:        
	#	print("module_identifier found: " + p[1] + "  <===============================")

def p_list_of_ports(p):
        '''list_of_ports : '(' port_list_BNF ')' '''
	p[0] = p[2]
	#returns a list of port objects

def p_port_list(p):
        '''port_list_BNF : port '''
	p[0] = [ p[1] ]
	#retunrs a list of port objects

def p_port_list_02(p):
 	'''port_list_BNF : port_list_BNF ',' port'''
	p[0] = [ p[3] ] + p[1]
	#returns a list of port objects

#in the EBNF grammar for Verilog 2001 see module_item
def p_module_items_BNF_01(p):
        '''module_items_BNF : module_or_generate_item module_items_BNF '''
	if p[1] != None and p[2] != None:
		p[0] = [ p[1] ] + p[2]
	elif p[2] == None:
		p[0] = [ p[1] ]
	#returns a list of item objects

def p_module_or_generate_item_01(p):
	'''module_or_generate_item : module_instantiation '''
	#must return an item object
	p[0] = item(itemtype='MODULEINSTANCE', itemvalue=p[1])

def p_module_or_generate_item_02(p):
	'''module_or_generate_item : module_or_generate_item_declaration'''
	p[0] = p[1]
	#returns an item object

def p_module_or_generate_item_03(p):
	'''module_or_generate_item : initial_construct '''
	#TODO: Implement this in the extraction model!

#NOTE: Initial Construct begins 

def p_initial_construct(p):
	'''initial_construct : initial_keyword statement '''

def p_statement(p):
	'''statement : blocking_assignment '''

def p_statement_01(p):
	'''statement : case_statement '''

def p_case_statement(p):
	'''case_statement : case_keyword '(' expression ')' case_item_BNF endcase_keyword '''

def p_case_item_BNF(p):
	'''case_item_BNF : case_item '''

def p_case_item_BNF_01(p):
	'''case_item_BNF : case_item case_item_BNF '''

def p_case_item(p):
	'''case_item : expression_list_BNF ':' statement_or_null '''

def p_expression_list_BNF(p):
	'''expression_list_BNF : expression '''

def p_expression_list_BNF_01(p):
	'''expression_list_BNF : expression ',' expression_list_BNF '''

def p_statement_or_null(p):
	'''statement_or_null : statement '''
	

def p_blocking_assignment(p):
	'''blocking_assignment : variable_lvalue expression '''
	#TODO: Delay can also be included  

def p_varaible_lvalue(p):
	'''variable_lvalue : hierarchical_variable_identifier '''

def p_hierarchical_variable_identifier(p):
	'''hierarchical_variable_identifier : hierarchical_identifier '''

# NOTE: Initial construct ends and Always Construct begins!

def p_module_or_generate_item_04(p):
	'''module_or_generate_item : always_construct '''

def p_always_construct(p):
	'''always_construct : always_keyword statement '''

# NOTE : Always construct ends and Assign Construct begins 

def p_module_or_generate_item_declaration_01(p):
	'''module_or_generate_item_declaration : net_declaration'''
	#returns an item object with itemtype=LISTOFWIRES and itemvalue a list of wire objects.
	try:
		wirelist = []
		if p[1][0] == 'wire':
			if p[1][2] == (0,0): 
				for i in p[1][1]:
					wirelist += [ wire(name=i, width=(0,0)) ]
				p[0] = item(itemtype='LISTOFWIRES', itemvalue=wirelist)
			else:
				for i in p[1][1]:
					wirelist += [ wire(name=i, width=p[1][2]) ]
				p[0] = item(itemtype='LISTOFWIRES', itemvalue=wirelist)
	except:
		if log:
			print("Error in parsing module_or_generate_item_declaration : net_declaration")
	

def p_net_declaration_01(p):
	'''net_declaration : net_type list_of_net_identifiers ';' '''
	p[0] = (p[1], p[2], (0,0))
	#returns a tuple whose first element is a string ('wire') and the second is a list of strings.


def p_net_declaration_02(p):
	'''net_declaration : net_type range list_of_net_identifiers ';' '''
	p[0] = (p[1], p[3], p[2])
	#returns a list of the wire elements i.e the width and name of each and every wire  
		

def p_net_type_01(p):
	'''net_type : wire_keyword'''
	p[0] = 'wire'
	#retunrs a string ('wire')
	 

def p_list_of_net_identifiers_01(p):
	#TODO: extend this rule if needed !
	'''list_of_net_identifiers : net_identifier ',' list_of_net_identifiers'''
	p[0] =  [ p[1] ] + p[3]
	#retunrs a list of strings

def p_list_of_net_identifiers_02(p):
	'''list_of_net_identifiers : net_identifier'''
	p[0] = [ p[1] ]
	#retunrs a list of strings (containing only one element)

def p_net_identifier_01(p):
	'''net_identifier : identifier'''
	p[0] = p[1]
	#retunrs a string

#NOTE: Assign Construct ends and Module Instantiation begins 

def p_module_instantiation_01(p):
	#TODO: Extend this!!
	'''module_instantiation : module_identifier module_instance ';'  '''
	# p[2] is moduleinstance object
	if p[2] != None:
		p[2].moduletype = p[1]
	p[0] = p[2]
	#returns a moduleinstance object

def p_module_instance_01(p):
	'''module_instance : name_of_instance '(' ')' '''

def p_module_instance_02(p):
	'''module_instance : name_of_instance '(' list_of_port_connections_BNF ')' '''
	p[0] = moduleinstance(name=p[1], ports=p[3])
	#returns a moduleinstance object
	if log:
		try:
			print("module instance " + p[1] + " found")
		except:
			print("module instance found")

def p_list_of_port_connections_BNF(p):
	'''list_of_port_connections_BNF : named_port_connection ',' list_of_port_connections_BNF'''
	p[0] = [ p[1] ] + p[3]
	#returns a list of port objects

def p_list_of_port_connections_BNF_02(p):
	'''list_of_port_connections_BNF : named_port_connection'''
	p[0] = [ p[1] ]
	#returns a list of port objects

def p_named_port_connection_01(p):
	'''named_port_connection : '.' port_identifier '(' expression ')' '''
	p[0] = port(name=p[2], connection=p[4])
	#returns a port object

def p_named_port_connection_02(p):
	'''named_port_connection : '.' port_identifier '(' ')' '''
	p[0] = port(name=p[2], connection=None)

def p_name_of_instance_01(p):
	'''name_of_instance : module_instance_identifier 
	| module_instance_identifier range'''
	p[0] = p[1]
	#returns a string
	#range has to be implemented

def p_module_instance_identifier_01(p):
	'''module_instance_identifier : arrayed_identifier'''
	p[0] = p[1]
	#returns a string

def p_arrayed_identifier_01(p):
	'''arrayed_identifier : simple_arrayed_identifier
	| escaped_arrayed_identifier'''
	p[0] = p[1]
	#returns a string

def p_simple_arrayed_identifier_01(p):
	'''simple_arrayed_identifier : simple_identifier'''
	p[0] = p[1]
	#returns a string

def p_simple_arrayed_identifier_02(p):
	'''simple_arrayed_identifier : simple_identifier range'''

def p_escaped_arrayed_identifier_01(p):
	'''escaped_arrayed_identifier : escaped_identifier'''
	p[0] = p[1]
	#return a string

def p_escaped_arrayed_identifier_02(p):
	'''escaped_arrayed_identifier :  escaped_identifier range'''

#NOTE: Module Instantiation ends and Module Ports begin.


def p_module_items_BNF_02(p):
        '''module_items_BNF : port_declaration ';' module_items_BNF '''
	#p[1] is a list of port objects; p[3] is a list of item objects
	if p[3] != None:
		p[0] = p[3] + [ item(itemtype='LISTOFPORTS',itemvalue=p[1]) ]
	else:
		p[0] =   [ item(itemtype='LISTOFPORTS',itemvalue=p[1]) ]
	#returns a list of item objects

#TODO: Implement delay for the extraction purpose!!

def p_module_items_BNF_03(p):
	'''module_items_BNF : delay3'''
	
def p_delay3_01(p):
	'''delay3 : '#' delay_value '''

def p_delay_value_01(p):
	'''delay_value : parameter_identifier '''

def p_delay_value_02(p):
	'''delay_value : unsigned_number '''

def p_parameter_identifier(p):
	'''parameter_identifier : identifier '''

def p_module_items_BNF_04(p):
        '''module_items_BNF :'''

def p_port_01(p):
        '''port : '.' port_identifier '(' port_expression ')' '''
	#p[2] is a string; p[4] is a port object
	#TO DO: implement this
	#print("Port " + p[2] + " connected to -------------------------> "+ p[4].name )
	p[0] = port(name=p[2], connection=p[4])
	#returns a port object

def p_port_02(p):
	'''port : port_expression '''
	p[0] = p[1]
	#returns a port object
	#if log:
	try:
		print("found port " + p[1].printinfo())
	except:
		pass

def p_port03(p):
	"port :"

def p_port_identifier(p):
        '''port_identifier : identifier'''
	if log:
	        print("Found port identifier " + p[1])
        p[0] = p[1]
	#returns a string

# NOTE: Module Ports identifiers ends and all other general constructs begin from here

def p_identifier_01(p):
        '''identifier : simple_identifier'''
	if log:
	        print("Found identifier : " + p[1])
        p[0] = p[1]
	#returns a simple_identifier string.

def p_identifier_02(p):
	'''identifier : escaped_identifier'''
	p[0] = p[1]
	#returns a string

def p_port_expression(p):
        '''port_expression : port_reference'''
	#p[1] is a port object
        p[0] = p[1]
	#returns a port object

def p_port_reference(p):
        '''port_reference : port_identifier  '''
	#p[1] is a string
        p[0] = port(name=p[1])
	#returns a port object

def p_port_reference_01(p):
	'''port_reference : port_identifier '[' constant_expression ']' '''
	p[0] = port(name=p[1]+'['+str(p[3])+']')
	

def p_port_reference_02(p):
	'''port_reference : port_identifier '[' range ']' '''
	p[0] = port(name=p[1]+'['+str(p[3])+']')
	#TODO: Check this!

def p_module_or_generate_item(p):
        '''module_or_generate_item : continuous_assign'''
	try:
		assignlist = []
		if p[1][0] == 'assign':
			for i in p[1][1]: 
				assignlist += [ assign(name=i[0],value=i[1]) ]
				p[0] = item(itemtype='LISTOFASSIGNS', itemvalue=assignlist)
	except:
		if log:
			print("Error in parsing module_or_generate_item_declaration : assign_declaration")

def p_continuous_Assign(p):
        '''continuous_assign : assign_keyword list_of_net_assignments ';' '''
	p[0] = (p[1],p[2])
	#returns a tuple whose first element is a string('assign') and the second is list of a tuple containing the assignments information	

def p_list_of_net_assignments_01(p):
        '''list_of_net_assignments : net_assignment ''' 
	p[0] = [ p[1] ] 
	#returns a list of the tuple containing the assignments of the particular net_values 
	
def p_list_of_net_assignments_02(p):
	'''list_of_net_assignments : list_of_net_assignments ',' net_assignment '''
	p[0] = [ p[1] ] + p[3] 
	#returns a list of the tuple containing the assignments of the particular net_values 

def p_net_assignment(p):
        '''net_assignment : net_lvalue '=' expression'''
	p[0] = (p[1],p[3])
	#returns a tuple of the expression assigned to the corresponding net value!

def p_net_lvalue_01(p):
        '''net_lvalue : hierarchical_net_identifier '''
	p[0] = p[1]        
	#returns a string

def p_net_lvalue_02(p):
	'''net_lvalue : hierarchical_net_identifier '[' constant_range_expression ']' '''
	#TODO : Implement this

def p_hierarchical_net_identifier(p):
        '''hierarchical_net_identifier : hierarchical_identifier'''
	p[0] = p[1]
	#returns a string

def p_hierarchical_identifier(p):
        '''hierarchical_identifier : simple_hierarchical_identifier'''
	p[0] = p[1]
	#returns a string
	if log:
		print "Found hierarchical_identifier  "
		try:
			print("hierarchical_identifier : " + p[1])
		except:
			pass

def p_simple_hierarchical_identifier(p):
        '''simple_hierarchical_identifier : simple_hierarchical_branch'''
	#returns a string
	p[0] = p[1]
	if log:
		print("Found simple_hierarchical_identifier")

def p_simple_hierarchical_branch_01(p):
        '''simple_hierarchical_branch : simple_identifier '[' unsigned_number ']' '''
	p[0] = p[1] + '[' + str(p[3]) + ']'
	#must return a string
	if log:
		print("Found: simple_hierarchical_branch : simple_identifier [ unsigned_number ]")

def p_simple_hierarchical_branch_02(p):
	'''simple_hierarchical_branch : simple_identifier '.' simple_hierarchical_branch'''
	#must return a string
	if log:
		print ("Found simple_hierarchical_branch **")

def p_simple_hierarchical_branch_03(p):
	'''simple_hierarchical_branch : simple_identifier'''
	p[0] = p[1]
	#retunrs a string

def p_escaped_hierarchical_identifier_01(p):
	'''escaped_hierarchical_identifier : escaped_hierarchical_branch'''
	p[0] = p[1]
	#returns a string

def p_escaped_hierarchical_branch_02(p):
        '''escaped_hierarchical_branch : escaped_identifier '[' unsigned_number ']'  '''
	p[0] = p[1] + '[' + str(p[3]) + ']'
	#returns a string

def p_escaped_hierarchical_branch_03(p):
        '''escaped_hierarchical_branch : escaped_identifier '.' escaped_hierarchical_branch'''
	p[0] = p[1] + '.' + p[3]
	#must return a string

def p_escaped_hierarchical_branch_04(p):
	'''escaped_hierarchical_branch : escaped_identifier'''
	#returns a string
	p[0] = p[1]

def p_port_declaration(p):
        '''port_declaration : input_declaration
        | output_declaration'''
	p[0] = p[1]
	#returns a list of port objects + 

def p_input_declaration_01(p):
        '''input_declaration : input_keyword list_of_port_identifiers'''
	inputs = []
	for port_id in p[2]: #p[2] is a list of strings
		inputs += [  port(name=port_id, porttype='input', width=(0,0)) ]
	p[0] = inputs
	#returns a list of port objects

def p_input_declaration_02(p):
        '''input_declaration : input_keyword range list_of_port_identifiers'''
	#p[3] is a list of strings; p[2] is a tuple of integers 
	inputs = []
	for port_id in p[3]: 
		inputs += [ port(name=port_id, porttype='input', width=p[2])   ]
	p[0] = inputs
	#returns a list of port objects


def p_output_declaration_01(p):
        '''output_declaration : output_keyword list_of_port_identifiers'''
	outputs = []
	for port_id in p[2]:  #p[2] is a list of strings
		outputs += [ port(name=port_id, porttype='output', width=(0,0)) ]
	p[0] = outputs
	#returns a list of port objects	


def p_output_declaration_02(p):
        '''output_declaration : output_keyword range list_of_port_identifiers'''
	#p[2] is a tuple of integers; p[3] is a list of strings
	outputs = []
	for port_id in p[3]:
		outputs += [  port(name=port_id, porttype='output', width=p[2])   ]
	p[0] = outputs
	#returns a list of port objects

def p_list_of_port_identifiers_01(p):
        '''list_of_port_identifiers : port_identifier '''
	p[0] = [ p[1] ]
	#returns a list containing one string (a list of strings)

def p_list_of_port_identifiers_02(p):
	'''list_of_port_identifiers :  port_identifier ',' list_of_port_identifiers '''
	p[0] = [ p[1] ] + p[3]
	#returns a list of strings

	
def p_range(p):
        '''range : '[' msb_constant_expression ':' lsb_constant_expression ']' '''
	p[0] = (p[2],p[4])
	#returns a tuple of integers

def p_msb_constant_expression(p):
        '''msb_constant_expression : constant_expression'''
	p[0] = p[1]
	#returns an integer

def p_lsb_constant_expression(p):
        '''lsb_constant_expression : constant_expression'''
	p[0] = p[1]
	#returns an integer

def p_constant_expression(p):
        '''constant_expression : constant_primary'''
	p[0] = p[1]
	#returns an integer

def p_constant_primary(p):
        '''constant_primary : number'''
	p[0] = p[1]
	#returns an integer
	#Note: if constant_primary is not a number change this.
	
def p_number(p):
        '''number : decimal_number'''
	p[0] = p[1]
	#returns an integer

def p_decimal_number(p):
        '''decimal_number : unsigned_number'''
	p[0] = toint(p[1])
	#returns an integer

def p_constant_range_expression(p):
        '''constant_range_expression : constant_expression'''

def p_expression(p):
        '''expression : primary'''
	p[0] = p[1]
	#returns a string
	if log:
		print "Found expression: primary"

def p_primary(p):
        '''primary : number''' 
	#must return a string
	if log:
		print "Found primary : number" 

def p_primary_02(p):
	'''primary : hierarchical_identifier  '''
	p[0] = p[1]
	#returns a string
	if log:
		print "Found primary : hierarchical_identifier"

def p_primary_03(p):
	'''primary : hierarchical_identifier '[' expression ']'  '''
	p[0] = p[1] + '[' + p[3] + ']'
	#returns a string
	if log:
		try:
			print ("primary : " + p[1] + "[" + p[3] + "]")
		except:
			print ("Found: primary : hierarchical_identifier [ expression ] ")


def p_hierarchical_identifier_02(p):
	'''hierarchical_identifier : escaped_hierarchical_identifier'''
	p[0] = p[1]
	#returns a string


#TODO: extend for other primary grammar rules and check the correctness...

def p_error(p):
       print ("PARSER ERROR: Syntax error at " + p.value)        

yacc.yacc()
#parsing file 
p = yacc.parse(vfile)
