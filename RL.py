#from keras.layers import Flatten, Dense, Activation
#from keras.models import Sequential
import numpy as np

history=6
epsilon=0.1
explore=3000000
gamma=0.8

def cal_QoS(users, action):
	def gen_task():
		tasks=dict()
		for i in range(users):
			buf=dict()
			buf['a']=np.random.uniform(100,1000)*2/1000
			buf['d']=buf['a']
			buf['fl']=np.random.uniform(1.5,2.5)
			buf['Tm']=np.random.uniform(0.1,1)
			buf['pri']=np.random.uniform(0.1,1)
			buf['SINR']=(10**np.random.uniform(4,10))*7.5/N
			tasks[i]=buf
		return tasks

	def iterative(tasks):
		B=0.5+action/10

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

	return iterative(gen_task())


#DRL
def gen_data():
	pass

#純QL, 
def QL():
	traffic=[29, 32, 39, 43, 50, 38, 38, 22, 12, 6, 3, 2, 3, 3, 7, 12, 15, 20, 28, 26, 33, 39, 36, 44, 30, 36, 41, 50, 48, 45, 32, 22, 12, 7, 4, 2, 1, 3, 7, 13, 25, 30, 28, 37, 39, 42, 47, 38, 32, 43, 45, 44, 49, 51, 42, 31, 19, 9, 5, 3, 2, 3, 6, 13, 19, 27, 27, 32, 43, 47, 55, 46, 35, 36, 39, 43, 38, 46, 37, 29, 23, 15, 6, 2, 1, 2, 4, 6, 13, 18, 26, 35, 37, 37, 36, 43, 39, 37, 48, 43, 43, 40, 35, 31, 21, 14, 6, 3, 2, 2, 3, 7, 11, 17, 25, 34, 40, 41, 43, 38, 26, 32, 41, 36, 43, 52, 39, 28, 20, 13, 6, 4, 3, 3, 7, 17, 24, 26, 37, 34, 39, 38, 46, 44, 37, 38, 47, 48, 52, 59, 46, 30, 16, 9, 3, 2, 3, 3, 6, 16, 19, 23, 26, 32, 33, 39, 44, 43, 33, 41, 42, 39, 51, 57, 44, 28, 20, 10, 5, 2, 1, 3, 6, 12, 23, 28, 27, 34, 35, 48, 50, 49, 36, 44, 45, 44, 49, 51, 48, 32, 20, 12, 5, 4, 2, 3, 6, 15, 19, 19, 33, 33, 33, 43, 46, 39, 35, 42, 48, 47, 51, 63, 50, 35, 24, 14, 6, 3, 2, 2, 6, 14, 22, 29, 26, 33, 42, 48, 48, 42, 37, 41, 41, 38, 41, 40, 33, 26, 22, 12, 5, 3, 1, 2, 3, 9, 14, 20, 22, 29, 33, 35, 38, 41, 35, 38, 38, 42, 42, 42, 36, 31, 24, 17, 9, 5, 4, 3, 3, 3, 10, 16, 21, 29, 33, 39, 42, 39, 32, 46, 49, 52, 52, 57, 45, 32, 20, 10, 3, 4, 3, 2]
	Q=dict()

	#Q table
	def init():
		for i in range(6, len(traffic)-1):
			Q[str(traffic[i-6:i])]=dict()
			for e in range(11):		
				Q[str(traffic[i-6:i])][e]=0

	#一個episode
	def play(episode):
		for i in range(6, len(traffic)-1):

			#epsilon-greedy
			if np.random.rand()<0.2:
				action=np.random.randint(11)

			else:
				best, action= 0, 0
				for e in Q[str(traffic[i-6:i])]:
					if Q[str(traffic[i-6:i])][e]>best:
						best=Q[str(traffic[i-6:i])][e]
						action=e
				if best==0:
					action=np.random.randint(11)

			Q[str(traffic[i-6:i])][action]=(cal_QoS(traffic[i+1], action)+Q[str(traffic[i-6:i])][action]*episode)/(episode+1)

			#if epsilon>0.0001:
			#	epsilon-=(0.1-0.0001)/explore

	def exam():
		pass


	def main():
		episode=1
		init()

		while 1:
			play(episode)
			episode+=1
			#test revenue

QL()


def DNN():

	model = Sequential()
	model.add(Dense(32, input_shape=(10,)) )
	model.add(Dense(32, activation="relu"))
	model.add(Dense(1))
	model.compile(loss='mae', optimizer='adam', metrics=['mae'])
	model.fit([train_x], [train_y], epochs=1000, batch_size=100)
