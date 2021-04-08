from keras.layers import Flatten, Dense, Activation
from keras.models import Sequential
from math import log2
from time import time
import matplotlib.pyplot as plt
import numpy as np

traffic=[29, 32, 39, 43, 50, 38, 38, 22, 12, 6, 3, 2, 3, 3, 7, 12, 15, 20, 28, 26, 33, 39, 36, 44, 30, 36, 41, 50, 48, 45, 32, 22, 12, 7, 4, 2, 1, 3, 7, 13, 25, 30, 28, 37, 39, 42, 47, 38, 32, 43, 45, 44, 49, 51, 42, 31, 19, 9, 5, 3, 2, 3, 6, 13, 19, 27, 27, 32, 43, 47, 55, 46, 35, 36, 39, 43, 38, 46, 37, 29, 23, 15, 6, 2, 1, 2, 4, 6, 13, 18, 26, 35, 37, 37, 36, 43, 39, 37, 48, 43, 43, 40, 35, 31, 21, 14, 6, 3, 2, 2, 3, 7, 11, 17, 25, 34, 40, 41, 43, 38, 26, 32, 41, 36, 43, 52, 39, 28, 20, 13, 6, 4, 3, 3, 7, 17, 24, 26, 37, 34, 39, 38, 46, 44, 37, 38, 47, 48, 52, 59, 46, 30, 16, 9, 3, 2, 3, 3, 6, 16, 19, 23, 26, 32, 33, 39, 44, 43, 33, 41, 42, 39, 51, 57, 44, 28, 20, 10, 5, 2, 1, 3, 6, 12, 23, 28, 27, 34, 35, 48, 50, 49, 36, 44, 45, 44, 49, 51, 48, 32, 20, 12, 5, 4, 2, 3, 6, 15, 19, 19, 33, 33, 33, 43, 46, 39, 35, 42, 48, 47, 51, 63, 50, 35, 24, 14, 6, 3, 2, 2, 6, 14, 22, 29, 26, 33, 42, 48, 48, 42, 37, 41, 41, 38, 41, 40, 33, 26, 22, 12, 5, 3, 1, 2, 3, 9, 14, 20, 22, 29, 33, 35, 38, 41, 35, 38, 38, 42, 42, 42, 36, 31, 24, 17, 9, 5, 4, 3, 3, 3, 10, 16, 21, 29, 33, 39, 42, 39, 32, 46, 49, 52, 52, 57, 45, 32, 20, 10, 3, 4, 3, 2]

history=6
epsilon=1
gamma=0.8
zeta=150

N=1e-10
F=10

num=20

def cal_profit(users, action):

	def gen_task():
		tasks=dict()
		for i in range(users):
			buf=dict()
			buf['a']=np.random.uniform(100,1000)*2/1000
			buf['d']=buf['a']
			buf['fl']=np.random.uniform(1.5,2.5)
			buf['Tm']=np.random.uniform(0.1,1)
			buf['pri']=np.random.uniform(0.1,1)*5
			buf['SINR']=(10**np.random.uniform(4,10))*7.5/N
			tasks[i]=buf
		return tasks

	def iterative(tasks):
		B=0.1+action*0.3

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

	QoS=iterative(gen_task())
	revenue=users*QoS*4

	#profit
	return revenue-zeta*(0.1+action*0.3)/1.3


#DRL
def DQL():
	Q=dict()
	exp_x, exp_y=list(), list()

	#DNN
	DNN = Sequential()
	DNN.add(Dense(64, input_shape=(history,)) )
	DNN.add(Dense(64, activation="relu"))
	DNN.add(Dense(5))
	DNN.compile(loss='mae', optimizer='adam', metrics=['mae'])

	def init():
		for i in range(history, len(traffic)-1):
			Q[str(traffic[i-history:i])]=dict()
			for e in range(5):
				Q[str(traffic[i-history:i])][e]=0


	#agent explore env 一個episode
	def play(episode):
		global epsilon
		start=time()
		for i in range(history, len(traffic)-1):
			state=traffic[i-history:i]
			exp_x.append(state)

			#epsilon-greedy
			if np.random.rand()<epsilon:
				action=np.random.randint(5)

			else:
				action=DNN.predict(np.array([state]))[0]
				action=list(action).index(max(action))

			if episode>0.01:
				epsilon-=(1-0.01)/10000

			target_Q=DNN.predict(np.array([state]))[0]
			Q[str(state)][action]=(cal_profit(traffic[i+1], action) + Q[str(state)][action]*episode )/(episode+1)
			target_Q[action]=Q[str(state)][action]
			exp_y.append(target_Q)
		

			if len(exp_x)>500:
				exp_x.pop(0)
				exp_y.pop(0)

			if episode%20==0:
				DNN.fit([exp_x], [exp_y], epochs=2, batch_size=150)
		print(time()-start)

	#放現在的agent進去玩
	def exam():
		profit=list()
		perform=0
		for i in range(history, len(traffic)-1):
			state=traffic[i-history:i]
			
			action=DNN.predict(np.array([state]))[0]
			action=list(action).index(max(action))

			for e in range(num):
				perform+=cal_profit(traffic[i+1], action)/traffic[i+1]/num

		return perform/len(traffic)


	def main():
		init()
		episode=1

		x=list()
		result=list()

		while episode<1000:
			play(episode)

			#test revenue
			if episode%100==0:
				x.append(episode)
				result.append(exam())
			print(episode)
			episode+=1

		plt.plot(x,result,"go-",label='unit_profit')
		plt.legend()
		plt.savefig('unit_profit.jpg', dpi=600, bbox_inches='tight')
		plt.show()

	main()


#純QL, 
def QL():
	Q=dict()

	#Q table
	def init():
		for i in range(history, len(traffic)-1):
			Q[str(traffic[i-history:i])]=dict()
			for e in range(5):
				Q[str(traffic[i-history:i])][e]=0

	#一個episode
	def play(episode):
		global epsilon
		start=time()
		for i in range(history, len(traffic)-1):
			state=str(traffic[i-history:i])
			#epsilon-greedy
			if np.random.rand()<epsilon:
				action=np.random.randint(5)

			else:
				best, action= 0, 0
				for e in Q[state]:
					if Q[state][e]>best:
						best=Q[state][e]
						action=e
				if best==0:
					action=np.random.randint(5)

			if episode>0.01:
				epsilon-=(1-0.01)/10000

			Q[state][action]=(cal_profit(traffic[i+1], action) + Q[state][action]*episode )/(episode+1)
		print(time()-start)

	#放現在的agent進去玩
	def exam():
		profit=list()
		perform=0
		for i in range(history, len(traffic)-1):
			state=str(traffic[i-history:i])
			best, action= 0, 0
			for e in Q[state]:
				if Q[state][e]>best:
					best=Q[state][e]
					action=e
			if best==0:
				action=np.random.randint(5)
			#print('next:',traffic[i+1],'action:',0.1+action*0.3)
			for e in range(num):
				perform+=cal_profit(traffic[i+1], action)/traffic[i+1]/num
			#profit.append(cal_profit(traffic[i+1], action)/traffic[i+1])

		return perform/len(traffic)
		#plt.plot(traffic[6:],label='real')
		#plt.plot(profit,label='revenue')
		#plt.legend()
		#plt.show()


	def main():
		episode=0
		init()

		x=list()
		result=list()

		while episode<1000:
			play(episode)
			#test revenue
			if episode%100==0:
				x.append(episode)
				result.append(exam())
			print(episode)
			episode+=1

		plt.plot(x,result,"go-",label='unit_profit')
		plt.legend()
		plt.savefig('unit_profit.jpg', dpi=600, bbox_inches='tight')
		plt.show()

	main()

DQL()

#4/8: QL, DQL done, traffic range 2~50, for 0.3, revenue=0.6~15*5, for 1.3, revenue=1~25*5