#!/usr/bin/env bash

set -euo pipefail -o errtrace

BASE_DIR="$(dirname "$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )")"
installation_type=false

main(){
    trap 'fail $? $LINENO' ERR

    parseOpts "$@"

    updateAndInstallPackages

    if [[ "$installation_type" != "receiver" ]]; then
        installNode
    fi

    info "Finished installing dependencies."
}

usage() {
    local exit_code=$1
    echo "usage: $0 -t INSTALLATION_TYPE"
    echo "    -h  display this help message"
    echo "    -t  Installation type: either 'controller', 'receiver', or 'all'"
    exit "$exit_code"
}

parseOpts(){
    while getopts ":ht:" opt; do
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
        warn "Installation type must be specified ('-t')."
        usage 1
    fi
}

updateAndInstallPackages(){
    info "Updating and installing packages..."

    sudo apt update

    # python3-pip: needed to ensure we have the pip module. Else we'd get errors like this:
    #   https://askubuntu.com/questions/1388144/usr-bin-python3-no-module-named-pip
    sudo apt -y install git python3-pip
    sudo apt -y full-upgrade

    sudo python3 -m pip install --upgrade pytz simpleaudio pyjson5
}

installNode(){
    info "\\nInstalling node and npm..."

    # Install node and npm. Installing this with the OS's default packages provided by apt installs a pretty old
    # version of node and npm. We need a newer version.
    # See: https://github.com/nodesource/distributions/blob/master/README.md#installation-instructions
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo bash -
    sudo apt-get install -y nodejs

    info "\\nInstalling react app dependencies..."
    # TODO: when installing from scratch on a fresh OS installation, this step once failed with
    # and error: https://gist.github.com/dasl-/01b9bf9650730c7dbfab6c859ea6c0dc
    # See if this is reproducible on a fresh install sometime...
    # It's weird because apparently it's a node error, but the line that is executing below is a
    # npm command. Could npm be shelling out to node? Maybe I can figure this out by running
    # checking the process list while the next step is running, and htop to look at RAM usage.`
    npm install --prefix "$BASE_DIR/app"
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
