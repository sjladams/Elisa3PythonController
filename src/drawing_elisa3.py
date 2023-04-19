import numpy as np
import matplotlib.pyplot as plt
import os.path
from os import path

filename = "data_run2.txt"
data = np.loadtxt(filename, comments="#", delimiter=",")

N = 3

id = data[:, 0]

t = np.zeros([N,100000])
theta = np.zeros([N,100000])
theta_filtered = np.zeros([N,100000])
xpos_filtered = np.zeros([N,100000])
xpos = np.zeros([N,100000])
ypos = np.zeros([N,100000])
ypos_filtered = np.zeros([N,100000])
turn = np.zeros([N,100000])
length = np.zeros(N, dtype=int)

for i in range(N):
    length[i] = int(np.where(id==i)[0].size)
    t[i, :length[i]] = data[np.where(id == i)[0], 1]
    theta[i, :length[i]] = data[np.where(id == i)[0], 2]
    theta_filtered[i, :length[i]] = data[np.where(id == i), 3]
    xpos[i, :length[i]] = data[np.where(id == i), 5]
    xpos_filtered[i, :length[i]] = data[np.where(id == i), 4]
    ypos[i, :length[i]] = data[np.where(id == i), 7]
    ypos_filtered[i, :length[i]] = data[np.where(id == i), 6]
    turn[i, :length[i]] = data[np.where(id == i), 8]


# t = data[:,1]
# theta = data[:,2]
# theta_filter = data[:,3]
# xpos_filtered = data[:,4]
# xpos = data[:,5]
# ypos_filtered = data[:,6]
# ypos = data[:,7]


plt.figure()
for i in range(N):
    plt.plot(t[i,:length[i]]-t[i,0], theta[i, :length[i]], '.')
    plt.plot(t[i, :length[i]] - t[i, 0], theta[i, :length[i]], 'k', alpha=0.2)
#plt.legend(["0","1","2"])
plt.title("theta")

plt.figure()
for i in range(N):
    plt.plot(t[i,:length[i]]-t[i,0], theta_filtered[i, :length[i]], '.')
    plt.plot(t[i, :length[i]] - t[i, 0], theta_filtered[i, :length[i]], 'k', alpha=0.2)
#plt.legend(["0","1","2"])
plt.title("theta (filtered)")


# plt.figure()
# plt.plot((t-t[0])/1000, theta)
# plt.plot((t-t[0])/1000, theta_filter, 'c')
#plt.axhline(10, color='r')

plt.figure()
for i in range(N):
    plt.plot(xpos_filtered[i,:length[i]], ypos_filtered[i,:length[i]], '.')
    plt.plot(xpos_filtered[i, :length[i]], ypos_filtered[i, :length[i]], 'k', alpha=0.2)
#plt.legend(["0","1","2"])
plt.ylim([0,4000])
plt.xlim([0,4000])
plt.title("xpos and ypos (filtered)")



# plt.figure()
# for i in range(N):
#     plt.plot(xpos[i,:length[i]], ypos[i,:length[i]], '.')
#     plt.plot(xpos[i, :length[i]], ypos[i, :length[i]], 'k', alpha=0.2)
#     plt.ylim([0,4000])
#     plt.xlim([0,4000])
# #plt.legend(["0","1","2"])
# plt.title("xpos and ypos")


plt.figure()
i = 2
plt.plot(t[i,:length[i]]-t[i,0], ypos_filtered[i,:length[i]], '.')
plt.plot(t[i,:length[i]]-t[i,0], ypos_filtered[i, :length[i]], 'k', alpha=0.2)
#plt.legend(["0","1","2"])
plt.title("ypos (filtered)")


plt.figure()
i = 2
plt.plot(t[i,:length[i]]-t[i,0], xpos_filtered[i,:length[i]], '.')
plt.plot(t[i,:length[i]]-t[i,0], xpos_filtered[i, :length[i]], 'k', alpha=0.2)
#plt.legend(["0","1","2"])
plt.title("xpos (filtered)")


plt.figure()
i = 2
plt.plot(t[i,:length[i]]-t[i,0], turn[i,:length[i]], '.')
plt.plot(t[i,:length[i]]-t[i,0], turn[i, :length[i]], 'k', alpha=0.2)
#plt.legend(["0","1","2"])
plt.title("Turning")

plt.show()
