from app import app,Submission,db

def read():
    with app.app_context():
        subs = Submission.query.all()
        submissions = ''
        with open('submission.txt','w') as f:
            for sub in subs:
                submissions += f'{sub.submission_name},' 
            
            f.write(submissions)

def write():
    with app.app_context():
        with open('submission.txt','r') as f:
            sublist = f.read().split(',')

        for subs in sublist:
            new_submission = Submission(submission_name=subs)
            db.session.add(new_submission)
            db.session.commit()
        
        print(Submission.query.all())
            





