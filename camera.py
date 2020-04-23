from picamera import PiCamera
from time import sleep
import datetime

now = datetime.datetime.now()
camera = PiCamera()
camera.resolution = (800, 480)
filePath='/home/pi/pi-cloud-frame/media/picamera/{}-{}-{}-{}.{}.jpg'.format(str(now.year), str(now.month), str(now.day), str(now.hour), str(now.minute))
print(filePath)
camera.capture(filePath)
