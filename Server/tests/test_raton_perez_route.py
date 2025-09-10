import asyncio
import pytest

from Server.core.agents.raton_perez import process_chat_message, get_next_destination
from Server.core.agents.family_context import load_family_context, save_family_context
from Server.core.agents.location_helper import RATON_PEREZ_ROUTE

# 🧩 Mock simple de DB
class MockDB:
    def execute_query(self, query, params=None):
        if "FROM families" in query:
            return [{"id": 1, "name": "Familia Test", "preferred_language": "es", "conversation_context": "{}"}]
        if "FROM family_members" in query:
            return [
                {"name": "Ana", "age": 35, "member_type": "adult"},
                {"name": "Luis", "age": 8, "member_type": "child"}
            ]
        if "FROM family_route_progress" in query:
            return [{"current_poi_index": 0, "points_earned": 0, "current_location": "{}"}]
        return []

@pytest.mark.asyncio
async def test_raton_perez_full_route():
    db = MockDB()
    family_id = 1

    context = await load_family_context(family_id, db)
    assert context.family_name == "Familia Test"

    total_points = 0

    for poi_index, poi in enumerate(RATON_PEREZ_ROUTE):
        poi_id = poi["id"]
        poi_name = poi["name"]

        # 🔄 Forzar el estado para que cada POI sea tratado como llegada nueva
        context.current_poi_index = poi_index
        context.visited_pois = []  # <--- Limpiamos visitas anteriores
        context.total_points = total_points
        await save_family_context(context, db)

        # 🟢 Llegada al POI
        arrival_response = await process_chat_message(family_id, "¡Hola!", db=db)
        assert arrival_response["success"] is True
        print(f"\n➡️ Llegada a {poi_name} - Puntos: {arrival_response['points_earned']}")
        print("Agente:", arrival_response["response"])
        # Ahora debería dar 100 puntos exactos
        assert arrival_response["points_earned"] == 100
        total_points += arrival_response["points_earned"]

        # Engagement
        engagement_response = await process_chat_message(
            family_id,
            "Me parece un lugar increíble y fascinante, ¡qué bonito!",
            db=db
        )
        assert engagement_response["success"] is True
        total_points += engagement_response["points_earned"]
        print(f"✨ Engagement - Puntos: {engagement_response['points_earned']}")
        print("Agente:", engagement_response["response"])

        # Responder pregunta
        question_response = await process_chat_message(
            family_id,
            "Sí, nos ha gustado mucho este lugar, ¡es genial!",
            db=db
        )
        assert question_response["success"] is True
        total_points += question_response["points_earned"]
        print(f"❓ Respuesta a pregunta - Puntos: {question_response['points_earned']}")
        print("Agente:", question_response["response"])

        next_poi = await get_next_destination(family_id, db)
        print(f"➡️ Siguiente destino: {next_poi}")

    print(f"\n🏁 Total puntos acumulados: {total_points}")
    assert total_points > 0
