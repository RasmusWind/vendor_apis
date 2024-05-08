# Vendor API functions
Works with Farnell, Mouser, Digikey and RS-Components

### About RS-Components
RS-Components doesn't have any public APIs.

To get data we use ```curl``` and find data through scraping their site. Luckily they supply all product information in a certain script tag.

## Getting started
Clone repository:
```
git clone https://github.com/RasmusWind/vendor_apis.git
```
CD into project:
```
cd vendor_apis
```
Install requirements:
```
pip install -r requirements.txt
```
Create "api_keys.json" file with this format:
```json
{
  "farnell": "your_farnell_api_key",
  "mouser": "your_mouser_api_key",
  "digikey": {
    "clientid": "your_digikey_client_id",
    "clientsecret": "your digikey_client_secret"
  }
}
```
First time running the digikey api function, a browser window will open to authenticate, this will redirect to the redirect_uri specified for the digikey production application. 

In some cases your browser might flag this as an insecure site, this is because the ssl certificate is invalid. Proceed anyway for the authentication to be complete.

## Getting your api keys
To get api keys for farnell, mouser and digikey, you must register with each of these vendors and be allowed access to their api.
### Farnell 
Go to this link (danish link) and register ```https://dk.farnell.com/search-api```.

Sign up for API access and await access.
### Mouser
Go to this link and register ```https://www.mouser.dk/MyAccount/Create```.

Go to this link ```https://www.mouser.dk/api-search/``` and press the "Sign Up for Search API" button.

Await access.
### Digikey
Go to this link ```https://www.digikey.dk/MyDigiKey/Registration``` and sign up for an account.

Go to this link ```https://developer.digikey.com/``` scroll down and follow the steps.

You'll need to create an organization and an application. The application will have the client id and client secret that you'll need.
