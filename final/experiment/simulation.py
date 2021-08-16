import matplotlib.pyplot as plt
import numpy as np
from math import log2

#number of users
users=40
#system bandwidth unit: MHz
B=1
#background noise
N=1e-10
#Computing capacity of a MECS unit: GHz
F=100
#number of computer run
num=100
#number of index in x axis
x_num=7
#number of MECS
MEC=1
#
prob=10

#this function generate a set of tasks with specific requirements
def gen_task():
	tasks=dict()
	for i in range(users):
		buf=dict()
		#input data size unit: Megabit
		buf['a']=np.random.uniform(100,1000)/1000
		#workload (required CPU cycle)
		buf['d']=np.random.uniform(1000,2000)/1000
		#computing capacity of local device unit: GHz
		buf['fl']=np.random.uniform(1,2)
		#delay requirment unit: sec
		buf['Tm']=np.random.uniform(0.5,1.5)
		#subscription level
		buf['pri']=np.random.uniform(0.5,1)
		#7.5跟uniform(4,10)是用得意的參數自己手動算的值
		buf['SINR']=(10**np.random.uniform(4,10))*7.5/N
		tasks[i]=buf
	return tasks

#this function compute the sum of utility of users given the offloading ratio xi
def caltech(tasks, xi):
	#xi為陣列 包含每個user的offloading ratio

	#紀錄utility的變數
	reward=0
	#按照順序分配MEC (node association)
	en=list()
	for i in range(users):
		en.append(i%MEC+1)

	#存每個user bandwidt allocation bi與computing capacity fi的變數
	b=[0]*users
	f=[0]*users

	#暫存計算optimal 公式中分母的變數
	ss=[0]*(MEC+1)
	for k,v in tasks.items():
		#compute sum of sqrt (就是optimal結果公式中的分母)
		ss[0]+=(xi[k]*v['a']*v['pri']/(v['Tm']*log2(1+v['SINR'])) )**0.5
		ss[en[k]]+=(xi[k]*v['d']*v['pri']/v['Tm'])**0.5

	for k,v in tasks.items():
		#計算 bi 就是user i optimal的bandwidth allocation
		if ss[0]>0:
			b[k]=((xi[k]*v['a']*v['pri']/(v['Tm']*log2(1+v['SINR'])) )**0.5)*B/ss[0]
		#計算 fi 就是user i就是optimal的算力allocation
		if ss[en[k]]>0:
			f[k]=((xi[k]*v['d']*v['pri']/v['Tm'])**0.5)*F/ss[en[k]]

	#算每個task的utility
	for k,v in tasks.items():
		#如果offloading ratio>0
		if xi[k]>0:
			t=max( (1-xi[k])*v['d']/v['fl'], xi[k]*v['a']/b[k]/log2(1+v['SINR']) + xi[k]*v['d']/f[k] )
		else:
			t=v['d']/v['fl']

		#如果在delay requirement 內
		if t<v['Tm']:
			reward+=v['pri']*(1-t/(v['Tm']) )
		#否則一個定值的penalty
		else:
			reward-=v['pri']*0.5

	return reward/users

def cal_reward(tasks, xi, en):
	reward=0

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
			t=v['d']/v['fl']

		if t<v['Tm']:
			reward+=v['pri']*(1-t/(v['Tm']) )
		else:
			reward-=v['pri']*0.5

	return reward/users

#this function compute the optimal node association, 要用此圖請將使用者數調低
def optimal(tasks, xi):
	#強制複寫一台MEC的computing capacity
	global F
	F=34

	#用來存最好的解的utility與最好的解本身
	M_d=[0,0]

	#recusive下去瓊舉每個task assign到每個MEC的組合
	def search(tasks, xi, en):
		#print(en)
		#如果每個task都assign MEC了
		if len(en)==len(tasks):
			r=cal_reward(tasks, xi, en)
			if r>M_d[0]:
				M_d[0]=r
				M_d[1]=en
			return

		for i in range(1, MEC+1):
			search(tasks, xi, en + [i])

	search(tasks, xi, [])

	#回傳找到的解以及他的utility
	return M_d[0], M_d[1]

#我們論文中使用的greedy assign node association的方法 i.e. equation (38)
def entropy(tasks, xi):
	#強制複寫一台MEC的computing capacity
	global F
	F=34

	#將每個task 初始化assign到MEC server 1
	en=[1]*users
	#對task的priority做sort
	tasks_s=sorted(tasks.items(), key=lambda kv: -kv[1]['pri'] )
	
	for e in tasks_s:
		#現在的utility以及現在的node association
		M_d=[cal_reward(tasks, xi, en), en]
		
		for i in range(1+1, MEC+1):
			temp=en.copy()
			temp[e[0]]=i
			r=cal_reward(tasks, xi, temp)
			#如果將這個task assign到MEC server i 會使utility更高, 則改寫M_d
			if r>M_d[0]:
				M_d[0]=r
				M_d[1]=temp
		en=M_d[1]

	#回傳找到的解以及他的utility
	return cal_reward(tasks, xi, en), en

#隨機assign task到不同MEC server
def random(tasks, xi):
	#強制複寫一台MEC的computing capacity
	global F
	F=34
	en=list()
	for e in range(users):
		en.append(np.random.randint(1, MEC+1))

	#回傳找到的解以及他的utility
	return cal_reward(tasks, xi, en)

#用GA找node association
def GA_en(tasks, xi):
	#強制複寫一台MEC的computing capacity
	global F
	F=34
	Maternal=list()
	table=list()

	def generate(size):
		for a in range(size):
			en=list()
			for b in range(users):
				en.append(np.random.randint(1,MEC+1))

			table.append(en)
			Maternal.append([en, cal_reward(tasks, xi, en)])

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
				Maternal.append([aa, cal_reward(tasks, xi, aa)])
			if bb not in table:
				table.append(bb)
				Maternal.append([bb, cal_reward(tasks, xi, bb)])

			if np.random.rand()<0.16:
				muta1, muta2=list(), list()
				tar=np.random.randint(len(aa))
				for i in range(len(aa)):
					if i!=tar:
						muta1.append(aa[i])
						muta2.append(bb[i])
					else:
						muta1.append(np.random.randint(1,MEC+1))
						muta2.append(np.random.randint(1,MEC+1))
				if muta1 not in table:
					table.append(muta1)
					Maternal.append([muta1, cal_reward(tasks, xi, muta1)])
				if muta2 not in table:
					table.append(muta2)
					Maternal.append([muta2, cal_reward(tasks, xi, muta2)])

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

	en=sorted(Maternal, key=lambda kv: -kv[1])[0][0]

	#回傳找到的解以及他的utility
	return cal_reward(tasks, xi, en), en

#this function is the proposed AO-based algorithm, which will return the vector of offloading ratio xi
def iterative(tasks):

	#decision variable, 存每個user offloading ratio xi, bandwidt allocation bi與computing capacity fi的變數
	xi=list()
	b=[0]*users
	f=[0]*users

	#按照順序分配MEC (node association)
	en=list()
	for i in range(users):
		en.append(i%MEC+1)

	#initialize xi by eq (37)
	for e in tasks.values():
		xi.append( 1-min(1, e['Tm']*e['fl']/e['d']) )

	#暫存計算optimal 公式中分母的變數
	ss=[0]*(MEC+1)
	for k,v in tasks.items():
		#compute sum of sqrt (就是optimal結果公式中的分母)
		ss[0]+=(v['a']*v['pri']/(v['Tm']*log2(1+v['SINR'])) )**0.5
		ss[en[k]]+=(v['d']*v['pri']/v['Tm'])**0.5

	for k,v in tasks.items():
		#計算 bi 就是user i optimal的bandwidth allocation
		if ss[0]>0:
			b[k]=(((v['a']*v['pri']/(v['Tm']*log2(1+v['SINR'])) )**0.5)*B/ss[0])
		#計算 fi 就是user i optimal的算力 allocation
		if ss[en[k]]!=0:
			f[k]=((v['d']*v['pri']/v['Tm'])**0.5)*F/ss[en[k]]

	i=0
	while i<100:
		#update x by eq (21)
		for k,v in tasks.items():
			xi[k]=v['d']/v['fl']/( v['a']/(b[k]*log2(1+v['SINR'])) + v['d']/f[k] + v['d']/v['fl'] )

		#暫存計算optimal 公式中分母的變數
		ss=[0]*(MEC+1)
		for k,v in tasks.items():
			#compute sum of sqrt (就是optimal結果公式中的分母)
			ss[0]+=(xi[k]*v['a']*v['pri']/(v['Tm']*log2(1+v['SINR'])) )**0.5
			ss[en[k]]+=(xi[k]*v['d']*v['pri']/v['Tm'])**0.5

		for k,v in tasks.items():
			#計算 bi 就是user i optimal的bandwidth allocation
			if ss[0]>0:
				b[k]=(((xi[k]*v['a']*v['pri']/(v['Tm']*log2(1+v['SINR'])) )**0.5)*B/ss[0])
			#計算 fi 就是user i optimal的算力 allocation
			if ss[en[k]]!=0:
				f[k]=((xi[k]*v['d']*v['pri']/v['Tm'])**0.5)*F/ss[en[k]]

		i+=1

	#回傳user的offloading ratio陣列
	return xi

#one of the compared scheme: greedy
def greedy(tasks):

	#user的offloading ratio陣列
	xi=[0]*users
	#對task做sort
	tasks_s=sorted(tasks.items(), key=lambda kv: kv[1]['pri']/(kv[1]['d']/kv[1]['Tm']))

	#從sort完的陣列開始一個一個確認要不要offload
	for e in tasks_s:
		buf=xi.copy()
		buf[e[0]]=1
		#如果offload他的話整體utility會比沒有offload他高
		if caltech(tasks, buf)>caltech(tasks, xi):
			#就全offload這個task (xi=1)
			xi=buf
		else:
			break

	#回傳user的offloading ratio陣列
	return xi

#one of the compared scheme: PSO
def PSO(tasks):

	#particle的數量
	particles=200
	#solution vector of particles, 每個particle代表xi陣列的一組解(particle 第i個elemet是第i個user的offloading ratio)
	decision=list()
	#存每個particle每個維度(方向)的速度
	velocity=list()

	#initialize particles, 從第i個particle開始
	for i in range(particles):
		decision.append([])
		velocity.append([])

		#從第j個element開始  每個element是該user的offloading ratio
		for j in range(users):
			#以一定機率在產生非0的offloading ratio 並產生0.5到-0.5的速度
			if np.random.rand()<10/users:
				decision[i].append(np.random.rand())
				velocity[i].append(np.random.uniform(0.5,-0.5))
			else:
				decision[i].append(0)
				velocity[i].append(0)

	#紀錄每個粒子的歷史最大值
	history=list()
	for i in range(particles):
		history.append([decision[i],-100])
	glob_best=[decision[-1],-100]
	
	#如果連續10次最佳解都一樣則收斂
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

	#回傳最好的粒子(解) (xi, vector offloading ratio)
	return glob_best[0]

#one of the compared scheme: GA
def GA_x(tasks):

	#存母群體的變數
	Maternal=list()
	table=list()

	#產生size個初始染色體
	def generate(size):
		for a in range(size):
			xi=list()
			#決定一個染色體中每個element的值
			for b in range(users):
				#以一定機率產生非0的offloading ratio
				if np.random.rand()<15/users:
					xi.append(np.random.rand())
				else:
					xi.append(0)

			#將此染色體加到母群體中
			table.append(xi)
			Maternal.append([xi, caltech(tasks, xi)])

	#交配
	def crossover(pairs, rank):
		#存要交配的對象的變數(父母)
		parent=list()

		#選出2*pair個染色體當交配對象
		for e in range(2*pairs):
			#用輪盤法選
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

		#從選出來的交配對象中每次抽兩個出來交配直到袋子內的染色體都被抽完
		while len(parent)>2:
			#父母a跟b
			a=parent.pop()
			b=parent.pop()
			#多點交配 (從開始觸到結束處整段交換)
			start=np.random.randint(len(a))
			end=np.random.randint(start,len(a))

			#a跟b生的兩個叫aa跟bb
			aa,bb=list(),list()
			for j in range(users):
				if j not in range(start, end):
					aa.append(a[j])
					bb.append(b[j])
				else:
					aa.append(b[j])	
					bb.append(a[j])

			#新增aa, bb到母群體
			if aa not in table:
				table.append(aa)
				Maternal.append([aa, caltech(tasks,aa)])
			if bb not in table:
				table.append(bb)
				Maternal.append([bb, caltech(tasks,bb)])

			#以一定機率突變
			if np.random.rand()<0.16:
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

		#如果母群體數量超過一定 則刪掉排名倒數的染色體
		if len(Maternal)>len(rank):
			for i in range(1, len(Maternal)-len(rank)+1):
				Maternal.pop(Maternal.index(rank[-i]))

	generate(200)
	
	#如果連續10次最好的染色體都一樣則收斂
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

	#回傳最好的染色體(vector of offloading ratio)
	return xi

#compute the average utility under current system settings
def test():
	#存各algorithm的performance的變數
	perform=[0]*6
	#看要重複做幾次取平均
	for i in range(num):
		tasks=gen_task()
		perform[0]+=caltech(tasks, [0]*users)/num
		perform[1]+=caltech(tasks, np.random.randint(1,MEC+1,users) )/num
		perform[2]+=caltech(tasks, greedy(tasks))/num
		perform[3]+=caltech(tasks, GA_x(tasks))/num
		perform[4]+=caltech(tasks, PSO(tasks))/num
		perform[5]+=caltech(tasks, iterative(tasks))/num

	return perform

#畫user數對average utility的圖
def draw_users():
	#最後圖用的數據:
	#result=[[-0.10689215350174067, -0.12258751955370198, -0.10664938851603122, -0.10914649076739066, -0.10352928516081307, -0.11127262145823709, -0.11005122844295091], [0.5598836536425962, 0.36792046928941746, 0.1649824545931375, -0.10109683084887193, -0.28177171302590576, -0.3590176136757609, -0.37326622068182996], [0.5598964288522993, 0.34955962066748136, 0.21763963785257454, 0.13635219564725318, 0.09686138192362795, 0.052573965820916654, 0.026589646026615635], [0.5216173876758898, 0.40404328923329014, 0.31663210920423096, 0.24558096638413635, 0.192273764101235, 0.1277150637090219, 0.07557143521468176], [0.5598836536425962, 0.3527461792501668, 0.22769903483542914, 0.14634974843610654, 0.10359187562921575, 0.06347987540291242, 0.040366798345693726], [0.5966541623574921, 0.4902104750325136, 0.42170249237138857, 0.3646301289171351, 0.32061896540159845, 0.2731650095641522, 0.23237548736062189]]
	#x=[10,20,30,40,50,60,70]
	
	global users
	global prob
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
	plt.xlabel("Number of active SSs")
	plt.ylabel("Average utility")
	plt.legend()
	plt.savefig('QoS.jpg', dpi = 600, bbox_inches='tight')
	plt.show()

#畫alpha對average utility的圖
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
	plt.savefig('alpha.jpg', dpi = 600, bbox_inches='tight')
	plt.show()

#畫beta對average utility的圖
def draw_beta():
	global users
	global F
	global B
	global prob
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
		print(F)
		F+=20
		prob+=2
	
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
	plt.savefig('beta.jpg', dpi = 600, bbox_inches='tight')
	plt.show()

#畫optimal的圖
def draw_optimal():
	'''tasks=gen_task()
	xi=iterative(tasks)
	rSS, SS= entropy(tasks,xi)
	print(rSS, SS)
	rOPT, OPT=optimal(tasks,xi)
	print(rOPT, OPT)
	print((rOPT-rSS)/rOPT)
	xi=GA_x(tasks)
	rGA, GA=GA_en(tasks,xi)
	print(rGA, GA)
	print((rOPT-rGA)/rOPT)
	xi=PSO(tasks)
	rPSO, PSO=GA_en(tasks,xi)
	print(rPSO, PSO, 'PSO')
	xi=greedy(tasks)
	RAN=random(tasks,xi)
	print(RAN, (rOPT-RAN)/rOPT)

	tasks=gen_task()
	xi=[0]*users
	print(random(tasks,xi))
	xi=[1]*users
	print(random(tasks,xi))'''

	#最後圖用的數據:
	#如要重新做則將上面的註解消掉, 先生成一組task然後用iterative找出xi 再來用不同的比較方法找出在這組xi下的node association
	x=['Opt', 'The Proposed', 'PSO', 'GA', 'greedy', 'FLE', 'FRE']
	a=[0.5731757667479276, 0.5704970428153521, 0.54, 0.5109011906529753, 0.44350087376304836, -0.10186141054581883, -0.37017025939914894]
	plt.bar(x,a, color=['r', 'g', 'b', 'm', 'y', 'k', 'c'])
	plt.ylabel("Average Utility")
	plt.savefig('OPT.jpg', dpi=600,bbox_inches='tight')
	plt.show()

draw_users()