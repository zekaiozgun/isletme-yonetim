"""Her DB degisikligini (CREATE/UPDATE/DELETE) otomatik olarak audit_logs'a
yazan mapper-seviyesi SQLAlchemy event listener'lari. `Mapper` sinifina
(instance degil, sinifin kendisine) baglanmak, TUM mapped modeller icin
gecerli olmasini saglar - hicbir servis fonksiyonu bunu elle cagirmak
zorunda degildir (Anayasa m.5 ruhu: turetilmis/otomatik bir islem, tekrar
tekrar elle yazilmaz).

after_insert/after_update/after_delete, ilgili SQL zaten calistiktan sonra
tetiklenir (PK'ler -otomatik artan olanlar dahil- bu noktada hazirdir) ve
ayni DB baglantisi/transaction'i (connection) alir - bu yuzden ORM Session
uzerinden session.add() yerine dogrudan connection.execute() ile yaziyoruz;
boylece Session'in flush dongusune mudahale etmiyoruz, sonsuz dongu riski
de yok.
"""

from sqlalchemy import event, insert
from sqlalchemy.orm import Mapper

from app.core.request_context import current_user_id
from app.modules.audit.models import AuditLog

_EXCLUDED_TABLES = {"audit_logs"}


def _record(connection, target, action: str) -> None:
    table_name = target.__tablename__
    if table_name in _EXCLUDED_TABLES:
        return
    pk_columns = target.__mapper__.primary_key
    record_id = "-".join(str(getattr(target, col.name)) for col in pk_columns)
    connection.execute(
        insert(AuditLog.__table__).values(
            user_id=current_user_id.get(),
            action=action,
            table_name=table_name,
            record_id=record_id,
        )
    )


def _after_insert(mapper, connection, target) -> None:
    _record(connection, target, "CREATE")


def _after_update(mapper, connection, target) -> None:
    _record(connection, target, "UPDATE")


def _after_delete(mapper, connection, target) -> None:
    _record(connection, target, "DELETE")


event.listen(Mapper, "after_insert", _after_insert)
event.listen(Mapper, "after_update", _after_update)
event.listen(Mapper, "after_delete", _after_delete)
