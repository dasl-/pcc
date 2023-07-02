#!/usr/bin/env bash

set -euo pipefail -o errtrace

BASE_DIR="$(dirname "$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )")"
installation_type=false

main(){
    trap 'fail $? $LINENO' ERR

    parseOpts "$@"

    setupLogging
    setupSystemdServices

    # Do controller stuff
    if [[ "$installation_type" != 'receiver' ]]; then
        buildWebApp
    fi

    # Do receiver stuff
    if [[ "$installation_type" != 'controller' ]]; then
        :
    fi

    info "Finished installation!"
}

usage() {
    local exit_code=$1
    echo "usage: $0 -t INSTALLATION_TYPE [-c] [-w]"
    echo "    -h  display this help message"
    echo "    -t  Installation type: either 'controller', 'receiver', or 'all'"
    exit "$exit_code"
}

parseOpts(){
    while getopts ":ht:cw" opt; do
        case $opt in
            h) usage 0 ;;
            t)
                if [[ "$OPTARG" != "controller" && "$OPTARG" != "receiver" && "$OPTARG" != "all" ]]; then
                    echo "Invalid installation type."
                    usage 1
                else
                    installation_type=${OPTARG}
                fi
                ;;
            \?)
                echo "Invalid option: -$OPTARG" >&2
                usage 1
                ;;
            :)
                echo "Option -$OPTARG requires an argument." >&2
                usage 1
                ;;
            *) usage 1 ;;
        esac
    done

    if [ "$installation_type" = false ] ; then
        echo "Installation type must be specified ('-t')."
        usage 1
    fi
}

setupLogging(){
    info "Setting up logging..."

    # syslog
    sudo mkdir -p /var/log/pcc
    if [[ "$installation_type" == 'controller' || "$installation_type" == 'all' ]]; then
        sudo touch /var/log/pcc/controller.log
        sudo cp "$BASE_DIR"/install/pcc_controller_syslog.conf /etc/rsyslog.d
    fi
    if [[ "$installation_type" == 'receiver' || "$installation_type" == 'all' ]]; then
        sudo touch /var/log/pcc/receiver.log
        sudo cp "$BASE_DIR"/install/pcc_receiver_syslog.conf /etc/rsyslog.d
    fi
    sudo systemctl restart rsyslog

    # logrotate
    sudo cp "$BASE_DIR"/install/pcc_logrotate /etc/logrotate.d
    sudo chown root:root /etc/logrotate.d/pcc_logrotate
    sudo chmod 644 /etc/logrotate.d/pcc_logrotate
}

setupSystemdServices(){
    info "Setting up systemd services..."

    if [[ "$installation_type" == 'controller' || "$installation_type" == 'all' ]]; then
        sudo "$BASE_DIR/install/pcc_controller_service.sh"
    fi
    if [[ "$installation_type" == 'receiver' || "$installation_type" == 'all' ]]; then
        sudo "$BASE_DIR/install/pcc_receiver_service.sh"
    fi
    sudo chown root:root /etc/systemd/system/pcc_*.service
    sudo chmod 644 /etc/systemd/system/pcc_*.service

    # stop and disable units in case we are changing which host is the controller / receiver
    # and unit files already existed...
    local units
    units=$(systemctl --all --no-legend list-units 'pcc_*' | awk '{ print $1; }' | paste -sd ' ')
    if [ -n "${units}" ]; then
        # shellcheck disable=SC2086
        sudo systemctl disable $units || true
        # shellcheck disable=SC2086
        sudo systemctl stop $units || true
    fi

    if [[ "$installation_type" == 'controller' || "$installation_type" == 'all' ]]; then
        sudo systemctl enable pcc_controller.service
        sudo systemctl daemon-reload
        sudo systemctl restart pcc_controller.service
    fi
    if [[ "$installation_type" == 'receiver' || "$installation_type" == 'all' ]]; then
        sudo systemctl enable pcc_receiver.service
        sudo systemctl daemon-reload
        sudo systemctl restart pcc_receiver.service
    fi
}

buildWebApp(){
    info "Writing web app config..."
    "$BASE_DIR"/utils/write_config_for_web_app

    info "Building web app..."
    npm run build --prefix "$BASE_DIR"/app
}

fail(){
    local exit_code=$1
    local line_no=$2
    local script_name
    script_name=$(basename "${BASH_SOURCE[0]}")
    die "Error in $script_name at line number: $line_no with exit code: $exit_code"
}

info(){
    echo -e "\x1b[32m$*\x1b[0m" # green stdout
}

warn(){
    echo -e "\x1b[33m$*\x1b[0m" # yellow stdout
}

die(){
    echo
    echo -e "\x1b[31m$*\x1b[0m" >&2 # red stderr
    exit 1
}

main "$@"
