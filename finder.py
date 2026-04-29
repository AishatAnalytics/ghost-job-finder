import os
import json
import boto3
from datetime import datetime
from dotenv import load_dotenv
import anthropic
import time

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
ses = boto3.client('ses', region_name=os.getenv('AWS_REGION'))

SAMPLE_JOBS = [
    {
        'title': 'Senior Solutions Architect',
        'company': 'AWS Partner — Deloitte',
        'location': 'Dallas TX',
        'salary': '$140k-$180k',
        'requirements': 'AWS SA Professional, 5+ years, serverless, multi-region, FinOps',
        'posted': '2 days ago'
    },
    {
        'title': 'Cloud Solutions Architect',
        'company': 'Microsoft',
        'location': 'Remote',
        'salary': '$130k-$160k',
        'requirements': 'AWS or Azure certified, IaC, containers, CI/CD',
        'posted': '1 day ago'
    },
    {
        'title': 'AWS Solutions Architect',
        'company': 'Accenture',
        'location': 'Irving TX',
        'salary': '$120k-$150k',
        'requirements': 'AWS certified, Python, Lambda, security, compliance',
        'posted': '3 days ago'
    },
    {
        'title': 'Platform Engineer',
        'company': 'Goldman Sachs',
        'location': 'Dallas TX',
        'salary': '$150k-$200k',
        'requirements': 'Kubernetes, Terraform, AWS, Python, CI/CD pipelines',
        'posted': '1 day ago'
    },
    {
        'title': 'Cloud Architect',
        'company': 'IBM',
        'location': 'Remote',
        'salary': '$125k-$155k',
        'requirements': 'Multi-cloud, AWS, Azure, cost optimization, enterprise',
        'posted': '4 days ago'
    }
]

CANDIDATE_PROFILE = """
Name: Aishat Olatunji
Certifications: AWS Solutions Architect Professional
Education: MS Computer Science
Experience: Cloud Engineer 2 years
Skills: AWS, Python, Node.js, Lambda, DynamoDB, S3, CloudWatch, Terraform, Claude API
Projects: 30 cloud projects including multi-region failover, IAM security, FinOps, chaos engineering
Location: Texas
"""

def rank_jobs(jobs, profile):
    print("Ranking jobs with Claude AI...")

    prompt = f"""
You are a career coach specializing in cloud engineering roles.

Rank these job listings for this candidate from best to worst match.

CANDIDATE PROFILE:
{profile}

JOB LISTINGS:
{json.dumps(jobs, indent=2)}

For each job provide:
1. MATCH SCORE out of 100
2. WHY IT IS A GOOD FIT
3. GAPS TO ADDRESS
4. APPLICATION TIP

Then recommend TOP 3 jobs to apply to first with specific reasons.

Be specific and actionable.
    """

    for attempt in range(3):
        try:
            message = client.messages.create(
                model="claude-opus-4-5",
                max_tokens=800,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < 2:
                time.sleep(5)

    return "Analysis unavailable"

def send_job_digest(jobs, analysis):
    message = f"""
GHOST JOB FINDER REPORT
=======================
Date: {datetime.now().strftime('%Y-%m-%d')}
Jobs analyzed: {len(jobs)}

TOP OPPORTUNITIES:
{chr(10).join([f"- {j['title']} at {j['company']} ({j['location']}) — {j['salary']}" for j in jobs])}

CLAUDE AI RANKING:
{analysis}

Ghost Job Finder
    """

    try:
        ses.send_email(
            Source=os.getenv('YOUR_EMAIL'),
            Destination={'ToAddresses': [os.getenv('YOUR_EMAIL')]},
            Message={
                'Subject': {'Data': f"Job Finder Report — {len(jobs)} opportunities ranked"},
                'Body': {'Text': {'Data': message}}
            }
        )
        print(f"\nJob digest sent to {os.getenv('YOUR_EMAIL')}")
    except Exception as e:
        print(f"\nEmail failed: {e}")

def run():
    print("Ghost Job Finder")
    print("================\n")

    print("Step 1: Loading job listings...")
    print(f"Found {len(SAMPLE_JOBS)} jobs\n")
    for job in SAMPLE_JOBS:
        print(f"- {job['title']} at {job['company']} — {job['salary']}")

    print("\nStep 2: Ranking with Claude AI...")
    analysis = rank_jobs(SAMPLE_JOBS, CANDIDATE_PROFILE)

    print("\n" + "="*50)
    print("JOB RANKINGS")
    print("="*50 + "\n")
    print(analysis)

    print("\nStep 3: Sending job digest...")
    send_job_digest(SAMPLE_JOBS, analysis)

    report = {
        'timestamp': datetime.now().isoformat(),
        'jobs': SAMPLE_JOBS,
        'analysis': analysis
    }

    with open('job_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    print("Report saved to job_report.json")
    print("\nGhost Job Finder complete!")

if __name__ == "__main__":
    run()