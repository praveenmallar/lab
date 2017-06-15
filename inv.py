from Tkinter import *
import connectdb as cdb
import tkMessageBox as tmb
import comp 
import shelve

class Inv(Frame):
	def __init__(self,parent=None):
		if not parent:
			parent=Toplevel()
		Frame.__init__(self,parent)
		self.pack()
		b=InvFrame(self)
		a=InvList(self,b)
		b.invlist=a
		a.pack(side=TOP,ipadx=25,ipady=25)
		b.pack(side=TOP,ipadx=25,ipady=25)



class InvList(Frame):
	
	def __init__(self,parent=None,invFrame=None):
		if not parent:
			parent=Toplevel()
		Frame.__init__(self,parent)
		self.invFrame=invFrame
		self.packitems()
	
	def packitems(self):
		try:
			self.f.pack_forget()
		except:
			pass		
		self.f=Frame(self)
		self.f.pack()
		self.list=comp.myComp2(self.f,listheight=5)
		self.list.pack(side=LEFT)
		f=Frame(self.f)
		f.pack(side=LEFT,ipadx=10,ipady=10)
		self.button=Button(f,text="Show",command=self.load)
		self.button.pack()
		self.button.bind("<Return>",self.load)
		self.deleteButton=Button(f,text="Delete",command=self.delete)
		self.deleteButton.pack()
		self.add=Button(f,text="New",command=self.new)
		self.add.pack()
		self.reload()

	def reload(self):
		cur=cdb.Db().connection().cursor()
		sql="select * from inv;"
		cur.execute(sql)
		rows=cur.fetchall()
		temp=[]
		for r in rows:
			temp.append([r[1],r[0]])
		self.list.changelist(temp)		
		
		
	def load(self,e=None):
		id=self.list.get()[1]
		self.invFrame.load(id)
	
	def new(self):
		self.invFrame.load()
	
	def delete(self):
		inv=self.list.get()
		if not tmb.askyesno("Confirm","Delete the investigation "+inv[0]+"?",parent=self.master):
			return
		sql="delete from inv where id =%s"
		con=cdb.Db().connection()
		cur=con.cursor()
		cur.execute(sql,(inv[1]))
		con.commit()
		sh=shelve.open("data.db")
		try:
			data=sh['misc']
		except:
			data="\n"
		data+="deleted investigation "+ str(inv[0])+"\n"
		sh['misc']=data
		self.packitems()

class InvFrame(Frame):
	
	def __init__(self,parent=None,inv=None,*arg,**karg):
		if not parent:
			parent=Toplevel()
		Frame.__init__(self,parent,*arg,**karg)
		self.id=inv
		self.invlist=None
		Label(self,text="Investigation").grid(row=0,column=0)
		self.name=StringVar()
		Entry(self,textvariable=self.name).grid(row=0,column=1,sticky=E+W,padx=10,pady=10)
		Label(self,text="rate").grid(row=1,column=0)
		self.rate=DoubleVar()
		Entry(self,textvariable=self.rate).grid(row=1,column=1,sticky=E+W,padx=10,pady=10)
		Label(self,text="templete").grid(row=2,column=0)
		self.templete=Text(self, width=24, height=8)
		self.templete.grid(row=2,column=1,sticky=E+W,padx=10,pady=10)
		self.save=Button(self,text="save",command=self.save)
		self.save.grid(row=3,column=1,padx=10,pady=10)
		self.save.bind("<Return>",self.save)
		if self.id:
			self.load(self.id)

	def load(self,id=None):
			if not id:
				self.clear()
				self.id=None
				return
			self.id=id
			sql="select * from inv where id=%s"
			cur=cdb.Db().connection().cursor()
			cur.execute(sql,(id,))
			row=cur.fetchone()
			self.name.set(row[1])
			self.rate.set(row[2])
			self.templete.delete("1.0",END)
			self.templete.insert(END,row[3])

	def save(self):
		sh=shelve.open("data.db")
		if self.id:
			id=self.id
			name=self.name.get()
			rate=self.rate.get()
			templete=self.templete.get("1.0","end-1c")
			try:
				cn=cdb.Db().connection()
				cr=cn.cursor()
				sql="update inv set name=%s , rate=%s, templete=%s where id=%s;"
				cr.execute(sql,(name,rate,templete,id))
				cn.commit()
				tmb.showinfo("Done","updated investigation",parent=self.master)
				try:
					data=sh['misc']
				except:
					data="\n"
				data+="updated investigation "+ name+" rate="+str(rate)+"\n"
				sh['misc']=data
			except:
				tmb.showerror("Error","couldn't update database",parent=self.master)
		else:
			if tmb.askyesno("Confirm","Add New Investigation?",parent=self.master):			
				try:
					name=self.name.get()
					rate=self.rate.get()
					templete=self.templete.get("1.0","end-1c")
					cn=cdb.Db().connection()
					cr=cn.cursor()
					sql="insert into inv(name,rate,templete) values(%s,%s,%s);"
					cr.execute(sql,(name,rate,templete))
					cn.commit()
					tmb.showinfo("Done","Added the investigation",parent=self.master)
					self.clear()
					self.invlist.reload()
					try:
						data=sh['misc']
					except:
						data="\n"
					data+="added investigation "+ name+" rate= "+str(rate)+"\n"
					sh['misc']=data
				except Exception,e:
					tmb.showerror("Error -couldn't update database",e,parent=self.master)

	def clear(self):
		self.name.set("")
		self.rate.set("")
		self.templete.delete("1.0",END)

if __name__=="__main__":
	i=Inv()
	i.mainloop()
