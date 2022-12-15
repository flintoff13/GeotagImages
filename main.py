import piexif
import csv
from fractions import Fraction
import glob


def get_exif_date_hour(image_file_path):
    exif = piexif.load(image_file_path)
    date = exif["0th"][306]  # get the creationdate from foto (exiftag 306)
    helper = date.decode("utf-8").split(" ") #split at space after decoding to string
    helper = helper[1].replace(":", "") # get the time element and remove :
    return helper


def load_gnss_log(log_file_path, time_foto_created):
    with open(log_file_path, "r") as file:
        csvreader = csv.reader(file)
        for row in csvreader:
            time = row[1]
            time = time.split(".") #
            time = time[0]
            if time_foto_created == time:
                return row


def to_deg(value, loc):
    """convert decimal coordinates into degrees, minutes and seconds tuple
    Keyword arguments: value is float gps-value, loc is direction list ["S", "N"] or ["W", "E"]
    return: tuple like (25, 13, 48.343 ,'N')
    """
    value = value / 100
    if value < 0:
        loc_value = loc[0]
    elif value > 0:
        loc_value = loc[1]
    else:
        loc_value = ""
    abs_value = abs(value)
    deg = int(abs_value)
    t1 = (abs_value - deg) * 100
    min = int(t1)
    sec = round((t1 - min) * 60, 5)
    return (deg, min, sec, loc_value)


def change_to_rational(number):
    """convert a number to rantional
    Keyword arguments: number
    return: tuple like (1, 2), (numerator, denominator)
    """
    f = Fraction(str(number))
    return (f.numerator, f.denominator)


def add_gps_to_foto(picture_path, log_path):
    date = get_exif_date_hour(picture_path)
    date = int(date) - 10000
    gnnslog = load_gnss_log(log_path, str(date))
    if gnnslog == None:
        return
    lat = float(gnnslog[2])
    long = float(gnnslog[4])
    altitude = float(gnnslog[9])
    print(lat)
    print(long)

    print(gnnslog)
    lat_deg = to_deg(lat, ["S", "N"])
    lng_deg = to_deg(long, ["W", "E"])

    exiv_lat = (change_to_rational(lat_deg[0]), change_to_rational(lat_deg[1]), change_to_rational(lat_deg[2]))
    exiv_lng = (change_to_rational(lng_deg[0]), change_to_rational(lng_deg[1]), change_to_rational(lng_deg[2]))

    gps_ifd = {
        piexif.GPSIFD.GPSVersionID: (2, 0, 0, 0),
        piexif.GPSIFD.GPSAltitudeRef: 1,
        piexif.GPSIFD.GPSAltitude: change_to_rational(round(altitude)),
        piexif.GPSIFD.GPSLatitudeRef: lat_deg[3],
        piexif.GPSIFD.GPSLatitude: exiv_lat,
        piexif.GPSIFD.GPSLongitudeRef: lng_deg[3],
        piexif.GPSIFD.GPSLongitude: exiv_lng,
    }

    gps_exif = {"GPS": gps_ifd}
    exif_data = piexif.load(picture_path)
    exif_data.update(gps_exif)
    exif_bytes = piexif.dump(exif_data)
    piexif.insert(exif_bytes, picture_path)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    log_path = r"<redacted>"

    files = glob.glob(r'<redacted>')
    for picture_path in files:
        add_gps_to_foto(picture_path, log_path)
