#!/usr/bin/env bash
set -euo pipefail
if [ "$#" -ne 1 ]; then echo "Usage: $0 /path/to/eve.json" >&2; exit 2; fi
jq -r 'select(.event_type == "alert") | [.timestamp // "", .src_ip // "", .src_port // "", .dest_ip // "", .dest_port // "", .alert.signature_id // "", .alert.signature // "", .pcap_cnt // "", .flow_id // ""] | @tsv' "$1"
