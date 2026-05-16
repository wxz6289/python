import json
from typing import List, Optional

from sqlalchemy.exc import SQLAlchemyError

from log import MyLogger

from sqlalchemy import create_engine, inspect, text

log = MyLogger().get_logger()

class DBManager:
    def __init__(self, connection_string: str):
        self.engine = create_engine(connection_string, pool_size=5)

    def get_table_names(self) -> list[str]:
        try:
          inspector = inspect(self.engine)
          return inspector.get_table_names()
        except Exception as e:
          log.exception(e)
          raise ValueError(f'获取表名失败: {e}')

    def get_tables_with_comments(self) -> List[dict]:
      """
      获取数据库中所有表名及其描述信息
      Returns:
        List[dict]:  包含'table_name'和'table_comment'的列表
      """
      try:
        query = text("""
        SELECT TABLE_NAME, TABLE_COMMENT
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_SCHEMA = DATABASE()
        AND TABLE_TYPE = 'BASE TABLE'
        ORDER BY TABLE_NAME
        """)
        with self.engine.connect() as connection:
          result = connection.execute(query)
          return [{'table_name': row[0], 'table_comment': row[1]} for row in result]
      except SQLAlchemyError as e:
        log.exception(e)
        raise ValueError(f'获取表名及其描述失败: {e}')

    def get_table_schema(self, table_names: Optional[List[str]] = None) -> str:
      """
      获取数据库中指定表名的表结构
      Args:
        table_names: 表名列表
      Returns:
        str: 表结构
      """
      try:
        inspector = inspect(self.engine)
        schema_info: list[str] = []
        target_tables = table_names if table_names else self.get_table_names()
        for table_name in target_tables:
          columns = inspector.get_columns(table_name)
          pk_constraint = inspector.get_pk_constraint(table_name)
          fk_constraint = inspector.get_foreign_keys(table_name)
          primary_keys = pk_constraint['constrained_columns'] if pk_constraint else []
          indexes = inspector.get_indexes(table_name)

          table_schema = f"表名: {table_name}\n"
          table_schema += "字段:\n"
          for column in columns:
            pk_indicator = '(主键)' if column['name'] in primary_keys else ''
            comment = column.get('comment') or '无注释'
            table_schema += (
              f"  字段名: {column['name']} | 字段类型: {column['type']} "
              f"{pk_indicator} [注释: {comment}]\n"
            )

          if fk_constraint:
            table_schema += "外键:\n"
            for fk in fk_constraint:
              table_schema += (
                f" - {fk['constrained_columns']} -> "
                f"{fk['referred_table']}.{fk['referred_columns']}\n"
              )

          if indexes:
            table_schema += "索引:\n"
            for index in indexes:
              name = index.get('name') or ''
              if name.startswith('sqlite_'):
                continue
              kind = '唯一索引' if index['unique'] else '普通索引'
              table_schema += f" - {name}: {index['column_names']} ({kind})\n"

          schema_info.append(table_schema)

        return '\n\n'.join(schema_info)
      except SQLAlchemyError as e:
        log.exception(e)
        raise ValueError(f'获取表结构失败: {e}')

    def execute_sql(self, sql: str) -> str:
      """
      执行SQL语句并返回结果（仅允许只读语句）
      Args:
        sql: SQL语句
      Returns:
        str: JSON 字符串形式的查询结果，或提示信息
      """
      query_lower = sql.lower().strip()
      if not query_lower.startswith(('select', 'with')):
        raise ValueError('出于安全考虑，仅允许执行 SELECT 语句和 WITH 语句')
      try:
        with self.engine.connect() as connection:
          result = connection.execute(text(sql))
          rows = result.fetchmany(100)
          if not rows:
            return '查询结果为空'
          columns = list(result.keys())
          result_data = []
          for row in rows:
            row_dict = {}
            for i, column in enumerate(columns):
              value = row[i]
              if value is None:
                row_dict[column] = None
                continue
              try:
                json.dumps(value)
                row_dict[column] = value
              except (TypeError, ValueError):
                row_dict[column] = str(value)
            result_data.append(row_dict)
          return json.dumps(result_data, ensure_ascii=False, indent=2, default=str)
      except SQLAlchemyError as e:
        log.exception(e)
        raise ValueError(f'执行SQL语句失败: {e}')

    def validate_sql(self, sql: str) -> str:
      """
      验证SQL语句是否合法
      Args:
        sql: SQL语句
      Returns:
        bool: 是否合法
      """
      sql = sql.strip()
      if not sql:
        return '错误:查询不能为空'
      try:
        with self.engine.connect() as connection:
          parsed_query = text( sql)
          compiled = parsed_query.compile(compile_kwargs={"literal_binds": True})
          return "SQL语句看起来是正确的"
      except SQLAlchemyError as e:
        log.exception(e)
        return f'SQL语法错误: {e}'

if __name__ == '__main__':
    db_connection_string = "mysql+pymysql://king:king123@localhost:3306/mybatis?charset=utf8mb4"
    db = DBManager(db_connection_string)
    log.info(db.get_table_names())
    log.info(db.get_table_schema())
    log.info(db.execute_sql('select * from user'))
    log.info(db.validate_sql('select * from user'))
    log.info(db.get_tables_with_comments())
