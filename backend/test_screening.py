import httpx
import time
import json

client = httpx.Client(base_url='http://127.0.0.1:8000')

# Upload with a sample resume
with open('d:/Resume/backend/sample_resumes/Candidate_1_Elena_Rostova_Senior_AI_TechLead.pdf', 'rb') as f:
    response = client.post('/api/screenings', 
        data={
            'job_title': 'Senior Python Developer',
            'job_description': 'We are looking for a Senior Python Developer with 5+ years experience in Python, Django, FastAPI, Docker, and AWS. Must have experience with REST APIs and microservices.',
        },
        files=[('files', ('test_resume.pdf', f, 'application/pdf'))],
        timeout=30.0
    )

print('Status:', response.status_code)
print('Response:', response.text[:2000])

if response.status_code == 200:
    session_id = response.json()['id']
    print('\nSession ID:', session_id)
    
    # Wait for processing
    for i in range(20):
        time.sleep(3)
        status_resp = client.get('/api/screenings/' + str(session_id) + '/status')
        status_data = status_resp.json()
        ps = status_data.get("processing_status", "unknown")
        print('  [' + str(i) + '] Status:', ps)
        
        if ps in ('completed', 'failed'):
            print('  Submissions:', json.dumps(status_data.get('submissions', []), indent=2))
            break
    
    # Get results
    results_resp = client.get('/api/screenings/' + str(session_id) + '/results')
    print('\nResults status:', results_resp.status_code)
    print('Results:', results_resp.text[:3000])
