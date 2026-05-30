"""Script helpers used by regression tests and ad hoc runbooks.

Several historical data-creation scripts live under ``scripts/create-datas``
because they are usually run as command-line files.  Exposing that directory on
the package path keeps imports such as ``scripts.create_v4_sqli_failure_slice``
working without duplicating the scripts.
"""

from __future__ import annotations

from pathlib import Path

_CREATE_DATAS = Path(__file__).resolve().parent / "create-datas"
if _CREATE_DATAS.is_dir():
    __path__.append(str(_CREATE_DATAS))
