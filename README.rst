Quickstart
==========

::

  $ docker network create readable-api
  $ docker build --tag readable-api .
  $ docker run -d --network readable-api -v $(pwd):/usr/src/app -v $HOME/.aws:/root/.aws -p 8888:80 --name readable-api readable-api
  $ docker run -d --network readable-api --network-alias --name mongo -p 27018:27017 mongo
