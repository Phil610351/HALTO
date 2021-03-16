import matplotlib.pyplot as plt
import numpy as np
from statsmodels.tsa.holtwinters import ExponentialSmoothing, SimpleExpSmoothing, Holt
from statsmodels.tsa.arima_model import ARIMA
from keras.layers import Flatten, Dense, Activation
from keras.models import Sequential

train_x=list()
train_y=list()
y=list()
with open("train.dat") as f:
	a=f.read().split('\n')
	count=0
	hour=0
	buf=list()
	for e in a:
		e=e.split()
		#if int(e[0][:10])-1189809385>60*hour:
		if int(e[0][:10])-1201639675>60*hour:
			y.append(count)
			buf.append(count)				
			count=0
			hour+=1
			
			if len(buf)>10:
				buf.pop(0)
				train_y.append(buf[-1])
				train_x.append(buf[:])
		else:
			count+=1
		
		if hour>5000:
			break

train_y.pop(0)
train_x.pop()
print(len(train_x),len(train_y))

DNN = Sequential()
DNN.add(Dense(32, input_shape=(10,)) )
DNN.add(Dense(32, activation="relu"))
DNN.add(Dense(1))
DNN.compile(loss='mae', optimizer='adam', metrics=['mae'])
DNN.fit([train_x], [train_y], epochs=1000, batch_size=100)

y=list()
train_x=list()
train_y=list()
with open("test.dat") as f:
	a=f.read().split('\n')
	count=0
	hour=0
	buf=list()
	for e in a:
		e=e.split()
		if int(e[0][:10])-1189809385>60*hour:
			y.append(count)
			buf.append(count)				
			count=0
			hour+=1
			
			if len(buf)>10:
				buf.pop(0)
				train_y.append(buf[-1])
				train_x.append(buf[:])
		else:
			count+=1
		if hour>5000:
			break

print(train_x)
y=DNN.predict( np.array(train_x))

'''plt.plot(y[:48], label='DNN')
plt.plot(train_y[:48], label='real')
plt.plot(fit3[10:58], label='ARIMA')'''
plt.plot(y, label='DNN')
plt.plot(train_y, label='real')
plt.legend()
plt.show()
'''
for i in range(len(train_x)):
	print(np.array(train_x[i]).shape)
	print(model.predict( np.array(train_x[i]) ) )'''