'''
Copyright (c) 2025 Hilton-Santana <https://my.github.com/Hilton-Santana>

Created Date: Saturday, January 18th 2025, 4:41:25 pm
Author: Hilton-Santana hiltonmarquess@gmail.com

Description: IMU class which is a wrapper for the accelerometer and
gyroscope defined in Mujoco
HISTORY:
Date      	By	Comments
----------	---	----------------------------------------------------------
'''

import numpy as np
import matplotlib.pyplot as plt

from scipy.spatial.transform import Rotation

class IMU:
  def __init__(self,
               mj_model,
               mj_data,
               accel_name,
               gyro_name,
               imu_site_name,
               accel_noise: float = 0.01,
               gyro_noise: float = 0.01,
               accel_bias_rate: float = 0.01,
               gyro_bias_rate: float = 0.01):
      '''
      Imu constructor

      mj_model: mujoco model
      mj_data: mujoco data
      accel_name: accelerometer name in the xml file
      gyro_name: gyroscope name in the xml file
      imu_site_name: imu site name in the xml file
      acc_noise: float with accelerometer's std assuming the same for all axes (m/s²)
      gyro_noise: float with gyroscope's std assuming the same for all axes (rad/s)
      acc_bias: float with accelerometer's bias assuming the same for all axes (m/s³)
      gyro_bias: float with gyroscope's bias assuming the same for all axes (rad/s²)
      '''
      self._mj_model = mj_model
      self._mj_data = mj_data

      self._accel_noise = accel_noise
      self._gyro_noise = gyro_noise
      self._accel_bias_drift = accel_bias_rate
      self._gyro_bias_drift = gyro_bias_rate

      self._accel_name = accel_name
      self._gyro_name = gyro_name

      self._accel_id = self._get_sensor_id(accel_name)
      self._gyro_id = self._get_sensor_id(gyro_name)
      self._imu_site_id = self._get_site_id(imu_site_name)

      # Store the bias of the IMU
      self._imu_gyro_bias = np.zeros(3)
      self._imu_accel_bias = np.zeros(3)

      # Build IMU frame w.r.t to the base frame
      # this is a geometric transformation from frame b 
      # to frame i
      self.b_X_i = self._build_imu_frame()

      # Turn off to inspect data
      self._show = False

#=============================================================================== 
  @property
  def get_accel(self, dt = 1.0) -> tuple:
    '''
    Get current linear acceleration measured by the IMU
    '''
    base_lin_acc_noise = np.random.normal(0, self._accel_noise, 3) 

    # Assuming dt*drift = bias (TODO: pass dt)
    self._imu_accel_bias += np.random.normal(0, self._accel_bias_drift, 3)

    accel_id = self._accel_id
    accel = self._mj_data.sensordata[accel_id:accel_id + 3] 
    # another option is with 
    #accel_2 = self._mj_data.sensor(self._accel_name).data
    # but I believe it is faster to use the sensordata

    # add noise and biases to the real value
    accel +=  dt * self._imu_accel_bias + base_lin_acc_noise

    return accel, base_lin_acc_noise, self._imu_accel_bias

#=============================================================================== 
  @property
  def get_gyro(self, dt = 1.0) -> np.array:
    '''
    Get current angular velocity measured by the IMU
    '''
    base_ang_vel_noise = np.random.normal(0, self._gyro_noise, 3) 
    self._imu_gyro_bias  = self._imu_gyro_bias + np.random.normal(0, self._gyro_bias_drift, 3)

    gyro_id = self._gyro_id
    gyro = self._mj_data.sensordata[gyro_id:gyro_id + 3]
    #gyro_2 = self._mj_data.sensor(self._gyro_name).data

    # add noise and biases to the real value
    gyro +=  dt * self._imu_accel_bias + base_ang_vel_noise

    return gyro, base_ang_vel_noise, self._imu_gyro_bias

#=============================================================================== 
  @property
  def get_imu_frame(self) -> np.array:
    '''
    Get IMU frame w.r.t to the base frame
    '''
    return self.b_X_i

#=============================================================================== 
  def prepare2show(self):
    '''
    Create canvas and legends for the IMU data
    '''
    self.time = []
    self.accel_x = []
    self.accel_bias_x = []
    self.gyro_x = []
    self.gyro_bias_x = []
    plt.ion()  # Turn on interactive mode
    fig, axs = plt.subplots(2, 1)
    
    # Plot for white noise
    accel_line_noise, = axs[0].plot([], [], label="Accel noise x")
    gyro_line_noise, = axs[0].plot([], [], label="Gyro noise x")
    axs[0].set_xlabel("Time (steps)")
    axs[0].set_ylabel("white noise")
    axs[0].legend()

    # Plot for bias noise
    accel_line_bias, = axs[1].plot([], [], label="Accel bias x")
    gyro_line_bias, = axs[1].plot([], [], label="Gyro bias x")
    axs[1].set_xlabel("Time (steps)")
    axs[1].set_ylabel("brownian noise")
    axs[1].legend()

    # Store relevant variables
    self.ax_white_noise = axs[0]
    self.ax_bias_noise = axs[1]
    self._show = True
    self.accel_line_noise_x = accel_line_noise
    self.gyro_line_noise_x = gyro_line_noise
    self.accel_line_bias_x = accel_line_bias
    self.gyro_line_bias_x = gyro_line_bias

#=============================================================================== 
  def show(self, time, accel_noise, gyro_noise, accel_bias, gyro_bias):
    '''
    Show the IMU data in the canvas
    '''
    if (not self._show):
      return

    self.time.append(time)
    self.accel_x.append(accel_noise[0])
    self.gyro_x.append(gyro_noise[0])
    self.accel_bias_x.append(accel_bias[0])
    self.gyro_bias_x.append(gyro_bias[0])

    # Update white noise
    self.accel_line_noise_x.set_xdata(self.time)
    self.accel_line_noise_x.set_ydata(self.accel_x)
    self.gyro_line_noise_x.set_xdata(self.time)
    self.gyro_line_noise_x.set_ydata(self.gyro_x)
    self.ax_white_noise.relim()
    self.ax_white_noise.autoscale_view()
    plt.draw()
    plt.pause(0.001)

    # Update bias noise
    self.accel_line_bias_x.set_xdata(self.time)
    self.accel_line_bias_x.set_ydata(self.accel_bias_x)
    self.gyro_line_bias_x.set_xdata(self.time)
    self.gyro_line_bias_x.set_ydata(self.gyro_bias_x)
    self.ax_bias_noise.relim()
    self.ax_bias_noise.autoscale_view()
    plt.draw()
    plt.pause(0.001)

#=============================================================================== 
  def _get_site_id(self, site_name) -> int:
    site_id = self._mj_model.site(name=site_name).id

    return site_id

#=============================================================================== 
  def _get_sensor_id(self, sensor_name) -> int:
    accel_id = self._mj_model.sensor(name=sensor_name).id
    # Find the starting index of the sensor in the sensor data
    start = 0
    for i in range(accel_id):
        start += self._mj_model.sensor(i).dim[0]

    return start

#=============================================================================== 
  def _build_imu_frame(self) -> np.array:
    '''
    Build IMU frame w.r.t to the base frame. This should be called only once
    '''
    # Build IMU frame w.r.t world frame w_T_i
    imu_pos = self._mj_data.site(self._imu_site_id).xpos
    imu_frame = self._mj_data.site(self._imu_site_id).xmat.reshape(3, 3)
    imu_frame = Rotation.from_matrix(imu_frame)

    X_imu = np.eye(4)
    X_imu[0:3, 0:3] = imu_frame.as_matrix()
    X_imu[0:3, 3] = imu_pos

    # Build Inverse of Body frame w.r.t world frame b_T_w
    com_pos = self._mj_data.qpos[0:3]  # world frame
    quat_wxyz = self._mj_data.qpos[3:7]  # world frame (wxyz) mujoco convention
    quat_xyzw = np.roll(quat_wxyz, -1)  # SciPy convention (xyzw)
    X_B_inv = np.eye(4)
    X_B_inv[0:3, 0:3] = Rotation.from_quat(quat_xyzw).as_matrix().T
    X_B_inv[0:3, 3] = -np.dot(X_B_inv[0:3, 0:3], com_pos)

    # b_T_w * w_T_i = b_T_i
    X = np.dot(X_B_inv, X_imu)

    return X