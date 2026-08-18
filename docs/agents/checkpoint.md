# Checkpoint規定

- state_<tick>.msgpack はrender snapshotではなく、次のsimulation stepを実行できる完全なdynamic stateとして保存する。
- checkpointは同じrun directoryに保存した解決済みparamsと組み合わせて継続する。
- checkpointの保存形式または対象を変更した場合、save/load後に同じstateから継続実行できることをunit testで確認する。
