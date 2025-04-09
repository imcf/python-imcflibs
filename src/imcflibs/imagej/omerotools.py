"""Functions allowing to interact with an OMERO server.

Contains helpers to parse URLs and / or OMERO image IDs, connect to OMERO and
fetch images from the server.

Requires both the [`simple-omero-client`][simple-omero-client] and the
[`omero-insight`][omero-insight] JARs to be installed.

Most of the functions will use the [`simple-omero-client`][simple-omero-client]
to interact with the OMERO server. However, there are still some that
requires the [`omero-insight`][omero-insight] plugin to read metadata.

[simple-omero-client]: https://github.com/GReD-Clermont/simple-omero-client
[omero-insight]: https://github.com/ome/omero-insight
"""

from fr.igred.omero import Client
from fr.igred.omero.annotations import (
    MapAnnotationWrapper,
    TableWrapper,
)
from fr.igred.omero.roi import ROIWrapper
from java.lang import Long
from java.text import SimpleDateFormat
from java.util import ArrayList
from omero.cmd import OriginalMetadataRequest
from omero.gateway.model import TableData, TableDataColumn


def parse_url(client, omero_str):
    """Parse an OMERO URL / image IDs into the respective ImageWrapper objects.

    Assemble a list of ImageWrapper objects from one of the following inputs:

    - An OMERO URL (as retrieved e.g. from OMERO.web).
    - One or more OMERO image IDs.
    - An OMERO Dataset ID.

    Parameters
    ----------
    client : fr.igred.omero.Client
        Client used for login to OMERO.
    omero_str : str
        Either an URL from OMERO or image IDs separated by commas.

    Returns
    -------
    list(fr.igred.omero.repository.ImageWrapper)
        List of ImageWrappers parsed from the string.
    """
    image_ids = []
    dataset_ids = []
    image_wpr_list = []

    # Check if the url is a dataset
    if "dataset-" in omero_str:
        # If there are multiple datasets
        if "|" in omero_str:
            parts = omero_str.split("|")
            for part in parts:
                if "dataset-" in part:
                    image_ids.extend(
                        [
                            image
                            for image in client.getDataset(
                                Long(part.split("dataset-")[1].split("/")[0])
                            ).getImages()
                        ]
                    )
                    dataset_id = Long(part.split("dataset-")[1].split("/")[0])
                    dataset_ids.append(dataset_id)
        else:
            image_ids.extend(
                [
                    image
                    for image in client.getDataset(
                        Long(omero_str.split("dataset-")[1].split("/")[0])
                    ).getImages()
                ]
            )
            # If there is only one dataset
            dataset_id = Long(omero_str.split("dataset-")[1].split("/")[0])
            dataset_ids.append(dataset_id)

        # Get the images from the dataset
        for dataset_id in dataset_ids:
            dataset_wpr = client.getDataset(dataset_id)
            image_wpr_list.extend(dataset_wpr.getImages())

        return image_wpr_list

    # Check if the url is an image
    elif "image-" in omero_str:
        image_ids = omero_str.split("image-")
        image_ids.pop(0)
        image_ids = [s.split("%")[0].replace("|", "") for s in image_ids]
    else:
        image_ids = (
            [s.split("%")[0].replace("|", "") for s in omero_str.split("image-")[1:]]
            if "image-" in omero_str
            else omero_str.split(",")
        )
        # If it is a list of IDs separated by commas
        image_ids = omero_str.split(",")

    return [client.getImage(Long(image_id)) for image_id in image_ids]


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
    fr.igred.omero.Client
        A Client object representing the connection to the OMERO server.
    """
    # Create a new OMERO client
    client = Client()

    # Connect to the OMERO server using provided credentials
    client.connect(host, port, username, password)

    # Return the connected client
    return client


def fetch_image(client, image_id):
    """Fetch an image from an OMERO server and open it as an ImagePlus.

    Parameters
    ----------
    client : fr.igred.omero.Client
        The client object used to connect to the OMERO server.
    image_id : int
        The ID of the image to fetch.

    Returns
    -------
    ij.ImagePlus
        The fetched image as an ImagePlus.
    """

    # Fetch the image from the OMERO server
    image_wpr = client.getImage(Long(image_id))

    # Convert the image to an ImagePlus
    return image_wpr.toImagePlus()


def upload_image_to_omero(user_client, path, dataset_id):
    """Upload an image to OMERO.

    Parameters
    ----------
    user_client : fr.igred.omero.Client
        The client object used to connect to the OMERO server.
    path : str
        Path of the file to upload back to OMERO.
    dataset_id : Long
        ID of the dataset where to upload the file.

    Returns
    -------
    Long
        ID of the uploaded image
    """
    return user_client.getDataset(Long(dataset_id)).importImage(user_client, path)[0]


def add_keyvalue_annotation(client, repository_wpr, annotations, header):
    """Add an annotation to an OMERO object.

    Parameters
    ----------
    client : fr.igred.omero.Client
        The client object used to connect to the OMERO server.
    repository_wpr : fr.igred.omero.repositor.GenericRepositoryObjectWrapper
        Wrapper to the object for the anotation.
    annotations : dict
        Dictionary with the annotation to add.
    header : str
        Name for the annotation header.
    """
    # for pair in dict:
    #     result.add
    map_annotation_wpr = MapAnnotationWrapper(annotations)
    map_annotation_wpr.setNameSpace(header)
    repository_wpr.addMapAnnotation(client, map_annotation_wpr)


def delete_keyvalue_annotations(user_client, object_wrapper):
    """Delete annotations linked to object.

    Parameters
    ----------
    user_client : fr.igred.omero.Client
        Client used for login to OMERO.
    object_wrapper : fr.igred.omero.repositor.GenericRepositoryObjectWrapper
        Wrapper to the object for the anotation.

    """
    kv_pairs = object_wrapper.getMapAnnotations(user_client)
    user_client.delete(kv_pairs)


def find_dataset(client, dataset_id):
    """Retrieve a dataset (wrapper) from the OMERO server.

    Parameters
    ----------
    client : fr.igred.omero.Client
        The client object used to connect to the OMERO server.
    dataset_id : int
        The ID of the dataset to retrieve.

    Returns
    -------
    fr.igred.omero.repositor.DatasetWrapper
        The dataset wrapper retrieved from the server.
    """
    # Fetch the dataset from the OMERO server using the provided dataset ID
    return client.getDataset(Long(dataset_id))


def get_acquisition_metadata(user_client, image_wpr):
    """Get acquisition metadata from OMERO based on an image wrapper.

    Parameters
    ----------
    user_client : fr.igred.omero.Client
        Client used for login to OMERO
    image_wpr : fr.igred.omero.repositor.ImageWrapper
        Wrapper to the image for the metadata

    Returns
    -------
    dict

        {
            objective_magnification : float,
            objective_na : float,
            acquisition_date : str,
            acquisition_date_number : str,
        }
    """
    ctx = user_client.getCtx()
    instrument_data = (
        user_client.getGateway()
        .getMetadataService(ctx)
        .loadInstrument(image_wpr.asDataObject().getInstrumentId())
    )
    objective_data = instrument_data.copyObjective().get(0)
    metadata = {}

    metadata["objective_magnification"] = (
        objective_data.getNominalMagnification().getValue()
        if objective_data.getNominalMagnification() is not None
        else 0
    )
    metadata["objective_na"] = (
        objective_data.getLensNA().getValue()
        if objective_data.getLensNA() is not None
        else 0
    )

    if image_wpr.getAcquisitionDate() is None:
        if image_wpr.asDataObject().getFormat() == "ZeissCZI":
            field = "Information|Document|CreationDate"
            date_field = get_info_from_original_metadata(user_client, image_wpr, field)
            metadata["acquisition_date"] = date_field.split("T")[0]
            metadata["acquisition_date_number"] = int(
                metadata["acquisition_date"].replace("-", "")
            )
        else:
            metadata["acquisition_date"] = "NA"
            metadata["acquisition_date_number"] = 0
    else:
        sdf = SimpleDateFormat("yyyy-MM-dd")
        metadata["acquisition_date"] = sdf.format(image_wpr.getAcquisitionDate())
        metadata["acquisition_date_number"] = int(
            metadata["acquisition_date"].replace("-", "")
        )

    return metadata


def get_info_from_original_metadata(user_client, image_wpr, field):
    """Retrieve information from the original metadata (as opposed to OME-MD).

    In some cases not all information is parsed correctly by BF and has to be
    recovered / identified directly from the *original* metadata. This function
    extracts the corresponding value based on the field identifier.

    Parameters
    ----------
    user_client : fr.igred.omero.Client
        Client used for login to OMERO
    image_wpr : fr.igred.omero.repositor.ImageWrapper
        Wrapper to the image
    field : str
        Field to look for in the original metadata. Needs to be found beforehand.

    Returns
    -------
    str
        Value of the field
    """
    omr = OriginalMetadataRequest(Long(image_wpr.getId()))
    cmd = user_client.getGateway().submit(user_client.getCtx(), omr)
    rsp = cmd.loop(5, 500)
    gm = rsp.globalMetadata
    return gm.get(field).getValue()


def create_table_columns(headings):
    """Create OMERO table headings from a list of column names.

    Parameters
    ----------
    headings : list(str)
        List of columns names.

    Returns
    -------
    list(omero.gateway.model.TableDataColumn)
        List of columns formatted to be uploaded to OMERO.
    """
    table_columns = []
    # populate the headings
    for h in range(len(headings)):
        heading = headings.keys()[h]
        type = headings.values()[h]
        # OMERO.tables queries don't handle whitespace well
        heading = heading.replace(" ", "_")
        # title_heading = ["Slice", "Label"]
        table_columns.append(TableDataColumn(heading, h, type))
    # table_columns.append(TableDataColumn("Image", size, ImageData))
    return table_columns


def upload_array_as_omero_table(user_client, table_title, data, columns, image_wpr):
    """Upload a table to OMERO from a list of lists.

    Parameters
    ----------
    user_client : fr.igred.omero.Client
        Client used for login to OMERO
    table_title : str
        Title of the table to be uploaded.
    data : list(list())
        List of lists of results to upload
    columns : list(str)
        List of columns names
    image_wpr : fr.igred.omero.repositor.ImageWrapper
        Wrapper to the image to be uploaded

    Examples
    --------
    >>> from fr.igred.omero import Client
    >>> from java.lang import String, Double, Long
    ...
    >>> client = Client()  # connect to OMERO
    >>> client.connect("omero.example.org", 4064, "username", "password")
    ...
    >>> image_wpr = client.getImage(Long(123456))  # get an image
    ...
    >>> columns = {  # prepare column definitions (name-type pairs)
    ...     "Row_ID": Long,
    ...     "Cell_Area": Double,
    ...     "Cell_Type": String,
    ... }
    ...
    >>> data = [  # prepare data (list of rows, each row is a list of values)
    ...     [1, 250.5, "Neuron"],
    ...     [2, 180.2, "Astrocyte"],
    ...     [3, 310.7, "Neuron"],
    ... ]
    ...
    >>> upload_array_as_omero_table(
    ...     client, "Cell Measurements", data, columns, image_wpr
    ... )
    """

    dataset_wpr = image_wpr.getDatasets(user_client)[0]

    table_columns = create_table_columns(columns)
    table_data = TableData(table_columns, data)
    table_wpr = TableWrapper(table_data)
    table_wpr.setName(table_title)
    dataset_wpr.addTable(user_client, table_wpr)


def save_rois_to_omero(user_client, image_wpr, rm):
    """Save ROIs to OMERO linked to the image.

    Parameters
    ----------
    user_client : fr.igred.omero.Client
        Client used for login to OMERO
    image_wpr : fr.igred.omero.repositor.ImageWrapper
        Wrapper to the image for the ROIs
    rm : ij.plugin.frame.RoiManager
        ROI Manager containing the ROIs

    """
    rois_list = rm.getRoisAsArray()
    rois_arraylist = ArrayList(len(rois_list))
    for roi in rois_list:
        rois_arraylist.add(roi)
    rois_to_upload = ROIWrapper.fromImageJ(rois_arraylist)
    image_wpr.saveROIs(user_client, rois_to_upload)
