# 普段の運用

## Backendの起動

プロジェクトルートでAPI付きの実行を開始します。

```bash
uv-prod run run-simulation
```

既定では `127.0.0.1:8000` でFastAPIとWebSocketを起動します。hostとportは次のように指定できます。

```bash
uv-prod run run-simulation --host 0.0.0.0 --port 8000
```

run_resultsを作成しない場合は、`--no-run-results` を指定します。

```bash
uv-prod run run-simulation --no-run-results
```

headless実行では、 params/headless.yaml の `ticks_simu` 回だけsimulationを進めて終了します。 `save_ticks_simu` のtickでstateを保存し、`null` なら保存しません。

```bash
uv-prod run run-simulation --headless
```

## Frontendの起動

Backendを起動したまま、別のターミナルでfrontendを起動します。

```bash
cd frontend
npm run dev
```

Viteが表示するURLをブラウザで開きます。通常は `http://localhost:5173` です。frontendは既定で `ws://127.0.0.1:8000/ws` へ接続します。接続先を変える場合は `VITE_ALIFE_WS_URL` を指定します。

```bash
VITE_ALIFE_WS_URL=ws://192.168.1.10:8000/ws npm run dev
```

## 操作

- `space`: pause / resume
- `r`: 同じseedの初期状態からrestart
- `s`: 現在stateを保存
- `esc`: 操作UIのopen / close
- 矢印キーまたはmouse drag: camera移動
- mouse scroll: camera zoom

server起動直後のsimulationは `paused` です。状態表示では `speed_multiplier`、`dt_simu`、`elapsed_average`、`snapshot_hz_render`、状態、tickを確認できます。`speed_multiplier` は実時間上の進行速度だけを変更し、`dt_simu` と `snapshot_hz_render` は変更しません。

## パラメータ変更

起動前に params/ のYAMLを編集します。変更後はbackendを再起動してください。実行中のYAML変更は反映されません。

| ファイル | 内容 |
| --- | --- |
| world.yaml | worldサイズ、粒子数、粒子半径、初期速度 |
| physics.yaml | timestep、最大速度、drag、粒子間反発、壁反射 |
| execution.yaml | seed、compute backend |
| headless.yaml | headlessのtick数と保存tick |
| frontend_ui.yaml | speed、camera、wall、particle footprintの表示設定 |
| render.yaml | snapshot配信頻度 |

距離の単位はworld unit、simulation時間の単位は秒です。`dt_simu` は1 tickあたりのsimulation時間です。

## 実行結果

simulation開始時またはrestart時に run_results/<run_id>/ を作成します。そこにはmetadata、解決済みparams、保存した state_<tick>.msgpack を格納します。checkpointは同じrun directory内のparamsと組み合わせてsimulationを継続できます。

`--no-run-results` を指定した場合、run directoryを作成せず、Saveは利用できません。

## 接続確認

Backendが起動しているかはhealth endpointで確認します。

```bash
curl http://127.0.0.1:8000/health
```

`{"status":"ok"}` が返ればHTTP接続は正常です。frontendが接続できない場合は、backendのhost/portと `VITE_ALIFE_WS_URL` が一致しているかを確認してください。
