# 初回の環境構築

## 必要なソフトウェア

- Python 3.12以上
- uv
- Node.jsとnpm

## Python環境

プロジェクトルートで開発用と公開用の環境を作成します。

```bash
uv-dev sync
uv-prod sync
```

`uv-dev` はtest、Pyright、formatter、linterを含みます。`uv-prod` は公開用の最小依存だけを含みます。

## Frontend環境

```bash
cd frontend
npm install
```

以後の起動と操作は docs/user_instruction.md を参照してください。
