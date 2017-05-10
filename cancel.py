from Tkinter import *
import connectdb as cdb
import comp
import tkMessageBox
import printer as printbill
import shelve

class Cancel(Frame):
		
	def __init__(self,parent=None,*arg,**karg):
		if not parent:
			parent=Toplevel()
		Frame.__init__(self,parent,*arg,**karg)
		self.pack()
		self.master.title("Cancel Bill")
		f1=Frame(self)  							#search frame		
		f1.pack(side=TOP,padx=15,pady=10,ipadx=20,ipady=10)
		Label(f1,text="Bill Number").pack(side=LEFT)
		self.billno=IntVar()
		self.billno.set("")
		t=comp.NumEntry(f1,textvariable=self.billno)
		t.pack(side=LEFT,padx=5)
		t.bind("<Return>",self.searchbill)
		b=Button(f1,text="Search",command=self.searchbill)
		b.pack(side=LEFT,padx=5)
		b.bind("<Return>",self.searchbill)
		Button(f1,text="<",command=lambda x=-1:self.movebill(x)).pack(side=LEFT)
		Button(f1,text=">",command=lambda x=1:self.movebill(x)).pack(side=LEFT)

		f2=Frame(self)			#bill details
		f2.pack(side=TOP,fill=BOTH,expand=1,padx=10)
		sb=Scrollbar(f2)
		sb.pack(side=RIGHT,fill=Y)
		self.canvas=Canvas(f2,bd=1,relief=SUNKEN,yscrollcommand=sb.set,width=300,height=300)
		self.canvas.pack(fill=BOTH,expand=1)
		sb.config(command=self.canvas.yview)

		f3=Frame(self)
		f3.pack(side=TOP,ipadx=20,ipady=10)
		self.cancelbutton=Button(f3,text="cancel Bill",state=DISABLED,command=self.cancelbill)
		self.cancelbutton.pack(side=LEFT,padx=20,pady=10)
		self.reprintbutton=Button(f3,text="reprint Bill",state=DISABLED,command=self.reprint)
		self.reprintbutton.pack(side=LEFT,padx=20,pady=10)
		self.curbill=0

	def searchbill(self,event=None):
		self.curbill=self.billno.get()
		self.canvas.delete(ALL)
		self.items=[]
		db=cdb.Db().connection()
		cur=db.cursor(cdb.dictcursor)
		sql="select bill.name,  bill.date, bill.amount-bill.discount as total, report.id, report.inv from bill join report on bill.id=report.bill where bill.id=%s;"
		cur.execute(sql,(str(self.curbill)))	
		rows=cur.fetchall()
		if len(rows)==0:
			return -1
		row=rows[0]
		f=Frame(self.canvas)
		Label(f,text=row['name']).pack(side=LEFT,padx=10,pady=10)
		Label(f,text=row['date']).pack(side=LEFT,padx=10,pady=10)
		Label(f,text=row['total']).pack(side=LEFT,padx=10,pady=10)
		self.canvas.create_window(1,1,window=f,anchor=NW)	
		i=1	
		for row in rows:
			f=Frame(self.canvas)
			Label(f,text=row['inv'],width=20).pack(side=LEFT,padx=10,pady=10)
			f.id=row['id']
			self.canvas.create_window(1,1+i*40,window=f,anchor=NW)
			i=i+1
			self.items.append(f)
		self.canvas.update_idletasks()
		self.canvas.config(scrollregion=self.canvas.bbox(ALL))
		self.cancelbutton.config(state=NORMAL)
		self.reprintbutton.config(state=NORMAL)

	def movebill(self,direction):
		billno=self.curbill
		billno+=direction
		self.billno.set(billno)
		if self.searchbill()<0:
			self.curbill=billno
		

	def cancelbill(self):
		if not tkMessageBox.askyesno("confirm Cancel","Are you sure you want to cancel bill "+str(self.curbill),parent=self.master):
			return
		self.billno.set(self.curbill)
		con=cdb.Db().connection()
		cur=con.cursor()
		try:
			ip=False
			if self.isip(self.curbill,cur):	
				ip=True
			sql="delete from report where bill=%s;"
			cur.execute(sql,(self.curbill))
			sql="select amount-discount from bill where id=%s;"
			cur.execute(sql,(self.curbill))
			row=cur.fetchone()
			returnamount=row[0]
			sql="delete from bill where id=%s;"
			cur.execute(sql,(self.curbill))
			con.commit()
			if not ip:
				printout=[]
				printout.extend(printbill.header)
				printout.extend(("","    BILL CANCEL"))
				printout.extend(("Bill no:" + str(self.curbill),"","Refund amount  "+str(returnamount)))
				printbill.printinfo(printout)
				sh=shelve.open("data.db")
				try:
					billreturn=sh['return']
				except:
					billreturn=0
				sh['return']=billreturn+returnamount			
			else:
				tkMessageBox.showinfo("Bill Cancelled","Refund only if bill is not IP",parent=self.master)
			
		except cdb.mdb.Error as e:
			tkMessageBox.showerror("Error "+str(e.args[0]),e.	args[1],parent=self.master)
			con.rollback()
		finally:
			con.close()


	def isip(self,bill,cur):
		sql="select patient.id from patient join credit on patient.id=credit.patientid join bill on credit.billid=bill.id where patient.discharged=0 and bill.id=%s;"
		cur.execute(sql,(bill))
		if cur.rowcount>0:
			return True
		else:
			return False

	def reprint(self):
		self.billno.set(self.curbill)
		con=cdb.Db().connection()
		cur=con.cursor()
		sql="select report.bill as billno, bill.name as patient, doc.name as doc, bill.date as date,bill.amount-bill.discount as total,report.inv as inv, report.rate, patient.name as ipname from bill join report on report.bill=bill.id join doc on bill.doc=doc.id left join  credit on credit.billid=bill.id left join patient on credit.patientid=patient.id where bill.id=%s;"
		cur.execute(sql,(self.billno.get()))
		row=cur.fetchone()
		patient=row[1]+ "   COPY BILL"
		doc=row[2]
		date=row[3]
		total=row[4]
		ip=row[7]
		if ip:
			ip=ip.split("::")[0]
		if total==0:
			selfbill=1
		else:
			selfbill=0
		cur.scroll(0,mode="absolute")
		rows=cur.fetchall()
		items=[]
		for row in rows:
			items.append([row[5],row[6	]])
		printbill.printbill(self.billno.get(),patient,doc,date,total,items,ip,selfbill)
		
		  	
if __name__=="__main__":
	f=Cancel()
	f.pack()
	f.mainloop()




