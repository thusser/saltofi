SALT OFI for TOMs
=================

This is an observing facility interface (OFI) for SALT, to be used within a [TOM](https://lco.global/tomtoolkit/).

Quick start
-----------

1. Create a new TOM following the instructions at 
   https://tom-toolkit.readthedocs.io/en/latest/introduction/getting_started.html
   
2. Clone this repository into the TOM's base directors: 

```
git clone https://github.com/thusser/saltofi.git
```

3. In the TOM's settings.py add the app:

```
TOM_FACILITY_CLASSES = [
    [...],
    'saltofi.facility.SaltFacility'
]
```
    
4. And add the SALT OFI's settings to the same file (you can also put username/password in here directly):

```
FACILITIES = {
    [...]
    'SALT': {
        'portal_url': 'http://www.saao.ac.za/wm/webservices/',
        'username': os.environ.get('SALT_USERNAME'),
        'password': os.environ.get('SALT_PASSWORD'),
        'proposal_code': '<some_proposal_code>'
    }
}
```    
    
Adding new templates
--------------------

The XML creation in this OFI is based on templates. See templates/grb.xml and the SaltFacilityGrbForm class in
facility.py as an example on how to build your own template.