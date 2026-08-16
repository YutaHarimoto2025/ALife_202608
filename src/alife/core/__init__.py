"""simulationの意味、state schema、tick順序、抽象契約を定義する。

責務: backendに依存しないsemantic layer。
依存: プロジェクト内moduleには依存せず、標準ライブラリのみ使用する。
backends/、runtime/、api/ から依存される最下層。
"""
