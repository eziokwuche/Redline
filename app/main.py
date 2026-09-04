from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import compare, grade, upload


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title='resume-ats', lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000', 'http://localhost:5173', 'http://localhost:5174', 'http://localhost:5175', 'http://[::1]:5173'],
    allow_origin_regex=r'https?://(localhost|127\.0\.0\.1|\[::1\]):\d+',
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(upload.router, prefix='/api')
app.include_router(grade.router, prefix='/api')
app.include_router(compare.router, prefix='/api')


@app.get('/health')
def health_check():
    return {'status': 'ok'}
