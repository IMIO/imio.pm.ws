FROM imiobe/iadelib:dev
WORKDIR /plone
USER root
RUN rm -Rf *.sh *.cfg* *.txt *.conf Makefile bin include lib local share develop-eggs downloads parts .git var
COPY --chown=imio *.cfg *.rst Makefile setup.py requirements.txt /plone/
COPY --chown=imio src/ /plone/src/
RUN su -c "virtualenv -p python2 ." -s /bin/sh imio \
  && su -c "bin/pip install -U coverage==5.3.1  -r requirements.txt" -s /bin/sh imio \
  && su -c "pip3 install -U coverage==5.3.1 'coveralls>=3.0.0'" -s /bin/sh imio \
  && su -c "bin/buildout -c jenkins.cfg" -s /bin/sh imio
USER imio
ENV PATH="/home/imio/.local/bin:${PATH}"
WORKDIR /plone
ENTRYPOINT ["/plone/bin/python"]
