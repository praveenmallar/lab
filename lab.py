#!/usr/bin/env python
from Tkinter import *
import bill,patient,inv,report,new,cancel,password
import printer as printbill
import datetime as dt
import shelve
import tkMessageBox as tmb
import connectdb as cdb
from PIL import Image, ImageTk

class Lab():

	def __init__(self):
		self.master=Tk()
		self.master.config(width=600,height=400)
		self.master.title("Mukunda Diagnostics")
		self.addmenus()
		self.addshortcuts()
		f=Frame(self.master)
		bill.Bill(f).pack()
		f.pack()
		self.master.mainloop()

	def addshortcuts(self):
		f=Frame(self.master,bd=1,relief=SUNKEN)
		f.pack()
		image=Image.open("./images/bill.png")
		photo=ImageTk.PhotoImage(image)
		b=Button(f,image=photo,text="bill",compound=BOTTOM,width=100,height=100,command=lambda:bill.Bill())
		b.pack(side=LEFT)
		b.image=photo
		image=Image.open("./images/patient.png")
		photo=ImageTk.PhotoImage(image)
		b=Button(f,image=photo,text="patient",compound=BOTTOM,width=100,height=100,command=lambda:patient.Patient())
		b.pack(side=LEFT)
		b.image=photo
		image=Image.open("./images/inv.png")
		photo=ImageTk.PhotoImage(image)
		b=Button(f,image=photo,text="investigation",compound=BOTTOM,width=100,height=100,command=lambda:inv.Inv())
		b.pack(side=LEFT)
		b.image=photo
		image=Image.open("./images/report.png")
		photo=ImageTk.PhotoImage(image)
		b=Button(f,image=photo,text="report",compound=BOTTOM,width=100,height=100,command=lambda:report.Report())
		b.pack(side=LEFT)
		b.image=photo
		image=Image.open("./images/cancel.png")
		photo=ImageTk.PhotoImage(image)
		b=Button(f,image=photo,text="cancel",compound=BOTTOM,width=100,height=100,command=lambda:cancel.Cancel())
		b.pack(side=LEFT)
		b.image=photo

	def addmenus(self):
		menu=Menu(self.master)
		
		repmenu=Menu(menu,tearoff=0)
		repmenu.add_command(label="Day Report",command=self.dayreport)
		menu.add_cascade(label="Report",menu=repmenu)

		self.debug=BooleanVar()
		self.debug.set(False)
		sh=shelve.open("data.db")
		try:
			noprinter=sh['noprinter']
		except:
			noprinter=False
		self.debug.set(noprinter)

		manmenu=Menu(menu,tearoff=0)
		manmenu.add_command(label="Add Doctor",command=self.adddoc)
		manmenu.add_command(label="Set Printers",command=self.setprinters)
		manmenu.add_checkbutton(label="Debug",command=self.noprinter,variable=self.debug)
		manmenu.add_command(label="Passwords",command=lambda:password.Password())
		manmenu.add_command(label="db params",command=self.set_db_params)
		menu.add_cascade(label="Manage",menu=manmenu)


		self.master.config(menu=menu)

	def dayreport(self):
		if not password.askpass():
			tmb.showerror("Error","wrong password")
			return
		sh=shelve.open("data.db")
		try:
			sale=sh['sale']
		except:
			sale=0
		try:
			lastbill=sh['lastbill']
		except:
			lastbill=0
		try:
			selfi=sh['self']
		except:
			selfi=0
		try:
			ipsale=sh['ipsale']
		except:
			ipsale=0
		try:
			discharge=sh['discharge']
		except:
			discharge=0
		try:
			returnb=sh['return']
		except:
			returnb=0
		try:
			lastprint=sh['lastprint']
		except:
			lastprint=0
		try:
			data=sh['misc']
		except:
			data="\n"

		lines=["Lab Day report"]
		lines.append(dt.date.today().strftime("%d- %b, %Y"))
		lines.append("sale from "+str(lastprint+1)+ " to "+str(lastbill))
		lines.append(" ")
		lines.append("sale : "+str(sale))
		lines.append("ip sale:"+str(ipsale))
		lines.append("diacharge:"+str(discharge))
		lines.append("self sale:"+str(selfi))
		lines.append("bill cancel:"+str(returnb))
		lines.append(data)
		printbill.printinfo(lines)
		sh['sale']=0
		sh['self']=0
		sh['ipsale']=0
		sh['discharge']=0
		sh['return']=0
		sh['lastprint']=lastbill
		sh['misc']="\n"

	def adddoc(self):
		new.adder()

	def setprinters(self):
		printbill.Checkprinters()

	def noprinter(self):
		if not password.askpass("admin"):
			return
		sh=shelve.open("data.db")
		sh['noprinter']=self.debug.get()

	def set_db_params(self):
		if not password.askpass("admin"):
			return
		cdb.DbVariables()
			
if __name__=="__main__":
	Lab()
