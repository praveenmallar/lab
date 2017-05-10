import Tkinter as tk
import connectdb as cdb
from tkMessageBox import askokcancel,showinfo

class addNew(tk.Frame):

	def __init__(self,parent=None,table="doc",field="name",title="Add New"):	
		tk.Frame.__init__(self,parent)		
		tk.Label(self,text=title).pack(side=tk.TOP)
		self.lb=tk.Listbox(self)
		sb=tk.Scrollbar(self,orient=tk.VERTICAL)
		self.lb.config(yscrollcommand=sb.set)
		sb.config(command=self.lb.yview)
		sb.pack(side=tk.RIGHT,fill=tk.Y)
		self.lb.pack(fill=tk.BOTH,expand=1)
		self.tx=tk.StringVar()
		fr=tk.Frame(self)
		self.en=tk.Entry(fr,textvariable=self.tx)
		btn=tk.Button(fr,text="Add",command=self.addnew,default="active")
		btn.bind('<Return>',lambda event:self.addnew())		
		fr.pack(side=tk.BOTTOM)
		self.en.pack(side=tk.LEFT)
		btn.pack()
		self.en.focus()
		self.table=table
		self.field=field
		self.db=cdb.Db().connection()
		self.refreshlist()
		self.pack(padx=10,pady=10)

	def addnew(self):
		cursor=self.db.cursor()
		newentry = self.tx.get()
		if askokcancel("Confirm", "Do you want to insert - {0}".format(newentry),parent=self.master):
			cursor.execute ("select * from "+self.table+" where "+self.field+"='"+newentry+"'")
			if cursor.rowcount==0:		
				cursor.execute("insert into "+self.table+"("+self.field+") values('"+self.tx.get()+"');")
				self.db.commit()
				showinfo("Done",newentry+" inserted!",parent=self.master)
		self.refreshlist()
		self.tx.set("")
		self.en.focus()

	def refreshlist(self):
		cursor = self.db.cursor()
		cursor.execute("select * from "+self.table+" order by "+self.field)
		result = cursor.fetchall()
		self.lb.delete(0,tk.END)
		for row in result:
			self.lb.insert(tk.END,row[1])


class addDoc(addNew):
	def __init__(self, parent=None, table="doc",field="name",title="Add Doctor"):
		addNew.__init__(self,parent,table,field,title)


class adder(tk.Frame):
	def __init__(self,parent=None):
		if not parent:
			t=tk.Toplevel()
			parent=t
		tk.Frame.__init__(self,parent)
		addDoc(self).pack(side="left")
		self.pack()

if __name__==	"__main__":
	t=Toplevel()
	ad=adder(t)
	ad.mainloop()
