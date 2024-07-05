orders_response = {
  "data": {
    "orders": {
      "nodes": [
        {
          "name": "#1001",
          "note": None,
          "createdAt": "2024-05-03T12:08:35Z",
          "phone": None,
          "fulfillable": False,
          "requiresShipping": False,
          "lineItems": {
            "nodes": [
              {
                "currentQuantity": 1,
                "image": {
                  "url": "https://cdn.shopify.com/s/files/1/0789/0052/7412/files/hj12342794_psychadelic20ayahuasca20fractals20symmetry_de23587f-6df2-4ac0-b6fb-0f9a3d36a263.png?v=1712953582"
                }
              }
            ]
          },
          "shippingAddress": False
        },
        {
          "name": "#1002",
          "note": False,
          "createdAt": "2024-05-06T12:54:30Z",
          "phone": None,
          "fulfillable": True,
          "requiresShipping": True,
          "lineItems": {
            "nodes": [
              {
                "currentQuantity": 1,
                "image": {
                  "url": "https://cdn.shopify.com/s/files/1/0789/0052/7412/files/hj12342794_fresh20air_60b960d1-4790-4266-9e1c-4b29c2024c02.png?v=1712953542"
                }
              }
            ]
          },
          "shippingAddress": {
            "address1": "11 Walker Street",
            "address2": None,
            "city": "South Fremantle",
            "company": None,
            "country": "Australia",
            "countryCodeV2": "AU",
            "firstName": "Phillip",
            "lastName": "Jenkins",
            "name": "Phillip Jenkins",
            "phone": None,
            "province": "Western Australia",
            "provinceCode": "WA",
            "zip": "6162"
          }
        }
      ]
    }
  },
  "extensions": {
    "cost": {
      "requestedQueryCost": 288,
      "actualQueryCost": 8,
      "throttleStatus": {
        "maximumAvailable": 2000,
        "currentlyAvailable": 1992,
        "restoreRate": 100
      }
    },
    "search": [
      {
        "path": [
          "orders"
        ],
        "query": "status:Unfulfilled",
        "parsed": {
          "field": "status",
          "match_all": "Unfulfilled"
        }
      }
    ]
  }
}