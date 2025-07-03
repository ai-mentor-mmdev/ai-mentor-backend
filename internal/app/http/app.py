from fastapi import FastAPI

from internal import interface
from internal import model


def NewHTTP(
        db: interface.IDB,
        edu_chat_controller: interface.IEduChatController,
        http_middleware: interface.IHttpMiddleware,
        prefix: str
):
    app = FastAPI()
    include_middleware(app, http_middleware)

    include_db_handler(app, db, prefix)
    include_edu_chat_handlers(app, edu_chat_controller, prefix)

    return app


def include_middleware(
        app: FastAPI,
        http_middleware: interface.IHttpMiddleware
):
    http_middleware.logger_middleware03(app)
    http_middleware.metrics_middleware02(app)
    http_middleware.trace_middleware01(app)


def include_edu_chat_handlers(
        app: FastAPI,
        edu_chat_controller: interface.IEduChatController,
        prefix: str
):
    app.add_api_route(
        prefix + "/edu/message/send/interview-expert",
        edu_chat_controller.send_message_to_interview_expert,
        methods=["POST"],
        summary="Отправить сообщение интервью-эксперту",
        description="Отправляет сообщение интервью-эксперту для подготовки к собеседованию"
    )

    app.add_api_route(
        prefix + "/edu/message/send/teacher",
        edu_chat_controller.send_message_to_teacher,
        methods=["POST"],
        summary="Отправить сообщение преподавателю",
        description="Отправляет сообщение преподавателю для изучения материала"
    )

    app.add_api_route(
        prefix + "/edu/message/send/test-expert",
        edu_chat_controller.send_message_to_test_expert,
        methods=["POST"],
        summary="Отправить сообщение тест-эксперту",
        description="Отправляет сообщение тест-эксперту для проверки знаний"
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