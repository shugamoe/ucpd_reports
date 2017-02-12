import googlemaps
import webbrowser

gmaps = googlemaps.Client(key = 'AIzaSyBeLUnhOHDWZTH4GPbhny9mcL2TUz_ZOes') 

geocode_result = gmaps.geocode('5111 South Kimbark venue, Chicago, IL')
coordinates = geocode_result[0]['geometry']['location']
lat = coordinates['lat']
lng = coordinates['lng']
center = '{:}, {:}'.format(lat, lng)
markers = ['color:blue|label:H|{:}'.format(center)]

def get_static_google_map(filename_wo_extension, center=center, zoom=16, imgsize=(400, 400), imgformat="jpeg",
maptype="roadmap", markers=markers):
 
#http://maps.google.com/maps/api/staticmap?center=Brooklyn+Bridge,New+York,NY&zoom=14&size=512x512&maptype=
#roadmap&markers=color:blue|label:S|40.702147,-74.015794&sensor=false'''
 
	url2  =  "http://maps.google.com/maps/api/staticmap?" # base URL, append query params, separated by &
 
	# if center and zoom  are not given, the map will show all marker locations
	if center != None:
		url2 += "center=%s&" % center
		#url2 += "center=%s&" % "40.714728, -73.998672"   # latitude and longitude (up to 6-digits)
		#url2 += "center=%s&" % "50011" # could also be a zipcode,
		#url2 += "center=%s&" % "Brooklyn+Bridge,New+York,NY"  # or a search term
	if zoom != None:
		url2 += "zoom=%i&" % zoom  # zoom 0 (all of the world scale ) to 22 (single buildings scale)
 
	url2 += "size=%ix%i&" % (imgsize)  # tuple of ints, up to 640 by 640
	url2 += "format=%s&" % imgformat
	url2 += "maptype=%s&" % maptype  # roadmap, satellite, hybrid, terrain
 
	# add markers (location and style)
	if markers != None:
		for marker in markers:
			url2 += "markers=%s&" % marker
 
	#url2 += "mobile=false&"  # optional: mobile=true will assume the image is shown on a small screen (mobile device)
	url2 += "sensor=false&"   # must be given, deals with getting loction from mobile device
	webbrowser.open(url2)

