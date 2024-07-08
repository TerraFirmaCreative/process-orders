orders_response = {
  "data": {
    "orders": {
      "nodes": [
        {
          "name": "#1003",
          "note": None,
          "createdAt": "2024-07-08T19:41:29Z",
          "phone": None,
          "fulfillable": True,
          "requiresShipping": True,
          "lineItems": {
            "nodes": [
              {
                "currentQuantity": 1,
                "image": {
                  "url": "https://cdn.shopify.com/s/files/1/0789/0052/7412/files/7e82aea8-f61d-46ed-8a2e-048c20e3c5b6_V3.png?v=1716767400"
                }
              }
            ]
          },
          "shippingAddress": {
            "address1": "30 Davilak Avenue",
            "address2": None,
            "city": "Hamilton Hill",
            "company": None,
            "country": "Australia",
            "countryCodeV2": "AU",
            "firstName": "Tymoteusz",
            "lastName": "Suszczynski",
            "name": "Tymoteusz Suszczynski",
            "phone": None,
            "province": "Western Australia",
            "provinceCode": "WA",
            "zip": "6163"
          },
          "shippingLine": {
            "code": "Standard"
          }
        }
      ]
    }
  },
  "extensions": {
    "cost": {
      "requestedQueryCost": 299,
      "actualQueryCost": 9,
      "throttleStatus": {
        "maximumAvailable": 2000,
        "currentlyAvailable": 1991,
        "restoreRate": 100
      }
    },
    "search": [
      {
        "path": [
          "orders"
        ],
        "query": "status:Unfulfilled AND financial_status:PAID AND created_at:>=2024-07-07T00:00:00",
        "parsed": {
          "and": [
            {
              "field": "created_at",
              "range_gte": "2024-07-07T00:00:00+08:00"
            },
            {
              "field": "status",
              "match_all": "Unfulfilled"
            },
            {
              "field": "financial_status",
              "match_all": "PAID"
            },
            {
              "field": "00",
              "match_all": "00"
            }
          ]
        },
        "warnings": [
          {
            "field": "00",
            "message": "Invalid search field for this query."
          }
        ]
      }
    ]
  }
}