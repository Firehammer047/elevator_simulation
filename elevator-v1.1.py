#
#	v1.0
#	elevator_simulation is a cost analysis program for different
#	elevator logic modes.
#	Mode 1: Elevators can be called to the same floor simultaneously
#	Mode 2: Only 1 elevator will answer a call to a floor
#
#	This is the streamlined version and most comments were omitted.
#
#	Copyright (c) 2020 GB Tony Cabrera
#

import random
import numpy as np

####################
#		INIT
####################
TOP_FLOOR = 4
TIME_STEP = 0.25
A1 = 10
A2 = 4
A3 = 4
A4 = 5
c1 = 90
c2 = 390
c3 = 330
c4 = 630
s1 = 10
s2 = 30
s3 = 30
s4 = 20
P_NOON = 0.75
P_FIVE = 0.9

class Elevator:

	def __init__(self):			# Initialize the elevator variables
		global TOP_FLOOR
		self.total_floors = 0		# Total number of floors traversed
		self.current_floor = 0		# Where we are now
		self.direction = 0			# Direction elevator is going (1 up, -1 down)
		self.cargo = 0				# People inside box
		self.button_panel = []		# Floor panel inside elevator
		self.call_button_up = []	# Call button on particular floor (0-TOP_FLOOR) 1=ON, 0=OFF
		self.call_button_dn = []	# Call button on particular floor (0-TOP_FLOOR) 1=ON, 0=OFF
		self.dest_inside = []		# Number of people going to floor "i"
		for i in range(TOP_FLOOR + 1):	# Clear all buttons and destinations
			self.button_panel.append(0)
			self.call_button_up.append(0)
			self.call_button_dn.append(0)
			self.dest_inside.append(0)
	
	def unload_cargo(self):		# Remove passengers from box and turn button OFF
		if self.dest_inside[self.current_floor] > 0: print('\tUnloading cargo: %d' % (self.dest_inside[self.current_floor]))
		self.cargo -= self.dest_inside[self.current_floor]
#		print('\tCargo : %d' % (self.cargo))
		self.dest_inside[self.current_floor] = 0
		self.button_panel[self.current_floor] = 0
	
	def load_cargo(self):		# Add passengers to box and press buttons
		global TOP_FLOOR
		global queue_up
		global dest_outside
		if self.direction > 0:	# If we're going UP then add people going up and press panel buttons
			if queue_up[self.current_floor] > 0: print('\tLoading cargo UP: %d' % (queue_up[self.current_floor]))
			self.cargo += queue_up[self.current_floor]
#			print('\tCargo : %d' % (self.cargo))
			queue_up[self.current_floor] = 0	# No one left outside the doors
			for i in range(self.current_floor + 1, TOP_FLOOR + 1):
				self.dest_inside[i] += dest_outside[self.current_floor][i]
#				print('\tdest_outside[%d][%d] = %d' % (self.current_floor,i,dest_outside[self.current_floor][i]))
#				print('\tdest_inside[%d] = %d' % (i,self.dest_inside[i]))
				dest_outside[self.current_floor][i] = 0
				if self.dest_inside[i] > 0:
					self.button_panel[i] = 1
			self.call_button_up[self.current_floor] = 0	# Turn call button OFF
		if self.direction < 0:	# If we're going down, do the same (but with people going DOWN)
			if queue_dn[self.current_floor] > 0: print('\tLoading cargo DN: %d' % (queue_dn[self.current_floor]))
			self.cargo += queue_dn[self.current_floor]
#			print('\tCargo : %d' % (self.cargo))
			queue_dn[self.current_floor] = 0	# No one left outside the doors
			for i in range(self.current_floor):
				self.dest_inside[i] += dest_outside[self.current_floor][i]
#				print('\tdest_outside[%d][%d] = %d' % (self.current_floor,i,dest_outside[self.current_floor][i]))
#				print('\tdest_inside[%d] = %d' % (i,self.dest_inside[i]))
				dest_outside[self.current_floor][i] = 0
				if self.dest_inside[i] > 0:
					self.button_panel[i] = 1
			self.call_button_dn[self.current_floor] = 0	# Turn call button OFF
	
	def goto_next_floor(self):
		self.current_floor += self.direction	# Add or subtract a floor
		if self.direction != 0:
			self.total_floors += 1	# Add a floor to the running total
	
	def stop_at_this_floor(self):
		global TOP_FLOOR
		if self.button_panel[self.current_floor]:	# We have a request to stop at this floor
			return 1
		if self.direction > 0:
			if self.call_button_up[self.current_floor]:	# There's a call outside and we're going in the same direction
				return 1
			if self.current_floor == TOP_FLOOR:	# We reached the top. Yay!
				return 1
		if self.direction < 0:
			if self.call_button_dn[self.current_floor]: # There's a call and we're going DOWN
				return 1
			if self.current_floor == 0:	# We are on the ground floor! Yay!
				return 1
		return 0
	
	def set_direction(self):	# Figure out which direction we need to go
		global TOP_FLOOR
		if self.direction > 0:	# We're already going UP
			if self.current_floor != 0 and self.current_floor != TOP_FLOOR: # Intermediate floors
				if not self.any_buttons_above() and not self.any_calls_above():	
					if self.call_button_dn[self.current_floor] or self.any_calls_below():
						self.direction = -1
				if not self.any_buttons_above() and not self.any_calls():	# Nothing to do
					self.direction = 0
			if self.current_floor == TOP_FLOOR:
				if self.any_calls():
					self.direction = -1
				else:
					self.direction = 0	# Nothing to do, no calls
		elif self.direction < 0: # We're already going DOWN
			if self.current_floor != 0 and self.current_floor != TOP_FLOOR:	# Intermediate floors
				if not self.any_buttons_below() and not self.any_calls_below():
					if self.call_button_up[self.current_floor] or self.any_calls_above():
						self.direction = 1
				if not self.any_buttons_below() and not self.any_calls():	# Nothing to do
					self.direction = 0
			if self.current_floor == 0:
				if self.any_calls():
					self.direction = 1
				else:
					self.direction = 0	# Nothing to do, no calls
		else:	# We're stopped
			self.first_call_floor = self.get_first_call_floor()	# Figure out who pressed the first button
			if self.current_floor != self.first_call_floor:
				self.direction = np.sign(self.first_call_floor - self.current_floor)
	
	def any_calls(self,f1=0,f2=4):
		for i in range(f1,f2+1):
			if self.call_button_up[i] or self.call_button_dn[i]:
				return 1
		return 0
	
	def any_calls_above(self):
		global TOP_FLOOR
		if self.current_floor != TOP_FLOOR:
			return self.any_calls(self.current_floor + 1, TOP_FLOOR)
		return 0

	def any_calls_below(self):
		if self.current_floor != 0:
			return self.any_calls(0, self.current_floor - 1)
		return 0
	
	def any_buttons(self,f1=0,f2=4):
		for i in range(f1,f2+1):
			if self.button_panel[i]:
				return 1
		return 0

	def any_buttons_above(self):
		global TOP_FLOOR
		if self.current_floor != TOP_FLOOR:
			return self.any_buttons(self.current_floor + 1, TOP_FLOOR)
		return 0

	def any_buttons_below(self):
		if self.current_floor != 0:
			return self.any_buttons(0, self.current_floor - 1)
		return 0

	def wait(self):
		pass
	
	def set_first_call_direction(self):	# Decide which way we are moving first
		if self.call_button_up[self.current_floor] and not self.call_button_dn[self.current_floor]:
			self.direction = 1
		if not self.call_button_up[self.current_floor] and self.call_button_dn[self.current_floor]:
			self.direction = -1
		if self.call_button_up[self.current_floor] and self.call_button_dn[self.current_floor]:
			r = random.random()	# Both UP and DOWN buttons were pressed so we toss a coin
			if r > 0.5:
				direction = 1
			else:
				direction = -1
	
	def get_first_call_floor(self):	# Randomly choose a floor from all calls
		global TOP_FLOOR
		floors_with_calls = []
		for i in range(0, TOP_FLOOR + 1):
			if self.call_button_up[i] or self.call_button_dn[i]:
				floors_with_calls.append(i)
		r = random.randint(0,len(floors_with_calls)-1)
		return floors_with_calls[r]

def prob_distro_arrivals(i, t):
#
# Arraivals follow a double gaussian distro with centers at c1 & c2 for the ground floor
# and c3 & c4 for the rest. 
# This is because everyone arrives on the ground floor at 8am and then those who come 
# back from lunch arrive on the ground floor around 1pm
#
# All other floors see arrivals leaving for lunch around 12pm and leaving work around 5pm
#
# rate is a rate in people/min. To get the number of people in a given time step we multiply by
# the time step. This would always be an average, so we randomize the arrivals (but on average we get
# the same as the gaussian distro.)
#
	global TIME_STEP

	if i == 0:
		rate = A1*np.exp(-0.5*((t-c1)/s1)**2) + A2*np.exp(-0.5*((t-c2)/s2)**2)
	else:
		rate = A3*np.exp(-0.5*((t-c3)/s3)**2) + A4*np.exp(-0.5*((t-c4)/s4)**2)
	if rate * TIME_STEP >= 1:
		r = random.randint(0,round(2*rate*TIME_STEP))
		return r
	else:
		r = random.random()
		if r < rate * TIME_STEP:
			return 1
		else:
			return 0

def prob_distro_dest_floor(i,t):
#
# This is the probability that an arriving passenger will choose a specific floor depending on
# 1) What floor they are on
# and
# 2) The time of day
#
	global TOP_FLOOR
	global P_NOON
	global P_FIVE

	if i == 0:
		return random.randint(1,TOP_FLOOR)
	else:
		if t < 300:
			r = random.randint(0,TOP_FLOOR)
			while r == i:
				r = random.randint(0,TOP_FLOOR)
			return r
		if t >= 300 and t < 360:
			p = random.random()
			if p < P_NOON:
				return 0
			else:
				r = random.randint(1,TOP_FLOOR)
				while r == i:
					r = random.randint(1,TOP_FLOOR)
				return r
		if t >= 360 and t < 600:
			r = random.randint(0,TOP_FLOOR)
			while r == i:
				r = random.randint(0,TOP_FLOOR)
			return r
		if t >= 600:
			p = random.random()
			if p < P_FIVE:
				return 0
			else:
				r = random.randint(1,TOP_FLOOR)
				while r == i:
					r = random.randint(1,TOP_FLOOR)
				return r




# Create elevator
elev = Elevator()

# Init queues
queue_up=[]
queue_dn=[]
for i in range(TOP_FLOOR + 1):
	queue_up.append(0)	
	queue_dn.append(0)	

dest_outside = [[0 for i in range(TOP_FLOOR + 1)] for j in range(TOP_FLOOR + 1)]

######### Start day ##########
time = 0

while time <= 720:
	h = (time + 390)//60
	m = (time + 390)%60

	print ('Time: %02d:%02d' % (h,m))
	print('Elevator on floor : %d' % (elev.current_floor))
#	print('\tDirection : %d' % (elev.direction))
	print('Cargo : %d' % (elev.cargo))
	
	arrivals = []
	for i in range(TOP_FLOOR + 1):
		arrivals.append(prob_distro_arrivals(i,time))
		for j in range(arrivals[i]):
			dest_floor = prob_distro_dest_floor(i, time)
			dest_outside[i][dest_floor] += 1
			if dest_floor > i:
				queue_up[i] += 1
				elev.call_button_up[i] = 1
			if dest_floor < i:
				queue_dn[i] += 1
				elev.call_button_dn[i] = 1
#		if queue_up[i] > 0:
#			print ('\tQueue up on floor %d : %d' % (i, queue_up[i]))
#		if queue_dn[i] > 0:
#			print ('\tQueue dn on floor %d : %d' % (i, queue_dn[i]))

	if elev.direction == 0:
		if elev.any_calls():
			elev.set_direction()
			if elev.direction == 0:
				elev.set_first_call_direction()
				elev.load_cargo()
			elev.goto_next_floor()
		else:
			elev.wait()
	else:
		if elev.stop_at_this_floor():
			elev.set_direction()
			elev.unload_cargo()
			elev.load_cargo()
		elev.goto_next_floor()
	
	time += TIME_STEP

print ('Total floors: %d' % elev.total_floors)

# End while loop
