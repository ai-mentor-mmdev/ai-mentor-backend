from fastapi import FastAPI

from internal import interface
from internal import model


def NewHTTP(
        db: interface.IDB,
        chat_controller: interface.IChatController,
        edu_student_controller: interface.IEduStudentController,  # Добавить параметр
        http_middleware: interface.IHttpMiddleware,
        prefix: str
):
    app = FastAPI()
    include_middleware(app, http_middleware)

    include_db_handler(app, db, prefix)
    include_chat_handlers(app, chat_controller, prefix)
    include_student_handlers(app, edu_student_controller, prefix)  # Добавить вызов

    return app


def include_middleware(
        app: FastAPI,
        http_middleware: interface.IHttpMiddleware
):
    http_middleware.logger_middleware03(app)
    http_middleware.metrics_middleware02(app)
    http_middleware.trace_middleware01(app)



def include_chat_handlers(
        app: FastAPI,
        chat_controller: interface.IChatController,
        prefix: str
):
    app.add_api_route(
        prefix + "/message/send",
        chat_controller.send_message_to_expert,
        methods=["POST"],
        summary="Отправить сообщение регистратору",
        description="Отправляет сообщение регистратору"
    )

def include_student_handlers(
        app: FastAPI,
        student_controller: interface.IStudentController,
        prefix: str
):
    app.add_api_route(
        prefix + "/student/{student_id}",
        student_controller.get_student_by_id,
        methods=["GET"],
        summary="Получить информацию о студенте",
        description="Возвращает полную информацию о студенте по его ID"
    )


def include_db_handler(app: FastAPI, db: interface.IDB, prefix: str):
    app.add_api_route(prefix + "/table/create", create_table_handler(db), methods=["GET"])
    app.add_api_route(prefix + "/table/drop", drop_table_handler(db), methods=["GET"])


def create_table_handler(db: interface.IDB):
    async def create_table():
        try:
            await db.multi_query(model.create_queries)
        except Exception as err:
            raise err

    return create_table


def drop_table_handler(db: interface.IDB):
    async def delete_table():
        try:
            await db.multi_query(model.drop_queries)
        except Exception as err:
            raise err

    return delete_table