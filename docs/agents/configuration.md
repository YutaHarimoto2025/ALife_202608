# Configuration規定

## Paramsの読み込み

- YAMLはconfig loaderだけが読み、検証済みの設定objectへ変換する。
- 本番の実行経路は `ProjectPaths` 経由でparamsを解決する。testは一時params用に `ParamsPaths` を直接構築できる。
- frontendはbuild時に params/frontend_ui.yaml を直接読む例外とする。Python側とfrontendの通信はWebSocket JSON messageを使用する。
- params/ は world.yaml、 physics.yaml、 execution.yaml、 headless.yaml、 frontend_ui.yaml、 render.yaml に分割する。
- 実行形態はCLIの `--headless` で選択する。

## 値の意味

- simulationの距離、速度、時間に関係する値は `_simu`、renderingに関係する値は `_render` を名前に付ける。
- 距離の単位はworld unit、simulation時間の単位は秒とする。 `dt_simu` は1 tickあたりのsimulation時間である。
- 乱数を使うSystemは execution.yaml の `seed` を起点とする共通の乱数管理へ接続し、未seedの乱数生成器を作らない。
- frontendの挙動に影響する調整値は、重要でない表示上の固定値を除き params/frontend_ui.yaml に定義する。particle footprintの保持点数は `max_particle_footprint_points` で設定する。
- resources/ にsimulation設定値や実験条件を置かない。
- timestep、最大速度、最小半径など数値安定性に関係する値は実行前に検証する。
