# 通用温度模型与绿化规划代码

仅保留温度代理模型的训练、预测和绿化规划。正文与附录明确的设置予以保留，未披露的配置采用常规默认值。本包是通用实现，不含研究数据。

## 运行

Python 3.10 或更高版本，在本目录执行：

```bash
python -m pip install -r requirements.txt
python run.py train --input input_arrays --output runs/model
python run.py evaluate --input input_arrays --checkpoint runs/model/model.pt --output runs/evaluation
python run.py plan --input input_arrays --checkpoint runs/model/model.pt --output runs/planning
```

训练后会自动评价空间留出区域。规划默认采用 heat-first 路径；可通过 `--route cool` 或 `--route random --route-seed 1` 更改，每次运行一条路径。每条路径分别生成蓝图与调适方案，保存分配掩膜和 30 m 温度预测。

## 输入

每个城市一个 `.npz` 文件。栅格应已配准，使用同一投影坐标系和左上角原点；H、W 均为 3 的倍数。

| 数组键 | 形状 | 内容 |
|---|---|---|
| `city_id` | 可选标量字符串 | 城市标识，默认使用文件名 |
| `landcover` | H × W | 10 m 土地覆盖类别 0–6，缺失为 −1 |
| `ndvi` | H × W | 10 m 原始 NDVI，缺失为 NaN |
| `height` | H × W | 10 m 建筑高度（m），缺失为 NaN |
| `building`、`urban` | H × W | 建筑足迹、城市评价域的 0/1 掩膜 |
| `lst` | H/3 × W/3 | 30 m LST（°C），缺失为 NaN |
| `climate` | D | 气候特征，默认 D=1，可输入夏季平均气温 |

默认类别为 0=tree、1=shrub、2=grass、3=built、4=bare、5=water、6=other。其他编码应先映射，或修改配置中的类别索引。

## 核心设置

全部参数位于 `config.json`。模型输入为七个土地覆盖通道、标准化 NDVI、经 `log1p` 后标准化的建筑高度和三个有效性掩膜。U-Net 宽度为 32/64/128/256，使用 GroupNorm、SiLU、抗混叠下采样和气候 FiLM 调制。城市背景面由训练区温度残差进行掩膜归一化高斯平滑得到，σ=16 个 30 m 单元。

训练使用 AdamW、batch size 8、55,000 次迭代；学习率从 0.001 余弦衰减至 0.00001，weight decay 为 0.0001。Huber 损失转折点为 2 °C，标签减去训练区城市面积加权中位数。空间块为 480 px，留出比例为 20%；留出标签不参与训练、归一化或背景面估计。

240 px 瓦片的起点对齐至 48 px 网格。每个 30 m 预测严格取九个 10 m 输出的均值，重叠瓦片取均值，评价按城市面积比例加权。

规划使用 17.64 ha 六边形和 10% 目标，筛除目标为零、可用面积不足或可用面积不足 1 ha 的单元。可绿化像元为非建筑足迹的 built/bare 像元。新增绿地采用城市现有绿地 NDVI 的 25% 分位，建筑高度为零，树、灌、草通道默认等权组合。

分配采用 50 次投影梯度更新，步长 0.1，梯度按单位内均方根归一化；紧凑性采用归一化总变差，权重 0.5。按优化强度选取目标数量的完整像元后重新预测温度。蓝图始终在初始景观上选择分配，调适方案在已实施景观上重新选择。

## 文件

- `greening/model.py`：温度网络。
- `greening/data.py`：输入处理、空间留出和网格对齐。
- `greening/engine.py`：训练、预测及基本精度评价。
- `greening/planning.py`：规划单元、绿化分配和两种规划规则。

训练结果包括模型与预处理配置；规划结果为 `initial.npz`、`blueprint.npz`、`adaptive.npz`。温度数组是代理模型直接预测值。
