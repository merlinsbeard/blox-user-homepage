import os
from slugify import slugify

def get_root_dirs_files():
	'''
	Returns a dict containing the paths of pictures and Pictures Folder,
	Inside the static/uploads/pictures folder.
	'''
	print 'fucker'
	main_path = os.path.dirname(os.path.abspath('__file__'))    
	new_path = main_path + '/static/uploads/Pictures'
	path_subtract = main_path + '/static/'
	dirs_files = {}

	items_per_page = 10
	pages = 0

	for root, dirs, files in os.walk(new_path):
		relative_path = root.replace(path_subtract,"")
		new_key = slugify(relative_path)
		folder_name = relative_path.replace("uploads/Pictures/","")
	if files:
		tm = files[0]
		pages = len(files)/items_per_page
		pages_dict = {}
		if len(files) < items_per_page:
			pages_dict[0] = []
			print 'pages_dict', pages_dict
			for item in files:
				pages_dict[0].append(item)
		else:
			for n in range(pages):
			   pages_dict[n]=[]

			initial_page = 0
			for item in files:
				if len(pages_dict[initial_page]) != items_per_page:
					pages_dict[initial_page].append(item)
				else:
					initial_page += 1
	else:
		#tm = url_for("static",filename="images/tm.jpg")
		tm = False


	dirs_files[new_key] = {
	'relative_path': relative_path,
	'dirs': dirs,
	'files': files,
	'folder_name': folder_name,
	'thumb': tm,
	'files_2': pages_dict,
	}
	print dirs_files

print get_root_dirs_files()
