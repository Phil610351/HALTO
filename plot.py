import matplotlib.pyplot as plt

y=list()
with open("train.dat") as f:
	a=f.read().split('\n')
	count=0
	hour=0
	for e in a:
		e=e.split()
		if int(e[0][:10])-1201639675>3600*hour:
		#if int(e[0][:10])-1189809385>3600*hour:
			y.append(round(count*1.5/100))
			count=0
			hour+=1
		else:
			count+=1

print(y)
plt.plot(y, "go-")
plt.show()