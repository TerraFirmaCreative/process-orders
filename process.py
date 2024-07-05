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
import datetime
from gql import gql, Client
from fixtures.responses import orders_response
from gql.transport.aiohttp import AIOHTTPTransport

load_dotenv()

parser = argparse.ArgumentParser()

parser.add_argument('--input', type=str, default='./batch_in')
parser.add_argument('--output', type=str, default='./batch_out')

s3Client = boto3.client(
    's3',
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
)

adminTransport = AIOHTTPTransport(url=f"https://{os.environ.get('SHOPIFY_STORE_DOMAIN')}/admin/api/2024-07/graphql.json", headers={
    'Content-Type': 'application/json',
    'X-Shopify-Access-Token': os.environ.get('SHOPIFY_ADMIN_ACCESS_TOKEN')
})

adminClient = Client(transport=adminTransport, fetch_schema_from_transport=True)

def fetch_orders():
    # pending_orders = adminClient.execute(gql(
    #     """
    #     query getOrders($query: String) {
    #         orders(query: $query, first: 250) {
    #             nodes {
    #                 name
    #                 note
    #               	createdAt
    #                 phone
    #                 fulfillable
    #                 requiresShipping
    #                 lineItems(first:250) {
    #                   	nodes {
    #                     	currentQuantity
    #                     	image {
    #                      	   url
    #                     	}
    #                     }
    #                 }
    #                 shippingAddress {
    #                     address1
    #                     address2
    #                     city
    #                     company
    #                     country
    #                     countryCodeV2
    #                     firstName
    #                     lastName
    #                     name
    #                     phone
    #                     province
    #                     provinceCode
    #                     zip
    #                 }

    #             }
    #         }
    #     }
    #     """
    # ), variable_values={
    #     "query": "status:Unfulfilled"
    #     # "query": f"status:Unfulfilled AND created_at:>={datetime.datetime.fromisoformat((datetime.date.today() - datetime.timedelta(days=1)).isoformat()).isoformat()}"
    # })

    orders = orders_response.get('data')['orders']['nodes']

    order_dict = {}
    for order in orders:
        order_dict[order['name']] = order

    print(order_dict)
    return order_dict

def new_request(orders: dict):
    tree = tree = ET.parse('./xml/request.xml')
    root = tree.getroot()

    for order_id, order in orders.items():
        order_element = ET.parse('./xml/order_element.xml').getroot()
       
        order_element.find('OrderId').text = order['name']
        order_element.find('ShippingMethod').text = 'FC' # """NEED TO SET UP SHIPPING OPTIONS"""
        order_info = order_element.find('OrderInfo')

        order_info.find('FirstName').text = order['shippingAddress']['firstName']
        order_info.find('LastName').text = order['shippingAddress']['lastName']
        order_info.find('Address1').text = order['shippingAddress']['address1']
        order_info.find('Address2').text = order['shippingAddress']['address2']
        order_info.find('City').text = order['shippingAddress']['city']
        order_info.find('State').text = order['shippingAddress']['province']
        order_info.find('PostalCode').text = order['shippingAddress']['zip']
        order_info.find('CountryCode').text = order['shippingAddress']['countryCodeV2']
        order_info.find('PhoneNumber').text = order['shippingAddress']['phone']
        order_info.find('OrderDate').text = order['createdAt']
        
        cases = order_element.find('Cases')
        for i, line_item in enumerate(order['lineItems']['nodes']):
            cases.append(ET.Element('CaseInfo'))
            case_info = cases.findall('CaseInfo')[-1]

            case_info.append(ET.Element('CaseId'))
            case_info.append(ET.Element('CaseType'))
            case_info.append(ET.Element('Quantity'))
            case_info.append(ET.Element('PrintImage'))
            print_image = case_info.find('PrintImage')
            print_image.append(ET.Element('ImageType'))
            print_image.append(ET.Element('Url'))

            case_info.find('CaseId').text = f"{order['name']}_{i}"
            case_info.find('CaseType').text = "yogamat"
            case_info.find('Quantity').text = str(line_item['currentQuantity'])
            print_image.find('ImageType').text = 'jpeg'
            print_image.find('Url').text = line_item['image']['url']

        root.append(order_element)

    tree.write('./out/new_order_output.xml')

def send_api_request(xml): 
    print(xml)
    res = requests.post(
        'https://api-staging.spokecustom.com/order/submit',
        headers={'Content-Type': 'application/xml'},
        data=xml
    )

    print(res.content)

def batch_upscale(src, dest):
    result = subprocess.run(['"/Applications/Topaz Photo AI.app/Contents/MacOS/Topaz Photo AI"', '--cli', src, '--output', dest, '--format', 'jpeg', '--verbose'])
    result.check_returncode()

    for file in os.listdir(src):
        if not os.path.isdir(file):
            print(file)
            shutil.move(os.path.join(src, file), os.path.join('./temp', file))

    for file in os.listdir(dest):
        if not os.path.isdir(file):
            print(file)
            shutil.move(os.path.join(dest, file), os.path.join(src, file))
    
    result = subprocess.run(['"/Applications/Topaz Photo AI.app/Contents/MacOS/Topaz Photo AI"', '--cli', src, '--output', dest, '--format', 'jpeg', '--verbose'])
    result.check_returncode()

def upload_images(dest, orders):
    for file in os.listdir(dest):
        print("Uploading...", file)

        filepath = os.path.join(dest, file)
        order_id, line_item_number = os.path.splitext(file)[0].split('_')
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
        orders[order_id]['s3_url'] = url

    return orders

def download_batch(orders: dict, input_dir):
    urls = set()

    if len(orders.keys()) > 0:
        for f in os.listdir(input_dir):
            os.remove(os.path.join(input_dir, f))


    for order_id, order in orders.items():
        for i, line_item in enumerate(order['lineItems']['nodes']):
            print(f"Found: {line_item['image']['url']}")
            req = requests.get(line_item['image']['url'])
            with open(os.path.join(input_dir, f"{order_id}_{i}.png"), "wb") as f:
                f.write(req.content)


def main(args):
    order_dict = fetch_orders()
    download_batch(order_dict, args.input)
    # batch_upscale(args.input, args.output)
    order_dict = upload_images(args.output, order_dict)

    with open(f"./processed_{datetime.date.today()}.json", "w+") as file:
        json.dump(order_dict, file, indent=2, sort_keys=True)
    
    spoke_request_xml = new_request(order_dict)
    send_api_request(spoke_request_xml)


if __name__ == "__main__":
    main(parser.parse_args())