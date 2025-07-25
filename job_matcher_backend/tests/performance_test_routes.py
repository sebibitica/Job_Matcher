import asyncio
import httpx
import time

# PERFORMANCE TESTS FOR JOB MATCHER BACKEND API

TOKEN = "" 

async def perf_test_countries(n=50):
    async with httpx.AsyncClient() as client:
        start = time.perf_counter()
        tasks = [client.get(f"http://localhost:8000/search_jobs/countries") for _ in range(n)]
        responses = await asyncio.gather(*tasks)

        for response in responses:
            if response.status_code != 200:
                print(f"Error: {response.status_code} - {response.text}")

        duration = time.perf_counter() - start
        print(f"/countries: {n} requests in {duration:.2f}s")

        durations = [r.elapsed.total_seconds() for r in responses if r.status_code == 200]
        print(f"Min: {min(durations):.3f}s, Max: {max(durations):.3f}s, Avg: {sum(durations)/len(durations):.3f}s")


async def perf_test_cities(n=50):
    async with httpx.AsyncClient() as client:
        start = time.perf_counter()
        tasks = [client.get(f"http://localhost:8000/search_jobs/cities", params={"country": "Romania"}) for _ in range(n)]
        responses = await asyncio.gather(*tasks)

        for response in responses:
            if response.status_code != 200:
                print(f"Error: {response.status_code} - {response.text}")

        duration = time.perf_counter() - start
        print(f"/cities: {n} requests in {duration:.2f}s")

        durations = [r.elapsed.total_seconds() for r in responses if r.status_code == 200]
        print(f"Min: {min(durations):.3f}s, Max: {max(durations):.3f}s, Avg: {sum(durations)/len(durations):.3f}s")


async def perf_test_job_search(n=20):
    headers = {"Authorization": f"Bearer {TOKEN}"}
    payload = {"query": "Developer"}
    async with httpx.AsyncClient() as client:
        start = time.perf_counter()
        tasks = [
            client.post(f"http://localhost:8000/search_jobs", json=payload, headers=headers)
            for _ in range(n)
        ]
        responses = await asyncio.gather(*tasks)

        for response in responses:
            if response.status_code != 200:
                print(f"Error: {response.status_code} - {response.text}")

        duration = time.perf_counter() - start
        print(f"/search_jobs: {n} requests in {duration:.2f}s")

        durations = [r.elapsed.total_seconds() for r in responses if r.status_code == 200]
        print(f"Min: {min(durations):.3f}s, Max: {max(durations):.3f}s, Avg: {sum(durations)/len(durations):.3f}s")


async def perf_test_profile_is_complete(n=50):
    headers = {"Authorization": f"Bearer {TOKEN}"}
    async with httpx.AsyncClient() as client:
        start = time.perf_counter()
        tasks = [
            client.get("http://localhost:8000/profile/is_complete", headers=headers)
            for _ in range(n)
        ]
        responses = await asyncio.gather(*tasks)
        for response in responses:
            if response.status_code != 200:
                print(f"Error: {response.status_code} - {response.text}")
        duration = time.perf_counter() - start
        print(f"/profile/is_complete: {n} requests in {duration:.2f}s")
        durations = [r.elapsed.total_seconds() for r in responses if r.status_code == 200]
        if durations:
            print(f"Min: {min(durations):.3f}s, Max: {max(durations):.3f}s, Avg: {sum(durations)/len(durations):.3f}s")

async def perf_test_profile_set_by_text(n=20):
    headers = {"Authorization": f"Bearer {TOKEN}"}
    profile_data = {
        "summary": "Software developer with 2 years of experience in web technologies.",
        "experience": [
            {
                "title": "Junior Developer",
                "company": "TechCorp",
                "startDate": "2022-01",
                "endDate": "Present",
                "description": "Developed and maintained web applications using React and Node.js."
            }
        ],
        "education": [
            {
                "degree": "Bachelor",
                "field": "Computer Science",
                "institution": "Tech University",
                "startDate": "2018-09",
                "endDate": "2022-06"
            }
        ],
        "skills": ["JavaScript", "React", "Node.js", "Git"]
    }
    
    import json
    payload = {
        "profile_text": json.dumps(profile_data)
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        start = time.perf_counter()
        tasks = [
            client.post("http://localhost:8000/profile/set_by_text", json=payload, headers=headers)
            for _ in range(n)
        ]
        responses = await asyncio.gather(*tasks)
        for response in responses:
            if response.status_code != 200:
                print(f"Error: {response.status_code} - {response.text}")
        duration = time.perf_counter() - start
        print(f"/profile/set_by_text: {n} requests in {duration:.2f}s")
        durations = [r.elapsed.total_seconds() for r in responses if r.status_code == 200]
        if durations:
            print(f"Min: {min(durations):.3f}s, Max: {max(durations):.3f}s, Avg: {sum(durations)/len(durations):.3f}s")

async def perf_test_interview_continue(interview_id, n=10):
    headers = {"Authorization": f"Bearer {TOKEN}"}
    payload = {"user_message": "Tell me more about the job."}
    async with httpx.AsyncClient(timeout=30.0) as client:
        start = time.perf_counter()
        tasks = [
            client.post(
                f"http://localhost:8000/interviews/continue/{interview_id}",
                json=payload,
                headers=headers
            )
            for _ in range(n)
        ]
        responses = await asyncio.gather(*tasks)
        for response in responses:
            if response.status_code != 200:
                print(f"Error: {response.status_code} - {response.text}")
        duration = time.perf_counter() - start
        print(f"/interviews/continue: {n} requests in {duration:.2f}s")
        durations = [r.elapsed.total_seconds() for r in responses if r.status_code == 200]
        if durations:
            print(f"Min: {min(durations):.3f}s, Max: {max(durations):.3f}s, Avg: {sum(durations)/len(durations):.3f}s")

async def perf_test_interview_get_all(n=10):
    headers = {"Authorization": f"Bearer {TOKEN}"}
    async with httpx.AsyncClient(timeout=10.0) as client:
        start = time.perf_counter()
        tasks = [
            client.get("http://localhost:8000/interviews", headers=headers)
            for _ in range(n)
        ]
        responses = await asyncio.gather(*tasks)
        for response in responses:
            if response.status_code != 200:
                print(f"Error: {response.status_code} - {response.text}")
        duration = time.perf_counter() - start
        print(f"/interviews/: {n} requests in {duration:.2f}s")
        durations = [r.elapsed.total_seconds() for r in responses if r.status_code == 200]
        if durations:
            print(f"Min: {min(durations):.3f}s, Max: {max(durations):.3f}s, Avg: {sum(durations)/len(durations):.3f}s")

async def perf_test_applied_jobs_get_all(n=20):
    headers = {"Authorization": f"Bearer {TOKEN}"}
    async with httpx.AsyncClient(timeout=10.0) as client:
        start = time.perf_counter()
        tasks = [
            client.get("http://localhost:8000/applied_jobs", headers=headers)
            for _ in range(n)
        ]
        responses = await asyncio.gather(*tasks)
        for response in responses:
            if response.status_code != 200:
                print(f"Error: {response.status_code} - {response.text}")
        duration = time.perf_counter() - start
        print(f"/applied_jobs/: {n} requests in {duration:.2f}s")
        durations = [r.elapsed.total_seconds() for r in responses if r.status_code == 200]
        if durations:
            print(f"Min: {min(durations):.3f}s, Max: {max(durations):.3f}s, Avg: {sum(durations)/len(durations):.3f}s")

async def perf_test_applied_jobs_is_applied(job_id, n=10):
    headers = {"Authorization": f"Bearer {TOKEN}"}
    async with httpx.AsyncClient(timeout=10.0) as client:
        start = time.perf_counter()
        tasks = [
            client.get(f"http://localhost:8000/applied_jobs/is_applied/{job_id}", headers=headers)
            for _ in range(n)
        ]
        responses = await asyncio.gather(*tasks)
        for response in responses:
            if response.status_code != 200:
                print(f"Error: {response.status_code} - {response.text}")
        duration = time.perf_counter() - start
        print(f"/applied_jobs/is_applied/{job_id}: {n} requests in {duration:.2f}s")
        durations = [r.elapsed.total_seconds() for r in responses if r.status_code == 200]
        if durations:
            print(f"Min: {min(durations):.3f}s, Max: {max(durations):.3f}s, Avg: {sum(durations)/len(durations):.3f}s")

            print(f"Min: {min(durations):.3f}s, Max: {max(durations):.3f}s, Avg: {sum(durations)/len(durations):.3f}s")

async def perf_test_applied_jobs_apply(job_id, n=2):
    headers = {"Authorization": f"Bearer {TOKEN}"}
    async with httpx.AsyncClient(timeout=10.0) as client:
        start = time.perf_counter()
        tasks = [
            client.post(f"http://localhost:8000/applied_jobs/apply/{job_id}", headers=headers)
            for _ in range(n)
        ]
        responses = await asyncio.gather(*tasks)
        for response in responses:
            if response.status_code != 200:
                print(f"Error: {response.status_code} - {response.text}")
        duration = time.perf_counter() - start
        print(f"/applied_jobs/apply/{job_id}: {n} requests in {duration:.2f}s")
        durations = [r.elapsed.total_seconds() for r in responses if r.status_code == 200]
        if durations:
            print(f"Min: {min(durations):.3f}s, Max: {max(durations):.3f}s, Avg: {sum(durations)/len(durations):.3f}s")

async def perf_test_match_jobs_by_profile(n=10):
    headers = {"Authorization": f"Bearer {TOKEN}"}
    async with httpx.AsyncClient(timeout=30.0) as client:
        start = time.perf_counter()
        tasks = [
            client.get("http://localhost:8000/match_jobs/by_profile", headers=headers)
            for _ in range(n)
        ]
        responses = await asyncio.gather(*tasks)
        for response in responses:
            if response.status_code != 200:
                print(f"Error: {response.status_code} - {response.text}")
        duration = time.perf_counter() - start
        print(f"/match_jobs/by_profile: {n} requests in {duration:.2f}s")
        durations = [r.elapsed.total_seconds() for r in responses if r.status_code == 200]
        if durations:
            print(f"Min: {min(durations):.3f}s, Max: {max(durations):.3f}s, Avg: {sum(durations)/len(durations):.3f}s")

if __name__ == "__main__":
    asyncio.run(perf_test_countries(50))
    asyncio.run(perf_test_cities(50))
    asyncio.run(perf_test_job_search(50))

    asyncio.run(perf_test_profile_is_complete(50))
    asyncio.run(perf_test_profile_set_by_text(10))

    asyncio.run(perf_test_interview_continue("1a6849e7-a2e7-488a-9ef1-22b97849fd9d", 20))
    asyncio.run(perf_test_interview_get_all(50))

    asyncio.run(perf_test_applied_jobs_get_all(20))
    asyncio.run(perf_test_applied_jobs_is_applied("jobs_matcher_1", 10))
    asyncio.run(perf_test_applied_jobs_apply("41afe575e690b4a9a1610d0cadc97218398856d91faaee9e441c7a31c9f3b4c4", 20))

    asyncio.run(perf_test_match_jobs_by_profile(10))