# Ecommerce 
A Microservice-based, E-commerce webapp.

Please read the following [EcommerceDesign Doc](EcommerceDesign.pdf) before proceeding...

## Dependencies ##
Use pip to install some of these dependencies
1. Python3
2. Requests
2. Flask
3. Sqlite3
4. NGINX webserver
5. POSTMAN

## How to launch Miroservice-based, Ecommerce ##
1. Set up the central database by running ecommerce.py
2. Copy over nginx.conf to local ngnix at \nginx-x.x.x\nginx-x.x.x\conf
3. Run NGINX
4. Run AccountService.py
5. Run ProudctService.py
6. Run CartService.py
7. Run OrderService.py
8. Run PaymentService.py

## Using the ecommerce app, from browsing to checkout ##
1. Launch POSTMAN
2. Sequence of events to following for the demo:

    /ecommerce/v1/account/register : form-data: email, password, ... look at API Documentation <- register new account
    
    /ecommerce/v1/account/login :  form-data: email, password <-login to account
    
    /ecommerce/v1/product/ : form-data: name, price, description, category [1..4], image (File), stock <- add new products
    
    /ecommerce/v1/product/query : form-data: query (for api purposes)
    
    /ecommerce/v1/cart/product : form-data: username, password, productId <- do this with as many products
    
    /ecommerce/v1/cart/user : form-data: username, password <- see items in cart
    
    /ecommerce/v1/payment/: form-data: username, password <- payment and checkout process; removes all from cart and into orders
    
    /ecommerce/v1/cart/product/remove <- form-post: raw: {"productId":"x", "userId":"x"} <-remove one item from the cart
    
    /ecommerce/v1/account/logout: none <- logout of account
    
## POSTMAN API Documenation ##
[Ecommerce](https://web.postman.co/collections/5404767-84525ed9-c1c4-4656-a83b-f1187a2a46a0?workspace=a8551fb5-e2e1-4bed-8669-d9be225e49f9)

