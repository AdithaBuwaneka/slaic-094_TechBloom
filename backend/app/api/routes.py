from fastapi import APIRouter

# Import all modular route modules
from app.api.v1 import (
    base,
    agents,
    data,
    route,
    personalization,
    fare,
    accessibility,
    language,
    disruption,
    local_knowledge,
    orchestration,
    websocket_api,
    users,
    journey_planning,
    external_apis
)

# Create main router
router = APIRouter()

# Include all route modules with appropriate prefixes
router.include_router(base.router, tags=["base"])
router.include_router(agents.router, prefix="/agents", tags=["agents"])
router.include_router(data.router, prefix="/data", tags=["data"])
router.include_router(route.router, prefix="/route", tags=["route"])
router.include_router(personalization.router, prefix="/personalization", tags=["personalization"])
router.include_router(fare.router, prefix="/fare", tags=["fare"])
router.include_router(accessibility.router, prefix="/accessibility", tags=["accessibility"])
router.include_router(language.router, prefix="/language", tags=["language"])
router.include_router(disruption.router, prefix="/disruption", tags=["disruption"])
router.include_router(local_knowledge.router, prefix="/local-knowledge", tags=["local-knowledge"])
router.include_router(orchestration.router, prefix="/orchestration", tags=["orchestration"])
router.include_router(websocket_api.router, prefix="/websocket", tags=["websocket"])
router.include_router(users.router, prefix="/users", tags=["users"])
router.include_router(journey_planning.router, prefix="/journey", tags=["journey_planning"])
router.include_router(external_apis.router, prefix="/external", tags=["external_apis"])