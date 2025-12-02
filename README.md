📘 GradeGear – 科目・タスク成績管理アプリ

自分の大学生活を最適化するために作った成績管理アプリ「GradeGear」。
科目・タスクの管理、成績予測、必要点数の計算などを 完全ローカルAPI（FastAPI） で実行できる学習用 Web アプリです。

🚀 Features（できること）
✏️ 科目管理

科目の追加 / 削除

担当教員、単位数、曜日・コマ、メモの記録

左側リストに科目一覧が表示され、選択すると詳細を確認可能

🗂️ タスク管理

タスクの追加 / 削除

種類（type）、配点（weight）、スコア、期限など

科目ごとのタスクリストを自動表示

📊 成績サマリー表示

科目ごとに成績サマリーを自動計算

現在の予測スコア、配点合計、取得済み配点などを表示

🎯 目標成績までの必要点数計算

「Aを取りたい」「Sを取りたい」など

目標スコアから逆算して、残りのタスクで必要な平均点を計算

📱 UI

HTML / CSS / JS のみで構築された軽量 UI

保存時にトースト通知が出る“アプリっぽい”デザイン

レスポンシブ対応でスマホでも表示可能

🛠️ Technology Stack
Backend（API）

FastAPI

SQLAlchemy

SQLite（ローカルDB）

Pydantic v1

Frontend

HTML / CSS / JavaScript（Vanilla）

Fetch API

No frameworks（軽量構成）

📂 Directory Structure（主な構成）
gradegear/
│── app/
│   ├── main.py          # FastAPI ルート定義
│   ├── schemas.py       # Pydantic スキーマ
│   ├── crud.py          # DB操作ロジック
│   ├── models.py        # SQLAlchemy モデル
│   └── database.py      # DB 接続設定
│
├── index.html           # フロントエンド UI
└── README.md            # この説明ファイル

🔧 Setup（ローカル環境で動かす）
1. Clone this repo
git clone https://github.com/Nakamura0902/gradegear.git
cd gradegear

2. Install dependencies
pip install -r requirements.txt

3. Run FastAPI server
uvicorn app.main:app --reload

4. Open the frontend

index.html をブラウザで開くだけで OK。

🖼️ Screenshots（イメージ）

※ 必要なら後であなたの画面のスクショ入れられるように見出しだけつけてある！

![screenshot1](image1.png)
![screenshot2](image2.png)

🌱 Future Plans（今後実装予定）

科目の色テーマ設定

タスクの進捗グラフ

学期ごとのGPA集計

クラウドへのデプロイ（Railway / Render）

アカウント機能（JWT ベース）

バックアップ / 復元機能

🧑‍💻 Author

Ayaki (Nakamura0902)

大学生エンジニア

FastAPI / Python / Webアプリ学習中

毎日努力と自己改善の記録を継続中

GitHub: https://github.com/Nakamura0902

⭐ 去年より成長した自分へ

このアプリは
「凡人では終わりたくない」
「自分を強くするための努力」
その象徴みたいな作品。

次のステップも一緒に作っていこう。

🔥 Ready to use!

git clone して uvicorn 叩けば即使える。
