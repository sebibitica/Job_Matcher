import asyncio
import numpy as np
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.jobs_matcher.jobs_matcher import JobsMatcher
from src.clients.es_client import ElasticsearchClient
from src.clients.openai_embedding_client import OpenAIEmbeddingClient
from src.preprocessor.preprocessor import TextPreprocessor

es_client = ElasticsearchClient()
embedding_client = OpenAIEmbeddingClient()
preprocessor = TextPreprocessor()


# TESTS FOR KNN RANKING OF JOBS

USERS = [
    {
        "user_id": "A81eScgtsdbAKIhVzUtXclWk7A02",
        "expected_jobs": [
            "b30632957ab3dbdeec23b0b7071f11de9c38ff96e4ad0ced8b3a942a749587fe",
            "aafdaab132417312c38bed9a45b545089e3e8bf0c91d1746902530c75a4cce0b",
            "b724624852edec889a92534c5872c557918512aaf2ea81bffdad3190866d0604",
            "41afe575e690b4a9a1610d0cadc97218398856d91faaee9e441c7a31c9f3b4c4",
            "14053305609846ff1e5a219b5e0c99047259aecb6954fb3eacb116d4cd5aede5",
        ]
    },
    {
        "user_id": "g8cJfI6MMOeReDCiSSZpsM0pDlH3",
        "expected_jobs": [
            "98c7afb5fb4c57e089d9881c5c7a9ed5543cd10ecc4328d1e38a8927529ed894",
            "900ed0652e4b21691c90ff409d3dfef1e16cc27455f296bed1177b235a182883",
            "770d903e4f6f9a8d7afa1a52bac371c8cf54c6180838fdb87a7a1c554c412f73",
            "e94c044ae4692a1b8f21cfabd8552c4f29d84cbf53799cc0db876502e2f8f23e",
        ]
    },
    {
        "user_id": "HLldDUDjO7O6KtanLoi6E2T5AKl2",
        "expected_jobs": [
            "bf01e6632c00de92b5ea46041c7b25bd91ec3c4f8cafeeb384a3ad8b84feeec4",
            "06be43238c3c8d311e902796b76b69e0ead7d3edfc1bd5a1fadd932471cdaeeb",
            "4b6f93fe7619f8c96fd0df729f74cafbda69c1ea674a79124cff567f7d641d48",
            "61dfcf0b1e843e6a8324e71f2cf781177c0551bead5fd471e67119a7dd640da1"
        ]
    }
]

def average_precision(ranked_list, expected_jobs):
    relevant_count = 0
    score_sum = 0
    for i, job in enumerate(ranked_list, 1):
        if job in expected_jobs:
            relevant_count += 1
            score_sum += relevant_count / i
    return score_sum / len(expected_jobs) if expected_jobs else 0

def compute_ndcg(ranked_list, expected_jobs, k=10):
    if not expected_jobs:
        return 0.0
    n_expected = len(expected_jobs)
    relevance_dict = {
        job: (n_expected - idx)
        for idx, job in enumerate(expected_jobs)
    }
    dcg = 0.0
    for rank, job in enumerate(ranked_list[:k], 1):
        if job in relevance_dict:
            rel = relevance_dict[job]
            dcg += rel / np.log2(rank + 1)
    idcg = 0.0
    for ideal_rank, job in enumerate(expected_jobs[:k], 1):
        rel = relevance_dict.get(job, 0)
        idcg += rel / np.log2(ideal_rank + 1)
    return dcg / idcg if idcg > 0 else 0.0

def mean_reciprocal_rank(result_ids, expected_jobs_list):
    for idx, job_id in enumerate(result_ids, 1):
        if job_id in expected_jobs_list:
            return 1.0 / idx
    return 0.0

async def main():
    matcher = JobsMatcher(embedding_client, es_client, preprocessor)
    top_k = 10

    total_recall = 0
    total_mrr = 0
    total_map = 0
    total_ndcg = 0
    num_users = len(USERS)

    for user in USERS:
        user_id = user["user_id"]
        expected_jobs_list = user["expected_jobs"]  # păstrează ordinea!
        expected_jobs_set = set(expected_jobs_list)
        try:
            results = await matcher.get_matching_jobs_with_user_id(user_id, top_k=top_k)
        except Exception as e:
            print(f"User {user_id}: ERROR: {e}")
            continue

        result_ids = [job.id for job in results]

        # Recall@K
        found = expected_jobs_set.intersection(result_ids)
        recall = len(found) / len(expected_jobs_list) if expected_jobs_list else 0
        print(f"User {user_id}: Recall@{top_k} = {recall:.2f} ({len(found)}/{len(expected_jobs_list)})")

        # Ranks
        for job_id in expected_jobs_list:
            if job_id in result_ids:
                rank = result_ids.index(job_id) + 1
                print(f"  Job {job_id} found at rank {rank}")
            else:
                print(f"  Job {job_id} NOT found in top {top_k}")

        # Mean Reciprocal Rank (MRR)
        mrr = mean_reciprocal_rank(result_ids, expected_jobs_list)
        print(f"User {user_id}: MRR = {mrr:.3f}")

        # MAP
        map_score = average_precision(result_ids, expected_jobs_list)
        print(f"User {user_id}: MAP = {map_score:.3f}")

        # NDCG@10
        ndcg_score = compute_ndcg(result_ids, expected_jobs_list, k=10)
        print(f"User {user_id}: NDCG@10 = {ndcg_score:.3f}")

        total_recall += recall
        total_mrr += mrr
        total_map += map_score
        total_ndcg += ndcg_score

        if recall == 0:
            print(f"WARNING: No relevant jobs found for user {user_id}!")
        print("-" * 40)

    print("==== Overall Metrics ====")
    print(f"Avg Recall@{top_k}: {total_recall/num_users:.3f}")
    print(f"Avg MRR: {total_mrr/num_users:.3f}")
    print(f"Avg MAP: {total_map/num_users:.3f}")
    print(f"Avg NDCG@10: {total_ndcg/num_users:.3f}")

if __name__ == "__main__":
    asyncio.run(main())