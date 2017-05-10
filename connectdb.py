import MySQLdb as mdb
import shelve
import MySQLdb.cursors as mdbcur
from Tkinter import *

dictcursor=mdbcur.DictCursor

class Db:
 """connects by default to mysql."""

 def __init__(self):
	self.sh = shelve.open('data.db')
	
 def write_db_variables(self):
	"use, to change the default mysql connection settings"
	sh = shelve.open('data.db')
	sh['host']='localhost'
	sh['db_user']='mukunda'
	sh['db_pass']='gopidr'
	sh['db']='lab'
 
 def connection(self):
 	"""returns connection."""
	db=mdb.connect(self.sh['host'],self.sh['db_user'],self.sh['db_pass'],self.sh['db'])
	return db

class DbVariables(Frame):
	def __init__(self,parent=None):
		if not parent:
			parent=Toplevel()
		self.parent=parent
		Frame.__init__(self,parent)
		self.pack()		
		sh=shelve.open('data.db')
		vars={'host':"",'db_user':"",'db_pass':"",'db':""}
		for k in vars.keys():
			try:
				vars[k]=sh[k]
			except:
				pass
		i=1
		for k in vars.keys():
			Label(self,text=k).grid(row=i,column=0)
			t=vars[k]
			vars[k]=StringVar()
			vars[k].set(t)
			Entry(self,textvariable=vars[k]).grid(row=i,column=1)
			i+=1
		self.hash=vars
		Button(self,text="Save",command=self.save).grid(row=i,column=1)

	def save(self):
		sh=shelve.open('data.db')
		for k in self.hash:
			sh[k]=self.hash[k].get()
		self.parent.destroy()

if __name__=="__main__":
	a=DbVariables()
	a.mainloop()	

