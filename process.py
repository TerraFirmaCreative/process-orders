import subprocess
import xml.etree.ElementTree as ET
import requests
import argparse
import shutil
import os
from dotenv import load_dotenv
import boto3
import uuid
import json

load_dotenv()

s3Client = boto3.client(
    's3',
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
)

parser = argparse.ArgumentParser()

parser.add_argument('--input', type=str, default='./batch_in')
parser.add_argument('--output', type=str, default='./batch_out')

def generate_new_order(order_id, urls):
    tree = ET.parse('./xml/new_order.xml')
    root = tree.getroot()
    
    order = root.find('Order')

    order.find('OrderId').text = str(order_id)
    order.find('ShippingMethod').text = 'FC'
    order_info = order.find('OrderInfo')

    order_info.find('FirstName').text = 'Tymoteusz'
    order_info.find('LastName').text = 'Suszczynski'
    order_info.find('Address1').text = '123 Abc Street'
    order_info.find('City').text = 'Perth'
    order_info.find('State').text = 'WA'
    order_info.find('PostalCode').text = '6000'
    order_info.find('CountryCode').text = 'AU'
    order_info.find('PhoneNumber').text = '12369978040'
    order_info.find('OrderDate').text = '01/01/2024 00:00'
  

    cases = order.findall('Cases')

    for url in urls:
        cases.insert(0, ET.Element('Case'))
        case

    for i, case in enumerate(cases):
        case_info = case.find('CaseInfo')
        case_info.find('CaseId').text = f'CASE_{i}'
        case_info.find('CaseType').text = 'yogamat'
        case_info.find('Quantity').text = '1'
        print_image = case_info.find('PrintImage')
        print_image.find('ImageType').text = 'png'
        print_image.find('Url').text = 'https://cdn.shopify.com/s/files/1/0789/0052/7412/files/hj12342794_Pastel_colours._Rain._Mountains._Flat_geometric_shap_202ffe91-f5ce-4309-943d-e4e35f231709.png'
        
    tree.write('./out/new_order_output.xml')
    
    new_order_xml_string = ET.tostring(root)

    return new_order_xml_string

def send_api_request(xml): 
    print(xml)
    res = requests.post(
        'https://api-staging.spokecustom.com/order/submit',
        headers={'Content-Type': 'application/xml'},
        data=xml
    )

    print(res.content)

def batch_upscale(src, dest):
    result = subprocess.run(f'/Applications/Topaz\ Photo\ AI.app/Contents/MacOS/Topaz\ Photo\ AI --cli {src} --output {dest} --format jpg --verbose')
    result.check_returncode()

    for file in os.listdir(src):
        if not os.path.isdir(file):
            print(file)
            shutil.move(os.path.join(src, file), os.path.join('./temp', file))

    for file in os.listdir(dest):
        if not os.path.isdir(file):
            print(file)
            shutil.move(os.path.join(dest, file), os.path.join(src, file))
    
    result = subprocess.run(f'/Applications/Topaz\ Photo\ AI.app/Contents/MacOS/Topaz\ Photo\ AI --cli {src} --output {dest} --format jpg --verbose')
    result.check_returncode()

def upload_images(dest):
    urls = []

    for file in os.listdir(dest):
        filepath = os.path.join(dest, file)
        key = f"{uuid.uuid4()}.jpg"
        s3Client.upload_file(filepath, 'terrafirma-upscaled', key, ExtraArgs={
            'ContentType': 'image/jpeg'
        })
        url = s3Client.generate_presigned_url('get_object', Params={
            'Bucket': 'terrafirma-upscaled',
            'Key': key,
            'ResponseContentType': 'image/jpeg',
            'ResponseContentDisposition': 'inline'
        }, ExpiresIn=604700)
        urls.append(url)

    return urls

def main(args):
    # batch_upscale(args.input, args.output)
    urls = upload_images(args.output)

    with open("./urls.json", "w+") as file:
        json.dump(urls, file)

    # new_order_xml = generate_new_order(uploaded_files)
    # send_api_request()


if __name__ == "__main__":
    main(parser.parse_args())