from adslib import *

app=Flask(__name__)

ini=jroads()
uri='mongodb://' +ini['connexion']
connexion=mcx(uri)
dbo=connexion[ini['dbase']]

def open_connection():
	connection=getattr(g,'_connection',None)
	if connection==None:
		connection=g._connection=sqlite3.connect(PATH)
	connection.row_factory=sqlite3.Row
	return connection

def execute_sql(sql,values=(),commit=False,single=False):
	connection=open_connection()
	cursor=connection.execute(sql,values)
	if commit==True:
		results=connection.commit()
	else:
		results=cursor.fetchone() if single else cursor.fetchall()
	cursor.close()
	return results

@app.teardown_appcontext
def close_connection(exception):
	connection=getattr(g,'_connection',None)
	if connection is not None:
		connection.close()

@app.route('/')
@app.route('/jobs')
def jobs():
	print('Home Page')
	pipe=[{'$lookup':{'from':'employer','localField':'employer_id','foreignField':'id', 'as':'emBED'}},
	{'$unwind':'$emBED'},
	{'$project':{'id':1,'_id':0,'title':1,'description':1,'salary':1,'employer_id':'$emBED.id','employer_name':'$emBED.name'}}]
	jobs=dbo.job.aggregate(pipe)
	print(jobs)
	return render_template('index.html',jobs=jobs)

@app.route('/job/<job_id>')
def job(job_id):
	print('Job Page')
	qpipe=[{'$match':{'id':int(job_id)}},
	{'$lookup':{'from':'employer','localField':'employer_id','foreignField':'id','as':'emBED'}},
	{'$unwind':'$emBED'},
	{'$project':{'id':1,'_id':0,'description':1,'title':1,'salary':1,'employer_id':'$emBED.id','employer_name':'$emBED.name'}}]
	jobCur=dbo.job.aggregate(qpipe)
	for jobie in jobCur:
		jobie
	return render_template('job.html', job=jobie)

@app.route('/employer/<employer_id>')
def employer(employer_id):
	eid=int(employer_id)
	qpipe=odict([('jobs',[{'$match':{'employer_id':eid}},
	{'$lookup':{'from':'employer','localField':'employer_id','foreignField':'id','as':'emBED'}},
	{'$unwind':'$emBED'},
	{'$project':{'id':1,'_id':0,'title':1,'description':1,'salary':1}}]),
	('review',[{'$match':{'employer_id':eid}},
	{'$lookup':{'from':'employer','localField':'employer_id','foreignField':'id','as':'emBED'}},
	{'$unwind':'$emBED'},
	{'$project':{'review':1,'rating':1,'title':1,'date':1,'status':1}}])])
	employer=list(dbo.employer.find({'id':eid}))[0]
	jobs=dbo.job.aggregate(qpipe['jobs'])
	reviews=dbo.review.aggregate(qpipe['review'])
	return render_template('employer.html',employer=employer,jobs=jobs,reviews=reviews)

@app.route('/employer/<employer_id>/review', methods=('GET', 'POST'))
def review(employer_id):
	eid=int(employer_id)
	if request.method=='POST':
		review=request.form['review']
		rating=request.form['rating']
		title=request.form['title']
		status=request.form['status']
		date=dt.utcnow().strftime("%m/%d/%Y")
		qpost={'review':review,'rating':int(rating),'title':title,'status':status,'date':date,'employer_id':eid}
		print(qpost)
		dbo.review.insert_one(qpost)
		return redirect(url_for('employer', employer_id=eid))
	return render_template('review.html',employer_id=eid)

if __name__=='__main__':
	app.run(debug=True,host='0.0.0.0',port=80)