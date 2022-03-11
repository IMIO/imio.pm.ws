#!/usr/bin/make
#
all: run

.PHONY: buildout
buildout:
	virtualenv -p python2 .
	bin/python bin/pip install -r https://raw.githubusercontent.com/IMIO/buildout.pm/master/requirements.txt
	bin/python bin/buildout

.PHONY: run
run:
	if ! test -f bin/instance1;then make buildout;fi
	bin/instance1 fg

.PHONY: cleanall
cleanall:
	rm -fr bin include lib local share develop-eggs downloads eggs parts .installed.cfg
