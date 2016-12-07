# Clean the scarped UCPD Data

import csv
import re

INVALID = ['None', 'Campus', 'Unknown', 'Out of Area', 'VOID', 'void', 'Void', 'IN', 'N/A', 'Location', 'Joliet', 'Campus Area', 'UC Campus', '61st to 65th / Cottage Grove to University', 'Various Campus Buildings', 'Quad - Haskell, Harper, Stuart, Wieboldt']


def and_fix(raw_addr):
    '''
    For an address with the form:
    '57th & Ellis & 55th & South Shore Dr.'

    This function replaces the 1st and 3rd '&'s with an 'and' so that an address
    lookup in coords.py can work properly.
    '''
    num_ands = raw_addr.count('&')

    assert num_ands == 3

    lst = raw_addr.split('&')

    assert len(lst) == 4 # Make sure there are 4 items (2 addresses)

    addr0 = lst[0] + 'and' + lst[1]
    addr1 = lst[2] + 'and' + lst[3]

    fixed_addr = '&'.join([addr0, addr1])
    return(fixed_addr)

with open('ucpd_daily_incidents.csv', 'r') as inp, open('ucpd_daily_incidents_clean.csv', 'w') as out:
    reader = csv.reader(inp)

    fieldnames = []
    tot, empty = 0, 0 
    for row in reader:
        tot += 1
        if not fieldnames:
            fieldnames = row
            writer = csv.writer(out)
            writer.writerow(fieldnames)
        
        if len(row) > 1:
            if (row[0].lower() in [':', 'void', 'no incidents reported this date']) or row[1] == '':
                empty += 1
            elif tot != 1: # Don't double write header row
                bad_addr = False

                full_addr = row[1]
                # The full_addr might have something in parantheses giving 
                # additional information. I.e. 5121 S. Kenwood (Grandma's House)
                # We want to remove 'Grandma's House' since the Google Maps API 
                # might get confused with this shit.
                match = re.findall('(\([^\)]*\))', full_addr)
                if match:
                    for not_needed in match:
                        simple_addr = full_addr.replace(not_needed, '')
                        simple_addr.strip()
                else:
                    simple_addr = full_addr.strip()

                row[1] = simple_addr
                
                for word in INVALID:
                    if word in row[1]:
                        empty += 1
                        bad_addr = True
                        # print('Bad address: {}'.format(full_addr))
                        break
                if not bad_addr:
                    row[1] = row[1].replace(' and ', ' & ')
                    row[1] = row[1].replace(' at ', ' & ')
                    row[1] = row[1].replace(' near ', ' & ')
                    row[1] = row[1].replace(' to ', ' & ')
                    row[1] = row[1].replace('51st St.', 'Hyde Park Blvd.')
                    row[1] = row[1].replace('51st', 'Hyde Park Blvd.')

                    if row[1].count('&') == 3:
                        row[1] = and_fix(row[1])
                        # print('\t Changed: {}'.format(row[1]))

                    # Special cases found by hand
                    if row[2] == '41659.01736':
                        print('got the sucka')
                        row[2] = '1/20/14'
                    elif row[2] == '5//29/14 1:20 AM':
                        print('got that otha sucka')
                        row[2] = r'5/29/14 1:20 AM'

                    # Truncate the reporting date to leave out times
                    match_date = re.search('([0-9]{1,2}\\/[0-9]{1,2}\\/[0-9]{1,2})', row[2])
                    if match_date:
                        row[2] = match_date.group()
                    else:
                        print('FUCK {}'.format(row[2]))


                    writer.writerow(row)
        else:
            pass
            # print('Stupid row found\n', row)
        


    # print("{} Empty entries out of {} Total".format(empty, tot))



    
