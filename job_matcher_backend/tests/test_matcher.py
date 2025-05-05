import json
import numpy as np
from src.jobs_matcher.jobs_matcher import JobsMatcher

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
    
    # Assign relevance scores based on position in expected_jobs
    n_expected = len(expected_jobs)
    relevance_dict = {
        job: (n_expected - idx)  # First job gets highest relevance
        for idx, job in enumerate(expected_jobs)
    }
    
    # Compute DCG@k
    dcg = 0.0
    for rank, job in enumerate(ranked_list[:k], 1):  # rank is 1-based
        if job in relevance_dict:
            rel = relevance_dict[job]
            dcg += rel / np.log2(rank + 1)  # Standard DCG discount
    
    # Compute IDCG@k (ideal ranking: expected_jobs in original order)
    idcg = 0.0
    for ideal_rank, job in enumerate(expected_jobs[:k], 1):  # 1-based rank
        rel = relevance_dict.get(job, 0)
        idcg += rel / np.log2(ideal_rank + 1)
    
    return dcg / idcg if idcg > 0 else 0.0

class JobsMatcherEvaluator:
    def __init__(self, test_cases_file):
        with open(test_cases_file, "r") as f:
            self.test_cases = json.load(f)["tests"]
        self.matcher = JobsMatcher()
    
    def evaluate(self):
        total_metrics = {
            'recall': 0,
            'exact_order_top_n': 0,
            'map': 0,
            'ndcg': 0
        }
        num_cases = len(self.test_cases)
        
        for test in self.test_cases:
            resume_id = test["resume_id"]
            expected_jobs = test["expected_jobs"]
            results = self.matcher.get_matching_jobs_with_resume_id(
                resume_id, user_id="A81eScgtsdbAKIhVzUtXclWk7A02", top_k=10
            )
            ranked_list = [hit['_id'] for hit in results['hits']['hits']]
            
            # Compute metrics
            common = set(ranked_list) & set(expected_jobs)
            total_expected = len(expected_jobs)
            
            recall = len(common) / total_expected if total_expected > 0 else 0
            exact_order_top_n = len(set(ranked_list[:total_expected]) & set(expected_jobs)) / total_expected if total_expected > 0 else 0
            map_score = average_precision(ranked_list, expected_jobs)
            ndcg_score = compute_ndcg(ranked_list, expected_jobs, k=10)
            
            # Accumulate totals
            total_metrics['recall'] += recall
            total_metrics['exact_order_top_n'] += exact_order_top_n
            total_metrics['map'] += map_score
            total_metrics['ndcg'] += ndcg_score
            
            print(f"Test case: {resume_id}")
            print(f"Recall: {recall:.3f}, Precision@N: {exact_order_top_n:.3f}, "
                  f"MAP: {map_score:.3f}, NDCG@10: {ndcg_score:.3f}\n")
        
        # Print final averages
        print("Overall Evaluation Results:")
        for metric, value in total_metrics.items():
            avg = value / num_cases
            print(f"Average {metric.replace('_', ' ').title()}: {avg:.3f}")

if __name__ == "__main__":
    evaluator = JobsMatcherEvaluator("tests/test_cases.json")
    evaluator.evaluate()