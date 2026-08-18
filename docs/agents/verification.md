# Verification規定

## テスト

- 新しい計算ロジックにはunit testを追加する。
- 実行profile、dependency injection、CLI、WebSocketの配線を変更した場合はsmoke testを更新する。
- randomを使用するtestはseedを固定する。CPU数値計算は既知の入力と期待値で検証する。
- testは本番コードや設定ファイルを変更しない。生成物は専用の一時directoryへ出力し、repository内のexperimentやparamsを上書きしない。
- 高コストなbenchmark、大量agentによる長時間実験、GPU実験は明示的な指示なく実行しない。

## 実行環境

- `uv-dev` は開発依存を含み、unit test、Pyright、formatter、linterに使用する。
- `uv-prod` は公開用の最小依存であり、headless実行とserver起動確認に使用する。
- host環境の `python`、 `pytest`、 `pyright` を直接使用しない。依存関係を変更する場合は開発用と公開用の必要性を確認する。

```text
uv-dev run pytest tests/unit
uv-dev run pytest tests/smoke
uv-dev run pyright src tests
uv-prod run run-simulation --headless
```

## 型検査と完了条件

- Pyrightの設定は pyrightconfig.json のstrict modeに統一する。型問題を `# type: ignore` や対象外指定で隠さない。
- 外部libraryのstub不足を抑制する場合は理由を記述し、対象を最小限にする。testでは `reportPrivateUsage` だけを無効にできる。
- 実装完了時は関連するunit test、smoke test、Pyright、公開用最小実行経路を確認する。
- frontendを変更した場合は frontend/ で `npm run typecheck` を実行する。production buildに影響する変更では `npm run build` も実行する。
