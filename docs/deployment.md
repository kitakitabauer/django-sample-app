# デプロイと運用ガイド

Django アプリケーションを本番環境にデプロイする際のポイントをまとめました。環境変数で設定を外部化し、静的ファイル・アプリサーバー・データベースの扱いを整理します。

---

## 1. 環境変数の管理

`django_sample_app/settings.py` は環境変数から主要設定を読み込みます。ローカル開発では `.env` を用意し、`python-dotenv` が自動で読み込みます。

`.env.example` をコピーして必要な値を設定してください。

```bash
cp .env.example .env
```

| 変数名 | 説明 |
| --- | --- |
| `DJANGO_SECRET_KEY` | Django のシークレットキー。本番では十分に長くランダムな値にする。 |
| `DJANGO_DEBUG` | `True`/`False` でデバッグモードを制御。通常は本番で `False`。 |
| `DJANGO_ALLOWED_HOSTS` | `example.com,api.example.com` のようにアクセスを許可するホストをカンマ区切りで指定。 |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | HTTPS のオリジンを指定（例: `https://example.com`）。リバースプロキシ越しで必要に応じて設定。 |
| `DATABASE_URL` | 例: `postgresql://USER:PASSWORD@HOST:PORT/DBNAME`。未設定時は SQLite を使用。 |
| `DJANGO_DB_SSL` | Postgres などで SSL を強制したい場合に `True` を指定。 |

`DJANGO_SECRET_KEY` が未設定で `DJANGO_DEBUG=False` の場合は起動時にエラーとなります。

---

## 2. 静的ファイル (`collectstatic`)

本番環境では `STATIC_ROOT` (`staticfiles/`) に静的ファイルを収集して Web サーバーから配信します。

```bash
uv run manage.py collectstatic
```

生成された `staticfiles/` ディレクトリを Nginx などのフロントエンドで配信してください。`STATICFILES_DIRS` には開発用の `static/` ディレクトリが登録されています。

---

## 3. Gunicorn / ASGI サーバー

### WSGI (Gunicorn)

アプリを WSGI モードで動かす場合は以下のコマンド例を参照してください。

```bash
uv run gunicorn django_sample_app.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

必要に応じて `--timeout` やロギング設定を追加します。`uv` 環境内であれば依存関係は pyproject の内容でインストールされます。

### ASGI (Uvicorn / Daphne など)

非同期サーバーを使う場合は ASGI アプリを指定します。

```bash
uv run uvicorn django_sample_app.asgi:application --host 0.0.0.0 --port 8000
```

Uvicorn や Daphne を使う際は `uv add uvicorn[standard]` などで依存を追加してください。

---

## 4. SQLite から PostgreSQL への移行手順

1. Postgres サーバーにデータベース・ユーザーを作成します。
2. 依存パッケージとして `psycopg` を追加します。
   ```bash
   uv add "psycopg[binary]>=3.2"
   ```
3. `.env` の `DATABASE_URL` を Postgres の接続文字列に更新します。
4. 既存のマイグレーションを適用します。
   ```bash
   uv run manage.py migrate
   ```
5. SQLite のデータを移行したい場合は、`dumpdata` / `loaddata` もしくは外部ツール（`python -m django_coreserializer` 等）を用いてデータをエクスポート＆インポートします。

例:

```bash
uv run manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission > fixtures.json
uv run manage.py migrate
uv run manage.py loaddata fixtures.json
```

---

## 5. 運用時のチェックリスト

- [ ] `DJANGO_DEBUG=False` で起動しているか
- [ ] `DJANGO_SECRET_KEY` が十分に強い値になっているか
- [ ] `DJANGO_ALLOWED_HOSTS` / `DJANGO_CSRF_TRUSTED_ORIGINS` が正しく設定されているか
- [ ] `collectstatic` を実行し、静的ファイルを Web サーバーに設定したか
- [ ] Postgres の接続に `sslmode=require` 等のセキュリティ設定を適用したか
- [ ] プロセスマネージャー（systemd, supervisord など）やリバースプロキシ (Nginx) との連携を整備したか

これらを満たすことで、安全に本番運用へ移行できます。
