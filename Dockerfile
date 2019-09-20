FROM python:3.7.4-alpine3.9

RUN apk add --no-cache --virtual build-deps build-base
RUN apk add libffi-dev openssl-dev

RUN adduser --disabled-password --gecos '' --home /wallet wallet

USER wallet
RUN python3 -m venv /wallet/env
RUN /wallet/env/bin/pip install --upgrade pip setuptools

ENV PATH /wallet/env/bin:$PATH

COPY --chown=wallet:wallet requirements /wallet/requirements
RUN pip install -r /wallet/requirements/requirements.txt
RUN rm -r /wallet/requirements && mkdir /wallet/static

USER root
RUN apk del build-deps

USER wallet

ENV UPVEST_USER_AGENT="upvest-wallet/docker"

COPY --chown=wallet:wallet wallet /wallet/app
WORKDIR /wallet/app
COPY --chown=wallet:wallet entrypoint.sh /wallet/entrypoint.sh
CMD ["sh", "/wallet/entrypoint.sh"]
