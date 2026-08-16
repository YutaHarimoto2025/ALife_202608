# User Instruction

## 概要

このプロジェクトは、Python backendで2D粒子simulationを実行し、必要に応じてReact + PixiJS frontendで表示します。

simulation時間とrendering時間は分離されています。

- simulationは `dt_simu` に従って進みます。
- renderingは `snapshot_hz_render` に従ってsnapshotを受け取ります。
- renderingのFPSや表示速度を変更しても、simulationの `max_speed_simu` は変わりません。

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

### Headlessで起動

```bash
uv-prod run run-simulation --headless
```

headless実行ではAPIやfrontendを起動せず、 params/headless.yaml  の `ticks_simu` 回simulationを進めて終了します。

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

現在のUIにはsimulationを操作するボタンやフォームはありません。

- ページを開くとWebSocketへ自動接続します。
- 接続状態が画面右上に表示されます。
- 現在のsimulation tickが画面右上に表示されます。
- 粒子は中央のcanvasに表示されます。
- ブラウザの表示幅に合わせてcanvasは縮小表示されます。
- ページを閉じるとWebSocket接続が切断されます。

現在利用できない操作:

- pause / resume
- simulationのreset
- simulation速度の変更
- パラメータのUI編集
- 粒子の選択・詳細表示
- カメラのzoom / pan

これらは今後の拡張対象です。

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
- params/render.yaml
  - snapshot配信頻度

距離はworld unit、simulation時間は秒です。例えば `dt_simu: 0.01` は1 tickあたり0.01秒を意味します。

設定変更後はbackendを再起動してください。実行中にYAMLを変更しても、現在のsimulationには反映されません。

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
