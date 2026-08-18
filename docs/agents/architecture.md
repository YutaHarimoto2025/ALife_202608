# Architecture規定

## ディレクトリの責務

- src/alife/core/ はsimulationの意味、state schema、tick順序、抽象契約を定義する。
- src/alife/backends/numpy/ はNumPyによるreference implementationを実装する。
- src/alife/runtime/ は設定からbackendとrunnerを組み立てる。
- src/alife/api/ はFastAPI、WebSocket、frontend向けmessage変換を担う。
- src/alife/config/ は `ProjectPaths` 、paramsの読み込みと検証、設定schemaを定義する。
- src/utils/file_io/ はmsgspecによるtyped JSON、YAML、MessagePack I/Oを実装する。
- src/cli/ はCLI entrypointを実装し、 pyproject.toml の `[project.scripts]` から公開する。
- tests/unit/ は単体テスト、 tests/smoke/ は設定から実行経路全体を確認するテストを置く。

## 依存

- Semantic Layerはbackendに依存しない。 `SimulationCore` 内で具体的なbackendを生成せず、factoryまたはdependency injectionで組み立てる。
- CPUのNumPy実装はreference implementationとして保持する。将来backendを追加しても、外部から観測できるstateの意味、tick順序、実験設定、統計の意味を変更しない。
- 数値状態はSoAで保持し、particleごとのPython objectを基本的に作らない。
- `core/` からNumPy、CuPy、Warp、CUDA、PixiJSを直接importしない。
- src/ は tests/、 frontend/、開発用scriptをimportしない。frontendとPython側はコードを共有しない。
- CLIは `alife.api`、 `alife.runtime`、 `alife.config` を利用できる。NumPy stateの型注釈はCLIで許可する例外とする。
- APIはruntime、backend、core、config、file I/Oを利用できる。runtimeはbackend、core、config、file I/Oを利用できる。backendはcoreとconfigを利用できる。configはfile I/O、標準library、msgspecを利用できる。

## Import記法

- importはファイル冒頭に記述し、標準library、third-party、project内moduleの順に置く。
- project内importは原則として `alife...` から始まる絶対importを使用する。
- `from ... import *` と `sys.path` の変更を使用しない。
- 遅延importでcycleを隠さず、責務または依存方向を修正する。
