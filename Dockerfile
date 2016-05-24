FROM python

RUN pip install twisted-web defusedxml
EXPOSE 12228

ADD . /
ENTRYPOINT ["python", "/entry.py"]
