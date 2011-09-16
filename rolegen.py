#!/usr/bin/env python

import email.mime.text
import email.mime.multipart
import glob
import os
import gzip

COMPRESS = False

def check_dir(path):

	if not os.path.exists(path):
		print("Directory does not exist. Creating: {0}".format(path))
		os.makedirs(path)

	elif not os.path.isdir(path):
		raise ValueError('{0} must be a directory.'.format(path))

def fill_vars(template_vars, content):
	for var in template_vars:
		content = content.replace('$[ec2_rolegen_{0}]'.format(var),
		                          template_vars[var])

	return content

def project_path(identifier):
	return os.path.abspath(os.path.join('.', identifier))

dist_dir = project_path('dist')
roles_dir = project_path('roles')

check_dir(roles_dir)
check_dir(dist_dir)

global_files = []
roles = {}

if COMPRESS:
	open_out = gzip.open
	output_suffix = '.gz'
else:
	open_out = open
	output_suffix = '.out'

# Iterate through list of all absolute paths in the files directory
for filename in glob.iglob(os.path.join(roles_dir, '*')):

	# Ignore hidden files.
	if filename[0] == '.':
		continue

	if os.path.isdir(filename):
		roles[os.path.basename(filename)] = filename
	else:
		current_file = open(filename, 'r')
		data = current_file.read()

		global_files.append(data)

# Create a directory to store our file output in
if not os.path.exists(dist_dir):
	os.makedirs(dist_dir)

elif not os.path.isdir(dist_dir):
	raise ValueError('{0} must be a directory.'.format(dist_dir))

# Generate output for each role
for role in roles:

	# Cloud init has limitations (IE, can't have two cloud-config)
	# files in one mime file. So, adding pseudo-templating fixes this.
	role_vars = {
		'rolename': role
	}

	role_dir = roles[role]
	role_filename = '{0}{1}'.format(role, output_suffix)

	role_output = open_out(os.path.join(dist_dir, role_filename), 'w')
	
	# Create a multi-part MIME file, which will be used to store
	# all of the related files for this role.
	mime_output = email.mime.multipart.MIMEMultipart()

	# Include all "global" requirements.
	for file_data in global_files:
		contents = fill_vars(role_vars, file_data)
		mime_output.attach(email.mime.text.MIMEText(contents))

	for filename in glob.iglob(os.path.join(role_dir, '*')):
		current_file = open(filename)
		contents = fill_vars(role_vars, current_file.read())
		current_mime = email.mime.text.MIMEText(contents)
		current_file.close()

		current_mime._headers = []

		mime_output.attach(current_mime)

	role_output.write(str(mime_output))
	role_output.close()
