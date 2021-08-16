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

#發offloading request到server
def cal_real(tasks, xi):
	#xi為陣列 包含每個user的offloading ratio
	global action

	#紀錄utility的變數
	reward=0

	#按照順序assign MEC (node association)
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
		#計算 fi 就是user i optimal的算力 allocation
		if ss[en[k]]>0:
			f[k]=((xi[k]*v['d']*v['pri']/v['Tm'])**0.5)/ss[en[k]]

	#算每個task的utility
	for k,v in tasks.items():
		#如果offloading ratio>0
		if xi[k]>0:
			#offload的part:
			load=dict()
			#指定要對該張圖重複detection, projection, rendering的次數 (以重複的次數來製造不同的workload), 10是自己條的參數讓數字對上 沒意義
			load['round']=int(xi[k]*v['d']*10)
			#發request到server 並指定次數, 須自己改server ip跟port
			r=requests.post('http://35.236.175.215:80', data = json.dumps(load))
			
			#server會回傳execution time, 5.27是我用GCP實測的一個校正值, 要根據你用的機器重新設
			#因為機器是queue一次只算一個並全力算, 所以實際運算時間要除以f[k]來模擬如果server 只分配f[k]的算力給那個task
			#校正方法: 重複一次AR那三個步驟所花的運算時間要與我們模擬設定中一個MEC全力算一個['d']=1000的task的運算時間一致, 所以我就時間直接/5.27的倍數使他們一致
			tiex=json.loads(r.text)['t']/5.27/f[k]
			#tiex=xi[k]*v['d']*fs[action]*0.0135/f[k]

			#transmission time是模擬的, 因為我們不能控制BS
			titx=xi[k]*v['a']/b[k]/log2(1+v['SINR'])
			#備註: 照片是同一張在server上 所以不用傳過去 全部就只有server自己本地運算並傳回來時間
			
			#最終與local計算的值取max
			t=max((1-xi[k])*v['d']/v['fl'], tiex+titx)
		
		else:
			t=v['d']/v['fl']

		#如果在delay requirement 內
		if t<v['Tm']:
			reward+=v['pri']*(1-t/(v['Tm']) )
		#否則一個定值的penalty
		else:
			reward-=v['pri']*0.5

	#回傳平均的utility
	return reward/users

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

	#回傳平均的utility
	return reward/users

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

def draw_users():
	#最後圖用的數據: 要畫就把註解拿掉  並把下面整段註解掉留下x跟plt.plot
	#result=[[-0.0560508543470955, -0.10232465113244134, -0.08640974215979584, -0.10710901409832328, -0.11701713688781498, -0.10427602351274189, -0.09746809895744712], [0.548330167484117, 0.3653749717294511, 0.1768105388819655, -0.10271013881293471, -0.30076116751519966, -0.3590444674082899, -0.3728112232960363], [0.5484052377587394, 0.3437210604302775, 0.18770637488011946, 0.09592393671138162, 0.027454697703110265, 0.009635876510567265, -0.0025874877668921447], [0.5084444599247216, 0.40346103604543243, 0.32688844161312286, 0.24020588553937477, 0.17849576879610227, 0.1285555842597195, 0.07409804858965259], [0.5484031817144704, 0.3581137583822125, 0.24268856218335222, 0.1448008236867084, 0.08426471425537715, 0.06177033436629506, 0.04645799788399567], [0.5844750504728554, 0.4874066022708568, 0.4296211836404238, 0.3629855676683852, 0.29489952781163703, 0.2606597573873945, 0.23213894889176406]]	
	#x=[10,20,30,40,50,60,70]
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
	plt.xlabel("Number of active SSs")
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
	#最後圖用的數據: 要畫就把註解拿掉  並把下面整段註解掉留下x跟plt.plot
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