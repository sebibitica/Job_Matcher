import numpy as np

def dcg_at_k(relevance_scores, k):
    """Computes DCG at K"""
    return sum(rel / np.log2(idx + 2) for idx, rel in enumerate(relevance_scores[:k]))

def ndcg_at_k(predicted_jobs, top_10_jobs, k):
    """Computes NDCG at K considering actual ranking positions"""
    
    # Create a mapping of job rankings in top_10_jobs (ideal list)
    ideal_rank_map = {job: len(top_10_jobs) - rank for rank, job in enumerate(top_10_jobs)}
    
    # Get relevance scores for predicted jobs (based on ideal ranking)
    predicted_relevance = [ideal_rank_map.get(job, 0) for job in predicted_jobs]
    
    # Get ideal relevance scores (sorted by highest possible relevance)
    ideal_relevance = sorted(predicted_relevance, reverse=True)
    
    # Compute DCG and IDCG
    dcg = dcg_at_k(predicted_relevance, k)
    idcg = dcg_at_k(ideal_relevance, k)
    
    return dcg / idcg if idcg > 0 else 0.0

def dcg_at_k(ranked_list, expected_jobs, k=3):
    """ Compute Discounted Cumulative Gain (DCG) at k """
    dcg = 0
    for i, job in enumerate(ranked_list[:k]):
        if job in expected_jobs:
            rel = len(expected_jobs) - expected_jobs.index(job)  # Higher relevance for earlier expected jobs
            dcg += rel / np.log2(i + 2)  # Log discount
    return dcg

def ndcg_at_k(ranked_list, expected_jobs, k=3):
    """ Compute Normalized Discounted Cumulative Gain (NDCG) at k """
    dcg = dcg_at_k(ranked_list, expected_jobs, k)
    ideal_dcg = dcg_at_k(expected_jobs, expected_jobs, k)  # Ideal ranking is expected jobs in given order
    return dcg / ideal_dcg if ideal_dcg > 0 else 0

# Given rankings
# predicted_jobs = ["job10", "job9", "job6", "job4", "job2", "job5","job7","job8","job3","job1"]  # Top 6 predictions
top_10_jobs = ["job1", "job2", "job3", "job4", "job5", "job6", "job7", "job8", "job9", "job10"]  # Ground truth ranking
predicted_jobs = top_10_jobs[::-1]  # Reverse ground truth ranking

# Compute NDCG for top 6 positions
ndcg_score = ndcg_at_k(predicted_jobs, top_10_jobs, 10)

print(f"NDCG Score: {ndcg_score:.4f}")
