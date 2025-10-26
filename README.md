# 🐍 Django Sample App (with uv)

Python パッケージマネージャ **[uv](https://github.com/astral-sh/uv)** と Django で作成した ToDo リストのサンプルアプリです。最小構成で CRUD の流れを確認できます。

---

## 🚀 セットアップ

1. **プロジェクト作成**

   ```bash
   mkdir django-sample-app
   cd django-sample-app
   uv init
   ```

2. **仮想環境の作成と有効化**

   ```bash
   uv venv
   ```

   - macOS / Linux: `source .venv/bin/activate`
   - Windows (PowerShell): `.venv\Scripts\Activate.ps1`

3. **Django のインストール**

   ```bash
   uv add "Django>=5.0,<6.0"
   ```

4. **プロジェクトとアプリ作成**

   ```bash
   django-admin startproject django_sample_app .
   python manage.py startapp tasks
   ```

5. **マイグレーション実行**

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **スーパーユーザー作成**

   ```bash
   python manage.py createsuperuser
   ```

7. **開発サーバー起動**

   ```bash
   uv run manage.py runserver
   ```

   - アプリ: <http://127.0.0.1:8000/>
   - 管理画面: <http://127.0.0.1:8000/admin/>

---

## 🛠 コード品質チェック

開発ツール（Black / Ruff / pre-commit）を含めてセットアップする:

```bash
uv sync --extra dev
```

整形と lint の実行例:

```bash
uv run black .
uv run ruff check .
```

### pre-commit フックを入れる

```bash
uv run pre-commit install
uv run pre-commit run --all-files
```

## ✅ チーム向け環境再現

```bash
uv sync --extra dev
```

GitHub Actions（`.github/workflows/ci.yml`）でも同じコマンドで依存関係を準備し、Black / Ruff / Django テストを自動実行します。

---

## 🧾 ライセンス

MIT License
