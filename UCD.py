import matplotlib.pyplot as plt
import numpy as np
from math import log2

users=30
B=1
N=1e-10
F=10
avg=0.1
num=60
x_num=7

def gen_task():
	tasks=dict()
	for i in range(users):
		buf=dict()
		buf['a']=np.random.uniform(100,1000)*2/1000
		#buf['d']=np.random.uniform(100,2000)/1000
		buf['d']=buf['a']
		buf['fl']=np.random.uniform(1.5,2.5)
		buf['Tm']=np.random.uniform(avg,1)
		buf['pri']=np.random.uniform(0.1,1)
		buf['SINR']=(10**np.random.uniform(4,10))*7.5/N
		tasks[i]=buf
	return tasks

def caltech(tasks, xi):
	reward=0
	b=list()

	#sum of sqrt
	ss=0
	for k,v in tasks.items():
		ss+=(xi[k]*v['a']*v['pri']/log2(1+v['SINR']))**0.5

	#cal lagrange b
	for k,v in tasks.items():
		if ss!=0:
			b.append(((xi[k]*v['a']*v['pri']/log2(1+v['SINR']))**0.5)*B/ss)
		else:
			b.append(0)

	for k,v in tasks.items():
		if xi[k]!=0:
			t=max( (1-xi[k])*v['d']/v['fl'], xi[k]*v['a']/b[k]/log2(1+v['SINR']))
		else:
			t=(1-xi[k])*v['d']/v['fl']
		if t<v['Tm']:
			reward+=v['pri']*(1-t/(v['d']) )*10
		#else:
		#	reward-=v['pri']*10

	return reward/users/10

def iterative(tasks):
	xi=list()
	b=[0]*users
	reserved_b=[0]*users
	for e in tasks.values():
		xi.append( 1-min(1,e['Tm']*e['fl']/e['d']) )
	
	tasks=sorted(tasks.items(), key=lambda kv: -kv[1]['pri']/(kv[1]['a']/kv[1]['Tm']/log2(1+kv[1]['SINR'])) )

	#occupied bandwidth
	remaining=B
	for e in tasks:
		#allocate minimum bandwidth
		bi=xi[e[0]]*e[1]['a']/e[1]['Tm']/log2(1+e[1]['SINR'])
		if remaining-bi<0:
			break
		else:
			remaining-=bi
			reserved_b[e[0]]=bi

	for e in tasks:
		b[e[0]]=reserved_b[e[0]] + remaining/users

	i=0
	while i<10:
		#update x
		for e in tasks:
			xi[e[0]]=e[1]['d']/e[1]['fl']/( e[1]['a']/(b[e[0]]*log2(1+e[1]['SINR'])) + e[1]['d']/e[1]['fl'] )


		#sum of sqrt
		ss=0
		for e in tasks:
			ss+=(xi[e[0]]*e[1]['a']*e[1]['pri']/log2(1+e[1]['SINR']))**0.5

		#update b
		for e in tasks:
			b[e[0]]=reserved_b[e[0]] + ((xi[e[0]]*e[1]['a']*e[1]['pri']/log2(1+e[1]['SINR']))**0.5)*remaining/ss
		i+=1

	reward=0
	for e in tasks:
		if xi[e[0]]!=0:
			t=max( (1-xi[e[0]])*e[1]['d']/e[1]['fl'], xi[e[0]]*e[1]['a']/b[e[0]]/log2(1+e[1]['SINR']))
		else:
			t=(1-xi[e[0]])*e[1]['d']/e[1]['fl']
		if t<e[1]['Tm']:
			reward+=e[1]['pri']*(1-t/(e[1]['d']) )
	return reward/users

def iterative2(tasks):
	xi=list()
	b=[0]*users
	reserved_b=[0]*users
	for e in tasks.values():
		xi.append( 1-min(1,e['Tm']*e['fl']/e['d']) )
	
	tasks=sorted(tasks.items(), key=lambda kv: -kv[1]['pri']-kv[1]['pri']/(kv[1]['a']/kv[1]['Tm']/log2(1+kv[1]['SINR'])))

	#occupied bandwidth
	remaining=B
	for e in tasks:
		#allocate minimum bandwidth
		bi=xi[e[0]]*e[1]['a']/e[1]['Tm']/log2(1+e[1]['SINR'])
		if remaining-bi<0:
			break
		else:
			remaining-=bi
			reserved_b[e[0]]=bi

	#sum of sqrt
	ss=0
	for e in tasks:
		ss+=(xi[e[0]]*e[1]['a']*e[1]['pri']/log2(1+e[1]['SINR']))**0.5

	for e in tasks:
		b[e[0]]=reserved_b[e[0]] + ((xi[e[0]]*e[1]['a']*e[1]['pri']/log2(1+e[1]['SINR']))**0.5)*remaining/ss

	i=0
	while i<10:
		#update x
		for e in tasks:
			if b[e[0]]!=0:
				xi[e[0]]=e[1]['d']/e[1]['fl']/( e[1]['a']/(b[e[0]]*log2(1+e[1]['SINR'])) + e[1]['d']/e[1]['fl'] )
			else:
				xi[e[0]]=0

		reserved_b=[0]*users		

		#occupied bandwidth
		remaining=B
		for e in tasks:
			#allocate minimum bandwidth
			bi=xi[e[0]]*e[1]['a']/e[1]['Tm']/log2(1+e[1]['SINR'])
			if remaining-bi<0:
				break
			else:
				remaining-=bi
				reserved_b[e[0]]=bi

		#sum of sqrt
		ss=0
		for e in tasks:
			ss+=(xi[e[0]]*e[1]['a']*e[1]['pri']/log2(1+e[1]['SINR']))**0.5

		#update b
		for e in tasks:
			b[e[0]]=reserved_b[e[0]] + ((xi[e[0]]*e[1]['a']*e[1]['pri']/log2(1+e[1]['SINR']))**0.5)*remaining/ss
		i+=1

	reward=0
	for e in tasks:
		if xi[e[0]]!=0:
			t=max( (1-xi[e[0]])*e[1]['d']/e[1]['fl'], xi[e[0]]*e[1]['a']/b[e[0]]/log2(1+e[1]['SINR']))
		else:
			t=(1-xi[e[0]])*e[1]['d']/e[1]['fl']
		if t<e[1]['Tm']:
			reward+=e[1]['pri']*(1-t/e[1]['Tm'])*10
		#else:
		#	reward-=e[1]['pri']*10

	return reward/users/10

def greedy(tasks):
	xi=[0]*users
	b=[0]*users

	tasks_s=sorted(tasks.items(), key=lambda kv: -kv[1]['pri'])

	#occupied bandwidth
	remaining=B
	for e in tasks_s:
		#allocate bandwidth
		bi=1*e[1]['a']/e[1]['Tm']/log2(1+e[1]['SINR'])
		if remaining-bi<0:
			pass
		else:
			remaining-=bi
			xi[e[0]]=1

	return xi

def GA_x(tasks):
	Maternal=list()
	table=list()
	def generate(size):
		for a in range(size):
			decision=list()
			for b in range(users):
				if np.random.rand()<15/users:
					decision.append(np.random.rand())
				else:
					decision.append(0)

			table.append(decision)
			Maternal.append([decision, caltech(tasks, decision)])

	def crossover(pairs, rank):
		parent=list()
		for e in range(2*pairs):
			a=np.random.rand()
			if a<rank[0][1]:
				parent.append(rank[0][0])
			else:
				accu=rank[0][1]
				for i in range(1, len(rank)):
					if a>accu and a<accu+rank[i][1]:
						parent.append(rank[i][0])
						break
					else:
						accu+=rank[i][1]

		while len(parent)>2:
			a=parent.pop()
			b=parent.pop()
			start=np.random.randint(len(a))
			end=np.random.randint(start,len(a))

			aa,bb=list(),list()
			for j in range(users):
				if j not in range(start, end):
					aa.append(a[j])
					bb.append(b[j])
				else:
					aa.append(b[j])
					bb.append(a[j])

			if aa not in table:
				table.append(aa)
				Maternal.append([aa, caltech(tasks,aa)])
			if bb not in table:
				table.append(bb)
				Maternal.append([bb, caltech(tasks,bb)])

			if np.random.rand()<0.1:
				muta1, muta2=list(), list()
				tar=np.random.randint(len(aa))
				for i in range(len(aa)):
					if i!=tar:
						muta1.append(aa[i])
						muta2.append(bb[i])
					else:
						muta1.append(np.random.rand())
						muta2.append(np.random.rand())
				if muta1 not in table:
					table.append(muta1)
					Maternal.append([muta1, caltech(tasks,muta1)])
				if muta2 not in table:
					table.append(muta2)
					Maternal.append([muta2, caltech(tasks,muta2)])

		if len(Maternal)>len(rank):
			for i in range(1, len(Maternal)-len(rank)+1):
				Maternal.pop(Maternal.index(rank[-i]))

	generate(200)
	cou=0
	st1=0
	while 1:
		total=0
		Roulette=Maternal.copy()
		for e in Roulette:
			total+=e[1]
		for i in range(len(Roulette)):
			Roulette[i][1]/=total
		crossover(10, sorted(Roulette, key=lambda kv: -kv[1]))
		if sorted(Maternal, key=lambda kv: -kv[1])[0][1]-st1<0.1:
			cou+=1
		else:
			st1=sorted(Maternal, key=lambda kv: -kv[1])[0][1]
			cou=0
		if cou>7:
			break
	xi=sorted(Maternal, key=lambda kv: -kv[1])[0][0]

	return xi

def PSO(tasks):
	particles=200
	#a single particle (solution vector)
	decision=list()
	#particle's v
	velocity=list()

	#initialize
	for i in range(particles):
		decision.append([])
		velocity.append([])
		for j in range(users):
			if np.random.rand()<15/users:
				decision[i].append(np.random.rand())
				velocity[i].append(np.random.uniform(0.5,0.5))
			else:
				decision[i].append(0)
				velocity[i].append(0)

	#each particle's history
	history=list()
	for i in range(particles):
		history.append([decision[i],-100])
	glob_best=[decision[-1],-100]
	
	cou=0
	while cou<7:
		#cal fitness & update
		best=glob_best[1]
		for i in range(particles):

			value=caltech(tasks, decision[i])
			if value > history[i][1]:
				history[i][0]=decision[i]
				history[i][1]=value
			if value > glob_best[1]:
				glob_best[0]=decision[i]
				glob_best[1]=value

		if best==glob_best[1]:
			cou+=1
		else:
			cou=0
		
		#update velocity & position
		for i in range(particles):
			for j in range(users):
				velocity[i][j]=velocity[i][j]+0.01*(history[i][0][j]-decision[i][j])+0.01*(glob_best[0][j]-decision[i][j])
				decision[i][j]+=velocity[i][j]
				if decision[i][j]>1:
					decision[i][j]=1
				if decision[i][j]<0:
					decision[i][j]=0

	#print(glob_best)
	return glob_best[0]

def genetic(tasks):
	Maternal=dict()

	def cal_reward(tasks, decision):
		reward=0
		ss=0
		for i in range(len(decision)):
			if decision[i]!='0':
				ss+=(tasks[i]['a']*tasks[i]['pri'])**0.5
		
		for i in range(len(decision)):
			if decision[i]=='0':
				t=tasks[i]['d']/tasks[i]['fl']
				if t<tasks[i]['Tm']:
					reward+=tasks[i]['pri']*t*10
			else:
				bi=B*(tasks[i]['a']*tasks[i]['pri']**0.5)/ss
				t=tasks[i]['a']/bi/log2(1+tasks[i]['SINR'])
				if t<tasks[i]['Tm']:
					reward+=tasks[i]['pri']*(1-t/tasks[i]['Tm'])*10
				#else:
				#	reward-=tasks[1]['pri']*10

		return reward/len(tasks)/10

	def generate(size):
		for a in range(size):
			decision=''
			for b in range(users):
				if np.random.rand()<=0.25:
					decision+='1'
				else:
					decision+='0'
			Maternal[decision]=cal_reward(tasks, decision)

	def crossover(pairs, rank):
		parent=set()
		for e in range(2*pairs):
			a=np.random.rand()
			if a<rank[0][1]:
				parent.add(rank[0][0])
			else:
				accu=rank[0][1]
				for i in range(1, len(rank)):
					if a>accu and a<accu+rank[i][1]:
						parent.add(rank[i][0])
						break
					else:
						accu+=rank[i][1]

		while len(parent)>2:
			a=parent.pop()
			b=parent.pop()
			start=np.random.randint(len(a))
			end=np.random.randint(start,len(a))
			#if start>end:   start,end=end,start
			aa,bb='',''
			for j in range(start):
				aa+=a[j]
				bb+=b[j]
			for j in range(start, end):
				aa+=b[j]
				bb+=a[j]
			for j in range(end, len(a)):
				aa+=a[j]
				bb+=b[j]
			if aa not in Maternal:
				Maternal[aa]=cal_reward(tasks,aa)
			if bb not in Maternal:
				Maternal[bb]=cal_reward(tasks,bb)

			if np.random.rand()<0.06:
				muta1, muta2='', ''
				tar=np.random.randint(len(aa))
				for i in range(len(aa)):
					if i!=tar:
						muta1+=aa[i]
						muta2+=bb[i]
					else:
						muta1+=str(np.random.randint(2))
						muta2+=str(np.random.randint(2))
				if muta1 not in Maternal:
					Maternal[muta1]=cal_reward(tasks, muta1)
				if muta2 not in Maternal:
					Maternal[muta2]=cal_reward(tasks, muta2)

		if len(Maternal)>len(rank):
			for i in range(1, len(Maternal)-len(rank)+1):
				Maternal.pop(rank[-i][0])

	generate(100)
	cou=0
	st1=0
	while 1:
		total=0
		Roulette=Maternal.copy()
		for e in Roulette.values():
			total+=e
		for e in Roulette.keys():
			Roulette[e]/=total
		crossover(10, sorted(Roulette.items(), key=lambda kv: -kv[1]))
		if st1==sorted(Maternal.items(), key=lambda kv: -kv[1])[0][1]:
			cou+=1
		else:
			st1=sorted(Maternal.items(), key=lambda kv: -kv[1])[0][1]
			cou=0
		if cou>7:
			break
	decision=sorted(Maternal.items(), key=lambda kv: -kv[1])[0][0]

	return cal_reward(tasks,decision)

def test():
	perform=[0]*6
	for i in range(num):
		tasks=gen_task()
		perform[0]+=caltech(tasks, [0]*users)/num
		perform[1]+=caltech(tasks, [1]*users)/num
		perform[2]+=caltech(tasks, greedy(tasks))/num
		perform[3]+=caltech(tasks, GA_x(tasks))/num
		perform[4]+=caltech(tasks, PSO(tasks))/num
		perform[5]+=iterative(tasks)/num

	return perform

def draw_users():
	global users
	x=list()
	result=list()
	for e in range(6):
		result.append([])

	for e in range(x_num):
		perform=test()
		x.append(users)
		for i in range(6):
			result[i].append(perform[i])

		users+=10

	plt.plot(x,result[5],"go-",label='SS')
	plt.plot(x,result[4],"b*-",label='PSO')
	plt.plot(x,result[3],"ks-",label='GA')
	plt.plot(x,result[2],"yD-",label='Greedy')
	plt.plot(x,result[1],"rp-",label='FRE')
	plt.plot(x,result[0],"cx-",label='FLE')
	plt.xlabel("Number of users")
	plt.ylabel("QoS")
	plt.legend()
	#plt.savefig('servers.png', dpi = 600, bbox_inches='tight')
	plt.savefig('QoS.png', dpi = 600, bbox_inches='tight')
	plt.show()

def draw_avg():
	global avg

	x=list()
	result=list()
	for e in range(6):
		result.append([])

	for e in range(x_num):
		perform=test()
		x.append(avg)
		for i in range(6):
			result[i].append(perform[i])

		avg+=0.1

	plt.plot(x,result[5],"go-",label='SS')
	plt.plot(x,result[4],"b*-",label='PSO')
	plt.plot(x,result[3],"ks-",label='GA')
	plt.plot(x,result[2],"yD-",label='Greedy')
	plt.plot(x,result[1],"rp-",label='FRE')
	plt.plot(x,result[0],"cx-",label='FLE')
	plt.xlabel("Latency requirement")
	plt.ylabel("QoS")
	plt.legend()
	#plt.savefig('servers.png', dpi = 600, bbox_inches='tight')
	plt.savefig('Tm.png', dpi = 600, bbox_inches='tight')
	plt.show()

draw_avg()

#iterative/greedy:1.08, iterative/GA:1.18 ,2/24

#iterative/GA_x:1.22, iterative/GA: 1.18 (both no penalty) 2/25

#iterative/PSO:1.21, iterative/greedy: 1.57 2/28