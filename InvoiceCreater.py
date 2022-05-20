import PySimpleGUI as gui
import smtplib, ssl
import pandas as pd
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import csv
from Tenant import Tenant

def Main():
	
	#GUI setup
	layout = [  [gui.Text('Profile Name'), gui.InputText('')],
                [gui.Text('Electric Amount'), gui.InputText('0.00')],
				[gui.Text('Month'), gui.InputText('')],
                [gui.Button('Deploy'),gui.Text('',key='-TEXT-')]]
	window = gui.Window('Rental Bill Deployment',layout)
	
	#Action Result
	name_list = []
	while True:
		event, values = window.read()
		if event == gui.WIN_CLOSED:
			break
		if event == 'Deploy':
			profile = FindProfile(values[0])
			if profile == -1:
				print("invalid profile choice")
				continue
			if (profile[0] in name_list):
				window['-TEXT-'].update(f"email already sent to {profile[0]}")
			else:
				tenant = Tenant(profile[0],profile[2],profile[1])
				invoice = CreateInvoice(tenant,values[1])
				Email(invoice,values[2])
				#TODO NAME LIST
				window['-TEXT-'].update(f"email sent successfully to {profile[0]}")
				name_list.append(profile[0])
	window.close()
	
def FindProfile(name):
	results = []
	with open('tenant-data.csv',encoding='utf-8-sig') as file:
		csv_file = csv.reader(file)
		for row in csv_file:
			res_row = list(row)
			if name == res_row[0]:
				return res_row
		return -1 

def Email(invoice_contents,month):
	email_from = 'sender@gmail.com'
	password = 'sender_password'
	email_to = 'receiver@gmail.com'
    
	date_str = pd.Timestamp.today().strftime('%Y-%m-%d')
	email_message = MIMEMultipart()
	email_message['From'] = email_from
	email_message['To'] = email_to
	email_message['Subject'] = f'{date_str} Rent Invoice for {month}'
	
	email_message.attach(MIMEText(invoice_contents, "html"))
	email_string = email_message.as_string()
	context = ssl.create_default_context()

	with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
		server.login(email_from, password)
		server.sendmail(email_from, email_to,email_string)

def CreateInvoice(tenant,electric):
    name = tenant.name
    email = tenant.email
    rent_amount = tenant.rent
    electric_amount = float(electric) / 3
    total = electric_amount + rent_amount

    file = open("invoice.html","w")

    file_contents = f"""
    <html>
	<head>
		<meta http-equiv="Content-type" content="text/html;charset=UTF-8">
	</head>
	<body>
		<h1 id="rental-receipt">Rental Receipt</h1>
		<p><strong>Address</strong>: 7990 Baymeadows Rd E, Unit #213, Jacksonville Fl</p>
		<h2 id="landlord-information">Landlord Information</h2>
		<ul>
			<li>
				Carter Johnston
			</li>
			<li>
				904-409-9944
			</li>
            <li>
				johnston.j.carter@gmail.com
			</li>
		</ul>
		<h2 id="tentant-information">Tentant Information</h2>
		<ul>
			<li>
				{name}
			</li>
			<li>
				{email}
			</li>
		</ul>
		<h2 id="payment-information">Payment Information</h2>
		<table>
			<thead>
				<tr>
					<th>Description</th>
					<th>Amount</th>
				</tr>
			</thead>
			<tbody>
				<tr>
					<td>Rent</td>
					<td>$ {rent_amount:.2f}</td>
				</tr>
				<tr>
					<td>Electric</td>
					<td>$ {electric_amount:.2f}</td>
				</tr>
				<tr>
					<td><strong>Total</strong></td>
					<td><strong>$ {total:.2f} </strong></td>
				</tr>
			</tbody>
		</table>
	</body>
    </html>
    """
    file.write(file_contents)
    file.close()
    return file_contents

if __name__ == "__main__":
    Main()
