#!/bin/bash

# throughput
python3 script/throughput.py origin_data/standard/ --output plot/throughput/standard
python3 script/throughput.py origin_data/throughput/congest/ --output plot/throughput/congest --no-config
python3 script/throughput.py origin_data/throughput/rain/ --output plot/throughput/rain --no-config
python3 script/throughput.py origin_data/throughput/random_loss/ --output plot/throughput/random_loss --no-config
python3 script/throughput.py origin_data/throughput/reconfig\&hadover/ --output plot/throughput/reconfig\&hadover

# delay with time
python3 script/delay.py origin_data/standard/ plot/delay/delay_with_time/
python3 script/delay.py origin_data/throughput/congest/ plot/delay/delay_with_time/
python3 script/delay.py origin_data/throughput/rain/ plot/delay/delay_with_time/
python3 script/delay.py origin_data/throughput/random_loss/ plot/delay/delay_with_time/
python3 script/delay.py origin_data/throughput/reconfig\&hadover/ plot/delay/delay_with_time/

# delay box
python3 script/delay2.py ./origin_data/standard/ plot/delay/box/
python3 script/delay2.py origin_data/throughput/congest/ plot/delay/box/
python3 script/delay2.py origin_data/throughput/rain/ plot/delay/box/
python3 script/delay2.py origin_data/throughput/random_loss/ plot/delay/box/
python3 script/delay2.py origin_data/throughput/reconfig\&hadover/ plot/delay/box/