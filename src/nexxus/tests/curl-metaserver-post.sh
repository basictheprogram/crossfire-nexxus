#!/bin/bash

curl -X POST http://nexxus.dev.local/meta_update.php  \
     -d "hostname=c-98-61-28-198.hsd1.mn.comcast.net" \
     -d "port=9000" \
     -d "html_comment=This is an HTML comment with curl" \
     -d "text_comment=This is a text comment with curl" \
     -d "archbase=Archetypes base description" \
     -d "mapbase=Maps base description" \
     -d "codebase=Server code base description" \
     -d "flags=abc" \
     -d "num_players=100" \
     -d "in_bytes=1024" \
     -d "out_bytes=2048" \
     -d "uptime=3600" \
     -d "version=1.0.0" \
     -d "sc_version=2.0.0" \
     -d "cs_version=2.0.0"
