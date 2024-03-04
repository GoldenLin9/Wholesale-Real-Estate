mail_address = """C/O KRZESICKI, MICHAEL POA
8169 LARCHWOOD RD
LARGO, FL 33777-3154"""

mail = mail_address.split("\n")
print(mail)
mail_city, mail = mail[1].split(", ")
print(mail_city, mail)