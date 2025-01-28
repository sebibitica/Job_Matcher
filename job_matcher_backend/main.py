from src.jobs_matcher.jobs_matcher import JobsMatcher

def main():
    cv_path = "sample_data/example4.docx"
    file = open(cv_path, "rb")
    
    matcher = JobsMatcher(file)
    
    try:
        matcher.process_cv()
        results = matcher.find_matching_jobs(top_k=10)
        
        JobsMatcher.print_results(results)
        
    except Exception as e:
        print(f"Error during job matching: {str(e)}")

if __name__ == "__main__":
    main()