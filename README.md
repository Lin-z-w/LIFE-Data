# LIFE-Data

## 各数据集测试场景

- delay、inter&intra：动态带宽、动态时延、seed=55555，UP_LOSS_RATE=0.45%、DOWN_LOSS_RATE=0.4%、jitter=5ms、30s 75s卫星切换事件。
- random loss：100Mbps，30ms，下行0.4%丢包，上行0.45%丢包
- rain：基于random loss场景，进行120s测试，在60s后，每隔15s，在基础丢包率上，增加0%~1%（10mm降雨量丢包率增加量）丢包率+并且带宽降为原本的1/3（模拟调制方式从64QAM切换至QPSK，编码效率变为原本的1/3）模拟降雨场景
- congest：100Mbps，30ms，进行120s测试，在每隔15s加入持续15s的50Mbps速率的UDP流抢占带宽
- reconfig&hadover：动态配置带宽、延迟(7ms抖动)，无丢包，其中30s、75s为卫星切换节点。