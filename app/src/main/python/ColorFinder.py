import cv2
import numpy as np


# def Mask(img,background,Mask_UpperRange,Mask_LowerRange):
def Mask(img,Mask_LowerRange,Mask_UpperRange):

	''' Generating the final mask to detect red color '''    
	''' In the previous step, we generated a mask to determine
	the region in the frame corresponding to the detected
	color. We refine this mask and then use it for segmenting
	out the that-colored objects from the frame '''
	
	hsv = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
	mask = cv2.inRange(hsv, Mask_LowerRange, Mask_UpperRange)

	mask1 = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3,3),np.uint8))
	mask1 = cv2.morphologyEx(mask, cv2.MORPH_DILATE, np.ones((3,3),np.uint8))


	''' creating an inverted mask to segment out the cloth from the frame '''
    
	mask2 = cv2.bitwise_not(mask1)

	''' Segmenting the cloth out of the frame using bitwise and with the inverted mask '''

	res1 = cv2.bitwise_and(img,img,mask=mask1)
    
	''' creating image showing static background frame pixels only for the masked region '''
	res2=0
	# res2 = cv2.bitwise_and(background, background, mask = mask1)

	''' Generating the final output '''

	# final_output = cv2.addWeighted(res1,1,res2,1,0)
	# return mask1,mask2
	return res1,res2



# def ColorFinder(im,background,Color,Hue=[0,10,170,180],Sat=[125,255],Val=[110,255]):
def ColorFinder(img,Color,Hue=[0,5,173,180],Sat=[75,255],Val=[158,200]):


	''' im can be Image File Name With Quotation Or Variable Wich Contains Image '''
	''' The Hue values are actually distributed over
	a circle (range between 0-360 degrees) but in
	OpenCV to fit into 8bit value the range is from
	0-180. The red color is represented by 0-30 as well as 150-180 values  '''
	''' We use the range 0-10 and 170-180 to avoid detection
	of skin as red. High range of 120-255 for saturation
	is used because our cloth should be of highly saturated
	red color
	The lower range of value is 70 so that we can detect red
	color in the wrinkles of the cloth as well ''' 

	e1 = cv2.getTickCount() 
	

	''' Finding White Color Hue Values in hsv for paper detection '''

	''' Range for White '''
	if (Color=='white') :
		lower_range = np.array([0,0,0], dtype=np.uint8)
		upper_range = np.array([0,0,255], dtype=np.uint8)
		mask1,mask2 = Mask(img, lower_range, upper_range)
		# cv2.imshow('contours',mask2)
		return mask1,img
		# cv2.imshow('contours',mask1)
	elif (Color=='red') :

		''' Finding Red Color Hue Values in hsv '''
		
		''' Range for lower red '''
		lower_red = np.array([Hue[0],Sat[0],Val[0]])
		upper_red = np.array([Hue[1],Sat[1],Val[1]])

		mask1,mask2 = Mask(img, lower_red, upper_red)
		# cv2.imshow('contours',mask1)


		''' Range for upper red '''
		lower_red = np.array([Hue[2],Sat[0],Val[0]])
		upper_red = np.array([Hue[3],Sat[1],Val[1]])
		Mask1,Mask2 = Mask(img, lower_red, upper_red)
		mask1 += Mask1
		mask2 += Mask2
		# print('123')
		# mask = red_mask1 + red_mask2
		return mask1,img
	else: 
		pass

	# if mask:
	# 	red_mask1 = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3,3),np.uint8))
	# 	red_mask1 = cv2.morphologyEx(mask, cv2.MORPH_DILATE, np.ones((3,3),np.uint8))
	# 	red_mask2 = cv2.bitwise_not(red_mask1)
	# 	res1 = cv2.bitwise_and(img,img,mask=red_mask2)
	# 	res2 = cv2.bitwise_and(background, background, mask = red_mask1)
	# 	final_output = cv2.addWeighted(res1,1,res2,1,0)
# first_frame = cv2.imread("OneKeyTest.jpg")
# mask1,img=ColorFinder(first_frame,'white')
# cv2.imshow('1',img)
# cv2.waitKey(0)
# cv2.destroyAllWindows()