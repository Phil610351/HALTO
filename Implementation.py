import matplotlib.pyplot as plt
import numpy as np
import requests
import json
from math import log2

users=10
B=1
N=1e-10
F=100
avg=0.1
num=15
x_num=7
MEC=1
prob=10
#fs=[257.73,561.8,781.25,1176.5,1351.35,1587.3,1887.8]
fs=[3.88,1.78,1.28,0.85,0.74,0.63,0.53]
action=0

def gen_task():
	tasks=dict()
	for i in range(users):
		buf=dict()
		buf['a']=np.random.uniform(100,1000)/1000
		buf['d']=np.random.uniform(1000,2000)/1000
		buf['fl']=np.random.uniform(1,2)
		buf['Tm']=np.random.uniform(0.5,1.5)
		buf['pri']=np.random.uniform(0.5,1)
		buf['SINR']=(10**np.random.uniform(4,10))*7.5/N
		tasks[i]=buf
	return tasks

#發offloading request到server
def cal_real(tasks, xi):
	global action
	reward=0
	en=list()
	for i in range(users):
		en.append(i%MEC+1)

	b=[0]*users
	f=[0]*users

	#sum of sqrt
	ss=[0]*(MEC+1)
	for k,v in tasks.items():
		ss[0]+=(xi[k]*v['a']*v['pri']/(v['Tm']*log2(1+v['SINR'])) )**0.5
		ss[en[k]]+=(xi[k]*v['d']*v['pri']/v['Tm'])**0.5

	for k,v in tasks.items():
		#cal lagrange b
		if ss[0]>0:
			b[k]=((xi[k]*v['a']*v['pri']/(v['Tm']*log2(1+v['SINR'])) )**0.5)*B/ss[0]
		#cal lagrange f
		if ss[en[k]]>0:
			f[k]=((xi[k]*v['d']*v['pri']/v['Tm'])**0.5)/ss[en[k]]

	for k,v in tasks.items():
		if xi[k]>0:
			load=dict()
			load['round']=int(xi[k]*v['d']*100)
			r=requests.post('http://35.236.175.215:80', data = json.dumps(load))
			tiex=json.loads(r.text)['t']/5.27/f[k]
			#tiex=xi[k]*v['d']*fs[action]*0.0135/f[k]
			#print((1-xi[k])*v['d']/v['fl'], tiex)
			titx=xi[k]*v['a']/b[k]/log2(1+v['SINR'])
			t=max((1-xi[k])*v['d']/v['fl'], tiex+titx)
		
		else:
			t=v['d']/v['fl']

		if t<v['Tm']:
			reward+=v['pri']*(1-t/(v['Tm']) )
		else:
			reward-=v['pri']*0.5

	return reward/users

def caltech(tasks, xi):
	reward=0
	en=list()
	for i in range(users):
		en.append(i%MEC+1)

	b=[0]*users
	f=[0]*users

	#sum of sqrt
	ss=[0]*(MEC+1)
	for k,v in tasks.items():
		ss[0]+=(xi[k]*v['a']*v['pri']/(v['Tm']*log2(1+v['SINR'])) )**0.5
		ss[en[k]]+=(xi[k]*v['d']*v['pri']/v['Tm'])**0.5

	for k,v in tasks.items():
		#cal lagrange b
		if ss[0]>0:
			b[k]=((xi[k]*v['a']*v['pri']/(v['Tm']*log2(1+v['SINR'])) )**0.5)*B/ss[0]
		#cal lagrange f
		if ss[en[k]]>0:
			f[k]=((xi[k]*v['d']*v['pri']/v['Tm'])**0.5)*F/ss[en[k]]

	for k,v in tasks.items():
		if xi[k]>0:
			t=max( (1-xi[k])*v['d']/v['fl'], xi[k]*v['a']/b[k]/log2(1+v['SINR']) + xi[k]*v['d']/f[k] )
		else:
			t=(1-xi[k])*v['d']/v['fl']

		if t<v['Tm']:
			reward+=v['pri']*(1-t/(v['Tm']) )
		else:
			reward-=v['pri']*0.5

	return reward/users

def iterative(tasks):
	xi=list()
	b=[0]*users
	f=[0]*users
	en=list()
	for i in range(users):
		en.append(i%MEC+1)

	for e in tasks.values():
		xi.append( 1-min(1, e['Tm']*e['fl']/e['d']) )

	#sum of sqrt
	ss=[0]*(MEC+1)
	for k,v in tasks.items():
		ss[0]+=(v['a']*v['pri']/(v['Tm']*log2(1+v['SINR'])) )**0.5
		ss[en[k]]+=(v['d']*v['pri']/v['Tm'])**0.5

	for k,v in tasks.items():
		#cal lagrange b
		if ss[0]>0:
			b[k]=(((v['a']*v['pri']/(v['Tm']*log2(1+v['SINR'])) )**0.5)*B/ss[0])
		#cal lagrange f
		if ss[en[k]]!=0:
			f[k]=((v['d']*v['pri']/v['Tm'])**0.5)*F/ss[en[k]]

	i=0
	while i<10:
		#update x
		for k,v in tasks.items():
			xi[k]=v['d']/v['fl']/( v['a']/(b[k]*log2(1+v['SINR'])) + v['d']/f[k] + v['d']/v['fl'] )

		#sum of sqrt
		ss=[0]*(MEC+1)
		for k,v in tasks.items():
			ss[0]+=(xi[k]*v['a']*v['pri']/(v['Tm']*log2(1+v['SINR'])) )**0.5
			ss[en[k]]+=(xi[k]*v['d']*v['pri']/v['Tm'])**0.5

		for k,v in tasks.items():
			#cal lagrange b
			if ss[0]>0:
				b[k]=(((xi[k]*v['a']*v['pri']/(v['Tm']*log2(1+v['SINR'])) )**0.5)*B/ss[0])

			#cal lagrange f
			if ss[en[k]]>0:
				f[k]=((xi[k]*v['d']*v['pri']/v['Tm'])**0.5)*F/ss[en[k]]

		i+=1

	return xi

def greedy(tasks):
	xi=[0]*users
	tasks_s=sorted(tasks.items(), key=lambda kv: kv[1]['pri'])

	for e in tasks_s:
		buf=xi.copy()
		buf[e[0]]=1
		if caltech(tasks, buf)>caltech(tasks,xi):
			xi=buf
		else:
			break
	return xi

def GA_x(tasks):
	Maternal=list()
	table=list()
	def generate(size):
		for a in range(size):
			decision=list()
			for b in range(users):
				if np.random.rand()<25/users:
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
		crossover(20, sorted(Roulette, key=lambda kv: -kv[1]))
		if sorted(Maternal, key=lambda kv: -kv[1])[0][1]-st1<0.0001:
			cou+=1
		else:
			st1=sorted(Maternal, key=lambda kv: -kv[1])[0][1]
			cou=0
		if cou>10:
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
			if np.random.rand()<prob/users:
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
	while cou<10:
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
				velocity[i][j]=velocity[i][j]+0.001*(history[i][0][j]-decision[i][j])+0.001*(glob_best[0][j]-decision[i][j])
				decision[i][j]+=velocity[i][j]
				if decision[i][j]>1:
					decision[i][j]=1
				if decision[i][j]<0:
					decision[i][j]=0

	return glob_best[0]

def test():
	perform=[0]*6
	for i in range(num):
		tasks=gen_task()
		perform[0]+=cal_real(tasks, [0]*users)/num
		perform[1]+=cal_real(tasks, [1]*users)/num
		perform[2]+=cal_real(tasks, greedy(tasks))/num
		perform[3]+=cal_real(tasks, GA_x(tasks))/num
		perform[4]+=cal_real(tasks, PSO(tasks))/num
		perform[5]+=cal_real(tasks, iterative(tasks))/num
		
	return perform

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
	plt.ylabel("Average utility")
	plt.legend()
	#plt.savefig('servers.png', dpi = 600, bbox_inches='tight')
	plt.savefig('Tm.jpg', dpi = 600, bbox_inches='tight')
	plt.show()

def draw_users():
	#[[-0.0560508543470955, -0.10232465113244134, -0.08640974215979584, -0.10710901409832328, -0.11701713688781498, -0.10427602351274189, -0.09746809895744712], [0.548330167484117, 0.3653749717294511, 0.1768105388819655, -0.10271013881293471, -0.30076116751519966, -0.3590444674082899, -0.3728112232960363], [0.5484052377587394, 0.3437210604302775, 0.18770637488011946, 0.09592393671138162, 0.027454697703110265, 0.009635876510567265, -0.0025874877668921447], [0.5084444599247216, 0.40346103604543243, 0.32688844161312286, 0.24020588553937477, 0.17849576879610227, 0.1285555842597195, 0.07409804858965259], [0.5484031817144704, 0.3581137583822125, 0.24268856218335222, 0.1448008236867084, 0.08426471425537715, 0.06177033436629506, 0.04645799788399567], [0.5844750504728554, 0.4874066022708568, 0.4296211836404238, 0.3629855676683852, 0.29489952781163703, 0.2606597573873945, 0.23213894889176406]]	
	global users
	global B
	global F

	users=10
	B=1
	F=100

	x=list()
	result=list()
	for e in range(6):
		result.append([])

	for e in range(x_num):
		perform=test()
		x.append(users)
		for i in range(6):
			result[i].append(perform[i])
		print(users)
		users+=10

	print('users', result)
	plt.plot(x,result[5],"go-",label='The Proposed')
	plt.plot(x,result[4],"b*-",label='PSO')
	plt.plot(x,result[3],"ks-",label='GA')
	plt.plot(x,result[2],"yD-",label='Greedy')
	plt.plot(x,result[1],"rp-",label='FRE')
	plt.plot(x,result[0],"cx-",label='FLE')
	plt.xlabel("Number of users")
	plt.ylabel("Average utility")
	plt.legend()
	plt.savefig('QoS_imp.jpg', dpi = 600, bbox_inches='tight')
	plt.show()

def draw_alpha():
	global users
	global B
	global F
	global prob

	users=40
	B=0.1
	F=100

	x=[0.1, 0.25, 0.4, 0.55, 0.7, 0.85, 1.0]

	result=list()
	for e in range(6):
		result.append([])

	for j in range(x_num):

		perform=test()
		for i in range(6):
			result[i].append(perform[i])
		print(B)
		B+=0.3
		prob+=2

	print('alpha', result)
	plt.plot(x,result[5],"go-",label='The Proposed')
	plt.plot(x,result[4],"b*-",label='PSO')
	plt.plot(x,result[3],"ks-",label='GA')
	plt.plot(x,result[2],"yD-",label='Greedy')
	plt.plot(x,result[1],"rp-",label='FRE')
	plt.plot(x,result[0],"cx-",label='FLE')
	plt.xlabel("The ratio of rented bandwidth")
	plt.ylabel("Average utility")
	plt.legend()
	plt.savefig('alpha_imp.jpg', dpi = 600, bbox_inches='tight')
	plt.show()

def draw_beta():
	#x=[[-0.10879866106844496, -0.11725025079956199, -0.10660510841711787, -0.11307704027337126, -0.10846732152428108, -0.10475123288444127, -0.10961808048181076], [-0.3749322977885126, -0.3771214321787286, -0.3563549649219013, -0.18841551556259342, -0.10790901209306714, -0.011781798089643171, 0.07373219562962838], [-0.06064481973306977, -0.018508742744827476, 0.021803399810650333, 0.05989479993998011, 0.08219146589725494, 0.10981912346140983, 0.1347166412008365], [-0.07544592302405732, -0.022176138334315636, 0.08976727156335386, 0.16292029465350574, 0.210722604423403, 0.24865832198388652, 0.263096845846362], [-0.10681923867930895, 0.009741945141403549, 0.0801422701583021, 0.14517171688614863, 0.16103560178069748, 0.1920991471197749, 0.21557720297242255], [0.04185391797899397, 0.19519541692279052, 0.268333364296298, 0.3322189081800225, 0.3584201158200735, 0.3833790799939305, 0.4025883589486936]]
	global users
	global F
	global prob
	global action

	users=40
	B=1
	F=20

	x=[0.1, 0.25, 0.4, 0.55, 0.7, 0.85, 1.0]

	result=list()
	for e in range(6):
		result.append([])

	for j in range(x_num):

		perform=test()
		for i in range(6):
			result[i].append(perform[i])
		print(action)
		action+=1
		prob+=2
		F+=20
	
	print('beta', result)
	plt.plot(x,result[5],"go-",label='The Proposed')
	plt.plot(x,result[4],"b*-",label='PSO')
	plt.plot(x,result[3],"ks-",label='GA')
	plt.plot(x,result[2],"yD-",label='Greedy')
	plt.plot(x,result[1],"rp-",label='FRE')
	plt.plot(x,result[0],"cx-",label='FLE')
	plt.xlabel("The ratio of rented computing capacity")
	plt.ylabel("Average utility")
	plt.legend()
	plt.savefig('beta_imp.jpg', dpi = 600, bbox_inches='tight')
	plt.show()

draw_users()