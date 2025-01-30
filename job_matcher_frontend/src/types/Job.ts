export interface JobLocation {
    country: string;
    city: string;
}

export interface JobSource {
    job_title: string;
    company: string;
    location: JobLocation;
    description: string;
    job_url: string;
}

export interface JobResult {
    _id: string;
    _score: number;
    _source: JobSource;
}

export interface AppliedJob {
    application_id: string;
    job_id: string;
    job_data: JobSource;
    applied_date: string;
}

export type UnifiedJob = JobResult & { application_id?: string; applied_date?: string; };