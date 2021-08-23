from controllers.pvsystem import PvSystem
from controllers.location import Location
from controllers.photo import Photo
from controllers.camera import Camera
from controllers.shading import Shading
from controllers.date import Date


if __name__ == "__main__":
    camera = Camera(360, 62)
    # camera = Camera(46, 62)
    specific_dates = ['2021-03-21', '2021-06-21', '2021-12-21']
    dates = Date('2021-01-01 00:00:00', '2022-01-01', 'H', specific_dates)
    location = Location(-19.983223, -44.030741, dates)
    photo = Photo(camera, './Images/foto.jpg', 'foto.jpg', photo_pos=180)
    # photo1 = Photo(camera, './Images/40.jpg', '40.jpg', angular_elevation=20, photo_pos=40)
    # photo2 = Photo(camera, './Images/65.jpg', '65.jpg', angular_elevation=20, photo_pos=65)
    # photo3 = Photo(camera, './Images/95.jpg', '95.jpg', angular_elevation=20, photo_pos=95)
    # photo4 = Photo(camera, './Images/124.jpg', '124.jpg', angular_elevation=20, photo_pos=124)
    # photo5 = Photo(camera, './Images/165.jpg', '165.jpg', angular_elevation=20, photo_pos=165)
    # shading = Shading([photo1, photo2, photo3, photo4, photo5])
    shading = Shading([photo])
    # shading.plot_shading_visualization()
    pv = PvSystem(dates, location, shading)
    # pv.plot_cartesian_chart_with_shading1('5min')
    # pv.plot_shading_losses()
    # pv.plot_cartesian_chart_with_shading2('5min')
    # pv.plot_polar_chart_with_shading('5min')
