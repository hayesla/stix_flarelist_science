from astropy import units as u 
from astropy.coordinates import SkyCoord
from sunpy.coordinates import frames
import sunpy.map
import sunpy.sun.constants as sun_const
from astropy.coordinates.representation import CartesianRepresentation
import numpy as np 

def get_rsun_obs(observer):
    """
    Get the observed radius of the Sun from an observer location.
    """

    rsun_obs = ((sun_const.radius / (observer.spherical.distance - sun_const.radius)).decompose()
                    * u.radian).to(u.arcsec)
    return rsun_obs


def get_distance_off_limb(coord):
    theta_x = coord.Tx
    theta_y = coord.Ty
    rsun_obs = get_rsun_obs(coord.observer)
    distance_off_limb = np.sqrt(theta_x**2 + theta_y**2) - rsun_obs
    distance_r_sun = np.sqrt(theta_x**2 + theta_y**2)/rsun_obs

    return distance_off_limb, distance_r_sun


def generate_blank_map(date_obs, observer):
    """
    Given a date and an observer create a blank map

    """
    data = np.full((12, 12), np.nan)
    
    # Define a reference coordinate and create a header using sunpy.map.make_fitswcs_header
    skycoord = SkyCoord(0*u.arcsec, 0*u.arcsec,
                        frame=frames.Helioprojective(observer=observer, obstime=date_obs))
    
    # Scale set to the following for solar limb to be in the field of view
    header = sunpy.map.make_fitswcs_header(data, skycoord, scale=[600, 600]*u.arcsec/u.pixel)
    
    # Use sunpy.map.Map to create the blank map
    blank_map = sunpy.map.Map(data, header)
    return blank_map


def is_visible(coord):
    """
    Returns whether the coordinate is on the visible side of the Sun.
    This function is a modified version of PR#7118
    """
   
    coord = coord.make_3d()
    data = coord.cartesian
    data_to_sun = coord.observer.radius * CartesianRepresentation(1, 0, 0) - data

    is_behind = data.x < 0
    #print(data.x.to(u.AU))
    is_beyond_limb = np.sqrt(1 - (data.x / data.norm()) ** 2) > coord.rsun / coord.observer.radius
    #is_above_surface = data_to_sun.norm() >= coord.rsun
    
    is_on_near_side = data.dot(data_to_sun) >= 0

    return is_behind | is_beyond_limb | (is_on_near_side)