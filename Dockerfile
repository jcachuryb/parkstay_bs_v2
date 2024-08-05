# Prepare the base environment.
FROM ubuntu:22.04 as builder_base_parkstay
MAINTAINER asi@dbca.wa.gov.au
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Australia/Perth
ENV PRODUCTION_EMAIL=True
ENV SECRET_KEY="ThisisNotRealKey"

RUN apt-get clean
RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install --no-install-recommends -y wget git libmagic-dev gcc binutils libproj-dev gdal-bin python3 python3-setuptools python3-dev python3-pip tzdata libreoffice cron rsyslog 
RUN apt-get install --no-install-recommends -y libpq-dev patch virtualenv
RUN apt-get install --no-install-recommends -y mtr
RUN apt-get install --no-install-recommends -y sqlite3 vim ssh htop
RUN apt-get install --no-install-recommends -y postgresql-client
RUN apt-get install --no-install-recommends -y nodejs npm
RUN apt-get install --no-install-recommends -y python3-pil
# RUN ln -s /usr/bin/python3 /usr/bin/python 
#RUN ln -s /usr/bin/pip3 /usr/bin/pip
# RUN pip install --upgrade pip
# RUN wget -O /tmp/GDAL-3.8.3-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl https://github.com/girder/large_image_wheels/raw/wheelhouse/GDAL-3.8.3-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl#sha256=e2fe6cfbab02d535bc52c77cdbe1e860304347f16d30a4708dc342a231412c57
# RUN pip install /tmp/GDAL-3.8.3-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl
# Install Python libs from requirements.txt.

RUN groupadd -g 5000 oim 
RUN useradd -g 5000 -u 5000 oim -s /bin/bash -d /app
RUN mkdir /app 
RUN chown -R oim.oim /app 

COPY timezone /etc/timezone
ENV TZ=Australia/Perth
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Health checks for kubernetes 
RUN wget https://raw.githubusercontent.com/dbca-wa/wagov_utils/main/wagov_utils/bin/health_check.sh -O /bin/health_check.sh
RUN chmod 755 /bin/health_check.sh

# scheduler
RUN wget https://raw.githubusercontent.com/dbca-wa/wagov_utils/main/wagov_utils/bin-python/scheduler/scheduler.py -O /bin/scheduler.py
RUN chmod 755 /bin/scheduler.py

# Add azcopy to container
RUN mkdir /tmp/azcopy/
RUN wget https://aka.ms/downloadazcopy-v10-linux -O /tmp/azcopy/azcopy.tar.gz
RUN cd /tmp/azcopy/ ; tar -xzvf azcopy.tar.gz
RUN cp /tmp/azcopy/azcopy_linux_amd64_10.26.0/azcopy /bin/azcopy
RUN chmod 755 /bin/azcopy

RUN rm -rf /var/lib/{apt,dpkg,cache,log}/ /tmp/* /var/tmp/*
FROM builder_base_parkstay as python_libs_parkstay
WORKDIR /app
USER oim
RUN virtualenv /app/venv
ENV PATH=/app/venv/bin:$PATH
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Install the project (ensure that frontend projects have been built prior to this step).
FROM python_libs_parkstay

COPY --chown=oim:oim  python-cron ./
COPY --chown=oim:oim  startup.sh /
RUN chmod 755 /startup.sh
COPY --chown=oim:oim  gunicorn.ini manage.py ./
COPY .git ./.git
RUN touch /app/.env
COPY --chown=oim:oim  parkstay ./parkstay
RUN mkdir -p /app/parkstay/cache/
RUN chmod 777 /app/parkstay/cache/
RUN python manage.py collectstatic --noinput





EXPOSE 8080
HEALTHCHECK --interval=1m --timeout=5s --start-period=10s --retries=3 CMD ["wget", "-q", "-O", "-", "http://localhost:8080/"]
CMD ["/startup.sh"]
#CMD ["gunicorn", "parkstay.wsgi", "--bind", ":8080", "--config", "gunicorn.ini"]

