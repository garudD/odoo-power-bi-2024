Odoo RESTful API(restful)
~~~~~~~~~~~~~~~~~~~~~~~~~

In other to use this module, a basic understating of Odoo RPC interface
is required(though not that neccessary) especially when dealing with
Many2many and One2many relationship. The implementation sits on the
existing Odoo RPC features, data structures and format when creating or
delecting Odoo's records are still applicable. I will be demostrating
the usage using python request library.

Access token request
^^^^^^^^^^^^^^^^^^^^

An access token is required in other to be able to perform any
operations and ths token once generated should alway be send a long side
any subsequents request.

.. code:: python

    import requests

    url = "http://localhost:8069/api/login"

    data = {
      "db":"test_db", 
      "login": "admin", 
      "password": "0000"
    }

    headers = {
        'content-type': "text/plain", 
        }

    response = requests.request("GET", url, data=data, headers=headers)

    print(response.text)

To delete acccess-token
~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    import requests

    url = "http://localhost:8069/api/logout"

    data = {
     
    }

    headers = {
        'content-type': "multipart/form-data", 
        'token': "_63e2db121d0ab33a3ea3ddb933249d9291c67c4f"
        }

    response = requests.request("DELETE", url, data=data, headers=headers)

    print(response.text)

[GET]
~~~~~

.. code:: python

    import requests

    url = "http://localhost:8069/api/sale.order"

    payload = {
       "limit": 2, 
       "fields": "['id', 'partner_id', 'name']", 
       "domain":"[('id', 'in', [10,11,12,13,14])]", 
       "offset":0
      }

    headers = {
        'token': "_63e2db121d0ab33a3ea3ddb933249d9291c67c4f",
        'content-type': "application/json"
        }

    response = requests.request("GET", url, data=payload, headers=headers)

    print(response.text)

[POST]
~~~~~~

\`\`\`python

**POST request**

.. code:: python

    import requests

    url = "http://localhost:8069/api/sale.order"

    headers = {
        'content-type': 'application/x-www-form-urlencoded',
        'charset': 'utf-8',
        'token': '_63e2db121d0ab33a3ea3ddb933249d9291c67c4f'
    }
    data = {
        "partner_id": 26, # many2onefield
        "company_id": 1
    }
    sale_order = requests.post(url=url, data=data, headers=headers)
    print(sale_order.text)

    order_id = json.loads(sale_order.text).get("data")[0].get('id')
    url = "http://localhost:8069/api/sale.order.line"
    data = {
        'price_unit': 4000,
        'product_id': 1,
        'order_id': order_id
    }

    order_line1 = requests.post(url=url, data=data, headers=headers)
    print(order_line1.text)

**PUT Request**

.. code:: python

    import requests

    url = "http://localhost:8069/api/res.partner/15"

    data = {"name":"partner name edited"}
    headers = {
        'content-type': "application/x-www-form-urlencoded",
        'token': "_63e2db121d0ab33a3ea3ddb933249d9291c67c4f"
        }

    response = requests.request("PUT", url, data=data, headers=headers)

    print(response.text)

**DELETE Request**

.. code:: python

    import requests

    url = "http://localhost:8069/api/sale.order/37"

    data = {}
    headers = {
        'content-type': "application/json",
        'token': "_63e2db121d0ab33a3ea3ddb933249d9291c67c4f"
        }

    response = requests.delete(url, data=data, headers=headers)

    print(response.text)


**PATCH Request: used to execute actions(example: validating sale order)**

.. code:: python

    import requests

    url = "http://localhost:8069/api/sale.order/37"

    data = {"_method":"action_confirm"}
    headers = {
        'content-type': "application/x-www-form-urlencoded",
        'token': "_63e2db121d0ab33a3ea3ddb933249d9291c67c4f"
        }

    response = requests.request("PATCH", url, data=data, headers=headers)

    print(response.text)
