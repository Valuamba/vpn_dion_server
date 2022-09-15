#!/bin/bash

CLIENT_MAX_COUNT=250
RED='\033[0;31m'
ORANGE='\033[0;33m'
NC='\033[0m'

function isRoot() {
  if [ "${EUID}" -ne 0 ]; then
    return_error "You need to run this script as root"
  fi
}

function checkVirt() {
  if [ "$(systemd-detect-virt)" == "openvz" ]; then
    return_error "OpenVZ is not supported"
  fi

  if [ "$(systemd-detect-virt)" == "lxc" ]; then
    echo "LXC is not supported (yet)."
    echo "WireGuard can technically run in an LXC container,"
    echo "but the kernel module has to be installed on the host,"
    echo "the container has to be run with some specific parameters"
    echo "and only the tools need to be installed in the container."
    exit 1
  fi
}

function checkOS() {
  # Check OS version
  if [[ -e /etc/debian_version ]]; then
    source /etc/os-release
    OS="${ID}" # debian or ubuntu
    if [[ ${ID} == "debian" || ${ID} == "raspbian" ]]; then
      if [[ ${VERSION_ID} -lt 10 ]]; then
        return_error "Your version of Debian (${VERSION_ID}) is not supported. Please use Debian 10 Buster or later"
      fi
      OS=debian # overwrite if raspbian
    fi
  elif [[ -e /etc/fedora-release ]]; then
    source /etc/os-release
    OS="${ID}"
  elif [[ -e /etc/centos-release ]]; then
    source /etc/os-release
    OS=centos
  elif [[ -e /etc/oracle-release ]]; then
    source /etc/os-release
    OS=oracle
  elif [[ -e /etc/arch-release ]]; then
    OS=arch
  else
    return_error "Looks like you aren't running this installer on a Debian, Ubuntu, Fedora, CentOS, Oracle or Arch Linux system"
  fi

  echo "
  [CheckOS]
  OS=${OS}
  "
}

function checkEnvironment {
  isRoot
  checkVirt
  checkOS
}

function checkClient() {
  does_dot_exist
  does_ipv4_exit
  does_ipv6_exists

  log_info "Client was checked."
}

function does_dot_exist() {
  echo "Check Dot existance"
  for DOT_IP in {2..254}; do
    DOT_EXISTS=$(grep -c "${WIREGUARD_IPv4::-1}${DOT_IP}" "${WIREGUARD_CLIENT_CONFIG_PATH}")
    if [[ $DOT_EXISTS -gt 0 ]]; then
      return_error "The subnet configured supports only 253 clients."
    else
      break
    fi
  done
}

function does_ipv4_exit() {
  echo "Check ipv4 existance"
  until [[ ${IPV4_EXISTS} == '0' ]]; do
    CLIENT_WG_IPV4="${WIREGUARD_IPv4}.${DOT_IP}"
    IPV4_EXISTS=$(grep -c "$CLIENT_WG_IPV4/24" "${WIREGUARD_CLIENT_CONFIG_PATH}")

    if [[ $IPV4_EXISTS -gt 0 ]]; then
      return_error "A client with the specified IPv6 was already created, please choose another IPv6."
    else
      break
    fi
  done

  echo "
  [Does_ipv4_exit]
  CLIENT_WG_IPV4=${CLIENT_WG_IPV4}
  "
}

function does_client_exist() {
  echo "Check client existance"
  until [[ ${CLIENT_NAME} =~ ^[a-zA-Z0-9_-]+$ && ${CLIENT_EXISTS} == '0' && ${#CLIENT_NAME} -lt 16 ]]; do
    CLIENT_EXISTS=$(grep -c -E "^### Client ${CLIENT_NAME}\$" "${WIREGUARD_CLIENT_CONFIG_PATH}")

    if [[ $CLIENT_EXISTS -gt 0 ]]; then
      return_error "A client with specified name already exist"
    else
      break
    fi
  done
}

function generate_client_name() {
  if [[ ${#CLIENT_NAME} -lt 2 ]]; then
    return_error "Incorrect client name"
  fi

  echo "Generating client name"
  client_index=0
  until [[ ${CLIENT_NAME} =~ ^[a-zA-Z0-9_-]+$ && ${CLIENT_EXISTS} == '0' && ${#CLIENT_NAME} -lt 16 ]]; do
      CLIENT_EXISTS=$(grep -c -E "^### Client ${CLIENT_NAME}_${client_index}\$" "${WIREGUARD_CLIENT_CONFIG_PATH}")
#      echo "Exists: ${CLIENT_EXISTS} ___ ${CLIENT_NAME}_${client_index}"

      if [[ ${CLIENT_EXISTS} == 0 ]]; then
          CLIENT_NAME="${CLIENT_NAME}_${client_index}"
          echo "Client name: ${CLIENT_NAME}"
          break
      elif [[ ${CLIENT_EXISTS} -gt 0 ]]; then
          if [[ ${client_index} -gt ${CLIENT_MAX_COUNT} ]]; then
              return_error "Cannot generate client name"
          fi
          client_index=$((client_index+1))
      else
          return_error "Incorrect client name"
      fi
  done
}

function does_ipv6_exists() {
  echo "Check IPv6 existance"
  until [[ ${IPV6_EXISTS} == '0' ]]; do
    CLIENT_WG_IPV6="${WIREGUARD_IPv6}::${DOT_IP}"
    IPV6_EXISTS=$(grep -c "${CLIENT_WG_IPV6}/64" "${WIREGUARD_CLIENT_CONFIG_PATH}")

    if [[ $IPV6_EXISTS -gt 0 ]]; then
      return_error "A client with the specified IPv6 was already created, please choose another IPv6."
    else
      break
    fi

  done
  echo "
  [Does_ipv6_exit]
  CLIENT_WG_IPV6=${CLIENT_WG_IPV4}
  "
}

function log_info() {
  info=$1
  echo "INFO: ${info}"
}

function return_error(){
  error_message=$1
  echo -e "[ERROR]\nMessage=${error_message}"
  exit 1
}

function newClient() {

  generate_client_name
  does_client_exist

  APACHE_CONFIG_PATH="/var/www/html/${SERVER_WG_NIC}-client-${CLIENT_NAME}.conf"
  CLIENT_CONFIG_HOME="${HOME_DIR}/${SERVER_WG_NIC}-client-${CLIENT_NAME}.conf"

  CLIENT_PRIV_KEY=$(wg genkey)
  CLIENT_PUB_KEY=$(echo "${CLIENT_PRIV_KEY}" | wg pubkey)
  CLIENT_PRE_SHARED_KEY=$(wg genpsk)

    echo "[Interface]
  PrivateKey = ${CLIENT_PRIV_KEY}
  Address = ${CLIENT_WG_IPV4}/32,${CLIENT_WG_IPV6}/128
  DNS = ${CLIENT_DNS_1},${CLIENT_DNS_2}

  [Peer]
  PublicKey = ${SERVER_PUB_KEY}
  PresharedKey = ${CLIENT_PRE_SHARED_KEY}
  Endpoint = ${ENDPOINT}
  AllowedIPs = 0.0.0.0/0,::/0" >>"${CLIENT_CONFIG_HOME}"

    # Add the client as a peer to the server
    echo -e "\n### Client ${CLIENT_NAME}
  [Peer]
  PublicKey = ${CLIENT_PUB_KEY}
  PresharedKey = ${CLIENT_PRE_SHARED_KEY}
  AllowedIPs = ${CLIENT_WG_IPV4}/32,${CLIENT_WG_IPV6}/128" >>"${WIREGUARD_CLIENT_CONFIG_PATH}"

  wg syncconf "${SERVER_WG_NIC}" <(wg-quick strip "${SERVER_WG_NIC}")

  cp "${CLIENT_CONFIG_HOME}" "${APACHE_CONFIG_PATH}"

    echo "
  [NewClient]
  ConfigPath=${CLIENT_CONFIG_HOME}"
}

function revokeClient() {
  echo "Removing client"
	NUMBER_OF_CLIENTS=$(grep -c -E "^### Client ${CLIENT_NAME}" $WIREGUARD_CLIENT_CONFIG_PATH)
	if [[ ${NUMBER_OF_CLIENTS} == '0' ]]; then
		return_error "You have no existing clients!"
	fi

	# remove [Peer] block matching $CLIENT_NAME
	sed -i "/^### Client ${CLIENT_NAME}\$/,/^$/d" "/etc/wireguard/${SERVER_WG_NIC}.conf"

  echo "RM path: ${HOME_DIR}/${SERVER_WG_NIC}-client-${CLIENT_NAME}.conf"
	# remove generated client file
	rm -f "${HOME_DIR}/${SERVER_WG_NIC}-client-${CLIENT_NAME}.conf"

	# restart wireguard to apply changes
	wg syncconf "${SERVER_WG_NIC}" <(wg-quick strip "${SERVER_WG_NIC}")
}

function setLocalVariables() {

  if [ -e "/home/${CLIENT_NAME}" ]; then
		# if $1 is a user name
		home_dir="/home/${CLIENT_NAME}"
	elif [ "${SUDO_USER}" ]; then
		# if not, use SUDO_USER
		if [ "${SUDO_USER}" == "root" ]; then
			# If running sudo as root
			home_dir="/root"
		else
			home_dir="/home/${SUDO_USER}"
		fi
	else
		# if not SUDO_USER, use /root
		home_dir="/root"
	fi

  ENDPOINT="${SERVER_PUB_IP}:${SERVER_PORT}"

  # if variable is empty set default
  [ -z "$WIREGUARD_IPv4" ] && WIREGUARD_IPv4=$(echo "$SERVER_WG_IPV4" | awk -F '.' '{ print $1"."$2"."$3 }')
  [ -z "$WIREGUARD_IPv6" ] && WIREGUARD_IPv6=$(echo "$SERVER_WG_IPV6" | awk -F '::' '{ print $1 }')
  [ -z "$WIREGUARD_DIRECTORY" ] && WIREGUARD_DIRECTORY="/etc/wireguard/"
  [ -z "$HOME_DIR" ] && HOME_DIR=$home_dir

  if [[ ! -e $HOME_DIR ]]; then
    return_error "Home dir ${HOME_DIR} doesn't exist."
  fi

  if [[ ! -e $WIREGUARD_DIRECTORY ]]; then
    return_error "WG dir ${WIREGUARD_DIRECTORY} doesn't exist."
  fi

    WIREGUARD_CLIENT_CONFIG_PATH="${WIREGUARD_DIRECTORY}${SERVER_WG_NIC}.conf"
}

function getCommand() {
    command=$1
    arr=$@
    shift 1
    if [[ $command == 'add' ]]; then
        if [[ ! " ${arr[*]} " =~ " --name " ]]; then
            return_error "Client name dosen't specified."
        fi

        while [ $# -gt 0 ]; do
            case "$1" in
            --name) CLIENT_NAME="$2"
            shift 2 ;;
            --wg-dir) WIREGUARD_DIRECTORY="$2"
            shift 2 ;;
            --home) HOME_DIR="$2"
            shift 2 ;;
            --ipv4) WIREGUARD_IPv4="$2"
            shift 2 ;;
            --ipv6) WIREGUARD_IPv6="$2"
            shift 2 ;;
             *) return_error $"Wrong parameter" ;;
            esac
        done

        checkEnvironment
        setLocalVariables
        checkClient
        newClient

    elif [[ $command == 'remove' ]]; then
      if [[ ! " ${arr[*]} " =~ " --name " ]]; then
            return_error "Client name dosen't specified."
        fi

        while [ $# -gt 0 ]; do
            case "$1" in
             --name) CLIENT_NAME="$2"
                shift 2 ;;
                --wg-dir) WIREGUARD_DIRECTORY="$2"
                shift 2 ;;
                --home) HOME_DIR="$2"
                shift 2 ;;
            esac
        done

        checkEnvironment
        setLocalVariables
        revokeClient
    elif [[ $command == 'check' ]]; then
        while [ $# -gt 0 ]; do
            case "$1" in
                --name) CLIENT_NAME="$2"
                shift 2 ;;
                --wg-dir)  WIREGUARD_DIRECTORY="$2"
                shift 2 ;;
                --home) HOME_DIR="$2"
                shift 2 ;;
            esac
        done

        checkEnvironment
        setLocalVariables
        checkClient
    else
      return_error "Command was not found"
    fi
}

if [[ -e /etc/wireguard/params ]]; then
  source /etc/wireguard/params
  getCommand "$@"
else
 return_error "Wireguard is not installed."
fi
