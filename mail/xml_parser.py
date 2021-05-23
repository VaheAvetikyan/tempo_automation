import os
import csv
import xml.etree.ElementTree as ET

ISO_STD = '{urn:iso:std:iso:20022:tech:xsd:pain.001.001.03}'
directory = "tempo_sepa"
data = []
with open('Sepa.csv', 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        data.append(row[0])

output = open('output.csv', 'a')
writer = csv.writer(output)

for filename in os.listdir(directory):
    filepath = os.path.join(directory, filename)
    with open(filepath, "r") as xml:
        tree = ET.parse(xml)
        root = tree.getroot()
        payment_info = root[0][1]
        tag_id = payment_info[0].text
        if tag_id in data:
            for payment in payment_info.findall(f'{ISO_STD}CdtTrfTxInf'):
                writer.writerow([tag_id,
                                 payment.find(f'{ISO_STD}Amt')[0].text,
                                 payment.find(f'{ISO_STD}Amt')[0].attrib['Ccy'],
                                 payment.find(f'{ISO_STD}RmtInf')[0].text])
