# MD//WORKS Restricted Viewer Format v1 Revision 0.2

**Status:** Draft / Experimental
**Format identifier:** `mdworks-restricted-viewer`
**Format version:** `1`
**Initial implementation target:** MD//WORKS v1.5.7
**Specification revision:** `0.2`

## Compatibility-Critical Components

Format v1では、主に次の要素を互換性の対象とします。

1. HTML内の形式識別方法
2. 表示用データの構造
3. Markdown復元用データの構造
4. 暗号方式と鍵導出条件
5. 復元時の検証方法

---

## 0. Conventions

本仕様では、次の用語を使用します。

* **MUST**：互換実装が必ず満たす必要がある要件
* **MUST NOT**：互換実装が行ってはならない処理
* **SHOULD**：特別な理由がない限り従うことを推奨する要件
* **SHOULD NOT**：特別な理由がない限り避けることを推奨する処理
* **MAY**：実装上、任意に採用できる機能

---

## 1. Purpose

MD//WORKS Restricted Viewer Format v1は、Markdown文書を、次の性質を持つHTMLファイルとして保存・配布するための形式です。

* ブラウザだけで閲覧できる
* 原則として外部通信を必要としない
* テキスト選択、コピー、右クリック、ドラッグ、印刷を抑制できる
* 表示時にはパスワードを要求しない
* 復元用パスワードを使用して、元のMarkdownをMD//WORKSへ戻せる
* MD//WORKS以外の互換ツールでも生成できる

本形式の閲覧制限は、一般的な操作によるコピーや印刷を抑制するためのものです。

Restricted ViewerはDRMではありません。スクリーンショット、画面撮影、ブラウザの開発者ツール、HTML解析などによる内容の取得を完全に防止するものではありません。

---

## 2. Scope

Format v1では、次の領域を互換性の対象とします。

### 2.1 互換性を固定する領域

* HTML内のRestricted Viewerデータ格納位置
* 最上位JSONオブジェクト
* 表示用暗号化データ
* Markdown復元用暗号化データ
* 暗号アルゴリズムと鍵導出条件
* 表示用ペイロード
* 復元用ペイロード
* ファイル形式とバージョンの識別方法

### 2.2 実装ごとに変更できる領域

* Viewerの配色
* ViewerのCSS
* Outlineのデザイン
* 画面幅、余白、フォント
* ローディング表示
* エラーメッセージ
* コピー抑制用JavaScriptの具体的な実装
* モバイル表示
* アクセシビリティ補助機能
* ファイルサイズに関する警告基準

Viewerの外観や操作画面を変更しても、本仕様で規定するJSON構造と暗号形式を維持する限り、Format v1互換とみなします。

---

## 3. Terminology

### Restricted Viewer

閲覧制限を付けたHTML文書全体を指します。

### Generator

Markdownや画像などからRestricted Viewer HTMLを生成するソフトウェアを指します。

MD//WORKSおよび`images2rHTML.py`はGeneratorに該当します。

### Reader

Restricted Viewerから元のMarkdownを復元するソフトウェアを指します。

MD//WORKSはReaderに該当します。

### Display payload

ブラウザ上で表示するHTML本文とタイトルを含むJSONデータです。

### Recovery payload

元のMarkdown、ファイル名、および関連メタデータを含むJSONデータです。

### Display box

Display payloadをAES-GCMで暗号化したオブジェクトです。

表示用鍵はViewerファイル内に保存されるため、Display boxは機密保護を目的とするものではありません。

### Recovery box

Recovery payloadを、復元用パスワードから導出した鍵で暗号化したオブジェクトです。

### Recovery password

元のMarkdownを復元するためのパスワードです。通常の閲覧時には使用しません。

---

## 4. File Requirements

### 4.1 Character Encoding

ファイル全体はUTF-8で保存しなければなりません。

HTMLには次を含めます。

```html
<meta charset="utf-8">
```

### 4.2 Recommended File Extension

推奨するファイル名は次の形式です。

```text
document.restricted.view.html
```

例：

```text
presentation.restricted.view.html
```

```text
研究報告書.restricted.view.html
```

`.restricted.view.htm`をReaderの読み込み対象にしても構いませんが、Generatorは原則として`.restricted.view.html`を使用します。

### 4.3 Standalone Operation

Restricted Viewerは、ローカルファイルとして開けるHTML文書であることを推奨します。

```text
file:///...
```

から開いた場合にも、文書本文の表示に外部サーバー接続を必要としないことを推奨します。

### 4.4 Performance and Size Considerations

Base64で埋め込まれた画像は、Restricted Viewerのファイルサイズを大きくします。

画像データがDisplay payloadとRecovery payloadの両方に含まれ、さらに暗号化後のデータがBase64化される場合、最終HTMLは元画像の合計サイズより大幅に大きくなる可能性があります。

Format v1は、すべての環境に共通する最大ファイルサイズを規定しません。

実用上の上限は、次の条件によって異なります。

* ブラウザ
* 使用可能なメモリ
* CPU性能
* 画像枚数
* 画像解像度
* Readerの実装
* Display payloadとRecovery payloadの構成

Generatorは、可能な範囲で次を行うべきです。

* 生成前または生成後に推定ファイルサイズを表示する
* 出力が著しく大きくなる場合に警告する
* 実装ごとの警告しきい値を設定できるようにする
* 不要なバイナリコピーを減らす
* 画像を1ファイルずつ検証する
* 処理不能な画像だけをスキップし、他の画像の処理を継続する

Readerは、Base64データURIなどを含む極端に長いMarkdown行によって、編集画面が停止しないように保護すべきです。

Readerは、実装上定めたしきい値を超える行について、次のような補助処理を省略しても構いません。

* Backdrop表示
* 不可視文字表示
* スペルチェック
* 構文強調
* 検索結果の装飾
* 行単位の追加レンダリング

これらはReaderの性能上の実装要件であり、Format v1のファイル互換性には影響しません。

---

## 5. HTML Container

Restricted Viewer HTMLには、次の`script`要素を1つだけ含めなければなりません。

```html
<script
  id="mdworks-restricted-viewer-box"
  type="application/json">
{
  ...
}
</script>
```

Readerは、この要素の`id`を使用してRestricted Viewerデータを検出します。

### 5.1 Required Element ID

```text
mdworks-restricted-viewer-box
```

### 5.2 Required MIME Type

```text
application/json
```

### 5.3 Recommended Metadata

次のメタデータは任意ですが、互換ツールによる識別を容易にするため、追加を推奨します。

```html
<meta
  name="mdworks-viewer-format"
  content="mdworks-restricted-viewer">

<meta
  name="mdworks-viewer-format-version"
  content="1">
```

Readerは、これらの`meta`要素が存在しない場合でも、JSON boxから形式を識別できます。

---

## 6. Top-Level JSON Object

`mdworks-restricted-viewer-box`要素には、次の形式のJSONを格納します。

```json
{
  "format": "mdworks-restricted-viewer",
  "formatVersion": 1,
  "display": {
    "...": "..."
  },
  "recovery": {
    "...": "..."
  }
}
```

### 6.1 Required Fields

| Field           |    Type | Required value              |
| --------------- | ------: | --------------------------- |
| `format`        |  string | `mdworks-restricted-viewer` |
| `formatVersion` | integer | `1`                         |
| `display`       |  object | Display box                 |
| `recovery`      |  object | Recovery box                |

### 6.2 Unknown Fields

Format v1 Readerは、未知の追加フィールドを原則として無視すべきです。

Generatorは、同じJSONオブジェクト内に重複するキーを出力してはなりません。

### 6.3 Version Handling

Readerは、次の場合にFormat v1として処理します。

```text
format = "mdworks-restricted-viewer"
formatVersion = 1
```

Readerは、未対応の`formatVersion`を無理に復号してはなりません。

未対応バージョンを検出した場合は、対応していない形式であることをユーザーへ通知すべきです。

---

## 7. Display Box

Display boxは、表示用HTMLを含むDisplay payloadをAES-GCMで暗号化したオブジェクトです。

```json
{
  "alg": "AES-GCM",
  "keyFormat": "raw-base64",
  "key": "BASE64_ENCODED_32_BYTE_KEY",
  "iv": "BASE64_ENCODED_12_BYTE_IV",
  "data": "BASE64_ENCODED_CIPHERTEXT_AND_TAG"
}
```

### 7.1 Required Fields

| Field       |   Type | Requirement        |
| ----------- | -----: | ------------------ |
| `alg`       | string | `AES-GCM`          |
| `keyFormat` | string | `raw-base64`       |
| `key`       | string | 32バイトの鍵を標準Base64化  |
| `iv`        | string | 12バイトのIVを標準Base64化 |
| `data`      | string | 暗号文と認証タグを標準Base64化 |

### 7.2 Encryption Parameters

| Parameter                     | Value    |
| ----------------------------- | -------- |
| Algorithm                     | AES-GCM  |
| Key length                    | 256 bits |
| Key size                      | 32 bytes |
| IV size                       | 12 bytes |
| Authentication tag            | 128 bits |
| Additional authenticated data | None     |
| Plaintext encoding            | UTF-8    |

Web Crypto APIで`tagLength`を省略した場合の、128ビット認証タグを使用します。

`data`には、暗号文の末尾に認証タグを連結したバイト列を格納します。

Pythonの`cryptography`パッケージに含まれる`AESGCM.encrypt()`の戻り値は、この形式と互換性があります。

### 7.3 Security Characteristics

Display boxの鍵は、同じHTMLファイル内の`key`フィールドに保存されます。

したがって、Display boxは次の目的には使用できません。

* 閲覧者に対する機密保持
* 画像や文章の完全な秘匿
* ブラウザ開発者ツールからの抽出防止
* ファイルの真正性確認
* 改ざん者の識別

Display boxの目的は、HTMLソース内に表示本文をそのまま平文で置かず、Viewer起動時に表示内容を復元することです。

---

## 8. Display Payload

Display boxを復号すると、UTF-8で符号化された次のJSONが得られます。

```json
{
  "v": 1,
  "type": "mdworks-restricted-viewer-display",
  "title": "Presentation Title",
  "createdAt": "2026-06-22T12:34:56.789Z",
  "html": "<h2 id=\"slide-1\">Slide 1</h2><p>...</p>"
}
```

### 8.1 Required Fields

| Field       |    Type | Description                         |
| ----------- | ------: | ----------------------------------- |
| `v`         | integer | Payload version。Format v1では`1`      |
| `type`      |  string | `mdworks-restricted-viewer-display` |
| `title`     |  string | Viewerに表示する文書タイトル                   |
| `createdAt` |  string | 生成日時                                |
| `html`      |  string | 表示用HTML本文                           |

### 8.2 `createdAt`

ISO 8601形式を使用します。

推奨形式：

```text
YYYY-MM-DDTHH:mm:ss.sssZ
```

例：

```text
2026-06-22T12:34:56.789Z
```

### 8.3 HTML Safety and XSS Protection

`html`は、ViewerのDOMへ挿入されることを前提とします。

Generatorは、Display payloadへ格納する前に、表示用HTMLをサニタイズしなければなりません。

表示用HTMLには、次を含めてはなりません。

* `<script>`
* `<iframe>`
* `<object>`
* `<embed>`
* `onclick`などのイベント属性
* `onload`
* `onerror`
* `javascript:` URL
* 信頼できない実行可能要素
* 未サニタイズの任意HTML

MD//WORKSから生成する場合は、MD//WORKSのMarkdown変換処理およびサニタイズ処理を通過したHTMLを使用します。

`images2rHTML.py`のような画像専用Generatorでは、安全なHTML要素と属性だけを直接組み立てることができます。

例：

```html
<h2 id="slide-1">Slide 1</h2>
<p>
  <img
    src="data:image/png;base64,..."
    alt="Slide 1">
</p>
```

Viewer実装は、復号したDisplay HTMLを信頼済みデータとして無条件に扱わず、DOMへ挿入する直前に、許可リスト方式による追加サニタイズを行うことが推奨されます。

このランタイムサニタイズは、防御の多層化を目的とするものです。

ただし、攻撃者がViewer HTML全体を書き換えられる場合は、表示データだけでなくViewerランタイム自体も変更できます。

そのため、ランタイムサニタイズは次を保証しません。

* Restricted Viewerファイルの真正性
* Viewerランタイムの非改ざん
* 配布元の証明
* 電子署名による検証

Format v1は、デジタル署名またはファイル真正性確認の仕組みを提供しません。

---

## 9. Recovery Box

Recovery boxは、元のMarkdownを含むRecovery payloadを、復元用パスワードから導出した鍵で暗号化したオブジェクトです。

```json
{
  "v": 1,
  "label": "restricted-viewer-recovery",
  "alg": "AES-GCM",
  "kdf": "PBKDF2",
  "hash": "SHA-256",
  "iterations": 310000,
  "salt": "BASE64_ENCODED_16_BYTE_SALT",
  "iv": "BASE64_ENCODED_12_BYTE_IV",
  "data": "BASE64_ENCODED_CIPHERTEXT_AND_TAG"
}
```

### 9.1 Required Fields

| Field        |    Type | Required value               |
| ------------ | ------: | ---------------------------- |
| `v`          | integer | `1`                          |
| `label`      |  string | `restricted-viewer-recovery` |
| `alg`        |  string | `AES-GCM`                    |
| `kdf`        |  string | `PBKDF2`                     |
| `hash`       |  string | `SHA-256`                    |
| `iterations` | integer | `310000`                     |
| `salt`       |  string | 16バイトのランダム値を標準Base64化        |
| `iv`         |  string | 12バイトのランダム値を標準Base64化        |
| `data`       |  string | 暗号文と認証タグを標準Base64化           |

---

## 10. Recovery Key Derivation

復元用AES鍵は、復元用パスワードからPBKDF2によって導出します。

### 10.1 Parameters

| Parameter           | Value       |
| ------------------- | ----------- |
| Password encoding   | UTF-8       |
| KDF                 | PBKDF2      |
| Hash                | SHA-256     |
| Iterations          | 310,000     |
| Salt length         | 16 bytes    |
| Derived key length  | 32 bytes    |
| Resulting algorithm | AES-256-GCM |

### 10.2 Password Processing

パスワード文字列は、そのままUTF-8へ変換してPBKDF2へ渡します。

GeneratorおよびReaderは、パスワードに対して次の処理を自動的に行ってはなりません。

* 前後の空白を削除する
* 大文字・小文字を変換する
* 改行を追加する
* 改行を削除する
* Unicode正規化を適用する
* 類似文字を置き換える
* 全角・半角を変換する

したがって、次の文字列は異なるパスワードとして扱われます。

```text
Password
password
Password 
```

見た目が同じでも、Unicodeコードポイント列が異なるパスワードは、異なるパスワードとして扱われます。

クロスプラットフォームでの入力差異を避けるため、復元用パスワードには、一般的なASCII文字を中心とした推測されにくい文字列を使用することを推奨します。

### 10.3 Python Equivalent

Pythonでは、次の処理に相当します。

```python
import hashlib

key = hashlib.pbkdf2_hmac(
    "sha256",
    password.encode("utf-8"),
    salt,
    310_000,
    dklen=32,
)
```

AES-GCM処理には、たとえば次を使用できます。

```python
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

encrypted = AESGCM(key).encrypt(
    iv,
    plaintext,
    None,
)
```

`encrypted`は、暗号文と128ビット認証タグを連結したバイト列です。

---

## 11. Recovery Payload

Recovery boxを正しいパスワードで復号すると、UTF-8で符号化された次のJSONが得られます。

```json
{
  "v": 1,
  "type": "mdworks-restricted-viewer-recovery",
  "title": "presentation.md",
  "filename": "presentation.md",
  "createdAt": "2026-06-22T12:34:56.789Z",
  "format": "mdworks-restricted-viewer",
  "markdown": "# Presentation\n\n## Slide 1\n\n![Slide 1](data:image/png;base64,...)"
}
```

### 11.1 Required Fields

| Field       |    Type | Description                          |
| ----------- | ------: | ------------------------------------ |
| `v`         | integer | Payload version。Format v1では`1`       |
| `type`      |  string | `mdworks-restricted-viewer-recovery` |
| `title`     |  string | 元文書の名前                               |
| `filename`  |  string | 復元後に使用するMarkdownファイル名                |
| `createdAt` |  string | Restricted Viewer生成日時                |
| `format`    |  string | `mdworks-restricted-viewer`          |
| `markdown`  |  string | 復元対象のMarkdown全文                      |

### 11.2 Filename

`filename`には、原則として`.md`拡張子を付けます。

```text
presentation.md
```

```text
研究報告書.md
```

Readerは、復元後のファイル名を決定する際に、次の優先順位を使用することを推奨します。

1. `payload.filename`
2. `payload.title`
3. Restricted Viewerの元ファイル名
4. Readerが定める既定名

### 11.3 Markdown Encoding and Recovery Consistency

`markdown`はUnicode文字列としてRecovery payloadへ格納し、Recovery payload全体をUTF-8で符号化して暗号化します。

Generatorは、原則として、入力されたMarkdownへ自動的なUnicode正規化を適用せず、その内容を保持すべきです。

Readerは、復元したMarkdownをエディタへ読み込む際に、Reader自身の文書処理方針としてUnicode正規化を適用しても構いません。

MD//WORKSの参照実装は、復元したMarkdownをエディタへ読み込む際にNFC正規化を適用します。

そのため、次の2種類の整合性を区別します。

#### Byte-for-byte consistency

元のUnicodeコードポイント列やバイト列まで含めて完全に同一であることを意味します。

ReaderがUnicode正規化を行う場合、byte-for-byte consistencyは保証されません。

#### Canonical text consistency

Unicodeの正準等価性を考慮し、NFC正規化後のテキストが一致することを意味します。

テストベクトルの整合性検証では、元Markdownと復元Markdownをそれぞれ別の比較用バッファへコピーし、両方をNFC正規化してからSHA-256を計算することを推奨します。

Python例：

```python
import hashlib
import unicodedata

source_for_comparison = unicodedata.normalize(
    "NFC",
    source_markdown,
)

restored_for_comparison = unicodedata.normalize(
    "NFC",
    restored_markdown,
)

source_hash = hashlib.sha256(
    source_for_comparison.encode("utf-8")
).hexdigest()

restored_hash = hashlib.sha256(
    restored_for_comparison.encode("utf-8")
).hexdigest()
```

この比較は、正準等価なテキストとしての一致を確認するものであり、元のUnicode表現のbyte-for-byte保存を意味しません。

---

## 12. Base64 Encoding

すべてのバイナリ値には、RFC 4648の標準Base64を使用します。

対象：

* AES鍵
* Salt
* IV
* 暗号文と認証タグ
* Markdown内へ埋め込む画像データ

### 12.1 Required Variant

次の文字を使用する標準Base64を使用します。

```text
A-Z
a-z
0-9
+
/
=
```

Base64URL形式の`-`および`_`は使用しません。

パディングの`=`は保持することを推奨します。

---

## 13. Safe JSON Embedding

JSONをHTMLの`script`要素へ挿入する前に、次の文字をエスケープすることを推奨します。

| Character | Replacement |
| --------- | ----------- |
| `<`       | `\u003c`    |
| `>`       | `\u003e`    |
| `&`       | `\u0026`    |
| U+2028    | `\u2028`    |
| U+2029    | `\u2029`    |

JavaScript例：

```javascript
function safeScriptJson(value) {
  return JSON.stringify(value)
    .replace(/</g, "\\u003c")
    .replace(/>/g, "\\u003e")
    .replace(/&/g, "\\u0026")
    .replace(/\u2028/g, "\\u2028")
    .replace(/\u2029/g, "\\u2029");
}
```

Python例：

```python
import json

def safe_script_json(value: object) -> str:
    text = json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
    )

    return (
        text
        .replace("<", r"\u003c")
        .replace(">", r"\u003e")
        .replace("&", r"\u0026")
        .replace("\u2028", r"\u2028")
        .replace("\u2029", r"\u2029")
    )
```

---

## 14. Reference Content Security Policy

### 14.1 Single-File Profile

画像をBase64で埋め込み、外部ファイルを使用しない単一HTMLでは、次のContent Security Policyを推奨します。

```html
<meta
  http-equiv="Content-Security-Policy"
  content="
    default-src 'none';
    script-src 'unsafe-inline';
    style-src 'unsafe-inline';
    img-src data: blob:;
    font-src data:;
    connect-src 'none';
    object-src 'none';
    base-uri 'none';
    form-action 'none';
  ">
```

実際のHTMLでは、1行にまとめて記載できます。

```html
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src data: blob:; font-src data:; connect-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none';">
```

### 14.2 Local Companion Media Profile

同じフォルダ内の画像、動画、PDFなどを参照する実装では、必要な範囲に限定してCSPを拡張できます。

例：

```html
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src 'self' data: blob:; media-src 'self' blob:; font-src data:; connect-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none';">
```

実装は、必要のない外部オリジンを許可すべきではありません。

`images2rHTML.py`のSingle-File Restricted Viewerプロファイルでは、原則として画像を`data:` URIとして埋め込みます。

---

## 15. Viewer Restrictions

Full Restricted Viewer実装では、少なくとも次の操作を抑制することを推奨します。

* `copy`
* `cut`
* `selectstart`
* `contextmenu`
* `dragstart`
* Ctrl/Cmd＋A
* Ctrl/Cmd＋C
* Ctrl/Cmd＋X
* Ctrl/Cmd＋P
* 画像のドラッグ
* リンクのドラッグ
* 印刷時の本文出力

CSS例：

```css
.viewer-shell {
  user-select: none;
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
  -webkit-touch-callout: none;
}

.viewer-shell img,
.viewer-shell a {
  -webkit-user-drag: none;
}

@media print {
  html,
  body {
    background: #fff !important;
  }

  body * {
    display: none !important;
  }
}
```

これらの制限は、Format v1のデータ互換性には影響しません。

各実装は、ブラウザや端末に応じて抑制方法を変更できます。

---

## 16. Outline

Viewerは、Display payload内のHTMLからOutlineを生成できます。

MD//WORKS v1.5.7の参照実装では、主に次の見出し要素を対象とします。

```text
h1
h2
h3
```

見出しには一意な`id`を割り当てることを推奨します。

```html
<h2 id="slide-1">Slide 1</h2>
```

重複する見出しには、重複しないIDを割り当てます。

```html
<h2 id="results">Results</h2>
<h2 id="results-2">Results</h2>
```

Outlineは表示上の補助機能であり、Markdown復元互換性の必須条件ではありません。

---

## 17. Import Procedure

MD//WORKS互換Readerは、次の順序でRestricted Viewerを読み込みます。

1. HTMLをテキストとして読み込む
2. `mdworks-restricted-viewer-box`要素を探す
3. 要素内のJSONを解析する
4. `format`と`formatVersion`を確認する
5. Recovery boxの暗号条件を確認する
6. ユーザーへ復元用パスワードを要求する
7. パスワードを変更せずUTF-8へ変換する
8. PBKDF2でAES鍵を導出する
9. AES-GCMでRecovery boxを復号する
10. Recovery payloadをUTF-8のJSONとして解析する
11. `type`と`markdown`を検証する
12. Markdownをエディタへ復元する
13. Readerの方針に従って必要な文字列処理を行う
14. `filename`を復元する
15. 極端に長い行がある場合は、補助レンダリングを制限する

### 17.1 Minimum Recovery Validation

少なくとも次を検証します。

```text
box.format = "mdworks-restricted-viewer"
box.formatVersion = 1

box.recovery.v = 1
box.recovery.label = "restricted-viewer-recovery"
box.recovery.alg = "AES-GCM"
box.recovery.kdf = "PBKDF2"
box.recovery.hash = "SHA-256"
box.recovery.iterations = 310000

payload.v = 1
payload.type = "mdworks-restricted-viewer-recovery"
payload.format = "mdworks-restricted-viewer"
payload.markdown is a string
```

Readerは、Salt、IV、鍵、暗号文のBase64デコード後の長さも検証することを推奨します。

### 17.2 Error Handling

次の場合は復元に失敗します。

* パスワードが異なる
* Salt、IVまたは暗号文が破損している
* 認証タグが一致しない
* JSONが不正
* Format identifierが異なる
* Format versionが未対応
* Payload typeが異なる
* `markdown`が文字列ではない
* 暗号パラメータがFormat v1と一致しない

パスワード間違いとデータ破損を、ユーザーへ詳細に区別して表示する必要はありません。

例：

```text
The password is incorrect, or the recovery data is damaged.
```

---

## 18. Conformance Levels

Format v1では、実装を次の3段階に分類できます。

### 18.1 Recovery-Compatible Generator

次を生成できる実装です。

* 有効なHTML
* `mdworks-restricted-viewer-box`
* 有効なRecovery box
* MD//WORKSで復元可能なRecovery payload

Viewer画面の実装は必須ではありません。

### 18.2 Full Restricted Viewer Generator

次をすべて実装します。

* 有効なDisplay box
* 有効なRecovery box
* ブラウザ上での自動表示
* Outline
* コピー等の抑制
* 印刷抑制
* MD//WORKSでのMarkdown復元

### 18.3 Single-File Restricted Viewer Generator

Full Restricted Viewer Generatorの条件に加え、次を満たします。

* 表示に必要な画像をBase64で埋め込む
* 外部JavaScriptを使用しない
* 外部CSSを使用しない
* 外部フォントを使用しない
* オフラインで閲覧できる
* HTMLファイル1つで配布できる

`images2rHTML.py`は、原則としてこのプロファイルを対象とします。

---

## 19. Security Considerations

### 19.1 Restricted Viewer Is Not DRM

本形式は、一般的なコピー、選択、右クリック、ドラッグ、印刷を抑制しますが、次を防ぐことはできません。

* スクリーンショット
* 画面撮影
* ブラウザ開発者ツール
* HTMLファイルの解析
* メモリ上の復号済みHTML取得
* Display keyを使用した表示データの復号
* Viewerランタイムを変更した再表示

### 19.2 Display Data Is Not Confidential

Display keyはHTML内に保存されます。

したがって、表示できる文章や画像は、技術的には閲覧者が抽出できます。

また、第三者がDisplay boxの鍵と暗号文を両方書き換えられる場合、改変された表示内容を作成できます。

Format v1は、Display payloadの配布元を認証しません。

### 19.3 Recovery Data

元Markdownは、復元用パスワードから導出した鍵で暗号化されます。

Recovery boxには、パスワード自体も復元用AES鍵も保存しません。

ただし、弱いパスワードを使用すると、オフライン総当たり攻撃を受ける可能性があります。

復元用パスワードには、次の条件を推奨します。

* 10文字以上
* 辞書語だけで構成しない
* 文書名や利用者名から推測しにくい
* 他のサービスのパスワードを再利用しない
* 可能であれば十分に長いパスフレーズを使用する

### 19.4 Password Loss

復元用パスワードを失った場合、Recovery payloadから元Markdownを復元する方法はありません。

Generatorは、パスワードを安全な場所へ記録するよう、ユーザーへ明示的に案内すべきです。

### 19.5 Plaintext Metadata

HTMLには、次の情報が平文で含まれる場合があります。

* HTMLの`<title>`
* Viewer上部の文書タイトル
* UI言語
* Viewerの生成ツール名
* Format version
* 生成日時
* Viewerランタイムのコード

文書タイトル自体を秘匿したい用途では注意が必要です。

### 19.6 File Authenticity

Format v1は、次の機能を提供しません。

* デジタル署名
* 証明書
* 配布者の認証
* ファイル改ざんの外部検証
* 信頼できるタイムスタンプ

必要に応じて、配布者はHTMLファイルのSHA-256を別の信頼できる経路で提示できます。

---

## 20. Forward Compatibility

### 20.1 Unknown Fields

Format v1 Readerは、未知の追加フィールドを可能な範囲で無視します。

ただし、未知のフィールドによって既知の必須フィールドの意味を変更してはなりません。

### 20.2 Format Version

互換性を破る変更を行う場合は、`formatVersion`を変更します。

```json
{
  "formatVersion": 2
}
```

### 20.3 Payload Version

Display payloadまたはRecovery payloadだけを変更する場合は、それぞれの`v`を変更できます。

Format v1では、次を使用します。

```text
display.v = 1
recovery.v = 1
```

Payload versionを変更した場合でも、既存Readerが安全に処理できない変更であれば、Format versionも更新すべきです。

### 20.4 Cryptographic Parameter Changes

次の変更は、原則としてFormat versionの更新対象です。

* AES-GCM以外への変更
* AES鍵長の変更
* PBKDF2以外への変更
* Salt形式の変更
* IV形式の変更
* 暗号文格納形式の変更
* 認証タグの格納形式の変更
* Base64方式の変更
* パスワード前処理の変更
* AADの導入

PBKDF2反復回数はRecovery box内に記録されますが、MD//WORKS v1.5.7互換Format v1では`310000`を必須とします。

---

## 21. Minimal Container Example

次は構造だけを示す最小例です。

Base64文字列は省略しています。

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">

<meta
  name="mdworks-viewer-format"
  content="mdworks-restricted-viewer">

<meta
  name="mdworks-viewer-format-version"
  content="1">

<title>Sample Document</title>
</head>

<body>

<div id="loading">Loading...</div>
<main id="viewer-document"></main>

<script
  id="mdworks-restricted-viewer-box"
  type="application/json">
{
  "format": "mdworks-restricted-viewer",
  "formatVersion": 1,
  "display": {
    "alg": "AES-GCM",
    "keyFormat": "raw-base64",
    "key": "...",
    "iv": "...",
    "data": "..."
  },
  "recovery": {
    "v": 1,
    "label": "restricted-viewer-recovery",
    "alg": "AES-GCM",
    "kdf": "PBKDF2",
    "hash": "SHA-256",
    "iterations": 310000,
    "salt": "...",
    "iv": "...",
    "data": "..."
  }
}
</script>

<script>
/* Viewer runtime */
</script>

</body>
</html>
```

---

## 22. Test Vectors

Format v1を公開する際は、次のテストデータを同時に公開することを推奨します。

```text
test-vectors/
└─ rvf1/
   ├─ source.md
   ├─ expected-display.html
   ├─ sample.restricted.view.html
   ├─ metadata.json
   ├─ README.md
   └─ checksums.sha256
```

### 22.1 Recommended Test Password

公開テスト専用パスワード：

```text
mdworks-demo
```

このパスワードは、実運用に使用してはなりません。

### 22.2 Test Markdown

```markdown
# Restricted Viewer Format Test

English text and 日本語テキスト。

## Symbols

H~2~O and Ca^2+^.

## Footnote

A footnote reference.[^test]

[^test]: Test footnote.
```

### 22.3 Required Tests

* MD//WORKSで生成したファイルをMD//WORKSで復元できる
* `images2rHTML.py`で生成したファイルをMD//WORKSで復元できる
* Pythonで暗号化したRecovery boxをWeb Crypto APIで復号できる
* Web Crypto APIで暗号化したRecovery boxをPythonで復号できる
* 間違ったパスワードでは復元できない
* 暗号文を1バイト変更すると復元できない
* Saltを変更すると復元できない
* IVを変更すると復元できない
* 日本語ファイル名を復元できる
* スペースや括弧を含むファイル名を復元できる
* 絵文字を含むMarkdownを復元できる
* CRLFおよびLFの扱いを確認できる
* 画像を含むBase64 Markdownを復元できる
* 20枚の画像を含むファイルを処理できる
* 50枚の画像を含むファイルについて性能を評価できる
* 非対応のFormat versionを安全に拒否できる
* 未知の追加フィールドを無視できる
* 不正なDisplay HTMLを安全に扱える

### 22.4 Integrity Comparison

Canonical text consistencyの比較では、元Markdownと復元MarkdownをそれぞれNFCへ正規化したうえでSHA-256を計算します。

```text
SHA-256(NFC(source Markdown))
=
SHA-256(NFC(restored Markdown))
```

byte-for-byte一致を別途検証する場合は、Unicode正規化を行わず、元のUTF-8バイト列同士を比較します。

Readerが復元時に正規化を行う場合、byte-for-byte一致は必須条件としません。

---

## 23. Implementation Profile for images2rHTML.py

`images2rHTML.py` v0.1.0は、次の条件を満たすことを目標とします。

* Format identifier：`mdworks-restricted-viewer`
* Format version：`1`
* Full Restricted Viewer Generator
* Single-File Restricted Viewer Generator
* MD//WORKS v1.5.7でMarkdown復元可能
* PNG対応
* JPEG対応
* WebP対応
* 画像をBase64で埋め込む
* ファイル名を自然順で並べる
* ファイル名から見出しを生成する
* 元MarkdownをRecovery payloadへ保存する
* Markdownへ自動的なUnicode正規化を適用しない
* パスワードへ自動的なUnicode正規化を適用しない
* `cryptography`を使用してAES-GCMを実装する
* PBKDF2-HMAC-SHA256を使用する
* PBKDF2反復回数を310,000回とする
* Saltを16バイトとする
* IVを12バイトとする
* AES鍵を32バイトとする
* 標準Base64を使用する
* 安全なHTMLだけを直接生成する
* 外部通信を行わない
* 元画像を変更しない
* 出力サイズが大きい場合に警告する
* 処理結果とスキップした画像を報告する

生成するMarkdown例：

```markdown
## Slide 1

![Slide 1](data:image/png;base64,...)

## Slide 2

![Slide 2](data:image/png;base64,...)
```

生成したRestricted ViewerをMD//WORKSで開いた場合、このMarkdownが復元されなければなりません。

### 23.1 Recommended Command Example

```bash
python images2rHTML.py ./slides \
  -o presentation.restricted.view.html \
  --title "Presentation" \
  --recovery-password
```

実際のコマンドライン仕様は、`images2rHTML.py`のREADMEで別途定義します。

---

## 24. Versioning Policy

本仕様の公開初期段階では、次の表記を使用します。

```text
Restricted Viewer Format v1
Specification revision 0.2
Status: Experimental
```

Format自体の識別番号と、仕様文書の改訂番号を分けて管理します。

| Item                   | Value            |
| ---------------------- | ---------------- |
| File format            | v1               |
| Specification revision | 0.2              |
| Implemented by         | MD//WORKS v1.5.7 |
| Status                 | Experimental     |

文章の修正、例の追加、説明の明確化など、ファイル互換性に影響しない変更では、仕様文書の改訂番号だけを更新します。

```text
0.1 → 0.2 → 0.3
```

JSON構造や暗号形式を変更し、既存Readerとの互換性が失われる場合は、Format versionを更新します。

```text
Format v1 → Format v2
```

仕様文書が安定した段階では、Format versionを変更せず、Specification revisionだけを`1.0`へ更新できます。

例：

```text
Format v1
Specification revision 1.0
```

---

## 25. Summary

MD//WORKS Restricted Viewer Format v1は、次の2種類のデータを1つのHTMLへ格納します。

1. 閲覧時に自動復号する表示用HTML
2. 復元用パスワードで暗号化した元Markdown

表示用HTMLは閲覧制限付きで表示されますが、表示用鍵が同じHTMLファイル内に含まれるため、表示内容の機密保護を目的とするものではありません。

表示用HTMLはGenerator側でサニタイズし、Viewer側でも可能な範囲で追加のサニタイズを行うことを推奨します。

ただし、Format v1はファイルの真正性や配布元を保証しません。

元Markdownは、PBKDF2-HMAC-SHA256とAES-256-GCMを使用して暗号化され、正しい復元用パスワードを持つ場合に限り、MD//WORKSまたは互換Readerへ復元できます。

Format v1では、パスワードやMarkdownへ自動的なUnicode正規化を強制しません。

テスト時には、目的に応じて次を区別します。

* 元バイト列の完全一致
* NFC正規化後の正準等価なテキスト一致

Format v1の固定対象はViewerの外観ではなく、JSON構造、ペイロード、暗号方式、およびMarkdown復元互換性です。
