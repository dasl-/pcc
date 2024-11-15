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
    # libasound2-dev: needed to install simpleaudio via pip
    sudo apt -y install git python3-pip libasound2-dev
    sudo apt -y full-upgrade

    sudo python3 -m pip install --upgrade pytz simpleaudio pyjson5
}

installNode(){
    info "\\nInstalling node and npm..."

    # Install node and npm. Installing this with the OS's default packages provided by apt installs a pretty old
    # version of node and npm. We need a newer version.
    # See: https://github.com/nodesource/distributions#installation-instructions
    sudo apt -y install ca-certificates curl gnupg
    sudo mkdir -p /etc/apt/keyrings

    # We added the `--batch --yes` flags to gpg to hopefully prevent errors like this:
    #
    # gpg: cannot open '/dev/tty': No such device or address
    # (23) Failed writing body
    # Error in install_dependencies.sh at line number: 81 with exit code: 2
    #
    # We got these errors the 2nd time we ran the installation script, from a dsh started from my laptop.
    # For some reason there were no errors the first time we ran the installation script.
    #
    # See: https://github.com/gravitational/teleport/issues/9726
    curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | sudo gpg --batch --yes --dearmor -o /etc/apt/keyrings/nodesource.gpg

    local NODE_MAJOR=18
    echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_$NODE_MAJOR.x nodistro main" | sudo tee /etc/apt/sources.list.d/nodesource.list
    sudo apt update
    sudo apt -y install nodejs

    info "\\nInstalling react app dependencies..."

    # You may get OOM errors at this step: https://gist.github.com/dasl-/5abdd44806ff75f644daa9bc46b69b3e
    # We tried working around this via the `--max-old-space-size` flag (see: https://stackoverflow.com/a/40939496 )
    # But that didn't work. Perhaps it's impossible to install with a lower limit - maybe it needs a ton of 
    # RAM to succeed. If you get failures here, I suggest temporarily moving the SD card to a pi with more RAM
    # and performing the installation there. Once it's been installed, you can move the SD card back to the
    # original pi.
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
