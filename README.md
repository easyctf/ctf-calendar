EasyCTF Calendar
======

A CTF calendar. Soon to be kewler than CTFTime ;) Not ready for production yet.

Quick Start
------

To run a development instance, clone the repositor and enter a password into a `MYSQL_ROOT_PASSWORD` file in the repository root. Then run the following commands to start vagrant:

```bash
$ vagrant up
$ vagrant ssh
```

Once you're in the virtual machine, initialize the development server:

```bash
$ cd /vagrant
$ python manage.py runserver
```

Copyright and License
------

Copyright 2016 by the EasyCTF team.
plz no copy
