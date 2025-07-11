#!/bin/bash

# throughput
python3 script/throughput.py origin_data/delay/single_delay/ --output plot/throughput/delay
python3 script/throughput.py origin_data/throughput/congest/ --output plot/throughput/congest --no-config
python3 script/throughput.py origin_data/throughput/rain/ --output plot/throughput/rain --no-config
python3 script/throughput.py origin_data/throughput/random_loss/ --output plot/throughput/random_loss --no-config
python3 script/throughput.py origin_data/throughput/reconfig\&hadover/single_delay/ --output plot/throughput/r\&r

# delay
python3 script/delay.py origin_data/delay/single_delay/ plot/delay/
python3 script/delay.py origin_data/throughput/congest/ plot/delay/
python3 script/delay.py origin_data/throughput/rain/ plot/delay/
python3 script/delay.py origin_data/throughput/random_loss/ plot/delay/
python3 script/delay.py origin_data/throughput/reconfig\&hadover/single_delay/ plot/delay/