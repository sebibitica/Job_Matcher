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