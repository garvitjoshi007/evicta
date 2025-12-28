import requests
import time

ASK_URL = "http://127.0.0.1:8000/ask"
STATS_URL = "http://127.0.0.1:8000/stats"

prompts = [
    # Recursion – definition / explanation
    "what is recursion",
    "define recursion",
    "explain recursion",
    "what is recursion",
    "explain recursion",
    "define recursion",

    # Difference
    "difference between recursion and iteration",
    "compare recursion and iteration",
    "recursion vs iteration",
    "difference between recursion and iteration",

    # How-to cluster
    "how to deploy a python app",
    "steps to deploy a python app",
    "guide to deploy a python app",
    "how to deploy a python app",
    "steps to deploy a python app",

    # Install / setup
    "install docker",
    "setup docker",
    "configure docker",
    "install docker",
    "setup docker",

    # Tool recommendation
    "best database for analytics",
    "recommend database for analytics",
    "which database is better for analytics",
    "best database for analytics",

    # Summarize
    "summarize kubernetes",
    "rewrite kubernetes explanation",
    "simplify kubernetes explanation",
    "summarize kubernetes",

    # Load balancing
    "what is load balancing",
    "define load balancing",
    "explain load balancing",
    "what is load balancing",

    # TCP vs UDP
    "difference between tcp and udp",
    "tcp vs udp",
    "compare tcp and udp",
    "difference between tcp and udp",

    # Nginx setup
    "how to setup nginx",
    "steps to setup nginx",
    "guide to setup nginx",
    "how to setup nginx",

    # Final repeats (force exact hits)
    "what is recursion",
    "explain recursion",
    "how to deploy a python app",
    "install docker",
    "summarize kubernetes",
    "what is load balancing",
    "tcp vs udp",
    "how to setup nginx",
    "best database for analytics",
    "define recursion",
]

def run():
    print("\n--- Running Evicta EASY workload ---\n")

    for i, prompt in enumerate(prompts, 1):
        r = requests.post(ASK_URL, json={"prompt": prompt})
        status = "OK" if r.status_code == 200 else "ERR"
        print(f"[{i:02}] {status} | {prompt}")
        time.sleep(0.08)  # keeps logs readable

    print("\n--- Final /stats ---")
    stats = requests.get(STATS_URL).json()
    for k, v in stats.items():
        print(f"{k:>16}: {v}")

if __name__ == "__main__":
    run()
