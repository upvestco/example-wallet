#!/bin/sh

set -e

if [ -z "$UPVEST_OAUTH_CLIENT_ID" ] || [ -z "$UPVEST_OAUTH_CLIENT_SECRET" ]; then
  echo "
The OAuth ID and Secret for your Upvest application must be set as the environment variables:
    UPVEST_OAUTH_CLIENT_ID
    UPVEST_OAUTH_CLIENT_SECRET
See the README for how to configure this wallet: https://github.com/upvestco/example-wallet/README.md
"
  exit 1
fi


if [ -z "$UPVEST_API_KEY_ID" ] || [ -z "$UPVEST_API_KEY_SECRET" ] || [ -z "$UPVEST_API_KEY_PASSPHRASE" ]; then
  echo "
The credentials for the user and the wallet to use must be set as environment variables:
   UPVEST_API_KEY_ID
   UPVEST_API_KEY_SECRET
   UPVEST_API_KEY_PASSPHRASE
See the README for how to configure this wallet: https://github.com/upvestco/example-wallet/README.md
"
  exit 1
fi

set -x

echo "Migrating database"
python manage.py migrate --no-input > /dev/null

echo "Collecting static files"
python manage.py collectstatic --no-input > /dev/null

gunicorn -c gunicorn.conf wallet.wsgi
