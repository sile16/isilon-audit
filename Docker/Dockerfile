FROM centos:7
RUN yum -y update && yum clean all

#Install CEPA
ENV LD_LIBRARY_PATH /opt/CEEPack
RUN echo "Red Hat Enterprise Linux Server release 6.7 (Final)" > /etc/redhat-release
ADD emc_cee_RHEL-7.1.0.x86_64.rpm /
RUN yum install -y /emc_cee_RHEL-7.1.0.x86_64.rpm && yum clean all

#CentOS 7 Stuff
#Needed for centos7 init script
RUN yum install -y net-tools python-twisted-web && yum clean all
RUN echo "Red Hat Enterprise Linux Server release 7.1 (Final)" > /etc/redhat-release

#Centos 6 Stuff
#Install Python 3.5
#RUN yum install -y https://centos6.iuscommunity.org/ius-release.rpm && \
#    yum install -y python35u && \
#    yum clean all


EXPOSE 12228
EXPOSE 12229

ADD entry.py /
ADD cepa.py /

CMD [' ']
ENTRYPOINT ["/usr/bin/python", "/entry.py"]
