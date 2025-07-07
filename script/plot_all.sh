#!/bin/bash

python3 script/throughput.py origin_data/delay/ --output plot/delay
python3 script/throughput.py origin_data/throughput/congest/ --output plot/congest --no-config
python3 script/throughput.py origin_data/throughput/rain/ --output plot/rain --no-config
python3 script/throughput.py origin_data/throughput/random_loss/ --output plot/random_loss --no-config
python3 script/throughput.py origin_data/throughput/reconfig\&hadover/ --output plot/r\&r