# pytest cache directory #

This directory contains data from the pytest's cache plugin,
which provides the `--lf` and `--ff` options, as well as the `cache` fixture.

**Do not** commit this to version control.

See [the docs](https://docs.pytest.org/en/stable/how-to/cache.html) for more information.

# フォルダ構成

- .env
- body.json
- requirements.txt
- 新規 テキスト ドキュメント.txt
- app/
  - \_\_init__.py
  - main.py
  - database/
    - db.py
    - products.db
  - routers/
    - \_\_init__.py
    - chat.py
    - product.py
    - index.py
  - tests/
    - \_\_init__.py
    - conftest.py
    - test_chat.py

