# AGENTS.md

## リポジトリ概要

このリポジトリは、PythonのNumPy reference implementationで2D粒子simulationを実行し、FastAPI/WebSocketとReact/PixiJS frontendで可視化するartificial-life sandboxです。headless実行、run_resultsへのcheckpoint保存、設定YAMLによる再現可能な実行を提供します。

将来はsensor、brain、action、evolution、environment interactionを追加し、CPU referenceとの互換性を保ちながらGPU backendとtransportを拡張します。確定していない内容は docs/open/ を参照し、実装規定として扱いません。

## 中核方針

- 変更前に対象コードと関連文書を確認する。
- 最小限の変更で目的を満たし、未要求の抽象化や将来用の空実装を追加しない。
- 既存の変更を、明示的な指示なく削除・巻き戻ししない。
- 参照先の指示ファイル内に、さらに現在のタスクに関係するファイル参照がある場合は、必要に応じて再帰的に Read してください。

## 文書の正本

- docs/agents/ は確定した開発規定の正本とする。
- docs/open/ は未解決事項のたたき台であり、内容を正本として扱わない。
- 解決済みの重要事項は docs/agents/ へ整理し、必要な場合だけ本ファイルから参照する。

PythonコードまたはPythonテストを変更する場合は、変更前に以下の指示を読んでください。
@docs/agents/python.md

 src/ の責務、依存、importを変更する場合は、変更前に以下の指示を読んでください。
@docs/agents/architecture.md

params、設定loader、実行設定を変更する場合は、変更前に以下の指示を読んでください。
@docs/agents/configuration.md

frontendまたはWebSocketのUI連携を変更する場合は、変更前に以下の指示を読んでください。
@docs/agents/frontend.md

checkpointまたはrun_resultsを変更する場合は、変更前に以下の指示を読んでください。
@docs/agents/checkpoint.md

テスト、型検査、実行確認を追加または変更する場合は、変更前に以下の指示を読んでください。
@docs/agents/verification.md

commitを作成する場合は、変更前に以下の指示を読んでください。
@docs/agents/commit.md
