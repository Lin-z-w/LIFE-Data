# LIFE-Data

本仓库保存 LIFE 论文的实验数据和基础绘图脚本。ICNP 2026 camera-ready 版本的数据沿革和本地大型原始运行目录说明见 [`CAMERA_READY_DATA.md`](CAMERA_READY_DATA.md)。

## 各数据集测试场景

- combine、inter&intra：动态带宽、动态时延、seed=55555，UP_LOSS_RATE=0.45%、DOWN_LOSS_RATE=0.4%、jitter=5ms、30s 75s卫星切换事件。
- random loss：100Mbps，30ms，下行0.4%丢包，上行0.45%丢包。
- rain：基于random loss场景，进行120s测试，在60s后，每隔15s，在基础丢包率上，增加0%~1%（10mm降雨量丢包率增加量）丢包率，并且带宽降为原本的1/3（模拟调制方式从64QAM切换至QPSK，编码效率变为原本的1/3）模拟降雨场景。
- congest：100Mbps，30ms，进行120s测试，在60s后加入持续的50Mbps速率的UDP流抢占带宽。
- reconfig&hadover：动态配置带宽、延迟(5ms抖动)，无丢包，其中30s、75s为卫星切换节点。

## 图像绘制

在仓库根目录运行`./script/plot_all.sh`即可

最终 camera-ready 图表使用的绘图脚本保存在论文源仓库的 `scripts/` 目录中。`camera_ready/` 下的完整原始运行约 52 GB，作为本地归档保留，不纳入普通 Git 同步。
