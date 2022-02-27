def get_scheduler():
    from app.main import app
    return app.state.scheduler
