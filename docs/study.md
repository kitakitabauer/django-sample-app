# Django プロジェクト学習メモ

## フォルダーの全体像

- `django-admin startproject django_sample_app .` のように初期化すると、リポジトリ直下に `manage.py`, `django_sample_app/`, `templates/`, `pyproject.toml` などが生成される。
- `manage.py` はローカル操作の入口で、サーバー起動やマイグレーションを `uv run manage.py …` として実行する。
- `pyproject.toml` と `uv.lock` は依存関係を管理するファイル。`uv` のコマンドで自動更新される。
- `db.sqlite3` はデフォルト DB。ローカル検証ではそのまま、本番では別エンジンに切り替えるのが一般的。

## プロジェクトパッケージ `django_sample_app/`

- `__init__.py` があることで Python パッケージとして認識され、内部モジュールを import できる。
- `settings.py` がグローバル設定の中枢。`INSTALLED_APPS` に `django_sample_app.tasks` を登録して、アプリを有効化する。
- `urls.py` はルート URLConf。`include()` を使ってアプリの URL をまとめて読み込む。`ROOT_URLCONF` がこのファイルを指している。
- `asgi.py` / `wsgi.py` は本番サーバーのエントリーポイント。ASGI/Wsgi サーバーがここから Django を起動する。
- `views.py` は共通ビューを置く場所だが、今回はアプリ内にまとめているので空でも問題ない。

## タスクアプリ `django_sample_app/tasks/`

- `apps.py` の `TasksConfig` で `name = "django_sample_app.tasks"` と設定し、Django に絶対パスを伝える。
- `models.py` にタスクモデル、`admin.py` に管理画面の表示設定、`views.py` に CRUD 処理を実装。
- `forms.py` で `TaskForm` を定義し、タイトル最小文字数・重複チェックや説明との重複禁止といったバリデーションを一元化してビューから利用する。
- `views.py` の `TaskListView.get_queryset()` で `?status=`（`all`/`open`/`done`）と `?q=` パラメーターを解釈し、未完了フィルターやキーワード検索を行う。コンテキストに現在の条件を渡し、テンプレート側でフォームを再表示できるようにする。
- `TaskListView.paginate_by = 10` でページネーションを有効化し、`query_urlencode` をコンテキストに渡してフィルター条件を維持したままページ遷移できるようにする。
- `urls.py` はアプリ専用の URLConf。ルート側で `include("django_sample_app.tasks.urls")` すると、`/` や `/create/` などが有効になる。
- `migrations/` はモデル変更履歴、`tests.py` はアプリ単体テスト用。Django アプリの基本的な構成。

## テンプレート `templates/`

- `templates/base.html` に共通レイアウトを定義し、`templates/tasks/` にリスト・フォーム・削除確認などのテンプレートを配置。
- `settings.py` の `TEMPLATES[0]["DIRS"]` に `BASE_DIR / "templates"` を指定しているので、`render()` 時にこのフォルダーが探索される。
- テンプレート内では Django テンプレート言語を使用し、`{% extends %}`, `{% block %}`, `{% if %}`, `{% url %}` などで構造や制御を書く。

## 学習の進め方のヒント

1. `startproject`（設定）と `startapp`（機能）の役割を区別する。
2. ルート URLConf とアプリ URLConf を切り分けて、URL ルーティングの仕組みを理解する。
3. モデル → マイグレーション → ビュー → テンプレート → フォームの流れを小さな機能で反復して覚える。
4. テンプレートタグ・フィルター、フォーム、管理サイトなど周辺機能を徐々に取り入れる。

## 継続的開発ワークフロー

- `.pre-commit-config.yaml` で Black と Ruff を走らせる。`uv sync --extra dev` で開発ツールを取得し、`uv run pre-commit install` でフックを有効化する。
- 手動で整形・lint したいときは `uv run black .`、`uv run ruff check .` を利用する。
- テストは `uv run manage.py test`（Django TestCase）と `uv run pytest`（pytest-django）を併用し、ビューとモデルの回帰テストをカバーする。
- GitHub Actions（`.github/workflows/ci.yml`）では `uv sync --extra dev` → Black チェック → Ruff lint → `pytest` → `manage.py test` の順に自動実行される。
- Bootstrap を CDN で読み込みつつ、`static/css/main.css`・`static/js/main.js` でカードやトースト表示を微調整。`templates/partials/` にナビゲーションとメッセージを分離して再利用性を高める。
- メッセージフレームワークを導入し、作成・更新・削除・トグル操作時に通知を表示。トーストは Bootstrap の Toast コンポーネントで自動表示される。
