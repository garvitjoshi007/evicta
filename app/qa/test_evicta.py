import requests
import time
import asyncio
import aiohttp

ASK_URL = "http://127.0.0.1:8000/ask"
STATS_URL = "http://127.0.0.1:8000/stats"

CONCURRENCY = 2

prompts = [
    # ===============================
    # Define / Explain (Concepts)
    # ===============================
    "what is recursion",
    "define recursion",
    "explain recursion in simple terms",
    "meaning of recursion",
    "recursion meaning",

    # Slight noise
    "what is recursion in programming",
    "define recursion with example",

    # ===============================
    # DifferenceBetween (unordered)
    # ===============================
    "difference between recursion and iteration",
    "compare recursion vs iteration",
    "iteration vs recursion",
    "recursion versus iteration",
    "difference between iteration and recursion",

    # ===============================
    # HowToGuide (procedural)
    # ===============================
    "how to deploy a python app",
    "steps to deploy a python application",
    "guide to deploy python app on server",
    "procedure to deploy a python app",
    "how to deploy python app",

    # ===============================
    # Install / Setup
    # ===============================
    "install docker",
    "setup docker",
    "configure docker on ubuntu",
    "download docker",
    "install docker on linux",

    # ===============================
    # Tool Recommendation
    # ===============================
    "best database for analytics",
    "which database is better for analytics workloads",
    "recommend database for analytics use case",
    "suggest a database for analytics",

    # ===============================
    # Summarize / Rewrite
    # ===============================
    "summarize kubernetes",
    "simplify kubernetes explanation",
    "rewrite kubernetes overview",
    "shorten kubernetes explanation",
    "summarize kubernetes in simple words",

    # ===============================
    # TroubleshootIssue (real dev phrasing)
    # ===============================
    "docker not working",
    "kafka consumer failed",
    "python app error",
    "nginx issue",
    "redis connection problem",

    # ===============================
    # DebugError (artifact-driven)
    # ===============================
    "traceback in python",
    "segfault",
    "panic in golang",
    "stack trace error",
    "exception in java",

    # ===============================
    # WriteCode
    # ===============================
    "implement lru cache",
    "write code for binary search",
    "implement rate limiter",
    "write a regex for email validation",
    "write function for fibonacci",

    # ===============================
    # CreativeGeneration (light, realistic)
    # ===============================
    "write a short poem about time",
    "create a caption for instagram",
    "write lyrics about hope",
    "write a story about failure",

    # ===============================
    # FindResource
    # ===============================
    "find course for kubernetes",
    "search resources for system design",
    "best learning resource for distributed systems",
    "find documentation for docker networking",

    # ===============================
    # FORCE CACHE HITS (exact + intent)
    # ===============================
    "what is recursion",
    "define recursion",
    "difference between recursion and iteration",
    "how to deploy a python app",
    "install docker",
    "best database for analytics",
    "summarize kubernetes",
    "docker not working",
    "traceback in python",
    "implement lru cache",
]

async def send_prompt(session, sem, idx, prompt):
    async with sem:
        async with session.post(ASK_URL, json={"prompt": prompt}) as resp:
            status = "OK" if resp.status == 200 else "ERR"
            print(f"[{idx:02}] {status} | {prompt}")

async def run():
    print("\n--- Running Evicta EASY workload (async) ---\n")

    sem = asyncio.Semaphore(CONCURRENCY)

    async with aiohttp.ClientSession() as session:
        tasks = [
            send_prompt(session, sem, i + 1, prompt)
            for i, prompt in enumerate(prompts)
        ]
        await asyncio.gather(*tasks)

    print("\n--- Final /stats ---")
    async with aiohttp.ClientSession() as session:
        async with session.get(STATS_URL) as resp:
            stats = await resp.json()
            for k, v in stats.items():
                print(f"{k:>16}: {v}")

if __name__ == "__main__":
    asyncio.run(run())
