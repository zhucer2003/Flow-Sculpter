
import numpy as np
import cv2
import matplotlib.pyplot as plt
import matplotlib.cm as cmx
from mpl_toolkits.mplot3d import Axes3D

import math

def binomial(top, bottom):
  coef = (math.factorial(top))/(math.factorial(bottom)*math.factorial(top-bottom))
  return coef

def x_le(nue, slope):
  return nue * slope

def c_coef(nue, length, c_x):
  slope = (length - c_x)
  c = nue * slope + c_x
  return c

def voxel_plot(voxel):
  X = []
  Y = []
  Z = []
  for i in xrange(voxel.shape[0]-2):
    for j in xrange(voxel.shape[1]-2):
      for k in xrange(voxel.shape[2]-2):
        if voxel[i+1,j+1,k+1] > 0:
          if not(voxel[i,j+1,k+1] > 0 and voxel[i+1,j,k+1] > 0 and voxel[i+1,j+1,k] > 0 and voxel[i+2,j+1,k+1] > 0 and voxel[i+1,j+2,k+1] > 0 and voxel[i+1,j+1,k+2] > 0):
            X.append(i)
            Y.append(j)
            Z.append(k)
  X = np.array(X)
  Y = np.array(Y)
  Z = np.array(Z)
  #X_q, Y_q, Z_q = np.meshgrid(np.arange(0, voxel.shape[0], 1), np.arange(0, voxel.shape[0], 1), np.arange(nz/2, nz/2+4, 1))
  fig = plt.figure()
  ax = fig.add_subplot(111, projection='3d')
  ax.scatter(X, Y, Z)
  ax.set_xlim3d((0,128))
  ax.set_ylim3d((0,128))
  ax.set_zlim3d((0,128))
  plt.show()
 
 
def rotateImage(image, angle):
  center=tuple(np.array(image.shape[0:2])/2)
  angle = np.degrees(angle)
  rot_mat = cv2.getRotationMatrix2D(center,angle,1.0)
  return cv2.warpAffine(image, rot_mat, image.shape[0:2],flags=cv2.INTER_NEAREST)

def get_params_range(nr_params, dims):
  if dims == 2:
    params_range_lower = np.array([-1.0, 0.0, 0.0] + (nr_params-4)*[0.0] + [-0.05] )
    params_range_upper = np.array([ 1.0, 1.0, 2.0] + (nr_params-4)*[0.3] + [ 0.05] )
  elif dims == 3:
    params_range_lower = np.array([ 0.0,  0.0, 0.0, 0.0, 0.0, 0.0] 
                                + (nr_params-7)*[0.0] + [ 0.0] )
    params_range_upper = np.array([ 0.0,  0.0, 1.0, 2.0, 0.5, 0.5]
                                + (nr_params-7)*[0.3] + [ 0.0] )
  return params_range_lower, params_range_upper
 
def get_random_params(nr_params, dims):
  params = np.random.rand((nr_params))
  params_range_lower, params_range_upper = get_params_range(nr_params, dims)
  params_range_upper = params_range_upper - params_range_lower
  params = (params * params_range_upper) + params_range_lower
  return params

def wing_boundary_2d(angle, N_1, N_2, A_1, A_2, d_t, shape, boundary=None):

  # make lines for upper and lower wing profile
  if boundary is None:
    boundary = np.zeros(shape)
  c = 1.0 
  x_1 = np.arange(0.0, 1.00, 1.0/(shape[0]))
  x_2 = np.arange(0.0, 1.00, 1.0/(shape[0]))
  phi_1 = x_1/c
  phi_2 = x_2/c
  y_1 = np.power(phi_1, N_1)*np.power(1.0-phi_1, N_2)
  y_2 = np.power(phi_2, N_1)*np.power(1.0-phi_2, N_2)
  y_1_store = 0.0
  y_2_store = 0.0
  for i in xrange(len(A_1)):
    y_1_store += A_1[i]*binomial(len(A_1), i)*(phi_1**i)*((1.0-phi_1)**(len(A_1)-i))
    y_2_store += A_2[i]*binomial(len(A_2), i)*(phi_2**i)*((1.0-phi_2)**(len(A_2)-i))
  y_1 = y_1*y_1_store + phi_1 * d_t
  y_2 = y_2*y_2_store - phi_2 * d_t

  y_2 = - y_2

  for i in xrange(len(x_1)):
    y_upper = int(round(np.max(y_1[i]) * shape[1] + shape[1]/2)) + 1
    y_lower = int(round(np.min(y_2[i]) * shape[1] + shape[1]/2)) + 1
    x_pos = int(round(x_1[i] * shape[0]))
    if x_pos >= shape[0]:
      continue
    boundary[y_lower:y_upper, x_pos] = 1.0

  boundary = rotateImage(boundary, angle)
  boundary = boundary.reshape(shape + [1])

  return boundary

def wing_boundary_3d(angle_1, angle_2, N_1, N_2, sweep_slope, end_length, A_1, A_2, B, d_t, shape, boundary=None):

  # make lines for upper and lower wing profile
  if boundary is None:
    boundary = np.zeros(shape)

  c_x = 0.5 

  x = np.arange(0.0, 1.0, 1.0/(shape[0]))
  y = np.arange(0.0, 1.0, 2.0/(shape[1]))
  x, y = np.meshgrid(x, y)

  nue = y
  slope = c_coef(nue, end_length, c_x)
  phi = (x - x_le(nue, sweep_slope))/slope
  phi = np.maximum(phi, 0.0)
  phi_1 = phi
  phi_2 = phi

  z_1 = np.power(np.maximum(phi_1,0.0), N_1)*np.power(np.maximum(1.0-phi_1,0.0), N_2)
  z_2 = np.power(np.maximum(phi_2,0.0), N_1)*np.power(np.maximum(1.0-phi_2,0.0), N_2)

  z_1_store = 0.0
  z_2_store = 0.0
  for i in xrange(len(A_1)):
    for j in xrange(len(B)):
      z_1_store += (B[j]*A_1[i]
                   *binomial(len(A_1), i)*binomial(len(B), j)
                   *(phi_1**i)*((1.0-phi_1)**(len(A_1)-i))
                   *(nue**j)*((1.0-nue)**(len(B)-j)))
      z_2_store += (B[j]*A_2[i]*binomial(len(A_2), i)*binomial(len(B), j)
                   *(phi_1**i)*((1.0-phi_1)**(len(A_2)-i))
                   *(nue**j)*((1.0-nue)**(len(B)-j)))
  z_1 = z_1*z_1_store + phi_1 * d_t
  z_2 = z_2*z_2_store - phi_2 * d_t
  z_2 = -z_2

  for i in xrange(shape[0]):
    for j in xrange(shape[1]/2):
      z_upper = int(round(np.max(10.0*z_1[j,i]) * shape[2] + shape[2]/2))
      z_lower = int(round(np.min(10.0*z_2[j,i]) * shape[2] + shape[2]/2))
      boundary[i, j+shape[1]/2-1, z_lower:z_upper] = 1.0
      boundary[i, -j+shape[1]/2-1, z_lower:z_upper] = 1.0

  """
  fig = plt.figure()
  ax = fig.gca(projection='3d')
  ax.plot_surface(x,y,z_1)
  ax.plot_surface(x,y,z_2)

  #plt.imshow(z_1)
  plt.show()
  plt.imshow(boundary[:,:,shape[1]/2])
  plt.show()
  voxel_plot(boundary)
  """

  #boundary = rotateImage(boundary, angle)
  boundary = boundary.reshape(shape + [1])

  return boundary

def wing_boundary_batch(nr_params, batch_size, shape, dims):

  boundary_batch = []
  input_batch = []
  for i in xrange(batch_size): 
    params = get_random_params(nr_params, dims)
    if dims == 2:
      boundary_batch.append(wing_boundary_2d(params[0], params[1], params[2],
                                             params[3:(nr_params-4)/2],
                                             params[(nr_params-4)/2:-1],
                                             params[-1], shape))
    elif dims == 3:
      boundary_batch.append(wing_boundary_3d(params[0], params[1], params[2],
                                             params[3], params[4], params[5],
                                             params[6:(nr_params-7)/3+6],
                                             params[(nr_params-7)/3+6:2*(nr_params-7)/3+6],
                                             params[2*(nr_params-7)/3+6:-1],
                                             params[-1], shape))
    input_batch.append(params)
  boundary_batch = np.stack(boundary_batch, axis=0)
  input_batch = np.stack(input_batch, axis=0)
  return input_batch, boundary_batch

"""
_, boundary_batch = wing_boundary_batch(12, 32, [128,128,128], 3)
for i in xrange(32):
  plt.imshow(boundary_batch[i,:,:,64,0])
  #plt.imshow(boundary_batch[i,:,:,0])
  plt.show()
"""