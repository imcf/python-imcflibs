"""Functions allowing to interact with an OMERO server.

Contains helpers to parse URLs and / or OMERO image IDs, connect to OMERO and
fetch images from the server.
"""

# ImageJ Import
from ij import IJ

# Omero Dependencies
from omero.gateway import Gateway
from omero.gateway import LoginCredentials
from omero.log import SimpleLogger


def parse_image_ids(input_string):
    """Parse an OMERO URL or a string with image IDs into a list.

    Parameters
    ----------
    input_string : str
        String which is either the direct image link (URL) from OMERO.web
        (which may contain multiple images selected) or a sequence of OMERO
        image IDs separated by commas.

    Returns
    -------
    str[]
        List of all the image IDs parsed from the input string.
    """
    if input_string.startswith("https"):
        image_ids = input_string.split("image-")
        image_ids.pop(0)
        image_ids = [s.split("%")[0].replace("|", "") for s in image_ids]
    else:
        image_ids = input_string.split(",")
    return image_ids


def connect(host, port, username, password):
    """Connect to OMERO using the credentials provided.

    Parameters
    ----------
    host : str
        The address (FQDN or IP) of the OMERO server.
    port : int
        The port number for the OMERO server.
    username : str
        The username for authentication.
    password : str
        The password for authentication.

    Returns
    -------
    omero.gateway.Gateway
        A Gateway object representing the connection to the OMERO server.
    """
    # Omero Connect with credentials and simpleLogger
    cred = LoginCredentials()
    cred.getServer().setHostname(host)
    cred.getServer().setPort(port)
    cred.getUser().setUsername(username.strip())
    cred.getUser().setPassword(password.strip())
    simple_logger = SimpleLogger()
    gateway = Gateway(simple_logger)
    gateway.connect(cred)
    return gateway


def fetch_image(host, username, password, image_id, group_id=-1):
    """Fetch an image from an OMERO server and open it as an ImagePlus.

    NOTE: the function does **NOT** return the ImagePlus (nor its ID) as this
    information is not provided by the underlying `loci.plugins.LociImporter`
    call - it simply opens it in the running ImageJ instance.

    Parameters
    ----------
    host : str
        The address (FQDN or IP) of the OMERO server.
    username : str
        The username for authentication.
    password : str
        The password for authentication.
    image_id: int
        ID of the image to fetch.
    group_id : int, optional
        The OMERO group ID, by default -1 meaning the user's default group.
    """

    stackview = "viewhyperstack=true stackorder=XYCZT "
    dataset_org = "groupfiles=false swapdimensions=false openallseries=false concatenate=false stitchtiles=false"
    color_opt = "colormode=Default autoscale=true"
    metadata_view = (
        "showmetadata=false showomexml=false showrois=true setroismode=roimanager"
    )
    memory_manage = "virtual=false specifyranges=false setcrop=false"
    split = " splitchannels=false splitfocalplanes=false splittimepoints=false"
    other = "windowless=true"
    options = (
        "location=[OMERO] open=[omero:server=%s\nuser=%s\npass=%s\ngroupID=%s\niid=%s] %s %s %s %s %s %s %s "
        % (
            host,
            username,
            password,
            group_id,
            image_id,
            stackview,
            dataset_org,
            color_opt,
            metadata_view,
            memory_manage,
            split,
            other,
        )
    )
    IJ.runPlugIn("loci.plugins.LociImporter", options)
