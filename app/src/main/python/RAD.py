import io
import cv2
import base64
import numpy as np
import sympy as sp
import ColorFinder as CF
from matplotlib import pyplot as plt
import PIL.Image as Image

def RAD(img):
	'img is Base64 string of Image'
	r1 = 90
	s1 = 1
	r2 = 140
	s2 = 255

	θ=-sp.pi*(25)/180

	def sin(x): return sp.N(sp.sin(x))

	def cos(x): return sp.N(sp.cos(x))

	def pixelVal(pix, r1, s1, r2, s2): 
	    if (0 <= pix and pix <= r1): 
	        return (s1 / r1)*pix 
	    elif (r1 < pix and pix <= r2): 
	        return ((s2 - s1)/(r2 - r1)) * (pix - r1) + s1 
	    else: 
	        return ((255 - s2)/(255 - r2)) * (pix - r2) + s2
	def LineRotate(Line,θ):
		Rotated_Line=np.int0(tuple([[Line[0,0]*cos(θ)-Line[0,1]*sin(θ),Line[0,1]*cos(θ)+Line[0,0]*sin(θ)],
								[Line[1,0]*cos(θ)-Line[1,1]*sin(θ),Line[1,1]*cos(θ)+Line[1,0]*sin(θ)]]))


		slope=(Rotated_Line[1,1]-Rotated_Line[0,1])/(Rotated_Line[1,0]-Rotated_Line[0,0])
		intercept=Rotated_Line[0,1]-slope*Rotated_Line[0,0]

		x1=Rotated_Line[0,0]
		y1=np.float64(slope*x1+intercept)
		x2=Rotated_Line[1,0]
		y2=np.float64(slope*x2+intercept)
		return x1,y1,x2,y2

	def LineRotate_Over_Point(pts,θ):
		x1,y1,x2,y2=pts
		
		L_pow2=(x2-x1)**2+(y2-y1)**2
		L=np.sqrt(L_pow2)

		x1_new=x1
		y1_new=y1
		x2_new=np.float64(x2 + L*sin(θ))
		y2_new=np.float64(y2 + L*(1-cos(θ)))
		# print(L)

		return x1_new,y1_new,x2_new,y2_new

	def GetAngle(a,b,c):
		
		ba = a - b
		bc = c - b

		cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
		angle = np.arccos(cosine_angle)
		return np.round(np.degrees(angle),3)

	def GammaBooster(img):
		
		B,G,R=cv2.split(img) 

		YCbCr = cv2.cvtColor(img,cv2.COLOR_BGR2YCrCb)
		Channels=cv2.split(YCbCr)
		Y=Channels[0]
		
		α=np.max(Y)+1 
		
		LogY=np.log(Y+1) / np.log(α)
		LogY_Reshaped=LogY.ravel()
		LogY_Upper=np.array(LogY_Reshaped[LogY_Reshaped>0.5]).astype('float32')
		LogY_Lower=np.array(LogY_Reshaped[LogY_Reshaped<=0.5]).astype('float32')
		
		σH=np.std(LogY_Upper)
		σL=np.std(LogY_Lower)
		
		MH=1-σH
		ML=σL+1/3
 
		γiL=np.arange(10,101)/100
 
		Sdark=np.zeros([len(γiL),len(LogY_Lower)])
		for i in range(len(γiL)):
			Sdark[i]=cv2.pow(LogY_Lower,γiL[i]).ravel() 

		γiH=np.arange(10,101)/10


		Sbright=np.zeros([len(γiH),len(LogY_Upper)])
		for i in range(len(γiH)):
			Sbright[i]=cv2.pow(LogY_Upper,γiH[i]).ravel()

		MedDark=np.median(Sdark,axis=1)
		MedBright=np.median(Sbright,axis=1)

		DiffDark=MedDark-ML
		DiffBright=MedBright-MH 

		γH=γiH[np.argmin(DiffBright)]	
		γL=γiL[np.argmin(DiffDark)]
		# print(γH,γL)

		Ld=(LogY**γH).astype('float32')
		Lb=(LogY**γL).astype('float32')

		blur1 = cv2.GaussianBlur(Ld, (0,0), sigmaX=0.5,sigmaY=1.5)
		blur2 = cv2.GaussianBlur(Lb, (0,0), sigmaX=0.5,sigmaY=1.5)


		LdNew=Ld+blur1
		LbNew=Lb+blur2

		w=np.exp(-Lb**2/0.5)
		Lout=w*LdNew+(1-w)*LbNew

		s=1-np.tanh(Lb)
		Iout_B=Iout_G=Iout_R=out = np.empty(Lout.shape)
		Iout_B=Lout*((np.divide(B,Y, out=out, where=Y!=0)/Y)**s)
		Iout_G=Lout*((np.divide(G,Y, out=out, where=Y!=0)/Y)**s)
		Iout_R=Lout*((np.divide(R,Y, out=out, where=Y!=0)/Y)**s)

		Output_Img=cv2.merge([Iout_B, Iout_G, Iout_R]).astype('float32')
		Output_Img=(Output_Img*(250/np.max(Output_Img))).astype('uint8')
		return Output_Img


	im_b64 = base64.b64decode(img)
	im_arr = np.array(list(im_b64),'uint8') 
	img = cv2.imdecode(im_arr, flags=cv2.IMREAD_COLOR)
 
	img2=cv2.pyrDown(cv2.pyrDown(img)) 

	size=img2.shape

	Output_Img=GammaBooster(img2)
	pixelVal_vec = np.vectorize(pixelVal) 
	Output_Img = pixelVal_vec(Output_Img, r1, s1, r2, s2) .astype('float32')

	image_8bit = np.uint8(Output_Img * 255)

	blur = cv2.GaussianBlur(image_8bit,(5,5),0)
	imgray = cv2.cvtColor(blur,cv2.COLOR_BGR2GRAY)
	ret,thresh = cv2.threshold(imgray,50,255,cv2.THRESH_BINARY)
	th3 = cv2.adaptiveThreshold(imgray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11,5)
	
	contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
	area=np.array([cv2.contourArea(contours[i1]) for i1 in range(len(contours))])
	Max=max(area)
	Index=np.argwhere(area==Max)[0][0]

 
	x,y,w,h = cv2.boundingRect(contours[Index])
	rectangle=np.float32([[x,y],[x+w,y],[x,y+h],[x+w,y+h]])


	pts = np.float32([[0,0],[w*2,0],[0,h*2],[w*2,h*2]])

	M = cv2.getPerspectiveTransform(rectangle,pts)
 
	dst = cv2.warpPerspective(Output_Img,M,(w*2,h*2)) 

	B,G,R=cv2.split(dst)

	ret2,thresh2 = cv2.threshold(G,50,255,cv2.THRESH_BINARY)
	image2_8bit = np.uint8(G)

	th3 = cv2.adaptiveThreshold(image2_8bit,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY_INV,11,5) 

	kernel = np.ones((20,20), np.uint8) 
	closing = cv2.morphologyEx(th3, cv2.MORPH_CLOSE, kernel)


	contours, hierarchy = cv2.findContours(closing,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
	area=np.array([cv2.contourArea(contours[i1]) for i1 in range(len(contours))])
	sorted=np.sort(area)[::-1]

	Max=max(area)
	Index=np.argwhere(area==sorted[1])[0][0] 

	rect = cv2.minAreaRect(contours[Index])
	box = cv2.boxPoints(rect)
	box = np.int0(box)

	Line=np.int0([np.average([box[0],box[1]],axis=0),np.average([box[2],box[3]],axis=0)]) 
 
	x1,y1,x2,y2=LineRotate(Line,-sp.pi*13.1/180)

	Orthogonal_Line=np.array([x1,y1,x2,y2])


	x_o1,y_o1,x_o2,y_o2=LineRotate_Over_Point(Orthogonal_Line,θ)  
	
	a=np.array([x2-5.19,0])
	b=np.array([x1,y1])
	c=np.array([x_o2,y_o2])
	
	angle=GetAngle(a,b,c) 

	retval, buffer = cv2.imencode('.jpg', dst)
	buffer=np.transpose(buffer)[0]
	jpg_as_text = base64.b64encode(buffer)
	strings=jpg_as_text.decode("utf-8")  


	return str(angle)+' '+str(a[0])+' '+str(a[1])+' '+str(b[0])+' '+str(b[1])+' '+str(c[0])+' '+str(c[1])+' '+strings
 

# img=cv2.imread('.//raw//raw//1.jpg')
# img2=cv2.imread('.//URIN//URIN//1.jpg')
# cv2.imshow('From App',img2)
# I=RAD(img)

# I=RAD(Data)
# print(I)
# cv2.imshow('3',I)
# cv2.imshow('2',closing)
