from fastapi import APIRouter
from fastapi.routing import APIRoute

router = APIRouter()

def custom_generate_unique_id(route: APIRoute): return f"{route.tags[0]}_api_{route.name}"

api_router = APIRouter(generate_unique_id_function=custom_generate_unique_id)

api_router.include_router(router, tags=["applications"])