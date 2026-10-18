# NAOの副業ラボ

会社員でも無理なく始められる副業の情報をまとめた静的サイトです。GitHub Pagesで公開しています。

- 公開URL: https://nao-web-lab.github.io/nao-fukugyou-lab/
- 技術構成: 素のHTML / CSS（フレームワーク・ビルドツール不使用）

## 構成

```
index.html          トップページ
articles.html        記事一覧
articles/*.html       各記事（19本）
about.html           運営者情報・サイトについて
contact.html          お問い合わせ（フォーム）
privacy.html          プライバシーポリシー（Amazonアソシエイト表記・Cookie/GA表記を含む）
css/style.css         共通スタイル
js/main.js            共通スクリプト（メニュー・カテゴリ絞り込み・簡易診断）
assets/*.png          各サービスの公式サイト・ストア画面のスクリーンショット
assets/ai/*.webp      記事冒頭のイメージ画像（AI生成。顔・文字・ロゴを含まないもの）
assets/og/*.jpg       SNS共有用のOGP画像（1200x630）
sitemap.xml / robots.txt
```

## 記事を追加するときのチェック

- `articles.html` のカード、`sitemap.xml`、関連記事の内部リンクを追加する
- 手数料・制度・数値は公式サイトで確認し、確認日と出典リンクを本文に入れる
- アフィリエイト・紹介リンクがある記事は、冒頭の `pr-note`（PR表記）と末尾の `disclosure-note` を入れ、リンクに `rel="sponsored"` を付ける
- スクリーンショットや画像は `width` / `height` 属性を付ける（レイアウトのずれ防止）
- 公式情報で確かめて記事を直したときは、トップ（`index.html`）の「検証ログ」に1行追加する（日付・項目・出典・反映した記事）。実際に確認していない項目は載せない

## 公開前にやること（Amazonアソシエイト審査に向けて）

1. ~~お問い合わせフォームの接続先を差し替える~~（対応済み）
   `contact.html` は [Formspree](https://formspree.io/) のフォームに接続済みです。受信通知の宛先や迷惑メール設定は Formspree の管理画面で変更できます。

2. **Amazonアソシエイトのトラッキングタグを差し替える**
   `articles/10-gadgets-for-side-work.html` 内のリンクにある `tag=YOUR_ASSOCIATE_ID-22` を、
   Amazonアソシエイトに登録して発行された自分のトラッキングIDに置き換えてください。

3. 内容を一通り読み、事実関係やご自身の経験と齟齬がないか確認してください。
