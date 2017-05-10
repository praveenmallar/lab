from  Tkinter import *
import shelve
import tkMessageBox

class Password(Frame):
	'''	changes passwords'''
	def __init__(self,master=None):
		if not master:
			master=Toplevel()
		Frame.__init__(self,master)
		self.pack()
		self.admin=IntVar()
		Checkbutton(self,text="Admin password",variable=self.admin).pack(pady=10)
		f=Frame(self)
		f.pack(expand=1,fill=BOTH,padx=10,pady=10)
		self.oldp=StringVar()
		self.newp1=StringVar()
		self.newp2=StringVar()
		Label(f,text="Old password").grid(row=0,column=0, sticky=W)
		Label(f,text="New password").grid(row=1,column=0, sticky=W)
		Label(f,text="Repeat password").grid(row=2,column=0, sticky=W)
		Entry(f,textvariable=self.oldp,show="*").grid(row=0,column=1,padx=10,pady=5)
		Entry(f,textvariable=self.newp1,show="*").grid(row=1,column=1,padx=10,pady=5)
		Entry(f,textvariable=self.newp2,show="*").grid(row=2,column=1,padx=10,pady=5)
		Button(self,text="Change password",command=self.changepass).pack(pady=10)

	def changepass(self):
		sh=shelve.open("data.db")
		if self.newp1.get()!=self.newp2.get():
			tkMessageBox.showerror("password error", "passwords don't match",parent=self.master)
			return
		oldp=self.oldp.get()
		newp=self.newp1.get()
		if self.admin.get()==1:
			role="admin_pass"
		else:
			role="pass"	
		try:
			passw=sh[role]
		except:
			passw=""
		if oldp!=passw:
			tkMessageBox.showerror("wrong password", "old password doesn't match",parent=self.master)
			return
		sh[role]=newp
		tkMessageBox.showinfo("success","password saved",parent=self.master)
def askpass(admin=0):
	'''	func checkpass(admin="admin|user"):
			asks user password and returns True or False
	'''
	c=Checkpass(admin)
	c.top.wait_window()
	return c.value	

def checkpass(passwd,role="user"):
	if role=="admin":
		roler="admin_pass"
	else:
		roler="pass"
	sh=shelve.open("data.db")
	passw=sh[roler]
	if passwd==passw:
		return True
	else:
		return False

class Checkpass:
	def __init__(self,admin=0):
		self.value=False
		self.top=top=Toplevel()
		self.admin=admin
		f=Frame(top)
		f.pack()
		Label(f,text="enter password").pack(padx=20,pady=5)
		self.var=StringVar()
		e=Entry(f,textvariable=self.var,show="*")
		e.pack()
		e.bind("<Return>",self.checkpass)
		b=Button(f,text="ok",command=self.checkpass)
		b.pack(pady=20)
		b.bind("<Return>",self.checkpass)
		f.pack()
		top.grab_set()
		e.focus()
	def checkpass(self,e=None):
		self.value=checkpass(self.var.get(),self.admin)
		self.top.destroy()

if __name__=="__main__":

	t=Tk()
	Button(t,text="check pass",command=lambda:askpass()).pack()
	t.mainloop()
	
