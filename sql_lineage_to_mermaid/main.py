#!/usr/bin/env python3
"""
SQLファイル群を静的解析し、テーブル/クエリ間の依存関係をMermaidのグラフとして出力する。

使い方:
    python sql_lineage_to_mermaid.py <SQLファイルが入ったディレクトリ> [--dialect bigquery]

前提:
    - 1ファイル = 1クエリ(1テーブルの定義)を想定
    - CREATE TABLE / CREATE OR REPLACE TABLE / INSERT INTO / MERGE INTO の
      いずれかで出力先テーブルを特定する
    - 出力先が特定できないファイル(SELECTのみ等)は、ファイル名をノード名として扱う
    - CTE(WITH句で定義した一時テーブル)は依存関係のノードから除外する
"""

import argparse
import sys
from pathlib import Path

import sqlglot
from sqlglot import exp


def extract_target_table(statement: exp.Expression) -> str | None:
    """CREATE / INSERT / MERGE から出力先テーブル名を抽出する"""
    if isinstance(statement, exp.Create):
        table = statement.this
        if isinstance(table, exp.Schema):
            table = table.this
        if isinstance(table, exp.Table):
            return table.name
    if isinstance(statement, (exp.Insert, exp.Merge)):
        table = statement.this
        if isinstance(table, exp.Table):
            return table.name
    return None


def extract_source_tables(statement: exp.Expression) -> set[str]:
    """クエリ内で参照している全テーブルから、CTE名を除いたものを返す"""
    cte_names = {cte.alias_or_name for cte in statement.find_all(exp.CTE)}
    target_table = extract_target_table(statement)

    sources = set()
    for table in statement.find_all(exp.Table):
        name = table.name
        if name in cte_names:
            continue
        if name == target_table:
            continue
        sources.add(name)
    return sources


def parse_sql_file(path: Path, dialect: str) -> tuple[str, set[str]]:
    """1つのSQLファイルから (出力先ノード名, 参照元テーブル集合) を返す"""
    sql = path.read_text(encoding="utf-8")
    try:
        statements = sqlglot.parse(sql, dialect=dialect)
    except Exception as e:
        print(f"[WARN] パース失敗: {path.name}: {e}", file=sys.stderr)
        return path.stem, set()

    target = None
    sources: set[str] = set()
    for statement in statements:
        if statement is None:
            continue
        t = extract_target_table(statement)
        if t:
            target = t
        sources |= extract_source_tables(statement)

    node_name = target or path.stem
    return node_name, sources


def build_edges(sql_dir: Path, dialect: str) -> set[tuple[str, str]]:
    edges: set[tuple[str, str]] = set()
    for path in sorted(sql_dir.glob("*.sql")):
        target, sources = parse_sql_file(path, dialect)
        for src in sources:
            edges.add((src, target))
    return edges


def to_mermaid(edges: set[tuple[str, str]]) -> str:
    lines = ["graph LR"]

    def sanitize(name: str) -> str:
        # Mermaidのノードidに使えない文字(., -等)を置換
        return name.replace(".", "_").replace("-", "_")

    ids = {}
    label_lines = []
    for src, dst in sorted(edges):
        for name in (src, dst):
            if name not in ids:
                ids[name] = sanitize(name)
                label_lines.append(f'    {ids[name]}["{name}"]')

    lines.extend(label_lines)
    for src, dst in sorted(edges):
        lines.append(f"    {ids[src]} --> {ids[dst]}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sql_dir", type=Path, help="SQLファイルが入ったディレクトリ")
    parser.add_argument("--dialect", default="bigquery", help="SQL方言 (デフォルト: bigquery)")
    args = parser.parse_args()

    edges = build_edges(args.sql_dir, args.dialect)
    print(f"```mermaid\n{to_mermaid(edges)}\n```")


if __name__ == "__main__":
    main()
