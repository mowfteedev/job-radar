/**
 * TypeScript Data Contracts matching Python Pydantic Schema
 */

export type RoleCategory = 'network' | 'helpdesk' | 'sysadmin' | 'devops' | 'cloud' | 'security_soc';

export type LocationCategory = 'ha_noi' | 'ho_chi_minh' | 'da_nang' | 'remote' | 'hybrid' | 'other';

export type ExperienceLevel = 'intern' | 'fresher' | 'junior';

export type JobStatus = 'active' | 'expired' | 'closed';

export type WorkType = 'full_time' | 'part_time' | 'internship' | 'contract';

export interface SalaryInfo {
  currency: string;
  min_amount?: number | null;
  max_amount?: number | null;
  is_negotiable: boolean;
  display_text: string;
}

export interface CompanyInfo {
  name: string;
  normalized_name: string;
  logo_url?: string | null;
  website?: string | null;
  location: LocationCategory;
  address?: string | null;
}

export interface JobPost {
  id: string;
  canonical_hash: string;
  title: string;
  company: CompanyInfo;
  role_category: RoleCategory;
  experience_level: ExperienceLevel;
  skills: string[];
  locations: LocationCategory[];
  salary: SalaryInfo;
  source_url: string;
  source_platform: string;
  description_summary: string;
  posted_at: string;
  scraped_at: string;
  expires_at?: string | null;
  status: JobStatus;
  relevance_score: number;
  work_type: WorkType;
}

export interface SkillFrequency {
  skill: string;
  count: number;
  percentage: number;
  category: string;
}

export interface RadarMetrics {
  last_updated: string;
  total_active_jobs: number;
  fresh_jobs_24h: number;
  jobs_by_role: Record<string, number>;
  jobs_by_location: Record<string, number>;
  top_skills: SkillFrequency[];
}
