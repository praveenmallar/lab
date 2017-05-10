from Tkinter import *
import threading


class myComp(Frame):
	def __init__(self, parent,listitems=["mango","pineapple"],listheight=4,  **kwargs):
		Frame.__init__(self,parent,kwargs)
		self.listitems=[]
		for item in listitems:
			self.listitems.append(item.lower())
		vcmd=self.register(self.validatetext)
		self.text=StringVar()
		sb=Scrollbar(self,orient=VERTICAL,takefocus=0)
		self.list=Listbox(self,height=listheight,yscrollcommand=sb.set,exportselection=0)
		self.entr = Entry(self,validate="key",validatecommand=(vcmd,'%P'),textvariable=self.text)
		self.entr.pack(side=TOP, fill=X, expand=TRUE)
		sb.pack(side=RIGHT,fill=Y)
		self.list.pack(fill=BOTH, expand=TRUE)
		sb.config(command=self.list.yview)
		self.list.config(yscrollcommand=sb.set)
		self.validatetext("")
		self.entr.bind("<Key>",self.moveselection)
		self.list.bind("<FocusIn>",self.lbfocus)
		self.list.bind("<<ListboxSelect>>",self.listchanged)
		key=Event()
		key.keysym="Up"
		self.moveselection(key)		

	def validatetext(self,text):
		newlist=[]
		text=text.lower()
		for item in self.listitems:
			if text in item:
				newlist.append(item)
		if len(newlist)==0:
			return False
		else:
			self.list.delete(0,END)
			for item in newlist:
				self.list.insert(END,item)
			self.list.selection_set(0)
			self.listchanged()
			return True

	def see(self,index):
		self.list.selection_clear(0)
		self.list.selection_set(index)
		self.listchanged()

	def index(self):
		return self.listitems.index(self.get())
			
	
	def get(self):
		try:
			text= self.list.get(self.list.curselection()).strip()
		except:
			text=""	
		if len(text)>0: return text
		else: return None

	def changeList(self,listitems=[]):
		self.listitems=listitems
		self.validatetext("")
		self.listchanged()

	def focus(self):
		self.entr.focus()
		self.listchanged()
		
	def moveselection(self,key):
		if key.keysym=="Down":
			sel=self.list.curselection()
			if len(sel)>0: sel=sel[0] 
			else : sel=-1
			self.list.selection_clear(sel)
			if sel<self.list.size()-1: sel=sel+1
			self.list.select_set(sel)
			self.list.see(sel)
		if key.keysym=="Up":
			sel=self.list.curselection()
			if len(sel)>0: sel=sel[0] 
			else : sel=0
			self.list.selection_clear(sel)
			if sel>0: sel=sel-1
			self.list.select_set(sel)
			self.list.see(sel)
		self.listchanged()

	def lbfocus(self,event):
		self.list.tk_focusNext().focus()

	def clear(self):
		self.text.set("")
		sel=self.list.curselection()
		self.list.selection_clear(sel)
		self.list.select_set(0)

	def listchanged(self,e=None):
		try:
			self.event.cancel()
		except:
			pass
		self.event=threading.Timer(.5,self.eventgenerate)
		self.event.start()

	def eventgenerate(self):
		self.event_generate("<<listChanged>>")


class myComp2(myComp):
	def __init__(self, parent,listitems=[["mango",1],["pineapple",2]],listheight=4,  **kwargs):
		self.array=[]
		items=[]
		for item in listitems:
			items.append(item[0].lower())
			self.array.append([item[0].strip().lower(),item])
		myComp.__init__(self, parent,items,listheight,**kwargs)

	def changelist(self,listitems):
		items=[]
		self.array=[]
		for item in listitems:
			items.append(item[0].lower())
			self.array.append([item[0].strip().lower(),item])
		myComp.changeList(self,items)


	def get(self):
		try:
			text= self.list.get(self.list.curselection()).strip()
		except:
			text=""	
		if len(text)>0: 
			for item in self.array:
				if text == item[0]:
					return item[1]
		else: return None

	def index(self):
		text=self.get()
		for item in self.array:
			if text[0]==item[0]:
				return self.array.index(item)

class NumEntry(Entry):
	def __init__(self, parent, *arg, **karg):
		Entry.__init__(self,parent,*arg,**karg)
		validate=(self.register(self.validate), '%S', '%P')
		self.configure(validate="key")
		self.configure(validatecommand=validate)

	def validate(self, char, entry_value):
		if entry_value=="": return True		
		try:
			float(entry_value)
			return True
		except ValueError:
			return False

if __name__=="__main__":
	root=Tk()
	a=myComp(root,listitems=["hi","paracet","moxhi","tapes fioe"],listheight=3)	
	a.pack()	
	b=myComp2(root,listitems=[["sdfoi",234],["jdfiod",[23,3232,32]]])
	b.pack()
	c=NumEntry(root)
	c.pack()
	a.focus()
	root.mainloop()	
