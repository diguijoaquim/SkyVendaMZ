from fastapi_utils.tasks import repeat_every
from fastapi import FastAPI
from controlers.pedido import verificar_liberacao_automatica
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

def init_scheduler(app: FastAPI):
    scheduler = AsyncIOScheduler()
    
    # Agenda a verificação para rodar todos os dias à meia-noite
    scheduler.add_job(
        verificar_liberacao_automatica,
        CronTrigger(hour=0, minute=0),  # Executa à meia-noite
        id="verificar_liberacao",
        name="Verifica e libera pedidos após prazo de confirmação",
        replace_existing=True,
    )
    
    @app.on_event("startup")
    async def start_scheduler():
        scheduler.start()
    
    @app.on_event("shutdown")
    async def shutdown_scheduler():
        scheduler.shutdown()

def init_scheduler(app: FastAPI):
    @app.on_event("startup")
    @repeat_every(seconds=60 * 60 * 24)  # Executa uma vez por dia
    async def schedule_verificar_liberacao():
        await verificar_liberacao_automatica()


