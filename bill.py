from Tkinter import *
import comp
import connectdb as cdb
import tkMessageBox as mb
import datetime as dt
import printer as printbill
import patient
import shelve

class Bill(Frame):
	def __init__(self,parent=None):
		if not parent:
			parent=Toplevel()
		Frame.__init__(self,parent)
		self.pack()		
		self.items=[]
		self.patients=patient.getPatients()
		temp=[[" ",None]]
		for pat in self.patients:
			temp.append([pat[1]+" :"+pat[0],pat[2]])
		self.patients=temp
		cur=cdb.Db().connection().cursor()
		sql="select * from doc order by name;"
		cur.execute(sql)
		result=cur.fetchall()
		docs=[]
		for row in result:
			docs.append([row[1],row])
		sql="select * from inv order by name;"
		cur.execute(sql)
		result=cur.fetchall()
		inv=[]
		for row in result:
			inv.append([row[1],row])
	
		f1=Frame(self)
		f1.pack(side=TOP,pady=10)
		myfont=("Times",10,"bold")
		Label(f1,text="Patient",font=myfont).grid(row=0,column=0,padx=4,pady=2)
		self.varpatient=StringVar()
		Entry(f1,textvariable=self.varpatient).grid(row=0,column=1,padx=4,pady=2,sticky=E+W)
		Label(f1,text="Age",font=myfont).grid(row=1,column=0,padx=4,pady=2)
		self.varage=StringVar()
		comp.NumEntry(f1,textvariable=self.varage).grid(row=1,column=1,padx=4,pady=2,sticky=E+W)
		Label(f1,text="Doctor",font=myfont).grid(row=2,column=0,padx=4,pady=2)
		self.doc=comp.myComp2(f1,listitems=docs,listheight=2,width=14)
		self.doc.grid(row=2,column=1,padx=4,pady=2,sticky=E+W)
		Label(f1,text="Add Investigation",font=myfont).grid(row=3,column=0,padx=4,pady=2)
		self.inv=comp.myComp2(f1,listitems=inv)
		self.inv.grid(row=3,column=1,padx=4,pady=2)	
		self.addbut=Button(f1,text="Add",command=self.addinv)
		self.addbut.bind("<Return>",self.addinv)
		self.addbut.grid(row=3,column=2,padx=4,pady=2)
		
		f=Frame(self)		
		f.pack(side=LEFT,fill=X,expand=1,padx=10,pady=10)
		sb=Scrollbar(f)
		sb.pack(side=RIGHT,fill=Y)
		f3=self.canvas=Canvas(f,bd=1,relief=SUNKEN,yscrollcommand=sb.set,width=300,height=300)
		f3.pack(fill=BOTH,expand=1)
		sb.config(command=f3.yview)		

		f4=Frame(self)
		f4.pack(side=TOP,fill=X,expand=1)
		self.selfbill=IntVar()
		Checkbutton(f4,text="Self Bill",variable=self.selfbill,background="cyan",bd=1,relief="sunken").pack(side=TOP,pady=15,fill=BOTH)
		Label(f4,text="IP Patient").pack(side=TOP)
		self.patient=comp.myComp2(f4,self.patients,listheight=6)	
		self.patient.pack(side=TOP)	
		self.total=Label(f4,text="Total:     ")
		self.total.pack(side=TOP,pady=20)
		b=Button(f4,text="Submit\nBill", font=("Times",14,"bold"),padx=10,pady=10,command=self.addbill)
		b.bind("<Return>",self.addbill)		
		b.pack(side=TOP)
		

	def addinv(self,event=None):
		inv=self.inv.get()
		if inv:
			f=Frame(self.canvas,bd=1,relief=RIDGE)
			f.inv=StringVar()
			f.rate=DoubleVar()
			f.id=inv[1][0]
			f.inv.set(inv[1][1])
			f.rate.set(inv[1][2])
			f.templete=inv[1][3]
			Label(f,textvariable=f.inv,width=15).pack(side=LEFT)
			Label(f,textvariable=f.rate,width=6).pack(side=LEFT)
			Button(f,text="remove",command=lambda:self.removeframe(f)).pack(side=LEFT)
			self.items.append(f)
			self.refreshcanvas()
			self.inv.clear()
			self.inv.focus()

	def refreshcanvas(self,event=None):
		self.canvas.delete(ALL)	
		i=0
		total=0
		for f in self.items:
			self.canvas.create_window(1,1+i*32,window=f, anchor=NW)
			i=i+1
			total+=f.rate.get()
		self.canvas.update_idletasks()
		self.canvas.config(scrollregion=self.canvas.bbox(ALL))
		self.total.config(text="Total: "+str(total))

	def removeframe(self,frame):
		self.items.remove(frame)
		self.refreshcanvas()

	def addbill(self):
		cn=cdb.Db().connection()
		cur=cn.cursor()
		patient=self.varpatient.get()
		age=self.varage.get()
		doc=self.doc.get()[1]
		date=dt.date.today()
		IP=None
		ip=None
		selfbill=self.selfbill.get()
		if selfbill==0:
			ip=self.patient.get()
			if ip: 
				if len(patient.strip())==0:
					patient=ip[0].split(" :")[0]
				IP=ip[0].split(" :")[1]
				patientid=ip[1]
		items=[]
		billtotal=0

		try:
			billid=0
			sql="insert into bill(name, age, date, doc,discount) values(%s,%s,%s,%s,0);"
			cur.execute(sql,(patient,age,date.isoformat(),doc[0]))
			billid=cur.lastrowid	
			for item in self.items:
				inv=item.inv.get()
				rate=item.rate.get()
				templete=item.templete
				id=item.id
				sql="insert into report (bill, inv,report,rate) values(%s,%s,%s,%s);"
				cur.execute(sql,(billid,inv,templete,rate))
				billtotal+=rate
				items.append([inv,rate])
			sql="update bill set amount=%s where id=%s;"
			cur.execute(sql,(billtotal,billid))
			if 	selfbill==1:		
				sql="update bill set discount=%s where id=%s;"
				cur.execute(sql,(billtotal,billid))
				selftotal=billtotal
				billtotal=0
			if ip:
				cur.execute("insert into credit (patientid,billid) values(%s,%s);",(patientid,billid))
			cn.commit()
			printbill.printbill(billid,patient,doc[1],date,billtotal,items,IP,selfbill)
			sh=shelve.open("data.db")
			if selfbill==0:
				if not ip:
					token="sale"
				else:
					token="ipsale"
				total=billtotal
			else:
				token="self"
				total=selftotal
			try:
				sale=sh[token]
			except:
				sale=0
			sh[token]=sale+total
			sh['lastbill']=billid
			self.varpatient.set("")
			self.varage.set("")
			self.doc.clear()
			self.items=[]
			self.refreshcanvas()
		except cdb.mdb.Error as e:
			mb.showerror("Error","error %d: %s" %(e.args[0],e.args[1]),parent=self.master)
			cn.rollback()
		finally :
			cn.close()


if __name__=="__main__":
	b=Bill()
	b.mainloop()
