FROM qzkc/python2.7:v2

MAINTAINER chenquan@hongsong.club

WORKDIR /opt
COPY requirement.txt \
     hongsong_gitlab_bot_feishu.py \
     WORKDIR/

RUN rm -rf /work

RUN unset APP_BASE_DIR PYTHONPATH \
    pip uninstall awscli flask requests  

RUN pip install -r WORKDIR/requirement.txt

CMD ["/bin/sh","-c","python -u WORKDIR/hongsong_gitlab_bot_feishu.py"]
