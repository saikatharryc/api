FROM judge0/api-base:1.3.0 AS production

ENV JUDGE0_HOMEPAGE "https://judge0.com"
LABEL homepage=$JUDGE0_HOMEPAGE

ENV JUDGE0_SOURCE_CODE "https://github.com/judge0/api"
LABEL source_code=$JUDGE0_SOURCE_CODE

ENV JUDGE0_MAINTAINER "Herman Zvonimir Došilović <hermanz.dosilovic@gmail.com>"
LABEL maintainer=$JUDGE0_MAINTAINER

ENV PATH "/usr/local/ruby-2.7.0/bin:/opt/.gem/bin:$PATH"
ENV GEM_HOME "/opt/.gem/"

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      python-pip  \
      python3-pip \
      libpq-dev \
      sudo && \
    rm -rf /var/lib/apt/lists/* && \
    echo "gem: --no-document" > /root/.gemrc && \
    gem install bundler:2.1.4 && \
    npm install -g --unsafe-perm aglio@2.3.0

WORKDIR /usr/src/api

COPY Gemfile* /usr/src/api/
RUN RAILS_ENV=production bundle

COPY . /usr/src/api


RUN /usr/local/python-3.8.1/bin/python3 -m pip install --upgrade pip && \
    /usr/local/python-3.8.1/bin/python3 -m pip install -r ./sql_executors/requirements.txt && \
    pip3 install pandas numpy && \
    pip2 install pandas numpy 

EXPOSE 3000

ENV JUDGE0_VERSION="1.11.0"
LABEL version=$JUDGE0_VERSION
