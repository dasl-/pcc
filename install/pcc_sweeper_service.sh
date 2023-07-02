#!/usr/bin/env bash
# creates the server service file
BASE_DIR="$(dirname "$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )")"
cat <<-EOF | sudo tee /etc/systemd/system/pcc_sweeper.service >/dev/null
[Unit]
Description=PCC sweeper
After=network-online.target
Wants=network-online.target

[Service]
Environment=HOME=/root
# Command to execute when the service is started
ExecStart=$BASE_DIR/bin/sweeper
Restart=on-failure
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=PCC_SWEEPER

[Install]
WantedBy=multi-user.target
EOF
