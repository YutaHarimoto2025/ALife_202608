# Python実装規定

## 公開範囲

- 公開API、Protocol、class、関数には型ヒントを付ける。
- 外部公開しないmodule、class、function、constant、attribute、method、typeには `_` prefixを付ける。
- 他moduleから参照される公開API、Protocol、schema、CLI entrypointには `_` prefixを付けない。
- `__dunder__` はPythonの特殊method・特殊attributeだけに使用する。
- `__name` はsubclassとの名前衝突を避ける必要がある場合だけに使用する。

## 記述

- コメントは実装上の理由や制約を説明する場合だけに追加し、日本語で記述する。
- 実装の意味と、実装に使用するlibraryを分離する。
