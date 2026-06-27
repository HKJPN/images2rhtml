# images2rHTML.py ユーザーマニュアル ![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)

[🇺🇸 English](readme.md) or [🇯🇵 日本語](readme-ja.md)
  <img width="1280" height="720" alt="プレゼンテーション1" src="https://github.com/user-attachments/assets/13934b8b-bf8e-4974-ae66-ea30d8b84910" />

`images2rHTML.py`は、フォルダ内の複数画像を、Outline（目次）付きの**Restricted Viewer HTML**にまとめるPython CLIツールです。作成したHTMLはブラウザだけで閲覧でき、テキスト選択、コピー、右クリック、画像ドラッグ、印刷などの一般的な操作を抑制します。生成時に設定したRecovery passwordを使うと、[MD//WORKS](https://github.com/HKJPN/markdown-editor)で元のMarkdownを復元し、見出しの修正、画像の追加・削除、文章の追記などを再び行えます。`images2rHTML.py`はコマンドラインで動作するため生成するサイズに事実上の制限がなく、多数の画像ファイルをHTMLにまとめる用途に向いています。一方、MD//WORKSも、GUI環境で同様な制限付きファイルの編集や生成が可能ですが、画像を含んだファイルサイズの上限は50MB程度に制限されます。

```text
画像フォルダ
    ↓
images2rHTML.py
    ↓
Outline付き Restricted Viewer HTML
    ↓
ブラウザで配布・閲覧

必要になった場合
    ↓
MD//WORKSでRecovery passwordを入力
    ↓
元のMarkdownを復元して再編集
```

> ⚠️ **重要：Restricted ViewerはDRMではありません。**
> 一般的なコピー、印刷、ドラッグ、意図しない編集を抑制するための形式です。スクリーンショット、画面撮影、ブラウザ開発者ツール、HTML解析などによる取得を完全に防ぐものではありません。

---

## ✨ 主な機能

* PNG、JPEG、WebP画像を1つのHTMLへまとめる
* ファイル名を自然な順序で並べる
* 画像ファイル名から見出しを自動生成する
* Outlineから各画像へすぐ移動できる
* 画像をBase64形式でHTML内へ埋め込む
* HTMLファイル1つだけでオフライン閲覧できる
* テキスト選択、コピー、右クリック、ドラッグ、印刷を抑制する
* Recovery passwordで元Markdownを暗号化して保存する
* MD//WORKSでMarkdownへ復元して再編集できる
* 元画像を書き換えない
* 外部サーバーへ通信しない
* 出力途中で失敗しても、不完全な最終ファイルを残しにくい原子的保存を行う

---

## 🛠️ 動作に必要な環境

* **Python 3.11以上**
* Pythonパッケージ**`cryptography`**
* `images2rHTML.py`と専用HTMLテンプレート

### `cryptography`のインストール

Windows PowerShellまたはmacOS／Linuxのターミナルで、次を実行します。

```bash
python -m pip install cryptography
```

Windowsで複数のPythonが入っている場合は、次でもインストールできます。

```powershell
py -m pip install cryptography
```

インストール確認：

```bash
python -c "import cryptography; print(cryptography.__version__)"
```

次のようなエラーが表示された場合は、`cryptography`が現在使用しているPython環境に入っていません。

```text
ModuleNotFoundError: No module named 'cryptography'
```

### 対応環境

Restricted Viewer HTMLの**作成**は、Windows、macOS、Linuxなど、Pythonと`cryptography`を利用できる環境を想定しています。iPadでは`cryptography`が利用できないためimages2rHTML.pyは利用できませんが、MD//WORKSを用いることでRestricted Viewer HTMLの出力が可能です。

作成済みHTMLの**閲覧**は、Chrome、Edge、Firefox、Brave、Safariなど、Web Crypto APIに対応した一般的なブラウザで行えます。iPadでも作成済みViewerを閲覧できます。

---

## ⚠️ `templates`フォルダを一緒に配置してください

`images2rHTML.py`は、次のHTMLテンプレートを使用します。

```text
templates/restricted-viewer-v1.html
```

次のディレクトリ構成を崩さずに使用してください。

```text
📂 images2rhtml
├── 📄 images2rHTML.py
└── 📂 templates
    └── 📄 restricted-viewer-v1.html
```

> **`images2rHTML.py`だけを別の場所へコピーすると、Restricted Viewerを生成できません。**
> `images2rHTML.py`と`templates`フォルダを、元の構成のまま一緒に配置してください。

テンプレートを確認するWindows PowerShellコマンド：

```powershell
Test-Path .\templates\restricted-viewer-v1.html
```

`True`と表示されれば、テンプレートを読み込める位置にあります。

---

## 🚀 基本的な使い方

### 1. 作業フォルダを準備する

例として、次の構成を使います。

```text
📂 work
├── 📂 tools
│   └── 📂 images2rhtml
│       ├── 📄 images2rHTML.py
│       └── 📂 templates
│           └── 📄 restricted-viewer-v1.html
│
└── 📂 slides
    ├── 🖼️ スライド1.JPG
    ├── 🖼️ スライド2.JPG
    ├── 🖼️ スライド3.JPG
    ├── 🖼️ スライド10.JPG
    └── ...
```

### 2. コマンド入力画面を開く

#### 🪟 Windows

作業フォルダをエクスプローラーで開き、アドレスバーへ`powershell`と入力してEnterを押すと、その場所でPowerShellを開けます。

または、フォルダ内の何もない場所で右クリックし、「ターミナルで開く」または「PowerShellウィンドウをここで開く」を選びます。

#### 🍎 macOS

Spotlightから「ターミナル」を開きます。

半角で`cd `と入力し、作業フォルダをターミナル画面へドラッグ＆ドロップしてからEnterを押すと、そのフォルダへ移動できます。

### 3. コマンドを実行する

Windows PowerShellの例：

```powershell
python .\tools\images2rhtml\images2rHTML.py .\slides `
  -o .\presentation.restricted.view.html `
  --title "Presentation" `
  --recovery-password
```

1行で入力しても構いません。

```powershell
python .\tools\images2rhtml\images2rHTML.py .\slides -o .\presentation.restricted.view.html --title "Presentation" --recovery-password
```

macOS／Linuxの例：

```bash
python3 ./tools/images2rhtml/images2rHTML.py ./slides \
  -o ./presentation.restricted.view.html \
  --title "Presentation" \
  --recovery-password
```

> 💡 PowerShellで複数行に分ける場合は、行末にバッククォート（`` ` ``）を使います。
> macOS／Linuxのシェルでは、行末にバックスラッシュ（`\`）を使います。

### 4. Recovery passwordを入力する

コマンドを実行すると、次のように表示されます。

```text
Recovery password:
Confirm recovery password:
```

パスワードを2回入力し、Enterを押してください。

> 💡 **パスワード入力中は、文字も「●」も画面に表示されません。**
> カーソルが動かないように見えても正常です。そのまま入力してEnterを押してください。

> 💡 **このパスワードは閲覧用ではありません。**
> 生成されたHTMLをブラウザで開く際、閲覧者はパスワードを入力せずに資料を閲覧できます。Recovery passwordは、後からMD//WORKSで元のMarkdownへ復元して再編集するための、作成者・編集者用のパスワードです。

> ⚠️ Recovery passwordを失うと、暗号化された元Markdownを復元できません。安全な場所へ記録してください。

Recovery passwordでは、大文字・小文字、全角・半角、空白、記号などが区別されます。復元時には、生成時と同じ文字列を正確に入力してください。

### 5. 出力ファイルを確認する

処理に成功すると、次のように表示されます。

```text
Wrote Restricted Viewer HTML: presentation.restricted.view.html
Final output size: 21682497 bytes
```

相対パスで出力名を指定した場合、ファイルは**コマンドを実行している現在のフォルダ**へ保存されます。

Windowsで現在のフォルダを開く場合：

```powershell
explorer .
```

---

## 📖 作成したViewerの使い方

生成された`.restricted.view.html`ファイルをダブルクリックするか、ブラウザへドラッグ＆ドロップします。

Viewerには次の機能があります。

* 左側のOutlineから各画像へ移動
* Outlineの開閉
* PC、タブレット、スマートフォンに応じたレスポンシブ表示
* テキスト選択の抑制
* コピー、切り取りの抑制
* 右クリックメニューの抑制
* 画像ドラッグの抑制
* 一般的な印刷操作の抑制

閲覧者は、元のPowerPointやMarkdownを持っていなくても、ブラウザだけで資料を確認できます。

---

## ⚙️ オプション

基本構文：

```text
python images2rHTML.py INPUT_DIR [options]
```

| オプション                        | 意味・使い方                                                          | 初期値・備考                 |
| ---------------------------- | --------------------------------------------------------------- | ---------------------- |
| `INPUT_DIR`                  | 画像が入っている入力フォルダです。                                               | 必須                     |
| `-o FILE`<br>`--output FILE` | 出力するRestricted Viewer HTMLの保存先です。                               | HTML生成時に指定             |
| `--title "タイトル"`             | Viewer上部へ表示する文書タイトルです。                                          | 指定なしの場合は`Presentation` |
| `--recovery-password`        | Recovery passwordを画面上で非表示入力します。パスワード文字列をコマンド引数へ直接記載する機能ではありません。 | HTML生成時に使用             |
| `--max-kb 数値`                | 1画像あたりの最大サイズをKiB単位で指定します。超過画像はスキップされます。                         | `300` KiB              |
| `--warning-mb 数値`            | 推定または実際のHTML容量が指定値を超えたときに警告します。警告後も生成は継続します。                    | `20` MiB               |
| `--overwrite`                | 同名の出力ファイルがある場合に上書きします。                                          | 無効                     |
| `--dry-run`                  | ファイルを書き出さず、対象画像、処理順、スキップ、推定容量を確認します。パスワード入力も行いません。              | 無効                     |
| `--emit-markdown FILE`       | 内部で生成されるMarkdownを、開発・確認用に書き出します。                                | 通常利用では不要               |
| `--emit-recovery-box FILE`   | Recovery box JSONを互換性検証用に書き出します。                                | 通常利用では不要               |
| `--version`                  | ツールのバージョンを表示します。                                                | -                      |
| `-h`, `--help`               | ヘルプを表示します。                                                      | -                      |

現在のバージョンで利用できる正確なオプションと既定値は、次でも確認できます。

```bash
python images2rHTML.py --help
```

### サイズ単位

`--max-kb`と`--warning-mb`のオプション名には`KB`と`MB`が含まれていますが、実際の計算はKiB／MiB単位です。

```text
300 KiB = 300 × 1024 = 307,200 bytes
20 MiB  = 20 × 1024 × 1024 = 20,971,520 bytes
```

---

## 🚦 終了コード

| コード | 意味                                                   |
| --- | ---------------------------------------------------- |
| `0` | すべての画像を正常に処理し、出力に成功しました。                             |
| `1` | 致命的エラーです。入力フォルダ、テンプレート、パスワード、引数、暗号化、書き込みなどを確認してください。 |
| `2` | 一部画像をスキップしましたが、残りの画像で出力に成功しました。                      |

終了コード`2`の場合は、画面に表示されるスキップ一覧と理由を確認してください。

---

## 🔍 実際に作成せず確認する：`--dry-run`

画像の処理順や推定ファイルサイズだけを先に確認できます。

```powershell
python .\tools\images2rhtml\images2rHTML.py .\slides `
  -o .\presentation.restricted.view.html `
  --title "Presentation" `
  --dry-run
```

`--dry-run`では次を確認できます。

* 対象画像数
* 自然順での処理予定
* 各画像の形式
* 各画像の容量
* スキップ予定の画像と理由
* 元画像の合計容量
* 推定Markdownサイズ
* 推定Restricted Viewerサイズ
* 出力予定ファイル名

`--dry-run`では、HTML生成、暗号化、パスワード入力、ファイル書き込みを行いません。

---

## ♻️ 同じ名前のファイルを上書きする

すでに出力ファイルが存在する場合、初期設定では安全のため処理を停止します。

上書きする場合は`--overwrite`を追加してください。

```powershell
python .\tools\images2rhtml\images2rHTML.py .\slides `
  -o .\presentation.restricted.view.html `
  --title "Presentation" `
  --recovery-password `
  --overwrite
```

---

## 📂 対応画像と並び順

### 対応形式

拡張子の大文字・小文字を問わず、次に対応します。

* `.png`
* `.jpg`
* `.jpeg`
* `.webp`

ツールは拡張子だけでなく、PNG、JPEG、WebPの基本的なファイルシグネチャも確認します。

拡張子と実際の画像形式が一致しない場合や、空ファイル、読み取り不能ファイル、サイズ超過ファイルはスキップされます。

> ファイルシグネチャ確認は最低限の形式確認です。画像全体の完全性を保証するものではありません。

### 画像を探す範囲

指定した入力フォルダの**直下にある通常ファイルだけ**を処理します。

サブフォルダの中は再帰検索しません。

### 自然順

ファイル名は自然順で処理されます。

```text
スライド1.JPG
スライド2.JPG
スライド3.JPG
スライド10.JPG
```

数字部分を数値として比較するため、一般的なファイル名順よりもプレゼンテーションに適した順序になります。

各画像の見出しには、拡張子を除いた元ファイル名が使われます。

```text
スライド1.JPG
```

↓

```markdown
## スライド1
```

---

## 📦 ファイルサイズと性能

画像は、Viewer表示用データと、MD//WORKSで復元するMarkdownの両方に含まれるため、最終HTMLは元画像の合計容量より大きくなります。

これはRestricted Viewer Format v1の構造上、正常な動作です。

### 実機試験の参考値

次の資料で試験しました。

```text
画像数：44枚
元画像合計：約6.1 MB
生成Markdown：約8.1 MB
最終HTML：約21.7 MB
```

確認結果：

* Restricted Viewerとしての閲覧は、確認した各環境で軽快
* Core Ultra 5搭載PCでは、MD//WORKSでの復元は数秒で、その後の編集も問題なし
* 第7世代Core i5搭載PCでは、復元に約15秒かかり、その後の編集もやや緩慢だが利用可能
* A16搭載iPadではMD//WORKSでの復元は数秒で、その後の編集も問題なし
* 第6世代iPadでは、復元に約30秒かかり、その後の編集もやや緩慢だが利用可能
* Pythonによる生成と暗号化は、第7世代Core i5でも一瞬で完了

### 利用の目安

画像容量にも左右されますが、概ね次を目安にできます。

| 資料規模   | 目安                                            |
| ------ | --------------------------------------------- |
| 20枚程度  | 旧世代PCや旧世代iPadでも、復元後の編集を含め比較的軽快                |
| 20～40枚 | 多くの環境で実用的                                     |
| 40枚超 | Viewer閲覧は軽快。旧世代端末ではMD//WORKSでの復元・編集が緩慢になる場合あり、必要に応じて資料の分割を検討 |

固定の最大枚数はありません。`--dry-run`と`--warning-mb`を使い、推定容量を確認してから生成することをおすすめします。

---

## 🔓 MD//WORKSでMarkdownへ復元する

生成されたRestricted Viewer HTMLには、元のMarkdownがRecovery passwordで暗号化されて保存されています。

復元手順：

1. [MD//WORKS](https://github.com/HKJPN/markdown-editor)を開く
2. `File` → `Open`から`.restricted.view.html`を選択する
3. 生成時に設定したRecovery passwordを入力する
4. 復元されたMarkdownを確認する
5. 必要に応じて文章、見出し、画像などを再編集する
6. Markdownまたは別のViewer形式で保存する

Viewer自体にはMarkdown復元画面を設けていません。復元と再編集はMD//WORKS側で行います。

大きな資料では、Viewerの閲覧が軽快でも、MD//WORKSでの復元や復元後の編集に時間がかかる場合があります。

---

## 🔐 セキュリティと制限

### オフライン処理

`images2rHTML.py`は、画像処理や暗号化のために外部サービスへ通信しません。

元画像も変更しません。

### パスワードと文字列の扱い

Recovery passwordは、入力された文字列をもとに暗号鍵を導出するために使用されます。

パスワードへ自動的なUnicode正規化は行いません。見た目が似ていても、次のような違いは別のパスワードとして扱われることがあります。

* 大文字と小文字
* 半角文字と全角文字
* 空白の有無
* 異なる種類の記号
* Unicode上の異なる文字表現

復元時には、生成時に入力したものと同じRecovery passwordを正確に入力してください。

Markdown本文や画像ファイル名についても、保存時に一律のUnicode正規化は行いません。

### Displayデータ

ブラウザで表示するためのDisplay keyは、Viewer HTML内に含まれます。

したがって、Viewerに表示できる文章や画像は、技術的には閲覧者が抽出できます。

Restricted Viewerは、表示内容を秘密にするための暗号化ファイルではありません。

### Recoveryデータ

元Markdownは、Recovery passwordから導出した鍵を使い、AES-GCMで暗号化されます。

Recovery passwordそのものはHTMLへ保存されません。

### Restricted Viewerで抑制できること

* 意図しないテキスト選択
* 一般的なコピー操作
* 一般的な印刷操作
* 右クリック
* 画像ドラッグ
* 閲覧者によるうっかりした再利用や改変

### 完全には防げないこと

* スクリーンショット
* 画面撮影
* ブラウザ開発者ツール
* HTMLファイルの解析
* 表示済みデータの技術的な抽出
* ファイルを持つ利用者による意図的な解析

機密保持や法的なDRMを必要とする用途では、Restricted Viewerだけに依存しないでください。MD//WORKS等の暗号化機能を備えたツールを検討ください。

---

## 🧯 トラブルシューティング

### `No module named 'cryptography'`

現在使用しているPython環境に`cryptography`がありません。

```bash
python -m pip install cryptography
```

Windowsで改善しない場合：

```powershell
py -m pip install cryptography
```

インストールしたPythonと、ツールの実行に使用しているPythonが異なる場合にも、このエラーが発生します。

次のコマンドで、実行中のPythonを確認できます。

```bash
python --version
python -c "import sys; print(sys.executable)"
```

### `Restricted Viewer template is missing or unreadable`

`templates/restricted-viewer-v1.html`が見つからないか、読み取れません。

次の配置を確認してください。

```text
images2rhtml/
├── images2rHTML.py
└── templates/
    └── restricted-viewer-v1.html
```

`images2rHTML.py`だけを画像フォルダへコピーしないでください。

Windows PowerShellでは、次のコマンドで確認できます。

```powershell
Test-Path .\templates\restricted-viewer-v1.html
```

### Recovery passwordを入力できないように見える

パスワードは画面へ表示されません。

そのまま入力してEnterを押し、同じパスワードを確認用にもう一度入力してください。

### MD//WORKSで復元できない

次を確認してください。

* 生成時と同じRecovery passwordを入力しているか
* 大文字・小文字、全角・半角、空白、記号が一致しているか
* HTMLファイルが途中で破損していないか
* MD//WORKSがRestricted Viewer Format v1の読み込みに対応したバージョンか

Recovery passwordを紛失した場合、暗号化された元Markdownを復元することはできません。

### 出力ファイルが見つからない

相対パスで出力した場合は、コマンドを実行した現在のフォルダへ保存されます。

Windows：

```powershell
explorer .
```

現在位置の確認：

```powershell
Get-Location
```

macOS／Linux：

```bash
pwd
```

### 出力ファイルがすでに存在する

`--overwrite`を追加してください。

```bash
python images2rHTML.py ./slides -o presentation.restricted.view.html --recovery-password --overwrite
```

### 一部画像がスキップされた

主な原因：

* `--max-kb`を超えている
* 拡張子と画像形式が一致していない
* 空ファイル
* ファイルを読み取れない
* 画像シグネチャが不正

容量上限を変更する例：

```bash
python images2rHTML.py ./slides -o presentation.restricted.view.html --max-kb 500 --recovery-password
```

上限を大きくすると、生成されるHTMLと復元用Markdownも大きくなります。

### 容量警告が表示された

出力サイズが`--warning-mb`の値を超えると警告が表示されます。

初期値は20 MiBです。警告が表示されてもHTML生成は継続します。

警告はエラーではありませんが、旧世代のPCやiPadでMD//WORKSへ復元する場合、処理に時間がかかる可能性があります。

### 大きな資料をMD//WORKSで復元すると重い

Viewer閲覧は軽快でも、Base64画像を含む大きなMarkdownをMD//WORKSへ復元して編集すると、端末性能によって時間がかかります。

対策：

* 画像枚数を20枚程度に減らす
* 資料を前編・後編へ分ける
* 画像容量を事前に小さくする
* 新しいPCまたはiPadで復元・編集する
* `--dry-run`で推定容量を先に確認する

### macOSやLinuxにてerror: externally-managed-environment というエラーでcryptographyがインストールできない

コマンドに --break-system-packages を追加して実行してください。

> ```bash
> python3 -m pip install cryptography --break-system-packages
> 
> ```


---

## 🔄 images2md.pyとの使い分け

| ツール               | 出力                     | 向いている用途                              |
| ----------------- | ---------------------- | ------------------------------------ |
| `images2md.py`    | Markdown               | 画像をまとめた後、文章、動画、PDF、議事録などを追加して編集したい   |
| `images2rHTML.py` | Restricted Viewer HTML | 画像資料をすぐに配布し、一般的なコピー、印刷、意図しない改変を抑制したい |
| MD//WORKS         | Markdown／Viewer        | 詳細編集、Markdown復元、各種Viewer出力を行いたい      |

編集してから配布する場合：

```text
画像
→ images2md.py
→ MD//WORKSで編集
→ Restricted Viewer
```

すぐに配布する場合：

```text
画像
→ images2rHTML.py
→ Restricted Viewer
```

`images2md.py`は編集を始めるための入口、`images2rHTML.py`は画像資料をすぐに配布するための出口として使い分けられます。

---

## 🚧 現在のバージョンでは未対応の機能

* 画像のリサイズ
* 画像の再圧縮
* JPEG画質の変更
* PNG／JPEG／WebP間の自動変換
* EXIF情報の削除や変更
* OCR
* PowerPointファイルからの直接読み込み
* PDFファイルからの直接読み込み
* サブフォルダの再帰検索
* 動画やPDFのViewer内への追加
* Viewer内でのMarkdown復元
* Viewer内でのMarkdown編集
* Recovery passwordの再発行
* パスワードを忘れた場合の復元
* GUI
* ドラッグ＆ドロップ画面
* 外部通信
* 自動アップデート
* スクリーンショットの完全防止
* DRM
* `images2rHTML.py`単体だけで動くテンプレート内蔵版

---

## 🧪 開発・互換性確認用オプション

通常利用では必要ありませんが、開発・試験用に次を使用できます。

### Markdownだけを書き出す

```bash
python images2rHTML.py ./slides --emit-markdown generated.md
```

### Recovery boxだけを書き出す

```bash
python images2rHTML.py ./slides \
  --emit-recovery-box recovery-box.json \
  --recovery-password
```

これらは内部処理とMD//WORKS Restricted Viewer Format v1の互換性を確認するための機能です。

---

## 📄 ライセンス

MIT License
