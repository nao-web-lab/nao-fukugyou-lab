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
js/main.js            共通スクリプト（メニュー・カテゴリ絞り込み・簡易診断・ニュース絞り込み）
news.html            副業ニュース（自動更新。手で編集しない）
data/news.json        副業ニュースの蓄積データ（自動更新）
scripts/update_news.py  ニュース取得スクリプト（標準ライブラリのみ）
.github/workflows/update-news.yml  毎日の自動実行
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

## 副業ニュースの自動更新

- 毎日 7:00 と 18:30（日本時間）に GitHub Actions が `scripts/update_news.py` を実行し、国民生活センター・消費者庁・金融庁・厚生労働省・国税庁の公開情報から副業に関係する見出しを集めて、`news.html` とトップの「副業ニュース」欄、`data/news.json` を更新します。変更があるときだけコミットされ、そのまま公開されます。
- 掲載するのは見出し・日付・出典・公式ページへのリンクだけです（本文の転載や要約はしません）。
- 取得元や抽出キーワードを変えるときは、`scripts/update_news.py` の `SOURCES` と `TOPICS` を編集します。ローカルでの確認は `python scripts/update_news.py`。
- 手動で今すぐ更新したいときは、GitHub の Actions タブから「副業ニュースの自動更新」を Run workflow します。
- 公開リポジトリは60日間コミットがないと定時実行が止まります。ニュースの更新コミットが活動として数えられるため通常は止まりませんが、止まった場合は Actions タブで再開してください。

## 公開前にやること（Amazonアソシエイト審査に向けて）

1. ~~お問い合わせフォームの接続先を差し替える~~（対応済み）
   `contact.html` は [Formspree](https://formspree.io/) のフォームに接続済みです。受信通知の宛先や迷惑メール設定は Formspree の管理画面で変更できます。

2. **Amazonアソシエイトのトラッキングタグを差し替える**
   `articles/10-gadgets-for-side-work.html` 内のリンクにある `tag=YOUR_ASSOCIATE_ID-22` を、
   Amazonアソシエイトに登録して発行された自分のトラッキングIDに置き換えてください。

3. 内容を一通り読み、事実関係やご自身の経験と齟齬がないか確認してください。
