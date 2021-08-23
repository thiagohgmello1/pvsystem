import matplotlib.pyplot as plt
import numpy as np
from controllers.photo import Photo


class Shading:
    def __init__(self, photos: [Photo]):
        self.shading = self._periodic_photo_assembly(photos)

    def _periodic_photo_assembly(self, photos):
        shading = np.array([[0, 0]])
        for photo in photos:
            shading = np.append(shading, self._circular_coord(photo.shading), axis=0)
        shading = shading[shading[:, 0].argsort()]
        shading = np.delete(arr=shading, obj=0, axis=0)
        return shading

    @staticmethod
    def _circular_coord(array: np.array) -> np.array:
        array[:, 0] = np.where(array[:, 0] < 0, (360 + array[:, 0]), array[:, 0])
        return array

    def plot_shading_visualization(self):
        fig, ax = plt.subplots()
        ax.plot(self.shading[:, 0], self.shading[:, 1])
        plt.show()
