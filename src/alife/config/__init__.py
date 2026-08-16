"""プロジェクトのパス解決、paramsの読み込みと検証、設定schemaを定義する。

責務: 検証済みの設定objectを他層へ渡す。
依存: utils.file_io、標準ライブラリ、msgspec。
core/、backends/、runtime/、api/、cli/ から依存される。
"""
