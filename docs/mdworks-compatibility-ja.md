# MD//WORKS 互換性に関する注意事項

本書は、`docs/restricted-viewer-format-v1.md` から抽出された、互換性において重要な要件をまとめたものです。なお、ソースの仕様書が引き続き正式なものとなります。

## 対象

* **フォーマット識別子:** `mdworks-restricted-viewer`
* **フォーマットバージョン:** `1`
* **初期リーダー対象:** MD//WORKS v1.5.7
* **`images2rHTML.py` ターゲットプロファイル:** 完全な制限付きビューアジェネレーター (Full Restricted Viewer Generator) および単一ファイル制限付きビューアジェネレーター (Single-File Restricted Viewer Generator)

## HTML コンテナ

* HTMLファイルはUTF-8であり、`<meta charset="utf-8">` を含める必要があります。
* 制限付きビューアの JSON は、以下の属性を持つ正確に1つの `<script>` 要素内に保存する必要があります。
* `id="mdworks-restricted-viewer-box"`
* `type="application/json"`


* **推奨されるメタデータ:**
* `mdworks-viewer-format = mdworks-restricted-viewer`
* `mdworks-viewer-format-version = 1`



## 最上位の JSON

必須のオブジェクトフィールド:

```json
{
  "format": "mdworks-restricted-viewer",
  "formatVersion": 1,
  "display": {},
  "recovery": {}
}

```

ジェネレーターは重複するキーを出力してはなりません。リーダーは可能な限り未知のフィールドを無視すべきです。

## 表示用ボックス (Display Box)

必須のフィールドと定数:

* `alg`: `AES-GCM`
* `keyFormat`: `raw-base64`
* `key`: 32バイトの生のキーの標準Base64
* `iv`: 12バイトのIVの標準Base64
* `data`: 暗号文の後に128ビットの認証タグが続く標準Base64
* **AAD:** なし
* **平文のエンコーディング:** UTF-8 JSON

表示用キーはHTML内に保存されるため、このボックスは機密性の境界にはなりません。

## 表示用ペイロード (Display Payload)

必須のフィールド:

* `v`: `1`
* `type`: `mdworks-restricted-viewer-display`
* `title`: ビューアのタイトル文字列
* `createdAt`: ISO 8601 タイムスタンプ（推奨: `YYYY-MM-DDTHH:mm:ss.sssZ`）
* `html`: サニタイズされた表示用HTML文字列

表示用のHTMLには、スクリプト、iframe、イベントハンドラー属性、または `javascript:` URL のような実行可能あるいは安全でないコンテンツを含めてはなりません。

## 復元用ボックス (Recovery Box)

必須のフィールドと定数:

* `v`: `1`
* `label`: `restricted-viewer-recovery`
* `alg`: `AES-GCM`
* `kdf`: `PBKDF2`
* `hash`: `SHA-256`
* `iterations`: `310000`
* `salt`: 16バイトのランダムデータの標準Base64
* `iv`: 12バイトのランダムデータの標準Base64
* `data`: 暗号文の後に128ビットの認証タグが続く標準Base64

## 復元キーの導出 (Recovery Key Derivation)

* **パスワードのエンコーディング:** UTF-8
* **パスワードの事前処理:** なし
* **KDF:** PBKDF2-HMAC-SHA256
* **反復回数:** 310,000回
* **ソルト長:** 16バイト
* **導出キー長:** 32バイト
* **結果の暗号化方式:** AES-256-GCM

キーの導出前に、パスワードのトリミング（空白削除）、正規化、大文字小文字の変換、その他の変更を行ってはなりません。

## 復元用ペイロード (Recovery Payload)

必須のフィールド:

* `v`: `1`
* `type`: `mdworks-restricted-viewer-recovery`
* `title`: ソースドキュメントのタイトル
* `filename`: 復元されるMarkdownのファイル名（通常は `.md` で終わる）
* `createdAt`: 生成タイムスタンプ
* `format`: `mdworks-restricted-viewer`
* `markdown`: 完全なMarkdown文字列

ソースのMarkdownは、暗号化前に自動的なUnicode正規化を行うことなく保持されるべきです。

## Base64

RFC 4648 の標準 Base64（`+` と `/` を使用し、`=` のパディングを保持）を使用してください。Base64URL は使用しないでください。

## 安全な JSON の埋め込み

`<script>` 要素に JSON を埋め込む前に、少なくとも以下をエスケープしてください。

* `<` を `\u003c` として
* `>` を `\u003e` として
* `&` を `\u0026` として
* U+2028 を `\u2028` として
* U+2029 を `\u2029` として