EC2 Rolegen
===========

How to use it
-------------

On EC2 images that use cloud-init, this can generate "user data scripts" for bootstrapping
systems to use different roles. This allows users to configure the systems without needing
to put themselves through the tedious process of creating custom AMIs (especially in
consideration of micro instances) and allows you to keep your user data scripts in a versioned
repository - if desired - with a simple tool that automates the process of generating the
scripts.

This script will leverage CloudInit's ability to use multi-part MIME files in order to allow
any number of scripts to coexist, and gzips the user data scripts.

A simple idea of using this might be that you want a server, but you don't want to make a custom
AMI and you don't want to manually configure it. You could create a directory hierarchy next to
*genroles.py* like this:

    roles/
      |- example/
           |- install.sh

Now, you could have the following inside of your install.sh file:

    #!/bin/sh
    echo 'Hello, world.' > /root/hello.txt

Now, execute this command - and you will have a final packge called example.gz in the ./dist
directory:

    python genroles.py

How it works
------------

This is pretty simple. All that this script does is look for a directory called 'roles' in
your current working directory. If this directory is not found, then it will be created. It
will then search this directory for any files or directories.

If the script finds a directory, then it creates a new role which is given the same name as
the directory which was found. If it finds a file, then that file is added to a list of files
that should be used for every role. These are called *global files*.

For reach directory, the script collects all global files and all files in that roles directory
and puts them into a gzipped (compression level 9) mime file in the dist directory. These files
can be used as user data for your instance in order to bootstrap it.

**Tada.**

