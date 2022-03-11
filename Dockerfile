FROM imiobe/iadelib:dev
WORKDIR /plone
USER root
RUN rm -Rfv !\(eggs\) \
  && rm .*.cfg
COPY --chown=imio buildout.cfg jenkins.cfg versions-base.cfg versions-dev.cfg *.rst Makefile setup.py requirements.txt /plone/
COPY --chown=imio src/ /plone/src/
# important for coveralls
COPY --chown=imio .git/ /plone/.git/
USER imio
ENV PATH="/home/imio/.local/bin:${PATH}"
RUN virtualenv -p python2 . \
# ensure bin/coverage exists and not just un dist-packages
  && bin/pip install --force-reinstall coverage==5.3.1 \
  && bin/pip install -r requirements.txt \
  && pip3 install -U coverage==5.3.1 "coveralls>=3.0.0" \
  && bin/buildout -c jenkins.cfg
WORKDIR /plone
ENTRYPOINT ["/plone/bin/python"]
