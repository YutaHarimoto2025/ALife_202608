# 公開版・高速版を互換にする抽象化設計

## 目的

同じ artificial-life simulation を、

- 公開しやすい CPU / Web 版
- CUDA を使う高速版
- headless 実験版

で共通利用できるようにする。

重要なのは、simulation の「意味」と「実行場所」を分離することである。

基本思想:

```text
Semantic Layer
    「何をするか」を定義

Implementation Layer
    「どう実行するか」を定義
```

例えば、

```text
PhysicsSystem
    「agent に力を加えて時間発展させる」

CpuPhysicsBackend
    NumPy で実装

CudaPhysicsBackend
    CUDA / CuPy / Warp で実装
```

という関係にする。

---

## 2 レイヤー構造

### Layer 1: Semantic / Abstract Layer

用途や hardware に依存しない意味論を定義する。

例:

- SimulationCore
- PhysicsSystem
- SensorSystem
- BrainSystem
- InteractionSystem
- EvolutionSystem
- Renderer
- ComputeBackend

この層では、

- simulation tick の順序
- state の意味
- force の意味
- sensor の意味
- action の意味
- reproduction / death の意味
- renderer に渡す情報

などを規定する。

「CPU でどう計算するか」「CUDA kernel をどう書くか」はここに含めない。

### Layer 2: Concrete / Backend Layer

Layer 1 の interface を、用途や library に応じて具体実装する。

例:

```text
ComputeBackend
    |
    +-- NumPyBackend
    +-- CuPyBackend
    +-- WarpBackend
    +-- CustomCudaBackend
```

```text
Renderer
    |
    +-- WebRenderer
    |     +-- PixiJS / WebGL
    |
    +-- NativeRenderer
          +-- OpenGL / Vulkan
          +-- CUDA interop
```

同じ abstract interface に複数の implementation option を持たせる。

---

## SimulationCore の役割

SimulationCore は simulation の意味論と実行フローを保持する。

例えば 1 tick を、

```text
1. environment update
2. spatial indexing
3. sensing
4. brain forward
5. action decode
6. force generation
7. integration
8. collision resolution
9. interaction
10. energy update
11. death / reproduction
12. evolution
13. statistics
```

として定義する。

概念的には:

```python
class SimulationCore:
    def step(self, dt: float) -> None:
        self.environment.update(self.state, dt)
        self.spatial.update(self.state)

        observations = self.sensors.observe(
            self.state,
            self.spatial,
        )

        actions = self.brain.forward(
            observations,
            self.state,
        )

        forces = self.action_system.to_forces(
            actions,
            self.state,
        )

        self.physics.step(
            self.state,
            forces,
            dt,
        )

        self.interactions.resolve(
            self.state,
            self.spatial,
            dt,
        )

        self.evolution.update(
            self.state,
            dt,
        )
```

ここには NumPy や CUDA 固有のコードを書かない。

---

## Backend の粒度

すべてを 1 個の巨大な `CpuBackend` / `CudaBackend` にする必要はない。

むしろ subsystem ごとに interface を持たせる方が柔軟である。

例:

```text
SpatialBackend
PhysicsBackend
SensorBackend
BrainBackend
EvolutionBackend
```

これにより、

```text
Physics      CUDA
Sensors      CUDA
Brain        PyTorch
Evolution    CPU
Statistics   CPU
```

のような混成構成も可能になる。

初期段階では実装を簡潔にするため、

```text
ComputeBackend
```

にまとめてもよい。

規模が大きくなったら subsystem ごとに分割する。

---

## State の共通化

公開版と高速版で互換性を保つため、最重要なのは state schema を共通化することである。

例:

```text
AgentState
    position[N, 2]
    velocity[N, 2]
    energy[N]
    radius[N]
    orientation[N]
    species[N]
    alive[N]
```

意味論としては同一にする。

ただし実体は異なってよい。

```text
CPU
    NumPy ndarray

GPU
    CuPy ndarray
    Warp array
    CUDA device pointer
```

つまり、

```text
same logical state
different storage backend
```

とする。

---

## Array Backend Abstraction

CPU / GPU をまたぐ場合、配列操作の backend abstraction を用意するとよい。

概念:

```python
class ArrayBackend:
    def zeros(self, shape, dtype):
        ...

    def empty(self, shape, dtype):
        ...

    def asarray(self, data, dtype=None):
        ...

    def synchronize(self) -> None:
        ...
```

具体実装:

```text
NumPyArrayBackend
CuPyArrayBackend
WarpArrayBackend
```

ただし NumPy API を完全に模倣する巨大 abstraction は避ける。

simulation が実際に必要とする操作だけを interface にする。

---

## CPU Reference Backend

CPU 実装は correctness の基準として保持する。

```text
Semantic Layer
      |
      +-- NumPy reference
      |
      +-- CUDA optimized
```

同一の初期条件に対して、

```text
sensor output
force
integration
collision
interaction
mutation
```

などを比較する。

浮動小数点演算の違いがあるため、bitwise equality ではなく tolerance を使用する。

```text
abs(cpu - gpu) < epsilon
```

長時間 simulation の trajectory 完全一致は要求しない。

---

## 公開版

公開版では hardware requirement を最小限にする。

想定構成:

```text
Browser
    React
    PixiJS / WebGL
        |
        | WebSocket
        v
FastAPI
        |
        v
SimulationCore
        |
        v
NumPy / CPU Backend
```

特徴:

- GPU 必須にしない
- 一般的な Linux VM / container で実行可能
- deployment が容易
- 無料または低価格 hosting を利用しやすい
- 最大 agent 数や simulation rate は制限可能

公開版では rendering 用 snapshot を一定周期で frontend に送る。

```text
SimulationState
      |
      | extract
      v
RenderSnapshot
      |
      | WebSocket
      v
PixiJS / WebGL
```

---

## 高速版

高速版では GPU 内で simulation と rendering をできるだけ完結させる。

想定構成:

```text
SimulationCore
      |
      v
CudaBackend
      |
      v
GPU Simulation State
      |
      | CUDA graphics interop
      v
OpenGL / Vulkan
```

理想的には、

```text
VRAM
+--------------------------+
| positions                |
| velocities               |
| radius                   |
| render attributes        |
+--------------------------+
       ^             |
       |             v
     CUDA        OpenGL/Vulkan
```

という形で、CPU <-> GPU 転送を最小化する。

---

## Web 版と Native 版で共通にするもの

以下は共通にする。

- world semantics
- agent state schema
- sensor definitions
- action definitions
- physics equations
- interaction rules
- reproduction rules
- genome definition
- simulation tick order
- experiment configuration format
- statistics definitions

つまり、

```text
同じ世界
同じルール
同じ実験
```

を異なる backend で実行する。

---

## Web 版と Native 版で異なるもの

異なるのは主に以下。

```text
Compute backend
    CPU / NumPy
    CUDA

Rendering backend
    PixiJS / WebGL
    OpenGL / Vulkan

State transport
    WebSocket snapshot
    VRAM direct access / interop

Performance profile
    compatibility oriented
    throughput oriented
```

---

## RenderState の抽象化

simulation state 全体を renderer に公開しない。

renderer に必要な情報だけを抽出した semantic view を定義する。

例:

```text
RenderState
    position
    orientation
    radius
    color / species
    alive
    optional debug attributes
```

interface:

```python
class Renderer:
    def render(self, state: "RenderState") -> None:
        ...
```

Web 版:

```text
SimulationState
    |
    v
RenderSnapshot
    |
    v
binary WebSocket
    |
    v
PixiJS
```

Native 高速版:

```text
GPU SimulationState
    |
    v
shared render buffer
    |
    v
OpenGL / Vulkan
```

描画内容は意味論的に同じだが、データ経路が異なる。

---

## Renderer の交換

```text
Renderer
    |
    +-- NullRenderer
    |
    +-- WebRenderer
    |
    +-- NativeInteropRenderer
```

### NullRenderer

headless 実験用。

```text
SimulationCore
    |
    v
ComputeBackend

rendererなし
```

### WebRenderer

公開 / interactive 用。

```text
RenderState
    |
    v
snapshot serialization
    |
    v
WebSocket
    |
    v
PixiJS / WebGL
```

### NativeInteropRenderer

最大性能用。

```text
GPU state
    |
    v
CUDA interop
    |
    v
OpenGL / Vulkan
```

---

## 実行 profile

backendはconfigurationで切り替え、headlessかどうかはCLIで選択する。

例:

```yaml
execution:
  compute_backend: numpy
```

```yaml
execution:
  compute_backend: cuda
```

```text
run-simulation
run-simulation --headless
```

想定 profile:

```text
1. CPU headless

SimulationCore
    + NumPyBackend
    + NullRenderer


2. Web interactive

SimulationCore
    + NumPyBackend
    + WebRenderer


3. GPU headless

SimulationCore
    + CudaBackend
    + NullRenderer


4. Native high-performance

SimulationCore
    + CudaBackend
    + NativeInteropRenderer
```

---

## Dependency Injection

SimulationCore の内部で具体 backend を直接生成しない。

避ける:

```python
class SimulationCore:
    def __init__(self):
        self.physics = NumPyPhysics()
```

代わりに外部から注入する。

```python
class SimulationCore:
    def __init__(
        self,
        physics: "PhysicsSystem",
        sensors: "SensorSystem",
        brain: "BrainSystem",
        renderer: "Renderer",
    ) -> None:
        self.physics = physics
        self.sensors = sensors
        self.brain = brain
        self.renderer = renderer
```

起動時に用途に応じた具体実装を選択する。

```text
config
  |
  v
BackendFactory
  |
  +-- NumPyPhysics
  +-- CudaPhysics
  +-- WebRenderer
  +-- NativeRenderer
```

この方式により SimulationCore は deployment target を知らなくてよい。

---

## Library 依存の隔離

外部 library は concrete implementation の内部に閉じ込める。

例えば:

```text
core/
    simulation.py
    interfaces.py
    state_schema.py

backends/
    cpu/
        numpy_physics.py
        numpy_spatial.py

    cuda/
        cupy_physics.py
        warp_spatial.py
        kernels/

renderers/
    web/
        snapshot.py

    native/
        opengl_interop.py
```

`core/` から `numpy`, `cupy`, `warp`, `OpenGL` を直接 import しないことを基本とする。

---

## ディレクトリ構成例

```text
alife/
|
+-- core/
|   +-- simulation.py
|   +-- world.py
|   +-- state.py
|   +-- interfaces.py
|
+-- systems/
|   +-- physics.py
|   +-- sensors.py
|   +-- brain.py
|   +-- interaction.py
|   +-- evolution.py
|
+-- backends/
|   |
|   +-- cpu/
|   |   +-- numpy_physics.py
|   |   +-- numpy_spatial.py
|   |   +-- numpy_sensors.py
|   |
|   +-- cuda/
|       +-- cuda_physics.py
|       +-- cuda_spatial.py
|       +-- cuda_sensors.py
|       +-- kernels/
|
+-- renderers/
|   +-- null.py
|   +-- web.py
|   +-- native.py
|
+-- api/
|   +-- server.py
|
+-- config/
|   +-- profiles.py
|
+-- tests/
    +-- reference/
    +-- regression/
```

---

## 設計上の重要なルール

### 1. Semantic interface を library API に合わせすぎない

例えば interface を、

```text
cupy.ndarray を受け取る
```

とは定義しない。

代わりに、

```text
AgentState の position を更新する
```

という意味で定義する。

library は implementation detail とする。

### 2. GPU 用に interface を細かくしすぎない

GPU では kernel launch 自体に overhead がある。

そのため、

```text
calculate_force()
integrate_velocity()
integrate_position()
```

を別々に呼ぶより、

```text
physics.step()
```

の内部で fusion した方が高速になる場合がある。

Semantic Layer は backend が内部最適化できる粒度を残す。

### 3. CPU と GPU で同じアルゴリズムを強制しすぎない

同じ意味論を保てば、内部アルゴリズムは異なってよい。

例:

```text
CPU spatial search
    dictionary based uniform grid

GPU spatial search
    sorted cell index + prefix sum
```

結果として同じ neighborhood relation を返せばよい。

つまり、

```text
same semantics
not necessarily same implementation
```

とする。

### 4. Rendering と Simulation を分離する

renderer が simulation state を変更してはいけない。

```text
Simulation
    -> RenderState
    -> Renderer
```

の一方向とする。

UI から simulation を変更する場合は command として戻す。

```text
UI
  |
  v
SimulationCommand
  |
  v
SimulationCore
```

---

## 全体像

```text
                         Experiment Config
                                |
                                v
                         Backend Factory
                                |
                  +-------------+-------------+
                  |                           |
                  v                           v
          Semantic Layer              Concrete Layer
                  |                           |
                  |                 +---------+---------+
                  |                 |                   |
                  |              CPU/Web           CUDA/Native
                  |                 |                   |
                  v                 v                   v
            SimulationCore     NumPyBackend        CudaBackend
                  |                 |                   |
                  |                 |                   |
                  +-----------------+-------------------+
                                |
                           World State
                                |
                +---------------+---------------+
                |                               |
                v                               v
          WebRenderer                  NativeInteropRenderer
                |                               |
         PixiJS / WebGL                 OpenGL / Vulkan
                |                               |
                v                               v
             Browser                           GPU
```

---

## 要約

設計上は、

```text
「何を意味するか」
        +
「どう実装するか」
```

を分ける。

より具体的には、

```text
Semantic / Abstract Layer
    SimulationCore
    PhysicsSystem
    SensorSystem
    BrainSystem
    Renderer
    State schema

Concrete / Backend Layer
    NumPy
    CuPy
    Warp
    custom CUDA
    PixiJS / WebGL
    OpenGL / Vulkan
```

とする。

公開版と高速版は、

```text
同じ SimulationCore
同じ state semantics
同じ experiment definition
```

を使い、

```text
compute backend
renderer backend
state transport
```

だけを交換する。

この構造により、

- 公開版は CPU-only で安価に deployment
- ローカル高速版は CUDA を利用
- headless 実験では renderer を完全に除去
- CPU reference implementation を regression test に利用
- 将来的な backend 追加

を同じコードベースで維持できる。
