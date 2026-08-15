# 1. 基盤環境・実行フロー

## 目的

将来的に sensor、brain、action、進化則、物理、環境要素などを追加・交換できることを前提に、シミュレーション基盤と実行フローを分離して設計する。

主な要件は以下。

- 2D 環境
- headless 実行可能
- UI 付き実行可能
- simulation rate と rendering rate を分離
- CPU 実装を reference implementation として保持
- regression test を通しながら GPU 実装へ段階的に置換
- 大量 agent を前提にデータ指向で設計
- 将来的な CUDA kernel 自作を妨げない構造
- agent / environment / evolution の各要素を交換可能にする

---

## 技術スタック

### Frontend

- TypeScript
- React
- Vite
- PixiJS

役割分担:

- React
  - 実験条件設定
  - simulation control
  - parameter editor
  - agent inspector
  - genome viewer
  - 統計・グラフ表示
  - 実験結果管理
- PixiJS
  - 2D world の描画
  - agent / food / obstacle / sensor の可視化
  - zoom / pan / click / drag / hover などの interaction

要件:

- 軽量
- UI の拡張性が高い
- mouse / keyboard interaction が可能
- browser 上で動作
- 外部公開しやすい
- 開発が活発な major ecosystem を使う

---

## Backend / orchestration

Python を中心にする。

### FastAPI

UI 付き実行時のみ使用する。

用途:

- REST API
- WebSocket
- experiment の開始・停止
- parameter 更新
- snapshot 配信

simulation core 自体は FastAPI に依存させない。

---

## 実行モード

同じ SimulationCore を複数の実行形態から使用する。

### Headless mode

例:

```bash
python -m alife run experiment.yaml
```

用途:

- 大規模進化実験
- benchmark
- parameter sweep
- regression test
- 長時間 simulation

UI、renderer、FastAPI は起動しない。

### Interactive mode

例:

```bash
python -m alife server experiment.yaml
```

構成:

```text
SimulationCore
    |
    +-- simulation loop
    |
    +-- snapshot publisher
            |
            v
        WebSocket
            |
            v
      React + PixiJS
```

---

## Simulation rate と Rendering rate

simulation と rendering は独立させる。

例:

```text
simulation: 1000 Hz
rendering :   30 Hz
```

simulation は固定 timestep で進行し、一定間隔で描画用 snapshot だけを frontend に送る。

```text
step
step
step
step
step
  |
  +------ snapshot ------> renderer
  |
step
step
step
...
```

高速実行時には rendering を完全に停止できる。

---

## Simulation tick

基本的な 1 tick の流れ。

```text
1. environment state 更新
2. spatial index 更新
3. sensor 計算
4. brain forward
5. action decode
6. force / control 入力生成
7. dynamics integration
8. collision / constraint 解決
9. interaction 判定
10. energy / internal state 更新
11. death / reproduction 判定
12. evolution 関連処理
13. statistics 更新
14. 必要なら snapshot 発行
```

各処理は独立した System として交換可能にする。

---

## Architecture

```text
World
|
+-- WorldState
|
+-- EnvironmentSystem
+-- SpatialSystem
+-- SensorSystem
+-- BrainSystem
+-- ActionSystem
+-- ForceSystem
+-- PhysicsSystem
+-- InteractionSystem
+-- EnergySystem
+-- EvolutionSystem
+-- StatisticsSystem
```

外側の構造は OOP (Object-Oriented Programming) で整理する。

数値状態は SoA (Structure of Arrays) で保持する。

---

## OOP と SoA

### OOP

システムの責務や依存関係を整理するために使う。

例:

```python
class World:
    state: WorldState
    physics: PhysicsSystem
    sensors: SensorSystem
    evolution: EvolutionSystem
```

### SoA

大量 agent の数値データは属性ごとの配列として保持する。

```text
position_x[N]
position_y[N]
velocity_x[N]
velocity_y[N]
energy[N]
radius[N]
...
```

利点:

- NumPy で vectorize しやすい
- GPU 並列化しやすい
- memory access が規則的
- CPU -> GPU 移行が容易

基本方針:

```text
OOP for architecture
+
SoA for numerical state
```

---

## CPU reference implementation

最初は NumPy ベースで簡明に実装する。

目的:

- correctness の基準
- debugging
- unit test
- GPU implementation の regression test

CPU 実装は GPU 化後も削除しない。

---

## GPU 移行方針

段階的に置き換える。

```text
Phase 1
NumPy reference implementation

Phase 2
CuPy / NVIDIA Warp

Phase 3
profiling により bottleneck を特定

Phase 4
必要箇所のみ custom CUDA kernel
```

候補:

- PyTorch
  - neural network
  - batched tensor computation
- CuPy
  - NumPy に近い GPU array
  - population 操作
  - custom RawKernel
- NVIDIA Warp
  - geometry
  - spatial computation
  - simulation kernel
- CUDA C++ / CUDA Python
  - profiler で必要性が確認された箇所のみ

---

## Regression test

CPU と GPU で同一初期条件を使用する。

ただし floating-point 演算の違いがあるため、長時間 trajectory の完全一致は要求しない。

主に subsystem 単位で比較する。

例:

- force calculation
- integration
- collision detection
- sensor result
- neighborhood search
- mutation
- NN forward

比較:

```text
abs(cpu_value - gpu_value) < tolerance
```

長期 simulation については統計量による regression test も使用する。

---

## 運動モデル

agent body は円とする。

基本状態:

```text
position
velocity または latent velocity
orientation
energy
radius
```

運動方程式は force の和として構成する。

```text
motor
potential field
drag
collision / constraint
other environmental forces
```

概念的には:

```text
F_total =
    F_motor
  + F_potential
  + F_drag
  + F_collision
  + ...
```

---

## Numerical integrator

integrator は交換可能にする。

候補:

- Semi-Implicit Euler: default
- Euler
- RK2
- RK4

大量 agent を考慮し、通常実行では Semi-Implicit Euler を基本とする。

RK4 は精度比較や特殊な dynamics 用として残す。

---

## 最大速度

world 全体として絶対速度上限を持つ。

```text
agent_vmax <= world_vmax
```

さらに障害物最小サイズと timestep から、

```text
world_vmax * dt < safety_factor * minimum_obstacle_size
```

を満たすよう validation する。

通常の運動では速度を滑らかに bound する変換も利用できる。

例えば latent state `u` から実速度 `v` を

```text
v = u / sqrt(1 + |u|^2 / vmax^2)
```

と定義すれば、

```text
|v| < vmax
```

が常に保証される。

必要なら線形抵抗

```text
F_drag = -gamma * v
```

も併用する。

---

## 空間探索・簡易衝突判定

agent は円とする。

agent-agent の接触条件:

```text
distance(i, j) < radius_i + radius_j
```

全 pair を調べる O(N^2) は避ける。

初期実装から uniform grid / spatial hash を使用する。

```text
world
  |
  +-- cell
  |     +-- agent ids
  |
  +-- cell
        +-- agent ids
```

各 agent は自身の cell と周囲の cell のみ探索する。

この bookkeeping と実際の距離判定を分離する。

---

## 障害物

リッチな rigid-body physics engine は使用しない。

要件:

- static obstacle
- circle-agent と obstacle の接触
- penetration correction
- 最小 obstacle size を設定
- 高速性重視

障害物形状はまず以下で十分。

- circle
- line segment
- polygon

agent と line segment の場合は、円中心から線分への最近接点を求めて判定する。

CCD (Continuous Collision Detection) は初期段階では使用せず、

```text
world_vmax
dt
minimum obstacle size
```

の制約によって tunneling を防止する。

---

## Interaction と Collision の分離

物理的衝突と、生物学的 interaction は別 System として扱う。

例:

- collision
- predation
- mating
- attack
- resource harvesting
- communication

predation などは spatial query の結果を再利用する。

一定距離以内に一定時間存在した場合に成立する interaction は、active pair のみ sparse に bookkeeping する。

---

## Frontend への snapshot

simulation state 全体は送らない。

描画に必要な情報だけを送る。

例:

```text
position
orientation
radius
species/type
selected state
optional sensor/debug data
```

大量 agent の場合、JSON より binary packet を使用する。

Frontend 側では:

```text
Float32Array
Uint16Array
```

などとして受け取る。

---

## 初期ディレクトリ構成案

```text
alife/
|
+-- core/
|   +-- world.py
|   +-- state.py
|   +-- runner.py
|
+-- systems/
|   +-- environment.py
|   +-- spatial.py
|   +-- sensor.py
|   +-- brain.py
|   +-- action.py
|   +-- force.py
|   +-- physics.py
|   +-- interaction.py
|   +-- energy.py
|   +-- evolution.py
|
+-- integrators/
|   +-- semi_implicit_euler.py
|   +-- rk4.py
|
+-- backends/
|   +-- cpu/
|   +-- gpu/
|
+-- api/
|   +-- server.py
|
+-- experiments/
|
+-- tests/
|
frontend/
|
+-- src/
    +-- ui/
    +-- world/
    +-- plots/
    +-- interaction/
```

最初の目標は、CPU headless simulation が UI なしで完全に動作し、その同じ SimulationCore に frontend を接続できる状態とする。
