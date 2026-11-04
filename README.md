# デイリーニュースまとめ (Daily News Summary)

主要なIT・モバイル・カメラ・音楽・車の最新ニュースを自動収集し、当日の記事をジャンル別にまとめて閲覧できるWebポータル（PWA対応）です。
**GitHub Actions** と **GitHub Pages** を使用し、**完全無料**で運用できます。

---

## 主な特徴

- ⏰ **毎日7:00〜22:00（3時間おき自動更新）**: GitHub Actions の定期実行（cron）により、日中の最新ニュースを自動集約（深夜はエコ停止）。
- 🏷️ **ジャンル別タブ**: 「テクノロジー・AI」「モバイル・通信」「カメラ・写真」「音楽・DJ」「自動車」「家電・ライフ」に分類。
- 🖼️ **サムネイル画像表示**: OGP（Open Graph Protocol）を自動解析し、各記事のサムネイル画像を表示。
- 🤖 **AIによる3行箇条書き要約**: Google Gemini API（無料枠）と連携し、記事ごとの重要ポイントを3行で要約（※未設定でもRSS概要で自動動作）。
- 🌙 **ダークモード対応**: OS設定に連動し、手動切り替えも可能。
- 📖 **既読・お気に入り管理**: ブラウザのLocalStorageを活用し、既読記事のグレーアウトや★お気に入り記事の保存・絞り込みに対応。
- 📱 **Androidアプリ化 (PWA)**: Chromeブラウザから「ホーム画面に追加」するだけで、独立したAndroidネイティブアプリ感覚で全画面起動。

---

## 収集対象メディア（12サイト）

1. **Impress Watch各誌**:
   - [ケータイ Watch](https://k-tai.watch.impress.co.jp/)
   - [Car Watch](https://car.watch.impress.co.jp/)
   - [AI Watch](https://ai.watch.impress.co.jp/)
   - [PC Watch](https://pc.watch.impress.co.jp/)
   - [デジカメ Watch](https://dc.watch.impress.co.jp/)
   - [家電 Watch](https://kaden.watch.impress.co.jp/)
2. **ITmedia各誌**:
   - [ITmedia Top](https://www.itmedia.co.jp/)
   - [ITmedia Mobile](https://www.itmedia.co.jp/mobile/)
3. [ギズモード・ジャパン](https://www.gizmodo.jp/)
4. [デジカメinfo](https://digicame-info.com/)
5. [DTMステーション](https://www.dtmstation.com/)
6. [Real Sound (DJタグ)](https://realsound.jp/tag/dj)

---

## セットアップ手順（完全無料で動かす方法）

### 1. GitHubリポジトリを作成してプッシュ
本プロジェクトのファイルを、あなたのGitHubアカウントに新規作成したリポジトリにプッシュします。

```bash
cd c:\ProjectAI\DailyNews
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/あなたのユーザー名/リポジトリ名.git
git push -u origin main
```

### 2. GitHub Pagesの設定を有効化
1. リポジトリの **[Settings]** タブを開きます。
2. 左メニューの **[Pages]** をクリックします。
3. **[Build and deployment]** > **[Source]** を **「GitHub Actions」** に変更します。

### 3. （任意・推奨）Gemini APIキーの設定（無料の3行AI要約用）
GeminiのAPIキーを設定すると、毎日の記事が自動で読みやすい3行の箇条書きに要約されます（無料枠で十分賄えます）。
※設定しなくても、通常のRSS概要が表示されるため動作に影響はありません。

1. [Google AI Studio](https://aistudio.google.com/) にアクセスし、無料のAPIキーを取得します。
2. GitHubリポジトリの **[Settings]** > **[Secrets and variables]** > **[Actions]** を開きます。
3. **[New repository secret]** をクリックします。
   - **Name**: `GEMINI_API_KEY`
   - **Secret**: 取得したAPIキー
4. **[Add secret]** をクリックします。

### 4. 手動で初回実行を試す
毎日18:00 (JST) に自動で更新されますが、今すぐ記事を取得したい場合は手動実行できます。

1. リポジトリの **[Actions]** タブを開きます。
2. 左側のワークフロー一覧から **[Daily News Collector & Deploy]** を選択します。
3. **[Run workflow]** ボタンをクリックして実行します。
4. 1〜2分で処理が完了し、`https://あなたのユーザー名.github.io/リポジトリ名/` に一覧ページが公開されます！

---

## Androidスマホでのアプリ化手順 (PWA)

1. Androidスマートフォンの **Google Chrome** で公開されたWebサイトURLを開きます。
2. 画面右上のメニュー（縦の3点リーダー `︙`）をタップします。
3. **「ホーム画面に追加」** または **「アプリをインストール」** をタップします。
4. ホーム画面に専用アプリアイコンが追加され、以降はワンタップで全画面アプリとして閲覧できます。

---

## ローカル環境でのテスト実行

```bash
# 依存ライブラリのインストール
pip install -r scripts/requirements.txt

# ニュース収集スクリプトの実行（public/data/news.json が生成されます）
python scripts/collector.py

# ローカルWebサーバーの起動（ブラウザで http://localhost:8000/public/ を開く）
python -m http.server 8000
```
