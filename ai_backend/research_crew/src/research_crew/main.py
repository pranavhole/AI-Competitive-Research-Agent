from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta

from .crew import CompetitiveResearchCrew
from .print_stream import PrintInterceptor

app = FastAPI()
executor = ThreadPoolExecutor()
crew = CompetitiveResearchCrew()

# ----- Rate Limit Store -----
RATE_LIMIT = 5  # max 5 requests
WINDOW_MINUTES = 60  # 1 hour rate-limit window

ip_store = {}  # { ip: { "count": int, "expires": datetime } }


def check_rate_limit(ip: str):
    now = datetime.utcnow()

    # First time seen → create record
    if ip not in ip_store:
        ip_store[ip] = {"count": 1, "expires": now + timedelta(minutes=WINDOW_MINUTES)}
        return True

    record = ip_store[ip]

    # If expired → reset window
    if now > record["expires"]:
        ip_store[ip] = {"count": 1, "expires": now + timedelta(minutes=WINDOW_MINUTES)}
        return True

    # If still in window → check count
    if record["count"] >= RATE_LIMIT:
        return False

    # Increase count
    record["count"] += 1
    return True


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/research")
async def run_research(startup: str, request: Request):
    client_ip = request.client.host

    # --- Rate Limit Check ---
    if not check_rate_limit(client_ip):
        return JSONResponse(
            status_code=429,
            content={"error": "Your request limit is over. Try again later."}
        )

    queue = asyncio.Queue()

    async def event_stream():
        while True:
            message = await queue.get()
            if message == "__END__":
                break
            yield f"{message}\n\n"

    def run_job_sync():
        interceptor = PrintInterceptor(queue)
        interceptor.start()

        asyncio.run(queue.put(f"🚀 Starting research for: {startup}"))

        crew_obj = crew.crew()
        result = crew_obj.kickoff(inputs={"startup": startup})

        asyncio.run(queue.put("📄 FINAL OUTPUT:"))
        asyncio.run(queue.put(str(result.raw)))

        interceptor.stop()
        asyncio.run(queue.put("__END__"))

    asyncio.get_event_loop().run_in_executor(executor, run_job_sync)

    return StreamingResponse(event_stream(), media_type="text/event-stream")
