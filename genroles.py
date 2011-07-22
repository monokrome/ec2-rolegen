#!/usr/bin/env python

import email.mime.text
import email.mime.multipart
import glob
import os
import gzip

def check_dir(path):

	if not os.path.exists(path):
		print("Directory does not exist. Creating: {0}".format(path))
		os.makedirs(path)

	elif not os.path.isdir(path):
		raise ValueError('{0} must be a directory.'.format(path))

def project_path(identifier):
	return os.path.abspath(os.path.join('.', identifier))

dist_dir = project_path('dist')
roles_dir = project_path('roles')

check_dir(roles_dir)
check_dir(dist_dir)

global_files = []
roles = {}

# Iterate through list of all absolute paths in the files directory
for filename in glob.iglob(os.path.join(roles_dir, '*')):

	if os.path.isdir(filename):
		roles[os.path.basename(filename)] = filename
	else:
		current_file = open(filename, 'r')
		data = current_file.read()

		global_files.append(email.mime.text.MIMEText(data))

# Create a directory to store our file output in
if not os.path.exists(dist_dir):
	os.makedirs(dist_dir)

elif not os.path.isdir(dist_dir):
	raise ValueError('{0} must be a directory.'.format(dist_dir))

# Generate output for each role
for role in roles:

	role_dir = roles[role]
	role_filename = '{0}{1}'.format(role, '.gz')

	role_output = gzip.open(os.path.join(dist_dir, role_filename), 'w')
	
	# Create a multi-part MIME file, which will be used to store
	# all of the related files for this role.
	mime_output = email.mime.multipart.MIMEMultipart()

	# Include all "global" requirements.
	for mime_file in global_files:
		mime_output.attach(mime_file)

	for filename in glob.iglob(os.path.join(role_dir, '*')):
		current_file = open(filename)
		current_mime = email.mime.text.MIMEText(current_file.read())
		current_file.close()

		current_mime._headers = []

		mime_output.attach(current_mime)

	role_output.write(str(mime_output))
	role_output.close()
