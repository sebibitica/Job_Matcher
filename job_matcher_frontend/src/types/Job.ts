export interface JobLocation {
    country: string;
    city: string;
}

export interface BaseJob {
    id: string;
    job_title: string;
    company: string;
    location: JobLocation;
    date_uploaded: string;
}

export interface MatchedJob extends BaseJob {
    score: number;
}

export interface AppliedJob extends BaseJob {
    application_id: string;
    applied_date: string;
}

export interface FullJobDetails extends BaseJob {
    description: string;
    job_url: string;
}