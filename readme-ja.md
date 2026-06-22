# images2rHTML.py ユーザーマニュアル ![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)

[🇺🇸 English](README.md) or [🇯🇵 日本語](README-ja.md)
![Uploading プレゼンテーション1.jpg…]()

`images2rHTML.py`は、フォルダ内の複数画像を、Outline（目次）付きの**Restricted Viewer HTML**にまとめるPython CLIツールです。

作成したHTMLはブラウザだけで閲覧でき、テキスト選択、コピー、右クリック、画像ドラッグ、印刷などの一般的な操作を抑制します。元の画像は変更せず、外部のインターネットサービスとも通信しません。さらに、生成時に設定したRecovery passwordを使うと、[MD//WORKS](https://github.com/HKJPN/markdown-editor)で元のMarkdownを復元し、見出しの修正、画像の追加・削除、文章の追記などを再び行えます。
