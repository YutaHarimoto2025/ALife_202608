# Frontend規定

## UIとsimulation

- 表示側はsimulation stateを変更しない。UIからの変更はWebSocket commandとしてsimulationへ渡す。
- `space` は操作中の要素によらずpause/resume専用とし、browser既定のbutton激活やinputへの空白入力を行わせない。
- `r` は同じseedの初期状態からrestart、 `s` は現在stateの保存、 `esc` は操作UIのopen / closeに割り当てる。
- 矢印キーとmouse dragはcamera移動、mouse scrollはcamera zoomに割り当てる。
- `speed_multiplier` は実時間上の進行速度だけを変更し、 `dt_simu` と `snapshot_hz_render` は変更しない。
- server起動直後のsimulation状態は `paused` とする。

## 表示

- 操作UIはtoggleで開閉し、buttonには対応するshortcutを併記する。
- `paused` / `running` は `⏸` / `▶` と状態文字を併記する。
- 操作UIの外に `speed_multiplier`、 `dt_simu`、 `elapsed_average`、 `snapshot_hz_render`、simulation状態、tickを表示する。
- `dt_required` は `dt_simu / speed_multiplier` とし、 `normal` / `lagging` は `elapsed_average` と `dt_required` の比較で判定する。
- UIは暗色と灰白色を基本とし、色は意味を持つ情報だけに用いる。performanceの色表示は文字も併記する。
