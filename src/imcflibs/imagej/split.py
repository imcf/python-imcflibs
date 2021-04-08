"""Functions for splitting channels and or slices."""

import os

from ij import IJ, ImagePlus  # pylint: disable-msg=E0401
from ij.io import FileSaver  # pylint: disable-msg=E0401
from ij.plugin import ChannelSplitter  # pylint: disable-msg=E0401


def split_by_c_and_z(log, dname, imgf, skip_top, skip_bottom):
    """Helper function to open, split and save a file.

    Load the file specified, split by channels and z-slices, create a directory
    for each channel using the channel number as a name suffix and export
    each slice as an individual TIF file.

    Parameters
    ----------
    log : logger or scijava-logservice
        The logger object to be used for logging.
    dname : str
        The directory to load TIF files from.
    imgf : str
        The file name to load and split.
    skip_top : int
        Number of slices to skip at the top.
    skip_bottom : int
        Number of slices to skip at the bottom.
    """
    log.info("Processing file [%s]" % imgf)
    imp = IJ.openImage(dname + "/" + imgf)
    fname = os.path.splitext(imgf)
    channels = ChannelSplitter().split(imp)
    for channel in channels:
        c_name = channel.getTitle().split("-")[0]
        tgt_dir = os.path.join(dname, fname[0] + "-" + c_name)
        if not os.path.isdir(tgt_dir):
            os.mkdir(tgt_dir)
        stack = channel.getStack()
        for z in range(1 + skip_top, stack.getSize() + 1 - skip_bottom):
            proc = stack.getProcessor(z)
            fout = "%s/%s-z%s%s" % (tgt_dir, fname[0], z, fname[1])
            # fout = dname + "/" + c_name + "/" + fname[0] + "-z" + z + fname[1]
            log.info("Writing channel %s, slice %s: %s" % (c_name, z, fout))
            FileSaver(ImagePlus(fname[0], proc)).saveAsTiff(fout)
