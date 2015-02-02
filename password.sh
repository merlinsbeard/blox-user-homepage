#!/bin/bash

username=$1
password=$2

echo -e "$password\n$password\n" | passwd $username
echo -e "$password\n$password\n" | smbpasswd -a $username
