from Tkinter import *
import connectdb as cdb
import comp
import tkMessageBox as mb
import printer as printbill

class Report(Frame):

	def __init__(self,parent=None,billno=0):
		if not parent:
			parent=Toplevel()
		Frame.__init__(self,parent)
		self.master.title("Report")
		self.pack()
		
		f1=Frame(self)
		f1.pack(side=TOP,fill=X,expand=1)
		Label(f1,text="Bill Number").pack(side=LEFT,padx=5,pady=5)
		Button(f1,text="<",command=lambda x=-1:self.movebill(x)).pack(side=LEFT,padx=2,pady=5)
		self.search=IntVar()
		self.search.set(billno)
		e=comp.NumEntry(f1,textvariable=self.search)
		e.pack(side=LEFT,padx=2,pady=5)
		e.bind("<Return>",self.loadbill)		
		Button(f1,text=">",command=lambda x=1:self.movebill(x)).pack(side=LEFT,padx=2,pady=5)
		Button(f1,text="Search",command=self.loadbill).pack(side=LEFT,padx=5,pady=5)

		f2=Frame(self)
		f2.pack(side=TOP,fill=X,expand=1,padx=20,pady=20)
		self.patient=StringVar()
		self.patient.set("")
		self.age=IntVar()
		self.age.set("")
		self.date=StringVar()
		self.date.set("")
		f2_title=Frame(f2)
		f2_title.pack(side=TOP)
		Label(f2_title,height=2,width=20,textvariable=self.patient).pack(side=LEFT)
		Label(f2_title,height=2,width=5,textvariable=self.age).pack(side=LEFT)
		Label(f2_title,height=2,width=20,textvariable=self.date).pack(side=LEFT)
		sb=Scrollbar(f2)
		sb.pack(side=RIGHT,fill=Y)
		self.canvas=f=Canvas(f2,width=350,height=300,yscrollcommand=sb.set)
		f.pack(fill=BOTH,expand=1)
		sb.config(command=f.yview)
		
		self.f3=Frame(self)
		
		if billno!=0:		
			self.loadbill()

	def loadbill(self,e=None):
		billno=self.search.get()
		if not billno:
			return
		can=self.canvas
		can.delete(ALL)
		db=cdb.Db().connection()
		cur=db.cursor()
		sql="select bill.name as name,age,bill.date  from bill  where bill.id=%s;"
		cur.execute(sql,(billno,))
		if cur.rowcount==0:
			return
		r=cur.fetchone()
		self.patient.set(r[0])
		self.age.set(r[1])
		self.date.set(r[2])
		sql="select report.id, report.inv, report.report from report where report.bill=%s;"
		cur.execute(sql,(billno,))
		if cur.rowcount==0:
			return
		rows=cur.fetchall()
		i=5
		self.items=[]
		for row in rows:
			can.create_text(25,i+30,anchor=NW,text=row[1])
			t=Text(can,width=30,height=5)
			t.id=row[0]
			t.insert(END,row[2])
			can.create_window(100,i,anchor=NW,window=t)
			i+=100
			self.items.append(t)
		can.update_idletasks()
		can.config(scrollregion=can.bbox(ALL))

		self.f3.pack_forget()
		self.f3=Frame(self)
		self.f3.pack(side=TOP,padx=20,pady=20)	
		Button(self.f3,text="Save ",padx=15, pady=3,command=self.save).pack(side=LEFT,padx=20,pady=5)
		Button(self.f3,text="Print",padx=15,pady=3,command=lambda x=1:self.printreport(x)).pack(side=LEFT,padx=20,pady=5)
		Button(self.f3,text="Print2",padx=15,pady=3,command=lambda x=2:self.printreport(x)).pack(side=LEFT,padx=20,pady=5)

	def movebill(self,direction=1):
		self.search.set(self.search.get()+direction)
		self.loadbill()

	
	def save(self):
		if not self.checkbill():
			return False
		db=cdb.Db().connection()
		cur=db.cursor()
		try:
			for t in self.items:
				r=t.get("1.0","end-1c")
				if len(r.strip())==0:
					continue
				id=t.id
				sql="update report set report=%s where id=%s;"
				cur.execute(sql,(r,id))
			db.commit()			 
			mb.showinfo("Saved","Report Saved", parent=self.master)
			return True
		except cdb.mdb.Error as e:
			mb.showerror("error: "+e.args[0], e.args[1])
			return False

	def printreport(self,prinnum):
		if not self.save():
			return False
		reportno=self.search.get()
		db=cdb.Db().connection()
		cur=db.cursor()
		sql="select bill.name as patient, doc.name as doc, bill.date from bill join doc on bill.doc=doc.id where bill.id=%s;"
		cur.execute(sql,[reportno])
		r=cur.fetchone()
		patient=r[0]
		doc=r[1]
		date=r[2]
		sql="select report.report as report, report.inv as inv from report  where report.bill=%s;"
		cur.execute(sql,[reportno])
		rows=cur.fetchall()
		items=[]
		for r in rows:
			if len(r[0])==0:
				continue
			else:
				items.append(r[0])
		if prinnum==1:
		    printbill.printreport(reportno,patient,doc,date,items)
		elif prinnum==2:
		    printbill.printreport2(reportno,patient,doc,date,items)			

	def checkbill(self):
		db=cdb.Db().connection()
		cur=db.cursor()
		billno=self.search.get()
		sql="select report.id from report where report.bill=%s"
		cur.execute(sql,[billno])
		rows=cur.fetchall()
		ids=[]
		for row in rows:
			ids.append(row[0])
		for t in self.items:
			if t.id not in ids:
				mb.showinfo("check bill number","bill number in search box and reports dont match",parent=self.master)
				return False
		return True
		

if __name__=="__main__":
	b=Report()
	b.mainloop()
