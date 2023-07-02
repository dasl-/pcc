#!/usr/bin/env bash
# creates the queue service file
BASE_DIR="$(dirname "$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )")"
cat <<-EOF | sudo tee /etc/systemd/system/pcc_controller.service >/dev/null
[Unit]
Description=PCC controller
After=network-online.target
Wants=network-online.target

[Service]
Environment=HOME=/root
ExecStart=$BASE_DIR/bin/controller
Restart=on-failure
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=PCC_CONTROLLER

[Install]
WantedBy=multi-user.target
EOF
