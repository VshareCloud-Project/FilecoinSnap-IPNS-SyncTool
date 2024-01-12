#!/bin/bash

# Variables
IPFS_GATEWAY=${IPFS_GATEWAY:-"https://gateway.ipns.tech"}

# Echo function with color
echo_func() {
    case $1 in
        "ERROR")
            echo -e "\033[1;31m$2\033[0m"
            ;;
        "INFO")
            echo -e "\033[1;36m$2\033[0m"
            ;;
        "SUCCESS")
            echo -e "\033[1;32m$2\033[0m"
            ;;
    esac
}

# Check if required tools are installed
for cmd in curl wget tar systemctl; do
    if ! command -v $cmd &>/dev/null; then
        echo_func ERROR "$cmd is not installed. Please install it first."
        exit 1
    fi
done

# Check the distribution release
if [[ -f /etc/redhat-release ]]; then
    release="centos"
elif cat /etc/issue | grep -q -E -i "debian"; then
    release="debian"
elif cat /etc/issue | grep -q -E -i "ubuntu"; then
    release="ubuntu"
elif cat /etc/issue | grep -q -E -i "centos|red hat|redhat"; then
    release="centos"
elif cat /proc/version | grep -q -E -i "raspbian|debian"; then
    release="debian"
elif cat /proc/version | grep -q -E -i "ubuntu"; then
    release="ubuntu"
elif cat /proc/version | grep -q -E -i "centos|red hat|redhat"; then
    release="centos"
elif cat /proc/version | grep -q -E -i "deepin"; then
    release="deepin"
else
    echo_func ERROR "Unsupported operating system!"
    exit 1
fi
echo_func INFO "System release: $release"

echo_func INFO "Updating system..."
if [[ ${release} == "centos" ]]; then
    yum makecache
    yum install epel-release -y
    yum update -y
else
    apt update
    apt dist-upgrade -y
    apt autoremove --purge -y
fi

echo_func INFO "Installing required tools..."
if [[ ${release} == "centos" ]]; then
    yum install aria2 python3-pip -y
else
    apt install aria2 python3-pip -y
fi

