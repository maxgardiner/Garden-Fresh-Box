import logging

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
from ast import literal_eval
from gardenfreshbox.lib.base import BaseController, render
from gardenfreshbox.model.cookie import Cookie
from gardenfreshbox.model.sale import Sale
from gardenfreshbox.model.GFBDatabaseController import GFBDatabaseController as DB
import json
import os
from _ast import Delete
import subprocess

log = logging.getLogger(__name__)

class SalesController(BaseController):

	# used for returning success messages
	trueString = "{\"success\":\"true\"}"

	'''
	   This function accepts get and put requests
	'''
	def sales(self):
		db = DB()	

		# for all sales (regardless of host site) send hostSiteName : *
		if (request.method == "GET"):
			if request.params['hostSiteName'] == "*":
				orderList = db.getAllOrders()
				return Sale.toTableMasterOrderList(orderList)
			elif (request.params['hostSiteName'] != "" and request.params['orderID'] == "" ):	
				orderList = db.getAllOrders()
				return Sale.toCashSaleList(orderList, request.params['hostSiteName']);
			else:
				order = db.getOrdersByOrderID(request.params['orderID'])
				return json.dumps(order)
		
		# uses orderID as a key, if it is sent as "" a new order is added
		# updating orders was not implemented 
		elif (request.method == "PUT"):				
			if request.params['orderID'] == "":
# 				if (self.validate_new_order_inputs(request.params)):
				order = Sale(None, request.params['dateCreated'], request.params['dateToDistribute'], request.params['firstName'], request.params['lastName'], request.params['email'], request.params['phoneNumber'], request.params['shouldSendNotifications'], request.params['smallBoxQuantity'],request.params['largeBoxQuantity'], request.params['donations'], request.params['donationReceipt'], request.params['totalPaid'], request.params['hostSitePickupID'],request.params['hostSiteOrderID'],request.params['customerID'])
				success = db.createNewOrderModel(order)
				if success:
					self.send_confirmation_email(request.params['dateCreated'], request.params['dateToDistribute'], request.params['firstName'], request.params['lastName'], request.params['email'], request.params['phoneNumber'], request.params['smallBoxQuantity'],request.params['largeBoxQuantity'], request.params['donations'], request.params['totalPaid'], request.params['hostSitePickupID'],request.params['hostSiteOrderID'])
					return self.trueString
				else:
					return "{\"success\":\"false\",\"message\":\"Failed to enter new order.\"}"
# 				else:
# 					return "{\"success\":\"false\",\"message\":\"Please fix inputs.\"}"
			else:
				if (request.params['smallBoxQuantity'] == "" and request.params['largeBoxQuantity'] == ""):
# 					Delete
					success = db.deleteOrder(request.params['orderID'])
					if success:
						self.send_confirmation_email(request.params['dateCreated'], request.params['dateToDistribute'], request.params['firstName'], request.params['lastName'], request.params['email'], request.params['phoneNumber'], request.params['smallBoxQuantity'],request.params['largeBoxQuantity'], request.params['donations'], request.params['totalPaid'], request.params['hostSitePickupID'],request.params['hostSiteOrderID'])
						return self.trueString
					else:
						return "{\"success\":\"false\",\"message\":\"Failed to enter new order.\"}"
				else:
# 					Edit
					order = Sale(request.params['orderID'], request.params['dateCreated'], request.params['dateToDistribute'], request.params['firstName'], request.params['lastName'], request.params['email'], request.params['phoneNumber'], request.params['shouldSendNotifications'], request.params['smallBoxQuantity'],request.params['largeBoxQuantity'], request.params['donations'], request.params['donationReceipt'], request.params['totalPaid'], request.params['hostSitePickupID'],request.params['hostSiteOrderID'],request.params['customerID'])
					
					success = db.createEditOrderModel(order)
					if success:
						self.send_confirmation_email(request.params['dateCreated'], request.params['dateToDistribute'], request.params['firstName'], request.params['lastName'], request.params['email'], request.params['phoneNumber'], request.params['smallBoxQuantity'],request.params['largeBoxQuantity'], request.params['donations'], request.params['totalPaid'], request.params['hostSitePickupID'],request.params['hostSiteOrderID'])
						return self.trueString
					else:
						return "{\"success\":\"false\",\"message\":\"Failed to enter new order.\"}"

	def send_confirmation_email(self,dateCreated, dateToDistribute, firstName, lastName, email, phoneNumber,smallBoxQuantity,largeBoxQuantity, donations,totalPaid, hostSitePickupID,hostSiteOrderID):
		if (smallBoxQuantity == "" and largeBoxQuantity == ""):
		
			to_send = 'curl -s --user \'api:key-5bc79fc3330ac42bf29e1b2f89bb1209\' \\\
	    https://api.mailgun.net/v2/sandboxf445b5fad6f649ffa60875af1df80dee.mailgun.org/messages \\\
	    -F from=\'Garden Fresh Box <postmaster@sandboxf445b5fad6f649ffa60875af1df80dee.mailgun.org>\' \\\
	    -F to=\'' + firstName +'<' + email +'>\'\\\
	    -F subject=\'Donation by ' + firstName +'\' \\\
	    -F text=\'Thank you ' + firstName +'!\n\nYou just made a donation to the Garden Fresh Box program and we really appreciate it! Please email the sysadmin at admin@gfb.com if you have any questions or concerns about this order Here are some of the details:\n\n \
			Date: ' + dateCreated +'\n \
			' + firstName +' ' + lastName + '\n \
			Donation amount: $' + donations+ '\n \''
		
		else:
			db = DB()
			pickupSiteName = db.getHostSite(hostSitePickupID)['name']
			totalCost = 0
			if (smallBoxQuantity != "" and int(smallBoxQuantity) > 0):
				totalCost += int(smallBoxQuantity) * 15
			if (largeBoxQuantity != "" and int(largeBoxQuantity) > 0):
				totalCost += int(largeBoxQuantity) * 20
				
			if (totalPaid == ""):
				totalPaid = 0
			else:
				totalPaid = int(totalPaid)
			amount_owed = totalCost - totalPaid
			
# 			to_send = 'curl -s --user \'api:key-5bc79fc3330ac42bf29e1b2f89bb1209\' \\\
# 	    https://api.mailgun.net/v2/sandboxf445b5fad6f649ffa60875af1df80dee.mailgun.org/messages \\\
# 	    -F from=\'Garden Fresh Box <postmaster@sandboxf445b5fad6f649ffa60875af1df80dee.mailgun.org>\' \\\
# 	    -F to=\'' + firstName +'<' + email +'>\'\\\
# 	    -F subject=\'Order by ' + firstName +'\' \\\
# 	    -F text=\'Thank you ' + firstName +'! \n\nYou just made a purchase on the Garden Fresh Box program! Thank you for your patronage, please email the sysadmin at admin@gfb.com if you have any questions or concerns about this order. Here are the details of the purchase: \n\n\
# 			Date created: ' + dateCreated +'\n \
# 			Date of distribution: ' + dateToDistribute +'\n \
# 			' + firstName +' ' + lastName + '\n \
# 			Number of small boxes: ' + smallBoxQuantity +'\n \
# 			Number of large boxes: ' + largeBoxQuantity +'\n \
# 			Host site for pickup: ' + pickupSiteName +'\n \
# 			Total: $' + str(totalCost) +'\n \
# 			Amount Paid: $' + str(totalPaid) +'\n \
# 			Amount Owed: $' + str(amount_owed) +'\''
# 		os.system(to_send)
		return

	def validate_new_order_inputs(self, params):
		isValid = True
		if params['orderID'] != "":
			isValid = False
			
		elif params['dateToDistribute'] == "--Select--":
			isValid = False
		
		elif params['hostSitePickupID'] == "--Select--":
			isValid = False
			
		elif params['smallBoxQuantity'] == 0 and params['largeBoxQuantity'] == 0 and ['params.donations'] == 0:
			isValid = False
			
		elif params['firstName'] == "":
			isValid = False
			
		elif params['lastName'] == "":
			isValid = False
			
		elif params['email'] == "" and params['phoneNumber'] == "":
			isValid = False
			
		elif '@' not in params['email'] or '.' not in params['email']:
			isValid = False

			
		
		return isValid

	'''
	   This method gets all orders to be sent to a given host site
	'''
	def dist(self):
		db = DB()	
		if (request.method == "GET"):
			hostSite = db.getHostSiteByName(request.params['hostSiteName'])
			orderList = db.getAllOrdersByHostSite(hostSite.get('id'), request.params['sortid'])
			return Sale.toDistList(orderList, request.params['hostSiteName']);

	'''
	   This method gets all orders to be sent to a given  user
	'''
	def usersales(self):
		db = DB()	
		if (request.method == "GET"):
			user = db.getUser(request.params['email'])
 			orderList = db.sortOrdersModel(user['id'], request.params['sortid'])
			return  Sale.toUserSaleList(orderList)
	
	
	def completeorder(self):
 	
		return render("/shop/completedOrder.mako");
		
	'''
	   This method gets all donations to be sent to a given  user
	'''
	def userdonations(self):
		db = DB()	
		if (request.method == "GET"):
			user = db.getUser(request.params['email'])
 			orderList = db.getDonationsByUserID(user['id'])
			return  Sale.toUserDonationList(orderList)

	'''
	   This method gets a list of all customers and returns it as a pretty html table
	   A 404 is thrown if the request does not have enough access
	'''
	def customers(self):
		cookie = request.cookies.get("GFB_Cookie")
		if(cookie == None):
			response.status_int = 404
			return
		else:
			creds = Cookie.decryptCookie(cookie)	
			if(creds.get('role') == '2') or (creds.get('role') == '1'):
				db = DB()
				customerList = db.getAllCustomers()
				return Sale.toTableMasterCustomerList(customerList);
			else:
				response.status_int = 404
				return 

	'''
	   This method gets a list of all donors and returns in a pretty html table
	   A 404 is thrown if the request does not have enough access
	'''
	def donors(self):
		cookie = request.cookies.get("GFB_Cookie")
		if(cookie == None):
			response.status_int = 404
			return
		else:
			creds = Cookie.decryptCookie(cookie)
			if (creds.get('role') == '1' or creds.get('role') == '2'):
				db = DB()
				donorList = db.getDonationOrders()			
				return Sale.toTableDonations(donorList);
			else:
				response.status_int = 404
				return

	def datesJSON(self):
		db = DB()
		if (request.method == "GET"):
			return json.dumps(db.getAllPickupDates())

	def samples(self):
		db = DB()	
		if (request.method == "GET"):
			if (request.params['id'] == '*'):
				smallitems, largeitems = db.getSampleBoxItems()
				return Sale.toTableSampleBoxes(smallitems, largeitems, request.params['staticTable']);
			else:
				date = db.getSampleItem(request.params['id'])
				return json.dumps(date)
		elif (request.method == "PUT"):
			#Edit Date
			if (request.params['id'] != '' and request.params['item'] != ''and request.params['is_small_box'] != ''):
				success = db.updateSampleItem(request.params['id'], request.params['item'], request.params['is_small_box'])
				if success:
					return self.trueString
				else:
					return "{\"success\":\"false\",\"message\":\"Failed to enter new order.\"}"
 			elif (request.params['id'] == '' and request.params['item'] != ''and request.params['is_small_box'] != ''):
 				#New Date
 				success = db.addNewSampleItem(request.params['item'], request.params['is_small_box'])
				if success:
					return self.trueString
				else:
					return "{\"success\":\"false\",\"message\":\"Failed to new item.\"}"
			#Delete Date
			else:
				success = db.deleteSampleItem(request.params['id'])
				if success:
					return self.trueString
				else:
					return "{\"success\":\"false\",\"message\":\"Failed to delete item.\"}"
				
	def dates(self):
		db = DB()	
		if (request.method == "GET"):
			if (request.params['dateID'] == '*'):
				dates = db.getAllPickupDates()
				return Sale.toTableDates(dates, request.params['staticTable']);
			else:
				date = db.getDate(request.params['dateID'])
				return json.dumps(date)
		elif (request.method == "PUT"):
			#Edit Date
			if (request.params['dateID'] != '' and request.params['orderDate'] != ''and request.params['pickupDate'] != ''):
				success = db.updateDate(request.params['dateID'], request.params['pickupDate'], request.params['orderDate'])
				if success:
					return self.trueString
				else:
					return "{\"success\":\"false\",\"message\":\"Failed to enter new order.\"}"
 			elif (request.params['dateID'] == '' and request.params['orderDate'] != ''and request.params['pickupDate'] != ''):
 				#New Date
 				success = db.addNewDate(request.params['pickupDate'], request.params['orderDate'])
				if success:
					return self.trueString
				else:
					return "{\"success\":\"false\",\"message\":\"Failed to enter new order.\"}"
			#Delete Date
			else:
				success = db.deleteDate(request.params['dateID'])
				if success:
					return self.trueString
				else:
					return "{\"success\":\"false\",\"message\":\"Failed to enter new order.\"}"