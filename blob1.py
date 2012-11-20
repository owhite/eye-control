#!/usr/bin/env python

# See also: http://sundararajana.blogspot.com/2007/05/motion-detection-using-opencv.html

import cv
import time
import serial

from scipy import *
from scipy.cluster import vq
import numpy
import sys, os, random, hashlib

from math import *

top = 0
bottom = 1
left = 0
right = 1

def merge_collided_bboxes( bbox_list ):
	for this_bbox in bbox_list:
		# Collision detect every other bbox:
		for other_bbox in bbox_list:
			if this_bbox is other_bbox: continue  # Skip self
			
			# Assume a collision to start out with:
			has_collision = True
			if (this_bbox[bottom][0]*1.1 < other_bbox[top][0]*0.9): has_collision = False
			if (this_bbox[top][0]*.9 > other_bbox[bottom][0]*1.1): has_collision = False
			
			if (this_bbox[right][1]*1.1 < other_bbox[left][1]*0.9): has_collision = False
			if (this_bbox[left][1]*0.9 > other_bbox[right][1]*1.1): has_collision = False
			
			if has_collision:
				# merge these two bboxes into one, then start over:
				top_left_x = min( this_bbox[left][0], other_bbox[left][0] )
				top_left_y = min( this_bbox[left][1], other_bbox[left][1] )
				bottom_right_x = max( this_bbox[right][0], other_bbox[right][0] )
				bottom_right_y = max( this_bbox[right][1], other_bbox[right][1] )
				
				new_bbox = ( (top_left_x, top_left_y), (bottom_right_x, bottom_right_y) )
				
				bbox_list.remove( this_bbox )
				bbox_list.remove( other_bbox )
				bbox_list.append( new_bbox )
				
				# Start over with the new list:
				return merge_collided_bboxes( bbox_list )
	
	# When there are no collions between boxes, return that list:
	return bbox_list


class Target:
	def __init__(self):
		self.ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
		self.joymap = [1,2,3,4] # link between joystick and the servo to move
		self.joyreverse = [0,0,0,0,0]

		fps=6
		is_color = True

		self.capture = cv.CaptureFromCAM(0)
		cv.SetCaptureProperty( self.capture, cv.CV_CAP_PROP_FRAME_WIDTH, 320 );
		cv.SetCaptureProperty( self.capture, cv.CV_CAP_PROP_FRAME_HEIGHT, 240 );
		frame = cv.QueryFrame(self.capture)
		frame_size = cv.GetSize(frame)
			
		self.writer = None
		frame = cv.QueryFrame(self.capture)
		cv.NamedWindow("Target", 1)

	def ServoMove(self, servo, angle):
		servo = self.joymap[servo]
		if self.joyreverse[servo]:
			angle = 180 - angle
		if (0 <= angle <= 180):
			self.ser.write(chr(255))
			self.ser.write(chr(servo))
			self.ser.write(chr(angle))
		else:
			print "Servo angle must be an integer between 0 and 180.\n"


	def run(self):
		frame = cv.QueryFrame( self.capture )
		frame_size = cv.GetSize( frame )
		
		# Capture the first frame from webcam for image properties
		display_image = cv.QueryFrame( self.capture )
		
		# Greyscale image, thresholded to create the motion mask:
		grey_image = cv.CreateImage( cv.GetSize(frame), cv.IPL_DEPTH_8U, 1 )
		
		# The RunningAvg() function requires a 32-bit or 64-bit image...
		running_average_image = cv.CreateImage( cv.GetSize(frame), cv.IPL_DEPTH_32F, 3 )
		# ...but the AbsDiff() function requires matching image depths:
		running_average_in_display_color_depth = cv.CloneImage( display_image )
		
		# RAM used by FindContours():
		mem_storage = cv.CreateMemStorage(0)
		
		# The difference between the running average and the current frame:
		difference = cv.CloneImage( display_image )
		
		target_count = 1
		last_target_count = 1
		last_target_change_t = 0.0
		k_or_guess = 1
		codebook=[]
		frame_count=0
		last_frame_entity_list = []
		
		t0 = time.time()
		
		# For toggling display:
		image_list = [ "display", "difference", "threshold", "camera"]
		image_index = 0   # Index into image_list
	
		# Prep for text drawing:
		text_font = cv.InitFont(cv.CV_FONT_HERSHEY_COMPLEX, .5, .5, 0.0, 1, cv.CV_AA )
		text_coord = ( 5, 15 )
		text_color = cv.CV_RGB(255,255,255)

		haar_cascade = cv.Load( '/usr/local/share/OpenCV/haarcascades/haarcascade_frontalface_alt.xml' )

		max_targets = 3
		
		while True:
			
			camera_image = cv.QueryFrame( self.capture )
			
			frame_count += 1
			frame_t0 = time.time()
			
			# Create an image with interactive feedback:
			display_image = cv.CloneImage( camera_image )
			
			# Create a working "color image" to modify / blur
			color_image = cv.CloneImage( display_image )

			# Smooth to get rid of false positives
			cv.Smooth( color_image, color_image, cv.CV_GAUSSIAN, 19, 0 )
			
			# Use the Running Average as the static background			
			# a = 0.020 leaves artifacts lingering way too long.
			# a = 0.320 works well at 320x240, 15fps.  (1/a is roughly num frames.)
			cv.RunningAvg( color_image, running_average_image, 0.420, None )
			
			# Convert the scale of the moving average.
			cv.ConvertScale( running_average_image, running_average_in_display_color_depth, 1.0, 0.0 )
			
			# Subtract the current frame from the moving average.
			cv.AbsDiff( color_image, running_average_in_display_color_depth, difference )
			
			# Convert the image to greyscale.
			cv.CvtColor( difference, grey_image, cv.CV_RGB2GRAY )

			# Threshold the image to a black and white motion mask:
			cv.Threshold( grey_image, grey_image, 2, 255, cv.CV_THRESH_BINARY )
			# Smooth and threshold again to eliminate "sparkles"
			cv.Smooth( grey_image, grey_image, cv.CV_GAUSSIAN, 19, 0 )
			cv.Threshold( grey_image, grey_image, 240, 255, cv.CV_THRESH_BINARY )
			cv.Dilate(grey_image, grey_image, None, 18)
			cv.Erode(grey_image, grey_image, None, 20)
			
			grey_image_as_array = numpy.asarray( cv.GetMat( grey_image ) )
			non_black_coords_array = numpy.where( grey_image_as_array > 3 )
			# Convert from numpy.where()'s two separate lists to one list of (x, y) tuples:
			non_black_coords_array = zip( non_black_coords_array[1], non_black_coords_array[0] )
			
			points = []   # Was using this to hold either pixel coords or polygon coords.
			bounding_box_list = []

			# Now calculate movements using the white pixels as "motion" data
			contour = cv.FindContours( grey_image, mem_storage, cv.CV_RETR_CCOMP, cv.CV_CHAIN_APPROX_SIMPLE )
			
			while contour:
				
				bounding_rect = cv.BoundingRect( list(contour) )
				point1 = ( bounding_rect[0], bounding_rect[1] )
				point2 = ( bounding_rect[0] + bounding_rect[2], bounding_rect[1] + bounding_rect[3] )
				
				bounding_box_list.append( ( point1, point2 ) )
				polygon_points = cv.ApproxPoly( list(contour), mem_storage, cv.CV_POLY_APPROX_DP )
				
				# To track polygon points only (instead of every pixel):
				#points += list(polygon_points)
				
				# Draw the contours:
				levels = 0
				cv.DrawContours(color_image, contour, cv.CV_RGB(255,0,0), cv.CV_RGB(0,255,0), levels, 3, 0, (0,0) )
				cv.FillPoly( grey_image, [ list(polygon_points), ], cv.CV_RGB(255,255,255), 0, 0 )
				cv.PolyLine( display_image, [ polygon_points, ], 0, cv.CV_RGB(255,255,255), 1, 0, 0 )
				#cv.Rectangle( display_image, point1, point2, cv.CV_RGB(120,120,120), 1)

				contour = contour.h_next()
			
			
			# Find the average size of the bbox (targets), then
			# remove any tiny bboxes (which are prolly just noise).
			# "Tiny" is defined as any box with 1/10th the area of the average box.
			# This reduces false positives on tiny "sparkles" noise.
			box_areas = []
			for box in bounding_box_list:
				box_width = box[right][0] - box[left][0]
				box_height = box[bottom][0] - box[top][0]
				box_areas.append( box_width * box_height )
				
				#cv.Rectangle( display_image, box[0], box[1], cv.CV_RGB(255,0,0), 1)
			
			average_box_area = 0.0
			if len(box_areas): average_box_area = float( sum(box_areas) ) / len(box_areas)
			
			trimmed_box_list = []
			for box in bounding_box_list:
				box_width = box[right][0] - box[left][0]
				box_height = box[bottom][0] - box[top][0]
				
				# Only keep the box if it's not a tiny noise box:
				if (box_width * box_height) > average_box_area*0.1: trimmed_box_list.append( box )
			
			# Draw the trimmed box list:
			#for box in trimmed_box_list:
			#	cv.Rectangle( display_image, box[0], box[1], cv.CV_RGB(0,255,0), 2 )
				
			bounding_box_list = merge_collided_bboxes( trimmed_box_list )

			# Draw the merged box list:
			for box in bounding_box_list:
				cv.Rectangle( display_image, box[0], box[1], cv.CV_RGB(0,255,0), 1 )
			
			# Here are our estimate points to track, based on merged & trimmed boxes:
			estimated_target_count = len( bounding_box_list )
			
			if frame_t0 - last_target_change_t < .650:  # 1 change per 0.35 secs
				estimated_target_count = last_target_count
			else:
				if last_target_count - estimated_target_count > 1: estimated_target_count = last_target_count - 1
				if estimated_target_count - last_target_count > 1: estimated_target_count = last_target_count + 1
				last_target_change_t = frame_t0
			
			# Clip to the user-supplied maximum:
			estimated_target_count = min( estimated_target_count, max_targets )
			points = non_black_coords_array
			center_points = []
			
			if len(points):
				
				k_or_guess = max( estimated_target_count, 1 )  # Need at least one target to look for.
				if len(codebook) == estimated_target_count: 
					k_or_guess = codebook
				
				#points = vq.whiten(array( points ))  # Don't do this!  Ruins everything.
				codebook, distortion = vq.kmeans( array( points ), k_or_guess )
				
				# Convert to tuples (and draw it to screen)
				for center_point in codebook:
					center_point = ( int(center_point[0]), int(center_point[1]) )
					center_points.append( center_point )
			trimmed_center_points = []
			removed_center_points = []
						
			for box in bounding_box_list:
				# Find the centers within this box:
				center_points_in_box = []
				
				for center_point in center_points:
					if	center_point[0] < box[right][0] and center_point[0] > box[left][0] and \
						center_point[1] < box[bottom][1] and center_point[1] > box[top][1] :
						
						# This point is within the box.
						center_points_in_box.append( center_point )
				
				# Now see if there are more than one.  If so, merge them.
				if len( center_points_in_box ) > 1:
					# Merge them:
					x_list = y_list = []
					for point in center_points_in_box:
						x_list.append(point[0])
						y_list.append(point[1])
					
					average_x = int( float(sum( x_list )) / len( x_list ) )
					average_y = int( float(sum( y_list )) / len( y_list ) )
					
					trimmed_center_points.append( (average_x, average_y) )
					
					# Record that they were removed:
					removed_center_points += center_points_in_box
					
				if len( center_points_in_box ) == 1:
					trimmed_center_points.append( center_points_in_box[0] ) # Just use it.
			
			# If there are any center_points not within a bbox, just use them.
			# (It's probably a cluster comprised of a bunch of small bboxes.)
			for center_point in center_points:
				if (not center_point in trimmed_center_points) and (not center_point in removed_center_points):
					trimmed_center_points.append( center_point )
			
			# Determine if there are any new (or lost) targets:
			actual_target_count = len( trimmed_center_points )
			last_target_count = actual_target_count
			
			# Now build the list of physical entities (objects)
			this_frame_entity_list = []
			
			# An entity is list: [ name, color, last_time_seen, last_known_coords ]
			
			for target in trimmed_center_points:
			
				# Is this a target near a prior entity (same physical entity)?
				entity_found = False
				entity_distance_dict = {}
				
				for entity in last_frame_entity_list:
					
					entity_coords= entity[3]
					delta_x = entity_coords[0] - target[0]
					delta_y = entity_coords[1] - target[1]
			
					distance = sqrt( pow(delta_x,2) + pow( delta_y,2) )
					entity_distance_dict[ distance ] = entity
				
				# Did we find any non-claimed entities (nearest to furthest):
				distance_list = entity_distance_dict.keys()
				distance_list.sort()
				
				for distance in distance_list:
					
					# Yes; see if we can claim the nearest one:
					nearest_possible_entity = entity_distance_dict[ distance ]
					
					if nearest_possible_entity in this_frame_entity_list:
						continue
					
					# Found the nearest entity to claim:
					entity_found = True
					nearest_possible_entity[2] = frame_t0  # Update last_time_seen
					nearest_possible_entity[3] = target  # Update the new location
					this_frame_entity_list.append( nearest_possible_entity )
					break
				
				if entity_found == False:
					# It's a new entity.
					color = ( random.randint(0,255), random.randint(0,255), random.randint(0,255) )
					name = hashlib.md5( str(frame_t0) + str(color) ).hexdigest()[:6]
					last_time_seen = frame_t0
					
					new_entity = [ name, color, last_time_seen, target ]
					this_frame_entity_list.append( new_entity )
			
			# Now "delete" any not-found entities which have expired:
			entity_ttl = 1.0  # 1 sec.
			
			ent_count = 0
			for entity in last_frame_entity_list:
				last_time_seen = entity[2]
				if frame_t0 - last_time_seen > entity_ttl:
					pass
				else:
					# Save it for next time... not expired yet:
					this_frame_entity_list.append( entity )
					ent_count += 1
			
			# For next frame:
			last_frame_entity_list = this_frame_entity_list
			
			# Draw the found entities to screen:
			count = 0
			if ent_count != 0:
				entity = this_frame_entity_list[0]
				center_point = entity[3]
				c = entity[1]  # RGB color tuple
				# print '%s %d %d %d' % (entity[0], count, center_point[0], center_point[1])
				cv.Circle(display_image, center_point, 20, cv.CV_RGB(c[0], c[1], c[2]), 1)
				cv.Circle(display_image, center_point, 15, cv.CV_RGB(c[0], c[1], c[2]), 1)
				cv.Circle(display_image, center_point, 10, cv.CV_RGB(c[0], c[1], c[2]), 2)
				cv.Circle(display_image, center_point,  5, cv.CV_RGB(c[0], c[1], c[2]), 3)
			
			text_font = cv.InitFont(cv.CV_FONT_HERSHEY_COMPLEX, .5, .5, 0.0, 1, cv.CV_AA )
			text_coord = ( 5, 15 )
			text_color = cv.CV_RGB(255,255,255)
			
			x = 50 + (center_point[0] * 80 / 320)
			y = 20 + (center_point[1] * 80 / 240)
			self.ServoMove(0, int(x))            
			self.ServoMove(1, int(y))            

			s = '%3.0d %3.0d' % (x, y)
			cv.PutText(display_image, str(s), text_coord, text_font, text_color )

			#print "min_size is: " + str(min_size)
			# Listen for ESC or ENTER key
			c = cv.WaitKey(7) % 0x100
			if c == 27 or c == 10:
				break
			
			# Toggle which image to show
			if chr(c) == 'd':
				image_index = ( image_index + 1 ) % len( image_list )
			
			image_name = image_list[ image_index ]
			
			# Display frame to user
			if image_name == "display":
				image = display_image
 				# cv.PutText( image, "AABBs and contours", text_coord, text_font, text_color )
			elif image_name == "camera":
				image = camera_image
				cv.PutText( image, "No overlay", text_coord, text_font, text_color )
			elif image_name == "difference":
				image = difference
				cv.PutText( image, "Difference Image", text_coord, text_font, text_color )
			elif image_name == "threshold":
				# Convert the image to color.
				cv.CvtColor( grey_image, display_image, cv.CV_GRAY2RGB )
				image = display_image  # Re-use display image here
				cv.PutText( image, "Motion Mask", text_coord, text_font, text_color )
			
			cv.ShowImage( "Target", image )
			
			if self.writer: 
				cv.WriteFrame( self.writer, image );
			
			frame_t1 = time.time()
			
		t1 = time.time()
		time_delta = t1 - t0
		processed_fps = float( frame_count ) / time_delta
		print "Got %d frames. %.1f s. %f fps." % ( frame_count, time_delta, processed_fps )
if __name__=="__main__":
	t = Target()
	t.run()

