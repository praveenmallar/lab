from Tkinter import *
import connectdb as cdb
import datetime as dt
import tkMessageBox
import printer as printbill
import shelve


class Patient(Frame):
	def __init__(self,parent=None):
		if not parent:
			t=Toplevel()
			parent = t
		Frame.__init__(self,parent)
		b=PatientDetails(self)
		a=PatientList(self,b)
		c=AddPatient(self,a)
		c.pack()
		a.pack()
		b.pack()
		self.pack()		

def getPatients():
	con=cdb.Db().connection()
	cur=con.cursor()
	patients=[]
	cur.execute ("select * from patient where discharged=0 order by name;")
	result = cur.fetchall()
	for row in result:
		name=row[1]
		name=name.split("::")
		patients.append([name[0],name[1],row[0]]) #ip,name,id
	return patients

def addPatient(ip,name):
	tod=dt.date.today()
	datestring=tod.strftime("%y%m%d")
	name=str(ip)+"::"+name+"::"+datestring
	con=cdb.Db().connection()
	cur=con.cursor()
	try:	
		cur.execute("insert into patient (name) values(%s)",[name])
		con.commit()
	except cdb.mdb.Error,e:
		print "error %d : %s" %(e.args[0],e.args[1])
		con.rollback()
	else:
		return cur.lastrowid

def removePatient(id,name,ip):
	output=["Lab Discharge"," "]
	output.extend(["patient discharged: "+name,"IP: "+ip])
	sql="update patient set discharged=1 where id=%s;"
	con=cdb.Db().connection()
	cur=con.cursor()
	cur.execute(sql,(id))
	sql="select bill.id, bill.amount, bill.date from bill join credit on bill.id=credit.billid join patient on patient.id=credit.patientid where patient.id=%s"
	cur.execute(sql,(id))
	result=cur.fetchall()
	billtotal=0
	for row in result:
		output.append(str(row[0])+" - "+str(row[2])+" - "+str(row[1]))
		billtotal=billtotal+float(row[1])
	output.append("total: "+str(billtotal))
	printbill.printinfo(output)
	con.commit()
	sh=shelve.open("data.db")
	try:
		dt=sh['discharge']
	except:
		dt=0
	dt+=billtotal
	sh['discharge']=dt
	
class AddPatient(Frame):
	def __init__(self,parent,patientlist=None,ip="",name=""):
		Frame.__init__(self,parent,padx=10,pady=10,bd=1,relief=SUNKEN)
		self.patientlist=patientlist
		Label(self,text="Add New Patient").pack(side=TOP)
		Label(self,text="IP no:").pack(side=TOP)
		self.ipVar=StringVar()
		self.ipVar.set(ip)
		Entry(self,textvariable=self.ipVar).pack(side=TOP)
		Label(self,text="name:").pack(side=TOP)
		self.nameVar=StringVar()
		self.nameVar.set(name)
		Entry(self,textvariable=self.nameVar).pack(side=TOP)
		self.button=Button(self,text="Add Patient",command=self.addpatient)
		self.button.pack(side=TOP)
		self.button.bind("<Return>",self.addpatient)

	def addpatient(self,e=None):
		ip=self.ipVar.get()
		name=self.nameVar.get()
		if not tkMessageBox.askyesno("Add New Patient?", "Name: "+name+"\nIP:   "+ip,parent=self.master):
			return
		addPatient(ip,name)
		self.ipVar.set("")
		self.nameVar.set("")
		if self.patientlist:
			self.patientlist.packitems()
		

class PatientList(Frame):
	def __init__(self,parent,billsframe=None):
		Frame.__init__(self,parent,bd=1,padx=10,pady=5)
		self.patientdetails=billsframe
		self.label=None
		sb=Scrollbar(self)
		sb.pack(side=RIGHT, fill=Y)
		self.container=Canvas(self,yscrollcommand=sb.set,width=400,height=200,bd=1,relief=SUNKEN)
		self.container.pack(fill=BOTH,expand=1,ipadx=10,ipady=10)
		sb.config(command=self.container.yview)
		self.items=[]
		self.packitems()
	
	def packitems(self):
		self.items=[]
		patients=getPatients()
		for patient in patients:
			f=Frame(self.container,bd=1, pady=1,relief=RIDGE)
			f.ip=StringVar()
			f.name=StringVar()
			f.ip.set(patient[0])
			f.name.set(patient[1])
			f.pid=patient[2]
			Label(f,textvariable=f.ip,width=10).pack(side=LEFT)
			Label(f,textvariable=f.name,width=20).pack(side=LEFT)
			Button(f,text="Discharge",command=lambda f=f:self.discharge(f)).pack(side=LEFT)
			Button(f,text="show Bills",command=lambda f=f: self.patientdetails.showbills(f.pid)).pack(side=LEFT)
			self.items.append(f)
			self.refreshcanvas()
					
	def refreshcanvas(self):
		self.container.delete(ALL)
		i=0
		for item in self.items:
			self.container.create_window(1,1+i*32,window=item, anchor=NW)
			i=i+1
		self.container.update_idletasks()
		self.container.config(scrollregion=self.container.bbox(ALL))
		
	def showlabel(self,text):
		self.label.showlabel(text)

	def discharge(self,frame):
		ip=frame.ip.get()
		name=frame.name.get()
		pid=frame.pid
		if not tkMessageBox.askyesno("Discharge Patient?", "Name: "+name+"\nIP:   "+ip,parent=self.master):
			return
		removePatient(pid,name,ip)
		self.items.remove(frame)
		self.refreshcanvas()
		self.patientdetails.showbills()

class PatientDetails(Frame):
	
	def __init__(self,parent):
		Frame.__init__(self,parent,bd=1,padx=10,pady=5)
		sb=Scrollbar(self)
		sb.pack(side=RIGHT,fill=Y)
		self.container=Canvas(self,yscrollcommand=sb.set,width=400,height=200,bd=1,relief=SUNKEN)
		self.container.pack(fill=BOTH,expand=1,ipadx=10,ipady=10)
		sb.config(command=self.container.yview)


	def showbills(self,id=None):
		self.container.delete(ALL)
		if id is None:
			return
		sql="select bill.id as bill, bill.name as patient, bill.date as date, bill.amount as amount from bill join credit on bill.id=credit.billid join patient on credit.patientid=patient.id where patient.id=%s;"
		cur=cdb.Db().connection().cursor()
		try:
			cur.execute(sql,(id))
		except cdb.mdb.Error as e:
			tkMessageBox.showerror("Error "+str(e.args[0]), e.args[1],parent=self.master)
			return
		result=cur.fetchall()
		i=0
		total=0
		for row in result:
			f=Frame(self.container,relief=RIDGE,bd=1,pady=1)
			Label(f,text=row[0],width=8).pack(side=LEFT)
			Label(f,text=row[1],width=20).pack(side=LEFT)
			Label(f,text=row[2],width=12).pack(side=LEFT)
			Label(f,text=row[3],width=10).pack(side=LEFT)
			self.container.create_window(1,i*32,window=f,anchor=NW)
			i=i+1
			total+=row[3]
		if total>0:		
			label=Label(self.container,text="Total: "+str(total))
			self.container.create_window(1,i*32,window=label,anchor=NW)
		self.container.update_idletasks()
		self.container.config(scrollregion=self.container.bbox(ALL))
	

if __name__=="__main__":

	f=Patient()
	f.mainloop()

