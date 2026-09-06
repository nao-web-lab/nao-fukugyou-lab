# NAOの副業ラボ

会社員でも無理なく始められる副業の情報をまとめた静的サイトです。GitHub Pagesで公開しています。

- 公開URL: https://naofukugyou623-ux.github.io/nao-fukugyou-lab/
- 技術構成: 素のHTML / CSS（フレームワーク・ビルドツール不使用）

## 構成

```
index.html          トップページ
articles.html        記事一覧
articles/*.html       各記事（10本）
about.html           運営者情報・サイトについて
contact.html          お問い合わせ（フォーム）
privacy.html          プライバシーポリシー（Amazonアソシエイト表記・Cookie/GA表記を含む）
css/style.css         共通スタイル
sitemap.xml / robots.txt
```

## 公開前にやること（Amazonアソシエイト審査に向けて）

1. **お問い合わせフォームの接続先を差し替える**
   `contact.html` の `<form action="https://formspree.io/f/YOUR_FORM_ID">` を、
   [Formspree](https://formspree.io/) などで自分のアカウントを作成して発行したフォームIDに置き換えてください。
   （アカウント作成はご本人が行う必要があるため、プレースホルダのままにしています）

2. **Amazonアソシエイトのトラッキングタグを差し替える**
   `articles/10-gadgets-for-side-work.html` 内のリンクにある `tag=YOUR_ASSOCIATE_ID-22` を、
   Amazonアソシエイトに登録して発行された自分のトラッキングIDに置き換えてください。

3. 内容を一通り読み、事実関係やご自身の経験と齟齬がないか確認してください。
