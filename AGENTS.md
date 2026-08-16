# AGENTS.md

## 開発方針

- 変更前に、対象コードと関連する docs を確認する。
- 最小限の変更で目的を満たし、未要求の抽象化や将来用の空実装を追加しない。
- 既存の変更を、明示的な指示なく削除・巻き戻ししない。
- 実装の意味と、実装に使用するライブラリを分離する。
- 公開API、Protocol、class、関数には型ヒントを付ける。
- コメントは実装上の理由や制約を説明する場合だけ追加し、日本語で記述する。
- frontendの挙動に影響する調整値は、重要でない表示上の固定値を除き `params/frontend_ui.yaml` に定義する。particle footprintの保持点数は `max_particle_footprint_points` で設定する。

## Prefix Rules

- 外部公開しないmodule、class、function、constant、attribute、method、typeは名前の先頭に `_` を付ける。
- 他moduleから参照される公開API、Protocol、schema、CLI entrypointはprefixを付けない。
- `__dunder__` はPythonの特殊method・特殊attributeに限定し、単なる非公開表現には使わない。
- `__name` はsubclassとの名前衝突を避けるname manglingが必要な場合に限定する。

## Commit Rules

- commit messageは日本語で記述する。
- commit messageの先頭に `update:`、`fix:`、`refactor:`、`remove:`、`test:`、`docs:`、`chore:` など変更種別のprefixを付ける。
- 1 commit 1責務とし、異なる責務の変更は複数commitへ分ける。

## 実行環境

開発環境と公開環境を分離する。

- `uv-dev` は開発依存を含む環境である。
- `uv-prod` は公開時と同じ最小依存の環境である。
- unit test、Pyright、formatter、linterは `uv-dev` で実行する。
- headless実行やserverの起動確認は `uv-prod` でも実行する。
- ホスト環境の `python`、`pytest`、`pyright` を直接使用せず、プロジェクトで定めたuv環境を使用する。
- 依存関係を追加・更新するときは、開発用と公開用のどちらに必要かを確認する。

標準的な確認コマンドは以下とする。

```text
uv-dev run pytest tests/unit
uv-dev run pytest tests/smoke
uv-dev run pyright src tests
uv-prod run run-simulation --headless
```

## ディレクトリと責務

- `src/alife/core/` は simulation の意味、state schema、tick順序、抽象契約を定義する。
- `src/alife/systems/` は環境、物理、空間探索などのSemantic / Abstract Layerを定義する。
- `src/alife/backends/numpy/` はNumPyによるConcrete Layerを実装する。
- `src/alife/runtime/` は設定からbackend、systemを組み立てる。
- `src/utils/file_io/` はmsgspecによるtyped JSON、YAML、MessagePackのI/Oを実装する。
- `src/alife/api/` はFastAPI、WebSocketなどの通信adapterと、backend stateからfrontend向けJSON messageへ変換する処理を実装する。
- `src/alife/config/` は `ProjectPaths` によるパス解決、paramsの読み込みと検証、設定schemaを定義する。
- `params/` はsimulation、headless、frontend_ui、renderの設定と全パラメータを大分類ごとのYAMLで定義する。
- `resources/` は見た目だけのアセット（sprite、テクスチャ、WebGL shader）を定義する。現時点では空とする。消費者はfrontend/とし、src/からは参照しない。
- プロジェクトとparamsのパスは `ProjectPaths` で解決し、各所で直接構築しない。
- CLIは `src/cli/` に実装し、`pyproject.toml` の `[project.scripts]` から公開する。
- `tests/unit/` は `src/` の責務に対応する単体テストを置く。
- `tests/smoke/` は設定から実行経路全体を確認するテストを置く。

## Semantic LayerとBackend

- `core/` と `systems/` からNumPy、CuPy、Warp、CUDA、PixiJSを直接importしない。
- backendはSemantic Layerの契約に依存し、Semantic Layerはbackendに依存しない。
- `SimulationCore` 内で具体的なbackendを生成しない。
- backend、runnerはfactoryまたはdependency injectionで組み立てる。
- CPUのNumPy実装はreference implementationとして保持する。
- 将来backendを追加しても、stateの意味、tick順序、実験設定、統計の意味を変更しない。
- CPUとGPUで内部アルゴリズムが異なることは許容するが、外部から観測できる意味は一致させる。
- 数値状態はSoAで保持し、particleごとのPythonオブジェクトを基本的に作らない。

## Importルール

### 記述のスタイル

- importはファイル冒頭に記述する。
- import順は、標準ライブラリ、サードパーティ、プロジェクト内モジュールの順とする。
- プロジェクト内importは、原則として `alife...` から始まる絶対importを使用する。
- `from ... import *` を使用しない。
- `sys.path` を変更してimportを通さない。
- import cycleを遅延importで隠さない。責務と依存方向を修正する。

### src/ 内の依存の方向

依存は下表の右側への片方向のみを許可する。逆方向と同層間（例: `api/` と `backends/`）のimportは禁止する。

| レイヤー | 依存してよい相手 |
| --- | --- |
| `src/cli/` | `alife.api`、`alife.runtime`、`alife.config` |
| `src/alife/api/` | `alife.runtime`、`alife.backends`、`alife.core`、`alife.config`、`utils.file_io` |
| `src/alife/runtime/` | `alife.backends`、`alife.systems`、`alife.core`、`alife.config`、`utils.file_io` |
| `src/utils/file_io/` | 標準ライブラリ、msgspec、NumPy |
| `src/alife/backends/` | `alife.systems`、`alife.core`、`alife.config` |
| `src/alife/systems/` | `alife.core`、`alife.config` |
| `src/alife/core/` | なし。標準ライブラリのみ |
| `src/alife/config/` | `utils.file_io`、標準ライブラリ、msgspec |

- `core/` と `systems/` からNumPy、CuPy、Warp、CUDA、PixiJSを直接importしない。
- NumPy、CuPy、Warp、WebSocket、FastAPI、uvicornなどの依存は、それを必要とするConcrete Layerまたはadapter（`backends/`、`api/`、`cli/`）に閉じ込める。
- 表示側はsimulation stateを変更しない。UIからの変更はcommandとしてsimulationへ渡す。

### src/ と他のディレクトリの関係

- `src/` から `tests/`、`frontend/`、開発用scriptをimportしない。
- `tests/` は `alife...` をimportしてよい。`src/` と `tests/` の依存はこの片方向のみとする。
- `frontend/` はPython側とコードを共有しない。両者の接点はWebSocketが配信するJSON messageのみとし、このschemaを変更する場合はfrontendの型定義と合わせて確認する。
- `params/` はimportするコードではなくデータである。読み取りは `alife.config` のloaderが `ProjectPaths` 経由でのみ行い、他の層はパスを直接構築しない。`resources/` の消費者はfrontend/であり、src/は参照しない。

## ConfigとParams

- YAMLを各Systemやbackendが直接読むことを禁止する。
- config loaderが設定を読み込み、検証済みの設定オブジェクトへ変換する。
- `params/` は「何を実験するか」「手法をどの値で動かすか」を完全に決定する。
- 実行形態はCLIの `--headless` で選択する。
- `params/` は `world.yaml`、`physics.yaml`、`execution.yaml`、`headless.yaml`、`frontend_ui.yaml`、`render.yaml` に分割する。
- simulationの距離、速度、時間に関係する値は `_simu`、renderingに関係する値は `_render` を名前に付ける。
- 距離の単位はworld unit、simulation時間の単位は秒とする。`dt_simu` は1 tickあたりのsimulation時間である。
- 乱数を使う全Systemは `execution.yaml` の `seed` を起点とする共通の乱数管理へ接続し、Systemごとに未seedの乱数生成器を作らない。
- `resources/` にsimulationの設定値や実験条件を置かない。
- config loaderが `ProjectPaths` 経由でparamsを読み込み、実行中にYAMLファイルを直接参照しない。
- timestep、最大速度、最小半径など数値安定性に関係する値は、実行前に検証する。

## Interactive UI

- `space` はsimulationのpause/resume、`r` は同じseedの初期状態からのrestart、`s` は現在stateの保存、`esc` は操作UIのopen/closeに割り当てる。
- `space` は操作中の要素によらずpause/resume専用とし、buttonにfocusがある場合もブラウザ既定の激活を挙動させない。
- 矢印キーとmouse dragはcameraの移動、mouse scrollはcameraのzoomに割り当てる。
- `speed_multiplier` はsimulationの実時間上の進行速度だけを変更し、`dt_simu` と `snapshot_hz_render` は変更しない。
- 操作UIはtoggleで開閉し、ボタンには対応するshortcutを併記する。
- paused / runningの状態は `⏸` / `▶` と `paused` / `running` の文字で表示する。
- 操作UIの外には `speed_multiplier`、`dt_simu`、`elapsed_average`、`snapshot_hz_render`、simulation状態、`tick`を表示する。
- `dt_required` は `dt_simu / speed_multiplier` とし、`normal` / `lagging` は `elapsed_average` と `dt_required` を比較して判定する。
- server起動直後のsimulation状態は `paused` とし、`space` で `running` に遷移する。
- 操作UIはデフォルトでopenとし、可視化windowの外側左下に配置する。panelのopen/closeは `esc` に割り当て、`space` には割り当てない。

## Checkpoint

- `state_<tick>.msgpack` は `NumpyWorldState` そのものをrender snapshotではなく、同梱された解決済みparamsと組み合わせてsimulationを継続できる完全なdynamic stateとして保存する。
- checkpointの保存対象は、読み込み後に次のsimulation stepを実行するために必要なstateを基準に決める。
- checkpointの追加・変更時は、save/load後に同じstateから継続実行できることをunit testで確認する。

## テストルール

- 新しい計算ロジックにはunit testを追加する。
- 実行profile、依存注入、CLI、WebSocketの配線を変更した場合はsmoke testを更新する。
- randomを使用するテストはseedを固定する。
- CPUの数値計算は、既知の入力と期待値を使って検証する。
- backendの実装は、Semantic Layerのcontract testで検証できるようにする。
- テストは本番コードや設定ファイルを変更しない。
- 生成物は専用の一時ディレクトリへ出力し、リポジトリ内のexperimentやparamsを上書きしない。
- 高コストなbenchmark、大量agentによる長時間実験、GPU実験は明示的な指示なく実行しない。

## Pyright

Pyrightによる型チェックを実装完了条件に含める。

- 実装終了後に `uv-dev run pyright src tests` を実行する。
- errorだけでなく、warning相当を含むすべてのdiagnosticを確認する。
- diagnosticが残っている場合は修正してから完了とする。
- `# type: ignore` で型問題を隠さない。
- 外部ライブラリのstub不足など、やむを得ない抑制には理由を記述し、対象を最小限にする。
- 型チェック対象外にすることで問題を回避しない。

## 完了条件

実装完了時には、以下をすべて満たすこと。

- 関連するunit testが成功する。
- 関連するsmoke testが成功する。
- `uv-prod` で公開用の最小実行経路が成功する。
- `uv-dev run pyright src tests` にdiagnosticがない。
- frontendを変更した場合は、`frontend/` で `npm run typecheck` を実行し、TypeScriptのdiagnosticがない。
- frontendのproduction buildが必要な変更では、`frontend/` で `npm run build` を実行する。
- 変更した責務とテストの対応を説明できる。
