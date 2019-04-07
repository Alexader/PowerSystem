# 电力系统网损优化

1. 输入输出

   输入：一个电力系统的潮流参数和线路本身的参数

* 节点数：N，节点的负载情况和发电机分布情况（确定节点的类型PV还是PQ还是平衡）
* 线路数：M，线路电路参数
* 节点或者线路能够进行的操作列表
* 已经计算好的线路瞬时潮流（计算网损） 

输出：应该在何处采取何种电力操作

* 220KV线路上的串联电容还是电感

通过改变线路的电路参数重新计算一次网损

* 线路改变并列方式（双线单线的切换）

  也是线路的电路参数

* 变压器的并列方式

  修改变压器模型中的电路参数 X

* 母线上的并联电容或者电抗器

* 同步调相机改变节点相位

* 同步调相机

  电力系统中的主要负载是异步电动机和变压器，需要从电网汲取大量的无功，在负载过大的时候，会造成电网的功率因数下降，造成线路的损耗上升。所以可以在受电端投入发出无功的同步调相机，这能够改善系统的功率因数，使得系统传输的无功减少，进而降低网损。

  比如在电网重载运行的时候，让调相机运行在过励的状态，可以增加电网中的滞后电流。

* 调节发电机的无功出力

  数字控制的自动励磁系统，通过控制励磁电流改变发电机的无功。建立负反馈的传递函数。

* 改变变压器的变比

  12.3节电力系统课本关于利用无功功率补偿调压

2. 电网拓扑分割

3. 程序模型

* 线路模型 Line：每条线路的网损，计算接口：

  `calcLineLoss();`

* 节点模型 Bus：每个节点的历史电价，平均值作为实时电价，作为网损代价的一部分

  计算接口：`updatePrice();`

* 变压器模型 Transformer：变压器的台数（并联运行的模式），

  计算接口：`calcTansformerLoss();`

* 总体网架结构 `grid_220`: 包括上面的三个对象模型，然后包含一些计算的接口。

  `calcPowerFlowLoss()`	

  `lossJudge();`  // 查看网络中网损情况最严重，优先等级较高的区域进行处理

4. 如何按照已经得到的数据建立优化的模型

   * 约束条件

     1. 电力系统的等式平衡
        $$
        P_i = V_i \sum_{j\in h} V_j(G_{ij}cos\delta_{ij}+B_{ij}sin\delta_{ij})\\
        Q_i = V_i \sum_{j\in h} V_j(G_{ij}cos\delta_{ij}-B_{ij}sin\delta_{ij})
        $$

     2. 电力系统的不等式平衡
        $$
        V_{gmin} \leq V_{gi} \leq V_{gmax}\\
        Q_{cmin} \leq Q_{ci} \leq Q_{cmax}\\
        T_{imin} \leq T_{i} \leq T_{imax}\\
        $$

     3. 目标函数
        $$
        F = min [\omega_1 P_{\Delta} + \omega_2 \sum_{i=1}^{N}(\frac{\Delta V_i} {V_{imax}-V_{imin}}) ^ 2 + \omega_3 \sum_{i=1}^{N} (\Delta Q_i)^2]
        $$
        第一项考虑网损值，第二项考虑了超过节点电压超过额定值的罚项，第三项考虑了无功超过界限的罚项。

        比如有投切的电抗电容器的组数，变压器分接头的挡数，实际发电机机端电压，等等。

        1. 电力系统拓扑调整方法

        * 并联电容电抗器

          把有并联电容电抗的节点处看做PV节点，最后优化算出的无功值可以转化为具体的电抗电容值。

          或者让有并联电容电抗器的节点的参数$G_{ij}$ 和 $B_{ij}$  作为变量参与优化。
          $$
          F = min [\omega_1 P_{\Delta} + \omega_2 \sum_{i=1}^{N}(\frac{\Delta V_i} {V_{imax}-V_{imin}}) ^ 2 + \omega_3 \sum_{i=1}^{N} (\Delta Q_i)^2]\\
          s.t.P_i = V_i \sum_{j\in h} V_j(G_{ij}cos\delta_{ij}+B_{ij}sin\delta_{ij})\\
          Q_i = V_i \sum_{j\in h} V_j(G_{ij}cos\delta_{ij}-B_{ij}sin\delta_{ij})\\
          V_{gmin} \leq V_{gi} \leq V_{gmax}\\
          Q_{cmin} \leq Q_{ci} \leq Q_{cmax}\\
          N_{min} \leq N \leq N_{max} // 可以增加减少的阻抗值的限制值
          $$

        * 线路改变并列方式

          改变对应线路的物理参数值，作为控制变量进行优化。（不过是整数规划）混合整数规划
          $$
          F = min [\omega_1 P_{\Delta} + \omega_2 \sum_{i=1}^{N}(\frac{\Delta V_i} {V_{imax}-V_{imin}}) ^ 2 + \omega_3 \sum_{i=1}^{N} (\Delta Q_i)^2]\\
          s.t.P_i = V_i \sum_{j\in h} V_j(G_{ij}cos\delta_{ij}+B_{ij}sin\delta_{ij})\\
          Q_i = V_i \sum_{j\in h} V_j(G_{ij}cos\delta_{ij}-B_{ij}sin\delta_{ij})\\
          V_{gmin} \leq V_{gi} \leq V_{gmax}\\
          Q_{cmin} \leq Q_{ci} \leq Q_{cmax}\\
          // 如何表示可行集？
          $$

        * 修改变压器的并列方式

          改变对应线路的物理参数值，作为控制变量进行优化。（不过是整数规划）

        * 改变变压器的变比

          先连续，选最接近的离散值

          改变节点的电压值，作为PV节点进行优化

        * 投切母线并联容抗器

        2. 发电机主动调整方法

        * 同步调相机

        * 调节发电机的无功输出

          调节调相机改变不同节点之间的角度差，把角度作为控制变量，把三角函数泰勒展开。多变量优化

     4. 变成矩阵的表示形式以及对非凸函数的凸化处理

        通过对非凸约束中凸函数的线性化和引入松弛变量，将非凸的最优潮流问题转化为凸优化问题求解。
        $$
        min  f(x)\\
        s.t. g_i(x)=0\\
        h_{low}\leq h(x) \leq h_{high}\\
        其中 f(x) = \omega_1 P_{\Delta} + \omega_2 \sum_{i=1}^{N}(\frac{\Delta V_i} {V_{imax}-V_{imin}}) ^ 2 + \omega_3 \sum_{i=1}^{N} (\Delta Q_i)^2\\
        g_1(x)=P_i - V_i \sum_{j\in h} V_j(G_{ij}cos\delta_{ij}+B_{ij}sin\delta_{ij})\\
        g_2(x) = Q_i - V_i \sum_{j\in h} V_j(G_{ij}cos\delta_{ij}-B_{ij}sin\delta_{ij})
        $$
        引入松弛因子 $l$，$u$ 。使用使用拉格朗日乘子
        $$
        min  f(x) - \mu(\sum_{j=1}^{r}lnl_j + \sum_{j=1}^{r}lnu_j), l>0, u>0\\
        s.t. g_i(x)=0\\
        h(x)+u-h_{high} = 0\\
        h(x)-l-h_{low} = 0
        $$


