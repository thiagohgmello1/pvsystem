import numpy as np
import matplotlib.pyplot as plt
import cv2
from controllers.camera import Camera


class Photo:
    def __init__(self, camera: Camera, file_in='test.jpeg', file_out='test(1).jpg', angular_elevation=0, photo_pos=0):
        self.file_in = file_in
        self.file_out = file_out
        self.angular_elevation = angular_elevation
        self.photo_pos = photo_pos
        self.camera = camera

        self.img = cv2.imread(self.file_in)
        self.img_shape = self.img.shape[:2]
        self.shade_img, self.superior_lim = self._image_preprocessing1()
        self.shading = self._cartesian_shading()

    def _image_preprocessing1(self) -> np.array:
        # Load image, convert to grayscale, Gaussian blur, Otsu's threshold
        gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (3, 3), 0)
        thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

        # Filter using contour area and remove small noise
        cnts = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]
        for c in cnts:
            area = cv2.contourArea(c)
            if area < 5500:
                cv2.drawContours(thresh, [c], -1, (0, 0, 0), -1)

        # Morph processed_img and invert image
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        processed_img = 255 - cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)
        # cv2.imwrite(self.file_out, processed_img)
        fig, ax = plt.subplots()
        ax.imshow(processed_img, cmap='gray', vmin=0, vmax=255)
        plt.savefig('outputs/photo/preprocessing1.png', dpi=80)
        # fig.show()
        return self._image_preprocessing2(processed_img)

    def _image_preprocessing2(self, processed_img) -> (np.array, np.array):
        pixels_y, pixels_x = self.img_shape
        superior_lim = np.zeros((pixels_x, 1))
        for x in np.arange(0, pixels_x):
            for y in np.arange(0, pixels_y):
                if processed_img[y][x] == 0:
                    superior_lim[x] = pixels_y - y
                    break
        shade_img = np.full((pixels_x, pixels_y), 255)
        for x in np.arange(0, superior_lim.size):
            count = 0
            while count < superior_lim[x]:
                shade_img[x][count] = 0
                count += 1
        fig, ax = plt.subplots()
        ax.imshow(shade_img.T, cmap='gray', vmin=0, vmax=255, origin='lower')
        plt.savefig('outputs/photo/preprocessing2.png', dpi=80)
        # fig.show()
        superior_lim -= pixels_y / 2
        return shade_img, superior_lim

    def _cartesian_shading(self) -> np.array:
        aperture_x = self.camera.theta_x
        aperture_y = self.camera.theta_y
        pixels_y, pixels_x = self.img_shape

        pixel2deg = aperture_y / (2 * pixels_y)
        shading_y = self.superior_lim * pixel2deg + self.angular_elevation
        shading_x = np.linspace(-aperture_x/2, aperture_x/2, num=pixels_x).reshape((pixels_x, 1)) + self.photo_pos
        fig, ax = plt.subplots()
        ax.plot(shading_x, shading_y)
        ax.set_ylim(0, None)
        plt.savefig('outputs/photo/c_shading.png', dpi=80)
        # fig.show()
        shading = np.concatenate((shading_x, shading_y), axis=1)
        return shading
