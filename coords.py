# Python Script to Convert Data addresses to GPS coordinates.

import csv
import re
import googlemaps
import pickle
import math

LOC_CONTEXT = ', Chicago, IL'
ADDR_NORM = {}
WORDS_PROB = ['between', 'at', 'near', 'Between']
ADDR_PROB = {}
CORNER_COORDS = {}
TEST_BW = ['University between 64th & 65th', 'Midway Pl. between Greenwood & University']

# Google Maps Client
GMAPS = googlemaps.Client(key='AIzaSyB-Bxo_bscSE1trPFoZRrxpx5KhLzkAbTw')

# Because the free Google Maps API has a limited number of lookups per day,
# we store a pickled dictionary with the GPS coordinates of an address so that
# we can minimize the number of requests to the Google Maps API
#
# Format: {'clean_addr': [(lon, lat), source_addr]  . . .  etc.}
try:
    ADDR_BOOK = pickle.load(open('ADDR_BOOK.p', 'rb'))
except:
    ADDR_BOOK = {}
    pickle.dump(ADDR_BOOK, open('ADDR_BOOK.p', 'wb'))

# Address Book for addresses yet to be donetry:
try:
    ADDR_TBD = pickle.load(open('ADDR_TBD.p', 'rb'))
except:
    ADDR_TBD = {}
    pickle.dump(ADDR_TBD, open('ADDR_TBD.p', 'wb'))
    

def man_add():
    '''
    Manually add the gps coordinates of addresses
    '''
    addr = input('Enter the address:').strip()
    coords = input('Enter GPS coords (lat, lon):').strip()
    coords = coords.split(', ')

    lat, lon = float(coords[0]), float(coords[1])

    ADDR_BOOK[addr] = [(lon, lat), addr]
    print(ADDR_BOOK[addr])

    pickle.dump(ADDR_BOOK, open('ADDR_BOOK.p', 'wb'))
    

def midpoint(coords0, coords1, raw_addr):
    '''
    Source (with slight modification):
    http://code.activestate.com/recipes/577713-midpoint-of-two-gps-points/

    Takes 2 sets of longitude and latitude coordinates and returns the midpoint
    of the two coordinates.

    This function will be used for the following types of address types in the 
    UCPD data:
        'Woodlawn between 62nd and 63rd'
        'Between 1414 E. 39th St. & 1100 E. 57th St.'

    Since typing these address types in raw does not return a valid set of GPS
    coordinates, we will simply find the midpoint of 'Woodlawn and 62nd' and 
    'Woodlawn and 63rd' and utilize that as the set of coordinates.
    '''
    # First attempt raw address Lookup
    stored_coords = ADDR_BOOK.get(raw_addr, False)

    if not stored_coords:
        lon1, lat1 = coords0
        lon2, lat2 = coords1

        #Convert to radians
        lon1 = math.radians(lon1)
        lon2 = math.radians(lon2)
        lat1 = math.radians(lat1)
        lat2 = math.radians(lat2)

        bx = math.cos(lat2) * math.cos(lon2 - lon1)
        by = math.cos(lat2) * math.sin(lon2 - lon1)
        lat3 = math.atan2(math.sin(lat1) + math.sin(lat2), \
               math.sqrt((math.cos(lat1) + bx) * (math.cos(lat1) \
               + bx) + by**2))
        lon3 = lon1 + math.atan2(by, math.cos(lat1) + bx)

        coords = (math.degrees(lon3), math.degrees(lat3))

        # Store paired 
        ADDR_BOOK[raw_addr] = [coords, raw_addr]
        pickle.dump(ADDR_BOOK, open('ADDR_BOOK.p', 'wb'))
    else:
        coords = stored_coords[0]

    return(coords)

def address_lookup(clean_addr, source_addr):
    '''
    This function takes a cleaned address and returns the GPS coordinates.
    '''
    # Check if we already have the GPS coordinates for this address
    stored_coords = ADDR_BOOK.get(clean_addr, False)

    if not stored_coords: # If we have not looked up this address before
        geocode_result = GMAPS.geocode(clean_addr + ', Chicago')

        # Extract lon, lat from appropriate dictionary
        try:
            gps_dict = geocode_result[0]['geometry']['location']
        except:
            print('Problem here probably\n')
            print(geocode_result, clean_addr + '|')
        lon = gps_dict['lng']
        lat = gps_dict['lat']

        # Store coordinates in address book and save to file
        ADDR_BOOK[clean_addr] = [(lon, lat), source_addr]
        pickle.dump(ADDR_BOOK, open('ADDR_BOOK.p', 'wb'))

        return((lon, lat))
    else:
        return(stored_coords[0])


def address_handler(raw_addr, reverse = False):
    '''
    This function should take a raw address string, process it as necessary, and
    then return a set of GPS coordinates to match the address.
    '''
    if 'between' in raw_addr and raw_addr.count('&') <= 1:
        # First we match the streets after the 'between'
        match_bw_streets = re.search(r'between(.*$)', raw_addr) 
        if match_bw_streets:
            streets = match_bw_streets.groups()[0]
            street0, street1 = streets.split('&')
            street0 = street0.strip()
            street1 = street1.strip()

            # Then we go back and catch the street before the 'between'
            match_init_street = re.search(r'.+(?= between)', raw_addr)
            if match_init_street:
                init_street = match_init_street.group()
            else:
                print('No initial street found for {}'.format(raw_addr))

            cross0 = init_street + ' & ' + street0
            cross1 = init_street + ' & ' + street1
     
            coords = midpoint(address_lookup(cross0, raw_addr), address_lookup(cross1, raw_addr), raw_addr)
        else:
            print('No between streets found for {}'.format(raw_addr))
            
    elif raw_addr.startswith('Between') and raw_addr.count('&') <= 1:
        match = re.search(r'Between(.*$)', raw_addr)
        if match:
            streets = match.groups()[0]
            street0, street1 = streets.split('&')
            street0 = street0.strip()
            street1 = street1.strip()
   
            coords = midpoint(address_lookup(street0, raw_addr), address_lookup(street1, raw_addr), raw_addr)
        else:
            print('Could not split {}'.format(raw_addr))

    elif raw_addr.count('&') > 1:
        print('Just do this one by hand lol: {}'.format(raw_addr))
        ADDR_TBD[raw_addr] = ''
        pickle.dump(ADDR_TBD, open('ADDR_TBD.p', 'wb'))
        coords = (0, 0)
    else: # The address doesn't require any special processing.
        raw_addr = raw_addr.strip()
        coords = address_lookup(raw_addr, raw_addr)

    if reverse:
        new_coords = (coords[1], coords[0])
        return(new_coords)
    else:
        return(coords)


def main():
    '''
    '''
    with open('ucpd_daily_incidents_clean.csv', 'r') as f, \
         open('incidents_gps.csv', 'w') as out:

        reader = csv.reader(f)

        fieldnames = []
        for row in reader:
            # Save and write fieldnames of input file to output file.
            if not fieldnames:
                fieldnames = row
                fieldnames += ['LON', 'LAT']
                writer = csv.writer(out)
                writer.writerow(fieldnames)
                continue

            simple_addr = row[1]
            ADDR_NORM[simple_addr] = ADDR_NORM.setdefault(simple_addr, 0) + 1

            lon, lat = address_handler(simple_addr)
            row += [lon, lat]
            writer.writerow(row)        


# Clear ADDR_NORM of all problem addresses and add them to ADDR_PROB
all_addr = list(ADDR_NORM.keys())
for addr in all_addr:
    for word in WORDS_PROB:
        if word in addr:
            ADDR_PROB[addr] = ADDR_NORM.pop(addr)


# Attempt to add normal addresses 
print('Attempting to lookup normal addresses')
for addr in ADDR_NORM:
    address_handler(addr)

# Attempt to add problem addresses
print('Attempting to lookup problem addresses')
for addr in ADDR_PROB:
    address_handler(addr)

