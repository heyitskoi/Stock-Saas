import asyncio
import httpx
import time
import argparse


async def run_benchmark(url: str, iterations: int, tenant_id: int) -> None:
    async with httpx.AsyncClient(base_url=url) as client:
        # Authenticate and obtain token
        resp = await client.post(
            "/token",
            data={"username": "admin", "password": "admin"},
        )
        resp.raise_for_status()
        token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Warm-up request
        await client.get(
            "/items/status",
            params={"tenant_id": tenant_id},
            headers=headers,
        )

        start = time.perf_counter()
        for _ in range(iterations):
            r = await client.get(
                "/items/status", params={"tenant_id": tenant_id}, headers=headers
            )
            r.raise_for_status()
        duration = time.perf_counter() - start
        rate = iterations / duration
        print(f"{iterations} requests in {duration:.2f}s -> {rate:.2f} rps")


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark the /items/status route")
    parser.add_argument("--url", default="http://localhost:8000", help="Base API URL")
    parser.add_argument(
        "--iterations", type=int, default=100, help="Number of requests"
    )
    parser.add_argument(
        "--tenant-id", type=int, default=1, help="Tenant ID to query"
    )
    args = parser.parse_args()
    asyncio.run(run_benchmark(args.url, args.iterations, args.tenant_id))


if __name__ == "__main__":
    main()
