import cv2
import numpy as np

"""For this to work on the rpi we need to avoid using the VideoCapture class and
	instead sublcass PiCamera and PiRGBArray. To get the raw frame we need to use capture_continuous
	and flush the buffer that contains the raw pixel array after every iteration"""
	
class FrameDetector(object):

	def __init__(self, inputDevice):
		self.captureDevice = inputDevice
		self.capture = cv2.VideoCapture(self.captureDevice)
		self.refArc = None
		self.processedFrame = None
		self.refFeatures = None
		self.minMatches = 10

	def startCapture(self):
		if not self.capture.isOpened():
			self.capture = cv2.VideoCapture(self.captureDevice)
		while self.capture.isOpened():
			ret, self.frame = self.capture.read()
			if ret == True:
				self.detectFrame(calibrate=False)

	def calibCamera(self):
		while self.capture.isOpened() and self.refArc is None:
			ret, self.frame = self.capture.read()
			if ret == True:
				self.detectFrame(calibrate=True)

	def getContours(self):
		gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
		edges = cv2.Canny(gray,30,570,apertureSize = 3)
		contours, h = cv2.findContours(edges,1,2)
		sortedContours = sorted(contours, key=cv2.contourArea, reverse = True)[:10]
		return sortedContours

	def getFeatures(self, frame):
		features = {}
		surf = cv2.SURF(400)
		features['keypoints'], features['descriptors'] = surf.detectAndCompute(frame, None)
		return features

	def checkFeatures(self, frame):
		currentFeatures = self.getFeatures(frame)

		indexParams = dict(algorithm=0, trees=5)
		searchParams = dict(checks=50)

		flann = cv2.FlannBasedMatcher(indexParams, searchParams)
		matches = flann.knnMatch(self.refFeatures['descriptors'], currentFeatures['descriptors'], k=2)
		goodMatches = []

		for m,n in matches:
		    if m.distance < 0.7*n.distance:
		        goodMatches.append(m)

		return goodMatches

	def detectFrame(self,calibrate):

		if calibrate is True:
			sortedContours = self.getContours()
			frameCnt = 0
			for contour in sortedContours:
				if frameCnt > 0:
					break
				else:
					approx = cv2.approxPolyDP(contour,0.01*cv2.arcLength(contour,True), True)

					if len(approx) == 4:

						cv2.drawContours(self.frame,[contour],-1, (0,255,0), 3)
						cv2.imshow('orig',self.frame)
						print 'Was The Frame Detected Successfully? \n Press Y to finish calibrating or N to capture a new frame'
						if cv2.waitKey(0) & 0xFF == ord('y'):
							self.refFeatures = self.getFeatures(self.frame)
							self.refArc = cv2.contourArea(contour, True)
							print 'Frame Area Stored'
							print 'Frame 1 Reference Features Computed'
							break

						elif cv2.waitKey(0) & 0xFF == ord('n'):
							print 'Requesting New Frame'
							break
						frameCnt += 1

		else:
			matches = self.checkFeatures(self.frame)
			if len(matches) >= self.minMatches:
				print 'Searching For a New Frame'
				print "{} Matches between Ref Frame and Current Frame".format(len(matches))
				cv2.destroyAllWindows()
			else:
				sortedContours = self.getContours()
				#check for matching frame features here first
				#if these check out, do the processing

				frameCnt = 0
				for contour in sortedContours:
					if frameCnt > 0:
						break
					else:
						approx = cv2.approxPolyDP(contour,0.01*cv2.arcLength(contour,True), True)

						if len(approx) == 4 and cv2.contourArea(contour, True) >= self.refArc:
							#store features and check them here
							x,y,w,h = cv2.boundingRect(contour)
							crop = self.frame[y:y+h,x:x+w]
							w,h,channels = crop.shape
							rotationMatrix = cv2.getRotationMatrix2D((h/2, w/2),90,1)
							transposed = cv2.transpose(crop, rotationMatrix)

							self.processedFrame = cv2.flip(transposed, 0)
							cv2.imwrite("test.jpg", self.processedFrame)
							cv2.drawContours(self.frame,[contour],-1, (0,255,0), 3)
							cv2.imshow('orig',self.frame)

							if cv2.waitKey(0) & 0xFF == ord('q'):
								self.capture.release()
								break
								frameCnt += 1


if __name__ == '__main__':
	device = 0
	frameDetect = FrameDetector(0)
	frameDetect.calibCamera()
	frameDetect.startCapture()
