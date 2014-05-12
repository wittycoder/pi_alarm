#!/usr/bin/bash

kill `ps -ef | grep brownnoise |grep -v grep| awk '{print $2}'`
