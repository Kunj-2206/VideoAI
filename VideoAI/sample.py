
import cv2
import matplotlib.pyplot as plt

images = ["VideoAI/static/src/images/freetest2/landscape-152502.png"]


cv_img = cv2.imread("static/src/images/freetest2/landscape-152502.png")
height, width = cv_img.shape[:2]
big_img = cv2.resize(cv_img, (3536, 2357))
cv2.imwrite('new_image.png', big_img)