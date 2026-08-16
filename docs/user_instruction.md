# User Instruction

## 概要

このプロジェクトは、Python backendで2D粒子simulationを実行し、必要に応じてReact + PixiJS frontendで表示します。

simulation時間とrendering時間は分離されています。

- simulationは `dt_simu` に従って進みます。
- renderingは `snapshot_hz_render` に従ってsnapshotを受け取ります。
- `speed_multiplier` はsimulationの実時間上の進行速度だけを変更します。
- `dt_simu` と `snapshot_hz_render` は `speed_multiplier` を変更しても変わりません。
- `dt_required` は `dt_simu / speed_multiplier` です。

## Backendの起動

プロジェクトルートで実行します。

### API付きで起動

```bash
uv-prod run run-simulation
```

デフォルトでは `127.0.0.1:8000` でFastAPIとWebSocketを起動します。

主なオプション:

```bash
uv-prod run run-simulation --host 0.0.0.0 --port 8000
```

run_resultsを作成せずに実行する場合:

```bash
uv-prod run run-simulation --no-run-results
```

### Headlessで起動

```bash
uv-prod run run-simulation --headless
```

headless実行ではAPIやfrontendを起動せず、 params/headless.yaml  の `ticks_simu` 回simulationを進めて終了します。`save_ticks_simu` に指定したtickでstateを保存します。`null` の場合はstate fileを保存しません。

開発環境では `uv-prod` の代わりに `uv-dev` を使用できます。

```bash
uv-dev run run-simulation
uv-dev run run-simulation --headless
```

## Frontendの起動

Backendを起動したまま、別のターミナルでfrontendを起動します。

```bash
cd frontend
npm install
npm run dev
```

Viteが表示するURLをブラウザで開きます。通常は次のURLです。

```text
http://localhost:5173
```

frontendは起動時に次のWebSocketへ自動接続します。

```text
ws://127.0.0.1:8000/ws
```

接続先を変更する場合は `VITE_ALIFE_WS_URL` を指定します。

```bash
VITE_ALIFE_WS_URL=ws://192.168.1.10:8000/ws npm run dev
```

## UIの操作

- ページを開くとWebSocketへ自動接続します。
- server起動直後は `paused` で、`space` を押すと `running` になります。
- simulationの情報と接続状態はfullscreen viewの左上に表示されます。
- `speed_multiplier`、`dt_simu`、`elapsed_average`、`snapshot_hz_render`、simulation状態、`tick` が常時表示されます。
- `dt_simu`、`elapsed_average`、`dt_required`、`normal` / `lagging` は同じ行に表示します。判定は `elapsed_average` と `dt_required` の比較です。
- `normal` は青、`lagging` は赤で表示しますが、判定文字も併記します。
- 粒子はブラウザviewport全体を使うfullscreen canvasに表示されます。
- ページを閉じるとWebSocket接続が切断されます。

操作UIを開くと、以下の操作をボタンから実行できます。

consoleはデフォルトでopenで、fullscreen viewの右上に配置されます。open/closeはconsole直下のボタンまたは`esc`で切り替えます。

- `▶ Start (space)` / `⏸ Pause (space)`
- `Restart (r)`
- `Save (s)`
- camera panの方向パッド（矢印キー、ホールド対応）
- `ResetView`
- `speed_multiplier` log sliderとfloat入力

キーボードとmouseによる操作:

- `space`: pause / resume（buttonにfocusがある場合も常にpause / resume）
- `esc`: 操作UIのopen / close
- `r`: 同じseedの初期状態からsimulationを再実行し、新しいrun IDを作成
- `s`: 現在stateを `run_results/` に保存
- 矢印キー、方向パッド、mouse drag: camera移動。矢印キーと方向パッドはホールド中に連続移動します。
- mouse scroll: camera zoom

## パラメータ変更

起動前に params/ のYAMLを編集します。

- params/world.yaml
  - ワールドサイズ、粒子数、粒子半径、初期速度
- params/physics.yaml
  - timestep、最大速度、drag、粒子間反発、壁反射
- params/execution.yaml
  - seed、compute backend
- params/headless.yaml
  - headlessのsimulation tick数
  - headlessでstateを保存するtickのリスト。`null`も指定可能
- params/frontend_ui.yaml
  - speed multiplierの初期値、最小値、最大値、step
  - elapsed averageのwindowサイズ
  - camera、wall、particle footprintの表示設定と保持点数
- params/render.yaml
  - snapshot配信頻度

statusには `snapshot_hz_render` の設定値（set）と、実際のsnapshot配信頻度（real）を表示します。

UI設定は params/frontend_ui.yaml に集約しています。frontendはこのYAMLをbuild時に直接読み込みます。現在のspeed sliderは `min: 0.01`、`max: 100.0`、`step: 0.01` です。

距離はworld unit、simulation時間は秒です。例えば `dt_simu: 0.01` は1 tickあたり0.01秒を意味します。

設定変更後はbackendを再起動してください。実行中にYAMLを変更しても、現在のsimulationには反映されません。

## 実行結果の保存

simulationが `running` になったとき、または `r` でrestartしたときに、aisin案件と同じ形式の local timestamp（例: `20260813_230750`）をもとにしたrun directoryが作成されます。同じ秒に作成された場合は `_2` 以降のsuffixを付けます。

```text
run_results/<run_id>/
  metadata.json
  params/
    world.yaml
    physics.yaml
    execution.yaml
    headless.yaml
    frontend_ui.yaml
    render.yaml
  state_<tick>.msgpack
```

`metadata.json` にはrun ID、実行日時、実行時のgit commit hash、`headless`、CLIの`--description`を保存します。pauseやspeed multiplierなどのuser inputは保存しません。

実験の説明をmetadataに付ける場合は `run-simulation --headless --description "説明"` のように指定します。server実行でも同じオプションを指定できます。

`state_<tick>.msgpack` は、そのtickのdynamic state全体を保存したcheckpointです。checkpointと同じrun directoryの解決済みparamsを使うことで、次のsimulation stepから継続できます。

`--no-run-results` を指定した場合はrun directoryを作成しないため、`Save (s)` は利用できません。

## 接続できない場合

backendとfrontendは別のポートを使用します。

- `127.0.0.1:8000`: FastAPIのHTTPとWebSocket
- `localhost:5173`: Viteのfrontend開発サーバー

まずbackendが起動しているターミナルとは別のターミナルで、health endpointを確認します。

```bash
curl http://127.0.0.1:8000/health
```

次のレスポンスが返れば、FastAPIへのHTTP接続は正常です。

```json
{"status":"ok"}
```

次にブラウザで `http://localhost:5173/` を開きます。frontendは起動時に `ws://127.0.0.1:8000/ws` へWebSocket接続し、simulation snapshotを受信します。

1. `curl http://127.0.0.1:8000/health` が成功することを確認します。
2. frontendの `VITE_ALIFE_WS_URL` とbackendのhost / portが一致していることを確認します。
3. ブラウザのdeveloper consoleにWebSocketエラーがないか確認します。
4. backendを再起動してからfrontendを再読み込みします。

## Frontendの確認

frontendの型チェックとproduction buildは frontend/ で実行します。

```bash
npm run typecheck
npm run build
```
